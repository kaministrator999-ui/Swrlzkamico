"""Regression: GitHub TXT creation is an approval proposal, never coder output."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from github_txt_intent_v256 import wants_github_text_file_creation
from github_txt_intent_v256 import wants_github_text_file_creation


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



if __name__ == "__main__":
    unittest.main()
