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
        self.assertEqual(incoming["repairPatchProtocol"], "swrlz-exact-patches-v11")
        self.assertNotIn("githubSourceChangeTask", incoming)
        self.assertNotIn("githubAction", incoming)
        self.assertNotIn("htmlRepairOwner", incoming)
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

    def test_conflicting_plan_payload_is_isolated_and_retry_is_specific(self):
        p = self.payload()
        p.update(githubSourceChangeTask="plan", githubAction={"mode":"plan"},
                 sourceChangeIdentity={"repo":"wrong"}, htmlProjectIntent={"create":True},
                 history=[{"role":"assistant","text":"old plan"}])
        received = []
        def model(incoming):
            received.append(incoming)
            self.assertNotIn("githubSourceChangeTask", incoming)
            self.assertNotIn("sourceChangeIdentity", incoming)
            self.assertNotIn("htmlProjectIntent", incoming)
            if len(received) == 1:
                yield {"type":"DELTA","text":json.dumps({"plan":[]})}
                yield {"type":"COMPLETED","phase":"COMPLETE"}
            else:
                self.assertIn("missing patches array", incoming["prompt"])
                yield from self.coder(incoming)
        with patch.object(runtime.approval,"should_route",return_value=True),\
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":SRC})),\
             patch.object(runtime,"inspect_static",return_value={"passed":True}),\
             patch.object(runtime.approval,"prepare_model",return_value={"kind":"review"}) as stage:
            events=list(runtime.run(p,model))
        self.assertEqual(len(received),2)
        stage.assert_called_once()
        self.assertEqual(events[-1]["phase"],"COMPLETE")

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

    def test_deploy_scope_requires_explicit_user_request(self):
        self.assertTrue(runtime.requested_publish_after_approval(
            "Present the approval request. Once approved, commit, deploy, and verify it works."))
        self.assertFalse(runtime.requested_publish_after_approval("Repair the existing viewer."))
        self.assertFalse(runtime.requested_publish_after_approval(
            "Once approved, commit the change. Do not deploy."))
        self.assertFalse(runtime.requested_publish_after_approval(
            "Once approved, commit and deploy. Never deploy."))
    
    def test_dependency_recovery_from_missing_node_modules_and_real_user_prompt(self):
        import importlib
        agent=importlib.import_module(runtime.bind_model_edits.__module__)
        dependency=importlib.import_module(agent.localize_imports.__module__)
        localize_imports,DependencyError=dependency.localize_imports,dependency.DependencyError
        source='<html><head><script type="importmap">{"imports":{"tiny":"https://unpkg.com/tiny@1.2.3/main.js"}}</script></head><body><script type="module">import {x} from "tiny"; document.body.textContent=x;</script></body></html>'
        members={"main.js":"export const x=1;","LICENSE":"MIT"}
        def reader(pkg,version,member):
            if (pkg,version)!=("tiny","1.2.3") or member not in members:
                raise DependencyError("DEPENDENCY_MODULE_MISSING: "+member)
            return members[member],"sha512-test"
        payload=self.payload()
        payload["receivedText"]="Inspect the existing project on GitHub. Identify why it fails to render correctly and repair it using your own coding model. Retrieve the actual source, generate targeted patches, validate them, and revise any failed patches until validation passes. Preserve the existing functionality and design. Do not regenerate the entire HTML page or rely on a predetermined repair script. Present the actual changes, validation results, and approval request. Once approved, commit, deploy, and verify that the project works."
        calls=[]
        def wrong_model(p):
            calls.append(p)
            self.assertEqual(p["modelId"],"coder")
            self.assertIn("availableToolCalls",p["prompt"])
            yield {"type":"DELTA","text":json.dumps({"patches":[{"path":"index.html","op":"replace_once","anchor":"https://unpkg.com/tiny@1.2.3/main.js","code":"./node_modules/tiny/main.js"}]})}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        with patch.object(runtime.approval,"should_route",return_value=True), \
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":source})), \
             patch.object(agent,"localize_imports",side_effect=lambda *a:localize_imports(*a,reader=reader)), \
             patch.object(runtime.approval,"prepare_model",return_value={"kind":"review"}) as stage:
            events=list(runtime.run(payload,wrong_model))
        self.assertEqual(len(calls),1)
        stage.assert_called_once()
        self.assertTrue(stage.call_args.kwargs["publish_after_validation"])
        self.assertEqual(stage.call_args.args[4]["patches"][0]["op"],"localize_imports")
        self.assertTrue(any("executor recovered" in e.get("text","") for e in events))
        self.assertEqual(events[-1]["phase"],"COMPLETE")

    def test_no_dependency_recovery_for_feature_or_explicit_restriction(self):
        baseline={"issues":[{"code":"CSP_EXTERNAL_MODULE","file":"index.html"}]}
        actions=[{"op":"localize_imports"}]
        for task in ("Repair rendering and add a new feature","Fix the save button",
                     "Fix rendering but do not download dependencies"):
            self.assertFalse(runtime.dependency_only_recovery(task,baseline,actions))
        self.assertTrue(runtime.dependency_only_recovery("Repair the rendering failure",baseline,actions))

    def test_browser_error_reaches_model_before_owner_review(self):
        responses=[]
        def model(p):
            responses.append(p)
            if len(responses)>1:self.assertIn("BROWSER_PAGE_ERROR",p["prompt"])
            yield from self.coder(p)
        browser_calls=[]
        def browser(project,files,canvas):
            browser_calls.append(files)
            ok=len(browser_calls)>1
            return {"receipt":{"browserVerified":ok,"issues":[] if ok else [{"code":"BROWSER_PAGE_ERROR","detail":"fixture runtime failure"}],"scope":"test"}}
        with patch.object(runtime.approval,"should_route",return_value=True), \
             patch.object(runtime,"_source_files",return_value=("b"*40,{"index.html":SRC})), \
             patch.object(runtime,"inspect_static",return_value={"passed":True}), \
             patch.object(runtime.approval,"prepare_model",return_value={"kind":"review"}) as stage:
            events=list(runtime.run(self.payload(),model,browser_validator=browser))
        self.assertEqual(len(browser_calls),2)
        self.assertEqual(len(responses),2)
        stage.assert_called_once()
        self.assertTrue(stage.call_args.args[6]["validation"]["browserVerified"])
        self.assertEqual(events[-1]["phase"],"COMPLETE")

    def test_owner_context_required(self):
        p=self.payload()
        del p["htmlRepairOwner"]
        with patch.object(runtime.approval,"should_route",return_value=True):
            events=list(runtime.run(p,self.coder))
        self.assertEqual(events[-1]["blocker"],"OWNER_CONTEXT_MISSING")


if __name__=="__main__":
    unittest.main()
