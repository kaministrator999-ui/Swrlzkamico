import json,unittest
from unittest.mock import Mock
from api.html_project_browser_backend_v1 import *
from api.html_project_agent_v1 import verify_source
class WorkerTest(unittest.TestCase):
    def setUp(self):
        self.project="fixture";self.sha="b"*40;self.nonce="c"*32;self.run_id=7
        self.hashes=verify_source(self.project,{"index.html":"<html></html>"})
        self.run={"id":self.run_id,"event":"workflow_dispatch","head_sha":self.sha,"head_branch":"main",
                  "display_title":title(self.nonce,self.project),"path":WORKFLOW_PATH,
                  "actor":{"login":OWNER},"status":"completed","conclusion":"success"}
        self.receipt={"schema":SCHEMA,"project":self.project,"sourceSha":self.sha,"nonce":self.nonce,
                      "runId":self.run_id,"hashes":self.hashes,"browserVerified":True,"issues":[],
                      "entrySha256":self.hashes["index.html"]}
    def api(self,method,path,**kw):
        if path.endswith("/artifacts"):return {"artifacts":[{"id":11,"name":"swrlz-browser-"+self.nonce,"expired":False}]}
        return self.run
    def verify(self):
        return fetch_verified_receipt(self.api,"token",self.project,self.sha,self.nonce,self.run_id,self.hashes,
                                      download=lambda *a:self.receipt)
    def test_exact_receipt(self):self.assertEqual(self.verify(),self.receipt)
    def test_reject_wrong_run(self):
        self.run["head_sha"]="d"*40
        with self.assertRaisesRegex(BrowserWorkerUnavailable,"IDENTITY_MISMATCH"):self.verify()
    def test_reject_wrong_hash(self):
        self.receipt["hashes"]={"index.html":"wrong"}
        with self.assertRaisesRegex(BrowserWorkerUnavailable,"HASH_MISMATCH"):self.verify()
    def test_candidate_error_is_not_infrastructure_error(self):
        self.receipt.update(browserVerified=False,issues=[{"code":"BROWSER_RUNTIME_ERROR","detail":"pageerror: test"}])
        self.assertFalse(self.verify()["browserVerified"])
        self.receipt["infrastructureError"]="BROWSER_LAUNCH_FAILED"
        with self.assertRaisesRegex(BrowserWorkerUnavailable,"INFRASTRUCTURE"):self.verify()
    def test_dispatch_cancellation_before_request(self):
        api=Mock()
        worker=GitHubBrowserBackend(api,"token",self.sha,cancel=lambda:True)
        with self.assertRaisesRegex(BrowserWorkerUnavailable,"CANCELLED"):
            worker.validate_candidate(self.project,{"index.html":"<html></html>"},False,{"schema":"x","project":self.project,"patches":[]})
        api.assert_not_called()
