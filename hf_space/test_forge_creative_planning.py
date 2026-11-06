"""Creative-planning policy and unchanged execution boundaries.

These tests inspect the instructions actually sent through native planning and
exercise review/abstention with controlled inference. Live model adherence and
character quality still require a real §c run.
"""
import json
import unittest
from unittest.mock import Mock

from brain_forge import native_plan_system, requests_new_project
from forge_chat_actions import operation_contract, native_plan_response_format, validate_operations
import test_forge_chat_actions as fixture


class CreativePlanningTests(unittest.TestCase):
    def setUp(self):
        self.planner = fixture.PlannerTest("runTest")
        self.planner.setUp()
        self.addCleanup(self.planner.doCleanups)
        self.summary = self.planner.summary
        self.summary["project"]["name"] = "Little Crystal Mage"
        self.summary["starters"] = [{"id": "blank-model", "name": "Blank Model"}]

    def test_existing_character_request_reaches_creative_policy_and_exact_preview(self):
        prompt = ('The active model is already named "Little Crystal Mage". '
                  'Preview a chibi mage inside this existing Model Atelier: '
                  'purple robe, cream face, violet eyes and a curved wooden staff. '
                  'Choose descriptive names and proportions for its parts.')
        parts = [{"op": "mesh.add", "kind": "sphere", "name": "Mage face",
                  "position": [0, 2.7, .2], "scale": [.6, .6, .3], "color": "#ffead4"},
                 {"op": "mesh.add", "kind": "cone", "name": "Purple robe",
                  "position": [0, 1.2, 0], "scale": [.8, 1, .6], "color": "#643774"}]
        events = self.planner.run_events(prompt=prompt, operations=parts)
        self.assertFalse(requests_new_project(prompt))
        messages = self.planner.infer.call_args.args[0]
        system = messages[0]["content"]
        self.assertIn("Work inside the current active project.", system)
        self.assertIn("choose descriptive names for new parts", system)
        self.assertIn("These design choices do not require", system)
        self.assertNotIn("If no project name or starter choice is clear", system)
        self.assertEqual(json.loads(messages[1]["content"])["currentUserRequest"], prompt)
        self.assertEqual(events[-1]["forgeStatus"], "DESIGN_PREVIEW")
        self.assertEqual(self.planner.stage.call_args.args[1], parts)
        self.planner.register.assert_not_called()
        self.planner.wait.assert_not_called()

    def test_new_project_policy_is_limited_to_explicit_creation(self):
        contract = operation_contract(self.summary)
        create = 'Create a new project from the blank-model starter named exactly "  Mage §§!  "'
        system = native_plan_system(contract, prompt=create, summary=self.summary)
        self.assertTrue(requests_new_project(create))
        self.assertIn("This request explicitly creates a separate project.", system)
        self.assertIn("If no project name or starter choice is clear", system)
        self.assertIn("must not be combined with object edits", system)
        edit = 'Add a sphere mesh named exactly "  Mage §§!  " in my current project'
        system = native_plan_system(contract, prompt=edit, summary=self.summary)
        self.assertFalse(requests_new_project(edit))
        self.assertIn("project.create is not requested.", system)
        self.assertNotIn("If no project name or starter choice is clear", system)
        self.assertIn("Preserve its exact requested names/text", system)
        self.assertIn("Preserve any exact part names and dimensions", system)

    def test_ambiguous_existing_target_can_still_abstain_without_retry_or_write(self):
        question = "Which mesh should I change?"
        infer = Mock(return_value=(json.dumps({"disposition": "clarify", "operations": [],
                                              "question": question}), {"finishReason": "stop"}))
        events = self.planner.run_events(prompt="Change a mesh to gold", infer=infer)
        system = infer.call_args.args[0][0]["content"]
        self.assertIn("If an existing target is ambiguous", system)
        self.assertIn("never resolves an ambiguous existing target", system)
        infer.assert_called_once()
        self.assertEqual(events[-1]["forgeStatus"], "CLARIFICATION")
        self.assertEqual(events[-2]["text"], question)
        self.planner.register.assert_not_called()
        self.planner.stage.assert_not_called()
        self.planner.wait.assert_not_called()

    def test_creative_discretion_does_not_admit_invented_existing_target(self):
        operations = [{"op": "mesh.set", "id": "imaginary-face", "color": "#ffead4"}]
        events = self.planner.run_events(prompt="Change the face mesh to cream", operations=operations)
        self.assertEqual(events[-1]["type"], "FAILED")
        self.assertFalse(any(e["type"] == "FORGE_BATCH_READY" for e in events))
        self.planner.register.assert_not_called()
        self.planner.stage.assert_not_called()
        self.planner.wait.assert_not_called()

    def test_mesh_inference_grammar_requires_complete_visual_fields_in_natural_order(self):
        self.summary["meshTools"] = {"schema": "swrlz-forge-mesh-tools-v2", "kinds":
                                    ["sphere", "box", "cone", "cylinder", "loft", "lathe"],
                                    "maxOperations": 64}
        shape = native_plan_response_format(self.summary)["schema"]["oneOf"][0]
        variants = shape["properties"]["operations"]["items"]["oneOf"]
        visual = ["op", "kind", "name", "position", "rotation", "scale", "color", "material"]
        for variant in variants:
            if variant["properties"]["op"]["const"] != "mesh.add":
                continue
            kind = variant["properties"]["kind"]["const"]
            geometry = (["path", "radii", "segments"] if kind == "loft" else
                        ["profile", "arcStart", "arcLength", "segments"] if kind == "lathe" else [])
            with self.subTest(kind=kind):
                self.assertEqual(list(variant["properties"]), visual + geometry)
                self.assertEqual(variant["required"], visual + geometry)
                self.assertFalse(variant["additionalProperties"])
        # Existing-target edits still allow changing just the requested field.
        target = next(v for v in variants if v["properties"]["op"]["const"] == "mesh.set")
        self.assertEqual(set(target["required"]), {"op", "id"})

    def test_inference_requirements_do_not_change_legacy_native_acceptance(self):
        minimal = [{"op": "mesh.add", "kind": "sphere"}]
        self.assertEqual(validate_operations(self.planner.context, minimal), minimal)
        self.summary["meshTools"] = {"schema": "swrlz-forge-mesh-tools-v2", "kinds":
                                    ["sphere", "box", "cone", "cylinder", "loft", "lathe"],
                                    "maxOperations": 64}
        lathe = [{"op": "mesh.add", "kind": "lathe", "profile": [[.5, 0], [.2, 1]]}]
        self.assertEqual(validate_operations(self.planner.context, lathe), lathe)

    def test_visual_quality_instructions_reach_real_planning_call(self):
        prompt = "Preview a paired wheel model with blue wheels and a bent gold axle in §E"
        self.planner.run_events(prompt=prompt, operations=[{"op": "mesh.add", "kind": "sphere"}])
        system = self.planner.infer.call_args.args[0][0]["content"]
        self.assertIn("assign the requested hex palette to the appropriate parts", system)
        self.assertIn("distinct opposite-X centers", system)
        self.assertIn("bottom-to-top Y order", system)
        self.assertIn("arcStart=1 and arcLength=4.283185", system)
        self.assertIn("at least three noncollinear path points", system)
        self.assertIn("Check each part's world extent", system)


if __name__ == "__main__":
    unittest.main(verbosity=2)
