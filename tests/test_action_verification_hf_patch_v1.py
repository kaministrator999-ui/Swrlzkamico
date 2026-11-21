"""No network or live Hugging Face mutation. Validate appended generation seam."""
import ast
import unittest
from scripts.hf_chat_action_verification_v1_release import patch, MARK


class ActionReleaseTests(unittest.TestCase):
    def test_exact_function_wrapped_without_replacing_existing_logic(self):
        base = b"def generate_events(payload):\n    yield {'type':'COMPLETED'}\n"
        changed = patch(base)
        self.assertIn(MARK.encode(), changed)
        self.assertIn(base.rstrip(), changed)
        ast.parse(changed.decode("utf-8"))
        self.assertIn(b"_actionVerificationPass", changed)
        self.assertIn(b"yield from supervise(", changed)

    def test_no_duplicate_install(self):
        once = patch(b"def generate_events(payload):\n    yield {'type':'COMPLETED'}\n")
        with self.assertRaisesRegex(RuntimeError, "ALREADY_INSTALLED"):
            patch(once)

    def test_no_ambiguous_generation_owner(self):
        with self.assertRaisesRegex(RuntimeError, "SOURCE_DRIFT"):
            patch(b"x=1\n")
        layered = patch(b"def generate_events(payload):\n    yield 1\n"
                        b"def generate_events(payload):\n    yield 2\n")
        self.assertIn(b"_swrlz_original_generate_events_action_v1 = generate_events", layered)


if __name__ == "__main__":
    unittest.main()
