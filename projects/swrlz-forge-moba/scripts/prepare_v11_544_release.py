#!/usr/bin/env python3
"""§E v11.544: seal actual compiled tool-search source from ordered patches.

Do not invent checksums. Replay authoritative 519-patch lineage and the
new navigation patch to calculate actual resulting native HTML and SHA-256.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
PATCH='patches/v11_543_tool_navigation_search.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_544_HUMANOID_SURFACE_PAINT'

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    manifest=json.loads(path.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.543'
    assert manifest['finalArtifact']=='swyrl_engine_v11_543.html'
    assert len(manifest['patches'])==520
    assert manifest['patches'][-1]=='patches/v11_543_tool_navigation_search.py'
    assert PATCH not in manifest['patches']
    assert (ROOT/'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json').exists()
    assert (ROOT/'assets/models/futuristic-humanoid-v11-544-surface-anchored.png').exists()
    packed=''.join((ROOT/rel).read_text('utf8').strip() for rel in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[PATCH]:
        html=load_patch(ROOT/rel)(html)
    encoded=html.encode('utf8')
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.544'" in html
    assert '<title>§wyrl§ Engine · Maker v11.544</title>' in html
    assert 'SE544_MAPPED_HUMANOID_STARTER_END' in html and 'SE544_MAPPED_MANNEQUIN_REPAIR_END' in html
    sha=hashlib.sha256(encoded).hexdigest()
    manifest.update(
        name='§wyrl§ Engine v11.544',
        finalArtifact='swyrl_engine_v11_543.html',
        patches=manifest['patches']+[PATCH],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,finalBytes=len(encoded)
    )
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE544_MAPPED_PAINT_SOURCE_SEALED',json.dumps({
        'sha256':sha,'bytes':len(encoded),'patches':len(manifest['patches'])}),flush=True)

if __name__=='__main__':
    main()
