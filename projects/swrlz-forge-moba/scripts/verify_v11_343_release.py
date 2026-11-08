#!/usr/bin/env python3
"""Seal and validate v11.343 camera-relative VR model surface picking release."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_343_MODEL_VR_SURFACE_CAMERA'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.343'
assert m['finalArtifact']=='swyrl_engine_v11_343.html'
assert len(m['patches'])==354
assert m['patches'][-1]=='patches/v11_343_model_vr_surface_camera.py'
assert m['finalBytes']==9128756 and m['finalSha256']=='7f34d4884d8491515789052b4c36a5564cdd298c5901debb9824cfe0b2dee2f6'
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes'] and hashlib.sha256(raw).hexdigest()==m['finalSha256']
text=raw.decode('utf8')
for needle in [
 MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.343'",
 '<title>§wyrl§ Engine · Maker v11.343</title>',
 'SE343_MODEL_VR_SURFACE_HOVER_START','se343HoverContact(entry,cast)',
 'SE343_HOVER_FACE_BUDGET=3600',
 'se340XR.pan.x-dx*dt*.42*gain','se340XR.pan.y+dy*dt*.42*gain',
 'se340XR.yaw+=dx*dt*1.35*gain','se340XR.pitch-dy*dt*1.05*gain',
 'SE340_MODEL_VR_BRIDGE_START','SE330_MATERIAL_STUDIO_LAYOUT_START'
]:assert needle in text,needle
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_vr_surface_pick_v11_343.js')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:
 assert receipt[key]==expected
assert len(receipt['assets'])==71
for name,meta in receipt['assets'].items():
 data=(out/name).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.343'
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256']
 assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.343',
 'patches':354,'bytes':len(raw),'sha256':m['finalSha256'],
 'assets':71,'surfaceRayTestRun':42450424824,'physicalHeadsetAcceptance':False},indent=2))
