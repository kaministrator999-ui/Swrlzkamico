"""No network/GPU: unit tests for verified image/answer dataset boundaries."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prepare_qwen3vl_sft import prepare  # noqa: E402


class DataPreflight(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.images = self.root / "images"
        self.images.mkdir()
        self.src = self.root / "annotated.jsonl"
        self.out = self.root / "prepared"
        self.rows = []
        for index, split in enumerate(("train", "train", "train", "val", "test")):
            name = f"subject-{index}.png"
            (self.images / name).write_bytes(
                b"\x89PNG\r\n\x1a\n" + bytes([index + 10]) * 30)
            self.rows.append({
                "id": f"subject-{index}-front",
                "character_id": f"subject-{index}",
                "split": split,
                "image": name,
                "question": "What do you see in this image?",
                "human_verified": True,
                "gold_answer": (
                    f"This hand-checked image {index} depicts a single character "
                    "in a clearly bounded viewpoint, with visible details."
                ),
            })

    def save(self):
        self.src.write_text(
            "".join(json.dumps(row) + "\n" for row in self.rows),
            encoding="utf-8")

    def test_train_validation_test_are_character_isolated(self):
        self.save()
        result = prepare(self.src, self.images, self.out)
        self.assertEqual(result["sampleCount"], {
            "train": 3, "val": 1, "test": 1,
        })
        self.assertEqual(result["characterCount"], {
            "train": 3, "val": 1, "test": 1,
        })
        train = json.loads((self.out / "train.jsonl").read_text().splitlines()[0])
        self.assertEqual(train["messages"][0]["role"], "user")
        self.assertTrue(train["messages"][0]["content"].startswith("<image>"))
        self.assertEqual(train["messages"][1]["role"], "assistant")
        self.assertEqual(len(train["images"]), 1)
        self.assertTrue(Path(train["images"][0]).is_file())
        self.assertEqual(result["splitByCharacter"], True)

    def test_unverified_model_guess_rejected(self):
        self.rows[0]["human_verified"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "human_verified"):
            prepare(self.src, self.images, self.out)
        self.assertFalse(self.out.exists())

    def test_raw_analyzer_output_rejected_as_gold(self):
        self.rows[0]["gold_answer"] = (
            "Local image analyzer's description (not directly inspected by"
            " §C): the model thinks it sees a figure.")
        self.save()
        with self.assertRaisesRegex(ValueError, "raw Qwen"):
            prepare(self.src, self.images, self.out)

    def test_same_character_must_not_leak_into_test_split(self):
        self.rows[-1]["character_id"] = self.rows[0]["character_id"]
        self.save()
        with self.assertRaisesRegex(ValueError, "leakage"):
            prepare(self.src, self.images, self.out)

    def test_identical_image_hash_must_not_leak_across_splits(self):
        (self.images / self.rows[-1]["image"]).write_bytes(
            (self.images / self.rows[0]["image"]).read_bytes())
        self.save()
        with self.assertRaisesRegex(ValueError, "leakage"):
            prepare(self.src, self.images, self.out)

    def test_path_escape_is_rejected(self):
        self.rows[0]["image"] = "../annotated.jsonl"
        self.save()
        with self.assertRaisesRegex(ValueError, "escapes"):
            prepare(self.src, self.images, self.out)

    def test_duplicate_sample_id_rejected(self):
        self.rows[1]["id"] = self.rows[0]["id"]
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicated"):
            prepare(self.src, self.images, self.out)

    def test_more_than_one_gold_label_for_same_image_rejected(self):
        # Identical data with different prompts is conservatively rejected
        # because independently authored answers could contradict each other.
        extra = dict(self.rows[0], id="subject-0-different-caption",
                     gold_answer="Different answer claims something else is in this image.")
        self.rows.insert(1, extra)
        self.save()
        with self.assertRaisesRegex(ValueError, "conflicting gold"):
            prepare(self.src, self.images, self.out)


if __name__ == "__main__":
    unittest.main()
