#!/usr/bin/env python3
"""Verify the exact source-sealed fluent Model VR controller release."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_391_SHEEP_QUEST_Y_TOOLS_RADIAL'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true');args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.391' and m['finalArtifact']=='swyrl_engine_v11_390.html'
assert len(m['patches'])==390 and m['patches'][-1]=='patches/v11_391_sheep_quest_y_tools.py'
assert m['finalBytes']>9_530_598 and len(m['finalSha256'])==64
out=Path(args.output).resolve();subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes();assert data==(out/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode()
for token in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.391'",'<title>§wyrl§ Engine · Maker v11.391</title>',
 'SE390_MODEL_VR_QUICK_CREATE_START','SE390_MODEL_VR_GRAB_POSE_START','SE390_MODEL_VR_FLUENT_TOOLS_START','SE390_MODEL_VR_FLUENT_UI',
 'SE390_MODEL_VR_HOTKEY_HINTS_START','vrCreate:se390ModelCreate','se390CreationFrame(s,dt)','se390BeginGrab(record,purpose,pose)',
 'SE376_VR_SELECTOR_LASSO_START','SE374_MODEL_VR_OWNER_FEEDBACK_START','SE372_MODEL_VR_PHASE1_START',
 'SWYRL_ENGINE_ADVANCED_GRAPHICS_380','SWYRL_ENGINE_SHEEP_XR_GUEST_381','SWYRL_ENGINE_SHEEP_VR_Y_MENU_391','se378Blockout','se366ImportAuthored',
 'se356ApplyCameraOrbit','SE362_CONTROLLER_HINTS_START','SWYRL_ENGINE_SAFE_PROJECTS_371']:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.391';source.version=11.390;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for name in ['model_vr_quick_create','model_vr_grab','model_vr_fluent_tools','model_vr_hotkey_hints','model_vr_input_profile','model_studio_vr_ui']:
 p=ROOT/'runtime'/f'{name}_v11_390.js';subprocess.run(['node','--check',str(p)],check=True)
 assert 'requestAnimationFrame(' not in p.read_text() and 'setAnimationLoop(' not in p.read_text()
subprocess.run(['node','--check',str(ROOT/'runtime/sheep_vr_y_tools_radial_v11_391.js')],check=True)
subprocess.run(['node',str(ROOT/'tests/test_sheep_vr_y_menu_v11_391.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text())
for key,want in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:assert receipt[key]==want,key
assert len(receipt['assets'])==77
for name,info in receipt['assets'].items():
 content=(out/name).read_bytes();assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],name
assert len([p for p in out.rglob('*') if p.is_file()])==81
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text());assert request['releaseVersion']=='v11.391' and request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256'] and len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.391','patches':len(m['patches']),
 'bytes':len(data),'sha256':m['finalSha256'],'assets':77,'physicalHeadsetAcceptance':False},indent=2))
