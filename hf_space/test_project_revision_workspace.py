"""Saved project continuity, guarded named deltas and actual owned ZIP HTTP.

The real engine is exercised with controlled model drafts; this proves the
inference/storage protocol, not learned model quality or browser execution.
"""
import copy
import hashlib
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from fastapi.testclient import TestClient

import station
from project_archive import MANIFEST_PATH, ProjectArchiveError, project_markdown
from project_revision_workspace import RevisionWorkspaceError, merge_project_revision_files
from test_generation_completion_budget import Responses
from test_github_change_model_context import load_engine


FILES = [
    {"path": "index.html", "language": "html", "content": '<!doctype html><html><head><title>Caption project</title><link rel="stylesheet" href="styles/site.css"></head><body><output id="caption"></output><script type="module" src="src/main.js"></script></body></html>\n'},
    {"path": "src/main.js", "language": "javascript", "content": 'document.querySelector("#caption").textContent="first";\r\n'},
    {"path": "styles/site.css", "language": "css", "content": '#caption { color: green; }\n'},
    {"path": "README.md", "language": "markdown", "content": '# Caption project\n\nServe this directory with a local static web server.\n'},
]
CHANGED = {**FILES[1], "content": 'document.querySelector("#caption").textContent="second §";\r\n'}


class ProjectRevisionWorkspace(unittest.TestCase):
    def test_one_named_delta_retains_all_other_bytes_order_and_language(self):
        before = copy.deepcopy(FILES)
        actual = merge_project_revision_files(FILES, project_markdown([CHANGED]))
        expected = copy.deepcopy(FILES); expected[1] = CHANGED
        self.assertEqual(actual, expected)
        self.assertEqual(FILES, before)
        self.assertEqual([item["path"] for item in actual], [item["path"] for item in FILES])

    def test_explicit_new_paths_append_but_omissions_never_remove_old_paths(self):
        added = {"path": "docs/guide.md", "language": "markdown", "content": '# Guide\nActual documentation.\n'}
        self.assertEqual(merge_project_revision_files(FILES, project_markdown([added])), FILES+[added])
        self.assertEqual(merge_project_revision_files(FILES, project_markdown([FILES[0]])), FILES)

    def test_multi_file_revision_never_uses_generated_fallback_names_as_targets(self):
        for delta in ['```javascript\nconst changed=true;\n```',
                      project_markdown([CHANGED])+'\n\n```css\nbody { color: blue; }\n```']:
            with self.subTest(delta=delta), self.assertRaises(RevisionWorkspaceError) as caught:
                merge_project_revision_files(FILES, delta)
            self.assertEqual(caught.exception.code, "FILE_PATH_REQUIRED")
        comment = '```javascript\n// src/main.js\nconst changed=true;\n```'
        self.assertEqual(merge_project_revision_files(FILES, comment)[1]["path"], "src/main.js")

    def test_legacy_sole_file_update_retains_its_authoritative_path(self):
        initial = [{"path": "viewer.html", "language": "html", "content": '<html><body>old</body></html>\n'}]
        actual = merge_project_revision_files(initial, '```html\n<html><body>new</body></html>\n```')
        self.assertEqual(actual, [{**initial[0], "content": '<html><body>new</body></html>\n'}])
        with self.assertRaises(RevisionWorkspaceError):
            merge_project_revision_files(initial, '```javascript\nconst unrelated=true;\n```')

    def test_combined_tree_collisions_and_stale_current_bytes_cannot_commit(self):
        for path in ["src/Main.js", "src", "../escape.js"]:
            with self.subTest(path=path), self.assertRaises(ProjectArchiveError):
                merge_project_revision_files(FILES, project_markdown([{**CHANGED, "path": path}]))
        record = {"files": copy.deepcopy(FILES), "currentRevision": 1,
                  "currentSourceHash": station._artifact_source_hash(FILES), "revisions": []}
        record["files"][0]["content"] += "changed outside revision\n"
        before = copy.deepcopy(record)
        self.assertEqual(station._commit_code_artifact_revision(record, project_markdown([CHANGED]),
                         "request", 1, record["currentSourceHash"]), (False, "CURRENT_SOURCE_HASH_CONFLICT"))
        self.assertEqual(record, before)

    def test_stale_revision_and_hash_reject_without_changing_any_snapshot(self):
        for requested_revision, requested_hash, reason in [(0,"","BASE_REVISION_REQUIRED"),
                (2,"a"*64,"REVISION_CONFLICT"), (1,"","SOURCE_HASH_REQUIRED"),
                (1,"a"*64,"SOURCE_HASH_CONFLICT")]:
            record = {"files": copy.deepcopy(FILES), "currentRevision": 1,
                "currentSourceHash": station._artifact_source_hash(FILES), "revisions": []}
            before = copy.deepcopy(record)
            self.assertEqual(station._commit_code_artifact_revision(record, project_markdown([CHANGED]),
                "request", requested_revision, requested_hash), (False,reason))
            self.assertEqual(record,before)


