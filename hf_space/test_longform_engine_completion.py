"""Both real engine loops, with controlled drafts rather than quality claims."""
import unittest
from unittest.mock import patch

from test_github_change_model_context import FakeModel, load_engine
from test_longform_completion import PROMPT


class Drafts(FakeModel):
    def __init__(self, outputs):
        super().__init__()
        self.outputs = outputs

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        text, reason = self.outputs[len(self.calls)-1]
        yield {"choices": [{"delta": {"content": text}, "finish_reason": None}]}
        yield {"choices": [{"delta": {}, "finish_reason": reason}]}


class LongformEngineCompletion(unittest.TestCase):
    def generate(self, engine, outputs, prompt=PROMPT, extra=None):
        model = Drafts(outputs)
        with patch.object(engine, "load", return_value=model):
            events = list(engine.generate_events({"prompt": prompt, "history": [], **(extra or {})}))
        return model, events

    def test_underlength_is_revised_before_any_draft_is_published(self):
        first, revised = "ocean " * 630, "climate " * 1200
        for name in ("lfm2_700m_engine", "qwen_coder_engine"):
            with self.subTest(engine=name):
                model, events = self.generate(load_engine(name), [(first, "stop"), (revised, "stop")])
                self.assertEqual(len(model.calls), 2)
                self.assertIn(PROMPT, str(model.calls[1]["messages"]))
                self.assertEqual(model.calls[1]["messages"][-2]["content"], first)
                self.assertEqual("".join(e.get("text", "") for e in events if e["type"]=="DELTA"), revised)
                attempts = [e["attempt"] for e in events if e["type"]=="CANDIDATE_ATTEMPT"]
                self.assertEqual([a["accepted"] for a in attempts], [False, True])
                self.assertEqual([a["selectedForDelivery"] for a in attempts], [False, True])
                observation = next(e["observation"] for e in events if e["type"]=="LONGFORM_COMPLETION")
                self.assertEqual(observation["wordCount"], 1200)
                self.assertLessEqual(observation["spentOutputTokens"], observation["maxOutputTokens"])
                self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_still_short_document_is_a_truthful_failed_request_with_unchanged_draft(self):
        first, revised = "ocean " * 630, "climate " * 881
        for name in ("lfm2_700m_engine", "qwen_coder_engine"):
            with self.subTest(engine=name):
                model, events = self.generate(load_engine(name), [(first, "stop"), (revised, "stop")])
                self.assertEqual(len(model.calls), 2)
                self.assertEqual("".join(e.get("text", "") for e in events if e["type"]=="DELTA"), revised)
                self.assertFalse(any(e["type"]=="COMPLETED" for e in events))
                self.assertEqual(events[-1]["type"], "FAILED")
                self.assertEqual(events[-1]["reason"], "LONGFORM_LENGTH_NOT_MET")
                self.assertEqual(events[-1]["wordCount"], 881)

    def test_truncated_expansion_cannot_corrupt_selected_normally_stopped_validation(self):
        first, unfinished = "ocean " * 630, "climate " * 1200
        for name in ("lfm2_700m_engine", "qwen_coder_engine"):
            with self.subTest(engine=name):
                _, events = self.generate(load_engine(name), [(first, "stop"), (unfinished, "length")])
                self.assertEqual("".join(e.get("text", "") for e in events if e["type"]=="DELTA"), first)
                validation = next(e["validation"] for e in events if e["type"]=="CANDIDATE_VALIDATION")
                self.assertEqual(validation["finishReason"], "stop")
                self.assertEqual(validation["wordCount"], 630)
                self.assertEqual(validation["status"], "REJECT")
                self.assertEqual(events[-1]["reason"], "LONGFORM_LENGTH_NOT_MET")

    def test_nonlongform_and_internal_json_remain_single_normal_model_calls(self):
        for name in ("lfm2_700m_engine", "qwen_coder_engine"):
            engine = load_engine(name)
            for prompt, extra, reply in (
                ("Explain ocean circulation briefly.", {}, "Ocean circulation transports heat."),
                (PROMPT, {"githubSourceChangeTask": "candidate"}, '{"changes":[]}'),
            ):
                with self.subTest(engine=name, prompt=prompt):
                    model, events = self.generate(engine, [(reply, "stop")], prompt, extra)
                    self.assertEqual(len(model.calls), 1)
                    self.assertFalse(any(e["type"]=="LONGFORM_COMPLETION" for e in events))
                    self.assertEqual(events[-1]["type"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
