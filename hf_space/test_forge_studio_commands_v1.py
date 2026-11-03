#!/usr/bin/env python3
"""Focused offline Studio Commands v1 checks; no hosted model or Quest test."""
import math
import unittest

from forge_studio_commands_v1 import (
    SPEC, MATERIAL_PRESETS, PARTICLE_PRESETS, StudioCommandError,
    validate_studio_operation as check,
)
from forge_design_preview_v1 import should_preview
from forge_chat_actions import native_plan_response_format, operation_contract, explicit_particle_create_plan


def snapshot(studio="materials", kind="hand"):
    return {
        "workspace": "model-atelier" if studio == "modeler" else "scene",
        "studio": studio,
        "mode": "edit",
        "actors": [{"id": "actor-1", "name": "Sheep house"}],
        "studioCommands": {
            "schema": SPEC,
            "materials": {"available": studio == "materials", "items": [{"id": "mat-1"}],
                          "presets": sorted(MATERIAL_PRESETS)},
            "particles": {"available": studio == "particles", "items": [{"id": "fx-1"}],
                          "presets": sorted(PARTICLE_PRESETS)},
            "rig": {"available": studio == "modeler", "kind": kind,
                    "bones": (["wrist"] + ["b" + str(i) for i in range(16)] if kind == "hand"
                              else ["wolf_root"] + ["b" + str(i) for i in range(13)]),
                    "duration": 2.5, "keyCount": 2, "selectedClip": "walk",
                    "clips": ["walk", "run"]},
        },
    }


class StudioCommandTests(unittest.TestCase):
    def assert_denied(self, summary, op):
        with self.assertRaises(StudioCommandError):
            check(summary, op, 1)

    def test_explicit_host_version_gate(self):
        snap = snapshot()
        snap.pop("studioCommands")
        self.assert_denied(snap, {"op": "material.create", "preset": "metal"})

    def test_material_allowlist_and_ids(self):
        s = snapshot()
        self.assertEqual(check(s, {"op": "material.create", "preset": "wood"}, 1)["preset"], "wood")
        self.assertEqual(check(s, {"op": "material.set", "id": "mat-1", "metalness": 0.2}, 1)["metalness"], .2)
        self.assertEqual(check(s, {"op": "material.assign", "id": "mat-1", "actorId": "actor-1"}, 1)["actorId"], "actor-1")
        self.assert_denied(s, {"op": "material.assign", "id": "mat-1", "actorId": "invented"})
        self.assert_denied(s, {"op": "material.set", "id": "invented", "metalness": .2})
        self.assert_denied(s, {"op": "material.set", "id": "mat-1", "glow": 99})
        self.assert_denied(s, {"op": "material.set", "id": "mat-1", "roughness": float("nan")})
        self.assert_denied(s, {"op": "material.set", "id": "mat-1"})
        with self.assertRaises(StudioCommandError):
            check(s, {"op": "material.create", "preset": "wood"}, 2)

    def test_particle_allowlist_bounds(self):
        s = snapshot("particles")
        self.assertEqual(check(s, {"op": "particle.create", "preset": "build"}, 1)["preset"], "build")
        self.assertEqual(check(s, {"op": "particle.set", "id": "fx-1", "rate": 30,
                                   "position": [1, 2, 3]}, 1)["rate"], 30)
        self.assert_denied(s, {"op": "particle.set", "id": "fx-1", "rate": 81})
        self.assert_denied(s, {"op": "particle.set", "id": "fx-1", "position": [1, float("inf"), 1]})
        self.assert_denied(s, {"op": "particle.create", "preset": "invented"})

    def test_single_particle_creation_needs_no_actor_or_position(self):
        s = snapshot("particles")
        phrases = [
            "Create one particle emitter using the Magic preset in the currently active §E Particle Studio.",
            "Create a standalone magic particle emitter in Particle Studio.",
            "Please add one magic emitter.",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertEqual(explicit_particle_create_plan(phrase, s),
                                 {"disposition": "apply", "operations": [
                                     {"op": "particle.create", "preset": "magic"}]})
        for phrase in [
            "Create a magic particle emitter next to Menu pine.",
            "Create a magic particle emitter attached to a sheep actor.",
            "Create a magic emitter at position X=2.",
            "Create a magic emitter and move it.",
            "Can you explain how to create a magic emitter?",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIsNone(explicit_particle_create_plan(phrase, s))
        self.assertIsNone(explicit_particle_create_plan(phrases[0], snapshot("materials")))
        s["studioCommands"]["particles"]["available"] = False
        self.assertIsNone(explicit_particle_create_plan(phrases[0], s))

    def test_rig_bone_clip_and_time(self):
        s = snapshot("modeler")
        self.assertEqual(check(s, {"op": "rig.pose", "boneId": "wrist",
                                   "rotation": [0.3, 0, 0]}, 1)["boneId"], "wrist")
        self.assertEqual(check(s, {"op": "rig.keyframe", "time": 1.2}, 1)["time"], 1.2)
        self.assert_denied(s, {"op": "rig.pose", "boneId": "ghost", "rotation": [0, 0, 0]})
        self.assert_denied(s, {"op": "rig.pose", "boneId": "wrist", "rotation": [3.0, 0, 0]})
        self.assert_denied(s, {"op": "rig.keyframe", "time": 3.1})
        self.assert_denied(s, {"op": "rig.keyframe", "time": 1.0, "clip": "walk"})
        wolf = snapshot("modeler", kind="wolf")
        self.assertEqual(check(wolf, {"op": "rig.keyframe", "time": 1.0, "clip": "walk"}, 1)["clip"], "walk")
        self.assert_denied(wolf, {"op": "rig.keyframe", "time": 1.0, "clip": "run"})

    def test_studio_switch_and_mode(self):
        self.assert_denied(snapshot("particles"), {"op": "material.create", "preset": "metal"})
        s = snapshot()
        s["mode"] = "play"
        self.assert_denied(s, {"op": "material.create", "preset": "metal"})

    def test_model_schema_and_compulsory_frozen_preview(self):
        fields = operation_contract()["operations"]
        for name in ("material.create", "material.set", "material.assign",
                     "particle.create", "particle.set", "rig.pose", "rig.keyframe"):
            self.assertIn(name, fields)
            self.assertTrue(should_preview("Apply in §e now: add a particle", [{"op": name}]))
        self.assertIn("schema", native_plan_response_format())


if __name__ == "__main__":
    unittest.main(verbosity=2)
