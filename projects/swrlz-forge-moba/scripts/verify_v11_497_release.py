#!/usr/bin/env python3
"""§E v11.497 — verify original and sculpted Sorting Hats, SHA and deployment request."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.497'
assert manifest['finalArtifact']=='swyrl_engine_v11_497.html'
assert len(manifest['patches'])==474
assert manifest['patches'][-2:]==[
 'patches/v11_496_model_mini_studios.py','patches/v11_497_sculpted_sorting_hat.py']
for name in ('sorting_hat_sculpted_v11_497.js','model_mini_studios_v11_496.js',
             'sorting_hat_starter_v11_483.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/sorting_hat_sculpted_v11_497.cjs')],check=True)
subprocess.run([sys.executable,str(ROOT/'tests/sorting_hat_single_mesh_v11_485.py')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_rig_workspace_v11_490.cjs')],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
source=(out/'index.html').read_bytes()
assert source==(out/'modeler.html').read_bytes()
assert len(source)==manifest['finalBytes']
assert hashlib.sha256(source).hexdigest()==manifest['finalSha256']
html=source.decode('utf8')
for keyword in (
 '<title>§wyrl§ Engine · Maker v11.497</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT',
 'data-project-template="sorting-hat-sculpted"',
 'SWYRL_ENGINE_SORTING_HAT_SCULPTED_497',
 'se497OpenSculptedHat','se497DeformHat',
 'SWYRL_ENGINE_MINI_STUDIOS_496',
 'data-project-template="sorting-hat"',
 'SE483_SORTING_HAT_END',
 'parts.length!==1||!Array.isArray(scene?.scene?.actors)',
):assert keyword in html,keyword
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
                str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for k,expect in (
 ('sourceVersion',manifest['name']),
 ('finalSha256',manifest['finalSha256']),
 ('finalBytes',manifest['finalBytes']),
 ('patches',manifest['patches'])
):assert receipt[k]==expect,k
assert 'scenes/model-atelier-sorting-hat.swyrl.json' in receipt['assets']
original=json.loads((out/'scenes/model-atelier-sorting-hat.swyrl.json').read_text('utf8'))
assert original['project']['canonicalId']=='sorting-hat'
assert len(original['project']['modelAtelier']['parts'])==1
assert len(original['project']['modelAtelier']['parts'][0]['topologyMesh']['positions'])==7859*3
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.497'
 assert request['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT'
 assert request['target']=='kamiloki/swrlz-forge-moba'
 assert request['sourceIntegritySha256']==manifest['finalSha256']
 assert len(request.get('sourceCommit',''))==40
print('SE497_SOURCE_VERIFIED',json.dumps({
 'version':'v11.497','sourceBytes':len(source),
 'sha256':manifest['finalSha256'],'patches':len(manifest['patches']),
 'originalStarterPreserved':True,'secondStarterNativeSingleMesh':True}),flush=True)
