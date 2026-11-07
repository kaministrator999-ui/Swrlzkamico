#!/usr/bin/env python3
"""Verify sealed §E v11.309 native Arcane aiming and complete beam hiding."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.309'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_309_ARCANE_NATIVE_RAY_AIM'
SHA='f52a2e9838735d4bf0026d560a4bdf24e943b54d01c933bce9e05dfb6af90ec5'
BYTES=8402089

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--request',action='store_true')
    args=p.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine '+VERSION
    assert m['finalArtifact']=='swyrl_engine_v11_309.html'
    assert len(m['patches'])==340
    assert m['patches'][-2:]==[
      'patches/v11_308_arcane_grip_fit_hide_rays.py',
      'patches/v11_309_arcane_native_ray_aim.py']
    assert m['finalBytes']==BYTES and m['finalSha256']==SHA
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==BYTES and hashlib.sha256(raw).hexdigest()==SHA
    html=raw.decode('utf8')
    for token in (
      MARKER,'function se309ArcaneRayless(){',
      'function se309HideRayGraphics(record){',
      'const se309PreviousRenderRay=se192RenderRay;',
      'const se309PreviousVRFrame=se192VRFrame;',
      'SE308_GRIP_ANCHOR','SE308_HIDE_XR_RAYS',
      'SE307_DORSAL_UP_CONTROLLER_GLOVES',
      'function se280Cast(side,record,key){',
      "window.SWRLZ_FORGE_BUILD={version:'v11.309'",
      '<title>§wyrl§ Engine · Maker v11.309</title>',
      'SE306_SHARED_APPROACH_CACHE'
    ):assert token in html,token
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('function se279XRFrame(){')==1
    assert html.count('function se280Cast(side,record,key){')==1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.309';source.version=11.309;")==3
    subprocess.run(['node','--check',str(ROOT/'runtime/arcane_ray_alignment_v11_309.js')],check=True)
    subprocess.run([sys.executable,'-m','py_compile',
      str(ROOT/'patches/v11_309_arcane_native_ray_aim.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
      str(out/'index.html')],check=True)
    subprocess.run(['node',str(ROOT/'tests/arcane_native_ray_v11_309.cjs'),
      str(out/'index.html')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==m['name']
    assert receipt['patches']==m['patches']
    assert receipt['finalSha256']==SHA and receipt['finalBytes']==BYTES
    assert len(receipt['assets'])==71
    if args.request:
        req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert req['releaseVersion']==VERSION and req['deployMarker']==MARKER
        assert req['sourceIntegritySha256']==SHA
        assert len(req['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':VERSION,
      'patches':340,'bytes':len(raw),'sha256':SHA,'assets':len(receipt['assets']),
      'nativeMetaPointerAcceptance':False},indent=2))
if __name__=='__main__':main()
