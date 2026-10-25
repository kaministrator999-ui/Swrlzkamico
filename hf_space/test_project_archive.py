"""Source ZIP byte fidelity, bounded path validation and real Station ownership."""
import copy
import hashlib
import io
import json
import stat
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from fastapi.testclient import TestClient

from project_archive import (MAX_FILES, MAX_FILE_BYTES, MANIFEST_PATH,
    ProjectArchiveError, archive_filename, build_project_archive, parse_project_files, validate_project_files)
import station
from brain_programming import programming_intent


FILES = [
    {"path": "index.html", "language": "html", "content": '<!doctype html>\n<script type="module" src="src/main.js"></script>\n'},
    {"path": "src/main.js", "language": "javascript", "content": 'export const caption = "π";\r\n'},
    {"path": "styles/editor.css", "language": "css", "content": '#viewport { width: 100%; }\n'},
]


def artifact(files=None, artifact_id="artifact-owned"):
    files = copy.deepcopy(FILES if files is None else files)
    digest = station._artifact_source_hash(files)
    return {"id": artifact_id, "title": "editor", "sourceMessageId": "assistant-code",
        "currentRevision": 1, "currentSourceHash": digest, "files": files,
        "revisions": [{"revision": 1, "sourceHash": digest, "files": copy.deepcopy(files)}]}


