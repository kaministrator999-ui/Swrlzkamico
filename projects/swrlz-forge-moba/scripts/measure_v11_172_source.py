#!/usr/bin/env python3
"""Measure v11.172 whole engine build from historical source before sealing."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf-8'))
assert m['name']=='§wyrl§ Engine v11.172'
assert len(m['patches'])==204 and m['patches'][-1]=='patches/v11_172_clean_chat_header.py'
blob=''.join((ROOT/x).read_text(encoding='utf-8').strip() for x in m['chunks'])
html=gzip.decompress(base64.b64decode(blob)).decode('utf-8')
for rel in m['patches']:html=load_patch(ROOT/rel)(html)
assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_172_CLEAN_CHAT_HEADER' in html
assert '<strong>§wyrlz Chat</strong><button type="button" id="seChatClose"' in html
assert '<a href="https://kamiloki-swyrlz.hf.space" target="_blank" rel="noopener">Open Chat</a>' not in html
assert 'id="seChatSignIn"' in html and 'id="seChatLoad"' in html
raw=html.encode('utf-8')
print('SE172_BYTES',len(raw),flush=True)
print('SE172_SHA',hashlib.sha256(raw).hexdigest(),flush=True)
