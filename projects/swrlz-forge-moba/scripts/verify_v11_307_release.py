#!/usr/bin/env python3
"""Verify the sealed §E v11.307 Arcane VR glove orientation release."""
import argparse,hashlib,json,math,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.307'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_307_ARCANE_VR_GLOVE_ORIENTATION'
SHA='6c3591a2e2261366de0f96f09517e5f933a770440a8d1b8a782bc8cd1b8f278a'
BYTES=8397373

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--request',action='store_true')
    args=p.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine '+VERSION
    assert m['finalArtifact']=='swyrl_engine_v11_307.html'
    assert len(m['patches'])==338
    assert m['patches'][-2:]==[
      'patches/v11_306_sheep_pursuit_performance.py',
      'patches/v11_307_arcane_vr_glove_orientation.py']
    assert m['finalBytes']==BYTES and m['finalSha256']==SHA
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==BYTES and hashlib.sha256(raw).hexdigest()==SHA
    html=raw.decode('utf8')
    for token in (
      MARKER,'SE307_DORSAL_UP_CONTROLLER_GLOVES',
      "const source=side==='left'?se212HandScene():se279LeftScene();",
      'poseGroup.rotation.set(-Math.PI/2,Math.PI,0);',
      "window.SWRLZ_FORGE_BUILD={version:'v11.307'",
      '<title>§wyrl§ Engine · Maker v11.307</title>',
      'SE306_SHARED_APPROACH_CACHE',
      'function se279XRFrame(){',
      'function se280Cast(side,record,key){',
      'SE304_MODELER_DOCUMENT_VIEW_SYNC_START'
    ):
        assert token in html,token
    assert html.count('poseGroup.rotation.set(-Math.PI/2,Math.PI,0);')==1
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('function se279BuildGlove(side){')==1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.307';source.version=11.307;")==3
    # Euler XYZ mount R_x(-pi/2) * R_y(pi). Check intended XR axes.
    def transform(v):
        x,y,z=v
        x,y,z=-x,y,-z   # rotate Y by pi
        return (x,z,-y) # rotate X by -pi/2
    def eq(actual,expected):
        assert all(abs(a-b)<1e-9 for a,b in zip(actual,expected)),(actual,expected)
    eq(transform((0,1,0)),(0,0,-1))  # fingers forward
    eq(transform((0,0,1)),(0,-1,0)) # palm down
    eq(transform((0,0,-1)),(0,1,0)) # backhand up
    eq(transform((1,0,0)),(-1,0,0)) # right inward thumb from mirrored source
    eq(transform((-1,0,0)),(1,0,0))# left inward thumb from original source
    subprocess.run([sys.executable,'-m','py_compile',
      str(ROOT/'patches/v11_307_arcane_vr_glove_orientation.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
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
      'patches':338,'bytes':len(raw),'sha256':SHA,'assets':len(receipt['assets']),
      'liveQuestGloveAcceptance':False},indent=2))
if __name__=='__main__':main()
