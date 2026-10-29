#!/usr/bin/env python3
"""Independently measure the actual governed v11.60 patch chain, without trusting its seal."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from build_space import load_patch
m=json.loads((root/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name']=='§wyrl§ Engine v11.60'
assert len(m['patches'])==92
assert m['patches'][-1]=='patches/v11_60_floating_tool_dock.py'
original=gzip.decompress(base64.b64decode(''.join((root/p).read_text(encoding='utf-8').strip() for p in m['chunks'])))
assert len(original)==m['baseBytes']
assert hashlib.sha256(original).hexdigest()==m['baseSha256']
html=original.decode('utf-8')
for patch in m['patches']:
    html=load_patch(root/patch)(html)
data=html.encode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_60_FLOATING_MODEL_ATELIER_DOCK')==1
print('V1160_INDEPENDENT_MEASURE',json.dumps({
  'finalBytes':len(data),'finalSha256':hashlib.sha256(data).hexdigest(),
  'manifestBytes':m['finalBytes'],'manifestSha256':m['finalSha256'],
  'matchesSeal':len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256'],
  'patches':len(m['patches'])},sort_keys=True),flush=True)
