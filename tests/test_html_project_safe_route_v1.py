"""Executable, offline contract tests for the §C isolated HTML project route."""
import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from api import html_project_safe_route_v1 as route


class SafeServingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.project = self.root / "published-html-projects" / "sample"
        self.project.mkdir(parents=True)
        (self.project / "index.html").write_text(
            "<!doctype html><title>Working project</title>"
            "<script>document.body.dataset.loaded='yes'</script>")
        (self.project / "main.js").write_text("document.body.dataset.js='yes'")
        app = FastAPI()
        route.install(app, self.root)
        self.client = TestClient(app)

    def test_html_must_have_opaque_origin_sandbox(self):
        response = self.client.get("/api/html-projects/sample/index.html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Working project", response.text)
        csp = response.headers["content-security-policy"]
        self.assertIn("sandbox allow-scripts;", csp)
        self.assertNotIn("allow-same-origin", csp)
        self.assertIn("connect-src 'none'", csp)
        self.assertIn("form-action 'none'", csp)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")

    def test_project_root_and_relative_js(self):
        self.assertEqual(self.client.get("/api/html-projects/sample/").status_code, 200)
        js = self.client.get("/api/html-projects/sample/main.js")
        self.assertEqual(js.status_code, 200)
        self.assertIn("javascript", js.headers["content-type"])
        self.assertEqual(js.headers["access-control-allow-origin"], "*")

    def test_invalid_slug_and_asset(self):
        for slug, asset in [("UPPER", "index.html"), ("hidden_", "index.html"),
                            ("sample", ".secret.js"), ("sample", "payload.py"),
                            ("sample", "subdir/../index.html")]:
            with self.subTest(slug=slug, asset=asset), self.assertRaises(HTTPException):
                route.resolve_asset(self.root/"published-html-projects", slug, asset)

    def test_missing_and_symlink_assets_denied(self):
        self.assertEqual(self.client.get("/api/html-projects/sample/no.html").status_code, 404)
        external = self.root / "outside.html"
        external.write_text("<title>private</title>")
        (self.project / "out.html").symlink_to(external)
        self.assertEqual(self.client.get("/api/html-projects/sample/out.html").status_code, 404)

    def test_private_tree_not_mounted(self):
        self.assertEqual(
            self.client.get("/published-html-projects/sample/index.html").status_code, 404)
        self.assertEqual(
            self.client.get("/chat/%C2%A7wyrlz/projects/sample/index.html").status_code, 404)


if __name__ == "__main__":
    unittest.main()
