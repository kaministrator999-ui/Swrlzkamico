"""Regression: GitHub TXT creation is an approval proposal, never coder output."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from github_txt_intent_v256 import wants_github_text_file_creation
from model_router import dispatch


class ExternalCreateRoutingTest(unittest.TestCase):
    def test_clear_repo_creation_paraphrases(self):
        cases=(
            "Can you make a txt file in the repo for me",
            "Please create a text file in the GitHub repository",
            "In github please add a text file",
            "save a txt file in my repo",
            "Put new-test.txt in the GitHub repo",
        )
        for prompt in cases:
            with self.subTest(prompt=prompt):
                self.assertTrue(wants_github_text_file_creation(prompt))

    def test_non_actions_and_code_requests_remain_separate(self):
        cases=(
            "Write Python code that creates a text file in the repo",
            "Create a Python script to create a text file in GitHub",
            "Explain how GitHub creates text files",
            "Show me how to create a text file in GitHub",
            "Don't create a text file in the repo",
            "Read the repo's existing txt file",
            "Can you make a webpage?",
            "Create a text file on my laptop",
        )
        for prompt in cases:
            with self.subTest(prompt=prompt):
                self.assertFalse(wants_github_text_file_creation(prompt))

    def test_dispatch_proposes_confirmation_without_executing_code(self):
        def unexpected_generator(_payload):
            raise AssertionError("A repository CREATE_FILE proposal must not invoke inference")
        events=list(dispatch(
            "700m",
            {"prompt":"Can you make a txt file in the repo for me","history":[]},
            unexpected_generator,
        ))
        self.assertTrue(any(e.get("phase")=="GITHUB_CREATE_TXT_APPROVAL_REQUIRED" for e in events))
        self.assertFalse(any(e.get("phase")=="CODER_AUTO_ROUTE" for e in events))
        self.assertFalse(any(e.get("type")=="CANDIDATE_VALIDATION" for e in events))
        self.assertEqual(events[-1].get("type"),"COMPLETED")
        response="".join(e.get("text","") for e in events if e.get("type")=="DELTA")
        self.assertIn("Swrlzing-core",response)
        self.assertIn("No file was created",response)
        intent=next(e["intent"] for e in events if e.get("type")=="PROGRAMMING_INTENT")
        self.assertFalse(intent["codingTask"])
        self.assertEqual(intent["externalActionRequest"],"github-create-text-file")


if __name__=="__main__":
    unittest.main()
