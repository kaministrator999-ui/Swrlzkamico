"""Offline regression suite for the bounded progressive project inspector."""
from __future__ import annotations
import hashlib
import io
import unittest
from unittest.mock import patch
from api.lightweight_webpage_inspector_v1 import inspect_files, inspect_published, _resolve

class InspectionTests(unittest.TestCase):
    def test_cdn_importmap_blocked_by_real_project_policy(self):
        html='''<!doctype html><script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js"}}</script><script type="module">import * as THREE from "three";</script><canvas></canvas>'''
        r=inspect_files({"index.html":html})
        self.assertFalse(r["staticPass"])
        self.assertTrue(r["renderingRequiredForFullVerification"])
        self.assertIn("CSP_EXTERNAL_MODULE", {x["code"] for x in r["issues"]})
        self.assertFalse(r["functionalVerified"])

    def test_local_bundles_are_static_pass_but_not_rendering_pass(self):
        html='<html><script src="./vendor.js"></script><canvas></canvas><button>Spin</button></html>'
        r=inspect_files({"index.html":html,"vendor.js":"const x = 1;"})
        self.assertTrue(r["staticPass"])
        self.assertFalse(r["functionalVerified"])
        self.assertTrue(r["renderingRequiredForFullVerification"])

    def test_missing_local_asset_flag(self):
        r=inspect_files({"index.html":'<link rel="stylesheet" href="styles.css">'})
        self.assertIn("LOCAL_ASSET_MISSING", {x["code"] for x in r["issues"]})

    def test_external_script_block(self):
        r=inspect_files({"index.html":'<script src="https://example.com/a.js"></script>'})
        self.assertIn("CSP_EXTERNAL_ASSET", {x["code"] for x in r["issues"]})

    def test_inline_script_syntax_not_claimed_verified(self):
        r=inspect_files({"index.html":'<script>const x = ;</script>'})
        self.assertFalse(r["syntaxVerified"])
        self.assertFalse(r["functionalVerified"])
        self.assertEqual(len(r["scripts"]),1)

    def test_escape_and_malicious_paths(self):
        self.assertEqual(_resolve("index.html","../../x.js")[1],"escape")
        with self.assertRaises(ValueError):
            inspect_files({"../escape.js":"hi","index.html":"<html></html>"})

    def test_opaque_origin_bounded_http_match(self):
        class Response:
            status=200
            headers={"Content-Security-Policy":"sandbox allow-scripts; connect-src 'none'; default-src 'none'",
                     "X-Content-Type-Options":"nosniff"}
            def __init__(self,body):self.body=body
            def read(self,n):return self.body[:n]
            def __enter__(self):return self
            def __exit__(self,*args):return False
        def fake_open(self,req,timeout=0):
            self.assertTrue(req.full_url.startswith("https://kamiloki-swyrlz.hf.space/api/html-projects/example/"))
            return Response(b"<html></html>")
        with patch("urllib.request.OpenerDirector.open",autospec=True,side_effect=fake_open):
            res=inspect_published("example",{"index.html":b"<html></html>"})
        self.assertTrue(res["deployedBytesMatch"])
        self.assertFalse(res["functionalVerified"])

    def test_redirects_rejected(self):
        from api.lightweight_webpage_inspector_v1 import _NoRedirect
        with self.assertRaises(ValueError):
            _NoRedirect().redirect_request(None,None,302,"redirect",{},"https://internal.local/")
    def test_disallow_arbitrary_host_argument(self):
        with self.assertRaises(ValueError):
            inspect_published("https://127.0.0.1/admin",{"index.html":"a"})

if __name__ == "__main__":
    unittest.main()
