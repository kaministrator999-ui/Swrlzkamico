#!/usr/bin/env python3
"""Build the 1-mesh Sorting Hat, validate it, seal v11.485 and static delivery.

The original v11.483 49-part hat is separately preserved. The tested scene
is committed alongside the source manifest by the releasing workflow, not
mutated in the user's saved projects. No hash is fabricated.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/"source-manifest.json"
m=json.loads(manifest_path.read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.484",m["name"]
assert m["finalArtifact"]=="swyrl_engine_v11_484.html"
assert len(m["patches"])==461
assert m["patches"][-1]=="patches/v11_484_ring_detail_transforms.py"
assert isinstance(m["finalSha256"],str) and len(m["finalSha256"])==64
for p in ("scenes/model-atelier-sorting-hat-v11-483-assembly.swyrl.json",
          "authoring/sorting_hat_single_surface_v11_485.py",
          "patches/v11_485_one_cloth_sorting_hat.py",
          "tests/sorting_hat_single_mesh_v11_485.py"):
    assert (ROOT/p).is_file(),p

# Bake the sculpt and its reusable color-and-shadow UV texture using the
# actual topology and native paint size constraints.
subprocess.run([sys.executable,str(ROOT/"authoring/sorting_hat_single_surface_v11_485.py")],check=True)
subprocess.run([sys.executable,str(ROOT/"tests/sorting_hat_single_mesh_v11_485.py")],check=True)
subprocess.run(["node","--check",str(ROOT/"runtime/sorting_hat_starter_v11_483.js")],check=True)
subprocess.run(["node",str(ROOT/"tests/model_ring_detail_transforms_v11_483.mjs")],check=True)

m["name"]="§wyrl§ Engine v11.485"
m["finalArtifact"]="swyrl_engine_v11_485.html"
m["patches"].append("patches/v11_485_one_cloth_sorting_hat.py")
m["finalBytes"]=None;m["finalSha256"]=None
manifest_path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n","utf8")
with tempfile.TemporaryDirectory(prefix="sorting-hat-485-") as folder:
    build=Path(folder)/"package"
    subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(build)],check=True)
    raw=(build/"index.html").read_bytes()
    assert raw==(build/"modeler.html").read_bytes()
    assert b"V11_485_ONE_CLOTH_SORTING_HAT" in raw
    assert b"parts.length!==1||!Array.isArray(scene?.scene?.actors)" in raw
    m["finalBytes"]=len(raw)
    m["finalSha256"]=hashlib.sha256(raw).hexdigest()
    manifest_path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n","utf8")

    subprocess.run([sys.executable,str(ROOT/"scripts/verify_v11_485_release.py"),"--output",str(build)],check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/package_static_delivery_v11_485.py"),"--output",str(build)],check=True)
    subprocess.run(["node","--check",str(build/"swrlz-engine-v11.485.js")],check=True)
    receipt=json.loads((build/"SOURCE.json").read_text("utf8"))
    assert receipt["sourceVersion"]==m["name"]
    assert receipt["finalSha256"]==m["finalSha256"]
    assert receipt["staticDelivery"]["verifiedSourceSha256"]==m["finalSha256"]
    assert receipt["assets"]["scenes/model-atelier-sorting-hat.swyrl.json"]["bytes"]>200000
    print(json.dumps({"status":"ONE_CLOTH_RELEASE_SEALED",
                     "sha256":m["finalSha256"],"bytes":m["finalBytes"],
                     "patches":len(m["patches"]), "assets":len(receipt["assets"]),
                     "sceneBytes":receipt["assets"]["scenes/model-atelier-sorting-hat.swyrl.json"]["bytes"],
                     "module":receipt["staticDelivery"]["module"]}),flush=True)
