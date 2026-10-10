"""Regression: general version literacy, exact project snapshot, content-first Chat."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from version_literacy import is_version_query, version_intent, style_hint
import project_thread_memory as memory


class VersionLiteracyTests(unittest.TestCase):
    def test_recalls_and_disambiguation(self):
        self.assertEqual(version_intent("What were the versions again?"), "recall")
        self.assertEqual(version_intent("Compare these module versions"), "compare")
        self.assertEqual(version_intent("Which commit first introduced version 1.0.0?"), "provenance")
        self.assertEqual(version_intent("What is CalVer versioning?"), "explain")
        self.assertEqual(version_intent("Hey how are you"), "")
        self.assertEqual(version_intent("Write a rap about a clockmaker"), "")
        self.assertFalse(is_version_query("Let's discuss our friendship"))

    def test_no_commit_provenance_hallucination_hint(self):
        self.assertIn("NOT the initial commit", style_hint("What is the origin of version 2.3?"))
        self.assertIn("NOT a module version", style_hint("Explain release versions"))

    def test_thread_snapshot_is_complete_when_versions_requested(self):
        ctx = memory.normalize({
            "repo":"public-example/project", "sourceSha":"a" * 40, "runtimeSha":"b" * 40,
            "branch":"main", "startupPath":"START.md",
            "modules":[
                ["REPOSITORY_WORK","1.0.135","active"],
                ["SERVER_RUNTIME","2.3.349","active"],
                ["LALM_ENGINE","2.1.177","active"],
                ["WEB_CHAT","1.5.94","active"],
                ["ONLINE_RESEARCH","1.0.30","active"],
                ["DEPLOYMENT_CONTROL","0.4.2","active"],
            ],
        })
        source = memory.model_context(ctx, "What were all the versions again?")
        for name,version,_ in ctx["modules"]:
            self.assertIn(name.replace("_"," ").title(),source)
            self.assertIn(version,source)
        self.assertIn("runtime@",source)
        self.assertIn("last verified source snapshot",source)
        self.assertNotIn("initial commit=",source)
        short = memory.model_context(ctx,"What did we deploy?")
        self.assertIn("Server Runtime",short)
        self.assertNotIn("Online Research",short)
        self.assertEqual(memory.model_context(ctx,"Write lyrics about a clockmaker"),"")

    def test_chat_has_no_automatic_response_frame(self):
        html=(HERE.parent/"chat"/"§wyrlz"/"index.html").read_text(encoding="utf-8")
        self.assertNotIn("const wrapMiscResponse=()=>",html)
        self.assertNotIn("wrapMiscResponse();",html)
        self.assertIn("v199: content-first response presentation",html)
        self.assertIn("const appendCode=(header,body,provisional=false)=>",html)
        self.assertIn("const appendLyric=(raw,key,file,provisional)=>",html)
        self.assertIn('const tableRule=line=>',html)
        self.assertIn("safeHttpUrl(match[2])",html)


if __name__=="__main__":
    unittest.main()
