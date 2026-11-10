"""Offline image-caption grounding regression cases (no model download).

The formatter is an evidence-bound display transform, not a second vision model.
It should omit narrow unsupported claims without inventing replacement content.
"""
from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "hf_space" / "model_router.py"


def load_formatters():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    names = {
        "_conflicting_staff_handedness",
        "_omit_unverifiable_turnaround_claims",
        "_format_direct_vision_report",
    }
    selected = [
        item for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name in names
    ]
    assert len(selected) == len(names)
    scope = {"re": re}
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])),
                 str(SOURCE), "exec"), scope)
    return scope["_omit_unverifiable_turnaround_claims"], scope["_format_direct_vision_report"]


class MultiViewClaimRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard, cls.format = load_formatters()

    def test_current_l2_false_armor_without_losing_real_design(self):
        raw = (
            "Subject and views: A chibi mage shown from front, left side, "
            "right side, back, and top views.\n"
            "Geometry and layers: The hooded robe has a segmented armored "
            "torso visible in the top view. The back view displays crescent "
            "moon, star, and swirl motifs on the cloak’s hem, while the "
            "front view shows a glowing crystal staff.\n"
            "Materials and markings: Gold embroidery, purple cloth, and "
            "brown boots with fur cuffs."
        )
        result = self.format(raw)
        self.assertNotIn("armored torso", result)
        self.assertNotIn("cloak’s hem", result)
        self.assertIn("crescent moon, star, and swirl motifs", result)
        self.assertIn("glowing crystal staff", result)
        self.assertIn("Gold embroidery", result)

    def test_genuine_front_armor_and_single_hem_emblem_survive(self):
        raw = (
            "The front view shows clearly visible plated armor on the chest. "
            "The back view includes a star motif on the robe hem. "
            "The top view shows the hood edge."
        )
        result = self.guard(raw)
        self.assertIn("clearly visible plated armor", result)
        self.assertIn("star motif on the robe hem", result)
        self.assertIn("hood edge", result)

    def test_no_top_view_does_not_remove_described_armor(self):
        text = "The hooded figure wears an armored torso plate in the front view."
        self.assertIn("armored torso plate", self.guard(text))


if __name__ == "__main__":
    unittest.main()
