"""End-to-end HTTP contract for the live GitHub OAuth / CREATE_FILE sandbox."""
import base64
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as gh
import github_sandbox_create_txt as txt
import station


class LiveOAuthSandboxTest(unittest.TestCase):
    def setUp(self):
        txt._pending.clear()
        self.record={
            "owner":"google:owner","token":"existing-encrypted-oauth-token",
            "repo":gh._SANDBOX_REPO,"login":gh._SANDBOX_OWNER,
            "scopes":"read:user public_repo","githubId":1001,
        }
        self.created=False
        self.puts=0
        def repo_api(token,path):
            self.assertEqual(token,"existing-encrypted-oauth-token")
            if path=="/repos/"+gh._SANDBOX_REPO:
                return {"full_name":gh._SANDBOX_REPO,"private":False,
                        "default_branch":"main","permissions":{"push":True}}
            raise AssertionError("Unexpected GitHub route: "+path)
        def content_api(method,path,token,body=None):
            self.assertEqual(token,"existing-encrypted-oauth-token")
            self.assertEqual(path,"write-action-tests/acceptance.txt")
            if method=="GET":
                return (200,{"content":base64.b64encode(b"Hello, GitHub!").decode()}) if self.created else (404,None)
            if method=="PUT":
                self.assertEqual(body["branch"],"main")
                self.assertNotIn("sha",body)
                self.created=True
                self.puts+=1
                return 201,{"commit":{"sha":"confirmed-commit"}}
            raise AssertionError(method)
        self.patchers=[
            patch.object(gh,"_google",return_value="google:owner"),
            patch.object(gh,"_config",return_value={"callback":"https://testserver/api/github/callback","client":"fake-test-client"}),
            patch.object(gh,"_load",return_value=self.record),
            patch.object(gh,"_api",side_effect=repo_api),
            patch.object(txt,"_request",side_effect=content_api),
        ]
        for patcher in self.patchers:patcher.start()
        self.client=TestClient(station.app)

    def tearDown(self):
        self.client.close()
        for patcher in reversed(self.patchers):patcher.stop()
        txt._pending.clear()

    def test_verified_account_prepare_confirm_and_exact_readback(self):
        report=self.client.get("/api/github/sandbox/write-status")
        self.assertEqual(report.status_code,200)
        self.assertTrue(report.json()["allowed"])
        headers={"origin":"https://testserver"}
        preview=self.client.post("/api/github/sandbox/prepare-create-txt",
            json={"filename":"acceptance.txt","content":"Hello, GitHub!"},headers=headers)
        self.assertEqual(preview.status_code,200,preview.text)
        self.assertEqual(self.puts,0)
        self.assertEqual(preview.json()["repo"],gh._SANDBOX_REPO)
        ticket=preview.json()["approvalToken"]
        result=self.client.post("/api/github/sandbox/confirm-create-txt",
            json={"approvalToken":ticket,"approved":True},headers=headers)
        self.assertEqual(result.status_code,200,result.text)
        self.assertTrue(result.json()["verified"])
        self.assertEqual(result.json()["commitSha"],"confirmed-commit")
        self.assertEqual(self.puts,1)
        repeat=self.client.post("/api/github/sandbox/confirm-create-txt",
            json={"approvalToken":ticket,"approved":True},headers=headers)
        self.assertEqual(repeat.status_code,403)
        self.assertEqual(self.puts,1)

    def test_read_only_connected_owner_requires_explicit_upgrade(self):
        self.record["scopes"]="read:user"
        report=self.client.get("/api/github/sandbox/write-status")
        self.assertFalse(report.json()["allowed"])
        self.assertEqual(report.json()["reason"],"GITHUB_WRITE_SCOPE_REQUIRED")
        self.assertEqual(report.json()["authorizeUrl"],"/api/github/start?access=public-write")
        denied=self.client.post("/api/github/sandbox/prepare-create-txt",
            json={"filename":"acceptance.txt","content":"Hello, GitHub!"},
            headers={"origin":"https://testserver"})
        self.assertEqual(denied.status_code,403)
        self.assertEqual(denied.json()["code"],"GITHUB_WRITE_SCOPE_REQUIRED")
        self.assertEqual(self.puts,0)

    def test_cross_origin_denied_before_authorization_or_write(self):
        result=self.client.post("/api/github/sandbox/prepare-create-txt",
            json={"filename":"acceptance.txt","content":"Hello, GitHub!"},
            headers={"origin":"https://other.example"})
        self.assertEqual(result.status_code,403)
        self.assertEqual(self.puts,0)

    def test_general_stage_one_mutations_remain_locked(self):
        with patch.object(gh,"_api",return_value={"full_name":gh._SANDBOX_REPO,
             "private":False,"default_branch":"main","permissions":{"push":True}}):
            for operation in ("branch-write","issue-write","workflow-dispatch","workflow-create"):
                self.assertFalse(gh._effective_access(self.record,gh._SANDBOX_REPO,operation)["allowed"])
        self.assertFalse(gh._read_stage_command("@GitHub create branch unsafe"))
        self.assertFalse(gh._read_stage_command("@GitHub confirm existing-write-token"))

    def test_oauth_upgrade_only_for_selected_owner_repo(self):
        self.record["scopes"]="read:user"
        with patch.object(gh,"_redis",return_value="OK"):
            response=self.client.get("/api/github/start?access=public-write",follow_redirects=False)
        self.assertEqual(response.status_code,303,response.text)
        self.assertIn("public_repo",response.headers["location"])
        # General CREATE_FILE now supports this second selected owner repo.
        self.record["repo"]="kaministrator999-ui/Swrlzkamico"
        with patch.object(gh,"_redis",return_value="OK"):
            other=self.client.get("/api/github/start?access=public-write",follow_redirects=False)
        self.assertEqual(other.status_code,303)
        self.record["repo"]="other-owner/unapproved"
        with patch.object(gh,"_redis",side_effect=AssertionError("OAuth state should not be created")):
            denied=self.client.get("/api/github/start?access=public-write",follow_redirects=False)
        self.assertEqual(denied.status_code,403)

if __name__=="__main__":
    unittest.main()
