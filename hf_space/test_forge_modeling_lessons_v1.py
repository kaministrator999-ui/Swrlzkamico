#!/usr/bin/env python3
"""Offline routing/permission guard checks; no live model or editor is invoked."""
import json
import pathlib
import unittest

from brain_forge import native_plan_system
from forge_modeling_lessons import select_modeling_lesson

ROOT = pathlib.Path(__file__).resolve().parent


class ForgeModelingLessonTests(unittest.TestCase):
    def test_irrelevant_topics_cost_zero_context(self):
        for prompt in (
            "What's the weather today?",
            "Write a rhyme about purple light.",
            "Tell me about your favorite restaurants.",
            "Explain how regular Python lists work.",
            "I have a sore hand.",  # general health, not editor work
        ):
            self.assertEqual(select_modeling_lesson(prompt), "", prompt)
        self.assertEqual(select_modeling_lesson("Tell me a joke", {"workspace": "model-atelier"}), "")

    def test_explicit_forge_modeling_without_host_is_educational(self):
        for prompt in (
            "In §E Model Atelier, how do I sculpt a thumb?",
            "Does §E support UV texture mapping in the modeler?",
            "How do I rig the floating glove in §E?",
            "§E modeler: group the armor parts.",
        ):
            lesson = select_modeling_lesson(prompt)
            self.assertIn("NOT tool access", lesson, prompt)
            self.assertIn("Never invent IDs", lesson, prompt)

    def test_native_workspace_adds_context_without_new_authority(self):
        context = {"workspace": "model-atelier", "selectedId": None}
        self.assertIn("native Model Atelier", select_modeling_lesson("Edit the mesh material", context))
        self.assertEqual(select_modeling_lesson("Edit the mesh material", {"workspace": "scene"}), "")

    def test_small_scoped_lessons(self):
        topics = {
            "Rig the skeleton in §E": "skin weights",
            "Brush sculpt the palm in §E": "sculptVertexEdits",
            "Group the armor meshes in §E": "non-destructive",
            "Map UV texture in §E": "UVs",
            "Fix the floating glove fingers in §E": "phalanges",
            "Export OBJ from §E Model Atelier": "triangulated",
        }
        for prompt, word in topics.items():
            lesson = select_modeling_lesson(prompt)
            self.assertIn(word, lesson, prompt)
            self.assertLessEqual(len(lesson), 1150)

    def test_planner_only_appends_when_relevant(self):
        operations = {"schema": "source-validated", "operations": ["mesh.add", "mesh.set"]}
        old = native_plan_system(operations)
        unchanged = native_plan_system(operations, prompt="build a fence", summary={"workspace": "scene"})
        self.assertEqual(old, unchanged)
        scoped = native_plan_system(
            operations, prompt="Sculpt the glove in §E Model Atelier",
            summary={"workspace": "model-atelier"})
        self.assertTrue(scoped.startswith(old))
        self.assertIn("disposition=clarify", scoped)
        self.assertIn(json.dumps(operations, ensure_ascii=False, separators=(",", ":")), scoped)

    def test_v11220_weighted_rig_and_conditional_chat_pose(self):
        cases = [
            "Can I rig the Arcane Glove in §E?",
            "How can I rotate the thumb joint in §E Model Atelier?",
            "§E: Are the skeleton and skin weights real for the new hand?",
        ]
        for prompt in cases:
            lesson = select_modeling_lesson(prompt)
            self.assertIn("v11.220", lesson)
            self.assertIn("17-bone", lesson)
            self.assertIn("SkinnedMesh", lesson)
            self.assertIn("Studio Commands v1", lesson)
            self.assertIn("old saved gloves", lesson)
            self.assertLessEqual(len(lesson), 1150)

    def test_v11220_keyframes_and_poses_have_separate_lesson(self):
        prompts = (
            "How do I save a pose keyframe in §E?",
            "How do I edit the glove timeline in §E?",
            "§E modeler: play a rigged glove animation clip",
        )
        for prompt in prompts:
            lesson = select_modeling_lesson(prompt)
            self.assertIn("Save/Delete key", lesson)
            self.assertIn("32 ordered keys", lesson)
            self.assertIn("2+ to animate", lesson)
            self.assertIn("OBJ", lesson)
            self.assertIn("Studio Commands v1", lesson)
            self.assertLessEqual(len(lesson), 1150)

    def test_pose_terms_do_not_trigger_on_non_editor_conversation(self):
        for prompt in (
            "Pose for a photo with your hand.",
            "Write a poem about a skeleton.",
            "Describe a film animation clip.",
            "I am playing on my Quest.",
        ):
            self.assertEqual(select_modeling_lesson(prompt), "", prompt)

    def test_planner_refuses_commands_outside_supplied_allowlist(self):
        contract = {"schema": "typed-allowed-only", "operations": ["mesh.add"]}
        answer = native_plan_system(
            contract, prompt="§E Model Atelier: pose the glove thumb and save a keyframe",
            summary={"workspace": "model-atelier"})
        self.assertIn("JSON object only", answer)
        self.assertIn("no extra operation types", answer)
        self.assertIn("Studio Commands v1", answer)

    def test_response_engines_share_selector_without_altering_permission_schema(self):
        for file in ("lfm2_700m_engine.py", "qwen_coder_engine.py"):
            source = (ROOT / file).read_text(encoding="utf-8")
            self.assertEqual(source.count("select_modeling_lesson("), 1, file)
            self.assertIn('native_evidence if isinstance(native_evidence, dict) else None', source)
            self.assertLess(source.index("modeling_lesson") if "modeling_lesson" in source else source.index("lesson = select_modeling_lesson("),
                            source.index('online_context=payload.get("onlineContext")'))
        planner_source = (ROOT / "forge_chat_actions.py").read_text(encoding="utf-8")
        self.assertIn("native_plan_system(operation_contract(), prompt=prompt, summary=summary)", planner_source)
        self.assertIn("validate_operations(context, plan[\"operations\"])", planner_source)
        self.assertNotIn('"mesh.group":', planner_source)
        self.assertNotIn('"mesh.sculpt":', planner_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
