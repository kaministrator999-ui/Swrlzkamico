#!/usr/bin/env python3
"""Source/asset integrity and bounded crowded-Sheep rendering verification."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--output',required=True);P.add_argument('--request',action='store_true');P.add_argument('--three-module');A=P.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text());assert m['name']=='§wyrl§ Engine v11.439';assert m['finalArtifact']=='swyrl_engine_v11_439.html';assert len(m['patches'])==416
assert m['patches'][-9:]==['patches/v11_431_model_gizmo_access.py','patches/v11_432_mobile_camera_orbit.py','patches/v11_433_model_camera_preferences.py','patches/v11_434_sheep_crowded_vr.py','patches/v11_435_model_vr_grab_gizmo.py','patches/v11_436_cube_extrude_satchel.py','patches/v11_437_sheep_territory_capture.py','patches/v11_438_engine_simulation_render_bridge.py','patches/v11_439_sheep_capture_pursuit.py']
out=Path(A.output).resolve();subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes();assert data==(out/'modeler.html').read_bytes();assert len(data)==m['finalBytes'];assert hashlib.sha256(data).hexdigest()==m['finalSha256'];html=data.decode()
marker='SWYRL_ENGINE_DEPLOY_MARKER: V11_439_SHEEP_CAPTURE_PURSUIT'
for token in [marker,"window.SWRLZ_FORGE_BUILD={version:'v11.439'",'<title>§wyrl§ Engine · Maker v11.439</title>',
 'const occluded=se434XrayEligible(unit,s)&&','renderer.xr?.isPresenting?renderer.xr.getCamera(camera):',
 'SE434_SHEEP_VISUAL_BATCH_START','SE434_SHEEP_VISIBLE_FRAME_RECOVERY_START','SE434_SHEEP_XRAY_POLICY_START','SE434_ENGINE_EDITOR_SHADOW_CACHE_START',
 'SE433_CAMERA_PREFS_START','se433CameraPrefs.install(panel);','touchRadius:28,mouseRadius:12','se411PlanSheepBuild(unit)','SE419_SHEEP_CONGESTION_BUDGET_START',
 'se265BatchBuilding(building)','SE425_LEVEL_UI_OBSERVER_GUARD','SE430_MODEL_VR_VISUAL_TEACHING','SE431_MODEL_VR_GIZMO_ACCESS_START',
 'SE417_MODEL_VR_OBJECT_INDEX_UI','SE421_MODEL_VR_MENU_STABILITY_START',
 'SE435_MODEL_VR_GRAB_GIZMO_START','SWYRL_ENGINE_MODEL_VR_GRAB_GIZMO',
 'se435PreviousGizmoFrame','se435PreviousBeginGrab',
 'SE436_SATCHEL_CAVITY_START','SE436_VR_CUBE_EXTRUDE_START','Inset and extrude one hollow body',
 'window.SWYRL_E_SATCHEL_CAVITY_436?.makeGhost(group)','SWYRL_ENGINE_MODEL_VR_CUBE_EXTRUDE_436',
 'SE437_SHEEP_TERRITORY_CAPTURE_START','se437BaseCandidates(unit)',
 'se437BaseAllowed(unit,p)','se437BuildAllowed(unit,x,z)',
 'SE438_ENGINE_SIMULATION_RENDER_BRIDGE_START',
 'se438Route(unit,unit.pos,aim,radius)',
 'window.SWYRL_ENGINE_RENDER_BRIDGE_438',
 'window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_437=',
 'SE439_SHEEP_CAPTURE_PURSUIT_START','se439DirectChase(unit,aim,context)?','window.SWYRL_ENGINE_SHEEP_CAPTURE_PURSUIT_439']:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.439';source.version=11.439;")==5
for name in ['model_vr_grab_gizmo_v11_435.js','se436_satchel_cavity.js','se436_vr_cube_extrude.js','sheep_territory_capture_v11_437.js','engine_simulation_render_bridge_v11_438.js','sheep_capture_pursuit_v11_439.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
for name in ['sheep_visual_batch_v11_434.js','sheep_visible_frame_recovery_v11_434.js','sheep_xray_policy_v11_434.js','engine_editor_shadow_cache_v11_434.js']:
 p=ROOT/'runtime'/name;subprocess.run(['node','--check',str(p)],check=True);s=p.read_text();assert 'requestAnimationFrame(' not in s and 'setAnimationLoop(' not in s and 'getViewerPose(' not in s
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for name in ['test_sheep_quest_ai_frame_budget_v11_411.cjs','test_sheep_congestion_budget_v11_419.cjs','test_sheep_vr_frame_cadence_v11_379.cjs','sheep_visible_recovery_v11_434.cjs','test_sheep_territory_capture_v11_437.cjs','test_engine_render_bridge_v11_438.cjs','test_sheep_capture_pursuit_v11_439.cjs']:
 subprocess.run(['node',str(ROOT/'tests'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_camera_preferences_preserved_v11_439.mjs'),str(out/'index.html')],check=True)
if A.three_module:
 three=Path(A.three_module).resolve();assert three.is_file()
 subprocess.run(['node',str(ROOT/'tests/sheep_visual_batch_v11_434.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/engine_editor_shadow_cache_v11_434.mjs'),str(three)],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_vr_grab_gizmo_v11_435.mjs'),str(three)],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_satchel_cavity_v11_436.mjs'),str(three),str(out/'index.html')],check=True)
s=json.loads((out/'SOURCE.json').read_text())
for k,v in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',len(data)),('finalSha256',m['finalSha256'])]:assert s[k]==v,k
assert len(s['assets'])==77
for name,receipt in s['assets'].items():
 b=(out/name).read_bytes();assert len(b)==receipt['bytes'];assert hashlib.sha256(b).hexdigest()==receipt['sha256'],name
assert len([p for p in out.rglob('*') if p.is_file()])==81
if A.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text());assert request['releaseVersion']=='v11.439' and request['deployMarker']==marker;assert request['sourceIntegritySha256']==m['finalSha256'];assert re.fullmatch('[0-9a-f]{40}',request['sourceCommit'])
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.439','bytes':len(data),'sha256':m['finalSha256'],'patches':416,'assets':77,'physicalQuestAcceptance':False},indent=2))
