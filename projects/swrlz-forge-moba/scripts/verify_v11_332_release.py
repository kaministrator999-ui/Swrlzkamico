#!/usr/bin/env python3
"""§E v11.332: minimal, exact, source-backed Smooth Cliff Hand release verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_332_CLIFF_CRACK_ATLAS'

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('--output', required=True)
    cli.add_argument('--request', action='store_true')
    args = cli.parse_args()
    manifest = json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert manifest['name'] == '§wyrl§ Engine v11.332'
    assert manifest['finalArtifact'] == 'swyrl_engine_v11_331.html'
    assert len(manifest['patches']) == 345
    assert manifest['patches'][-2:] == [
        'patches/v11_330_material_studio_layout.py',
        'patches/v11_331_smooth_cliff_material_uv.py']
    assert manifest['finalBytes'] > 0 and len(manifest['finalSha256']) == 64
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw == (out/'modeler.html').read_bytes()
    assert len(raw)==manifest['finalBytes']
    assert hashlib.sha256(raw).hexdigest()==manifest['finalSha256']
    html=raw.decode('utf8')
    for token in (
        MARKER,
        "window.SWRLZ_FORGE_BUILD={version:'v11.332'",
        '<title>§wyrl§ Engine · Maker v11.332</title>',
        "part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se292WristMossKnuckleMaterial(part)",
        "g.setAttribute('uv2',g.getAttribute('uv').clone());",
        "g.setAttribute('uv1',g.getAttribute('uv2'));",
        "if(kind==='ao')tex.channel=1;",
        "function se292WristMossKnuckleMaterial(part){",
        "  color:'#ffffff',",
        "  aoMap:t.ao,aoMapIntensity:1,",
        "model.parts=[stone];model.meshGroups=[];",
        'function se332OverlayRockFractures(img,albedoCtx){',
        'se332OverlayRockFractures(img,albedo);',
        'SE330_MATERIAL_STUDIO_LAYOUT_START',
        'SE321_LOS_CORE_START',
    ):
        assert token in html,token
    assert html.count("g.setAttribute('uv1',g.getAttribute('uv2'));")==1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.332';source.version=11.331;")==3
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
    subprocess.run(['node',str(ROOT/'scripts/test_v11_332_cliff_fractures.cjs')],check=True)
    subprocess.run(['node',str(ROOT/'scripts/test_v11_292_cliff_material.cjs')],check=True)
    subprocess.run(['node',str(ROOT/'scripts/test_v11_290_cliff_gauntlet.cjs')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==manifest['name']
    assert receipt['patches']==manifest['patches']
    assert receipt['finalBytes']==manifest['finalBytes']
    assert receipt['finalSha256']==manifest['finalSha256']
    assert receipt['workspacePages']=={'game':'index.html','modeler':'modeler.html'}
    assert len(receipt['assets'])==71
    for name,meta in receipt['assets'].items():
        content=(out/name).read_bytes()
        assert len(content)==meta['bytes'] and hashlib.sha256(content).hexdigest()==meta['sha256'],name
    if args.request:
        request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert request['releaseVersion']=='v11.332'
        assert request['deployMarker']==MARKER
        assert request['sourceIntegritySha256']==manifest['finalSha256']
        assert len(request['sourceCommit'])==40
    print(json.dumps({
        'status':'SEALED_SOURCE_VERIFIED','version':'v11.332',
        'patches':345,'htmlBytes':len(raw),
        'sha256':manifest['finalSha256'],'assets':71,
        'ownerDeviceAccepted':False},indent=2))

if __name__=='__main__':
    main()