class ProjectArchiveUnit(unittest.TestCase):
    def test_three_real_files_roundtrip_paths_bytes_and_honest_manifest(self):
        content = build_project_archive(FILES, artifact_id="artifact-owned", revision=3,
            source_hash="a" * 64)
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.namelist(), [item["path"] for item in FILES] + [MANIFEST_PATH])
            for item in FILES:
                self.assertEqual(archive.read(item["path"]), item["content"].encode("utf-8"))
                self.assertEqual(stat.S_IFMT(archive.getinfo(item["path"]).external_attr >> 16), stat.S_IFREG)
            manifest = json.loads(archive.read(MANIFEST_PATH))
        self.assertEqual(manifest["revision"], 3)
        self.assertEqual(manifest["sourceHash"], "a" * 64)
        self.assertEqual(manifest["verification"], "SOURCE_FILES_ONLY")
        self.assertIs(manifest["executionVerified"], False)
        for item, record in zip(FILES, manifest["files"]):
            data = item["content"].encode("utf-8")
            self.assertEqual(record["bytes"], len(data))
            self.assertEqual(record["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(content, build_project_archive(FILES,
            artifact_id="artifact-owned", revision=3, source_hash="a" * 64))

    def test_unsafe_portable_paths_rejected_without_normalizing_them(self):
        for path in ["", ".", "..", "../x.js", "a/../x.js", "./x.js", "/x.js",
                "//server/x", "C:/x.js", "a\\x.js", "src//x.js", "src/x.js/",
                "src/x.js ", "src/x.js.", "a\x00b", "a\nb", "a:b", "a?b", "a*b",
                "CON", "con.txt", "src/LPT1.js", "src/.git/config", ".hg/store",
                MANIFEST_PATH, MANIFEST_PATH.lower(), MANIFEST_PATH + "/x", "x" * 241]:
            with self.subTest(path=path), self.assertRaises(ProjectArchiveError):
                validate_project_files([{"path": path, "content": "source"}])
        self.assertEqual(validate_project_files([
            {"path": ".github/workflows/check.yml", "content": "name: check\n"},
            {"path": ".gitignore", "content": "node_modules/\n"},
            {"path": "src/__init__.py", "content": ""},
        ])[0]["path"], ".github/workflows/check.yml")

    def test_case_unicode_and_directory_collisions_reject(self):
        for paths in [("src/a.js", "src/A.js"), ("é.txt", "e\u0301.txt"),
                ("src", "src/main.js"), ("src/main.js", "src")]:
            with self.subTest(paths=paths), self.assertRaises(ProjectArchiveError):
                validate_project_files([{"path": path, "content": "source"} for path in paths])

    def test_file_count_utf8_bytes_and_total_bytes_are_bounded(self):
        with self.assertRaises(ProjectArchiveError):
            validate_project_files([{"path": f"file-{n}.txt", "content": ""}
                                    for n in range(MAX_FILES + 1)])
        with self.assertRaises(ProjectArchiveError):
            validate_project_files([{"path": "a.txt", "content": "☃" * (MAX_FILE_BYTES // 3 + 1)}])
        with self.assertRaises(ProjectArchiveError):
            validate_project_files([{"path": f"file-{n}.txt", "content": "x" * MAX_FILE_BYTES}
                                    for n in range(5)])
        for item in [None, {}, {"path": "a", "content": b"bytes"}, {"path": "a", "content": "\ud800"}]:
            with self.subTest(item=str(item)[:30]), self.assertRaises(ProjectArchiveError):
                validate_project_files([item])

    def test_revision_identity_and_download_name_are_bounded(self):
        for revision in [0, -1, True, "1"]:
            with self.subTest(revision=revision), self.assertRaises(ProjectArchiveError):
                build_project_archive(FILES, artifact_id="a", revision=revision)
        with self.assertRaises(ProjectArchiveError):
            build_project_archive(FILES, artifact_id="a", revision=1, source_hash="wrong")
        name = archive_filename('../../evil\r\nX-Evil: yes.html', 'untrusted\r\n"id', 2)
        self.assertRegex(name, r"^[a-z0-9-]+-r2\.zip$")
        self.assertNotEqual(name, archive_filename('editor', 'other-id', 2))

    def test_fence_parser_preserves_names_contents_and_rejects_path_clipping(self):
        text = '```html file=index.html project=editor\n<h1>Editor</h1>\n```\n\n```javascript file="src/my editor.js" project=editor\nexport const selected = 1;\n```'
        files = parse_project_files(text)
        self.assertEqual([item["path"] for item in files], ["index.html", "src/my editor.js"])
        self.assertEqual(files[1]["content"], "export const selected = 1;\n")
        self.assertEqual(station._parse_code_files(text), files)
        for header in ['html file=' + 'x' * 241, 'html file=../escape.html',
                'html file=a.html path=b.html', 'html file=a.html file=b.html']:
            with self.subTest(header=header[:50]), self.assertRaises(ProjectArchiveError):
                parse_project_files('```' + header + '\nsource\n```')
            self.assertEqual(station._parse_code_files('```' + header + '\nsource\n```'), [])

    def test_tiny_explicit_multi_file_project_is_persisted_for_zip(self):
        thread = {"codeArtifacts": []}
        message = {"id": "short-code", "meta": {}}
        text = '```html file=index.html\nHi\n```\n```css file=style.css\nbody{}\n```'
        self.assertLess(len(text), 120)
        created = station._create_code_artifact(thread, message, "request", text)
        self.assertIsNotNone(created)
        self.assertEqual(len(created["files"]), 2)
        self.assertEqual(message["meta"]["codeArtifactId"], created["id"])

    def test_nested_readme_and_inline_markers_preserve_complete_file_bytes(self):
        files = [
            {"path": "README.md", "language": "markdown", "content": "# Editor\n\n```sh\npython -m http.server\n```\n"},
            {"path": "src/my editor.js", "language": "javascript", "content": 'export const marker = "```";\nexport const complete = true;\n'},
            {"path": "styles.css", "language": "css", "content": "#editor { color: green; }\n"},
            {"path": "src/tick`name.js", "language": "javascript", "content": 'export const complete = true;\n'},
        ]
        markdown = station._artifact_markdown(files)
        self.assertIn('````markdown file="README.md"', markdown)
        self.assertEqual(parse_project_files(markdown), files)
        self.assertEqual(station._parse_code_files(markdown), files)
        self.assertEqual(station._response_prose("Project files:\n" + markdown + "\nFinished.").split(), ["Project", "files:", "Finished."])
        with zipfile.ZipFile(io.BytesIO(build_project_archive(parse_project_files(markdown), artifact_id="a", revision=1))) as archive:
            for file in files:
                self.assertEqual(archive.read(file["path"]), file["content"].encode("utf-8"))
        tilde = '~~~javascript file=src/example.js\nconst value = "```";\n~~~~\n'
        self.assertEqual(parse_project_files(tilde)[0]["content"], 'const value = "```";\n')

    def test_canonical_revision_source_larger_than_12k_is_not_cut(self):
        files = [{"path": "src/large.js", "language": "javascript",
                  "content": "// begin\n" + "const x = 1;\n" * 1300 + "// END-OF-CANONICAL-SOURCE\n"}]
        record = artifact(files)
        actual = station._artifact_revision_markdown(record, 1)
        self.assertGreater(len(actual), 12000)
        self.assertEqual(actual, station._artifact_markdown(files))
        self.assertIn("END-OF-CANONICAL-SOURCE", actual)
        message = {"id": "assistant-code", "role": "assistant", "text": actual,
                   "meta": {"codeArtifactId": record["id"], "artifactRevision": 1}}
        thread = {"codeArtifacts": [record], "messages": [message]}
        context = station._artifact_context_item(thread, message)
        self.assertEqual(context["text"], actual)
        history = station._history_projection(thread)
        self.assertEqual(history[0]["meta"]["artifactSourceSnapshot"], actual)


class ProjectArchiveHTTP(unittest.TestCase):
    def setUp(self):
        self.sessions = {
            "owner-cookie": {"revision": 1, "ownerGoogleId": "anonymous", "currentId": "thread-owned",
                "activeGeneration": None, "threads": [{"id": "thread-owned", "messages": [],
                    "codeArtifacts": [artifact()]}]},
            "other-cookie": {"revision": 1, "ownerGoogleId": "anonymous", "currentId": "thread-other",
                "activeGeneration": None, "threads": [{"id": "thread-other", "messages": [],
                    "codeArtifacts": [artifact(artifact_id="artifact-other")]}]},
        }
        self.patchers = [patch.object(station, "_sessions", self.sessions),
            patch.object(station, "_account_session", return_value=(None, None)),
            patch.object(station.account_chat_store, "save_chat", side_effect=AssertionError("Download must not write account data"))]
        for p in self.patchers:
            p.start(); self.addCleanup(p.stop)
        self.client = TestClient(station.app)
        self.client.cookies.set("swrlz_hf_sid", "owner-cookie")
        self.addCleanup(self.client.close)
        self.url = "/api/lalm_station/artifacts/thread-owned/artifact-owned/download"

    def test_owned_three_file_zip_has_correct_bytes_private_headers_and_no_mutation(self):
        before = copy.deepcopy(self.sessions)
        response = self.client.get(self.url + "?revision=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/zip")
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-swrlz-artifact-revision"], "1")
        self.assertEqual(response.headers["x-swrlz-archive-sha256"], hashlib.sha256(response.content).hexdigest())
        self.assertRegex(response.headers["content-disposition"], r'^attachment; filename="editor-[a-f0-9]{8}-r1.zip"$')
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            self.assertEqual(archive.read("src/main.js"), FILES[1]["content"].encode("utf-8"))
        self.assertEqual(self.sessions, before)

    def test_accepted_station_response_sync_then_download_preserves_all_three_files(self):
        # Model generation is a deterministic boundary double here. Exercise
        # real admission, worker storage, sync metadata and ZIP delivery.
        text = station._artifact_markdown(FILES)
        events = [{"type": "DELTA", "text": text},
                  {"type": "CANDIDATE_VALIDATION", "validation": {"status": "PASS", "executionVerified": False}},
                  {"type": "COMPLETED", "phase": "COMPLETE"}]
        with patch.object(station, "routes", return_value=[SimpleNamespace(model_id="700m", available=True)]), \
                patch.object(station, "dispatch", side_effect=lambda *args: iter(copy.deepcopy(events))), \
                patch.object(station._pool, "submit", side_effect=lambda fn, *args: fn(*args)):
            sent = self.client.post("/api/lalm_station/send", json={"modelId": "700m",
                "prompt": "Create a small project with index.html, src/main.js and styles/editor.css.",
                "threadId": "thread-roundtrip", "requestId": "request-project", "assistantMessageId": "assistant-project"})
        self.assertEqual(sent.status_code, 202)
        snapshot = self.client.get("/api/lalm_station/sync").json()
        self.assertEqual(snapshot["activeGeneration"]["artifactReceipt"]["action"], "ARTIFACT_CREATED")
        saved = snapshot["currentThread"]["codeArtifacts"][0]
        self.assertEqual(saved["files"], FILES)
        response = self.client.get("/api/lalm_station/artifacts/thread-roundtrip/" + saved["id"] + "/download?revision=1")
        self.assertEqual(response.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            for item in FILES:
                self.assertEqual(archive.read(item["path"]), item["content"].encode("utf-8"))

    def test_other_anonymous_session_missing_cookie_and_wrong_thread_cannot_download(self):
        self.client.cookies.set("swrlz_hf_sid", "other-cookie")
        self.assertEqual(self.client.get(self.url + "?ownerGoogleId=anonymous").status_code, 404)
        self.client.cookies.clear()
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.client.cookies.set("swrlz_hf_sid", "owner-cookie")
        self.assertEqual(self.client.get(self.url.replace("thread-owned", "thread-other")).status_code, 404)
        self.assertEqual(self.client.get(self.url.replace("artifact-owned", "artifact-other")).status_code, 404)

    def test_revision_pinned_download_survives_current_project_update(self):
        record = self.sessions["owner-cookie"]["threads"][0]["codeArtifacts"][0]
        second = copy.deepcopy(FILES); second[1]["content"] = "export const version = 2;\n"
        record["currentRevision"] = 2; record["files"] = second
        record["currentSourceHash"] = station._artifact_source_hash(second)
        record["revisions"].append({"revision": 2, "files": copy.deepcopy(second), "sourceHash": record["currentSourceHash"]})
        first = self.client.get(self.url + "?revision=1")
        current = self.client.get(self.url)
        for response, expected in [(first, FILES), (current, second)]:
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                self.assertEqual(archive.read("src/main.js"), expected[1]["content"].encode("utf-8"))
        self.assertEqual(self.client.get(self.url + "?revision=3").status_code, 404)
        self.assertEqual(self.client.get(self.url + "?revision=-1").status_code, 404)

    def test_invalid_stored_project_rejected_instead_of_traversal_archive(self):
        record = self.sessions["owner-cookie"]["threads"][0]["codeArtifacts"][0]
        record["revisions"][0]["files"][0]["path"] = "../escape.html"
        self.assertEqual(self.client.get(self.url + "?revision=1").status_code, 422)

    def test_stale_source_identity_cannot_label_changed_files_as_that_revision(self):
        record = self.sessions["owner-cookie"]["threads"][0]["codeArtifacts"][0]
        record["revisions"][0]["files"][1]["content"] = "export const changed = true;\n"
        self.assertEqual(self.client.get(self.url + "?revision=1").status_code, 409)

    def test_new_project_cannot_mutate_a_previous_artifact_from_stale_target_metadata(self):
        previous = self.sessions["owner-cookie"]["threads"][0]["codeArtifacts"][0]
        before = copy.deepcopy(previous)
        text = station._artifact_markdown(FILES)
        intent = {"codingTask": True, "newProject": True, "artifactMutationRequested": True,
                  "artifactTargetId": previous["id"], "baseRevision": 1,
                  "baseSourceHash": previous["currentSourceHash"]}
        events = [{"type": "PROGRAMMING_INTENT", "intent": intent},
                  {"type": "DELTA", "text": text},
                  {"type": "CANDIDATE_VALIDATION", "validation": {"status": "PASS", "executionVerified": False}},
                  {"type": "COMPLETED", "phase": "COMPLETE"}]
        with patch.object(station, "routes", return_value=[SimpleNamespace(model_id="700m", available=True)]), \
                patch.object(station, "dispatch", side_effect=lambda *args: iter(copy.deepcopy(events))), \
                patch.object(station, "persist_runtime_diagnostic", return_value=None), \
                patch.object(station._pool, "submit", side_effect=lambda fn, *args: fn(*args)):
            response = self.client.post("/api/lalm_station/send", json={"modelId": "700m",
                "prompt": "Now can you make a separate 3d model editor page", "threadId": "thread-owned",
                "requestId": "request-new-project", "assistantMessageId": "assistant-new-project"})
        self.assertEqual(response.status_code, 202)
        snapshot = self.client.get("/api/lalm_station/sync").json()
        self.assertEqual(snapshot["activeGeneration"]["artifactReceipt"]["action"], "ARTIFACT_CREATED")
        artifacts = snapshot["currentThread"]["codeArtifacts"]
        self.assertEqual(len(artifacts), 2)
        self.assertEqual(artifacts[0], before)
        self.assertNotEqual(artifacts[1]["id"], before["id"])
        self.assertEqual(artifacts[1]["currentRevision"], 1)

    def test_viewer_heading_revision_then_separate_editor_with_real_brain_routing(self):
        # Source delivery is a boundary double; this checks real request/history
        # projection, Brain target selection, Station revision commits and ZIPs.
        # It makes no claim that this synthetic viewport is a working 3D model.
        prompts = ["Can you do a 3d model viewer html page for me",
                   "Now can you add text to the top saying §wyrlz of that 3d model viewer",
                   "Now can you make a 3d model editor page"]
        viewer = '<!doctype html><html><head><title>3D Model Viewer</title></head><body><canvas id="viewport"></canvas><script>window.fixtureKind = "viewer";</script></body></html>\n'
        headed = viewer.replace('<body>', '<body><h1>§wyrlz</h1>')
        editor = viewer.replace('3D Model Viewer', '3D Model Editor').replace('"viewer"', '"editor"')
        outputs = ['```html file=index.html project=' + project + '\n' + source + '```'
                   for project, source in [('viewer', viewer), ('viewer', headed), ('editor', editor)]]
        intents = []
        def dispatch(_model_id, payload, *_generators):
            intent = programming_intent(payload['prompt'], payload['history'],
                                        payload.get('pinnedContext') or [], payload.get('priorProgrammingState'))
            index = len(intents); intents.append(intent)
            return iter([{'type': 'PROGRAMMING_INTENT', 'intent': intent},
                         {'type': 'DELTA', 'text': outputs[index]},
                         {'type': 'CANDIDATE_VALIDATION', 'validation': {'status': 'PASS', 'executionVerified': False}},
                         {'type': 'COMPLETED', 'phase': 'COMPLETE'}])
        snapshots = []
        with patch.object(station, 'routes', return_value=[SimpleNamespace(model_id='700m', available=True)]), \
                patch.object(station, 'dispatch', side_effect=dispatch), \
                patch.object(station, 'persist_runtime_diagnostic', return_value=None), \
                patch.object(station._pool, 'submit', side_effect=lambda fn, *args: fn(*args)):
            for index, prompt in enumerate(prompts):
                sent = self.client.post('/api/lalm_station/send', json={'modelId': '700m',
                    'prompt': prompt, 'threadId': 'thread-three-turns', 'requestId': 'three-turn-' + str(index),
                    'assistantMessageId': 'three-turn-assistant-' + str(index)})
                self.assertEqual(sent.status_code, 202)
                snapshots.append(self.client.get('/api/lalm_station/sync').json())
        first = snapshots[0]['currentThread']['codeArtifacts'][0]
        second = snapshots[1]['currentThread']['codeArtifacts'][0]
        final = snapshots[2]['currentThread']['codeArtifacts']
        self.assertTrue(intents[1]['artifactMutationRequested'])
        self.assertEqual(intents[1]['artifactTargetId'], first['id'])
        self.assertEqual(snapshots[1]['activeGeneration']['artifactReceipt']['action'], 'REVISION_COMMITTED')
        self.assertEqual(second['id'], first['id']); self.assertEqual(second['currentRevision'], 2)
        self.assertEqual(second['files'][0]['content'], headed)
        self.assertTrue(intents[2]['newProject']); self.assertFalse(intents[2]['artifactMutationRequested'])
        self.assertEqual(len(final), 2); self.assertEqual(final[0], second)
        self.assertNotEqual(final[1]['id'], second['id']); self.assertEqual(final[1]['currentRevision'], 1)
        self.assertEqual(final[1]['files'][0]['content'], editor)
        for record, revision, expected in [(final[0], 1, viewer), (final[0], 2, headed), (final[1], 1, editor)]:
            response = self.client.get('/api/lalm_station/artifacts/thread-three-turns/' + record['id'] + '/download?revision=' + str(revision))
            self.assertEqual(response.status_code, 200)
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                self.assertEqual(archive.read('index.html'), expected.encode('utf-8'))

    def test_verified_google_owner_switch_and_revocation_do_not_expose_project(self):
        saved = copy.deepcopy(self.sessions["owner-cookie"])
        saved["ownerGoogleId"] = "google:alice"
        empty = {"revision": 0, "ownerGoogleId": "google:bob", "currentId": "", "activeGeneration": None, "threads": []}
        with patch.object(station, "_account_session", return_value=("account-session", {"id": "google:alice"})) as auth, \
                patch.object(station.account_chat_store, "load_chat", side_effect=lambda owner: copy.deepcopy(saved if owner == "google:alice" else empty)):
            self.client.cookies.clear()
            self.assertEqual(self.client.get("/api/lalm_station/sync").status_code, 200)
            self.assertEqual(self.client.get(self.url + "?revision=1").status_code, 200)
            auth.return_value = ("other-account", {"id": "google:bob"})
            self.assertEqual(self.client.get(self.url + "?ownerGoogleId=google:alice").status_code, 404)
            auth.return_value = (None, None)
            self.assertEqual(self.client.get(self.url).status_code, 404)


if __name__ == "__main__":
    unittest.main()
