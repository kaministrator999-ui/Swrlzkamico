"""Regression: project repair must not use the last unrelated GitHub file."""
import base64
import hashlib
import importlib.util
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

root = pathlib.Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("html_context_v1_test", root/"api/html_project_context_v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SLUG = "interactive-3d-model-viewer"
thread = {"messages": [
    {"role":"assistant","meta":{"htmlProjectHandoff":{"project":SLUG,"state":"AWAITING_GITHUB_CREATE_APPROVAL"}}},
    {"role":"user","text":"@GitHub status HTML project interactive-3d-model-viewer"},
    {"role":"assistant","text":"Earlier GitHub source report: swrlz-review-test.txt"},
]}
request = ('The deployed 3D model viewer opens but is stuck on "Loading 3D Viewer". '
           "Inspect GitHub source, repair the existing project and redeploy.")

class ProjectContextTest(unittest.TestCase):
    def test_exact_regression(self):
        found = m.resolve(request, thread)
        self.assertEqual(found["path"], "html-projects/" + SLUG + "/index.html")
        self.assertNotIn("swrlz-review-test", str(found))
    def test_command_and_unrelated_file_unchanged(self):
        self.assertIsNone(m.resolve("@GitHub status HTML project " + SLUG, thread))
        self.assertIsNone(m.resolve("@GitHub inspect swrlz-review-test.txt", thread))
        self.assertIsNone(m.resolve("Hello", thread))
    def test_ambiguous_project_requires_explicit_reference(self):
        t = {"messages":[
            {"role":"assistant","meta":{"htmlProjectHandoff":{"project":"a-project"}}},
            {"role":"assistant","meta":{"htmlProjectHandoff":{"project":"b-project"}}}]}
        self.assertIsNone(m.resolve("Repair the deployed website", t))
        self.assertEqual(m.resolve("Repair HTML project b-project",t)["project"],"b-project")
    def test_assistant_prose_cannot_invent_project_identity(self):
        t={"messages":[{"role":"assistant","text":"I created project hidden-website"}]}
        self.assertIsNone(m.resolve("Repair the deployed website", t))
    def test_github_read_and_git_blob_integrity(self):
        src = '<script type="importmap">{"imports":{"three":"https://cdn.example/x"}}</script>'
        raw = src.encode()
        sha = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        publisher = types.ModuleType("github_html_publish_action_v1")
        publisher._authorized = lambda user: {"repo":"kaministrator999-ui/Swrlzkamico","branch":"main"}
        publisher._github = lambda auth, method, path: {"type":"file","encoding":"base64",
            "content":base64.b64encode(raw).decode(),"sha":sha}
        with patch.dict(sys.modules,{"github_html_publish_action_v1":publisher}), \
             patch("api.lightweight_webpage_inspector_v1.inspect_published", return_value={
                 "tier":"http", "deployedBytesMatch":False,
                 "functionalVerified":False, "issues":[{"code":"HTTP_NOT_TESTED"}]}):
            fetched=m.read_project_source("google:user",m.resolve(request,thread))
            self.assertEqual(fetched["blobSha"],sha)
            self.assertIn("external module URLs",m.evidence(m.resolve(request,thread),fetched))
            self.assertNotIn("swrlz-review-test.txt",m.evidence(m.resolve(request,thread),fetched).split("START OWNER SOURCE")[1])
            publisher._github=lambda a,b,c: {"type":"file","encoding":"base64",
                "content":base64.b64encode(raw).decode(),"sha":"0"*40}
            with self.assertRaisesRegex(ValueError,"INTEGRITY"):
                m.read_project_source("google:user",m.resolve(request,thread))

if __name__=="__main__":
    unittest.main()
