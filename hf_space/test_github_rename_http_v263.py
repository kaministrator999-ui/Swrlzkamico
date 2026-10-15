"""HTTP rename proposal: origin, session and per-file confirm are mandatory."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
import github_rename_v263 as ren
import station

class RenameHttp(unittest.TestCase):
    def setUp(self):
        self.writes=0
        self.user="google:owner"
        self.patches=[
            patch.object(gh,"_google",side_effect=lambda request:self.user),
            patch.object(gh,"_config",return_value={"callback":"https://testserver/api/github/callback"}),
            patch.object(ren,"prepare",return_value={"approvalToken":"ticket","operation":"RENAME_FILE",
                "sourcePath":"a.py","destinationPath":"b.py","atomic":True}),
            patch.object(ren,"confirm",side_effect=self.confirm),
            patch("github_rename_receipt_v263.make_rename_widget",return_value={
                "kind":"github-rename","contract":"swrlz-widget-v1","data":{"filesRenamed":1}}),
        ]
        for p in self.patches:p.start()
        self.client=TestClient(station.app)
    def tearDown(self):
        self.client.close()
        for p in reversed(self.patches):p.stop()
    def confirm(self,user,token,approval):
        self.writes+=1
        self.assertEqual(user,"google:owner")
        self.assertEqual(token,"ticket")
        self.assertIs(approval,True)
        return {"ok":True,"verified":True,"operation":"RENAME_FILE",
                "sourcePath":"a.py","destinationPath":"b.py","atomic":True}
    def test_review_before_write_then_confirm(self):
        prep=self.client.post("/api/github/files/prepare-rename",
            headers={"origin":"https://testserver"},
            json={"sourcePath":"a.py","destinationPath":"b.py"})
        self.assertEqual(prep.status_code,200,prep.text)
        self.assertEqual(self.writes,0)
        confirmed=self.client.post("/api/github/files/confirm-rename",
            headers={"origin":"https://testserver"},
            json={"approvalToken":"ticket","approved":True})
        self.assertEqual(confirmed.status_code,200,confirmed.text)
        self.assertEqual(self.writes,1)
        self.assertEqual(confirmed.json()["widget"]["kind"],"github-rename")
    def test_cross_origin_is_denied(self):
        for endpoint,body in (
            ("prepare-rename",{"sourcePath":"a.py","destinationPath":"b.py"}),
            ("confirm-rename",{"approvalToken":"ticket","approved":True}),
        ):
            r=self.client.post("/api/github/files/"+endpoint,
              headers={"origin":"https://other.example"},json=body)
            self.assertEqual(r.status_code,403)
        self.assertEqual(self.writes,0)

if __name__=="__main__":unittest.main()
