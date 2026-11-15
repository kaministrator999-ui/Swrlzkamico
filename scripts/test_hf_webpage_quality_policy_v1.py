"""Unit checks for HTML-specific quality policy without running a model."""
from __future__ import annotations
import ast, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hf_webpage_quality_policy_v1 as policy

class QualityTests(unittest.TestCase):
    def setUp(self):
        self.env={}
        exec(compile(ast.parse(policy.HELPER),"<web-quality-policy>","exec"),self.env)
        self.guidance=self.env["_swrlz_webpage_quality_policy"]
        self.flags=self.env["_swrlz_webpage_quality_risks"]

    def test_broad_request_avoids_agency_template_and_fake_ui(self):
        instruction=self.guidance("Make me a cool HTML webpage",{})
        for phrase in ("OPEN-ENDED CREATIVE PAGE","one cohesive",
                       "WORKING interactive","marketing template",
                       "Project Alpha/Beta/Gamma",
                       "Buttons, links, tabs, menus, toggles, and forms"):
            self.assertIn(phrase,instruction)

    def test_specified_site_preserves_requirements(self):
        instruction=self.guidance("Create a website for an actual bakery",{})
        self.assertIn("USER-SPECIFIC PAGE",instruction)
        self.assertNotIn("OPEN-ENDED CREATIVE PAGE",instruction)
        self.assertIn("do not replace",instruction)

    def test_responsive_and_no_inert_buttons_on_all_websites(self):
        instruction=self.guidance("Make a shop HTML page",{})
        for phrase in ("320-390px","viewport","wrapping/collapsing",
                       "no horizontal overflow","backend","tap targets",
                       "keyboard/focus","reduced-motion"):
            self.assertIn(phrase,instruction)

    def test_nonblocking_flags_catch_screenshot_regressions(self):
        page='''<!DOCTYPE html><html><head><title>Neon Horizon</title></head>
<body><a href="#">Home</a><h2>Project Alpha</h2><h3>Project Beta</h3>
<form><input name="email"><button>SEND MESSAGE</button></form></body></html>'''
        self.assertEqual(self.flags(page,"Make a cool webpage"),
          ["mobile-viewport-missing","form-submission-not-implemented",
           "invented-project-placeholder","unresolved-navigation-anchor"])

    def test_complete_functional_page_has_no_flags(self):
        page='''<!doctype html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
</head><body><form id="f"><label>Email<input type="email"></label>
<button type="submit">Save locally</button></form>
<script>document.getElementById("f").addEventListener("submit",e=>{e.preventDefault()})</script>
</body></html>'''
        self.assertEqual(self.flags(page,"Make a contact form"),[])

    def test_policy_never_changes_validation_status_or_triggers_extra_repairs(self):
        sample='''# SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1
def generate_events(payload):
    programming={}
    system=""
    prompt=""
    model=None
    history=[]
    available_output_tokens=4096
    delivery_output_limit=4096
    source_change_mode=False
    fitted_prompt=""
'''+policy.WEB_DELIVERY+'''
'''+policy.SHARED+'''
    if True:
'''+policy.REPAIR_FIT+'''
    else:
        fitted=_fit_messages(model,system,history,prompt,delivery_output_limit,preserve_latest_code=preserve_existing_source(programming))
'''
        patched=policy.patch_coder(sample.encode()).decode()
        ast.parse(patched)
        self.assertEqual(patched.count('system+="\\n"+_swrlz_webpage_quality_policy'),2)
        self.assertEqual(patched.count("SWRLZ_WEBPAGE_QUALITY_POLICY_V1")>=2,True)
        self.assertIn('result={"status":"REJECT" if reasons else "PASS","reasons":reasons}',patched)
        self.assertIn('result["webPageQualityRisks"]=quality_flags',patched)
        self.assertEqual(patched.count('fitted=_fit_messages('),1)


class ReleaseReadinessTests(unittest.TestCase):
    def _gate(self, stage="RUNNING_APP_STARTING", native_ok=True):
        import types
        filename=Path(__file__).resolve().parent/"hf_webpage_quality_release.py"
        node=next(n for n in ast.parse(filename.read_text("utf-8")).body
                  if isinstance(n,ast.FunctionDef) and n.name=="healthy")
        class Clock:
            elapsed=0.
            def monotonic(self):return self.elapsed
            def sleep(self,seconds):self.elapsed+=seconds
        clock=Clock()
        events=[]
        def fake_get(path):
            if "native" in path:
                return {"backendSelected":native_ok,"nativeSETGET":native_ok,
                        "nativeLua":native_ok}
            return {"ok":True}
        ns={"time":clock,"SPACE":"kamiloki/Swyrlz",
            "get_status":fake_get,"emit":lambda *a,**kw:events.append((a,kw))}
        exec(compile(ast.Module(body=[node],type_ignores=[]),"<readiness>","exec"),ns)
        api=types.SimpleNamespace(get_space_runtime=lambda space:types.SimpleNamespace(stage=stage))
        return ns["healthy"](api,deadline=18),events

    def test_starting_but_functional_app_is_accepted_after_repeated_checks(self):
        accepted,events=self._gate(stage="RUNNING_APP_STARTING")
        self.assertTrue(accepted)
        self.assertEqual(events[-1][0][0],"SWRLZ_WEB_QUALITY_RUNTIME_PASS")

    def test_build_error_stage_is_not_accepted(self):
        accepted,events=self._gate(stage="BUILD_ERROR")
        self.assertFalse(accepted)

    def test_bad_valkey_response_is_not_accepted(self):
        accepted,events=self._gate(stage="RUNNING",native_ok=False)
        self.assertFalse(accepted)

if __name__=="__main__":unittest.main()
