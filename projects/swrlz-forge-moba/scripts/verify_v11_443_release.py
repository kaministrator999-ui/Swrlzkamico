#!/usr/bin/env python3
"""Sealed modeling-tool release, native transactions and source preservation."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--output',required=True);P.add_argument('--request',action='store_true');P.add_argument('--three-module');A=P.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text());assert m['name']=='§wyrl§ Engine v11.443';assert m['finalArtifact']=='swyrl_engine_v11_443.html';assert len(m['patches'])==420
assert m['patches'][-13:]==['patches/v11_431_model_gizmo_access.py','patches/v11_432_mobile_camera_orbit.py','patches/v11_433_model_camera_preferences.py','patches/v11_434_sheep_crowded_vr.py','patches/v11_435_model_vr_grab_gizmo.py','patches/v11_436_cube_extrude_satchel.py','patches/v11_437_sheep_territory_capture.py','patches/v11_438_engine_simulation_render_bridge.py','patches/v11_439_sheep_capture_pursuit.py','patches/v11_440_model_tools_validation.py','patches/v11_441_satchel_vr_workflow.py','patches/v11_442_satchel_mobile_dialog.py','patches/v11_443_model_vr_vertical_dock.py']
out=Path(A.output).resolve();subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes();assert data==(out/'modeler.html').read_bytes();assert len(data)==m['finalBytes'];assert hashlib.sha256(data).hexdigest()==m['finalSha256'];html=data.decode()
marker='SWYRL_ENGINE_DEPLOY_MARKER: V11_443_VR_VERTICAL_TOOL_DOCK'
for token in [marker,"window.SWRLZ_FORGE_BUILD={version:'v11.443'",'<title>§wyrl§ Engine · Maker v11.443</title>',
 'const occluded=se434XrayEligible(unit,s)&&','renderer.xr?.isPresenting?renderer.xr.getCamera(camera):',
 'SE434_SHEEP_VISUAL_BATCH_START','SE434_SHEEP_VISIBLE_FRAME_RECOVERY_START','SE434_SHEEP_XRAY_POLICY_START','SE434_ENGINE_EDITOR_SHADOW_CACHE_START',
 'SE433_CAMERA_PREFS_START','se433CameraPrefs.install(panel);','touchRadius:28,mouseRadius:12','se411PlanSheepBuild(unit)','SE419_SHEEP_CONGESTION_BUDGET_START',
 'se265BatchBuilding(building)','SE425_LEVEL_UI_OBSERVER_GUARD','SE430_MODEL_VR_VISUAL_TEACHING','SE431_MODEL_VR_GIZMO_ACCESS_START',
 'SE417_MODEL_VR_OBJECT_INDEX_UI','SE421_MODEL_VR_MENU_STABILITY_START',
 'SE435_MODEL_VR_GRAB_GIZMO_START','SWYRL_ENGINE_MODEL_VR_GRAB_GIZMO',
 'se435PreviousGizmoFrame','se435PreviousBeginGrab',
 'SE436_SATCHEL_CAVITY_START','SE436_VR_CUBE_EXTRUDE_START','Inset and hollow the same body','SE441_SATCHEL_LESSON_START','SE441_SATCHEL_WORKFLOW_START','SE441_VISIBLE_QUEST_INPUT','SE441_QUEST_GRIP_INPUT','SE441_QUEST_TRIGGER_INPUT','SE441_NATIVE_GHOST_ROOT','SE441_QUEST_SIDE_PLACEMENT','SE442_SATCHEL_DIALOG_START','SE442_SATCHEL_FLAT_LESSON_START','SE442_TRANSFORM_DISCOVERY','SE442_VALID_NUMERIC_PRECISION','one-body-v1','SE443_MODEL_VR_VERTICAL_DOCK_START','SWYRL_ENGINE_MODEL_VR_DOCK_443',
 'window.SWYRL_E_SATCHEL_CAVITY_436?.makeGhost(group)','SWYRL_ENGINE_MODEL_VR_CUBE_EXTRUDE_436',
 'SE440_NATIVE_OUTLINE_ROUTE','SE440_TOOL_PREVIEW_IDENTITY','SE440_TOUCH_COMPONENT_BORDER','SE440_ASSEMBLY_MENU_SYNC_START','SE440_CURRENT_CONTROLLER_POSE','SE440_VISIBLE_MENU_TARGETS',
 'SE437_SHEEP_TERRITORY_CAPTURE_START','se437BaseCandidates(unit)',
 'se437BaseAllowed(unit,p)','se437BuildAllowed(unit,x,z)']:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.443';source.version=11.443;")==5
for name in ['model_vr_dock_v11_443.js','model_vr_grab_gizmo_v11_435.js','se436_satchel_cavity.js','se436_vr_cube_extrude.js','sheep_territory_capture_v11_437.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
for name in ['sheep_visual_batch_v11_434.js','sheep_visible_frame_recovery_v11_434.js','sheep_xray_policy_v11_434.js','engine_editor_shadow_cache_v11_434.js']:
 p=ROOT/'runtime'/name;subprocess.run(['node','--check',str(p)],check=True);s=p.read_text();assert 'requestAnimationFrame(' not in s and 'setAnimationLoop(' not in s and 'getViewerPose(' not in s
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for name in ['test_sheep_quest_ai_frame_budget_v11_411.cjs','test_sheep_congestion_budget_v11_419.cjs','test_sheep_vr_frame_cadence_v11_379.cjs','sheep_visible_recovery_v11_434.cjs','test_sheep_territory_capture_v11_437.cjs','test_engine_render_bridge_v11_438.cjs','test_sheep_capture_pursuit_v11_439.cjs']:
 subprocess.run(['node',str(ROOT/'tests'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_camera_preferences_preserved_v11_442.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_motion_menu_v11_440.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_satchel_browser_preservation_v11_442.mjs'),str(out/'index.html')],check=True)
if A.three_module:
 three=Path(A.three_module).resolve();assert three.is_file()
 subprocess.run(['node',str(ROOT/'tests/sheep_visual_batch_v11_434.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/engine_editor_shadow_cache_v11_434.mjs'),str(three)],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_vr_grab_gizmo_v11_435.mjs'),str(three)],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_satchel_cavity_preserved_v11_442.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_satchel_workflow_v11_441.mjs'),str(three)],check=True)
 for name in ['model_vr_native_tools_v11_350.mjs','model_vr_sculpt_draw_v11_350.mjs',
  'model_vr_fluent_tools_v11_390.mjs','model_vr_grab_v11_390.mjs','model_vr_quick_create_v11_390.mjs',
  'model_vr_input_profile_v11_390.mjs','model_accessory_geometry_v11_410.mjs','model_accessory_bridge_v11_410.mjs',
  'model_mesh_operations_v11_430.mjs','model_studio_workshop_bridge_v11_430.mjs','model_studio_camera_v11_430.mjs',
  'model_vr_gizmo_access_v11_431.mjs']:
  subprocess.run(['node',str(ROOT/'tests'/name),str(three)],check=True)
 for name in ['model_component_selection_v11_430.mjs','model_project_clone_identity_v11_430.mjs']:
  subprocess.run(['node',str(ROOT/'tests'/name),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_gizmo_access_v11_431.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_tool_routing_v11_440.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_touch_components_v11_440.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_controller_frame_v11_440.mjs'),str(three),str(out/'index.html')],check=True)
 subprocess.run(['node',str(ROOT/'tests/model_studio_teaching_v11_430.mjs')],check=True)

s=json.loads((out/'SOURCE.json').read_text())
for k,v in [('sourceVersion',m['name']),('patches',m['patches']),('finalBytes',len(data)),('finalSha256',m['finalSha256'])]:assert s[k]==v,k
assert len(s['assets'])==77
for name,receipt in s['assets'].items():
 b=(out/name).read_bytes();assert len(b)==receipt['bytes'];assert hashlib.sha256(b).hexdigest()==receipt['sha256'],name
assert len([p for p in out.rglob('*') if p.is_file()])==81
if A.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text());assert request['releaseVersion']=='v11.443' and request['deployMarker']==marker;assert request['sourceIntegritySha256']==m['finalSha256'];assert re.fullmatch('[0-9a-f]{40}',request['sourceCommit'])
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.443','bytes':len(data),'sha256':m['finalSha256'],'patches':len(m['patches']),'assets':77,'physicalQuestAcceptance':False},indent=2))
