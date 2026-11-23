import ast,unittest
from scripts.hf_chat_github_write_routing_release_v1 import transform
class RoutingTests(unittest.TestCase):
    def test_explicit_edits_outrank_read_only_explain(self):
        sample='''from pathlib import Path
ROOT=Path(__file__).resolve().parent
def route(prompt,google_owner,tid,active_github,history):
    payload={}
    if False: pass
    elif github_report_explain_v236.is_report_request(prompt):
        payload["suppliedGitHubReportExplanation"]=True
    elif github_chat_files.is_file_action(prompt,active_github,history):
        payload["githubChatFileAction"]={}
    return payload
'''
        out=transform(sample)
        tree=ast.parse(out)
        namespace={"__file__":"station.py"}
        exec(compile(tree,"station.py","exec"),namespace)
        helper=namespace["_explicit_github_file_mutation"]
        self.assertTrue(helper("@GitHub edit file swrlz-review-test.txt\nContent: Version 3"))
        self.assertTrue(helper("@GitHub create file demo.txt\nContent: hi"))
        self.assertFalse(helper("@GitHub explain file demo.txt"))
        self.assertFalse(helper("explain the GitHub file edit process"))
        self.assertFalse(helper("yes"))
        self.assertLess(out.index("elif _explicit_github_file_mutation(prompt)"),out.index("elif github_report_explain_v236.is_report_request(prompt)"))
    def test_no_duplicate_patch(self):
        sample='from pathlib import Path\nROOT=Path(__file__).resolve().parent\n# swrlz-explicit-github-write-routing-v1\n'
        with self.assertRaises(AssertionError):transform(sample)
if __name__=="__main__":unittest.main()
