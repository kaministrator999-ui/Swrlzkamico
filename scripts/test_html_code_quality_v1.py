from __future__ import annotations
import unittest
from html_code_quality_v1 import quality_guidance, diagnose_html_candidate, extend_candidate_check


class QualityTests(unittest.TestCase):
    def test_no_noncode_contamination(self):
        self.assertEqual(quality_guidance("How is your day?", {"codingTask": False}), "")
    def test_new_and_existing_distinction(self):
        new = quality_guidance("Make a cool HTML page", {"codingTask": True, "projectContext":"new"})
        old = quality_guidance("Improve it", {"codingTask": True, "projectContext":"existing", "intentContract":{"artifactType":"web-page"}})
        self.assertIn("New creation", new)
        self.assertIn("Existing-source edit", old)
        self.assertIn("Pointer Events", new)
        self.assertIn("preserve", old)
        self.assertIn("device", new)
    def test_known_aether_errors_are_blocking(self):
        source = """<!doctype html><html><style>.a{stroke:rgba(#00f0ff,0.5)}</style><canvas></canvas><script>
        class A { pause(){ this.isPaused=!this.isPaused; this.logSystem(isPaused ? 'Pause' : 'Play'); } }
        window.addEventListener('mousemove',()=>{});
        </script></html>"""
        check = diagnose_html_candidate(source)
        self.assertEqual(len(check["blocking"]), 2)
        self.assertIn("mouse-only-canvas", check["warnings"][0])
        merged = extend_candidate_check({"status":"PASS","reasons":[]},source)
        self.assertEqual(merged["status"],"REJECT")
        self.assertEqual(len(merged["reasons"]),2)
    def test_no_false_positive_on_valid_css_and_scoped_pause(self):
        source = """<html><style>.a{background:rgba(0,240,255,.3)}</style><script>
        class A { pause(){this.isPaused=!this.isPaused;this.logSystem(this.isPaused?'Paused':'Resumed')} }
        </script></html>"""
        self.assertEqual(diagnose_html_candidate(source)["blocking"],[])
        base={"status":"PASS","reasons":["original"]}
        self.assertIs(extend_candidate_check(base,source),base)
    def test_nonhtml_source_left_alone(self):
        self.assertFalse(diagnose_html_candidate("const rgba = '#00f0ff';")["inspected"])
    def test_warning_not_blocking(self):
        source="<canvas></canvas><script>window.addEventListener('mousemove', ()=>{});ctx.shadowBlur=10;ctx.arc(2,3,4,0,6);</script>"
        self.assertTrue(diagnose_html_candidate(source)["warnings"])
        self.assertEqual(extend_candidate_check({"status":"PASS"},source)["status"],"PASS")

if __name__ == "__main__":
    unittest.main()
