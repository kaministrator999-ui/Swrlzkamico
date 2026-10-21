#!/usr/bin/env python3
"""Produce an immutable v11.59 UI-regression fixture from the same governed source.

Use only AFTER verifying the exact latest sealed release candidate. This fixture deliberately
does NOT represent the release build: it exercises pre-dock brush/reference and
viewport assumptions, while the current release's browser tests exercise its floating UI behavior.
"""
import base64,gzip,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from build_space import load_patch
assert len(sys.argv)==2,"Usage: prepare_v11_59_regression_fixture.py /tmp/verified-current-package"
out=Path(sys.argv[1])
m=json.loads((root/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name']=='§wyrl§ Engine v11.62'
assert len(m['patches'])==94 and m['patches'][-1]=='patches/v11_62_mobile_adaptive.py'
assert (out/'SOURCE.json').exists() and (out/'index.html').exists()
receipt=json.loads((out/'SOURCE.json').read_text(encoding='utf-8'))
assert receipt['sourceVersion']==m['name'] and receipt['finalSha256']==m['finalSha256']
assert hashlib.sha256((out/'index.html').read_bytes()).hexdigest()==m['finalSha256']
raw=gzip.decompress(base64.b64decode(''.join((root/p).read_text(encoding='utf-8').strip() for p in m['chunks'])))
assert hashlib.sha256(raw).hexdigest()==m['baseSha256']
html=raw.decode('utf-8')
for rel in m['patches'][:-3]:
    html=load_patch(root/rel)(html)
data=html.encode('utf-8')
legacy_sha='f4d72c72a5fc4ee90c921198d7086b5898b89941de3efadd7f52c063d3dab0b3'
assert len(data)==2927005 and hashlib.sha256(data).hexdigest()==legacy_sha
assert b'SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER' in data
assert b'modelAtelierToolRail' not in data
(out/'index.html').write_bytes(data)
receipt.update(sourceVersion='§wyrl§ Engine v11.59',
               finalBytes=len(data),finalSha256=legacy_sha,
               patches=m['patches'][:-3])
(out/'SOURCE.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('V1159_HISTORICAL_BROWSER_FIXTURE_VERIFIED',len(data),legacy_sha,len(receipt['patches']),len(receipt['assets']))
