#!/usr/bin/env python3
"""§E v11.499 release: original + improved single mesh, isolated rig controls, exact source and HF request."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((root/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.499'
assert m['finalArtifact']=='swyrl_engine_v11_498.html'
assert len(m['patches'])==476
assert m['patches'][-3:]==[
 'patches/v11_497_sculpted_sorting_hat.py',
 'patches/v11_498_hat_proportions.py',
 'patches/v11_499_rig_studio_polish.py']
subprocess.run(['node','--check',str(root/'runtime/sorting_hat_sculpted_v11_497.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_studio_polish_v11_499.js')],check=True)
subprocess.run(['node',str(root/'tests/model_rig_workspace_v11_490.cjs')],check=True)
subprocess.run(['node',str(root/'tests/sorting_hat_sculpted_v11_497.cjs')],check=True)
subprocess.run([sys.executable,str(root/'tests/sorting_hat_single_mesh_v11_485.py')],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']
s=raw.decode('utf8')
for needle in (
 '<title>§wyrl§ Engine · Maker v11.499</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_499_RIG_STUDIO_POLISH',
 'data-project-template="sorting-hat-sculpted"',
 'data-project-template="sorting-hat"',
 'SWYRL_ENGINE_SORTING_HAT_SCULPTED_497',
 'SE483_SORTING_HAT_END',
 'SWYRL_ENGINE_MINI_STUDIOS_496',
 'SWYRL_ENGINE_RIG_POLISH_499',
 'new THREE.SphereGeometry(1,12,9)',
 'new THREE.CylinderGeometry(.50,.86,1,9,1)',
 'data-se499-rig-kind=object'
):assert needle in s,needle
subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/sorting_hat_proportion_v11_498.cjs'),str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,value in [('sourceVersion',m['name']),('finalBytes',len(raw)),
                  ('finalSha256',m['finalSha256']),('patches',m['patches'])]:
 assert receipt[key]==value,key
scene=json.loads((out/'scenes/model-atelier-sorting-hat.swyrl.json').read_text('utf8'))
assert scene['project']['canonicalId']=='sorting-hat'
assert len(scene['project']['modelAtelier']['parts'])==1
if args.request:
 req=json.loads((root/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.499'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_499_RIG_STUDIO_POLISH'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert len(req.get('sourceCommit',''))==40
print('SE499_SOURCE_VERIFIED',json.dumps({'version':'v11.499','patches':476,
 'bytes':len(raw),'sha256':m['finalSha256'],
 'nativeSingleMesh':True,'originalStarterPreserved':True,'rigStudioUIIsolated':True}),flush=True)
