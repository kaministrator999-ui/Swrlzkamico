#!/usr/bin/env python3
"""Build/verify the sealed v11.344 Model Studio XR aim/view/click release."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_344_MODEL_VR_AIM_VIEWS_TRIGGER'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.344'
assert manifest['finalArtifact']=='swyrl_engine_v11_344.html'
assert len(manifest['patches'])==355
assert manifest['patches'][-1]=='patches/v11_344_model_vr_aim_views_trigger.py'
assert manifest['finalBytes']==9135955
assert manifest['finalSha256']=='7adec1e91ee56f5eeda364c3d733de3d95d8fb5824753d943ef6382f27bc3d4f'
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
text=data.decode('utf8')
for key in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.344'",
 '<title>§wyrl§ Engine · Maker v11.344</title>',
 'SE344_MODEL_VR_AIM_VIEWS_START','se344AimQuat(record)',
 "page:s.page,viewMode:s.viewMode","const triggerStarted=performance.now();const hit=se340Hit(record,false);",
 'SE343_MODEL_VR_SURFACE_HOVER_START','SE340_MODEL_VR_BRIDGE_START',
 'SE330_MATERIAL_STUDIO_LAYOUT_START','SE321_LOS_CORE_START']:
 assert key in text,key
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
for fn in ['model_vr_aim_views_v11_344.js','model_studio_vr_ui_v11_344.js','model_vr_bridge_v11_344.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/fn)],check=True)
receipt=json.loads((output/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',manifest['name']),('patches',manifest['patches']),
                     ('finalBytes',manifest['finalBytes']),('finalSha256',manifest['finalSha256'])]:
 assert receipt[key]==expected,key
assert len(receipt['assets'])==71
for name,info in receipt['assets'].items():
 blob=(output/name).read_bytes()
 assert len(blob)==info['bytes'] and hashlib.sha256(blob).hexdigest()==info['sha256'],name
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.344'
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==manifest['finalSha256']
 assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.344',
 'patches':355,'bytes':len(data),'sha256':manifest['finalSha256'],
 'assets':71,'nativeAimViewTestRun':42455530224,'physicalHeadsetAcceptance':False},indent=2))
