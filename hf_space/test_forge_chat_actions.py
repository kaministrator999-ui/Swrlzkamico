"""Bounded native-planning and truthful-receipt regressions; no model/network."""
import json
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

import forge_embed
from brain_forge import classify_forge_intent, inspection_text, requests_new_project
from forge_chat_actions import ForgePlanError, decode_plan, generate_events, validate_operations, explicit_project_plan, _validate_requested_actions


PROJECT = "a" * 32
BATCH = "b" * 32


def native_summary(workspace="model-atelier"):
    return {"projectId": PROJECT, "project": {"name": "Native project", "kind": "scene"},
            "workspace": workspace, "mode": "edit", "epoch": 4, "selectedId": "mesh-1" if workspace == "model-atelier" else "actor-1",
            "meshes": [{"id": "mesh-1", "name": "Exact Name §§", "kind": "box",
                        "position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1], "color": "#ffffff", "material": "matte"}],
            "actors": [{"id": "actor-1", "name": "Wall", "type": "wall", "position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]}],
            "totalMeshes": 1, "totalActors": 1, "canUndo": True, "canRedo": False}


class PlannerTest(unittest.TestCase):
    def setUp(self):
        self.summary = native_summary()
        self.context = forge_embed.AuthorizedForgeContext("c" * 32, "thread-1", "gen-1", PROJECT,
                                                         self.summary, "private-session-key", "private-owner",
                                                         "private-generation-key", "context-hash", object())
        # Capability tests exercise the real encrypted owner backend separately.
        # Here one exact fixture instance represents the already-authorized live
        # context; JSON dictionaries and manufactured instances are denied.
        self.live = True
        def validate(context, require_snapshot=True):
            if context is not self.context or not self.live:
                raise HTTPException(403, "FORGE_SERVER_CONTEXT_REQUIRED")
        self.patcher = patch.object(forge_embed, "revalidate", side_effect=validate)
        self.validation = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def run_events(self, operations=None, *, prompt="Make the selected model red", plan=None,
                   finish="stop", result=None, infer=None, register=None, wait=None, extra=None):
        operations = operations or [{"op": "mesh.set", "id": "mesh-1", "color": "#ff0000"}]
        proposal = plan or {"disposition": "apply", "operations": operations}
        self.infer = infer or Mock(return_value=(json.dumps(proposal), {"finishReason": finish}))
        self.register = register or Mock(return_value=BATCH)
        self.wait = wait or Mock(return_value=result or {"batchId": BATCH, "status": "finished", "allSucceeded": True,
                                                       "receipts": [{"ok": True} for _ in operations]})
        return list(generate_events({"prompt": prompt, **(extra or {})}, self.context, self.register, self.wait, self.infer))

    def test_intent_keeps_explanations_code_and_history_outside_mutation(self):
        for prompt in ("How do I add a cube?", "Explain how to move the selected model", "What if I remove the actor?",
                       "Can the AI create a sphere?", "Do not add a sphere", "Never remove the model",
                       "How would you move the selected mesh?", "Should I add a cube?", "Why did you add a sphere?",
                       "Is it possible to add a box?", "I asked you to add a cube yesterday"):
            with self.subTest(prompt=prompt):
                self.assertFalse(classify_forge_intent(prompt, self.summary)["applicable"])
        for prompt in ("Create a 3d model viewer HTML page", "Write code to add a sphere", "Add a project to GitHub",
                       "Continue", '"add a cube"', "Hello there", "```js\nadd a sphere\n```"):
            with self.subTest(prompt=prompt):
                self.assertEqual(classify_forge_intent(prompt, self.summary)["disposition"], "ordinary")
        for prompt in ("Can you add a cube?", "Please make it red", "Rename the selected mesh exactly to Dragon §§",
                       "Rotate the selected model", "Undo", "Add a blue box", "Add two spheres",
                       'Rename the selected mesh to "HTML Explain do not add"',
                       "Rename the selected mesh to Shoulder", "Rename the selected mesh to Explainable Cube"):
            self.assertEqual(classify_forge_intent(prompt, self.summary)["disposition"], "mutation", prompt)
        self.assertEqual(classify_forge_intent("What objects are in this scene?", self.summary)["disposition"], "read")

    def test_typed_mesh_contract_preserves_literal_requested_name(self):
        literal = "  §§ This is THE exact Text!  "
        ops = [{"op": "mesh.add", "kind": "box", "name": literal, "position": [0, 1.5, 2],
                "rotation": [0, 0, 0], "scale": [1, .5, 2], "material": "metal", "color": "#aBC123"},
               {"op": "mesh.set", "id": "mesh-1", "name": literal},
               {"op": "mesh.select", "id": "mesh-1"}, {"op": "mesh.duplicate", "id": "mesh-1"}]
        canonical = validate_operations(self.context, ops)
        self.assertEqual(canonical, ops)
        self.assertEqual(canonical[0]["name"], literal)
        canonical[0]["position"][0] = 2
        self.assertEqual(ops[0]["position"][0], 0)

    def test_server_shape_preconditions_and_native_bounds_reject(self):
        invalid = [[], [{"op": "eval", "script": "alert(1)"}], [{"op": "mesh.set", "id": "outside-id", "color": "#ff0000"}],
                   [{"op": "mesh.set", "id": "mesh-1", "kind": "sphere"}], [{"op": "mesh.set", "id": "mesh-1"}],
                   [{"op": "mesh.add", "kind": "loft"}], [{"op": "mesh.add", "kind": "box", "material": "glass"}],
                   [{"op": "mesh.add", "kind": "box", "position": [1, 2]}],
                   [{"op": "mesh.add", "kind": "box", "position": [True, 0, 0]}],
                   [{"op": "mesh.add", "kind": "box", "position": [float("nan"), 0, 0]}],
                   [{"op": "mesh.add", "kind": "box", "position": [10 ** 500, 0, 0]}],
                   [{"op": "mesh.add", "kind": "box", "position": [101, 0, 0]}],
                   [{"op": "mesh.add", "kind": "box", "scale": [.005, 1, 1]}],
                   [{"op": "mesh.add", "kind": "box", "color": "red"}],
                   [{"op": "mesh.add", "kind": "box", "name": ""}],
                   [{"op": "mesh.add", "kind": "box", "name": "bad\nname"}],
                   [{"op": "mesh.add", "kind": "box", "__proto__": {}}],
                   [{"op": "sceneactor.add", "prefab": "wall"}],
                   [{"op": "editor.redo"}], [{"op": "editor.undo"}, {"op": "mesh.select", "id": "mesh-1"}],
                   [{"op": "mesh.select", "id": "mesh-1"}] * 17]
        for operations in invalid:
            with self.subTest(operations=operations), self.assertRaises(ForgePlanError):
                validate_operations(self.context, operations)
        for field, value in (("epoch", True), ("projectId", "different"), ("mode", "play"), ("workspace", "unknown")):
            original = self.summary[field]
            self.summary[field] = value
            with self.subTest(field=field), self.assertRaises(ForgePlanError):
                validate_operations(self.context, [{"op": "mesh.select", "id": "mesh-1"}])
            self.summary[field] = original

    def test_sceneactor_contract_uses_current_actor_ids_only(self):
        self.summary.update(native_summary("scene"))
        valid = [{"op": "sceneactor.add", "prefab": "rock", "name": "Rock §§", "position": [1, 2, 3]},
                 {"op": "sceneactor.rename", "id": "actor-1", "name": "Exact name"},
                 {"op": "sceneactor.transform", "id": "actor-1", "scale": [1, 2, 1]},
                 {"op": "sceneactor.select", "id": "actor-1"}]
        self.assertEqual(validate_operations(self.context, valid), valid)
        with self.assertRaises(ForgePlanError):
            validate_operations(self.context, [{"op": "sceneactor.add", "prefab": "dragon"}])
        with self.assertRaises(ForgePlanError):
            validate_operations(self.context, [{"op": "sceneactor.transform", "id": "actor-1", "color": "#ff0000"}])

    def test_no_success_prose_before_native_receipt_and_stream_is_public(self):
        register = Mock(return_value=BATCH)
        wait = Mock(return_value={"batchId": BATCH, "status": "finished", "allSucceeded": True, "receipts": [{"ok": True}]})
        infer = Mock(return_value=(json.dumps({"disposition": "apply", "operations": [{"op": "mesh.add", "kind": "box"}]}), {"finishReason": "stop"}))
        iterator = generate_events({"prompt": "Add a cube"}, self.context, register, wait, infer)
        self.assertEqual(next(iterator)["type"], "STATUS")
        ready = next(iterator)
        self.assertEqual(ready, {"type": "FORGE_BATCH_READY", "batchId": BATCH, **self.context.public_binding()})
        register.assert_called_once()
        wait.assert_not_called()
        events = list(iterator)
        self.assertEqual(events[-1]["forgeStatus"], "APPLIED")
        self.assertIn("confirmed 1", events[0]["text"])
        private = ("private-session-key", "private-owner", "private-generation-key", "hostToken", "receiptNonce")
        for value in private:
            self.assertNotIn(value, json.dumps([ready, *events]))
            self.assertNotIn(value, json.dumps(infer.call_args.args[0]))

    def test_stop_required_and_malformed_model_plan_never_registers(self):
        for finish in ("length", None, "error"):
            events = self.run_events(finish=finish)
            self.register.assert_not_called()
            self.assertEqual(events[-1]["type"], "FAILED")
            self.assertEqual(events[-1]["code"], "FORGE_PLAN_INCOMPLETE_GENERATION")
        for text in ('{}', '[]', '```json\n{}\n```', '{"disposition":"apply","disposition":"clarify","operations":[]}',
                     '{"disposition":"apply","operations":[],"trusted":true}',
                     '{"disposition":"apply","operations":[NaN]}'):
            with self.subTest(text=text), self.assertRaises(ForgePlanError):
                decode_plan(text, {"finishReason": "stop"})

    def test_model_abstention_has_no_mutation_and_is_not_applied(self):
        events = self.run_events(plan={"disposition": "clarify", "operations": [], "question": "Which mesh should I rename?"})
        self.register.assert_not_called()
        self.wait.assert_not_called()
        self.assertEqual(events[-1]["forgeStatus"], "CLARIFICATION")
        self.assertEqual(events[-2]["text"], "Which mesh should I rename?")

    def test_stale_authority_during_model_inference_prevents_registration(self):
        def model(messages, budget):
            self.live = False
            return json.dumps({"disposition": "apply", "operations": [{"op": "mesh.add", "kind": "box"}]}), {"finishReason": "stop"}
        events = self.run_events(infer=model)
        self.register.assert_not_called()
        self.assertEqual(events[-1]["type"], "FAILED")
        self.assertNotIn("APPLIED", json.dumps(events))

    def test_public_payload_cannot_supply_native_plan_or_auth(self):
        events = self.run_events(prompt="Hello", extra={"trusted": True, "inForge": True,
                                "forgePlan": {"operations": [{"op": "mesh.remove", "id": "mesh-1"}]}})
        self.infer.assert_not_called()
        self.register.assert_not_called()
        self.assertEqual(events[-1]["code"], "FORGE_NO_CURRENT_NATIVE_EDIT")
        with self.assertRaises(HTTPException):
            validate_operations({"trusted": True, **self.context.public_binding()}, [{"op": "editor.undo"}])

    def test_model_cannot_introduce_unrequested_delete_history_or_duplicate(self):
        for operation in ({"op": "mesh.remove", "id": "mesh-1"}, {"op": "mesh.duplicate", "id": "mesh-1"},
                          {"op": "editor.undo"}):
            events = self.run_events(operations=[operation], prompt='Add a blue box named "delete undo duplicate"')
            self.register.assert_not_called()
            self.assertEqual(events[-1]["code"], "FORGE_UNREQUESTED_NATIVE_ACTION")

    def test_timeouts_cancellations_and_mismatched_receipts_never_complete(self):
        for result in ({"batchId": BATCH, "status": "timeout", "receipts": []},
                       {"batchId": BATCH, "status": "cancelled", "receipts": []},
                       {"batchId": "d" * 32, "status": "finished", "allSucceeded": True, "receipts": [{"ok": True}]},
                       {"batchId": BATCH, "status": "finished", "allSucceeded": True, "receipts": []},
                       {"batchId": BATCH, "status": "finished", "allSucceeded": True, "receipts": [{"ok": "yes"}]},
                       {"batchId": BATCH, "status": "finished", "allSucceeded": False, "receipts": [{"ok": True}]}):
            with self.subTest(result=result):
                events = self.run_events(result=result)
                self.assertFalse(any(event["type"] == "COMPLETED" for event in events))
                self.assertEqual(events[-1]["type"], "FAILED")

    def test_partial_success_and_failed_operations_are_truthful(self):
        operations = [{"op": "mesh.set", "id": "mesh-1", "name": "One"}, {"op": "mesh.select", "id": "mesh-1"}]
        events = self.run_events(operations=operations, result={"batchId": BATCH, "status": "finished", "allSucceeded": False,
                                      "receipts": [{"ok": True}, {"ok": False, "error": "private exception text"}]})
        self.assertEqual(events[-1]["forgeStatus"], "PARTIAL")
        self.assertIn("1 of 2", events[-2]["text"])
        self.assertNotIn("private exception", json.dumps(events))
        self.assertFalse(any(event["type"] == "COMPLETED" for event in events))
        events = self.run_events(result={"batchId": BATCH, "status": "finished", "allSucceeded": False, "receipts": [{"ok": False}]})
        self.assertEqual(events[-1]["forgeStatus"], "FAILED")

    def test_readonly_context_is_bounded_and_does_not_generate_or_register(self):
        self.summary["meshes"][0]["name"] = "[inject](https://example.invalid) <script>"
        self.summary["totalMeshes"] = 80
        events = self.run_events(prompt="Show me the selected mesh")
        self.infer.assert_not_called()
        self.register.assert_not_called()
        self.assertEqual(events[-1]["forgeStatus"], "INSPECTED")
        self.assertIn("80 Model Atelier meshes", events[0]["text"])
        self.assertNotIn("<script>", events[0]["text"])
        self.assertIn("bounded metadata", events[0]["text"])

    def test_create_project_uses_advertised_starter_and_literal_name_only(self):
        self.summary["starters"] = [{"id": "blank-scene", "name": "Blank scene", "kind": "sandbox", "workspace": "scene"}]
        name = "  §§ My exact PROJECT!  "
        operation = {"op": "project.create", "starterId": "blank-scene", "name": name}
        self.assertEqual(validate_operations(self.context, [operation]), [operation])
        receipt = {"op": "project.create", "ok": True, "projectId": "e" * 32, "name": name, "starterId": "blank-scene"}
        events = self.run_events(operations=[operation], prompt='Create a new blank scene project called "' + name + '"',
                                 result={"batchId": BATCH, "status": "finished", "allSucceeded": True, "receipts": [receipt]})
        self.assertEqual(events[-1]["forgeStatus"], "APPLIED")
        self.assertIn("bundled starter is preserved", events[-2]["text"])
        self.assertIn("My exact PROJECT\\!", events[-2]["text"])
        self.assertEqual(self.register.call_args.args[1][0]["name"], name)
        for invalid in ([{**operation, "starterId": "unknown"}], [operation, {"op": "mesh.add", "kind": "box"}],
                        [{**operation, "name": ""}], [{**operation, "overwrite": True}]):
            with self.subTest(invalid=invalid), self.assertRaises(ForgePlanError):
                validate_operations(self.context, invalid)
        self.infer.assert_not_called()
        with self.assertRaises(ForgePlanError) as error:
            _validate_requested_actions('Create a project from the blank scene starter called "' + name + '"', [{**operation, "name": "Wrong spelling"}])
        self.assertEqual(error.exception.code, "FORGE_PROJECT_LITERAL_NAME_MISMATCH")

    def test_complete_explicit_creation_resolves_exact_catalog_and_literal_without_model(self):
        self.summary["starters"] = [{"id": "blank-scene", "name": "Blank Scene"}, {"id": "blank-model", "name": "Blank Model"}]
        name = "  My Starter §§!  "
        operation = {"op": "project.create", "starterId": "blank-scene", "name": name}
        for prompt in ('Create a new project from the Blank Scene starter named exactly "' + name + '".',
                       'Create a new blank-scene project called "' + name + '"'):
            self.assertEqual(explicit_project_plan(prompt, self.summary), {"disposition": "apply", "operations": [operation]})
        for prompt in ('Create a new project called "blank-scene"', 'Create a new project from an unavailable starter called "Desk"',
                       'Create a new project from Blank Scene or Blank Model named "Desk"',
                       'Create a Blank Scene project called "Desk" then add a cube',
                       'Create a Blank Scene project called "Desk", add a cube',
                       'Create a Blank Scene project called "Desk" with two boxes',
                       'Create a Blank Scene project with two boxes called "Desk"',
                       'Create a Blank Scene project', 'Explain creating a Blank Scene project called "Desk"',
                       'Create a cube in my project called "blank-scene"'):
            with self.subTest(prompt=prompt):
                self.assertIsNone(explicit_project_plan(prompt, self.summary))

    def test_project_request_does_not_fall_back_to_mesh_or_reuse_old_host(self):
        events = self.run_events(prompt='Create a new project called "Desk"')
        self.infer.assert_not_called()
        self.register.assert_not_called()
        self.assertEqual(events[-1]["code"], "FORGE_PROJECT_STARTER_UNAVAILABLE")
        self.summary["starters"] = [{"id": "model-atelier", "name": "Festival Armor"}]
        events = self.run_events(operations=[{"op": "mesh.add", "kind": "box"}],
                                 prompt='Create a new blank model project called "Desk"')
        self.register.assert_not_called()
        self.assertEqual(events[-1]["code"], "FORGE_UNREQUESTED_NATIVE_ACTION")

    def test_project_creation_relation_excludes_continuing_edits_and_documents(self):
        for prompt in ("Make a blue box in my project", "Create a wall in the project", "Build a pedestal in our project",
                       "Make this project better", "Set up the selected object in this project", "Create a project report",
                       "Create a project context document", "Create a project summary", "Build a project archive",
                       "Start working on my project", 'Rename the mesh to "create a project"'):
            with self.subTest(prompt=prompt):
                self.assertFalse(requests_new_project(prompt))
        for prompt in ('Create a new project named "Desk"', 'Make a blank model project called "Desk"',
                       'Start a Sheep Tag project called "Desk"', 'Set up a new scene project named "Desk"',
                       'Start from the Sheep Tag starter'):
            self.assertTrue(requests_new_project(prompt), prompt)
        for prompt in ("Make a blue box in my project", "Create a wall in the project", "Build a pedestal in our project"):
            self.assertEqual(classify_forge_intent(prompt, self.summary)["disposition"], "mutation")
        self.summary["starters"] = [{"id": "blank-model"}]
        events = self.run_events(operations=[{"op": "project.create", "starterId": "blank-model", "name": "Desk"}],
                                 prompt="Add a box in this project")
        self.register.assert_not_called()
        self.assertEqual(events[-1]["code"], "FORGE_UNREQUESTED_NATIVE_ACTION")

    def test_project_creation_requires_real_identity_receipt(self):
        self.summary["starters"] = [{"id": "blank-model"}]
        operation = {"op": "project.create", "starterId": "blank-model", "name": "Desk"}
        for receipt in ({"ok": True}, {"op": "project.create", "ok": True, "projectId": PROJECT,
                                      "name": "Desk", "starterId": "blank-model"}):
            events = self.run_events(operations=[operation], prompt='Start a blank model project called "Desk"',
                                     result={"batchId": BATCH, "status": "finished", "allSucceeded": True, "receipts": [receipt]})
            self.assertEqual(events[-1]["code"], "FORGE_PROJECT_RECEIPT_INVALID")

    def test_project_inspection_uses_actual_current_context_without_inference(self):
        self.summary.update(project={"name": "Desk §§", "kind": "model-atelier", "template": "blank-model", "sourceStarterId": "blank-model"},
                            dirty=True, activeLevel={"id": "level-1", "name": "Desk level"},
                            starters=[{"id": "blank-model", "name": "Blank Model"}])
        for prompt in ("What project is open?", "List the available starters", "What workspace am I in?"):
            self.assertEqual(classify_forge_intent(prompt, self.summary)["disposition"], "read")
            events = self.run_events(prompt=prompt)
            self.infer.assert_not_called()
            self.register.assert_not_called()
            self.assertIn("Desk §§", events[0]["text"])
            self.assertIn("Blank Model", events[0]["text"])
            self.assertIn("Desk level", events[0]["text"])


class RealSealTest(unittest.TestCase):
    def test_unsealed_or_dictionary_context_rejected_before_model_or_redis(self):
        fake = forge_embed.AuthorizedForgeContext("c" * 32, "thread", "gen", PROJECT, native_summary(),
                                                 "secret", "owner", "generation", "hash", object())
        for context in ({"trusted": True}, fake):
            inference, register = Mock(), Mock()
            with patch.object(forge_embed, "_live_lease") as backend:
                events = list(generate_events({"prompt": "Add a cube"}, context, register_batch=register, generate_plan=inference))
            backend.assert_not_called()
            inference.assert_not_called()
            register.assert_not_called()
            self.assertEqual(events[-1]["type"], "FAILED")


if __name__ == "__main__":
    unittest.main()
