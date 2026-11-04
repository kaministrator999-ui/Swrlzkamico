#!/usr/bin/env python3
"""Focused §E v11.251 validation: assembled source and original one-renderer invariants."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.251",m["name"]
assert len(m["patches"])==282 and m["patches"][-1]=="patches/v11_251_unified_studios_galaxy_curves.py"
raw=gzip.decompress(base64.b64decode("".join(
 (ROOT/p).read_text("utf8").strip() for p in m["chunks"])))
assert len(raw)==m["baseBytes"] and hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for p in m["patches"]:
 html=load_patch(ROOT/p)(html)
for k in (
 "SWYRL_ENGINE_DEPLOY_MARKER: V11_251_UNIFIED_GALAXY_CURVES",
 "se251UnifiedStudiosStyle",
 "SWYRL_ENGINE_PARTICLE_CURVE_RUNTIME_251",
 "SWYRL_ENGINE_PARTICLE_CURVES_251",
 "SWYRL_ENGINE_PARAMETER_TIMELINE_251",
 "SWYRL_ENGINE_SHARED_WORKSTATIONS_251",
 "SWYRL_ENGINE_NEBULA_251",
 "SWYRL_ENGINE_NEBULA_SETTINGS_251",
 "se251CurveGraph","se251ModelLibrary","se251MaterialLibrary"
):
 assert k in html,k
assert html.count("renderer.setAnimationLoop(tick);")==1
data=html.encode("utf8")
print(json.dumps({
 "version":"v11.251","patches":len(m["patches"]),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
