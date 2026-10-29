#!/usr/bin/env python3
"""§E v11.150 exact generated source from 181 historical ordered patches."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf8'))
assert m['name']=='§wyrl§ Engine v11.150' and len(m['patches'])==182
assert m['patches'][-1]=='patches/v11_150_host_start_native_match.py'
raw=''.join((ROOT/x).read_text(encoding='utf8').strip() for x in m['chunks'])
html=gzip.decompress(base64.b64decode(raw)).decode('utf8')
for rel in m['patches']: html=load_patch(ROOT/rel)(html)
raw=html.encode('utf8');sha=hashlib.sha256(raw).hexdigest()
print('SE150_BYTES',len(raw),flush=True)
print('SE150_SHA',sha,flush=True)
print('SE150_SEAL_MATCH' if m['finalBytes']==len(raw) and m['finalSha256']==sha else 'SE150_NEEDS_SEAL',flush=True)
