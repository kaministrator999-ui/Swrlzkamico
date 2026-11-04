#!/usr/bin/env python3
"""Narrow source-integrity calculator for the v11.247 append-only engine patch.
Rebuild from the verified base and all existing patches; print candidate bytes/SHA.
Does not change source-manifest.json, modify user data or deploy.
"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch

manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.246'
assert len(manifest['patches'])==277
base=gzip.decompress(base64.b64decode(''.join(
 (ROOT/name).read_text('utf8').strip() for name in manifest['chunks'])))
assert len(base)==manifest['baseBytes']
assert hashlib.sha256(base).hexdigest()==manifest['baseSha256']
html=base.decode('utf8')
for rel in [*manifest['patches'],'patches/v11_247_editor_live_previews.py']:
    html=load_patch(ROOT/rel)(html)
raw=html.encode('utf8')
for key in (
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_247_EDITOR_PREVIEW_TOGGLES',
 'SWYRL_ENGINE_EDITOR_PREVIEW_247',
 'se247PreviewPanel',
 'se247LivePreviewStyle',
):
    assert key in html,key
assert html.count('renderer.setAnimationLoop(tick);')==1
print(json.dumps({'version':'v11.247','patches':278,
                  'finalBytes':len(raw),
                  'finalSha256':hashlib.sha256(raw).hexdigest(),
                  'singleRenderer':True},indent=2))
