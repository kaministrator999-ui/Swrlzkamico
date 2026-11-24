"""Offline owner-approval, atomic commit, source identity and no-overwrite tests."""
import base64
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
publisher = types.ModuleType("github_html_publish_action_v1")
publisher.REPO = "kaministrator999-ui/Swrlzkamico"
publisher.MAX_FILES = 48
publisher.MAX_BYTES = 1_000_000
class PublishActionError(Exception):
    def __init__(self, code):
        self.code = code
publisher.PublishActionError = PublishActionError
publisher._authorized = lambda user_id: {
    "token": "stub", "repo": publisher.REPO, "branch": "main"}
publisher._head = lambda auth: "a"*40
publisher._github = lambda *args, **kwargs: {}
publisher.prepare = lambda user_id, thread_id, slug: {
    "project": slug, "sourceSha": "e"*40,
    "repo": publisher.REPO, "branch": "main",
    "files": [{"path": "index.html", "bytes": 50}],
    "bytes": 50,
    "destinationPrefix": "published-html-projects/"+slug+"/",
}
sys.modules[publisher.__name__] = publisher
spec = importlib.util.spec_from_file_location(
    "html_handoff_under_test", ROOT/"api/github_html_project_handoff_v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def artifact(content='<!doctype html><title>3D Model Viewer</title><button>Rotate</button>'):
    files = [{"path": "index.html", "language": "html", "content": content},
             {"path": "style.css", "language": "css", "content": "body{margin:0}"}]
    return {"id": "artifact-1", "type": "code", "currentRevision": 1,
            "currentSourceHash": m._source_hash(files), "files": files}
REQUEST = {"kind": "html-project-generate-and-publish", "requestedSlug": ""}

class HtmlArtifactHandoffTest(unittest.TestCase):
    def setUp(self):
        m._pending.clear()

    def test_natural_language_intent_and_refusals(self):
        request = ("Create an interactive futuristic 3D model viewer webpage "
                   "with rotation, zoom and wireframe. Create files in GitHub and "
                   "publish to our existing Hugging Face Space after my approval.")
        self.assertEqual(m.intent(request)["kind"], REQUEST["kind"])
        self.assertIsNone(m.intent("Make a cool HTML page"))
        self.assertTrue(m.is_saved_review_request("@GitHub review saved HTML project"))
        self.assertFalse(m.is_saved_review_request("review the old test project please"))
        self.assertIsNone(m.intent("Create a webpage but do not publish it in GitHub"))
        self.assertIsNone(m.intent("Review a deployed HTML page on GitHub"))

    def test_stage_has_no_repository_mutation(self):
        with patch.object(publisher, "_github", side_effect=AssertionError("GitHub touched")):
            review = m.stage("google:owner", "thread", artifact(), REQUEST)
        self.assertTrue(m.has_pending("google:owner", "thread"))
        self.assertEqual(review["data"]["project"], "3d-model-viewer")
        self.assertEqual(review["data"]["mode"], "create")
        self.assertEqual(review["data"]["sourceSha"], artifact()["currentSourceHash"])
        self.assertEqual(len(review["data"]["files"]), 2)
        self.assertNotIn("content", review["data"]["files"][0])
        self.assertEqual(m.confirm("google:owner", "thread", False)["text"].startswith(
            "GitHub project creation rejected."), True)
        self.assertFalse(m.has_pending("google:owner", "thread"))
        with self.assertRaises(m.HandoffError):
            m.confirm("google:owner", "thread", True)

    def test_source_change_and_unsupported_paths_fail_closed(self):
        bad = artifact()
        bad["files"][0]["content"] = "altered"
        with self.assertRaisesRegex(m.HandoffError, "HASH_MISMATCH"):
            m.stage("google:owner", "thread", bad, REQUEST)
        bad = artifact()
        bad["files"][0]["path"] = "../index.html"
        bad["currentSourceHash"] = m._source_hash(bad["files"])
        with self.assertRaisesRegex(m.HandoffError, "PATH_UNSAFE"):
            m.stage("google:owner", "thread", bad, REQUEST)
        with self.assertRaisesRegex(m.HandoffError, "SIGN_IN_REQUIRED"):
            m.stage("guest", "thread", artifact(), REQUEST)
        bad = artifact('<script src="https://cdn.example/three.js"></script>')
        with self.assertRaisesRegex(m.HandoffError, "REMOTE_DEPENDENCY"):
            m.stage("google:owner", "thread", bad, REQUEST)

    def test_approved_multi_file_git_commit_then_separate_publish_review(self):
        src = artifact()
        original = {f["path"]: f["content"].encode("utf-8") for f in src["files"]}
        calls = []
        def request(auth, method, path, **kw):
            calls.append((method, path))
            if method == "GET" and path.startswith("git/commits/"):
                return {"tree": {"sha": "b"*40}}
            if method == "GET" and path.startswith("git/trees/"):
                return {"truncated": False, "tree": []}
            if method == "POST" and path == "git/blobs":
                return {"sha": "c"*40}
            if method == "POST" and path == "git/trees":
                self.assertEqual(len(kw["data"]["tree"]), 2)
                self.assertTrue(all(x["path"].startswith("html-projects/3d-model-viewer/")
                                    for x in kw["data"]["tree"]))
                return {"sha": "d"*40}
            if method == "POST" and path == "git/commits":
                self.assertEqual(kw["data"]["parents"], ["a"*40])
                return {"sha": "e"*40}
            if method == "PATCH":
                self.assertFalse(kw["data"]["force"])
                return None
            if method == "GET" and path.startswith("contents/"):
                return {"encoding": "base64", "content": base64.b64encode(
                    original[path.rsplit("/", 1)[-1]]).decode()}
            raise AssertionError((method, path))
        with patch.object(publisher, "_github", side_effect=request):
            m.stage("google:owner", "thread", src, REQUEST)
            receipt = m.confirm("google:owner", "thread", True)
        self.assertIn("All generated file bytes were verified", receipt["text"])
        self.assertEqual(receipt["widget"]["data"]["project"], "3d-model-viewer")
        self.assertEqual(sum(method == "PATCH" for method, path in calls), 1)
        self.assertFalse(m.has_pending("google:owner", "thread"))

    def test_only_last_saved_review_binds_late_approval(self):
        saved={"messages":[
            {"role":"assistant","meta":{"htmlProjectHandoff":{"state":"AWAITING_GITHUB_CREATE_APPROVAL"}}}]}
        self.assertTrue(m.last_assistant_review(saved))
        saved["messages"].append({"role":"assistant","meta":{},"text":"Different discussion"})
        self.assertFalse(m.last_assistant_review(saved))
        saved["messages"][-1]["meta"]["widgets"]=[
            {"kind":"github-html-publish-review","data":{"project":"sample"}}]
        self.assertTrue(m.last_assistant_review(saved))

    def test_approved_and_expired_review_are_deterministic(self):
        self.assertTrue(m.is_decision("Approved"))
        self.assertTrue(m.is_decision("yes"))
        self.assertFalse(m.is_decision("Deploy it somewhere else"))
        m.stage("google:owner", "thread-expired", artifact(), REQUEST)
        with m._lock:
            m._pending[("google:owner", "thread-expired")]["expires"] -= m.TTL + 1
        self.assertFalse(m.has_pending("google:owner", "thread-expired"))
        self.assertTrue(m.has_approval_record("google:owner", "thread-expired"))
        with patch.object(publisher, "_github", side_effect=AssertionError("Expired approval touched GitHub")):
            with self.assertRaisesRegex(m.HandoffError, "APPROVAL_EXPIRED"):
                m.confirm("google:owner", "thread-expired", m.decision_approved("Approved"))
        self.assertFalse(m.has_approval_record("google:owner", "thread-expired"))

    def test_existing_project_is_never_overwritten(self):
        calls = []
        def request(auth, method, path, **kw):
            calls.append((method, path))
            if path.startswith("git/commits/"):
                return {"tree": {"sha": "b"*40}}
            return {"truncated": False, "tree": [
                {"path": "html-projects/3d-model-viewer/index.html", "type": "blob"}]}
        with patch.object(publisher, "_github", side_effect=request):
            m.stage("google:owner", "thread", artifact(), REQUEST)
            with self.assertRaisesRegex(m.HandoffError, "ALREADY_EXISTS"):
                m.confirm("google:owner", "thread", True)
        self.assertFalse(any(method in ("POST", "PATCH") for method, path in calls))

if __name__ == "__main__":
    unittest.main()
