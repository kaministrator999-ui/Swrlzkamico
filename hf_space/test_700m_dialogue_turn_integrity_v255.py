"""Dependency-free regression for 700M conversation-turn context trimming."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ENGINE = Path(__file__).resolve().parent / "lfm2_700m_engine.py"


def load_fitter():
    source = ast.parse(ENGINE.read_text(encoding="utf-8"))
    selected = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "_fit_messages")
    namespace = {
        "INPUT_BUDGET_TOKENS": 45,
        "CONTEXT_TOKENS": 100,
        "MIN_OUTPUT_TOKENS": 12,
        "OUTPUT_TOKENS": 30,
        "CONTEXT_SAFETY_TOKENS": 5,
        "_token_count": lambda model, messages: sum(len(str(m["content"]).split()) + 2 for m in messages),
    }
    exec(compile(ast.Module(body=[selected], type_ignores=[]), str(ENGINE), "exec"), namespace)
    return namespace["_fit_messages"]


class DialogueTurnIntegrity(unittest.TestCase):
    def setUp(self):
        self.fit = load_fitter()

    def test_overflow_drops_user_and_assistant_together(self):
        history = [
            {"role": "user", "content": "obsolete " * 21},
            {"role": "assistant", "content": "old reply about obsolete task"},
            {"role": "user", "content": "read the main start document"},
            {"role": "assistant", "content": "the main project router is here"},
        ]
        messages, removed, *_ = self.fit(None, "current", history, "Please follow that document")
        self.assertEqual(removed, 2)
        self.assertEqual([m["role"] for m in messages], ["system", "user", "assistant", "user"])
        self.assertNotIn("old reply", str(messages))
        self.assertIn("main start", str(messages))

    def test_initial_orphan_assistant_is_removed(self):
        history = [
            {"role": "assistant", "content": "old orphan " * 35},
            {"role": "user", "content": "the important task"},
            {"role": "assistant", "content": "important context"},
        ]
        messages, removed, *_ = self.fit(None, "current", history, "correct that")
        self.assertEqual(removed, 1)
        self.assertEqual(messages[1]["role"], "user")

    def test_no_overflow_preserves_every_message(self):
        history = [
            {"role": "user", "content": "I said start"},
            {"role": "assistant", "content": "I routed to engine"},
            {"role": "user", "content": "not engine, main"},
        ]
        messages, removed, *_ = self.fit(None, "current", history, "yes")
        self.assertEqual(removed, 0)
        self.assertEqual(messages[1:-1], history)

    def test_unfittable_current_prompt_still_fails_closed(self):
        with self.assertRaises(ValueError):
            self.fit(None, "system " * 40, [], "current " * 30)


if __name__ == "__main__":
    unittest.main()
