"""Synthetic tests; never read user data or make external calls."""
import unittest

from api.action_verification_v1 import proposed_action, supervise, available_context


def response(text):
    yield {"type": "STARTED"}
    for i in range(0, len(text), 23):
        yield {"type": "DELTA", "text": text[i:i + 23]}
    yield {"type": "COMPLETED", "phase": "COMPLETE"}


def answer(events):
    text = ""
    for event in events:
        if event["type"] == "RESET":
            text = ""
        if event["type"] == "DELTA":
            text += event.get("text", "")
    return text


class ActionVerificationTests(unittest.TestCase):
    def test_exclamation_is_not_action(self):
        for s in ["Bruh, that's hilarious!", "You should be proud of that!",
                  "The fries are already there.", "I can understand your frustration."]:
            self.assertFalse(proposed_action(s), s)

    def test_detect_generation_not_user_trigger(self):
        for s in ["You should build a portfolio.",
                  "Would you like me to create one?",
                  "I recommend using your existing documents.",
                  "We could deploy a new version."]:
            self.assertTrue(proposed_action(s), s)

    def test_code_example_not_action(self):
        self.assertFalse(proposed_action("Here is a code sample: \x60\x60\x60text\nYou should build a portfolio.\n\x60\x60\x60"))

    def test_requested_song_does_not_enter_advice_supervisor(self):
        for prompt in ["Write a song about a castle", "Remix the rap with a new hook"]:
            events = list(supervise({"prompt": prompt},
                lambda p: response("We can build a dream tonight, under the stars."),
                lambda p, q: self.fail("Song text is not advice"), lambda: False))
            self.assertEqual(answer(events), "We can build a dream tonight, under the stars.")

    def test_ordinary_chat_keeps_stream_and_no_lookup(self):
        events = list(supervise({"prompt": "Tell me about the afternoon."},
                                lambda p: response("It sounds like a busy afternoon. Glad you got everything cleared."),
                                lambda p, q: self.fail("No lookup for ordinary chat"),
                                lambda: False))
        self.assertEqual(answer(events), "It sounds like a busy afternoon. Glad you got everything cleared.")
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_catches_spontaneous_portfolio_advice(self):
        seen, calls = [], []
        payload = {"prompt": "I put in long shifts and want better opportunities.",
                   "historicalEvidence": [{"source": "prior-user-claim",
                                           "excerpt": "I previously built resume and project pages."}]}

        def model(p):
            seen.append(p)
            if p.get("_actionVerificationPass"):
                return response("Your existing resume and projects may help. Let's review their current state before creating anything.")
            return response("You should build yourself a portfolio from scratch.")

        def inventory(p, proposal):
            calls.append(proposal)
            return available_context(p, proposal)

        events = list(supervise(payload, model, inventory, lambda: False))
        self.assertEqual(len(seen), 2)
        self.assertEqual(len(calls), 1)
        self.assertIn("You should build", calls[0])
        self.assertIn("prior-user-claim", seen[1]["responseDirective"])
        self.assertIn("no actual file/project lookup", seen[1]["responseDirective"].lower())
        self.assertNotIn("build yourself", answer(events))
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_no_false_inventory_success(self):
        seen = []
        def model(p):
            seen.append(p)
            return response("I can create a new project for you." if len(seen) == 1
                            else "We can review what exists before planning any new project.")
        events = list(supervise({"prompt": "My projects have grown."}, model,
                                lambda p, q: {"status": "unavailable", "entries": []}, lambda: False))
        self.assertIn("unavailable", seen[1]["responseDirective"])
        self.assertNotIn("I checked your project files", answer(events))

    def test_reset_if_earlier_prose_was_streamed(self):
        initial = "You have accomplished a lot with software. " * 8 + "You should create a portfolio."
        events = list(supervise({"prompt": "I want to change jobs."},
                                lambda p: response("Review your existing work first." if p.get("_actionVerificationPass") else initial),
                                lambda p, q: available_context(p, q), lambda: False))
        self.assertIn("RESET", [x["type"] for x in events])
        self.assertEqual(answer(events), "Review your existing work first.")

    def test_skip_direct_coding(self):
        seen = []
        events = list(supervise({"prompt": "Write a JS function", "codingTask": True},
                                lambda p: response("You should build a function."),
                                lambda p, q: seen.append(q), lambda: False))
        self.assertFalse(seen)
        self.assertEqual(answer(events), "You should build a function.")

    def test_stop_before_lookup(self):
        count = [0]
        def stopped():
            count[0] += 1
            return count[0] > 2
        events = list(supervise({"prompt": "How's the career plan?"},
                                lambda p: response("You should build a portfolio."),
                                lambda p, q: self.fail("Cancelled request must not lookup"),
                                stopped))
        self.assertEqual(events[-1]["type"], "CANCELLED")

    def test_lookup_happens_while_first_generation_is_active(self):
        order = []
        def model(p):
            if p.get("_actionVerificationPass"):
                return response("Review available documents first.")
            def first():
                yield {"type": "STARTED"}
                yield {"type": "DELTA", "text": "You should build a portfolio."}
                order.append("first-generation-continued")
                yield {"type": "COMPLETED"}
            return first()
        def lookup(p, q):
            self.assertNotIn("first-generation-continued", order)
            order.append("lookup")
            return {"status": "context_only", "entries": []}
        events = list(supervise({"prompt": "I want a different career."},
                                model, lookup, lambda: False))
        self.assertEqual(order, ["lookup", "first-generation-continued"])
        self.assertEqual(answer(events), "Review available documents first.")

    def test_context_is_bounded(self):
        p = {"historicalEvidence": [{"source": "test", "excerpt": "x" * 100000}] * 200}
        c = available_context(p, "proposal")
        self.assertLessEqual(len(c["entries"]), 6)
        self.assertLessEqual(len(c["entries"][0]["excerpt"]), 750)


if __name__ == "__main__":
    unittest.main()
