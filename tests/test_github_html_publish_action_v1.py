"""Offline proof of owner-bound, one-use GitHub HTML release approval."""
import base64
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

class FakeCreateError(Exception):
    def __init__(self,code):
        self.code=code

fake=types.ModuleType("github_general_create_v262")
fake.CreateFileError=FakeCreateError
fake._authorize=lambda user_id,repo: {"token":"fake-never-log","repo":repo,"branch":"main"}
sys.modules["github_general_create_v262"]=fake
spec=importlib.util.spec_from_file_location(
    "html_publish_under_test",
    Path(__file__).parents[1]/"api/github_html_publish_action_v1.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SHA="a"*40
AUTH={"token":"stub","repo":m.REPO,"branch":"main"}

class PublishApprovalTests(unittest.TestCase):
    def setUp(self):
        m._pending.clear()

    def test_exact_commands_only(self):
        self.assertEqual(m.command("@GitHub publish HTML project sample"),("publish","sample"))
        self.assertEqual(m.command("@GitHub status HTML project sample"),("status","sample"))
        self.assertIsNone(m.command("please publish every project"))
        self.assertIsNone(m.command("@GitHub publish HTML project ../oops"))
        self.assertIsNone(m.command("@GitHub publish HTML project sample\nyes"))

    def test_owner_approval_one_use_and_decline(self):
        preview={"repo":m.REPO,"branch":"main","project":"sample",
                 "sourceSha":SHA,"files":[{"path":"index.html","bytes":24}],
                 "bytes":24,"url":m._url("sample")}
        dispatch=[]
        def github(method,path,data=None,**kwargs):
            dispatch.append((method,path,data))
            return None
        with patch.object(m,"_authorized",return_value=AUTH),\
             patch.object(m,"_head",return_value=SHA),\
             patch.object(m,"_manifest",return_value=preview),\
             patch.object(m,"_github",side_effect=lambda auth,method,path,**kwargs: github(method,path,**kwargs)):
            staged=m.prepare("google:owner","thread1","sample")
            self.assertEqual(staged["sourceSha"],SHA)
            self.assertNotIn("token",staged)
            self.assertTrue(m.has_pending("google:owner","thread1"))
            rejected=m.confirm("google:owner","thread1",False)
            self.assertFalse(rejected["dispatched"])
            self.assertFalse(dispatch)
            with self.assertRaises(m.PublishActionError):
                m.confirm("google:owner","thread1",True)
            m.prepare("google:owner","thread1","sample")
            accepted=m.confirm("google:owner","thread1",True)
            self.assertTrue(accepted["dispatched"])
            self.assertEqual(len(dispatch),1)
            self.assertEqual(dispatch[0][0],"POST")
            self.assertEqual(dispatch[0][2]["inputs"]["approved"],"yes")
            self.assertEqual(dispatch[0][2]["inputs"]["source_sha"],SHA)
            with self.assertRaises(m.PublishActionError):
                m.confirm("google:owner","thread1",True)

    def test_branch_changed_fails_closed(self):
        preview={"repo":m.REPO,"branch":"main","project":"sample","sourceSha":SHA}
        with patch.object(m,"_authorized",return_value=AUTH),\
             patch.object(m,"_head",side_effect=[SHA,"b"*40]),\
             patch.object(m,"_manifest",return_value=preview),\
             patch.object(m,"_github") as req:
            m.prepare("google:owner","thread","sample")
            with self.assertRaises(m.PublishActionError) as error:
                m.confirm("google:owner","thread",True)
            self.assertEqual(error.exception.code,"SOURCE_CHANGED_REPREPARE")
            req.assert_not_called()

    def test_index_and_symlink_preflight(self):
        tree={"truncated":False,"tree":[
            {"path":"html-projects/sample/index.html","type":"blob","mode":"100644",
             "size":20,"sha":"e"*40}]}
        def req(auth,method,path,**kwargs):
            return {"tree":{"sha":"c"*40}} if "/commits/" in path else tree
        with patch.object(m,"_github",side_effect=req):
            preview=m._manifest(AUTH,SHA,"sample")
            self.assertEqual(preview["bytes"],20)
            self.assertEqual(preview["indexGitBlobSha"],"e"*40)
            tree["tree"][0]["mode"]="120000"
            with self.assertRaises(m.PublishActionError) as error:
                m._manifest(AUTH,SHA,"sample")
            self.assertEqual(error.exception.code,"PROJECT_SYMLINK_FORBIDDEN")

    def test_status_never_calls_live_verified_without_csp(self):
        page=b"<!doctype html><title>sample</title>"
        run={"display_title":"HTML sample \u00b7 "+SHA,"status":"completed",
             "conclusion":"success","html_url":"https://github.com/"+m.REPO+"/actions/runs/123"}
        def req(auth,method,path,**kwargs):
            if path.endswith("/runs"):
                return {"workflow_runs":[run]}
            return {"encoding":"base64","content":base64.b64encode(page).decode()}
        good=types.SimpleNamespace(
            status_code=200,content=page,headers={
                "Content-Security-Policy":"sandbox allow-scripts; connect-src 'none'",
                "X-Content-Type-Options":"nosniff"})
        bad=types.SimpleNamespace(
            status_code=200,content=page,headers={
                "Content-Security-Policy":"default-src 'self'",
                "X-Content-Type-Options":"nosniff"})
        with patch.object(m,"_authorized",return_value=AUTH),\
             patch.object(m,"_github",side_effect=req),\
             patch.object(m.requests,"get",return_value=good):
            self.assertTrue(m.status("google:owner","sample")["verified"])
        with patch.object(m,"_authorized",return_value=AUTH),\
             patch.object(m,"_github",side_effect=req),\
             patch.object(m.requests,"get",return_value=bad):
            self.assertFalse(m.status("google:owner","sample")["verified"])

if __name__=="__main__":
    unittest.main()
