#!/usr/bin/env python3
"""Authoritative §E v11.538 SHA reseal from all historical patches + the new patch.

No hard-coded digest: generate the exact UTF-8 HTML through the existing
ordered patch lineage, calculate its actual bytes/hash and independently
revalidate with the standard production builder before deployment.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
NEW='patches/v11_538_smooth_uv_humanoid.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_538_SMOOTH_UV_HUMANOID'

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    m=json.loads(path.read_text('utf8'))
    assert m['name']=='§wyrl§ Engine v11.537'
    assert m['finalArtifact']=='swyrl_engine_v11_537.html'
    assert len(m['patches'])==514
    assert m['patches'][-1]=='patches/v11_537_robotic_humanoid_mannequin.py'
    assert NEW not in m['patches']
    assert (ROOT/'scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json').exists()
    packed=''.join((ROOT/part).read_text('utf8').strip() for part in m['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==m['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==m['baseSha256']
    html=raw.decode('utf8')
    for rel in m['patches']+[NEW]:
        html=load_patch(ROOT/rel)(html)
    encoded=html.encode('utf8')
    sha=hashlib.sha256(encoded).hexdigest()
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.538'" in html
    assert '<title>§wyrl§ Engine · Maker v11.538</title>' in html
    assert 'se537OpenMannequin=se538OpenHumanoid' in html
    m.update(name='§wyrl§ Engine v11.538',
             finalArtifact='swyrl_engine_v11_538.html',
             patches=m['patches']+[NEW],
             previousFinalSha256=m['finalSha256'],
             previousFinalBytes=m['finalBytes'],
             previousManifestFinalSha256=m['finalSha256'],
             finalSha256=sha,finalBytes=len(encoded))
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE538_SEALED_MANIFEST',json.dumps({
        'bytes':len(encoded),'sha256':sha,'patches':len(m['patches'])}),flush=True)

if __name__=='__main__':
    main()
