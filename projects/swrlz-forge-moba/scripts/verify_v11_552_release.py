#!/usr/bin/env python3
"""Verify v11.552 sealed source, native UV editing and deploy request."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args): subprocess.run(args,check=True)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--request',action='store_true')
    args=parser.parse_args()
    m=json.loads((ROOT/'source-manifest.json').read_text())
    assert m['name']=='§wyrl§ Engine v11.552 UV texture alignment'
    assert m['finalArtifact']=='swyrl_engine_v11_552.html'
    assert m['patches'][-1]=='patches/v11_552_uv_texture_alignment.py'
    assert len(m['patches'])==526
    # Gate publication on the actual newly authored six-shell humanoid asset.
    run(sys.executable,str(ROOT/'scripts/check_humanoid_anatomy_v11_546.py'))
    run('node',str(ROOT/'tests/humanoid_anatomy_starter_v11_546.cjs'))
    run('node',str(ROOT/'tests/anatomical_region_sync_v11_552.cjs'))
    run('node',str(ROOT/'tests/startup_restore_regression_v11_552.cjs'))
    run(sys.executable,str(ROOT/'build_space.py'),'--output',str(args.output))
    page=(args.output/'index.html').read_bytes()
    assert page==(args.output/'modeler.html').read_bytes()
    assert hashlib.sha256(page).hexdigest()==m['finalSha256']
    assert len(page)==m['finalBytes']
    html=page.decode('utf8')
    for token in ('function se552Open()','function se551Install()','function se356EditInstall()','function se356EditApply(','se356EditInstall();','SE546_ANATOMY_ROBOT_STARTER_END','V11_546_ANATOMY_ROBOT_UV_4K'):
        assert token in html,token
    assert html.count('function se552Open()')==1
    assert html.count('function se551Install()')==1
    assert html.count('function se356EditInstall()')==1
    assert html.count('se356EditInstall();')==1
    run('node','--check',str(ROOT/'runtime/uv_texture_alignment_v11_552.js'))
    run(sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(args.output/'index.html'))
    receipt=json.loads((args.output/'SOURCE.json').read_text())
    assert receipt['finalSha256']==m['finalSha256']
    assert receipt['patches']==m['patches']
    for rel,expected in receipt['assets'].items():
        raw=(args.output/rel).read_bytes()
        assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],rel
    if args.request:
        req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
        assert req['releaseVersion']=='v11.552'
        assert req['target']=='kamiloki/swrlz-forge-moba'
        assert req['sourceIntegritySha256']==m['finalSha256']
        assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_546_ANATOMY_ROBOT_UV_4K'
    print('SE552_RELEASE_VERIFIED',json.dumps({'patches':len(m['patches']),'bytes':len(page),'sha256':m['finalSha256'],'assets':len(receipt['assets'])}),flush=True)
if __name__=='__main__':main()
