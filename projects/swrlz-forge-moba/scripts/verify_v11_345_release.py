#!/usr/bin/env python3
"""Seal and validate the original-UV multi-part atlas + VR material-mode release."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_345_MODEL_MULTI_UV_VR_DISPLAY'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.345'
assert manifest['finalArtifact']=='swyrl_engine_v11_345.html'
assert len(manifest['patches'])==356
assert manifest['patches'][-1]=='patches/v11_345_model_multi_uv_vr_display.py'
assert manifest['finalBytes']==9162827 and manifest['finalSha256']=='39a192fc72c4eac1435a6bdec4a53039578196e6bb97040716fe6b64b3452cc5'
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
html=data.decode('utf8')
for key in [
 MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.345'",
 '<title>§wyrl§ Engine · Maker v11.345</title>',
 'SE345_MODEL_VR_DISPLAY_MODES_START',
 "['display-wireframe','Wireframe']","['display-xray','X-ray']",
 'se345RestoreDisplay();','se345SyncDisplay();',
 'function se345AtlasLayout(', "schema:'swyrl-model-uv-atlas-v1'",
 'Whole-model UV atlas','se345AtlasVerify(plan)',"for (const button of root.querySelectorAll('.se336-uv-actions button'))",
 'SE344_MODEL_VR_AIM_VIEWS_START','SE343_MODEL_VR_SURFACE_HOVER_START',
 'SE340_MODEL_VR_BRIDGE_START','SE330_MATERIAL_STUDIO_LAYOUT_START'
]:assert key in html,key
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
for name in ['model_vr_display_modes_v11_345.js','model_studio_vr_ui_v11_345.js','model_atelier_multi_uv_atlas_v11_345.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
receipt=json.loads((output/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',manifest['name']),('patches',manifest['patches']),('finalBytes',manifest['finalBytes']),('finalSha256',manifest['finalSha256'])]:
 assert receipt[key]==expected,key
assert len(receipt['assets'])==71
for name,info in receipt['assets'].items():
 data=(output/name).read_bytes()
 assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256'],name
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.345'
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==manifest['finalSha256']
 assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.345',
 'patches':356,'bytes':len(data),'sha256':manifest['finalSha256'],
 'assets':71,'linkedUVTestRun':42457148584,'physicalHardwareAcceptance':False},indent=2))
