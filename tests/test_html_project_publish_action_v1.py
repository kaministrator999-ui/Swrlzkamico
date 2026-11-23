"""No-network owner approval contract tests for the §C HTML release button."""
import base64
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from api import html_project_publish_action_v1 as m

HEAD = "a" * 40
INDEX = b"<!doctype html><title>Approved project</title>"
CALLS = []


def fake_github(method, token, path, payload=None):
    CALLS.append((method, path, payload))
    if "/git/ref/heads/" in path:
        return 200, {"object": {"sha": HEAD}}
    if "/git/trees/" in path:
        return 200, {"truncated": False, "tree": [
            {"path": "html-projects/sample/", "type": "tree", "mode": "040000"},
            {"path": "html-projects/sample/index.html", "type": "blob", "mode": "100644", "sha": "b"*40, "size": len(INDEX)},
        ]}
    if "/contents/" in path:
        return 200, {"content": base64.b64encode(INDEX).decode()}
    if "/dispatches" in path:
        return 204, {}
    if "/runs?" in path:
        return 200, {"workflow_runs": []}
    raise AssertionError("Unexpected endpoint " + path)


class ProjectApprovalTests(unittest.TestCase):
    def setUp(self):
        CALLS.clear()
        m._PENDING.clear()
        m._DEPLOYMENTS.clear()
        self.authorizer = patch.object(m, "_authorize", return_value={
            "repo":m.REPO,"branch":"main","token":"test-token"})
        self.github = patch.object(m, "_github", side_effect=fake_github)
        self.authorizer.start()
        self.github.start()
        self.addCleanup(self.authorizer.stop)
        self.addCleanup(self.github.stop)

    def test_requires_one_use_owner_confirm_and_source_pin(self):
        preview = m.prepare("google:owner", "sample")
        self.assertEqual(preview["sourceSha"], HEAD)
        self.assertEqual(preview["previewHtml"], INDEX.decode())
        self.assertEqual(preview["count"], 1)
        self.assertEqual(preview["files"][0]["path"], "index.html")
        self.assertEqual(preview["approvalRequired"], True)
        self.assertEqual(sum(method == "POST" for method,_,_ in CALLS), 0)
        with self.assertRaises(HTTPException):
            m.confirm("google:other", preview["approvalToken"], True)
        self.assertEqual(sum(method == "POST" for method,_,_ in CALLS), 0)

        approved = m.prepare("google:owner", "sample")
        issued = m.confirm("google:owner", approved["approvalToken"], True)
        self.assertTrue(issued["ok"])
        dispatches = [p for method,_,p in CALLS if method == "POST"]
        self.assertEqual(len(dispatches), 1)
        self.assertEqual(dispatches[0]["inputs"]["source_sha"], HEAD)
        self.assertEqual(dispatches[0]["inputs"]["project"], "sample")
        self.assertEqual(dispatches[0]["inputs"]["request_nonce"], issued["requestNonce"])
        with self.assertRaises(HTTPException):
            m.confirm("google:owner", approved["approvalToken"], True)
        self.assertEqual(len([p for method,_,p in CALLS if method == "POST"]), 1)

    def test_decline_and_reject_bad_project(self):
        with self.assertRaises(HTTPException):
            m.prepare("google:owner", "../bad")
        preview = m.prepare("google:owner", "sample")
        self.assertEqual(m.confirm("google:owner", preview["approvalToken"], False)["code"],"OWNER_DECLINED")
        self.assertEqual(sum(method == "POST" for method,_,_ in CALLS), 0)

    def test_branch_moved_requires_new_review(self):
        preview = m.prepare("google:owner", "sample")
        with patch.object(m, "_head", return_value="b"*40):
            with self.assertRaises(HTTPException) as error:
                m.confirm("google:owner", preview["approvalToken"], True)
            self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(sum(method == "POST" for method,_,_ in CALLS), 0)


if __name__ == "__main__":
    unittest.main()
