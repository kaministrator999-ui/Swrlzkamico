#!/usr/bin/env python3
"""Verify sealed §E v11.308 Arcane grip-space glove + scoped ray hiding."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.308'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_308_ARCANE_HAND_GRIP_FIT'
SHA='a0148e2a9d406ef806bc580eee692e66011dc0922a0573ae07820d4f9f242511'
BYTES=8399073

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--request',action='store_true')
    args=p.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine '+VERSION
    assert m['finalArtifact']=='swyrl_engine_v11_308.html'
    assert len(m['patches'])==339
    assert m['patches'][-2:]==[
      'patches/v11_307_arcane_vr_glove_orientation.py',
      'patches/v11_308_arcane_grip_fit_hide_rays.py']
    assert m['finalBytes']==BYTES and m['finalSha256']==SHA
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==BYTES and hashlib.sha256(raw).hexdigest()==SHA
    html=raw.decode('utf8')
    for token in (
      MARKER,'SE307_DORSAL_UP_CONTROLLER_GLOVES','SE308_GRIP_ANCHOR',
      'SE308_HIDE_XR_RAYS','SE308_GLOVE_FIT','function se308GloveAnchor(side,record){',
      "poseGroup.rotation.set(-Math.PI/2,Math.PI,0);",
      'function se280Cast(side,record,key){',
      "window.SWRLZ_FORGE_BUILD={version:'v11.308'",
      '<title>§wyrl§ Engine · Maker v11.308</title>',
      'SE306_SHARED_APPROACH_CACHE','SE304_MODELER_DOCUMENT_VIEW_SYNC_START'
    ): assert token in html,token
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('function se279XRFrame(){')==1
    assert html.count('function se279BuildGlove(side){')==1
    assert html.count('function se280Cast(side,record,key){')==1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.308';source.version=11.308;")==3
    subprocess.run([sys.executable,'-m','py_compile',
      str(ROOT/'patches/v11_308_arcane_grip_fit_hide_rays.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
      str(out/'index.html')],check=True)
    subprocess.run(['node',str(ROOT/'tests/arcane_grip_ray_v11_308.cjs'),
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
      'patches':339,'bytes':len(raw),'sha256':SHA,'assets':len(receipt['assets']),
      'liveQuestGripFitAcceptance':False},indent=2))
if __name__=='__main__':main()
