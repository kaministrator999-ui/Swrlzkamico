"""Local deterministic grader regressions for §C anonymous Chromium round 2."""
import unittest

from scripts.eval_chat_research_lyrics_conversations import CASES, ORIGINAL_TEST_LINES, check


def fails(kind, body, prev=None):
    return [x["check"] for x in check(kind,body,prev)["checks"] if not x["pass"]]


class BroadGuestGraderTests(unittest.TestCase):
    def test_all_batches_have_unique_multi_turn_scenarios(self):
        self.assertEqual(set(CASES), {"research","songwriting","conversation","transformations"})
        ids=[c["id"] for batch in CASES.values() for c in batch]
        self.assertEqual(len(ids),len(set(ids)))
        for cases in CASES.values():
            for case in cases:
                self.assertGreaterEqual(len(case["turns"]),2)
                for turn in case["turns"]:
                    self.assertTrue(turn["kind"] and turn["prompt"])

    def test_500_does_not_count_as_a_song(self):
        self.assertIn("no_generation_or_router_error",
                      fails("pop_song","Generation failed: HTTP Error 500: Internal Server Error"))

    def test_original_remix_rejects_copied_source_even_with_valid_sections(self):
        song=("[Verse 1]\n"+ORIGINAL_TEST_LINES[0]+"\nNoon sparks hurry round the dome\n"
              "[Chorus]\nCarry me out, carry me home\n"
              "[Verse 2]\nFresh feet cross a neon floor\n"
              "[Chorus]\nCarry me out, carry me home\n"
              "[Bridge]\nI choose the open door\n"+"New words keep moving. "*30)
        bad=fails("original_remix",song)
        self.assertIn("no_verbatim_source_line_1",bad)
        self.assertNotIn("distinct_verses",bad)

    def test_distinguishes_feedback_from_new_lyric(self):
        text="I can compare whether Verse 2 introduces a new event, but actual vocal flow needs a human performance check."
        self.assertEqual([],fails("feedback_only",text))
        self.assertIn("no_new_song",fails("feedback_only","[Verse 1]\nNew words\n[Verse 2]\nMore words"))

    def test_invalid_browser_listener_method_is_rejected(self):
        reply="On mobile, inspect click listeners using buttonElement.getEventListeners(). Check touch overlap and console events."
        self.assertIn("valid_dom_debugging_api",fails("debugging",reply))
        valid="On mobile, inspect the browser console, reproduce the tap, and inspect overlay pointer-events."
        self.assertEqual([],fails("debugging",valid))

    def test_staff_must_not_appear_out_of_nowhere(self):
        fabricated="Rae has 8 minutes; an extra cook arrived to help. Label containers."
        self.assertIn("no_invented_helpers",fails("staffing_followup",fabricated))

    def test_science_answer_checks_actual_contrast(self):
        good=("The Moon and Sun must align with Earth. Totality is smaller than the partial eclipse region. "
              "Not every new moon has a total eclipse because of orbital inclination. "
              "See https://science.nasa.gov/eclipses")
        self.assertEqual([],fails("public_science",good))


if __name__=="__main__":
    unittest.main()
