#!/usr/bin/env python3
"""Verify the exact sealed §E v11.351 Game Engine quick-actions release."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_351_GAME_QUICK_ACTIONS'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true');args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.351' and m['finalArtifact']=='swyrl_engine_v11_351.html'
assert len(m['patches'])==359 and m['patches'][-1]=='patches/v11_351_game_quick_actions.py'
assert m['finalBytes']>9_200_000 and len(m['finalSha256'])==64
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes();assert data==(output/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for needle in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.351'",'<title>§wyrl§ Engine · Maker v11.351</title>',
 'SE351_GAME_QUICK_ACTIONS_START','se351GameQuickBar','se238GameTools','se320GameMore',
 'projectBtn','playBtn','stopBtn','se181EnterVR','More options','SE350_MODEL_VR_TWO_HAND_WORKSPACE','SE350_MODEL_VR_NATIVE_TOOLS_START','SE350_MODEL_VR_SURFACE_START',
 'vrTools:se350ModelTools,vrSurface:se350ModelSurface','se350CreateModelVRInput','currentProfile:()=>',
 'SE346_MULTI_UV_SHEETS_START','SE345_MODEL_VR_DISPLAY_MODES_START','SE344_MODEL_VR_AIM_VIEWS_START',
 'SE343_MODEL_VR_SURFACE_HOVER_START','SE330_MATERIAL_STUDIO_LAYOUT_START','brushRadius','lassoBegin']:
 assert needle in html,needle
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/game_quick_actions_v11_351.js')],check=True)
for name in ['model_vr_workspace','model_vr_native_tools','model_vr_sculpt_draw','model_vr_input_profile','model_studio_vr_ui']:
 source=ROOT/'runtime'/f'{name}_v11_350.js'
 subprocess.run(['node','--check',str(source)],check=True)
 assert 'requestAnimationFrame(' not in source.read_text() and 'setAnimationLoop(' not in source.read_text()
receipt=json.loads((output/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:
 assert receipt[key]==expected,key
assert len(receipt['assets'])==71
for name,info in receipt['assets'].items():
 content=(output/name).read_bytes();assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],name
assert len([p for p in output.rglob('*') if p.is_file()])==75
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.351' and request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256'] and len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.351','patches':len(m['patches']),
 'bytes':len(data),'sha256':m['finalSha256'],'assets':71,'physicalHeadsetAcceptance':False},indent=2))
