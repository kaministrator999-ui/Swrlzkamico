#!/usr/bin/env python3
"""§E v11.504 release: connected joint editing, real weights and intact source, exact source and HF request."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((root/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.504'
assert m['finalArtifact']=='swyrl_engine_v11_504.html'
assert len(m['patches'])==481
assert m['patches'][-5:]==[
 'patches/v11_500_connected_rig_weights.py',
 'patches/v11_501_uv_diagnostic_exports.py',
 'patches/v11_502_uv_touch_resize.py',
 'patches/v11_503_uv_island_atlas.py',
 'patches/v11_504_smooth_witch_hat.py']
subprocess.run(['node','--check',str(root/'runtime/sorting_hat_sculpted_v11_497.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_studio_polish_v11_499.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_connected_math_v11_500.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_connected_edit_v11_500.js')],check=True)
subprocess.run(['node',str(root/'tests/model_rig_connected_v11_500.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_rig_workspace_v11_490.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_heatmap_export_v11_501.js')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_heatmap_export_v11_501.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_touch_resize_v11_502.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_island_math_v11_503.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_island_ui_v11_503.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/smooth_witch_hat_v11_504.js')],check=True)
subprocess.run(['node',str(root/'tests/smooth_witch_hat_v11_504.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_island_atlas_v11_503.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_touch_resize_v11_502.cjs')],check=True)
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
 '<title>§wyrl§ Engine · Maker v11.504</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT',
 'data-project-template="smooth-witch-hat"',
 'SE504_SMOOTH_WITCH_HAT_END',
 'SWYRL_ENGINE_SMOOTH_WITCH_HAT_504',
 'data-project-template="sorting-hat-sculpted"',
 'data-project-template="sorting-hat"',
 'SWYRL_ENGINE_SORTING_HAT_SCULPTED_497',
 'SE483_SORTING_HAT_END',
 'SWYRL_ENGINE_MINI_STUDIOS_496',
 'SWYRL_ENGINE_RIG_POLISH_499',
 'new THREE.SphereGeometry(1,12,9)',
 'new THREE.CylinderGeometry(.50,.86,1,9,1)',
 'data-se499-rig-kind=object',
 'SWYRL_ENGINE_RIG_CONNECTED_MATH_500',
 'SWYRL_ENGINE_RIG_CONNECTED_EDIT_500',
 'se500WeightsCount','se500LockLength','syncRestTransform',
 'SE501_UV_HEATMAP_EXPORT_START','SWYRLZ_E_UV_HEATMAP_EXPORT_501',
 'data-se501-export="heat"','data-se501-export="overlay"',
 'SE502_UV_TOUCH_RESIZE_START','se502InstallResizable(popup)',
 'se502UVMax','se502-uv-se','se502ToggleMax',
 'SE503_UV_ISLAND_MATH_START','SE503_UV_ISLAND_UI_START',
 'se503AtlasPrepare','se503AtlasApply','V11_503_UV_ISLAND_ATLAS'
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
 assert req['releaseVersion']=='v11.504'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert len(req.get('sourceCommit',''))==40
print('SE504_SOURCE_VERIFIED',json.dumps({'version':'v11.504','patches':481,
 'bytes':len(raw),'sha256':m['finalSha256'],
 'nativeSingleMesh':True,'originalStarterPreserved':True,'rigStudioUIIsolated':True,'connectedRigAndWeights':True,'uvDiagnosticExports':True,'uvTouchResize':True,'uvIslandAtlas':True}),flush=True)
