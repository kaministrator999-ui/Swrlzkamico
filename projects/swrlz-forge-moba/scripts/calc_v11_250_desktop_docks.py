#!/usr/bin/env python3
"""Measure final §E v11.250 desktop/VR dock and shader candidate. No browser suite."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert m["name"]=="§wyrl§ Engine v11.250"
assert len(m["patches"])==281 and m["patches"][-1]=="patches/v11_250_particle_desktop_docks.py"
raw=gzip.decompress(base64.b64decode("".join((ROOT/p).read_text("utf8").strip() for p in m["chunks"])))
assert len(raw)==m["baseBytes"] and hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for p in m["patches"]:html=load_patch(ROOT/p)(html)
for key in ("SWYRL_ENGINE_DEPLOY_MARKER: V11_250_DESKTOP_DOCKS",
 "se250DesktopDocksStyle","SWYRL_ENGINE_PARTICLE_DOCKS_250",
 "se250Handle-left","se250LayoutMode","ShaderMaterial",
 "vRibbonUV","se250GroupStart"):
 assert key in html,key
assert html.count("renderer.setAnimationLoop(tick);")==1
data=html.encode("utf8")
print(json.dumps({"version":"v11.250","patches":len(m["patches"]),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
