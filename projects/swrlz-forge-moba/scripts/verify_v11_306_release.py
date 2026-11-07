#!/usr/bin/env python3
"""Verify the sealed §E v11.306 Sheep Tag pursuit performance release."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.306'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_306_SHEEP_PURSUIT_PERFORMANCE'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--request',action='store_true')
    args=p.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine v11.306'
    assert m['finalArtifact']=='swyrl_engine_v11_306.html'
    assert len(m['patches'])==337
    assert m['patches'][-2:]==[
      'patches/v11_305_vanguard_complete_mesh_uv.py',
      'patches/v11_306_sheep_pursuit_performance.py']
    assert m['finalBytes']==8397357
    assert m['finalSha256']=='a47415627055cda09f2152e9c6adc311347ed709971e6c0bea1be6bc7195910c'
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==m['finalBytes'] and hashlib.sha256(raw).hexdigest()==m['finalSha256']
    html=raw.decode('utf8')
    for marker in (MARKER,'SE306_SHARED_APPROACH_CACHE','SE306_CACHE_BOTH_CALLERS',
                   'SWYRL_ENGINE_SHEEP_PURSUIT_306','const se256AIBudget',
                   "window.SWRLZ_FORGE_BUILD={version:'v11.306'",
                   '<title>§wyrl§ Engine · Maker v11.306</title>',
                   'SE304_MODELER_DOCUMENT_VIEW_SYNC_START'):
        assert marker in html,marker
    assert html.count('renderer.setAnimationLoop(tick);')==1
    assert html.count('function se306CachedApproach(wolf,sheep){')==1
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.306';source.version=11.306;")==3
    subprocess.run(['node','--check',str(ROOT/'runtime/sheep_pursuit_performance_v11_306.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/sheep_pursuit_cache_v11_306.cjs'),str(out/'index.html')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==m['name']
    assert receipt['patches']==m['patches']
    assert receipt['finalSha256']==m['finalSha256']
    assert receipt['finalBytes']==m['finalBytes']
    assert len(receipt['assets'])==71
    if args.request:
        req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert req['releaseVersion']==VERSION and req['deployMarker']==MARKER
        assert req['sourceIntegritySha256']==m['finalSha256']
        assert len(req['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':VERSION,
      'patches':337,'bytes':len(raw),'sha256':m['finalSha256'],
      'assets':len(receipt['assets']),
      'liveQuestPerformanceAcceptance':False},indent=2))
if __name__=='__main__':main()
