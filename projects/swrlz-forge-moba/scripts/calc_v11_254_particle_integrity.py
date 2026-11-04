#!/usr/bin/env python3
"""Remeasure exact v11.254 source after final manifest sealing."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
p="patches/v11_254_particle_dock_preview_camera.py"
patches=m["patches"] if m["patches"][-1]==p else m["patches"]+[p]
assert len(patches)==285 and patches[-1]==p
raw=gzip.decompress(base64.b64decode("".join(
 (ROOT/n).read_text("utf8").strip() for n in m["chunks"])))
assert hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for path in patches:html=load_patch(ROOT/path)(html)
for required in (
 "SWYRL_ENGINE_DEPLOY_MARKER: V11_254_PARTICLE_DOCK_PREVIEW_CAMERA",
 "window.SWYRL_ENGINE_PARTICLE_DOCKS_250?.init?.();",
 "se254ParticleDockHotfix",
 "if(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())return;",
 "const active=stageActive?!!se223State.preview:",
 "if(state.active)frame();return true;",
 "zoomDistance:state.distance",
 "window.SWYRL_ENGINE_STRESS_TEST_252",
 "window.SWYRL_ENGINE_PARTICLE_CURVES_251",
 "seReleaseNotesClose"):
 assert required in html,required
assert html.count("renderer.setAnimationLoop(tick);")==1
data=html.encode("utf8")
print(json.dumps({"version":"v11.254","patches":len(patches),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
