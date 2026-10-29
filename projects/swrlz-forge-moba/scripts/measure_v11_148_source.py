#!/usr/bin/env python3
"""Measure exact §E v11.148 from original payload + ALL 180 patches."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
manifest=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf8'))
assert manifest['name']=='§wyrl§ Engine v11.148'
assert len(manifest['patches'])==180
assert manifest['patches'][-1]=='patches/v11_148_sheep_lan_waiting_room.py'
data=''.join((ROOT/path).read_text(encoding='utf8').strip() for path in manifest['chunks'])
html=gzip.decompress(base64.b64decode(data)).decode('utf8')
for rel in manifest['patches']:
    html=load_patch(ROOT/rel)(html)
raw=html.encode('utf8')
digest=hashlib.sha256(raw).hexdigest()
print('SE148_EXACT_BYTES',len(raw),flush=True)
print('SE148_EXACT_SHA256',digest,flush=True)
print('SE148_PATCHES',len(manifest['patches']),flush=True)
if len(raw)!=manifest['finalBytes'] or digest!=manifest['finalSha256']:
    print('SE148_CANDIDATE_NEEDS_SEAL',flush=True)
else:
    print('SE148_SOURCE_SEAL_MATCH',flush=True)
    from tempfile import TemporaryDirectory
    import subprocess
    with TemporaryDirectory() as tmp:
        subprocess.run(['python',str(ROOT/'build_space.py'),'--output',tmp],check=True)
        bundled=(Path(tmp)/'index.html').read_bytes()
        assert bundled==raw
        assert len(json.loads((Path(tmp)/'SOURCE.json').read_text())['assets'])==68
        print('SE148_BUNDLE_68_ASSETS_VERIFIED',flush=True)
