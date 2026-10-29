#!/usr/bin/env python3
"""Compute exact §E v11.171 output with all historical patches, without publishing."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name']=='§wyrl§ Engine v11.171'
assert len(m['patches'])==203 and m['patches'][-1]=='patches/v11_171_project_modal_priority.py'
raw=''.join((ROOT/x).read_text(encoding='utf-8').strip() for x in m['chunks'])
html=gzip.decompress(base64.b64decode(raw)).decode('utf-8')
for rel in m['patches']: html=load_patch(ROOT/rel)(html)
data=html.encode('utf-8')
assert html.count('id="se171-project-hub-layer"')==1
print('SE171_BYTES',len(data),flush=True)
print('SE171_SHA',hashlib.sha256(data).hexdigest(),flush=True)
