"""Offline unit checks for §C multi-studio context. No live model/host needed."""
import unittest
from forge_modeling_lessons import select_modeling_lesson as choose


class StudioCoachTests(unittest.TestCase):
    def test_irrelevant_and_ambiguous(self):
        for q in ("What's the weather today?", "Write a verse about fire",
                  "My hand hurts", "Explain texture mapping in Blender",
                  "Tell me a joke", "Work on my game"):
            self.assertEqual(choose(q), "", q)
        self.assertEqual(choose("Tell me a joke", {"workspace": "scene"}), "")
        self.assertEqual(choose("build a fence", {"workspace": "scene"}), "")

    def test_game_design(self):
        s = choose("Design a Sheep Tag level and GUI in §E")
        self.assertIn("Game Editor owns scene actors", s)
        self.assertIn("Show in Play", s)

    def test_material(self):
        s = choose("Use §E to create a PBR material and UV texture")
        self.assertIn("currentProject.materialStudio", s)
        self.assertIn("NOT individual Model Atelier parts", s)

    def test_particles(self):
        s = choose("§E: edit Particle Studio emitters and attach smoke")
        self.assertIn("currentProject.particleStudio", s)
        self.assertIn("world space", s)
        self.assertIn("No native §C particle.create", s)

    def test_animation(self):
        s = choose("Improve the wolf's animation clip in §E")
        self.assertIn("14-bone rig", s)
        self.assertIn("Clover", s)

    def test_rig(self):
        s = choose("Rig the skeleton in §E")
        self.assertIn("skin weights", s)
        self.assertIn("Quest hand", s)

    def test_cross_studio(self):
        s = choose("In §E, design a game with models, material textures, animations and particle effects")
        self.assertIn("scene/gameplay", s)
        self.assertIn("rig/clip", s)
        self.assertIn("native preview/save", s)

    def test_native_context_only_for_relevant_topic(self):
        self.assertIn("currentProject.materialStudio", choose("Edit material texture", {"workspace": "materials"}))
        self.assertEqual(choose("Edit material texture", {"workspace": "untrusted"}), "")

    def test_existing_modeler_lessons(self):
        cases = {
            "Brush sculpt the palm in §E": "sculptVertexEdits",
            "Group the armor meshes in §E": "non-destructive",
            "Map UV texture in §E": "UVs",
            "Fix the floating glove fingers in §E": "phalanges",
            "Export OBJ from §E Model Atelier": "triangulated",
        }
        for q, word in cases.items():
            s = choose(q)
            self.assertIn(word, s, q)
            self.assertIn("NOT tool access", s)
            self.assertIn("Never invent IDs", s)

    def test_bounded_and_planner_safe(self):
        for q in ("§E game design GUI", "§E material texture", "§E particle emitters",
                  "§E animation clips", "§E rig skeleton",
                  "§E model sculpt component",
                  "§E models materials animation particles game design"):
            s = choose(q, role="planner")
            self.assertLessEqual(len(s), 1150, q)
            self.assertIn("disposition=clarify", s, q)
            self.assertIn("no new operation types", s, q)
            self.assertNotIn("operation executed", s.lower(), q)


if __name__ == "__main__":
    unittest.main(verbosity=2)
