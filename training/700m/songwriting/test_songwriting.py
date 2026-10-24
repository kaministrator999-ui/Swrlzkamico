"""Small stdlib-only guard tests: no model download, GPU, network or private data."""
import json
import tempfile
import unittest
from pathlib import Path

from benchmark_first_pass import inspect_form, load_prompts
from corpus import load_reviewed_corpus, split_corpus


def record(suffix="a", split="train"):
    return {
        "schema": "swrlz-700m-songwriting-sft-v1",
        "id": "synthetic-" + suffix,
        "status": "APPROVED", "split": split,
        "origin": "author-original", "rightsCleared": True, "privacyReviewed": True,
        "prompt": "Write a detailed original rap about an unusual mechanical bird " + suffix,
        "completion": ("A new machine makes its way across the sky, " + suffix + ".\n") * 7,
        "reviews": [
            {"reviewerId": key, "approved": True, "originalityChecked": True,
             "scores": {"rhyme": 4, "flow": 4, "coherence": 4, "completion": 4, "originality": 4}}
            for key in ("reviewer-A", "reviewer-B")
        ]
    }


class SongwritingTests(unittest.TestCase):
    def load(self, rows):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.jsonl"
            path.write_text("\n".join(json.dumps(x) for x in rows) + "\n")
            return load_reviewed_corpus(path)

    def test_approved_reviews_separate_split(self):
        train, heldout = split_corpus(self.load([record("a"), record("b", "holdout")]))
        self.assertEqual((len(train), len(heldout)), (1, 1))

    def test_unreviewed_cannot_train(self):
        row = record()
        row["reviews"] = row["reviews"][:1]
        with self.assertRaisesRegex(ValueError, "two documented"):
            self.load([row])

    def test_duplicate_completions_rejected(self):
        same = record("b")
        same["completion"] = record("a")["completion"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.load([record("a"), same])

    def test_duplicate_reviewer_rejected(self):
        row = record()
        row["reviews"][1]["reviewerId"] = "reviewer-A"
        with self.assertRaisesRegex(ValueError, "duplicate/failed"):
            self.load([row])

    def test_bad_score_rejected(self):
        row = record()
        row["reviews"][0]["scores"]["flow"] = 3
        with self.assertRaisesRegex(ValueError, "quality threshold"):
            self.load([row])

    def test_unreviewed_form_not_semantic_quality(self):
        shape = inspect_form("Line one\nLine two\n", {"expectedLines": 2, "noChorus": True})
        self.assertTrue(shape["formPass"])
        self.assertFalse(shape["semanticQualityReviewed"])

    def test_unwanted_chorus(self):
        shape = inspect_form("[Chorus]\nLine one\nLine two", {"expectedLines": 2, "noChorus": True})
        self.assertFalse(shape["formPass"])
        self.assertIn("unexpected-chorus-section", shape["formIssues"])

    def test_prompt_suite(self):
        suite = load_prompts(Path(__file__).with_name("prompts.jsonl"))
        self.assertGreaterEqual(len(suite), 12)
        self.assertTrue(all(row.get("topicOriginal") for row in suite))


if __name__ == "__main__":
    unittest.main()
