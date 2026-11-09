#!/usr/bin/env python3
"""Verify the sealed §E v11.361 WebXR hand starter repair and Quest 2 Touch models."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_361_WEBXR_STARTERS_OPEN_AND_TOUCH'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true');args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.361' and m['finalArtifact']=='swyrl_engine_v11_361.html'
assert len(m['patches'])==368 and m['patches'][-1]=='patches/v11_361_webxr_hand_open_touch_starters.py'
assert m['finalBytes']==9346125 and m['finalSha256']=='20e0bb0183cd6fcc579d6f08cf8b126472bcf3a5dcfe043366e170dcb5fe9810'
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes();assert data==(output/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for needle in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.361'",'<title>§wyrl§ Engine · Maker v11.361</title>',
 'se358OpenWebXRHand','assets/models/webxr-hands/',
 'SE360_MODEL_VR_MENU_MOTION_START','SE360_MODEL_VR_UI_START','se360AdvanceMenu(dt)',
 'se360MenuContact(record)','prefers-reduced-motion: reduce',
 'se356UVMode=\'guide\'','Export UV wireframe','Import painted image','Advanced UV references (optional)',
 'window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze','function se336InstallSlideEvents()', 'texture.offset.set(slide[0],slide[1]);','part.uvPaintOffset=next;', 'data-se320-history="undo"','data-se320-history="redo"','window.SWYRLZ_E_UV_POPUP=Object.freeze','se355UVEditorOpen','se355UVPopup','se355UVNativeHost','modelAtelierUVLayout','se345UVAtlas','se355-uv-slide','se355-uv-scroll',
 'se356UVPreview','se356UVCanvas','se356UVPick3D','se356UVResolve(u,v)', 'function se356ApplyCameraOrbit()','renderer.xr.setReferenceSpace(space);', "s.rig.rotation.set(0,s.baseYaw,0,'YXZ')",'const tools=se350Tools(),chosen=tools.selection()', 'function safeBounds(){','fitWindow(true);',
 'SE351_GAME_QUICK_ACTIONS_START',"se320ModelTransformAccess(panel,inspector);","const scene=q('.atelier-scene',panel);",'se320-native-transform-proxy',"const active=!!state?.open&&!!state?.selected&&!panel.hidden;",'data-se320-transform="move"','data-se320-transform="rotate"','data-se320-transform="scale"','data-se320-transform="minus"','data-se320-transform="plus"','source?.click();','se351GameQuickBar','se238GameTools','se320GameMore',
 'projectBtn','playBtn','stopBtn','se181EnterVR','More options','SE350_MODEL_VR_TWO_HAND_WORKSPACE','SE350_MODEL_VR_NATIVE_TOOLS_START','SE350_MODEL_VR_SURFACE_START',
 'vrTools:se350ModelTools,vrSurface:se350ModelSurface','se350CreateModelVRInput','currentProfile:()=>',
 'SE346_MULTI_UV_SHEETS_START','SE345_MODEL_VR_DISPLAY_MODES_START','SE344_MODEL_VR_AIM_VIEWS_START',
 'SE343_MODEL_VR_SURFACE_HOVER_START','SE330_MATERIAL_STUDIO_LAYOUT_START','brushRadius','lassoBegin']:
 assert needle in html,needle
assert html.count("source.engine='§wyrl§ Engine · Maker v11.361';source.version=11.361;")==5
for needle in [
 'data-project-template="webxr-hand-left"',
 'data-project-template="webxr-hand-right"',
 'data-project-template="webxr-touch-left"',
 'data-project-template="webxr-touch-right"',
 'se361OpenStarter',
 'se361InstallStarterClicks',
 'SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361',
 'se361ControllerScene',
 'assets/models/webxr-touch-v3/'
]:
 assert needle in html,needle
subprocess.run(['node','--check',str(ROOT/'runtime/webxr_model_starters_v11_361.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_webxr_model_starters_v11_361.cjs')],check=True)
for side in ('left','right'):
 data=json.loads((output/f'assets/models/webxr-touch-v3/{side}.json').read_text('utf8'))
 assert data['schema']=='swrlz-webxr-controller-v1' and len(data['parts'])==7
 assert data['colorTexturePNG'].startswith('data:image/png;base64,')
 assert all(len(p['mesh']['positions'])//3<=9000 and len(p['mesh']['indices'])//3<=16000 for p in data['parts'])
assert 'MIT License' in (output/'assets/models/webxr-touch-v3/LICENSE.md').read_text('utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/studio_editor_layout_v11_320.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_atelier_uv_layout_v11_336.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_studio_uv_popup_v11_355.js')],check=True)
for jsname in ['model_atelier_uv_preview_v11_356.js','model_vr_workspace_v11_350.js','model_vr_input_profile_v11_350.js','model_studio_vr_ui_v11_360.js','model_vr_menu_motion_v11_360.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/jsname)],check=True)
assert 'max-height:calc(100dvh - 64px)' in (ROOT/'runtime/model_studio_uv_popup_v11_355.css').read_text('utf8')
assert 'host.append(single)' in (ROOT/'runtime/model_studio_uv_popup_v11_355.js').read_text('utf8')
assert 'position:absolute!important' in (ROOT/'runtime/studio_editor_layout_v11_320.css').read_text('utf8')
assert '#se320ModelTransform[hidden]' in (ROOT/'runtime/studio_editor_layout_v11_320.css').read_text('utf8')
assert 'se320-native-transform-proxy' in (ROOT/'runtime/studio_editor_layout_v11_320.css').read_text('utf8')
subprocess.run(['node','--check',str(ROOT/'runtime/game_quick_actions_v11_351.js')],check=True)
for name in ['model_vr_workspace','model_vr_native_tools','model_vr_sculpt_draw','model_vr_input_profile','model_studio_vr_ui']:
 source=ROOT/'runtime'/f'{name}_v11_350.js'
 subprocess.run(['node','--check',str(source)],check=True)
 assert 'requestAnimationFrame(' not in source.read_text() and 'setAnimationLoop(' not in source.read_text()
receipt=json.loads((output/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256'])]:
 assert receipt[key]==expected,key
assert len(receipt['assets'])==77
for name,info in receipt['assets'].items():
 content=(output/name).read_bytes();assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],name
assert len([p for p in output.rglob('*') if p.is_file()])==81
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.361' and request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256'] and len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.361','patches':len(m['patches']),
 'bytes':len(data),'sha256':m['finalSha256'],'assets':77,'physicalHeadsetAcceptance':False},indent=2))
