"""Focused offline regression for vision conversation follow-ups and CPU trial.

No model downloads or paid inference are required. Exercise the same station
functions used at runtime, without importing the heavy Station web app.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "hf_space"


def load_function(path: str, name: str, namespace: dict):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"), filename=path)
    found = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(found) == 1, (path, name)
    code = compile(ast.fix_missing_locations(ast.Module(body=found, type_ignores=[])), path, "exec")
    exec(code, namespace)
    return namespace[name]


class VisionConversationIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = {"re": re, "copy": copy}
        cls.scope["vision_handoff_from_message"] = lambda msg: (
            {"description": "unverified"}
            if msg.get("role") == "user"
            and "[Uploaded image — vision description, not original pixels]" in msg.get("text", "")
            else None
        )
        cls.topic_shift = staticmethod(load_function("station.py", "_companion_topic_shift_from_vision", cls.scope))
        cls.project = staticmethod(load_function("station.py", "_history_projection", cls.scope))

    def test_current_social_message_addresses_assistant(self):
        for prompt in (
            "How are you doing, §wyrlz?",
            "How are you doing, swyrlz?",
            "How's §wyrlz doing?",
            "No, I was talking to you, not the image.",
            "No, I'm talking to you, not about the picture.",
            "I meant you, §wyrlz, not the mage.",
            "I'm asking you how you are.",
        ):
            with self.subTest(prompt=prompt):
                self.assertTrue(self.topic_shift(prompt))

    def test_visual_followups_keep_image_context(self):
        for prompt in (
            "What can you see in this image?",
            "Is that a sleeve or a cape in the side view?",
            "Which motif is on the robe, not the hood?",
            "I meant the image, not you.",
        ):
            with self.subTest(prompt=prompt):
                self.assertFalse(self.topic_shift(prompt))

    def test_multiple_image_trials_are_isolated_only_when_conversation_shifts(self):
        img = "[Uploaded image — vision description, not original pixels]"
        messages = [
            {"role": "user", "text": "Hello there", "id": "a"},
            {"role": "assistant", "text": "Hi!", "id": "b"},
            {"role": "user", "text": "What can you see?\n" + img + "Mage front view", "id": "c"},
            {"role": "assistant", "text": "Mage image analysis L1", "id": "d"},
            {"role": "user", "text": "What can you see?\n" + img + "Mage front view L2", "id": "e"},
            {"role": "assistant", "text": "Mage image analysis L2", "id": "f"},
        ]
        original = copy.deepcopy(messages)
        thread = {"messages": messages}
        social = self.project(thread, "No, I'm talking to you, not about the picture.")
        self.assertEqual([item["id"] for item in social], ["a", "b"])
        visual = self.project(thread, "Compare the staff details between both pictures.")
        self.assertEqual([item["id"] for item in visual], ["a", "b", "c", "d", "e", "f"])
        self.assertEqual(messages, original, "Inference projection must not mutate saved chat")


class CPUTrialTests(unittest.TestCase):
    def test_normal_chat_decode_budget_stays_within_affinity(self):
        scope = {"_cpu_capacity": lambda: 16}
        thread_plan = load_function("lfm2_700m_engine.py", "_thread_plan", scope)
        self.assertEqual(thread_plan(), (10, 16))
        scope["_cpu_capacity"] = lambda: 6
        self.assertEqual(thread_plan(), (6, 6))

    def test_vision_thread_trial_retains_single_job_limit(self):
        tree = ast.parse((ROOT / "qwen3vl_local_server.py").read_text(encoding="utf-8"))
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        values[target.id] = node.value.value
        self.assertEqual(
            (values["DECODE_THREADS"], values["BATCH_THREADS"], values["PARALLEL_REQUESTS"]),
            (8, 14, 1),
        )


if __name__ == "__main__":
    unittest.main()
