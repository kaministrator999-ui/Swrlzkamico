"""Integration smoke for real HTTP local §E lobby discovery, without Internet."""
import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lan_bridge import LANState, PROTOCOL, make_handler, safe_local_ip
from http.server import ThreadingHTTPServer


class Bridge(unittest.TestCase):
    def test_local_only(self):
        self.assertTrue(safe_local_ip("192.168.1.55", "192.168.1.3"))
        self.assertFalse(safe_local_ip("192.168.2.7", "192.168.1.3"))
        self.assertFalse(safe_local_ip("8.8.8.8", "192.168.1.3"))

    def test_host_status_and_list(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "index.html").write_text("SHEEP TAG LOCAL", encoding="utf8")
            state = LANState(ip="127.0.0.1")
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(state, Path(directory)))
            state.port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            url = "http://127.0.0.1:%d" % state.port

            def get(path):
                with urllib.request.urlopen(url + path, timeout=2) as r:
                    return json.loads(r.read())

            def request(path, method, data=None, origin=None):
                body = json.dumps(data).encode() if data is not None else None
                headers = {"Content-Type": "application/json"}
                if origin:
                    headers["Origin"] = origin
                req = urllib.request.Request(url + path, body, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=2) as r:
                    return json.loads(r.read())

            try:
                status = get("/api/lan/status")
                self.assertEqual(status["protocol"], PROTOCOL)
                self.assertTrue(status["canHost"])
                self.assertIsNone(status["game"])
                self.assertEqual(get("/api/lan/games")["games"], [])
                hosted = request("/api/lan/host", "POST", {"name": "Sheep Tag QA"})
                self.assertEqual(hosted["game"]["name"], "Sheep Tag QA")
                directory_list = get("/api/lan/games?scan=1")["games"]
                self.assertEqual(len(directory_list), 1)
                self.assertTrue(directory_list[0]["self"])
                self.assertEqual(directory_list[0]["players"], 1)
                host_id = hosted["game"]["id"]
                self.assertTrue(request("/api/lan/register", "POST",
                                        {"gameId": host_id, "playerId": "test-device"})["joined"])
                self.assertEqual(get("/api/lan/status")["game"]["players"], 2)
                with self.assertRaises(urllib.error.HTTPError) as bad:
                    request("/api/lan/host", "POST", {"name": "evil"}, "http://evil.example")
                self.assertEqual(bad.exception.code, 403)
                request("/api/lan/host", "DELETE")
                self.assertIsNone(get("/api/lan/status")["game"])
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
