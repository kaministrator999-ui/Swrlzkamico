#!/usr/bin/env python3
"""Independently reconstruct and measure a proposed v11.62 source even before its manifest seal is updated."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from build_space import load_patch
manifest=json.loads((root/'source-manifest.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.62' and len(manifest['patches'])==94
src=gzip.decompress(base64.b64decode(''.join((root/p).read_text(encoding='utf-8').strip() for p in manifest['chunks'])))
assert hashlib.sha256(src).hexdigest()==manifest['baseSha256']
html=src.decode('utf-8')
for patch in manifest['patches']:
 html=load_patch(root/patch)(html)
data=html.encode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_LAYOUT')==1
print('V1162_RELEASE_RESEAL '+json.dumps({'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'patches':len(manifest['patches']),'manifestSha256':manifest['finalSha256'],'manifestBytes':manifest['finalBytes']},sort_keys=True),flush=True)
