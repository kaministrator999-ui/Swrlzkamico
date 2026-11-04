#!/usr/bin/env python3
"""Compute v11.252 exact artifact receipt after native-closure anchor repair."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
patch="patches/v11_252_stress_diagnostics.py"
if patch in m["patches"]:
 patches=m["patches"]
else:
 assert m["name"]=="§wyrl§ Engine v11.251",m["name"]
 assert len(m["patches"])==282,m["patches"][-1]
 patches=m["patches"]+[patch]
assert len(patches)==283 and patches[-1]==patch
raw=gzip.decompress(base64.b64decode("".join((ROOT/p).read_text("utf8").strip() for p in m["chunks"])))
assert len(raw)==m["baseBytes"] and hashlib.sha256(raw).hexdigest()==m["baseSha256"]
html=raw.decode("utf8")
for name in patches:
 html=load_patch(ROOT/name)(html)
for k in ("SWYRL_ENGINE_DEPLOY_MARKER: V11_252_STRESS_DIAGNOSTICS",
 "window.SWYRL_ENGINE_MODEL_STRESS_252",
 "window.SWYRL_ENGINE_STRESS_TEST_252",
 "se252StressDiagnosticsStyle",
 'id="se252-model"',
 'id="se252-particles"'):
 if k in ('id="se252-model"','id="se252-particles"'):
  continue # dynamic DOM mount, not static HTML
 assert k in html,k
assert html.count("renderer.setAnimationLoop(tick);")==1
data=html.encode("utf8")
print(json.dumps({"version":"v11.252","patches":len(patches),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleEngineRenderer":True},indent=2))
