"""Word-target boundaries and bounded real-callback expansion orchestration."""
import copy
import unittest

from longform_completion import (complete_longform, expansion_messages,
                                 longform_contract, longform_validation, prose_word_count)

PROMPT = ("Write a detailed 1,200-word explanation of how ocean currents affect climate. "
          "Discuss several distinct mechanisms and regional examples, then finish with a brief conclusion.")


class LongformCompletion(unittest.TestCase):
    def test_ranges_upper_bounds_and_approximate_targets_keep_normal_handling(self):
        # An1100-word answer can satisfy these ranges; imposing1200 is wrong.
        for request in ("Write a 1000-1200-word explanation.", "Write a 1000–1200-word explanation.",
                        "Write between 1000 and 1200 words about oceans.",
                        "Write from 1000 to 1200 words about oceans.",
                        "Write an explanation within 1200 words.",
                        "Write an explanation limited to 1200 words.",
                        "Write less than 1200 words about oceans.",
                        "Write a maximum of 1200 words about oceans.",
                        "Write about 1200 words about oceans.",
                        "Write around 1200 words about oceans.",
                        "Write roughly 1200 words about oceans.",
                        "Write approximately 1200 words about oceans."):
            with self.subTest(request=request):
                self.assertIsNone(longform_contract(request))

    def test_explicit_deliverable_and_brief_conclusion_preserve_large_target(self):
        contract = longform_contract(PROMPT)
        self.assertEqual(contract["requestedWords"], 1200)
        self.assertEqual(longform_contract("In 1500 words, explain how a community garden operates.")["minimumWords"], 1500)
        for request in ("What is a 1200-word explanation?", "Explain why 1200-word reports are common.",
                        "Write no more than 1200 words about oceans.", "Write up to 1200 words about oceans.",
                        "Write exactly 1200 words about oceans.", "Write a 1200-word poem.",
                        "Write a 1200-word explanation as JSON.", "Translate this 1200-word document.",
                        "Write a 1200-word explanation in Japanese.", "Write a 20000-word book.",
                        "Write a 1200-word outline only.", "Write 1200 words but keep the answer brief."):
            with self.subTest(request=request):
                self.assertIsNone(longform_contract(request))
        for flags in ({"programming": {"codingTask": True}}, {"response_mode": "RESPONSE MODE: USER-IDENTITY-DIRECT"},
                      {"response_mode": "RESPONSE MODE: EXACT-NUMBERED-STEPS"}, {"source_change_mode": "candidate"},
                      {"creative": True}, {"file_dialogue": True}):
            self.assertIsNone(longform_contract(PROMPT, **flags))

    def test_full_original_instruction_and_draft_are_retained_without_rewriting(self):
        original = [{"role": "system", "content": "Use verified facts only."},
                    {"role": "user", "content": PROMPT}]
        before = copy.deepcopy(original)
        draft = "Ocean circulation redistributes heat.\n\nA brief conclusion.\r\n"
        revised = expansion_messages(original, draft, longform_contract(PROMPT))
        self.assertEqual(revised[:len(original)], original)
        self.assertEqual(revised[-2], {"role": "assistant", "content": draft})
        self.assertIn("1200", revised[-1]["content"])
        self.assertIn("do not invent facts", revised[-1]["content"].lower())
        revised[0]["content"] = "changed copy"
        self.assertEqual(original, before)

    def run_model(self, outputs, *, budget=8192, context=32768, counts=None):
        calls = []
        def generate(messages, maximum, temperature):
            text, finish = outputs[len(calls)]
            calls.append({"messages": copy.deepcopy(messages), "maximum": maximum})
            return text, {"finishReason": finish, "requestedMaxTokens": maximum,
                          "durationMs": 1, "firstTokenLatencyMs": 1, "deltaChunks": 1}
        result = complete_longform(messages=[{"role": "user", "content": PROMPT}],
            contract=longform_contract(PROMPT), max_output_tokens=budget,
            context_tokens=context, safety_tokens=128, temperature=0.4,
            generate=generate, count_message_tokens=(counts or (lambda messages: sum(prose_word_count(m["content"]) for m in messages))),
            count_text_tokens=prose_word_count)
        return result, calls

    def test_short_normally_stopped_document_gets_one_full_model_revision(self):
        first = "ocean " * 630
        second = "climate " * 1200
        result, calls = self.run_model([(first, "stop"), (second, "stop")])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1]["maximum"], 8192-631)
        self.assertEqual(calls[1]["messages"][-2]["content"], first)
        self.assertEqual(result["text"], second)
        self.assertEqual(result["selectedAttempt"], 2)
        self.assertEqual(result["spentOutputTokens"], 1832)
        self.assertEqual(result["attempts"][0]["outputTokenAccounting"], "visible-text-tokenizer-plus-one-stop-token-estimate")
        self.assertEqual(result["validation"]["status"], "PASS")
        self.assertEqual(result["validation"]["verificationState"], "REQUESTED_LENGTH_ONLY")

    def test_a_complete_document_does_not_request_expansion(self):
        text = "current " * 1200
        result, calls = self.run_model([(text, "stop")])
        self.assertEqual(len(calls), 1)
        self.assertFalse(result["expansionAttempted"])
        self.assertEqual(result["text"], text)

    def test_second_underlength_draft_remains_rejected_and_is_never_padded(self):
        first, second = "first " * 630, "second " * 881
        result, calls = self.run_model([(first, "stop"), (second, "stop")])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["text"], second)
        self.assertEqual(result["validation"]["status"], "REJECT")
        self.assertIn("longform-underlength:881/1200", result["validation"]["reasons"])

    def test_truncated_replacement_never_replaces_a_normally_stopped_draft(self):
        first, second = "first " * 630, "unfinished " * 1200
        result, calls = self.run_model([(first, "stop"), (second, "length")])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["selectedAttempt"], 1)
        self.assertEqual(result["text"], first)
        self.assertEqual(result["validation"]["status"], "REJECT")
        self.assertIn("model-output-token-limit", result["attempts"][1]["validation"]["reasons"])

    def test_context_and_total_output_bounds_do_not_clip_original_messages(self):
        for kwargs in ({"budget": 800}, {"context": 2048, "counts": lambda messages: 100 if len(messages)==1 else 1800}):
            result, calls = self.run_model([("ocean " * 630, "stop")], **kwargs)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["text"], "ocean " * 630)
            self.assertEqual(result["validation"]["status"], "REJECT")
            self.assertEqual(result["stoppedReason"], "longform-expansion-context-or-output-budget")

    def test_unknown_stop_or_observed_limit_cannot_pass_a_length_check(self):
        for reason in (None, "length", "cancelled"):
            result, calls = self.run_model([("current " * 1200, reason)])
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["validation"]["status"], "REJECT")
        self.assertEqual(prose_word_count("Current-driven heat; Earth's oceans. 1,200."), 6)


if __name__ == "__main__":
    unittest.main()
