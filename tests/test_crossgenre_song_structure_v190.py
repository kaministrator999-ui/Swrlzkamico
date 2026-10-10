"""Source-only cross-genre lyric pedagogy contracts (not model quality grades)."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hf_space"))

from lyric_structure_school import _structure_cards, structure_teaching
from lyric_craft_school import lyric_craft_policy


CLOCKMAKER = (
    "Write a 40-line original chopper freestyle about a clockmaker solving a "
    "mystery. Keep it continuous, use meaningful internal rhymes, and "
    "alternate rapid-fire passages with short punchlines. No chorus."
)


class CrossGenreSongStructureTest(unittest.TestCase):
    def test_study_provenance_and_breadth(self):
        data = json.loads((ROOT / "training/lyrics/crossgenre_song_studies_v1.json").read_text())
        self.assertEqual(data["schema"], "swrlz-crossgenre-song-studies-v1")
        self.assertEqual(data["studyCount"], len(data["studies"]))
        self.assertGreaterEqual(len(data["studies"]), 16)
        self.assertGreaterEqual(len({x["genre"] for x in data["studies"]}), 12)
        self.assertEqual(len({x["id"] for x in data["studies"]}), len(data["studies"]))
        self.assertTrue(all(x["sourceUrl"].startswith("https://") for x in data["studies"]))
        self.assertTrue(all(x["lyricTextStored"] is False for x in data["studies"]))
        self.assertTrue(all(x["transferMechanism"] and x["sourceObservation"] for x in data["studies"]))
        self.assertEqual(data["evaluations"]["weightUpdate"], "NONE")

    def test_compact_public_form_patterns(self):
        data = json.loads((ROOT / "hf_space/lyric_structure_patterns_v1.json").read_text())
        self.assertEqual(data["schema"], "swrlz-lyric-structure-patterns-v1")
        self.assertEqual(data["count"], len(data["cards"]))
        self.assertEqual(len(_structure_cards()), data["count"])
        self.assertEqual(len({x["id"] for x in data["cards"]}), len(data["cards"]))
        self.assertTrue(all(len(x["cue"]) <= 200 for x in data["cards"]))
        self.assertTrue(all(x["triggers"] for x in data["cards"]))
        self.assertTrue(all("title" not in x and "artist" not in x for x in data["cards"]))

    def test_clockmaker_uses_three_complementary_axes(self):
        result = structure_teaching(CLOCKMAKER)
        self.assertIn("chopper-contrast:", result)
        self.assertIn("mystery-reveal:", result)
        self.assertIn("continuous-arc:", result)
        self.assertNotIn("verse-chorus:", result)
        self.assertLess(len(result), 650)

    def test_constraints_outweigh_positive_chorus_words(self):
        result = structure_teaching("Write catchy pop lyrics with a hook but no chorus, no hook, and an uninterrupted story")
        self.assertNotIn("verse-chorus:", result)
        self.assertIn("continuous-arc:", result)

    def test_other_genres_are_not_forced_into_chopper(self):
        cases = [
            ("Write a twelve-bar blues song about a train", "blues-aab:"),
            ("Create an orchestral classical suite with a repeating motif", "classical-development:"),
            ("Write an intimate sad ballad about a departure", "intimate-motif:"),
            ("Compose an EDM dance track with a drop", "electronic-layering:"),
            ("Write a folk acoustic song about the farm", "folk-detail:"),
            ("Write a metal riff song about a storm", "rock-dynamics:"),
        ]
        for prompt, expected in cases:
            with self.subTest(prompt=prompt):
                result = structure_teaching(prompt)
                self.assertIn(expected, result)
                self.assertNotIn("chopper-contrast:", result)

    def test_existing_noncreation_gate_remains_authoritative(self):
        for prompt in (
            "Find the lyrics to Worldwide Choppers online",
            "Analyze Bohemian Rhapsody",
            "Review all the songs we made",
            "Compare two verses",
            "Write an analysis of a famous rap song",
        ):
            self.assertEqual(lyric_craft_policy(prompt), "")

    def test_genre_guidance_is_wired_and_prompt_bounded(self):
        full = lyric_craft_policy(CLOCKMAKER)
        self.assertIn("ORIGINAL LYRIC CRAFT", full)
        self.assertIn("TARGETED FORM/GENRE MECHANICS", full)
        self.assertIn("mystery-reveal:", full)
        self.assertIn("chopper-contrast:", full)
        self.assertLess(len(full), 2900)
        self.assertEqual(full, lyric_craft_policy(CLOCKMAKER))
        self.assertNotIn("Worldwide Choppers", full)
        self.assertNotIn("DUCKWORTH.", full)
        self.assertNotIn("Bohemian Rhapsody", full)

    def test_no_model_weight_or_acceptance_claims(self):
        bank = (ROOT / "hf_space/lyric_structure_patterns_v1.json").read_text()
        study = (ROOT / "training/lyrics/crossgenre_song_studies_v1.json").read_text()
        self.assertIn("NOT_MODEL_WEIGHT_TRAINING", bank)
        self.assertIn("NOT_RUN", study)


if __name__ == "__main__":
    unittest.main()
