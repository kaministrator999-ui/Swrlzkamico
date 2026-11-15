#!/usr/bin/env python3
"""§E v11.465 source, full native toolbar history regression and asset integrity."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--request',action='store_true')
a=p.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.465'
assert m['finalArtifact']=='swyrl_engine_v11_465.html'
assert len(m['patches'])==442
assert m['patches'][-2:]==['patches/v11_464_model_visual_inspector.py','patches/v11_465_inspector_readability.py']
out=Path(a.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
b=(out/'index.html').read_bytes()
assert b==(out/'modeler.html').read_bytes()
assert len(b)==m['finalBytes'] and hashlib.sha256(b).hexdigest()==m['finalSha256']
h=b.decode()
for token in ["window.SWRLZ_FORGE_BUILD={version:'v11.465'",
 '<title>§wyrl§ Engine · Maker v11.465</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_465_INSPECTOR_READABILITY',
 'SE465_NARROW_INSPECTOR_START','SE465_NARROW_INSPECTOR_STYLES_START',
 'SE464_MODEL_VISUAL_POLISH_START','SE464_INSPECTOR_VISUAL_POLISH_START',
 'SE462_MODEL_WIRE_CLARITY_START','SE461_HARD_SURFACE_ORBIT_START',
 'SE460_NATIVE_VIEW_COMMANDS_START','SE450_CAMERA_RESIZE_GUARD_START',
 'SE455_TRANSIENT_FACE_HIGHLIGHT_START','SE436_SATCHEL_CAVITY_START',
 'se320ModelTransformAccess(panel,inspector);',
 'SE461_TOUCH_DOCK_BOUNDS_START','SE462_VIEW_AND_DOCK_STYLES_START']:
 assert token in h,token
assert h.count(" source.engine='§wyrl§ Engine · Maker v11.465';source.version=11.465;")==5
for name in ['model_inspector_readability_v11_465.js','model_visual_polish_v11_464.js','model_wire_clarity_v11_462.js','model_hard_surface_orbit_v11_461.js',
             'model_native_view_commands_v11_460.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_transform_history_v11_465.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_visual_polish_v11_464.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_inspector_readability_v11_465.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_wire_clarity_v11_462.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_hard_surface_orbit_v11_461.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_native_view_commands_v11_461.mjs')],check=True)
s=json.loads((out/'SOURCE.json').read_text())
for key,value in [('sourceVersion',m['name']),('patches',m['patches']),
                  ('finalBytes',len(b)),('finalSha256',m['finalSha256'])]:
 assert s[key]==value
assert len(s['assets'])==77
for name,r in s['assets'].items():
 data=(out/name).read_bytes()
 assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],name
if a.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
 assert req['releaseVersion']=='v11.464'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_465_INSPECTOR_READABILITY'
 assert req['sourceIntegritySha256']==m['finalSha256']
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.465',
  'bytes':len(b),'sha256':m['finalSha256'],'assets':77,'patches':442,
  'physicalPhoneAcceptance':False}))
