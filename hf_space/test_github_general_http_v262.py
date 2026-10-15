"""HTTP review/confirmation acceptance for generalized text + binary GitHub files."""
import base64
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as gh
import github_general_create_v262 as f
import station


class HTTPGeneralFiles(unittest.TestCase):
    def setUp(self):
        f._pending.clear()
        self.current="google:owner"
        self.content={}
        self.puts=0
        def auth(user_id,expected_repo=None):
            if user_id!="google:owner":raise f.CreateFileError("GOOGLE_SIGN_IN_REQUIRED",401)
            return {"token":"oauth","repo":"kaministrator999-ui/Swrlzing-core","branch":"main"}
        def github(method,auth,path,data=None):
            if method=="GET":
                if path not in self.content:return 404,None
                return 200,{"encoding":"base64","content":base64.b64encode(self.content[path]).decode()}
            if method=="PUT":
                self.puts+=1
                self.content[path]=base64.b64decode(data["content"],validate=True)
                return 201,{"commit":{"sha":"a"*40}}
            raise AssertionError(method)
        self.patchers=[
            patch.object(gh,"_google",side_effect=lambda _request:self.current),
            patch.object(gh,"_config",return_value={"callback":"https://testserver/api/github/callback"}),
            patch.object(f,"_authorize",side_effect=auth),
            patch.object(f,"_github",side_effect=github),
        ]
        for p in self.patchers:p.start()
        self.client=TestClient(station.app)

    def tearDown(self):
        self.client.close()
        for p in reversed(self.patchers):p.stop()
        f._pending.clear()

    def test_http_prepare_preview_then_confirm_both_formats(self):
        for path,raw in (
            ("src/app.py",b"print(1)\n"),
            ("assets/logo.png",bytes([137,80,78,71,0,255])),
        ):
            proposal=self.client.post("/api/github/files/prepare-create",headers={"origin":"https://testserver"},json={
                "path":path,
                "contentBase64":base64.b64encode(raw).decode(),
                "mediaType":"image/png" if path.endswith(".png") else "text/plain",
            })
            self.assertEqual(proposal.status_code,200,proposal.text)
            self.assertEqual(self.puts,len(self.content))
            self.assertEqual(proposal.json()["path"],path)
            receipt=self.client.post("/api/github/files/confirm-create",headers={"origin":"https://testserver"},json={
                "approvalToken":proposal.json()["approvalToken"],"approved":True,
            })
            self.assertEqual(receipt.status_code,200,receipt.text)
            self.assertTrue(receipt.json()["verified"])
            self.assertEqual(self.content[path],raw)
        self.assertEqual(self.puts,2)

    def test_other_origin_cannot_prepare_or_confirm(self):
        response=self.client.post("/api/github/files/prepare-create",headers={"origin":"https://evil.example"},json={
            "path":"app.py","contentBase64":"YQ==",
        })
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.puts,0)

    def test_bounded_invalid_file_payload_fails_without_commit(self):
        response=self.client.post("/api/github/files/prepare-create",headers={"origin":"https://testserver"},json={
            "path":"src/../fail.txt","contentBase64":"YQ==",
        })
        self.assertEqual(response.status_code,422)
        self.assertEqual(self.puts,0)

    def test_tampered_approval_token_never_writes(self):
        response=self.client.post("/api/github/files/confirm-create",headers={"origin":"https://testserver"},json={
            "approvalToken":"not-a-real-token","approved":True,
        })
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.puts,0)


if __name__=="__main__":
    unittest.main()
