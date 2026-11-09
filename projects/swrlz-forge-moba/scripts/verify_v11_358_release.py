#!/usr/bin/env python3
"""Verify §E v11.358 native WebXR left/right reference hand starter release."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_358_WEBXR_HAND_STARTERS'
ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--request',action='store_true');args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.358' and m['finalArtifact']=='swyrl_engine_v11_358.html'
assert len(m['patches'])==366 and m['patches'][-1]=='patches/v11_358_webxr_hand_starters.py'
assert m['finalBytes']==9323081 and m['finalSha256']=='8f3e1d431e95d8abd48c7f73176afa9faf41834bcb489c195855289b1420530d'
output=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes();assert data==(output/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for needle in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.358'",'<title>§wyrl§ Engine · Maker v11.358</title>',
 'se356UVMode=\'guide\'','Export UV wireframe','Import painted image','Advanced UV references (optional)',
 'window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze','function se336InstallSlideEvents()', 'texture.offset.set(slide[0],slide[1]);','part.uvPaintOffset=next;', 'data-se320-history="undo"','data-se320-history="redo"','window.SWYRLZ_E_UV_POPUP=Object.freeze','se355UVEditorOpen','se355UVPopup','se355UVNativeHost','modelAtelierUVLayout','se345UVAtlas','se355-uv-slide','se355-uv-scroll',
 'se356UVPreview','se356UVCanvas','se356UVPick3D','se356UVResolve(u,v)', 'function se356ApplyCameraOrbit()','renderer.xr.setReferenceSpace(space);', "s.rig.rotation.set(0,s.baseYaw,0,'YXZ')",'const tools=se350Tools(),chosen=tools.selection()', 'function safeBounds(){','fitWindow(true);',
 'SE351_GAME_QUICK_ACTIONS_START',"se320ModelTransformAccess(panel,inspector);","const scene=q('.atelier-scene',panel);",'se320-native-transform-proxy',"const active=!!state?.open&&!!state?.selected&&!panel.hidden;",'data-se320-transform="move"','data-se320-transform="rotate"','data-se320-transform="scale"','data-se320-transform="minus"','data-se320-transform="plus"','source?.click();','se351GameQuickBar','se238GameTools','se320GameMore',
 'projectBtn','playBtn','stopBtn','se181EnterVR','More options','SE350_MODEL_VR_TWO_HAND_WORKSPACE','SE350_MODEL_VR_NATIVE_TOOLS_START','SE350_MODEL_VR_SURFACE_START',
 'vrTools:se350ModelTools,vrSurface:se350ModelSurface','se350CreateModelVRInput','currentProfile:()=>',
 'SE346_MULTI_UV_SHEETS_START','SE345_MODEL_VR_DISPLAY_MODES_START','SE344_MODEL_VR_AIM_VIEWS_START',
 'SE343_MODEL_VR_SURFACE_HOVER_START','SE330_MATERIAL_STUDIO_LAYOUT_START','brushRadius','lassoBegin']:
 assert needle in html,needle
for needle in [
 'data-project-template="webxr-hand-left"',
 'data-project-template="webxr-hand-right"',
 'SWYRL_ENGINE_WEBXR_HAND_STARTERS',
 'se358OpenWebXRHand',
 'se358WebXRHandScene',
 'topologyMesh:structuredClone(asset.mesh)',
 'referenceJoints=structuredClone(asset.joints)',
 'assets/models/webxr-hands/left.json',
 'assets/models/webxr-hands/right.json'
]:
 assert needle in html,needle
subprocess.run(['node','--check',str(ROOT/'runtime/webxr_reference_hand_starters_v11_358.js')],check=True)
for side in ('left','right'):
 asset=json.loads((output/f'assets/models/webxr-hands/{side}.json').read_text('utf8'))
 t=asset['mesh']
 assert asset['schema']=='swrlz-webxr-reference-hand-v1' and asset['side']==side
 assert len(t['positions'])==4080 and len(t['uvs'])==2720 and len(t['indices'])==6942
 assert len(asset['joints'])==25 and max(t['indices'])<1360
license=(output/'assets/models/webxr-hands/LICENSE.md').read_text('utf8')
assert 'MIT License' in license and 'Copyright (c) 2019 Amazon' in license
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/studio_editor_layout_v11_320.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_atelier_uv_layout_v11_336.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_studio_uv_popup_v11_355.js')],check=True)
for jsname in ['model_atelier_uv_preview_v11_356.js','model_vr_workspace_v11_350.js','model_vr_input_profile_v11_350.js','model_studio_vr_ui_v11_350.js']:
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
assert len(receipt['assets'])==74
for name,info in receipt['assets'].items():
 content=(output/name).read_bytes();assert len(content)==info['bytes'] and hashlib.sha256(content).hexdigest()==info['sha256'],name
assert len([p for p in output.rglob('*') if p.is_file()])==78
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']=='v11.358' and request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==m['finalSha256'] and len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.358','patches':len(m['patches']),
 'bytes':len(data),'sha256':m['finalSha256'],'assets':74,'physicalHeadsetAcceptance':False},indent=2))
