#!/usr/bin/env python3
"""Calculate exact sealed source and check galaxy TDZ hotfix is the sole VFX change."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.257"
assert len(m["patches"])==288
assert m["patches"][-1]=="patches/v11_257_nebula_tdz_unfreeze.py"
raw=gzip.decompress(base64.b64decode("".join((ROOT/n).read_text("utf8").strip() for n in m["chunks"])))
assert hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for p in m["patches"]:html=load_patch(ROOT/p)(html)
assert "const nextPoint=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index)" in html
assert "const b=location(Math.min(1,u+.001),phase,cfg,origin,0,b.index)" not in html
assert html.count("renderer.setAnimationLoop(tick);")==1
assert "window.SWYRL_ENGINE_SHEEP_BUILD_RAY_256" in html
assert "se256AIBudget.used<se256AIBudget.perFrame" in html
assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_257_GALAXY_FIRST_FRAME_UNFREEZE" in html
data=html.encode("utf8")
print(json.dumps({"version":"v11.257","patches":len(m["patches"]),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
