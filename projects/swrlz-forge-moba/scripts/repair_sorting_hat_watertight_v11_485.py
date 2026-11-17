#!/usr/bin/env python3
"""Regenerate the single §E Sorting Hat as closed cloth, not a wrapped sheet.

Asset-only fix. Preserve published engine source, save schema, project structure,
UV coordinates and the painted PNG. The new native triangles close the rear UV
meridian with real non-degenerate geometry and softly blend the upper crown.
"""
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCENE=ROOT/"scenes/model-atelier-sorting-hat.swyrl.json"
MANIFEST=ROOT/"source-manifest.json"
manifest_before=MANIFEST.read_bytes()
m=json.loads(manifest_before)
assert m["name"]=="§wyrl§ Engine v11.485"
assert len(m["patches"])==462 and m["patches"][-1]=="patches/v11_485_one_cloth_sorting_hat.py"
original=json.loads(SCENE.read_text("utf8"))
original_parts=original["project"]["modelAtelier"]["parts"]
assert len(original_parts)==1 and original_parts[0]["kind"]=="topologyMesh"
original_part=original_parts[0]
original_mesh=original_part["topologyMesh"]
assert len(original_mesh["positions"])//3==7859
assert len(original_mesh["indices"])//3==15552

subprocess.run([sys.executable,str(ROOT/"authoring/sorting_hat_single_surface_v11_485.py")],check=True)
updated=json.loads(SCENE.read_text("utf8"))
new_parts=updated["project"]["modelAtelier"]["parts"]
assert len(new_parts)==1 and new_parts[0]["id"]==original_part["id"]
new_part=new_parts[0]
new_mesh=new_part["topologyMesh"]
assert new_part["uvPaintPNG"]==original_part["uvPaintPNG"],"Native paint changed unexpectedly"
assert new_mesh["uvs"]==original_mesh["uvs"],"Preserved UV atlas coordinates were shifted"
assert len(new_mesh["positions"])==len(original_mesh["positions"])
assert len(new_mesh["indices"])//3==15714,"Rear seam was not filled along all rings"
assert len(new_mesh["indices"])>len(original_mesh["indices"])
assert {k:v for k,v in updated.items() if k!="project"}=={
    k:v for k,v in original.items() if k!="project"}
assert {k:v for k,v in updated["project"].items() if k!="modelAtelier"}=={
    k:v for k,v in original["project"].items() if k!="modelAtelier"}
assert {k:v for k,v in new_part.items() if k!="topologyMesh"}=={
    k:v for k,v in original_part.items() if k!="topologyMesh"}
assert MANIFEST.read_bytes()==manifest_before,"Source integrity seal changed"

# No changes to the face or brim except the low-width repair around the old
# open rear meridian and sub-centimeter periodic wrinkle alignment. The
# connected 3D body must not be replaced with a primitive or multiple parts.
outer_rows=60
stride=97
nonseam_delta=0.
for row in range(outer_rows):
    for j in range(1,96):
        q=3*(row*stride+j)
        a=original_mesh["positions"][q:q+3]
        b=new_mesh["positions"][q:q+3]
        diff=math.dist(a,b)
        nonseam_delta=max(nonseam_delta,diff)
        if row>=8:
            assert diff<.14,("Unexpected sculpt or face deformation",row,j,diff)
assert nonseam_delta<.14

# This specifically catches the previous false positive: a single connected
# mesh could still have thousands of exposed edges along its open sheet seam.
subprocess.run([sys.executable,str(ROOT/"tests/sorting_hat_single_mesh_v11_485.py")],check=True)
with tempfile.TemporaryDirectory(prefix="se485-closed-hat-") as directory:
    out=Path(directory)/"package"
    subprocess.run([sys.executable,str(ROOT/"scripts/verify_v11_485_release.py"),
                    "--output",str(out)],check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/package_static_delivery_v11_485.py"),
                    "--output",str(out)],check=True)
    subprocess.run(["node","--check",str(out/"swrlz-engine-v11.485.js")],check=True)
    assert MANIFEST.read_bytes()==manifest_before
    receipt=json.loads((out/"SOURCE.json").read_text("utf8"))
    asset="scenes/model-atelier-sorting-hat.swyrl.json"
    encoded=SCENE.read_bytes()
    assert receipt["finalSha256"]==m["finalSha256"]
    assert receipt["assets"][asset]["sha256"]==hashlib.sha256(encoded).hexdigest()
    assert receipt["assets"][asset]["bytes"]==len(encoded)
    print(json.dumps({
        "status":"SE485_WATERTIGHT_HAT_PASS",
        "parts":1,
        "vertices":len(new_mesh["positions"])//3,
        "triangles":len(new_mesh["indices"])//3,
        "seamClosureFaces":162,
        "preserved":["native project","UV atlas","UV paint PNG","engine source seal",
                     "single-mesh editor","stored user projects"],
        "maxUntouchedColumnDelta":round(nonseam_delta,6),
        "assetSha256":hashlib.sha256(encoded).hexdigest(),
        "engineSha256":m["finalSha256"]
    }),flush=True)
