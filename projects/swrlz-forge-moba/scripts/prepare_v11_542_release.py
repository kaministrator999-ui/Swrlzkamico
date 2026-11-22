#!/usr/bin/env python3
"""§E v11.542 seal exact 519-patch source after native UV atlas baking.

The source manifest's finalBytes/SHA-256 are computed from actually rebuilt
HTML, never guessed from a diff or overridden to make deployment pass.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
PATCH='patches/v11_542_humanoid_relaxed_uv.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_542_HUMANOID_RELAXED_UV_ATLAS'

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    p=ROOT/'source-manifest.json'
    manifest=json.loads(p.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.541'
    assert manifest['finalArtifact']=='swyrl_engine_v11_541.html'
    assert len(manifest['patches'])==518
    assert manifest['patches'][-1]=='patches/v11_541_humanoid_starter_category.py'
    assert PATCH not in manifest['patches']
    assert (ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json').exists()
    assert (ROOT/'assets/models/futuristic-humanoid-v11-542-uv-guide.png').exists()
    packed=''.join((ROOT/rel).read_text('utf8').strip()
                   for rel in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[PATCH]:
        html=load_patch(ROOT/rel)(html)
    content=html.encode('utf8')
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.542'" in html
    assert '<title>§wyrl§ Engine · Maker v11.542</title>' in html
    assert 'se537OpenMannequin=se542OpenHumanoid' in html
    sha=hashlib.sha256(content).hexdigest()
    manifest.update(
        name='§wyrl§ Engine v11.542',
        finalArtifact='swyrl_engine_v11_542.html',
        patches=manifest['patches']+[PATCH],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,
        finalBytes=len(content))
    p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE542_UV_ATLAS_SOURCE_SEALED',json.dumps({
        'bytes':len(content),'sha256':sha,
        'patches':len(manifest['patches'])}),flush=True)

if __name__=='__main__':
    main()
