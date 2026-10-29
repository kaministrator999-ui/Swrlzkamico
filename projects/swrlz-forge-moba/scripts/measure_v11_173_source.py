#!/usr/bin/env python3
"""Measure reconstructed v11.173 source without weakening the sealed builder."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name'] in ('§wyrl§ Engine v11.172','§wyrl§ Engine v11.173')
patches=list(m['patches'])
last='patches/v11_173_dialog_stack.py'
if patches[-1]!=last:patches.append(last)
assert len(patches)==205 and patches[-2]=='patches/v11_172_clean_chat_header.py'
encoded=''.join((ROOT/x).read_text(encoding='utf-8').strip() for x in m['chunks'])
html=gzip.decompress(base64.b64decode(encoded)).decode('utf-8')
for rel in patches:html=load_patch(ROOT/rel)(html)
assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_173_DIALOG_LAYER_PRIORITY' in html
assert 'se173PromoteProjectDialog' in html and 'se173-editor-layer-priority' in html
assert 'se170Install' in html and 'st141RuntimeMenu' in html
raw=html.encode('utf-8')
print('SE173_BYTES',len(raw),flush=True)
print('SE173_SHA',hashlib.sha256(raw).hexdigest(),flush=True)
