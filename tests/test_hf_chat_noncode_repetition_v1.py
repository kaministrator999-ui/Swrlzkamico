"""Runaway text-loop regression and wrapper cancellation tests (offline)."""
from __future__ import annotations
import ast
import unittest
from api.noncode_repetition_guard_v1 import RepetitionWatch, guard_eligible
from scripts.hf_chat_noncode_repetition_release_v1 import patch_engine

A = "I'm the one who's the peace, I'm the one who's the cease,"
B = "I'm the one who's the cause, I'm the one who's the cease,"


class DetectorTests(unittest.TestCase):
    def test_alternating_loop_across_arbitrary_stream_chunks(self):
        w = RepetitionWatch()
        value = ((A + "\n" + B + "\n") * 6)
        found = None
        for size in range(0, len(value), 13):
            found = w.observe(value[size:size+13]) or found
        self.assertEqual(found, {"blockSize": 2, "cycles": 4})

    def test_one_line_runaway(self):
        w = RepetitionWatch()
        self.assertEqual(w.observe((A + "\n") * 5), {"blockSize": 1, "cycles": 5})

    def test_intentional_chorus_with_distinct_verses_not_stopped(self):
        w = RepetitionWatch()
        chorus = A + "\n" + B + "\n"
        for verse in (
            "Different lyrics move the story forward while the rhythm remains strong.\n",
            "A second verse brings a different character and a new narrative angle.\n",
            "A third verse changes the subject and lands an original final rhyme.\n",
        ):
            self.assertIsNone(w.observe(chorus + verse))
        self.assertIsNone(w.detected)

    def test_three_copies_of_two_line_hook_not_blocked(self):
        self.assertIsNone(RepetitionWatch().observe((A + "\n" + B + "\n") * 3))

    def test_reset_between_candidates(self):
        w = RepetitionWatch()
        w.observe((A + "\n" + B + "\n") * 3)
        w.reset()
        self.assertIsNone(w.observe(A + "\n" + B + "\n"))

    def test_short_ui_and_code_repetition_not_detected(self):
        w = RepetitionWatch()
        self.assertIsNone(w.observe("yo\nyo\nyo\nyo\nyo\n"))
        self.assertIsNone(w.observe("```css\n" + (".hero { padding: 8px; color: white; }\n" * 40) + "```\n"))

    def test_eligibility_scoped(self):
        self.assertTrue(guard_eligible({"prompt": "Write an original rap"}))
        for payload in (
            None, {}, {"codingTask": True, "githubSourceChangeTask": True},
            {"programming": {"codingTask": True}},
            {"generation": {"codingTask": True}},
            {"presentationIntent": "CODE"}, {"prompt": "Repeat this 12 times"},
        ):
            if payload == {}:
                self.assertTrue(guard_eligible(payload))
            else:
                self.assertFalse(guard_eligible(payload))


class WrappedStreamTests(unittest.TestCase):
    def _engine(self, *, event_kind="CANDIDATE_PREVIEW_DELTA"):
        example = '''
def generate_events(payload):
    try:
        for i in range(12):
            yield {"type": EVENT_KIND, "text": LINE[i % 2] + "\\n", "attempt": 1}
        yield {"type": "COMPLETED", "phase": "COMPLETE"}
    finally:
        CLOSED.append(True)
'''
        patched = patch_engine(example, "fixture.py")
        ast.parse(patched)
        scope = {"EVENT_KIND": event_kind, "LINE": [A, B], "CLOSED": []}
        exec(patched, scope)
        return scope

    def test_preview_cleared_then_bounded_status_and_partial_terminal(self):
        scope = self._engine()
        events = list(scope["generate_events"]({"prompt": "Compose an original song"}))
        self.assertTrue(scope["CLOSED"])
        self.assertLess(len(events), 12)
        self.assertEqual(events[-1]["type"], "COMPLETED")
        self.assertEqual(events[-1]["phase"], "PARTIAL")
        self.assertTrue(any(e["type"] == "CANDIDATE_PREVIEW_RESET" for e in events))
        self.assertTrue(any(e.get("phase") == "REPETITION_LOOP_STOPPED" for e in events))
        self.assertEqual(sum(e["type"] == "DELTA" for e in events), 1)

    def test_delivered_stream_bounded_without_preview_reset(self):
        scope = self._engine(event_kind="DELTA")
        events = list(scope["generate_events"]({"prompt": "Write a rap"}))
        self.assertEqual(events[-1]["phase"], "PARTIAL")
        self.assertFalse(any(e["type"] == "CANDIDATE_PREVIEW_RESET" for e in events))

    def test_coding_exempt_keeps_all_original_events(self):
        scope = self._engine()
        events = list(scope["generate_events"]({"programming": {"codingTask": True}}))
        self.assertEqual(len(events), 13)
        self.assertEqual(events[-1]["phase"], "COMPLETE")
        self.assertFalse(any(e.get("phase") == "REPETITION_LOOP_STOPPED" for e in events))

    def test_patcher_fails_closed_on_reapply(self):
        first = patch_engine("def generate_events(payload):\n    yield {'type':'COMPLETED'}\n")
        with self.assertRaises(ValueError):
            patch_engine(first)


if __name__ == "__main__":
    unittest.main()
