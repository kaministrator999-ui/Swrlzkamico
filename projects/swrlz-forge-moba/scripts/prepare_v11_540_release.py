#!/usr/bin/env python3
"""§E v11.540 deterministic SHA sealing from the 516 historical patches plus hand release."""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
NEW='patches/v11_540_humanoid_five_digit.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_540_HUMANOID_FIVE_DIGIT'

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    manifest=json.loads(path.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.539','source version changed; reconcile lineage'
    assert manifest['finalArtifact']=='swyrl_engine_v11_539.html'
    assert len(manifest['patches'])==516
    assert manifest['patches'][-1]=='patches/v11_539_immersive_sculpt_load.py'
    assert NEW not in manifest['patches']
    assert (ROOT/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json').exists()
    packed=''.join((ROOT/rel).read_text('utf8').strip() for rel in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[NEW]:
        html=load_patch(ROOT/rel)(html)
    content=html.encode('utf8')
    sha=hashlib.sha256(content).hexdigest()
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.540'" in html
    assert '<title>§wyrl§ Engine · Maker v11.540</title>' in html
    assert 'se537OpenMannequin=se540OpenHumanoid' in html
    manifest.update(
        name='§wyrl§ Engine v11.540',
        finalArtifact='swyrl_engine_v11_540.html',
        patches=manifest['patches']+[NEW],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,
        finalBytes=len(content)
    )
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE540_SEALED_MANIFEST',json.dumps({'sha256':sha,'bytes':len(content),
          'patches':len(manifest['patches'])}),flush=True)

if __name__=='__main__':
    main()
