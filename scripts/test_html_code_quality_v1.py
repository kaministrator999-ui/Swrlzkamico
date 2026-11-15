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
    def test_aether_interpolated_hex_rgba(self):
        # Preserve Aether's actual interpolated-color failure, not merely
        # the easier literal rgba(#hex, opacity) variant.
        source = """<html><script>
        const config = {solid:{color:'#00f0ff'},chaos:{color:'#ffffff'}};
        const style = `rgba(__COLOR_TOKEN__, 0.15)`;
        </script></html>""".replace("__COLOR_TOKEN__", "$" + "{config.color}")
        findings = diagnose_html_candidate(source)
        self.assertTrue(any("interpolated-hex-rgba" in issue
                            for issue in findings["blocking"]))

    def test_no_false_positive_on_valid_css_and_scoped_pause(self):
        source = """<html><style>.a{background:rgba(0,240,255,.3)}</style><script>
        class A { pause(){this.isPaused=!this.isPaused;this.logSystem(this.isPaused?'Paused':'Resumed')} }
        </script></html>"""
        self.assertEqual(diagnose_html_candidate(source)["blocking"],[])
        base={"status":"PASS","reasons":["original"]}
        self.assertIs(extend_candidate_check(base,source),base)
    def test_neon_flux_actual_canvas_input_blocked(self):
        html = """<!doctype html><html><head><style>
        /* UI Overlay */
        #ui-layer { position:absolute; pointer-events: none; }
        header { pointer-events:auto; }
        </style></head><body><div id="ui-layer">
        <header>Header</header><canvas id="game-canvas"></canvas></div>
        <script>const canvas=document.getElementById('game-canvas');
        canvas.addEventListener('mousedown',()=>{});</script></body></html>"""
        report = diagnose_html_candidate(html)
        self.assertIn("canvas-pointer-inert", str(report["blocking"]))
        self.assertEqual(extend_candidate_check(
            {"status":"PASS","reasons":[]},html)["status"],"REJECT")
        fixed = html.replace("header { pointer-events:auto; }",
                             "header { pointer-events:auto; } #game-canvas {pointer-events:auto;touch-action:none;}")
        self.assertFalse(any("canvas-pointer-inert" in i
                             for i in diagnose_html_candidate(fixed)["blocking"]))

    def test_neon_flux_gradient_and_fps_error(self):
        html = """<html><style>canvas{background:radial-gradient(
            circle at 50% 50%, from 50% 50% transparent 10%, transparent 90%)}
            </style><canvas></canvas>
            <script>state.fps = Math.round((1000 / state.fpsTimer) * 60);</script></html>"""
        findings = diagnose_html_candidate(html)
        self.assertIn("invalid-radial-gradient-from", str(findings["blocking"]))
        self.assertIn("fps-fixed-60", str(findings["blocking"]))
        fixed = html.replace("from 50% 50% ", "").replace(
            "Math.round((1000 / state.fpsTimer) * 60)",
            "Math.round((frames * 1000) / elapsedMs)")
        self.assertFalse(diagnose_html_candidate(fixed)["blocking"])

    def test_initial_empty_canvas_warning_is_not_rejection(self):
        src = "<canvas></canvas><script>const particles:[];requestAnimationFrame(tick)</script>"
        diagnostics = diagnose_html_candidate(src)
        self.assertIn("initial-empty-canvas", str(diagnostics["warnings"]))
        self.assertEqual(extend_candidate_check({"status":"PASS"},src)["status"],"PASS")

    def test_pointer_inheritance_checks_do_not_block_unrelated_webpage(self):
        src = """<html><style>#ui-layer{pointer-events:none}
                  #game-canvas{pointer-events:auto}</style>
                  <div id='ui-layer'><canvas id='game-canvas'></canvas></div>
                  <script>canvas.addEventListener('pointermove',()=>{})</script></html>"""
        self.assertFalse(diagnose_html_candidate(src)["blocking"])

    def test_nonhtml_source_left_alone(self):
        self.assertFalse(diagnose_html_candidate("const rgba = '#00f0ff';")["inspected"])
    def test_warning_not_blocking(self):
        source="<canvas></canvas><script>window.addEventListener('mousemove', ()=>{});ctx.shadowBlur=10;ctx.arc(2,3,4,0,6);</script>"
        self.assertTrue(diagnose_html_candidate(source)["warnings"])
        self.assertEqual(extend_candidate_check({"status":"PASS"},source)["status"],"PASS")

if __name__ == "__main__":
    unittest.main()
