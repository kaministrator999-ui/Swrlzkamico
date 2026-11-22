#!/usr/bin/env python3
"""§E v11.546: replay actual source patches, seal the real assembled SHA."""
import base64,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATCH='patches/v11_546_humanoid_anatomical_uv_4k.py'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_546_ANATOMY_ROBOT_UV_4K'
def main():
    sys.path.insert(0,str(ROOT))
    from build_space import load_patch
    path=ROOT/'source-manifest.json'
    manifest=json.loads(path.read_text('utf8'))
    assert manifest['name']=='§wyrl§ Engine v11.545'
    assert manifest['finalArtifact']=='swyrl_engine_v11_545.html'
    assert len(manifest['patches'])==522
    assert manifest['patches'][-1]=='patches/v11_545_humanoid_uv_anatomy.py'
    assert PATCH not in manifest['patches']
    for rel in ('runtime/humanoid_anatomical_robot_v11_546.js',
                'tests/humanoid_anatomy_starter_v11_546.cjs',
                'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'):
        assert (ROOT/rel).exists(),rel
    packed=''.join((ROOT/rel).read_text('utf8').strip() for rel in manifest['chunks'])
    raw=gzip.decompress(base64.b64decode(packed))
    assert len(raw)==manifest['baseBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['baseSha256']
    html=raw.decode('utf8')
    for rel in manifest['patches']+[PATCH]:
        html=load_patch(ROOT/rel)(html)
    encoded=html.encode('utf8')
    assert MARKER in html
    assert "window.SWRLZ_FORGE_BUILD={version:'v11.546'" in html
    assert '<title>§wyrl§ Engine · Maker v11.546</title>' in html
    assert 'SE546_ANATOMY_ROBOT_STARTER_END' in html
    sha=hashlib.sha256(encoded).hexdigest()
    manifest.update(
        name='§wyrl§ Engine v11.546',
        finalArtifact='swyrl_engine_v11_546.html',
        patches=manifest['patches']+[PATCH],
        previousFinalSha256=manifest['finalSha256'],
        previousFinalBytes=manifest['finalBytes'],
        previousManifestFinalSha256=manifest['finalSha256'],
        finalSha256=sha,finalBytes=len(encoded))
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print('SE546_ANATOMY_ROBOT_SOURCE_SEALED',json.dumps({
        'sha256':sha,'bytes':len(encoded),'patches':len(manifest['patches'])}),flush=True)
if __name__=='__main__':main()
