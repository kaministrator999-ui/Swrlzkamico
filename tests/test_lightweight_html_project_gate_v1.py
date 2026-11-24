"""End-to-end static/Node project gate tests (no Chromium)."""
from __future__ import annotations
import shutil
import unittest
from unittest.mock import patch
from scripts import verify_html_project_lightweight_v1 as verifier

class ProjectGateTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is optional outside CI")
    def test_local_js_syntax_passes_without_browser(self):
        file_map={"index.html":b'<html><script src="./app.js"></script><button>Start</button></html>',
                  "app.js":b'document.querySelector("button").onclick = () => 42;'}
        with patch.object(verifier.publishing,"local_files",return_value=list(file_map.items())):
            result=verifier.run("sample",require_node=True)
        self.assertTrue(result["staticPass"])
        self.assertTrue(result["syntaxVerified"])
        self.assertFalse(result["functionalVerified"])
        self.assertEqual(result["status"],"STATIC_PASS_INTERACTIONS_UNVERIFIED")

    @unittest.skipUnless(shutil.which("node"), "Node is optional outside CI")
    def test_invalid_javascript_fails_closed(self):
        files=[("index.html",b"<script>const x = ;</script>")]
        with patch.object(verifier.publishing,"local_files",return_value=files):
            result=verifier.run("sample")
        self.assertFalse(result["staticPass"])
        self.assertIn("SCRIPT_SYNTAX_INVALID",{i["code"] for i in result["issues"]})

    @unittest.skipUnless(shutil.which("node"), "Node is optional outside CI")
    def test_remote_threejs_csp_failure_blocks_publication(self):
        html=b'''<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/three.js"}}</script>
<script type="module">import * as THREE from "three";</script><canvas></canvas>'''
        with patch.object(verifier.publishing,"local_files",return_value=[("index.html",html)]):
            result=verifier.run("sample")
        self.assertFalse(result["staticPass"])
        self.assertTrue(result["renderingRequiredForFullVerification"])
        self.assertIn("CSP_EXTERNAL_MODULE",{i["code"] for i in result["issues"]})

if __name__ == "__main__":
    unittest.main()
