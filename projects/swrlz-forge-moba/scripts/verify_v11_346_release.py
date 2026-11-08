#!/usr/bin/env python3
"""Source-sealed v11.346 whole-character multi-sheet native UV atlas release."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_346_MODEL_MULTI_UV_SHEETS'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.346'
assert m['finalArtifact']=='swyrl_engine_v11_346.html'
assert len(m['patches'])==357
assert m['patches'][-1]=='patches/v11_346_model_multi_uv_sheets.py'
assert m['finalBytes']==9165566 and m['finalSha256']=='77228e757f77977a35f0b9b74bf0f5efc9c82659d70178256b4b9c8f2919ed23'
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for needle in [
 MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.346'",
 '<title>§wyrl§ Engine · Maker v11.346</title>',
 'SE346_MULTI_UV_SHEETS_START','SE345_MODEL_VR_DISPLAY_MODES_START',
 'function se346AtlasGo(', 'function se346AtlasSuffix(',
 'Previous sheet', 'Next sheet','se346AtlasPageInfo().pages',
 'function se345AtlasVerify(plan)','se345AtlasSelectedParts()',
 'SE344_MODEL_VR_AIM_VIEWS_START','SE343_MODEL_VR_SURFACE_HOVER_START',
 'SE340_MODEL_VR_BRIDGE_START','SE330_MATERIAL_STUDIO_LAYOUT_START'
]:assert needle in html,needle
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
for fn in ['model_multi_uv_sheets_v11_346.js','model_atelier_multi_uv_atlas_v11_345.js','model_studio_vr_ui_v11_345.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/fn)],check=True)
receipt=json.loads((output/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',m['name']),('patches',m['patches']),
                     ('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:
 assert receipt[key]==expected,key
assert len(receipt['assets'])==71
for name,info in receipt['assets'].items():
 content=(output/name).read_bytes()
 assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],name
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.346'
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256']
 assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.346',
 'patches':357,'bytes':len(data),'sha256':m['finalSha256'],
 'assets':71,'fullCharacterTestRun':42458051449,'physicalDeviceAcceptance':False},indent=2))
