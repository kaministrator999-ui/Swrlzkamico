#!/usr/bin/env python3
"""Focused §E v11.249 final candidate measurement after native panel state reset. No full browser suites."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.249"
assert len(m["patches"])==280
assert m["patches"][-1]=="patches/v11_249_particle_studio_workstation.py"
raw=gzip.decompress(base64.b64decode("".join((ROOT/p).read_text("utf8").strip() for p in m["chunks"])))
assert len(raw)==m["baseBytes"] and hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for p in m["patches"]:
    html=load_patch(ROOT/p)(html)
for key in (
 "SWYRL_ENGINE_DEPLOY_MARKER: V11_249_PARTICLE_WORKSTATION",
 "se249ParticleWorkstationStyle",
 "window.SWYRL_ENGINE_PARTICLE_UI_249",
 "window.SWYRL_ENGINE_RIBBONS_249",
 "vortexSpin","vortexPull","vortexGlow","vortexTilt",
 "se249Root","se249LayerRows","se249SelectedName"):
    assert key in html,key
assert html.count("renderer.setAnimationLoop(tick);")==1
out=html.encode("utf8")
print(json.dumps({"version":"v11.249","patches":len(m["patches"]),
  "finalBytes":len(out),"finalSha256":hashlib.sha256(out).hexdigest(),
  "singleRenderer":True},indent=2))
