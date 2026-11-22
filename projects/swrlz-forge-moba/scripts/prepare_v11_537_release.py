#!/usr/bin/env python3
"""Reconstruct and seal §E v11.537 in CI from authoritative ordered patch lineage.

Does not bypass any final source-integrity checks: the actual UTF-8 HTML
is built and hashed before recording the manifest, then the normal production
builder and release tests independently verify the same bytes.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    manifest=json.loads(path.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.536', 'Source moved; reconcile before release.'
    assert manifest['finalArtifact']=='swyrl_engine_v11_536.html'
    assert len(manifest['patches'])==513
    new='patches/v11_537_robotic_humanoid_mannequin.py'
    assert new not in manifest['patches']
    packed=''.join((ROOT/name).read_text('utf8').strip() for name in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[new]:
        html=load_patch(ROOT/rel)(html)
    encoded=html.encode('utf8')
    sha=hashlib.sha256(encoded).hexdigest()
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_537_ROBOTIC_HUMANOID_MANNEQUIN' in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.537'" in html
    assert '<title>§wyrl§ Engine · Maker v11.537</title>' in html
    manifest.update(
        name='§wyrl§ Engine v11.537',
        finalArtifact='swyrl_engine_v11_537.html',
        patches=manifest['patches']+[new],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,
        finalBytes=len(encoded)
    )
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE537_SEALED_MANIFEST',json.dumps({'sha256':sha,'bytes':len(encoded),'patches':len(manifest['patches'])}),flush=True)

if __name__=='__main__':
    main()
