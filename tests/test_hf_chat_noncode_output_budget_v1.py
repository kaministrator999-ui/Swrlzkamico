"""Regression for non-code output limit finalization without a model or network."""
import runpy
import unittest
from pathlib import Path

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/hf_chat_noncode_output_budget_v1.py"))
OLD = MODULE["OLD_TAIL"]
NEW = MODULE["NEW_TAIL"]
PATCH = MODULE["patch_source"]

def simulate(*, coding=False, source_change=False, already_streamed=True,
             accepted=False, final_text="Verse 1\nVerse 2", length=True):
    source = (
        "def events(candidate_attempts, programming, source_change_mode, "
        "first_delta, candidate_check, candidate_text):\n"
        + NEW
    )
    namespace = {}
    exec(compile(source, "<bounded-output-guard>", "exec"), namespace)
    return list(namespace["events"](
        [{"finishReason": "length" if length else "stop"}],
        {"codingTask": coding},
        "apply" if source_change else "",
        1.0 if already_streamed else None,
        {"status": "PASS" if accepted else "REJECT"},
        final_text,
    ))

class NoncodeOutputBudgetTests(unittest.TestCase):
    def test_current_live_anchor_rewrites_exactly_once(self):
        original = "def generate_events():\n" + OLD
        rewritten = PATCH(original, "fixture.py")
        self.assertNotEqual(original, rewritten)
        self.assertIn("UNVERIFIED_PARTIAL", rewritten)
        self.assertIn('not programming.get("codingTask")', rewritten)
        with self.assertRaises(ValueError):
            PATCH(rewritten, "fixture.py")

    def test_noncode_streamed_draft_is_preserved_not_failed(self):
        events = simulate()
        self.assertEqual([e["type"] for e in events],
                         ["CANDIDATE_VALIDATION", "STATUS", "COMPLETED"])
        self.assertEqual(events[0]["validation"]["status"], "INCOMPLETE")
        self.assertEqual(events[-1]["phase"], "PARTIAL")

    def test_valid_buffered_candidate_is_emitted_once(self):
        events = simulate(already_streamed=False, accepted=True)
        self.assertEqual(events[0], {"type": "DELTA", "text": "Verse 1\nVerse 2"})
        self.assertNotIn("FAILED", [e["type"] for e in events])

    def test_unverified_buffered_draft_is_not_leaked(self):
        events = simulate(already_streamed=False, accepted=False)
        self.assertEqual(events[0]["type"], "DELTA")
        self.assertNotIn("Verse 1", events[0]["text"])
        self.assertEqual(events[-1]["phase"], "PARTIAL")

    def test_coding_and_source_edit_rejections_are_untouched(self):
        for args in ({"coding": True}, {"source_change": True}):
            with self.subTest(args=args):
                events = simulate(**args)
                self.assertEqual([e["type"] for e in events], ["FAILED"])
                self.assertEqual(events[0]["reason"], "OUTPUT_TOKEN_LIMIT")

    def test_normal_stop_is_not_intercepted(self):
        self.assertEqual(simulate(length=False), [])

if __name__ == "__main__":
    unittest.main()
