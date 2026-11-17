#!/usr/bin/env python3
"""Contract validation for the native editable §E Sorting Hat starter scene."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = json.loads((ROOT / "scenes/model-atelier-sorting-hat.swyrl.json").read_text("utf8"))
assert scene["project"]["kind"] == "model-atelier"
assert scene["project"]["canonicalId"] == "sorting-hat"
assert scene["project"]["template"] == "sorting-hat"
assert scene["scene"]["actors"]
model = scene["project"]["modelAtelier"]
assert model["schema"] == "swyrl-model-atelier-v1"
parts = model["parts"]
assert len(parts) == 49
seen = set()
total_vertices = total_triangles = 0
for part in parts:
    assert part["kind"] == "topologyMesh"
    assert part["id"] not in seen
    seen.add(part["id"])
    assert all(math.isfinite(x) for key in ("position", "rotation", "scale") for x in part[key])
    assert all(0.005 < x <= 20 for x in part["scale"])
    assert part["material"] in ("matte", "silk", "gloss", "metal", "emissive")
    geometry = part["topologyMesh"]
    vertices, uvs, triangles = (geometry[key] for key in ("positions", "uvs", "indices"))
    assert vertices and len(vertices) % 3 == 0
    assert len(uvs) == 2 * (len(vertices) // 3)
    assert triangles and len(triangles) % 3 == 0
    assert all(math.isfinite(x) and abs(x) < 100 for x in vertices)
    assert all(math.isfinite(x) and abs(x) < 20 for x in uvs)
    assert all(isinstance(i, int) and 0 <= i < len(vertices)//3 for i in triangles)
    total_vertices += len(vertices)//3
    total_triangles += len(triangles)//3
assert total_vertices == 7874, total_vertices
assert total_triangles == 13238, total_triangles
groups = model["meshGroups"]
assert len(groups) == 3
assert {i for group in groups for i in group["members"]} == seen
assert sum(len(group["members"]) for group in groups) == len(parts)
assert "face" in groups[1]["name"].lower()
assert {part["group"] for part in parts} >= {"Crown","Brim","Face folds","Seams","Patches","Stitches"}
print("SORTING_HAT_NATIVE_SCENE_PASS", {
    "parts":len(parts), "vertices":total_vertices,
    "triangles":total_triangles, "groups":len(groups),
    "editable":True, "nativeScene":True,
})
