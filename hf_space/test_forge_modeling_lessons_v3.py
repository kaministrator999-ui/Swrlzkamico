#!/usr/bin/env python3
"""Offline §C v3 context-routing checks. No web calls, inference, editor actions or model training."""
import unittest
from forge_modeling_lessons import select_modeling_lesson
from online_tools import classify_online_request

CTX = {"workspace": "model-atelier", "selectedId": None}

class ModelingLearningV3(unittest.TestCase):
    def test_wave_is_eight_keys_not_three(self):
        answer = select_modeling_lesson("How does our §E Wave gesture animate?", CTX)
        for marker in ("v11.223", "EIGHT", "2.20", "Other gestures", "§C has NO native"):
            self.assertIn(marker, answer, marker)
        self.assertLessEqual(len(answer), 1150)

    def test_fist_is_skeletal_curl(self):
        answer = select_modeling_lesson("Why is §E Fist clenched more tightly now?")
        for marker in ("v11.223", "MCP/PIP/DIP", "thumb CMC", "whole-hand scaling", "§C currently"):
            self.assertIn(marker, answer, marker)

    def test_webxr_joint_count_and_permission(self):
        answer = select_modeling_lesson("How should WebXR hand tracking map to our §E glove?")
        for marker in ("25", "17", "hand-tracking", "handedness", "missing-joint", "NOT yet verified"):
            self.assertIn(marker, answer, marker)

    def test_rig_remains_skeleton_not_editor_authority(self):
        answer = select_modeling_lesson("Rig the new §E Arcane Glove.")
        self.assertIn("17-bone", answer)
        self.assertIn("NOT a new §C Chat-native", answer)

    def test_research_is_references_not_automatic_tool(self):
        answer = select_modeling_lesson("Search online for WebXR hand tracking references in §E")
        self.assertIn("W3C WebXR", answer)
        self.assertIn("untrusted evidence", answer)
        self.assertIn("Cite ONLY retrieved URLs", answer)
        route = classify_online_request("Search the web for WebXR hand input specification", [], {}, None)
        self.assertTrue(route.get("requested"))
        self.assertEqual(route.get("kind"), "search")

    def test_no_web_or_editor_from_ordinary_hypothetical(self):
        for query in ("How would I connect Quest hand tracking to our §E glove?",
                      "Explain v11.223 Wave rotation in our §E.",
                      "How do I close the fist in §E?"):
            route = classify_online_request(query, [], {}, None)
            self.assertFalse(route.get("requested"), query)
        self.assertEqual(select_modeling_lesson("Tell me a joke about a waving hand"), "")

    def test_negative_planner_action_is_still_clarification(self):
        for query in ("Animate §E Wave with eight keys", "Retarget WebXR Quest hands into §E"):
            answer = select_modeling_lesson(query, CTX, role="planner")
            self.assertIn("disposition=clarify", answer)
            self.assertLessEqual(len(answer), 1150)

    def test_not_replaced_by_export_or_group_topics(self):
        answer = select_modeling_lesson("Export my §E Wave animation to OBJ", CTX)
        self.assertIn("OBJ", answer)
        self.assertIn("EIGHT", answer)

if __name__ == "__main__":
    unittest.main(verbosity=2)
