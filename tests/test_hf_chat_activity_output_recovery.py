"""Regression tests for §C observed work narration and answer-limit recovery."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from api.response_limit_recovery import (
    trim_overlap, should_continue_research, continuation_prompt,
)
from scripts.hf_chat_activity_answer_recovery_v1 import (
    ENGINE_MARKER, UI_MARKER, BRIEF_OLD, STREAM_OLD,
    NARRATION_OLD, TITLE_OLD, SUB_OLD, patch_engine, patch_ui,
)


class ResponseLimitRecoveryTests(unittest.TestCase):
    def test_overlap_only_removes_verified_repeat(self):
        self.assertEqual(trim_overlap("The Diablo II release was 2000.",
                                      "was 2000. The expansion followed in 2001."),
                         " The expansion followed in 2001.")
        self.assertEqual(trim_overlap("Original answer.", "A new sentence."),
                         "A new sentence.")
        self.assertEqual(trim_overlap("Repeated line. Repeated line.",
                                      "Repeated line."), "")
        self.assertEqual(trim_overlap("Earlier text.", ""), "")

    def test_only_real_sourced_noncode_length_routes_continue(self):
        p = {"onlineContext": {"resultCount": 2, "evidence": []}}
        self.assertTrue(should_continue_research("length", p, {}, "", False))
        self.assertFalse(should_continue_research("stop", p, {}, "", False))
        self.assertFalse(should_continue_research("length", {}, {}, "", False))
        self.assertFalse(should_continue_research("length", p, {"codingTask": True}))
        self.assertFalse(should_continue_research("length", p, {}, "candidate"))
        self.assertFalse(should_continue_research("length", p, {}, "", True))
        self.assertFalse(should_continue_research("length",
                                                 {"onlineContext": {"resultCount": 0}}, {}))
        self.assertIn("Do not restart", continuation_prompt())

    def test_engine_patch_exact_scope_and_python_syntax(self):
        baseline = (
            "def sample():\n"
            + BRIEF_OLD + "\n"
            "        pass\n"
            "    with _lock:\n"
            "        for chunk in stream:\n"
            "            if delta:\n"
            "                yield {\"type\":\"DELTA\",\"text\":delta}\n"
            + STREAM_OLD + "\n"
            "    return\n"
        ).encode("utf-8")
        candidate = patch_engine(baseline).decode("utf-8")
        ast.parse(candidate)
        self.assertEqual(candidate.count(ENGINE_MARKER), 2)
        self.assertIn("RESPONSE_CONTINUING", candidate)
        self.assertIn("SOURCE", candidate)
        self.assertIn("continuation_segments<2", candidate)
        self.assertIn("not starting", "not starting")
        with self.assertRaises(RuntimeError):
            patch_engine(candidate.encode("utf-8"))

    def test_ui_reuses_the_existing_timeline(self):
        baseline = (
            NARRATION_OLD + "\n"
            + TITLE_OLD + "\n"
            + SUB_OLD + "\n"
            "      };"
        ).encode("utf-8")
        candidate = patch_ui(baseline).decode("utf-8")
        self.assertEqual(candidate.count(UI_MARKER), 1)
        self.assertEqual(candidate.count("const renderActivityTimelineV238="), 1)
        self.assertIn("activityNarrationV1(events", candidate)
        self.assertIn("Recorded work steps", candidate)
        with self.assertRaises(RuntimeError):
            patch_ui(candidate.encode("utf-8"))

    def test_narration_logic_requires_observed_receipts(self):
        baseline = (
            NARRATION_OLD + "\n" + TITLE_OLD + "\n" + SUB_OLD + "\n      };"
        ).encode("utf-8")
        candidate = patch_ui(baseline).decode("utf-8")
        a = candidate.index("const activityNarrationV1=")
        b = candidate.index("const renderActivityTimelineV238=", a)
        js = candidate[a:b] + """
          const cases=[
            activityNarrationV1([], {active:true,streaming:true}),
            activityNarrationV1([{phase:"RESEARCH_READY"}], {active:true,streaming:true}),
            activityNarrationV1([{phase:"RESEARCH_UNAVAILABLE"}], {active:true}),
            activityNarrationV1([{phase:"RESPONSE_CONTINUING"}], {active:true}),
            activityNarrationV1([{phase:"CODE_DRAFT_CHECKPOINTED"}], {active:true}),
            activityNarrationV1([{phase:"CROSS_CONVERSATION_REVIEW"}], {active:true}),
            activityNarrationV1([{phase:"RESEARCH_READY"}], {active:false}),
          ];
          if(cases[0].detail.includes("sources"))throw Error("invented research");
          if(!cases[1].detail.includes("sources"))throw Error("missing sourced narration");
          if(!cases[2].detail.includes("couldn't retrieve"))throw Error("research outage not reported");
          if(!cases[3].detail.includes("continuing"))throw Error("missing continuation");
          if(!cases[4].detail.includes("checkpoint"))throw Error("missing code checkpoint");
          if(!cases[5].title.includes("conversation"))throw Error("missing history check");
          if(cases[6].title!=="Activity recorded")throw Error("bad collapsed title");
          console.log("ACTIVITY_NARRATION_OBSERVED_EVENTS_PASS");
        """
        result = subprocess.run(["node", "-e", js], capture_output=True,
                                text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ACTIVITY_NARRATION_OBSERVED_EVENTS_PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
