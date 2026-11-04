#!/usr/bin/env python3
"""Measure sealed v11.255 viewport input release after manifest name and patch-list update."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
p="patches/v11_255_particle_viewport_ownership.py"
patches=m['patches'] if m['patches'][-1]==p else m['patches']+[p]
assert len(patches)==286 and patches[-1]==p
raw=gzip.decompress(base64.b64decode(''.join((ROOT/n).read_text('utf8').strip() for n in m['chunks'])))
assert hashlib.sha256(raw).hexdigest()==m['baseSha256']
html=raw.decode('utf8')
for name in patches:html=load_patch(ROOT/name)(html)
required=(
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_255_PARTICLE_VIEWPORT_OWNERSHIP',
 "!window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())orbit.update();",
 "se255BindViewportInput(viewing);",
 "pointer-events:auto!important;touch-action:none!important;cursor:grab!important",
 "pointer-events:none!important",
 "case 'preview':",
 "Chamber ON",
 "const two=[...fingers.values()]" # this intentionally catches outdated diagnostics if code renamed
)
for key in required:
 if key=="const two=[...fingers.values()]":
  key="const two=[...fingers.values()]"
 assert key in html,key
assert html.count('renderer.setAnimationLoop(tick);')==1
assert html.count('if(!playing&&!renderer.xr.isPresenting&&')==1
data=html.encode('utf8')
print(json.dumps({"version":"v11.255","patches":len(patches),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
