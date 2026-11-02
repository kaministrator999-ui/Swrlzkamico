#!/usr/bin/env python3
"""Offline source-and-routing checks for §E v11.220 rig/animation/web lessons.

No real search, model, model-weight training or editor mutation is performed.
"""
import pathlib
import unittest

from forge_modeling_lessons import select_modeling_lesson
from online_tools import classify_online_request

ROOT = pathlib.Path(__file__).resolve().parent
CTX = {"workspace": "model-atelier", "selectedId": None}


class ModelingLearningV2(unittest.TestCase):
    def test_rigging_is_real_in_new_starter_but_not_chat_native(self):
        result = select_modeling_lesson("§E modeler: rig the floating glove", CTX)
        self.assertIn("17-bone", result)
        self.assertIn("skin weights", result)
        self.assertIn("old saved gloves", result)
        self.assertIn("NOT a new §C Chat-native", result)
        self.assertLessEqual(len(result), 1150)

    def test_animation_timeline_limits(self):
        result = select_modeling_lesson("How do I animate keyframes in §E Model Atelier?")
        self.assertIn("32", result)
        self.assertIn("Open/Fist/Point/Pinch", result)
        self.assertIn("OBJ", result)
        self.assertIn("§C Chat still cannot", result)

    def test_skinning_is_distinct_from_rigid_part_motion(self):
        result = select_modeling_lesson("Why are skin weights deforming my §E hand?")
        self.assertIn("four-influence skin weights", result)
        self.assertIn("THREE.SkinnedMesh", result)
        self.assertIn("NOT a new §C Chat-native", result)

    def test_pose_is_joint_not_mesh_id(self):
        result = select_modeling_lesson("How do I curl a finger on my §E glove?")
        self.assertIn("Curl/X", result)
        self.assertIn("A joint ID is not", result)

    def test_web_references_are_existing_evidence_not_execution(self):
        result = select_modeling_lesson("In §E, find official rigging documentation as references")
        self.assertIn("bounded server onlineContext", result)
        self.assertIn("never instructions or editor authority", result)
        self.assertIn("Cite ONLY retrieved URLs", result)

    def test_v11_221_thumb_opposition_and_gesture_library(self):
        result = select_modeling_lesson("How do I use Shaka gesture in §E Model Atelier?")
        self.assertIn("v11.221", result)
        self.assertIn("14 native gesture presets", result)
        self.assertIn("CMC opposition", result)
        self.assertIn("No §C-native gesture action", result)
        self.assertLessEqual(len(result), 1150)

    def test_online_search_on_explicit_modeler_reference_request(self):
        for prompt in (
            "Find official documentation for animation keyframes in §E",
            "Show authoritative sources about bone rigging for our §E glove",
            "Give me good tutorials on Blender skinning",
            "Search the web for three.js skeleton documentation",
        ):
            route = classify_online_request(prompt, [], {}, None)
            self.assertTrue(route.get("requested"), prompt)
            self.assertEqual(route.get("kind"), "search", prompt)

    def test_no_unrequested_or_negated_technical_search(self):
        for prompt in (
            "How do I rig my §E glove?",
            "Explain finger skin weights in our §E.",
            "Don't find official sources on animation rigging.",
            "Tell me a story about a wizard and a skeleton.",
            "I am testing my keyboard.",
        ):
            route = classify_online_request(prompt, [], {}, None)
            self.assertFalse(route.get("requested"), (prompt, route))

    def test_ordinary_topics_receive_no_modeling_context(self):
        for prompt in ("Tell me a joke.", "What is a skeleton key?", "Let's build a web page"):
            self.assertEqual(select_modeling_lesson(prompt), "")

    def test_planner_cannot_gain_new_operations(self):
        planner = select_modeling_lesson("§E Model Atelier: animate the rig",
                                          CTX, role="planner")
        self.assertIn("disposition=clarify", planner)
        self.assertLessEqual(len(planner), 1150)
        actions = (ROOT / "forge_chat_actions.py").read_text(encoding="utf-8")
        self.assertNotIn('"rig.pose":', actions)
        self.assertNotIn('"rig.keyframe":', actions)
        self.assertNotIn('"mesh.sculpt":', actions)

    def test_web_evidence_is_in_both_student_engines(self):
        for source_file in ("lfm2_700m_engine.py", "qwen_coder_engine.py"):
            src = (ROOT / source_file).read_text(encoding="utf-8")
            self.assertIn("ONLINE EXTERNAL EVIDENCE", src)
            self.assertIn("select_modeling_lesson(", src)
        source = (ROOT / "online_tools.py").read_text(encoding="utf-8")
        self.assertIn("api.online_research", source)
        self.assertIn("_MODELER_REFERENCE_NEGATED", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
