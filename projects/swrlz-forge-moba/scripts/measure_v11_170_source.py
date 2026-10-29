#!/usr/bin/env python3
"""Measure exact generated HTML without weakening production's final seal gate."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name']=='§wyrl§ Engine v11.170'
assert len(m['patches'])==202 and m['patches'][-1]=='patches/v11_170_project_library_tabs.py'
encoded=''.join((ROOT/x).read_text(encoding='utf-8').strip() for x in m['chunks'])
html=gzip.decompress(base64.b64decode(encoded)).decode('utf-8')
for rel in m['patches']:html=load_patch(ROOT/rel)(html)
raw=html.encode('utf-8')
assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_170_PROJECT_LIBRARY_TABS' in html
assert 'se170Install' in html
print('SE170_BYTES',len(raw),flush=True)
print('SE170_SHA',hashlib.sha256(raw).hexdigest(),flush=True)
