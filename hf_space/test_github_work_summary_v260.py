"""Bounded GitHub work metrics: verified bytes versus provider-backed diffs."""
import pathlib
import sys
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from github_work_summary_v260 import make_work_widget

SHA="d7d24c4629c62613744742e52ca9349716721e31"
PATH="write-action-tests/chat-test-6bbae6acc5289bb8.txt"
TEXT=("Hello from §wyrlz Chat!\n"
      "This is a harmless GitHub text-file creation test, requested directly "
      "in Chat by the connected repository owner.\n"
      "Target: Swrlzing-core / main / write-action-tests/\n")
RECEIPT={"ok":True,"verified":True,"operation":"CREATE_FILE",
         "repo":"kaministrator999-ui/Swrlzing-core","branch":"main","path":PATH,
         "commitSha":SHA}

class GithubWorkWidgetTest(unittest.TestCase):
    def test_known_committed_sample_statistics(self):
        def provider(token,endpoint):
            self.assertEqual(token,"secret")
            self.assertEqual(endpoint,"/repos/kaministrator999-ui/Swrlzing-core/commits/"+SHA)
            return {"sha":SHA,"stats":{"total":3,"additions":3,"deletions":0},
                    "files":[{"filename":PATH,"status":"added",
                              "additions":3,"deletions":0,"changes":3}],
                    "commit":{"committer":{"date":"2026-10-15T22:08:53Z"}}}
        widget=make_work_widget(RECEIPT,TEXT,"secret",provider)
        self.assertEqual(widget["contract"],"swrlz-widget-v1")
        self.assertEqual(widget["kind"],"github-work")
        data=widget["data"]
        self.assertEqual(data["bytesWritten"],189)
        self.assertEqual(data["textLines"],3)
        self.assertEqual(data["filesCreated"],1)
        self.assertEqual(data["filesOverwritten"],0)
        self.assertTrue(data["providerStatsAvailable"])
        self.assertEqual((data["additions"],data["deletions"],data["filesChanged"]),(3,0,1))
        self.assertEqual(data["commitAt"],"2026-10-15T22:08:53Z")
        self.assertNotIn("secret",str(widget))
        self.assertEqual(data["fileUrl"],"https://github.com/kaministrator999-ui/Swrlzing-core/blob/main/"+PATH)

    def test_provider_error_keeps_verified_receipt_without_fake_diff(self):
        def fail(_token,_path):raise ConnectionError("Provider unavailable")
        result=make_work_widget(RECEIPT,TEXT,"secret",fail)["data"]
        self.assertEqual(result["verification"],"EXACT_BYTES_MATCHED")
        self.assertFalse(result["providerStatsAvailable"])
        self.assertNotIn("additions",result)
        self.assertNotIn("deletions",result)
        self.assertNotIn("filesChanged",result)

    def test_mismatched_provider_response_cannot_claim_git_diff(self):
        obj={"sha":SHA,"files":[{"filename":PATH,"status":"modified",
                               "additions":99,"deletions":1,"changes":100}]}
        result=make_work_widget(RECEIPT,TEXT,"secret",lambda *_:obj)["data"]
        self.assertFalse(result["providerStatsAvailable"])
        self.assertNotIn("additions",result)

    def test_out_of_scope_and_unverified_receipts_refused(self):
        for patch in (
            {"verified":False}, {"operation":"UPDATE_FILE"},
            {"repo":"other/account"}, {"path":"write-action-tests/../oops.txt"},
            {"path":"secrets.txt"}, {"branch":"developer"}
        ):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):
                    make_work_widget({**RECEIPT,**patch},TEXT,"secret")

    def test_source_uses_structured_widget_for_live_and_persisted_messages(self):
        src=(pathlib.Path(__file__).parent/"station.py").read_text(encoding="utf-8")
        self.assertIn('{"type":"WIDGET","widget":receipt["widget"]}',src)
        self.assertIn('telemetry_meta["widgets"]=online_widgets',src)
        helper=(pathlib.Path(__file__).parent/"github_sandbox_create_txt.py").read_text(encoding="utf-8")
        self.assertIn('receipt["widget"] = make_work_widget(',helper)

if __name__=="__main__":unittest.main()
