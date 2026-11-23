#!/usr/bin/env python3
"""Rebuild §E native source and seal appended UV editor patch."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
patch='patches/v11_552_uv_texture_alignment.py'
assert patch not in m['patches']
packed=''.join((ROOT/p).read_text('utf8').strip() for p in m['chunks'])
base=gzip.decompress(base64.b64decode(packed))
assert hashlib.sha256(base).hexdigest()==m['baseSha256']
html=base.decode('utf8')
for p in m['patches']+[patch]:
    html=load_patch(ROOT/p)(html)
data=html.encode('utf8')
m['patches'].append(patch)
m['finalSha256']=hashlib.sha256(data).hexdigest()
m['finalBytes']=len(data)
m['name']='§wyrl§ Engine v11.552 UV texture alignment'
m['finalArtifact']='swyrl_engine_v11_552.html'
path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
print('UV_EDIT_SEALED',m['finalSha256'],len(data))
