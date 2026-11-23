"""Offline checks for static project origin isolation and live Station patch scope."""
from pathlib import Path
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.html_project_routes_v1 import MARKER, SANDBOX_POLICY, install
from scripts.hf_chat_html_project_route_release_v1 import ANCHOR, INJECTION, prepare


class RouteTests(unittest.TestCase):
    def test_route_sandbox_on_direct_html_and_svg(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "chat" / "§wyrlz" / "projects" / "sample"
            folder.mkdir(parents=True)
            (folder / "index.html").write_text("<!doctype html><script>window.test=true</script>")
            (folder / "image.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            app = FastAPI()
            install(app, temp)
            client = TestClient(app)
            for path in ("/projects/sample/index.html", "/projects/sample/image.svg"):
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers["content-security-policy"], SANDBOX_POLICY)
                self.assertIn("sandbox allow-scripts", response.headers["content-security-policy"])
                self.assertNotIn("allow-same-origin", response.headers["content-security-policy"])
                self.assertNotIn("allow-forms", response.headers["content-security-policy"])
                self.assertNotIn("allow-top-navigation", response.headers["content-security-policy"])
                self.assertEqual(response.headers["x-content-type-options"], "nosniff")
            status = client.get("/api/html-projects/security").json()
            self.assertEqual(status["contract"], MARKER)
            self.assertFalse(status["sameOriginPermission"])

    def test_only_one_station_anchor(self):
        station = ("from fastapi import FastAPI\n"
                   "from fastapi.staticfiles import StaticFiles\n"
                   "from pathlib import Path\n"
                   "ROOT=Path('.')\napp=FastAPI()\n" + ANCHOR + "\n").encode()
        updated = prepare(station, Path("api/html_project_routes_v1.py").read_bytes())
        self.assertEqual(updated.count(INJECTION.encode()), 1)
        with self.assertRaises(RuntimeError):
            prepare(updated, Path("api/html_project_routes_v1.py").read_bytes())
        with self.assertRaises(RuntimeError):
            prepare(b"app=1\n", Path("api/html_project_routes_v1.py").read_bytes())


if __name__ == "__main__":
    unittest.main()
