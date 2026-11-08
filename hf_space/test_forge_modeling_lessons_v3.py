#!/usr/bin/env python3
"""Offline v3 source-grounded WebXR hand mapping and wrist-wave lesson gates.

No live WebXR, real web retrieval, language-model evaluation or editor action.
"""
import unittest
from forge_modeling_lessons import select_modeling_lesson
from online_tools import classify_online_request


class ModelingLearningV3(unittest.TestCase):
    def test_webxr_joint_space_not_a_direct_seventeen_bone_binding(self):
        s = select_modeling_lesson("How would §E WebXR hand tracking retarget to our glove?")
        for term in ("25 XRHand", "17 target", "metacarpals", "CMC/MCP/IP",
                     "parent-local rotations", "No §C/§E WebXR capture/retarget bridge"):
            self.assertIn(term, s)
        self.assertLessEqual(len(s), 1150)

    def test_hand_tracking_needs_verified_sample_and_consent(self):
        s = select_modeling_lesson("§E Model Atelier: Quest hand tracking capture")
        self.assertIn("opted-in hand-tracking XR session", s)
        self.assertIn("handedness", s)
        self.assertIn("null/occlusion", s)
        self.assertIn("Studio Commands v1 keyframe writes are manually", s)
        self.assertIn("dense capture needs new work", s)

    def test_wave_bends_wrist_over_eight_keys_and_other_gestures_remain_three(self):
        s = select_modeling_lesson("Animate the Wave gesture of my §E glove")
        for term in ("14 native gesture presets", "v11.223 Wave", "8 keys",
                     "2.20 seconds", "3 keys", "1.5 seconds", "No §C-native gesture action"):
            self.assertIn(term, s)
        self.assertLessEqual(len(s), 1150)

    def test_research_includes_w3c_and_source_priority(self):
        s = select_modeling_lesson("Find official WebXR and §E glove rig references")
        self.assertIn("W3C WebXR Hand Input", s)
        self.assertIn("untrusted evidence", s)
        self.assertIn("Cite ONLY retrieved URLs", s)

    def test_no_automatic_web_fetch_for_general_modeling_question(self):
        for question in ("How could §E use Quest hands?", "Explain §E wrist bone mapping."):
            route = classify_online_request(question, [], {}, None)
            self.assertFalse(route.get("requested"), (question, route))

    def test_unrelated_webxr_queries_do_not_receive_forge_instruction(self):
        for question in ("What is WebXR?", "Find the latest Quest hand tracking specs.",
                         "How do I animate a presentation?", "Play some music."):
            self.assertEqual(select_modeling_lesson(question), "")

    def test_planner_unsupported_action_remains_clarify(self):
        s = select_modeling_lesson("Record WebXR glove hand motion in §E", 
                                   {"workspace": "model-atelier"}, role="planner")
        self.assertIn("disposition=clarify", s)
        self.assertLessEqual(len(s), 1150)


if __name__ == "__main__":
    unittest.main(verbosity=2)
