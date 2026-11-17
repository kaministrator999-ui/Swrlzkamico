#!/usr/bin/env python3
"""Asset-only §E v11.485 hotfix: smoother Sorting Hat tip, no new objects or engine patches.

Rebuild the existing model deterministically from its source generator, prove
that only the tip geometry changed, then verify the entire sealed engine and
asset package. No update to source-manifest's HTML hash is needed because the
HTML/JS build is unchanged and the new asset is separately checked by CI.
"""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCENE=ROOT/"scenes/model-atelier-sorting-hat.swyrl.json"
MANIFEST=ROOT/"source-manifest.json"
m=json.loads(MANIFEST.read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.485" and len(m["patches"])==462
assert m["patches"][-1]=="patches/v11_485_one_cloth_sorting_hat.py"
before_manifest=MANIFEST.read_bytes()
before=json.loads(SCENE.read_text("utf8"))
old=before["project"]["modelAtelier"]["parts"]
assert len(old)==1 and old[0]["kind"]=="topologyMesh"
before_mesh=old[0]["topologyMesh"]
old_paint=old[0]["uvPaintPNG"]
old_uv=before_mesh["uvs"]
old_faces=before_mesh["indices"]
old_xyz=before_mesh["positions"]

subprocess.run([sys.executable,str(ROOT/"authoring/sorting_hat_single_surface_v11_485.py")],check=True)
after=json.loads(SCENE.read_text("utf8"))
new=after["project"]["modelAtelier"]["parts"]
assert len(new)==1 and new[0]["id"]==old[0]["id"]
assert new[0]["uvPaintPNG"]==old_paint, "UV texture was changed by a tip-only fix"
new_mesh=new[0]["topologyMesh"]
assert new_mesh["uvs"]==old_uv, "UV layout was changed"
assert new_mesh["indices"]==old_faces, "Vertex connectivity changed"
assert len(new_mesh["positions"])==len(old_xyz)
stride=97
last_tip_xyz=8*stride*3
# The tip's eight rings and matching cap are the ONLY coordinates modified.
assert new_mesh["positions"][last_tip_xyz:-6]==old_xyz[last_tip_xyz:-6], "Face, brim or lining moved"
assert new_mesh["positions"][-3:]==old_xyz[-3:], "Interior tip cap moved"
assert new_mesh["positions"][:last_tip_xyz]!=old_xyz[:last_tip_xyz], "Tip did not change"
assert new_mesh["positions"][-6:-3]!=old_xyz[-6:-3], "Tip end not rounded at new location"
assert {key:value for key,value in new[0].items() if key!="topologyMesh"}=={
    key:value for key,value in old[0].items() if key!="topologyMesh"}
assert MANIFEST.read_bytes()==before_manifest, "Source seal unexpectedly changed"

subprocess.run([sys.executable,str(ROOT/"tests/sorting_hat_single_mesh_v11_485.py")],check=True)
with tempfile.TemporaryDirectory(prefix="se485-hat-tip-") as folder:
    output=Path(folder)/"package"
    subprocess.run([sys.executable,str(ROOT/"scripts/verify_v11_485_release.py"),"--output",str(output)],check=True)
    assert MANIFEST.read_bytes()==before_manifest, "HTML source manifest should remain sealed"
    receipt=json.loads((output/"SOURCE.json").read_text("utf8"))
    assert receipt["finalSha256"]==m["finalSha256"]
    relative="scenes/model-atelier-sorting-hat.swyrl.json"
    scene_data=SCENE.read_bytes()
    assert receipt["assets"][relative]["sha256"]==hashlib.sha256(scene_data).hexdigest()
    assert receipt["assets"][relative]["bytes"]==len(scene_data)
    print(json.dumps({"status":"SORTING_HAT_TIP_HOTFIX_PASS",
        "sourceVersion":m["name"],"sourceSha256":m["finalSha256"],
        "sceneSha256":hashlib.sha256(scene_data).hexdigest(),
        "parts":len(new),"vertices":len(new_mesh["positions"])//3,
        "triangles":len(new_mesh["indices"])//3,
        "modifiedGeometry":"tip ring vertices and exterior cap only",
        "unchanged":"all other coordinates, UVs, UV paint, triangle connectivity, project metadata, engine source"}),flush=True)
