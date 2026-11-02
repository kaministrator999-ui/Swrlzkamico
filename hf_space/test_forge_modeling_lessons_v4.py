#!/usr/bin/env python3
"""v4 targeted source-level §C modeler lessons. No model inference or native editing."""
import unittest
from forge_modeling_lessons import select_modeling_lesson
from online_tools import classify_online_request

CTX={"workspace":"model-atelier"}

class ForgeModelingLessonsV4(unittest.TestCase):
    def test_wolf_armature_and_release_caveat(self):
        text=select_modeling_lesson("Teach me the §E Astra wolf rig")
        for part in ("14-bone", "FOUR", "SkinnedMesh", "sealed manifest", "NO"):
            self.assertIn(part,text,part)
        self.assertLessEqual(len(text),1150)

    def test_wolf_clip_library_and_bounds(self):
        text=select_modeling_lesson("Explain the §E wolf animation clips")
        for part in ("Ten clip", "13 sampled keys", "64 keys", "Sheep Tag", "NOT the high-detail"):
            self.assertIn(part,text)

    def test_particle_is_game_scene_not_model_atelier(self):
        text=select_modeling_lesson("How does §E Particle Studio work?")
        for part in ("v11.224", "GAME EDITOR", "12 emitters", "96 motes", "576 total", "JSON"):
            self.assertIn(part,text)
        self.assertIn("NO native particle.create",text)

    def test_particle_gameplay_distinction(self):
        text=select_modeling_lesson("§E create sparkles for a sheep building")
        self.assertIn("legacy Sheep Tag",text.lower().replace("legacy sheep tag","legacy Sheep Tag") if "legacy" in text.lower() else text)
        self.assertIn("not",text.lower())

    def test_sheep_preview_is_reversible(self):
        text=select_modeling_lesson("In §E Model Atelier animate the Clover sheep")
        self.assertIn("Clover Model Atelier",text)
        self.assertIn("reversible part-transform",text)
        self.assertIn("not",text.lower())

    def test_trusted_source_vs_external_docs(self):
        text=select_modeling_lesson("Search the web for §E wolf AnimationMixer reference")
        self.assertIn("AnimationClip/AnimationMixer",text)
        self.assertIn("custom Astra wolf",text)
        self.assertIn("untrusted",text)
        result=classify_online_request("Search the web for three.js AnimationMixer official docs",[],{},None)
        self.assertTrue(result["requested"])
        self.assertEqual(result["kind"],"search")

    def test_negative_game_and_social_no_context(self):
        for query in ("What's my sheep food budget in §E Sheep Tag?",
                      "Tell me a joke about a wolf", "Hello friend"):
            self.assertEqual(select_modeling_lesson(query),"")

    def test_fresh_editor_permission_still_required(self):
        for query in ("§E create a particle emitter now", "§E Wolf rig, save a keyframe"):
            text=select_modeling_lesson(query,CTX,role="planner")
            self.assertIn("disposition=clarify",text)
            self.assertLessEqual(len(text),1150)

    def test_earlier_v3_topics_still_present(self):
        text=select_modeling_lesson("Retarget WebXR Quest hands to §E")
        self.assertIn("25 XRHand",text)
        text=select_modeling_lesson("§E Wave gesture")
        self.assertIn("2.20 seconds",text)

if __name__=="__main__":
    unittest.main(verbosity=2)
