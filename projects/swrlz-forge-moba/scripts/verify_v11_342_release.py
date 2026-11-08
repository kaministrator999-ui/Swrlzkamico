#!/usr/bin/env python3
"""Seal and verify v11.342 Model VR proxy hover source/asset integrity."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_342_MODEL_VR_PROXY_PICKING'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.342'
assert m['finalArtifact']=='swyrl_engine_v11_342.html'
assert len(m['patches'])==353
assert m['patches'][-1]=='patches/v11_342_model_vr_proxy_picking.py'
assert m['finalBytes']==9122053 and m['finalSha256']=='ab1f1309ac860c540583db730c4ff1866be5fc074f73ca220181a6cf5029a4ad'
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes'] and hashlib.sha256(raw).hexdigest()==m['finalSha256']
html=raw.decode('utf8')
for needle in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.342'",
               '<title>§wyrl§ Engine · Maker v11.342</title>',
               'se340Hit(record,false)','s.projectionRevision!==native.revision',
               'hoverFaceRaycasts:0','SE340_MODEL_VR_BRIDGE_START',
               'SE330_MATERIAL_STUDIO_LAYOUT_START','SE321_LOS_CORE_START']:
 assert needle in html,needle
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for filename in ['model_vr_workspace_v11_342.js','model_studio_vr_ui_v11_342.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/filename)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_vr_proxy_picking_v11_342.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:
 assert receipt[key]==expected
assert len(receipt['assets'])==71
for name,meta in receipt['assets'].items():
 data=(out/name).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.342'
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256']
 assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.342',
                  'patches':353,'bytes':len(raw),'sha256':m['finalSha256'],
                  'assets':71,'physicalHeadsetAcceptance':False},indent=2))
