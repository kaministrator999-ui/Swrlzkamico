"""Mocked integration tests for exact SHA-bound GitHub edits; no network."""
import base64
import importlib.util
import pathlib
import sys
import types
import unittest

class Error(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status
        super().__init__(code)

fake = types.ModuleType("github_general_create_v262")
fake.CreateFileError = Error
fake.safe_path = lambda p: p if p and p != "../escape" else (_ for _ in ()).throw(Error("INVALID_FILE_PATH"))
state = {"sha": "a" * 40, "content": "old\n", "writes": 0, "auth": True}
def authorize(user, expected_repo=None):
    if not state["auth"] or user != "google:owner":
        raise Error("GITHUB_WRITE_SCOPE_REQUIRED", 403)
    if expected_repo and expected_repo != "owner/repo":
        raise Error("SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED", 403)
    return {"repo": "owner/repo", "branch": "main", "token": "test"}
def github(method, auth, path, payload=None):
    assert path == "src/file.py"
    if method == "GET":
        return 200, {"sha": state["sha"], "type": "file", "encoding": "base64",
                     "content": base64.b64encode(state["content"].encode()).decode()}
    if method == "PUT":
        if payload["sha"] != state["sha"]:
            raise Error("GITHUB_FILE_EXISTS_OR_CONFLICT", 409)
        state["content"] = base64.b64decode(payload["content"]).decode()
        state["sha"] = "b" * 40
        state["writes"] += 1
        return 200, {"commit": {"sha": "c" * 40}}
    raise AssertionError(method)
fake._authorize, fake._github = authorize, github
sys.modules["github_general_create_v262"] = fake
spec = importlib.util.spec_from_file_location(
    "github_review_update_v1",
    pathlib.Path(__file__).resolve().parents[1] / "api/github_review_update_v1.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

class TestUpdate(unittest.TestCase):
    def setUp(self):
        state.update(sha="a" * 40, content="old\n", writes=0, auth=True)
        with module._lock:
            module._pending.clear()
    def proposal(self):
        return module.prepare("google:owner", "src/file.py", "new\n")
    def test_proposal_and_verified_write(self):
        p = self.proposal()
        self.assertEqual(p["before"], "old\n")
        self.assertIn("+new", p["diff"])
        self.assertEqual(state["writes"], 0)
        receipt = module.confirm("google:owner", p["approvalToken"], True)
        self.assertTrue(receipt["verified"])
        self.assertEqual(state["content"], "new\n")
        self.assertEqual(state["writes"], 1)
        with self.assertRaises(Error):
            module.confirm("google:owner", p["approvalToken"], True)
    def test_reject_no_mutation(self):
        p=self.proposal()
        self.assertFalse(module.confirm("google:owner",p["approvalToken"],False)["ok"])
        self.assertEqual(state["writes"],0)
    def test_other_account_cannot_consume(self):
        p=self.proposal()
        with self.assertRaises(Error):
            module.confirm("google:other",p["approvalToken"],True)
        self.assertEqual(state["writes"],0)
        self.assertTrue(module.confirm("google:owner",p["approvalToken"],True)["verified"])
    def test_changed_sha_prevents_write(self):
        p=self.proposal()
        state["sha"]="f"*40
        with self.assertRaises(Error) as ctx:
            module.confirm("google:owner",p["approvalToken"],True)
        self.assertEqual(ctx.exception.code,"SOURCE_CHANGED_SINCE_PREVIEW")
        self.assertEqual(state["writes"],0)
    def test_oauth_rechecked(self):
        p=self.proposal()
        state["auth"]=False
        with self.assertRaises(Error):
            module.confirm("google:owner",p["approvalToken"],True)
        self.assertEqual(state["writes"],0)
    def test_expired_rejected(self):
        p=self.proposal()
        with module._lock:
            module._pending[p["approvalToken"]]["expires"]=0
        with self.assertRaises(Error):
            module.confirm("google:owner",p["approvalToken"],True)
        self.assertEqual(state["writes"],0)
    def test_binary_rejected(self):
        state["content"]="old\n"
        with self.assertRaises(Error):
            module.prepare("google:owner","../escape","new")

if __name__=="__main__":unittest.main()
