#!/usr/bin/env python3
"""Build and measure §E v11.484 native Ring Detail + group transforms.

The existing 460-patch Sorting Hat source is preserved; append exactly one
UV-safe Ring Detail patch. Source bytes/SHA come only from the real builder.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/"source-manifest.json"
m=json.loads(manifest_path.read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.484",m["name"]
assert m["finalArtifact"]=="swyrl_engine_v11_484.html"
assert len(m["patches"])==461 and m["patches"][-2:]==[
 "patches/v11_483_sorting_hat_starter.py","patches/v11_484_ring_detail_transforms.py"]
for source in (
 "runtime/model_ring_detail_kernel_v11_483.js",
 "runtime/model_ring_detail_studio_v11_483.js",
 "runtime/model_ring_detail_studio_v11_483.css",
 "patches/v11_484_ring_detail_transforms.py",
 "runtime/sorting_hat_starter_v11_483.js",
 "scenes/model-atelier-sorting-hat.swyrl.json"):
 assert (ROOT/source).is_file(),source
for file in (
 "runtime/model_ring_detail_kernel_v11_483.js",
 "runtime/model_ring_detail_studio_v11_483.js",
 "runtime/sorting_hat_starter_v11_483.js"):
 subprocess.run(["node","--check",str(ROOT/file)],check=True)
subprocess.run(["node",str(ROOT/"tests/model_ring_detail_transforms_v11_483.mjs")],check=True)
subprocess.run([sys.executable,str(ROOT/"tests/sorting_hat_scene_v11_483.py")],check=True)
m["finalBytes"]=None;m["finalSha256"]=None
manifest_path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n","utf8")
out=ROOT/"_release_v11_484_candidate"
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
data=(out/"index.html").read_bytes()
assert data==(out/"modeler.html").read_bytes()
assert b"SE483_RING_DETAIL_STUDIO_END" in data
assert b"SE483_SORTING_HAT_END" in data
assert b"SE483_RING_DETAIL_KERNEL_END" in data
m["finalBytes"]=len(data)
m["finalSha256"]=hashlib.sha256(data).hexdigest()
manifest_path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+"\n","utf8")
subprocess.run([sys.executable,str(ROOT/"scripts/verify_v11_484_release.py"),
 "--output",str(ROOT/"_release_v11_484_verified")],check=True)
print("SE484_MEASURED_RECEIPT="+json.dumps({
 "version":m["name"],"bytes":m["finalBytes"],
 "sha256":m["finalSha256"],"patches":len(m["patches"])
},sort_keys=True),flush=True)
