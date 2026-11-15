#!/usr/bin/env python3
"""§E v11.462 sealed source and bounded native wire/display release gate."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--output',required=True);p.add_argument('--request',action='store_true')
a=p.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.462'
assert m['finalArtifact']=='swyrl_engine_v11_462.html'
assert len(m['patches'])==439
assert m['patches'][-2:]==['patches/v11_461_model_edges_orbit_dock.py','patches/v11_462_model_wire_clarity.py']
out=Path(a.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
b=(out/'index.html').read_bytes()
assert b==(out/'modeler.html').read_bytes()
assert len(b)==m['finalBytes'] and hashlib.sha256(b).hexdigest()==m['finalSha256']
h=b.decode()
for token in ["window.SWRLZ_FORGE_BUILD={version:'v11.462'",
 '<title>§wyrl§ Engine · Maker v11.462</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE',
 'SE462_MODEL_WIRE_CLARITY_START','SE462_VIEW_AND_DOCK_STYLES_START',
 'SE461_HARD_SURFACE_ORBIT_START','SE460_NATIVE_VIEW_COMMANDS_START',
 'SE455_TRANSIENT_FACE_HIGHLIGHT_START','SE436_SATCHEL_CAVITY_START']:
 assert token in h,token
assert h.count(" source.engine='§wyrl§ Engine · Maker v11.462';source.version=11.462;")==5
for name in ['model_wire_clarity_v11_462.js','model_hard_surface_orbit_v11_461.js',
             'model_native_view_commands_v11_460.js','model_view_readability_v11_455.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_wire_clarity_v11_462.mjs'),str(out/'index.html')],check=True)
for name in ['model_hard_surface_orbit_v11_461.mjs','model_native_view_commands_v11_461.mjs']:
 subprocess.run(['node',str(ROOT/'tests'/name)],check=True)
s=json.loads((out/'SOURCE.json').read_text())
for key,value in [('sourceVersion',m['name']),('patches',m['patches']),
                  ('finalBytes',len(b)),('finalSha256',m['finalSha256'])]:assert s[key]==value
assert len(s['assets'])==77
for name,r in s['assets'].items():
 data=(out/name).read_bytes()
 assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],name
if a.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text())
 assert req['releaseVersion']=='v11.462'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE'
 assert req['sourceIntegritySha256']==m['finalSha256']
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.462',
                  'bytes':len(b),'sha256':m['finalSha256'],'assets':77,'patches':439}))