class ProjectRevisionHTTP(unittest.TestCase):
    def setUp(self):
        self.sessions = {"owner-cookie": {"revision": 0, "ownerGoogleId": "anonymous",
            "currentId": "", "activeGeneration": None, "threads": []}}
        for patcher in [patch.object(station, "_sessions", self.sessions),
                        patch.object(station, "_account_session", return_value=(None, None)),
                        patch.object(station, "persist_runtime_diagnostic", return_value=None)]:
            patcher.start(); self.addCleanup(patcher.stop)
        self.client = TestClient(station.app)
        self.client.cookies.set("swrlz_hf_sid", "owner-cookie")
        self.addCleanup(self.client.close)

    def read_zip(self, url, expected, revision):
        response = self.client.get(url+"?revision="+str(revision))
        self.assertEqual(response.status_code, 200, response.text[:200] if response.status_code!=200 else "")
        self.assertEqual(response.headers["x-swrlz-artifact-revision"], str(revision))
        self.assertEqual(response.headers["x-swrlz-archive-sha256"], hashlib.sha256(response.content).hexdigest())
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            self.assertEqual(archive.namelist(), [item["path"] for item in expected]+[MANIFEST_PATH])
            manifest = json.loads(archive.read(MANIFEST_PATH))
            self.assertEqual(manifest["revision"], revision)
            self.assertEqual(manifest["sourceHash"], station._artifact_source_hash(expected))
            for item, receipt in zip(expected, manifest["files"]):
                data = item["content"].encode()
                self.assertEqual(archive.read(item["path"]), data)
                self.assertEqual(receipt["sha256"], hashlib.sha256(data).hexdigest())
        return response.content

    def test_real_engine_create_four_files_then_named_js_edit_downloads_complete_same_project(self):
        engine = load_engine("qwen_coder_engine")
        model = Responses([(project_markdown(FILES), "stop"), (project_markdown([CHANGED]), "stop")])
        observed = []
        def dispatch(_model, payload, *_generators):
            events = list(engine.generate_events(payload)); observed.append(events)
            return iter(events)
        with patch.object(engine, "load", return_value=model), \
                patch.object(station, "routes", return_value=[SimpleNamespace(model_id="coder", available=True)]), \
                patch.object(station, "dispatch", side_effect=dispatch), \
                patch.object(station._pool, "submit", side_effect=lambda fn,*args: fn(*args)):
            snapshots = []
            for index, prompt in enumerate([
                "Create a small HTML project with index.html, src/main.js, styles/site.css and README.md.",
                "Now update src/main.js in this project to set the caption to second §; preserve every other file.",
            ]):
                response = self.client.post("/api/lalm_station/send", json={"modelId": "coder", "prompt": prompt,
                    "threadId": "project-workspace", "requestId": "workspace-"+str(index),
                    "assistantMessageId": "workspace-assistant-"+str(index)})
                self.assertEqual(response.status_code, 202, response.text)
                snapshots.append(self.client.get("/api/lalm_station/sync").json())
        self.assertEqual(len(model.calls), 2, "Both real engine contracts must accept the controlled source drafts")
        for events in observed:
            validation = next(event["validation"] for event in events if event["type"]=="CANDIDATE_VALIDATION")
            self.assertEqual(validation["status"], "PASS", validation)
        first = snapshots[0]["currentThread"]["codeArtifacts"][0]
        final = snapshots[1]["currentThread"]["codeArtifacts"]
        self.assertEqual(len(final), 1)
        current = final[0]
        self.assertEqual(current["id"], first["id"])
        self.assertEqual(current["currentRevision"], 2)
        expected = copy.deepcopy(FILES); expected[1] = CHANGED
        self.assertEqual(current["files"], expected)
        self.assertEqual(snapshots[1]["activeGeneration"]["artifactReceipt"]["action"], "REVISION_COMMITTED")
        self.assertIn("omitted files are preserved", model.calls[1]["messages"][0]["content"])
        url = "/api/lalm_station/artifacts/project-workspace/"+current["id"]+"/download"
        first_zip = self.read_zip(url, FILES, 1)
        self.read_zip(url, expected, 2)
        self.assertEqual(self.client.get(url+"?revision=1").content, first_zip)
        thread = self.sessions["owner-cookie"]["threads"][0]
        self.assertIsNone(station._owned_project_edit_intent(thread,
            "@GitHub update src/main.js in my repository", station._history_projection(thread), [],
            thread.get("programmingState") or {}), "Explicit provider intent must not be diverted into local editing")
        with patch.object(station, "routes", return_value=[SimpleNamespace(model_id="coder", available=True)]), \
                patch.object(station, "dispatch", side_effect=AssertionError("Explicit GitHub requests retain the provider owner")) as model_dispatch, \
                patch.object(station.github_connection, "_api", side_effect=AssertionError("No provider network access is authorized in this anonymous fixture")), \
                patch.object(station._pool, "submit", side_effect=lambda fn,*args: fn(*args)):
            provider = self.client.post("/api/lalm_station/send", json={"modelId": "coder",
                "prompt": "@GitHub update src/main.js in my repository", "threadId": "project-workspace",
                "requestId": "workspace-explicit-github", "assistantMessageId": "workspace-provider"})
        self.assertEqual(provider.status_code,202)
        model_dispatch.assert_not_called()
        self.assertEqual(thread["codeArtifacts"][0]["currentRevision"],2)
        self.assertEqual(thread["codeArtifacts"][0]["files"],expected)
        self.client.cookies.clear()
        self.client.cookies.set("swrlz_hf_sid", "foreign-cookie")
        self.assertEqual(self.client.get(url+"?revision=2").status_code, 404)


if __name__ == "__main__":
    unittest.main()
