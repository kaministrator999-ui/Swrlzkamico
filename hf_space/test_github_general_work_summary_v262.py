"""General GitHub metrics must stay grounded for text, binary and missing provider stats."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from github_work_summary_v260 import make_general_work_widget

SHA="a"*40
BASE={"verified":True,"operation":"CREATE_FILE","repo":"kaministrator999-ui/Swrlzkamico",
      "branch":"main","path":"assets/logo.png","commitSha":SHA,"mediaType":"image/png"}

class GeneralWorkStats(unittest.TestCase):
    def test_png_has_verified_bytes_and_provider_diff_not_fake_lines(self):
        blob=b"\x89PNG\r\n\x1a\n\x00\xff"
        def checked(_token,path):
            self.assertEqual(path,"/repos/kaministrator999-ui/Swrlzkamico/commits/"+SHA)
            return {"sha":SHA,"files":[{"filename":"assets/logo.png","status":"added",
                                       "additions":0,"deletions":0,"changes":0}]}
        widget=make_general_work_widget(BASE,blob,"opaque",checked)
        x=widget["data"]
        self.assertEqual(x["bytesWritten"],len(blob))
        self.assertEqual(x["filesCreated"],1)
        self.assertEqual(x["filesOverwritten"],0)
        self.assertNotIn("textLines",x)
        self.assertTrue(x["providerStatsAvailable"])
        self.assertEqual(x["additions"],0)
        self.assertNotIn("opaque",str(widget))
        self.assertEqual(x["fileUrl"],"https://github.com/kaministrator999-ui/Swrlzkamico/blob/main/assets/logo.png")

    def test_unicode_markdown_and_unavailable_stats(self):
        receipt={**BASE,"path":"docs/日本語.md","mediaType":"text/markdown"}
        widget=make_general_work_widget(receipt,"一行\n二行\n".encode(),"secret",
                                        lambda *_:(_ for _ in ()).throw(ConnectionError()))
        x=widget["data"]
        self.assertEqual(x["textLines"],2)
        self.assertFalse(x["providerStatsAvailable"])
        self.assertNotIn("additions",x)
        self.assertIn("%E6%97%A5",x["fileUrl"])

    def test_refuse_wrong_repo_and_unverified_receipts(self):
        for delta in ({"repo":"evil/other"},{"verified":False},
                      {"path":"../escape.txt"},{"commitSha":"bad"},{"branch":"../bad"}):
            with self.subTest(delta=delta):
                with self.assertRaises((ValueError,Exception)):
                    make_general_work_widget({**BASE,**delta},b"x","secret")

if __name__=="__main__":
    unittest.main()
