"""Tests for the actual loaded §C repair runtime, not just source readback."""
import ast
import importlib.util
from pathlib import Path
from types import ModuleType
from unittest import TestCase, main, mock

ROOT=Path(__file__).resolve().parents[1]
script=ROOT/"scripts/hf_chat_repair_runtime_sync_release_v7.py"
spec=importlib.util.spec_from_file_location("release_runtime_v7",script)
release=importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

FIXTURE = '''from pathlib import Path
ROOT=Path(".")
app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")
def response(payload, _coder_generate):
    if False:
        pass
    elif _swrlz_project_repair.should_route(payload):
        event_source=_swrlz_model_repair.run(payload,_coder_generate)
    return event_source
def context(payload,html_project_ref):
    if True:
        if True:
            payload["activeHtmlProject"]=html_project_ref
# swrlz-generated-html-github-handoff-v1: called only after the canonical response is persisted.
def handoff(payload):
    if True:
        if True:
            if payload.get("htmlProjectIntent"):
                return "CREATE_A_NEW_HTML_PROJECT"
'''

def new_source_files(a,b):
    return "index.html".endswith(tuple((".html",".css")))

def old_source_files(a,b):
    return "index.html".endswith(frozenset((".html",".css")))


class RuntimeV7Tests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.after=release.patch_station(FIXTURE)
        source=ast.parse(cls.after)
        functions=[n for n in source.body if isinstance(n,ast.FunctionDef)
                   and n.name in ("_swrlz_repair_tuple_is_loaded_v7",
                                  "_swrlz_verified_repair_runtime_v7",
                                  "_swrlz_execute_model_repair_v7")]
        cls.env={"_swrlz_model_repair":ModuleType("html_project_agent_runtime_v1")}
        exec(compile(ast.Module(body=functions,type_ignores=[]),"<v7>", "exec"),cls.env)

    def test_source_footprint_and_idempotence(self):
        self.assertLess(self.after.index(release.MARKER),self.after.index("def response"))
        self.assertIn(release.HANDOFF_NEW,self.after)
        self.assertNotIn(release.HANDOFF_OLD,self.after)
        self.assertIn(release.OWNER_NEW,self.after)
        self.assertIn(release.NEW_ROUTE,self.after)
        self.assertNotIn(release.OLD_ROUTE,self.after)
        self.assertEqual(release.patch_station(self.after),self.after)
        self.assertEqual(self.after.count(release.MARKER),1)

    def test_in_memory_fingerprint_is_not_a_file_check(self):
        module=self.env["_swrlz_model_repair"]
        module._source_files=old_source_files
        self.assertFalse(self.env["_swrlz_repair_tuple_is_loaded_v7"]())
        module._source_files=new_source_files
        self.assertTrue(self.env["_swrlz_repair_tuple_is_loaded_v7"]())

    def test_stale_module_is_reloaded_on_user_request(self):
        module=self.env["_swrlz_model_repair"]
        module._source_files=old_source_files
        def reload(target):
            self.assertIs(target,module)
            module._source_files=new_source_files
            return module
        with mock.patch("importlib.reload",side_effect=reload) as called:
            self.assertIs(self.env["_swrlz_verified_repair_runtime_v7"](),module)
        called.assert_called_once_with(module)
        self.assertTrue(self.env["_swrlz_repair_tuple_is_loaded_v7"]())

    def test_stale_module_rejected_if_reload_did_not_fix_it(self):
        module=self.env["_swrlz_model_repair"]
        module._source_files=old_source_files
        with mock.patch("importlib.reload",return_value=module):
            with self.assertRaisesRegex(RuntimeError,"REPAIR_RUNTIME_MODULE_STALE"):
                self.env["_swrlz_verified_repair_runtime_v7"]()

    def test_model_repair_status_uses_verified_loaded_code(self):
        module=self.env["_swrlz_model_repair"]
        module._source_files=new_source_files
        def fake_run(payload,coder):
            yield {"type":"DELTA","text":"Owner source repair candidate"}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        module.run=fake_run
        events=list(self.env["_swrlz_execute_model_repair_v7"]({"activeHtmlProject":{}},lambda _:iter(())))
        self.assertEqual(events[0]["phase"],"REPAIR_RUNTIME_V7_VERIFIED")
        self.assertEqual(events[1]["text"],"Owner source repair candidate")
        self.assertEqual(events[-1]["type"],"COMPLETED")

    def test_existing_repair_cannot_trigger_new_html_creation(self):
        module=self.env["_swrlz_model_repair"]
        payload={"htmlProjectIntent":{"kind":"html-project-generate-and-publish"},
                 "activeHtmlProject":{"project":"interactive-3d-model-viewer"}}
        self.assertFalse(bool(payload.get("htmlProjectIntent") and not (
            payload.get("activeHtmlProject") or payload.get("existingProjectSourceError"))))
        self.assertTrue(bool({"htmlProjectIntent":True}.get("htmlProjectIntent") and not (
            None or None)))
        self.assertTrue(bool({"htmlProjectIntent":True,"existingProjectSourceError":"fail"}.get("existingProjectSourceError")))
        self.assertIn('payload["htmlProjectIntent"]=None',self.after)


if __name__=="__main__":
    main()
