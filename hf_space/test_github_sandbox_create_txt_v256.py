"""Sandbox CREATE_FILE authorization and scope contract tests; network calls stubbed."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_sandbox_create_txt as s


class SandboxTxtTest(unittest.TestCase):
    def setUp(self):
        s._pending.clear()
        self.user = {"id": "google:owner"}
        def fake_authorized(user):
            if not user or user.get("id") != "google:owner":
                raise s.WriteError("SANDBOX_OWNER_REQUIRED", 403)
            return "existing-user-oauth-token"
        self.authorization = patch.object(s, "_authorized", side_effect=fake_authorized)
        self.authorization.start()

    def tearDown(self):
        self.authorization.stop()
        s._pending.clear()

    def test_no_permission_by_default_or_unrecognized_owner(self):
        with self.assertRaises(s.WriteError):
            s.prepare(None, "ok.txt", "hello")
        with self.assertRaises(s.WriteError):
            s.prepare({"id": "google:unapproved"}, "ok.txt", "hello")

    def test_no_path_traversal_or_other_extensions(self):
        for name in ("../ok.txt", "/etc/passwd", "ok.md", "a/b.txt", ".hidden.txt", "x..txt", "a\\b.txt"):
            with self.subTest(name=name):
                with self.assertRaises(s.WriteError):
                    s._path(name)
        self.assertEqual(s._path("hello-swyrlz.txt"), "write-action-tests/hello-swyrlz.txt")

    def test_prepare_rejects_existing_file(self):
        with patch.object(s, "_request", return_value=(200, {})):
            with self.assertRaises(s.WriteError) as err:
                s.prepare(self.user, "existing.txt", "body")
        self.assertEqual(err.exception.code, "FILE_ALREADY_EXISTS")

    def test_approval_is_single_use_and_scoped(self):
        data = b"hello"
        def fake_request(method, path, token, body=None):
            if method == "GET" and not getattr(fake_request, "written", False):
                return 404, None
            if method == "PUT":
                self.assertEqual(path, "write-action-tests/ok.txt")
                self.assertNotIn("sha", body)
                fake_request.written = True
                return 201, {"commit": {"sha": "abc"}}
            return 200, {"content": "aGVsbG8="}
        with patch.object(s, "_request", side_effect=fake_request):
            prepared = s.prepare(self.user, "ok.txt", data.decode())
            with self.assertRaises(s.WriteError):
                s.confirm({"id": "google:someone-else"}, prepared["approvalToken"], True)
            # Non-owner has no authority and must not consume the owner's ticket.
            answer = s.confirm(self.user, prepared["approvalToken"], True)
            self.assertTrue(answer["verified"])
            self.assertEqual(answer["commitSha"], "abc")
            with self.assertRaises(s.WriteError):
                s.confirm(self.user, prepared["approvalToken"], True)

    def test_decline_never_writes(self):
        with patch.object(s, "_request", return_value=(404, None)) as request:
            prepared = s.prepare(self.user, "cancel.txt", "content")
            result = s.confirm(self.user, prepared["approvalToken"], False)
            self.assertEqual(result["code"], "USER_DECLINED")
            self.assertEqual(request.call_count, 1)

    def test_too_large_content(self):
        with self.assertRaises(s.WriteError):
            s._content("a" * (s.MAX_BYTES + 1))


if __name__ == "__main__":
    unittest.main()
