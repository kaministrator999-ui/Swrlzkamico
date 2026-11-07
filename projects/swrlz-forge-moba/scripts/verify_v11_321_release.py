#!/usr/bin/env python3
"""Verify the sealed §E v11.321 Sheep Tag sight and crowded Quest diagnostics release."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_321_SHEEP_SIGHT_XR_CROWD'
def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--output',required=True)
    cli.add_argument('--request',action='store_true')
    args=cli.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
    assert m['name']=='§wyrl§ Engine v11.321'
    assert m['finalArtifact']=='swyrl_engine_v11_321.html'
    assert len(m['patches'])==342
    assert m['patches'][-2:]==['patches/v11_320_studio_navigation_layout.py',
        'patches/v11_321_sheep_sight_xr_crowd.py']
    assert m['finalBytes']==8451859
    assert m['finalSha256']=='47e8cc9f9f54fb1592715961ecd4faab13fc94f56e0f8208c250efc3306b2079'
    out=Path(args.output).resolve()
    subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
    raw=(out/'index.html').read_bytes()
    assert raw==(out/'modeler.html').read_bytes()
    assert len(raw)==m['finalBytes']
    assert hashlib.sha256(raw).hexdigest()==m['finalSha256']
    html=raw.decode('utf8')
    for token in (MARKER,'SE321_LOS_CORE_START','SE321_LOS_CORE_END',
        'SWYRL_ENGINE_SHEEP_VISION_XR_321',
        'SE306_SHARED_APPROACH_CACHE','const se256AIBudget',
        'SE320_PROJECT_STUDIO_ROUTING_START','SE320_EDITOR_LAYOUT_START',
        '<title>§wyrl§ Engine · Maker v11.321</title>',
        "window.SWRLZ_FORGE_BUILD={version:'v11.321'"):
        assert token in html,token
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.321';source.version=11.321;")==3
    assert html.count('renderer.setAnimationLoop(tick);')==1
    subprocess.run(['node','--check',str(ROOT/'runtime/sheep_sight_xr_crowd_v11_321.js')],check=True)
    subprocess.run(['node',str(ROOT/'tests/sheep_sight_xr_crowd_v11_321.cjs'),str(out/'index.html')],check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
       str(out/'index.html')],check=True)
    receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
    assert receipt['sourceVersion']==m['name']
    assert receipt['patches']==m['patches']
    assert receipt['finalSha256']==m['finalSha256']
    assert receipt['finalBytes']==m['finalBytes']
    assert len(receipt['assets'])==71
    if args.request:
        req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
        assert req['releaseVersion']=='v11.321'
        assert req['deployMarker']==MARKER
        assert req['sourceIntegritySha256']==m['finalSha256']
        assert len(req['sourceCommit'])==40
    print(json.dumps({'status':'SEALED_SOURCE_VERIFIED',
      'version':'v11.321','patches':len(m['patches']),
      'htmlBytes':len(raw),'sha256':m['finalSha256'],
      'assets':len(receipt['assets']),
      'QuestVisualAndPerformanceAcceptance':False},indent=2))
if __name__=='__main__':main()
