"""HTTP acceptance contract for the account-bound GitHub TXT creation flow."""
import base64
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
import station
import github_oauth_reuse_v257 as oauth
import github_sandbox_create_txt as sandbox


class SandboxHttpFlowTest(unittest.TestCase):
    def setUp(self):
        sandbox._pending.clear()
        self.user={"id":"google:owner"}
        self.record={
            "owner":self.user["id"],"token":"stored-oauth-token",
            "repo":oauth.TARGET,"login":oauth.OWNER,
            "scopes":"read:user public_repo","githubId":123,
        }
        self.written=False
        self.put_count=0
        def github_request(method,path,token,body=None):
            self.assertEqual(token,"stored-oauth-token")
            self.assertEqual(path,"write-action-tests/http-test.txt")
            if method=="GET":
                return ((200,{"content":base64.b64encode(b"hello world").decode("ascii")})
                        if self.written else (404,None))
            if method=="PUT":
                self.put_count+=1
                self.assertNotIn("sha",body)
                self.written=True
                return 201,{"commit":{"sha":"verified-commit"}}
            raise AssertionError(method)
        self.patches=[
            patch.object(station,"_account_session",return_value=("signed-in",self.user)),
            patch.object(oauth,"_account_lookup",return_value=("signed-in",self.user)),
            patch.object(oauth,"_config",return_value={"callback":"https://testserver/api/github/callback"}),
            patch.object(oauth,"_load",return_value=self.record),
            patch.object(oauth,"_api",return_value={"full_name":oauth.TARGET,"private":False,"permissions":{"push":True}}),
            patch.object(sandbox,"_request",side_effect=github_request),
        ]
        for p in self.patches:p.start()
        self.client=TestClient(station.app)

    def tearDown(self):
        self.client.close()
        for p in reversed(self.patches):p.stop()
        sandbox._pending.clear()

    def test_preflight_confirm_readback_without_standalone_token(self):
        view=self.client.get("/api/github/sandbox/write-status")
        self.assertEqual(view.status_code,200)
        self.assertTrue(view.json()["allowed"])
        headers={"origin":"https://testserver"}
        proposal=self.client.post(
            "/api/github/sandbox/prepare-create-txt",
            json={"filename":"http-test.txt","content":"hello world"},headers=headers,
        )
        self.assertEqual(proposal.status_code,200,proposal.text)
        self.assertEqual(self.put_count,0)
        self.assertEqual(proposal.json()["path"],"write-action-tests/http-test.txt")
        token=proposal.json()["approvalToken"]
        confirmed=self.client.post(
            "/api/github/sandbox/confirm-create-txt",
            json={"approvalToken":token,"approved":True},headers=headers,
        )
        self.assertEqual(confirmed.status_code,200,confirmed.text)
        self.assertTrue(confirmed.json()["verified"])
        self.assertEqual(confirmed.json()["commitSha"],"verified-commit")
        self.assertEqual(self.put_count,1)
        replay=self.client.post(
            "/api/github/sandbox/confirm-create-txt",
            json={"approvalToken":token,"approved":True},headers=headers,
        )
        self.assertEqual(replay.status_code,403)
        self.assertEqual(self.put_count,1)

    def test_cross_origin_cannot_issue_a_write(self):
        response=self.client.post(
            "/api/github/sandbox/prepare-create-txt",
            json={"filename":"http-test.txt","content":"hello world"},
            headers={"origin":"https://attacker.example"},
        )
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.put_count,0)

    def test_read_only_grant_cannot_prepare_a_write(self):
        self.record["scopes"]="read:user"
        response=self.client.post(
            "/api/github/sandbox/prepare-create-txt",
            json={"filename":"http-test.txt","content":"hello world"},
            headers={"origin":"https://testserver"},
        )
        self.assertEqual(response.status_code,403)
        self.assertEqual(response.json()["code"],"GITHUB_WRITE_SCOPE_REQUIRED")
        self.assertEqual(self.put_count,0)

if __name__=="__main__":
    unittest.main()
