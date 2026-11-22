#!/usr/bin/env python3
"""§E v11.541 exact integrity seal for category-only mannequin recovery.

Reassemble all 517 original ordered patches, append the independent native
Projects category correction, then compute the actual resulting HTML bytes
and SHA. No manual checksum overrides.
"""
from pathlib import Path
import base64
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
PATCH='patches/v11_541_humanoid_starter_category.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_541_HUMANOID_STARTER_CATEGORY'

def main():
    import sys
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    manifest=json.loads(path.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.540'
    assert manifest['finalArtifact']=='swyrl_engine_v11_540.html'
    assert len(manifest['patches'])==517
    assert manifest['patches'][-1]=='patches/v11_540_humanoid_five_digit.py'
    assert PATCH not in manifest['patches']
    packed=''.join((ROOT/rel).read_text('utf8').strip()
                   for rel in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[PATCH]:
        html=load_patch(ROOT/rel)(html)
    assembled=html.encode('utf8')
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.541'" in html
    assert '<title>§wyrl§ Engine · Maker v11.541</title>' in html
    sha=hashlib.sha256(assembled).hexdigest()
    manifest.update(
        name='§wyrl§ Engine v11.541',
        finalArtifact='swyrl_engine_v11_541.html',
        patches=manifest['patches']+[PATCH],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,finalBytes=len(assembled))
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE541_CATEGORY_SEALED',json.dumps({
        'bytes':len(assembled),'sha256':sha,'patches':len(manifest['patches'])}),flush=True)

if __name__=='__main__':
    main()
