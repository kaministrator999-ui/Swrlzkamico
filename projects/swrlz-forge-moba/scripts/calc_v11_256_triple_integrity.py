#!/usr/bin/env python3
"""Measure final documented v11.256 full source with preserved AI scoring."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.256"
assert len(m["patches"])==287 and m["patches"][-1]=="patches/v11_256_galaxy_ai_xr_ray.py"
raw=gzip.decompress(base64.b64decode("".join((ROOT/n).read_text("utf8").strip() for n in m["chunks"])))
assert hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for name in m["patches"]:html=load_patch(ROOT/name)(html)
for label,needle in {
 "particle project continuity":"state.projectRebinds=(state.projectRebinds||0)+1",
 "particle stage recovery":"const stageActive=chamber?.frame?.()===true",
 "AI path-budgeted over frames":"se256AIBudget.used<se256AIBudget.perFrame",
 "XR real ray":"se193XRGameGround=function(record){",
 "no fake build aim":"se203GroundFromForwardRay=function(){return null;}",
 "VR menu cursor foreground":"beam.renderOrder=11100",
 "normal ray restored":"beam.renderOrder=9999",
 "XR ghost sky hide":"if(stUi.preview)stUi.preview.visible=false",
 "single WebGL owner":"renderer.setAnimationLoop(tick);",
 "particle curves":"window.SWYRL_ENGINE_PARTICLE_CURVE_RUNTIME_251",
 "stress controls":"window.SWYRL_ENGINE_STRESS_TEST_252",
 "new release":"SWYRL_ENGINE_DEPLOY_MARKER: V11_256_GALAXY_AI_XR_RAY"
}.items():
 assert needle in html,(label,needle)
assert html.count("renderer.setAnimationLoop(tick);")==1
data=html.encode("utf8")
print(json.dumps({"version":"v11.256","patches":len(m["patches"]),"finalBytes":len(data),
"finalSha256":hashlib.sha256(data).hexdigest(),"singleRenderer":True},indent=2))
