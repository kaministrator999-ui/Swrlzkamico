"""Execute the actual Station branch shape with the complete user prompt.

Unlike earlier tests, htmlProjectIntent=True simulates the fresh HTML
classifier intercepting a named existing-project repair before source retrieval.
"""
import ast
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

from api import html_project_context_v1 as context
from api import html_project_repair_v1 as repair

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location(
    "station_project_repair_v5", ROOT / "scripts/hf_chat_station_existing_repair_precedence_v5.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

SOURCE = '''from pathlib import Path
ROOT=Path(".")
app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")
def _run(payload):
    if False:
        pass
    elif _swrlz_project_repair.should_route(payload):
        event_source=iter(({"type":"STATUS","phase":"MODEL_REPAIR_SELECTED"},
                           {"type":"COMPLETED","phase":"COMPLETE"}))
    else:
        event_source=iter(({"type":"STATUS","phase":"GENERIC_CODER_SELECTED"},
                           {"type":"COMPLETED","phase":"COMPLETE"}))
    return list(event_source)
def incoming(prompt,t,payload,google_owner,tid):
    if False:
        pass
    elif payload.get("htmlProjectIntent"):
        payload["selectedRoute"]="FRESH_HTML_CREATE"
    elif not _swrlz_project_repair.is_command(prompt) and (html_project_ref := _swrlz_project_context.resolve(prompt,t)):
        try:
            html_project_source=_swrlz_project_context.read_project_source(
                google_owner,html_project_ref)
            payload["projectFileEvidence"]=_swrlz_project_context.evidence(
                html_project_ref,html_project_source)
            payload["activeHtmlProject"]=html_project_ref
            payload["htmlRepairOwner"]=google_owner
            payload["htmlRepairThreadId"]=tid
        except Exception:
            payload["projectFileEvidence"]=(
                "The user refers to HTML project "+html_project_ref["project"]+
                " at "+html_project_ref["path"]+
                " but exact owner-authorized GitHub source could not be retrieved.")
    elif github_report_explain_v236.is_report_request(prompt):
        payload["report"]=True
    return payload
'''


class RepairPrecedenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patched = release.patch_station(SOURCE)

    def namespace(self, fail=False):
        def source_read(owner, project):
            if fail:
                raise LookupError("source not available")
            return {"source": "<html></html>", "blobSha": "a"*40}
        project = SimpleNamespace(
            resolve=context.resolve,
            read_project_source=source_read,
            evidence=lambda project,source: "Verified Git blob: "+"a"*40,
        )
        tree = ast.parse(self.patched)
        fns = [n for n in tree.body if isinstance(n, ast.FunctionDef)
               and n.name in ("_run", "incoming")]
        env = {
            "_swrlz_project_context": project,
            "_swrlz_project_repair": repair,
            "github_report_explain_v236": SimpleNamespace(is_report_request=lambda text: False),
        }
        exec(compile(ast.fix_missing_locations(
            ast.Module(body=fns,type_ignores=[])), "<station-routing-test>", "exec"), env)
        return env

    def test_existing_project_beats_fresh_html_generation_even_with_html_intent(self):
        env = self.namespace()
        payload = env["incoming"](
            release.PROBE_PROMPT, {"messages": []}, {"htmlProjectIntent": True},
            "google:owner", "thread-1")
        self.assertNotEqual(payload.get("selectedRoute"), "FRESH_HTML_CREATE")
        self.assertEqual(payload["activeHtmlProject"]["project"],
                         "interactive-3d-model-viewer")
        self.assertIn("Verified Git blob:", payload["projectFileEvidence"])
        self.assertTrue(repair.should_route({**payload,"receivedText":release.PROBE_PROMPT}))
        self.assertEqual(env["_run"]({**payload,"receivedText":release.PROBE_PROMPT})[0]["phase"],
                         "MODEL_REPAIR_SELECTED")

    def test_missing_source_never_falls_through_to_generic_coder(self):
        env = self.namespace(fail=True)
        payload = env["incoming"](
            release.PROBE_PROMPT, {"messages": []}, {"htmlProjectIntent": True},
            "google:owner", "thread-1")
        self.assertIn("existingProjectSourceError", payload)
        event = env["_run"]({**payload,"receivedText":release.PROBE_PROMPT})[0]
        self.assertEqual(event["phase"], "EXISTING_PROJECT_SOURCE_UNAVAILABLE")
        self.assertNotIn("FRESH_HTML_CREATE", str(payload))

    def test_actual_new_html_request_retains_original_behavior(self):
        env = self.namespace()
        payload = env["incoming"]("Make me a new HTML page", {"messages":[]},
                                  {"htmlProjectIntent":True}, "google:owner", "thread")
        self.assertEqual(payload["selectedRoute"], "FRESH_HTML_CREATE")
        self.assertNotIn("activeHtmlProject", payload)

    def test_source_order_is_fixed_and_patch_idempotent(self):
        self.assertLess(self.patched.index(release.PROJECT),
                        self.patched.index(release.HTML_CREATE))
        self.assertEqual(release.patch_station(self.patched), self.patched)
        self.assertIn("EXISTING_PROJECT_SOURCE_UNAVAILABLE", self.patched)
        self.assertEqual(self.patched.count(release.MARKER), 1)


if __name__ == "__main__":
    unittest.main()
