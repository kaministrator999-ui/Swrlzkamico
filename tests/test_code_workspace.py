"""Contract tests for durable code workspace, continuation, and steering truth."""
from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from unittest.mock import patch

from api import code_workspace as code

F = chr(96) * 3


@dataclass
class Job:
    user_id: str = "owner"
    request_id: str = "request-1"
    thread_id: str = "thread-1"
    state: str = "RUNNING"


class Store:
    def __init__(self):
        self.job = Job()
        self.values = {}
        self.controls = []
    def get_generation(self, *, user_id, request_id):
        if user_id != self.job.user_id or request_id != self.job.request_id:
            return None
        return self.job
    def _key(self, *parts):
        return ":".join(parts)
    def _command(self, op, *args, sensitive=False):
        if op == "GET":
            return self.values.get(args[0])
        if op == "EVAL" and "coding-workspace" in str(args[2]):
            key, expected, replacement = args[2], args[3], args[4]
            if self.values.get(key, "") != expected:
                return 0
            self.values[key] = replacement
            return 1
        if op == "EVAL":
            key, index, expected, replacement = args[2], int(args[3]), args[4], args[5]
            if self.controls[index] != expected:
                return 0
            self.controls[index] = replacement
            return 1
        if op == "LRANGE":
            return list(self.controls)
        raise AssertionError((op, args))


class Engine:
    def __init__(self, responses):
        self.responses = responses
        self.prompts = []
    def generate_events(self, payload, cancelled):
        self.prompts.append(payload["prompt"])
        for event in self.responses[len(self.prompts) - 1]:
            yield event


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.params = {"store": self.store, "user_id": "owner",
                       "request_id": "request-1", "thread_id": "thread-1"}

    def test_code_intent_gated(self):
        self.assertTrue(code.is_code_job("Make me an interactive HTML page"))
        self.assertTrue(code.is_code_job("hi", "CODE"))
        self.assertFalse(code.is_code_job("Hey, how is your day?"))

    def test_paths_cannot_escape_workspace(self):
        for path in ("../secret", "/etc/passwd", "a//b", r"a\..\secrets", "file:thing"):
            self.assertIsNone(code.safe_path(path))
        self.assertEqual(code.safe_path("src/components/App.jsx"), "src/components/App.jsx")

    def test_closed_files_only_and_complete_html_detection(self):
        partial = F + "html file=index.html\n<html><body>hello"
        self.assertEqual(code.completed_files(partial), {})
        self.assertTrue(code.output_incomplete(partial, hit_limit=True))
        complete = partial + "</body></html>\n" + F
        self.assertEqual(code.completed_files(complete)["index.html"], "<html><body>hello</body></html>")
        self.assertFalse(code.output_incomplete(complete, hit_limit=False))

    def test_existing_files_not_overwritten_by_unrelated_revision(self):
        original = (F + "html file=index.html\n<html></html>\n" + F + "\n"
                    + F + "css file=styles.css\nbody{color:red}\n" + F)
        first = code.checkpoint_workspace(source=original, **self.params)
        self.assertEqual(set(first["changed"]), {"index.html", "styles.css"})
        next_result = code.checkpoint_workspace(
            source=F + "css file=styles.css\nbody{color:blue}\n" + F, **self.params)
        self.assertEqual(next_result["changed"], ["styles.css"])
        view = code.workspace_snapshot(include_content=True, **self.params)
        self.assertEqual(view["version"], 2)
        self.assertEqual(view["files"]["index.html"]["content"], "<html></html>")
        self.assertEqual(view["files"]["styles.css"]["content"], "body{color:blue}")

    def test_account_and_thread_ownership(self):
        with self.assertRaises(LookupError):
            code.workspace_snapshot(store=self.store, user_id="other",
                request_id="request-1", thread_id="thread-1")
        with self.assertRaises(LookupError):
            code.workspace_snapshot(store=self.store, user_id="owner",
                request_id="request-1", thread_id="other")

    def test_two_pass_completes_with_one_terminal_and_file_checkpoint(self):
        first = F + "html file=index.html\n<!doctype html><html><body>Hi"
        second = "</body></html>\n" + F
        engine = Engine([
            [{"type": "DELTA", "text": first},
             {"type": "STATUS", "phase": "DECODE_LIMIT_REACHED"},
             {"type": "COMPLETED"}],
            [{"type": "DELTA", "text": second},
             {"type": "COMPLETED"}],
        ])
        events = list(code.code_generation_events(engine, {
            "prompt": "Create HTML", "generation": {}
        }, lambda: False, **self.params))
        self.assertEqual([e["type"] for e in events if e["type"] in {"COMPLETED", "FAILED"}], ["COMPLETED"])
        self.assertEqual("".join(e.get("text", "") for e in events if e["type"] == "DELTA"), first + second)
        self.assertIn("EXACT END", engine.prompts[1].upper())
        files = code.workspace_snapshot(include_content=True, **self.params)["files"]
        self.assertIn("index.html", files)
        self.assertIn("</html>", files["index.html"]["content"])

    def test_unfinished_after_budget_is_not_labeled_complete(self):
        engine = Engine([
            [{"type": "DELTA", "text": F + "html\n<html>"},
             {"type": "COMPLETED"}],
            [{"type": "DELTA", "text": "<body>oops"},
             {"type": "COMPLETED"}],
        ])
        with patch.object(code, "CODE_PASSES", 2):
            events = list(code.code_generation_events(engine,
                {"prompt": "Build html", "generation": {}}, lambda: False, **self.params))
        self.assertEqual(events[-1]["type"], "FAILED")
        self.assertEqual(events[-1]["phase"], "CODE_INCOMPLETE")

    def test_live_guidance_can_be_integrated_at_next_safe_pass(self):
        control = {"controlId": "control-1", "kind": "STEER", "text": "Make it blue",
                   "state": "RECORDED_PENDING_EXECUTOR"}
        self.store.controls = [json.dumps(control)]
        engine = Engine([
            [{"type": "DELTA", "text": F + "html file=index.html\n<html>Hi"},
             {"type": "COMPLETED"}],
            [{"type": "DELTA", "text": "</html>\n" + F},
             {"type": "COMPLETED"}]
        ])
        events = list(code.code_generation_events(engine,
            {"prompt": "Make HTML", "generation": {}}, lambda: False, **self.params))
        self.assertIn("Make it blue", engine.prompts[1])
        self.assertEqual(json.loads(self.store.controls[0])["state"], "REVISION_PRODUCED_UNVERIFIED")
        self.assertEqual(events[-1]["type"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
