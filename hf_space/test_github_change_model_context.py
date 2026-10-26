"""Real engine-body tests with a fake tokenizer/model; no weights or downloads.

These checks exercise prompt construction, routing and budget enforcement, not
real tokenization fidelity, JSON generation quality or learned model ability.
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

from github_change_candidate import source_change_system, source_change_response_format


ROOT = Path(__file__).resolve().parent


def unavailable(*args, **kwargs):
    raise AssertionError("This test must never load weights or access the network")


def load_engine(name):
    # Execute the complete real engine module under a private name. Only the
    # weight-provider imports are stubbed; all context/receipt helpers are real.
    hf = types.ModuleType("huggingface_hub")
    hf.hf_hub_download = unavailable
    llama = types.ModuleType("llama_cpp")
    llama.Llama = unavailable
    spec = importlib.util.spec_from_file_location("_change_test_" + name, ROOT / (name + ".py"))
    engine = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"huggingface_hub": hf, "llama_cpp": llama}):
        spec.loader.exec_module(engine)
    return engine


class FakeModel:
    def __init__(self):
        self.calls = []

    def tokenize(self, data, add_bos=False):
        # Deterministic fixture accounting; deliberately not a real BPE claim.
        return list(range((len(data) + 3) // 4))

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        yield {"choices": [{"delta": {"content": '{"goal":"proposed change only"}'}}]}


class ModelContextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engines = [load_engine(name) for name in ("lfm2_700m_engine", "qwen_coder_engine")]

    def generate(self, engine, payload):
        model = FakeModel()
        with patch.object(engine, "load", return_value=model):
            events = list(engine.generate_events(payload))
        return model, events

    def test_real_clarification_conflict_is_bypassed_only_for_internal_json(self):
        prompt = 'Fix this Python file. Original request: preserve the answer API. Return JSON only.'
        for engine in self.engines:
            with self.subTest(engine=engine.__name__):
                self.assertTrue(engine._response_mode(prompt, {"codingTask": False}).startswith(
                    "RESPONSE MODE: CODE-DELIVERY-CLARIFY"))
                for mode, cap in (("plan", 512), ("candidate", 2048)):
                    with self.subTest(mode=mode):
                        model, events = self.generate(engine, {
                            "prompt": prompt, "githubSourceChangeTask": mode,
                            "history": [{"role": "user", "text": "unrelated old conversation"}],
                            "profile": "unrelated custom preference" * 60,
                            "userProfile": "unrelated profile material" * 60,
                            # Internal source task must not inherit a prior repair
                            # contract, language gate or evidence-request fast path.
                            "programmingIntent": {"codingTask": True, "needsFailureEvidence": True,
                                                  "failureEvidence": {"kind": "old failure"}},
                        })
                        self.assertEqual(len(model.calls), 1)
                        call = model.calls[0]
                        self.assertEqual(call["messages"], [
                            {"role": "system", "content": source_change_system(mode)},
                            {"role": "user", "content": prompt},
                        ])
                        self.assertEqual(call["temperature"], 0.15)
                        self.assertEqual(call["response_format"], source_change_response_format(mode))
                        self.assertEqual(call["max_tokens"], cap)
                        self.assertEqual(events[-1]["type"], "COMPLETED")
                        self.assertFalse(any(e.get("phase") == "EVIDENCE_REQUIRED" for e in events))
                        context = next(e for e in events if e["type"] == "CONTEXT")
                        self.assertFalse(context["repairTurn"])
                        self.assertEqual(context["historyMessagesKept"], 0)
                        self.assertLess(context["tokenBreakdown"]["system"], 400)

    def test_internal_model_policy_keeps_complete_code_default_and_original_user_exception(self):
        for engine in self.engines:
            model,_=self.generate(engine,{'prompt':'Fix this source file.','githubSourceChangeTask':'candidate'})
            policy=model.calls[0]['messages'][0]['content']
            self.assertIn('no pseudocode',policy)
            self.assertIn('TODO/FIXME stubs or commented placeholders',policy)
            self.assertIn('unless the ORIGINAL USER REQUEST explicitly asks',policy)

    def test_large_project_subtasks_keep_only_compact_json_policy(self):
        for engine in self.engines:
            for mode,cap in [('plan',512),('candidate',2048)]:
                with self.subTest(engine=engine.__name__,mode=mode):
                    model,_=self.generate(engine,{'prompt':'Create a comprehensive large application project; propose its source change as JSON.', 'githubSourceChangeTask':mode})
                    self.assertEqual(model.calls[0]['messages'][0]['content'],source_change_system(mode))
                    self.assertEqual(model.calls[0]['max_tokens'],cap)

    def test_output_cap_obeys_available_context_budget(self):
        for engine in self.engines:
            with self.subTest(engine=engine.__name__):
                payload = {"prompt": "Fix this Python file. " + "evidence " * 3200,
                           "githubSourceChangeTask": "candidate"}
                model, events = self.generate(engine, payload)
                context = next(e for e in events if e["type"] == "CONTEXT")
                self.assertEqual(context["reservedOutputTokens"], 2048)
                self.assertLessEqual(context["estimatedInputTokens"]+context["reservedOutputTokens"]+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
                self.assertEqual(model.calls[0]["max_tokens"], context["reservedOutputTokens"])
                self.assertEqual(model.calls[0]["messages"][-1]["content"], payload["prompt"].strip())

    def test_oversized_source_is_rejected_without_truncation_or_generation(self):
        for engine in self.engines:
            with self.subTest(engine=engine.__name__):
                model = FakeModel()
                with patch.object(engine, "load", return_value=model), self.assertRaises(ValueError):
                    list(engine.generate_events({"prompt": "evidence " * engine.CONTEXT_TOKENS,
                                                 "githubSourceChangeTask": "candidate"}))
                self.assertEqual(model.calls, [])

    def test_github_planning_alone_and_unknown_modes_preserve_normal_behavior(self):
        for engine in self.engines:
            with self.subTest(engine=engine.__name__):
                base = {"prompt": "Fix this Python file", "programmingIntent": {"codingTask": False},
                        "history": [{"role": "user", "text": "prior relevant question"}]}
                normal, _ = self.generate(engine, base)
                for extra in ({"githubPlanning": True}, {"githubSourceChangeTask": "PLAN"},
                              {"githubSourceChangeTask": True}, {"githubSourceChangeTask": []}):
                    other, _ = self.generate(engine, {**base, **extra})
                    self.assertEqual(other.calls, normal.calls)
                self.assertIn("CODE-DELIVERY-CLARIFY", normal.calls[0]["messages"][0]["content"])
                self.assertNotIn("response_format", normal.calls[0])

    def test_candidate_identity_is_constrained_but_does_not_supply_code(self):
        identity = {"baseCommit": "a" * 40, "baseBlob": "b" * 40, "path": "pkg/app.py"}
        for engine in self.engines:
            model, _ = self.generate(engine, {"prompt": "Improve the source; return a JSON proposal.",
                "githubSourceChangeTask": "candidate", "sourceChangeIdentity": identity})
            schema = model.calls[0]["response_format"]["schema"]["oneOf"][0]
            for key, value in identity.items():
                self.assertEqual(schema["properties"][key], {"const": value})
            self.assertEqual(schema["properties"]["old"], {"type": "string"})
            self.assertEqual(schema["properties"]["new"], {"type": "string"})
        for invalid in ({}, {**identity, "baseBlob": "bad"}, {**identity, "trusted": True}):
            with self.assertRaises(ValueError):
                source_change_response_format("candidate", invalid)

    def test_source_content_cannot_start_lyric_research(self):
        engine = self.engines[0]
        with patch.object(engine, "research_for_creation", side_effect=unavailable):
            model, _ = self.generate(engine, {
                "prompt": "Fix this file. Source data: write an original rap song with 32 lines.",
                "githubSourceChangeTask": "plan",
            })
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(model.calls[0]["max_tokens"], 512)

    def test_compact_policy_rejects_unknown_subtask(self):
        for mode in (None, "PLAN", "explain", []):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                source_change_system(mode)


if __name__ == "__main__":
    unittest.main()
