"""Model invocation and approval separation regression for §C live repair."""
import json
import unittest
from unittest.mock import patch

from api import html_project_agent_runtime_v1 as runtime
from api.html_project_agent_v1 import VERSION
from scripts.project_code_targeted_repair_v1 import source_sha

PROJECT={"repo":"kaministrator999-ui/Swrlzkamico",
         "project":"interactive-3d-model-viewer"}
SRC="<html><head><title>Project</title></head><body><button id='go'>Go</button></body></html>"


def proposal():
    return {"schema":VERSION,"project":PROJECT["project"],
            "patches":[{"path":"index.html","sourceSha256":source_sha(SRC),
                        "op":"insert_before","anchor":"</body>",
                        "code":"<script>document.querySelector('#go').onclick=()=>{}</script>"}]}


class RuntimeTests(unittest.TestCase):
    def payload(self):
        return {"activeHtmlProject":PROJECT,
                "projectFileEvidence":"Verified Git blob: "+"a"*40,
                "receivedText":"Fix the existing project save button",
                "htmlRepairOwner":"google:owner",
                "htmlRepairThreadId":"thread123"}

    def coder(self, incoming):
        self.assertIn("SOURCE-PRESERVING",incoming["prompt"])
        self.assertEqual(incoming["history"],[])
        yield {"type":"STATUS","phase":"GENERATING"}
        self.assertIn("server binds", incoming["responseDirective"])
        generated = {"patches": [
            {"path":"index.html","op":"insert_before","anchor":"</body>",
             "code":"<script>document.querySelector('#go').onclick=()=>{}</script>"}
        ]}
        yield {"type":"DELTA","text":json.dumps(generated)}
        yield {"type":"COMPLETED","phase":"COMPLETE"}

    def test_model_selected_repair_calls_approval_only_after_validation(self):
        with patch.object(runtime.approval,"should_route",return_value=True),\
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":SRC})),\
             patch.object(runtime,"inspect_static",return_value={"passed":True}),\
             patch.object(runtime.approval,"prepare_model",return_value={
                 "contract":"swrlz-widget-v1","kind":"github-html-publish-review",
                 "data":{"project":PROJECT["project"]}}) as stage:
            events=list(runtime.run(self.payload(),self.coder))
        self.assertEqual(len(stage.call_args.args),7)
        self.assertTrue(any(e.get("type")=="WIDGET" for e in events))
        self.assertTrue(any("No GitHub write" in e.get("text","") for e in events))
        self.assertEqual(events[-1]["phase"],"COMPLETE")

    def test_runtime_normalizes_wrong_identity_and_hash_before_review(self):
        def model(incoming):
            incorrect = proposal()
            incorrect["schema"] = "model-invented-schema"
            incorrect["project"] = "wrong-project-name"
            incorrect["patches"][0]["sourceSha256"] = "f"*64
            yield {"type":"DELTA","text":json.dumps(incorrect)}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        with patch.object(runtime.approval,"should_route",return_value=True),\
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":SRC})),\
             patch.object(runtime,"inspect_static",return_value={"passed":True}),\
             patch.object(runtime.approval,"prepare_model",return_value={"kind":"review"}) as stage:
            events = list(runtime.run(self.payload(),model))
        self.assertEqual(events[-1]["phase"],"COMPLETE")
        self.assertTrue(any(e.get("type")=="WIDGET" for e in events))
        bound = stage.call_args.args[4]
        self.assertEqual(bound["schema"],VERSION)
        self.assertEqual(bound["project"],PROJECT["project"])
        self.assertEqual(bound["patches"][0]["sourceSha256"],source_sha(SRC))

    def test_bad_model_output_never_stages(self):
        def bad_model(p):
            yield {"type":"DELTA","text":"I will repair it later."}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        with patch.object(runtime.approval,"should_route",return_value=True),\
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":SRC})),\
             patch.object(runtime.approval,"prepare_model") as stage:
            events=list(runtime.run(self.payload(),bad_model))
        stage.assert_not_called()
        self.assertEqual(events[-1]["phase"],"PARTIAL")

    def test_manifest_source_files_use_tuple_extensions_and_verify_blobs(self):
        """Real _source_files with mocked owner GitHub operations, not a stub."""
        import base64
        import hashlib
        from types import ModuleType
        from unittest.mock import Mock
        import sys

        body = SRC.encode("utf-8")
        blob = hashlib.sha1(
            b"blob " + str(len(body)).encode("ascii") + bytes([0]) + body
        ).hexdigest()
        sha = "b" * 40
        auth = {"repo": PROJECT["repo"], "branch": "main", "token": "test"}
        fake = ModuleType("github_html_publish_action_v1")
        fake._authorized = Mock(return_value=auth)
        fake._head = Mock(return_value=sha)
        fake._manifest = Mock(return_value={
            "repo": PROJECT["repo"], "sourceSha": sha,
            "files": [
                {"path": "index.html", "bytes": len(body)},
                {"path": "art.png", "bytes": 9},
            ],
        })
        fake._github = Mock(return_value={
            "encoding": "base64", "content": base64.b64encode(body).decode("ascii"),
            "sha": blob,
        })
        with patch.dict(sys.modules, {"github_html_publish_action_v1": fake}):
            head, files = runtime._source_files("google:owner", PROJECT)
        self.assertEqual(head, sha)
        self.assertEqual(files, {"index.html": SRC})
        self.assertEqual(fake._github.call_count, 1)
        self.assertIn("contents/html-projects/interactive-3d-model-viewer/index.html",
                      fake._github.call_args.args)
        self.assertIsInstance(runtime.TEXT_EXTENSIONS, frozenset)

    def test_owner_context_required(self):
        p=self.payload()
        del p["htmlRepairOwner"]
        with patch.object(runtime.approval,"should_route",return_value=True):
            events=list(runtime.run(p,self.coder))
        self.assertEqual(events[-1]["blocker"],"OWNER_CONTEXT_MISSING")


if __name__=="__main__":
    unittest.main()
