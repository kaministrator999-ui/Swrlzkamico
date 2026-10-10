"""v198: rap micro-lessons select one cue, never weaken original intent."""
import os
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
from rap_micro_curriculum import rap_micro_guidance, CUES
from lyric_output_contract import lyric_shape_request


class RapPracticeV198(unittest.TestCase):
    def test_creative_generic_freestyle_starts_with_cadence(self):
        cue,lesson=rap_micro_guidance("Spit a freestyle about my weekend")
        self.assertEqual(lesson,"pocket")
        self.assertIn("two-bar",cue)
        self.assertNotIn("weekend",cue)
        self.assertLess(len(cue),480)

    def test_targeted_skills_are_independent_and_bounded(self):
        prompts={
            "flow":"Write 16 chopper rap bars with flow switches",
            "rhyme":"Write 8 rap bars with multisyllabic internal rhymes",
            "punch":"Create battle rap punchlines",
            "story":"Write a storytelling rap about a town",
            "pocket":"Give me a freestyle",
        }
        for expected,prompt in prompts.items():
            with self.subTest(focus=expected):
                cue,lesson=rap_micro_guidance(prompt)
                self.assertEqual(lesson,expected)
                self.assertEqual(cue.count("ONE RAP CRAFT FOCUS"),1)
                self.assertNotIn("town",cue)
                self.assertNotIn("Step 1",cue)
                self.assertLess(len(cue),490)

    def test_user_must_keep_full_count_and_negative_constraints(self):
        prompt="Write a 40-line chopper freestyle about a clockmaker mystery; no chorus, one continuous verse"
        shape=lyric_shape_request(prompt)
        self.assertEqual(shape["requestedLines"],40)
        self.assertTrue(shape["continuous"])
        self.assertTrue(shape["noChorus"])
        cue,focus=rap_micro_guidance(prompt)
        self.assertEqual(focus,"flow")
        self.assertIn("exact length",cue)
        self.assertNotIn("clockmaker",cue)
        self.assertFalse("8 bars only" in cue)

    def test_plain_songs_and_noncreation_discussion_not_coached(self):
        for prompt in ("Write a folk song", "How does a conductor lead orchestra?",
                       "Explain rhyme theory", "Please write a letter"):
            with self.subTest(prompt=prompt):
                self.assertEqual(rap_micro_guidance(prompt),("","SKIPPED"))

    def test_off_switch_and_non_code_hijack(self):
        with patch.dict(os.environ,{"SWRLZ_RAP_MICROLESSON_ENABLED":"0"}):
            self.assertEqual(rap_micro_guidance("Write rap bars"),("","SKIPPED"))
        eng=(ROOT/"hf_space"/"lfm2_700m_engine.py").read_text(encoding="utf-8")
        self.assertIn("if music_policy and not programming.get(\"codingTask\")",eng)
        self.assertIn("if craft_policy:",eng)
        self.assertIn("rap_hint,rap_focus=rap_micro_guidance(prompt)",eng)
        self.assertIn("if rap_hint and not reference_structure:",eng)
        self.assertIn('candidate_check["rapMicroFocus"]',eng)
        self.assertIn("verify_original_lyrics",eng)
        self.assertIn("research_hint,lyric_research_receipt=research_for_creation(prompt)",eng)

    def test_one_author_written_skill_not_a_mandatory_six_point_list(self):
        self.assertEqual(set(CUES),{"pocket","flow","rhyme","punch","story"})
        for cue in CUES.values():
            self.assertLess(len(cue),330)
            self.assertNotIn("Tech N9ne",cue)
            self.assertNotIn("Eminem",cue)
            self.assertNotIn("40 lines",cue)


if __name__ == "__main__":
    unittest.main()
