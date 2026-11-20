#!/usr/bin/env python3
"""§E v11.531: native full-project account save, responsive My Projects, all prior VR and model regressions."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((root/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.531'
assert m['finalBytes']>1000000 and len(m['finalSha256'])==64, 'Unsealed v11.531 source cannot be released'
assert m['finalArtifact']=='swyrl_engine_v11_531.html'
assert len(m['patches'])==508
assert m['patches'][-31:-1]==[
 'patches/v11_501_uv_diagnostic_exports.py',
 'patches/v11_502_uv_touch_resize.py',
 'patches/v11_503_uv_island_atlas.py',
 'patches/v11_504_smooth_witch_hat.py',
 'patches/v11_505_action_prerequisites.py',
 'patches/v11_506_uv_button_ownership.py',
 'patches/v11_507_model_tool_rail_recovery.py',
 'patches/v11_508_uv_degenerate_preview.py',
 'patches/v11_509_rail_reexpand.py',
 'patches/v11_510_cone_aware_uv.py',
 'patches/v11_511_model_dock_visibility.py',
 'patches/v11_512_vr_trigger_gizmo.py',
 'patches/v11_513_rig_skin_weights.py',
 'patches/v11_514_native_xr_rig.py',
 'patches/v11_515_spatial_menu_controller.py',
 'patches/v11_516_rig_precision.py',
 'patches/v11_517_xr_project_rotation.py',
 'patches/v11_518_quest_rig_cache.py',
 'patches/v11_519_quest_browser_selection.py',
 'patches/v11_520_quest_interaction_qa.py',
 'patches/v11_521_model_labs_persistent_history.py',
 'patches/v11_522_sculpt_brush_menu.py',
 'patches/v11_523_sculpt_direction_cleanup.py',
 'patches/v11_524_select_menu_cleanup.py',
 'patches/v11_525_display_menu_groups.py',
 'patches/v11_526_create_menu_cleanup.py',
 'patches/v11_527_draw_menu_cleanup.py',
 'patches/v11_528_immersive_ux_account_repair.py',
  'patches/v11_529_native_account_browser_library.py',
  'patches/v11_530_quest_gizmo_controller_menu.py']
assert m['patches'][-1]=='patches/v11_531_quest_menu_gizmo_account.py'
for rel in ('runtime/model_edit_journal_v11_521.js','runtime/model_lab_native_bridge_v11_521.js','runtime/model_vr_labs_v11_521.js'):
 subprocess.run(['node','--check',str(root/rel)],check=True)
subprocess.run(['node',str(root/'tests/model_project_edit_journal_v11_521.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_vr_controller_palette_v11_530.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_vr_quest_interactions_v11_531.js')],check=True)
for rel in ('runtime/model_vr_trigger_gizmo_v11_512.js',
            'runtime/model_vr_browser_pick_v11_512.js',
            'runtime/model_display_platform_v11_512.js'):
 subprocess.run(['node','--check',str(root/rel)],check=True)
subprocess.run(['node',str(root/'tests/model_vr_trigger_gizmo_v11_512.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_browser_platform_v11_512.cjs')],check=True)
for rel in ('runtime/model_rig_skin_math_v11_513.js','runtime/model_rig_weight_studio_v11_513.js','runtime/model_vr_native_rig_v11_514.js','runtime/model_vr_spatial_polish_v11_515.js','runtime/model_rig_precision_v11_516.js','runtime/model_vr_project_library_v11_517.js','runtime/model_vr_project_browser_v11_517.js','runtime/model_rig_scope_access_v11_518.js','runtime/engine_cloud_revision_cache_v11_518.js','runtime/model_quest_browser_transform_v11_519.js','runtime/model_vr_interaction_repair_v11_520.js','runtime/model_quest_browser_picking_v11_520.js'):
 subprocess.run(['node','--check',str(root/rel)],check=True)
for rel in ('tests/model_rig_skin_weight_v11_513.cjs','tests/model_rig_persisted_skin_v11_513.cjs','tests/model_rig_precision_v11_516.cjs','tests/model_vr_project_library_v11_517.cjs','tests/model_vr_rotation_isolation_v11_517.cjs','tests/engine_cloud_revision_cache_v11_518.cjs','tests/model_quest_browser_transform_v11_519.cjs'):
 subprocess.run(['node',str(root/rel)],check=True)
subprocess.run(['node','--check',str(root/'runtime/sorting_hat_sculpted_v11_497.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_studio_polish_v11_499.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_connected_math_v11_500.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_rig_connected_edit_v11_500.js')],check=True)
subprocess.run(['node',str(root/'tests/model_rig_connected_v11_500.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_rig_workspace_v11_490.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_heatmap_export_v11_501.js')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_heatmap_export_v11_501.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_touch_resize_v11_502.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_island_math_v11_503.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_island_ui_v11_503.js')],check=True)
subprocess.run(['node','--check',str(root/'runtime/smooth_witch_hat_v11_504.js')],check=True)
subprocess.run(['node',str(root/'tests/smooth_witch_hat_v11_504.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_island_atlas_v11_503.cjs')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_action_prerequisites_v11_505.js')],check=True)
subprocess.run(['node',str(root/'tests/model_action_prerequisites_v11_505.cjs')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_touch_resize_v11_502.cjs')],check=True)
subprocess.run(['node',str(root/'tests/sorting_hat_sculpted_v11_497.cjs')],check=True)
subprocess.run([sys.executable,str(root/'tests/sorting_hat_single_mesh_v11_485.py')],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']
s=raw.decode('utf8')
for needle in (
 '<title>§wyrl§ Engine · Maker v11.531</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_MENU_GIZMO_ACCOUNT',
 'data-project-template="smooth-witch-hat"',
 'SE504_SMOOTH_WITCH_HAT_END',
 'SWYRL_ENGINE_SMOOTH_WITCH_HAT_504',
 'data-project-template="sorting-hat-sculpted"',
 'data-project-template="sorting-hat"',
 'SWYRL_ENGINE_SORTING_HAT_SCULPTED_497',
 'SE483_SORTING_HAT_END',
 'SWYRL_ENGINE_MINI_STUDIOS_496',
 'SWYRL_ENGINE_RIG_POLISH_499',
 'new THREE.SphereGeometry(1,12,9)',
 'new THREE.CylinderGeometry(.50,.86,1,9,1)',
 'data-se499-rig-kind=object',
 'SWYRL_ENGINE_RIG_CONNECTED_MATH_500',
 'SWYRL_ENGINE_RIG_CONNECTED_EDIT_500',
 'se500WeightsCount','se500LockLength','syncRestTransform',
 'SE501_UV_HEATMAP_EXPORT_START','SWYRLZ_E_UV_HEATMAP_EXPORT_501',
 'data-se501-export="heat"','data-se501-export="overlay"',
 'SE502_UV_TOUCH_RESIZE_START','se502InstallResizable(popup)',
 'se502UVMax','se502-uv-se','se502ToggleMax',
 'SE503_UV_ISLAND_MATH_START','SE503_UV_ISLAND_UI_START',
 'SE510_CONE_AWARE_UV_START','se510ConeUV.compare',
 'se503AtlasPrepare','se503AtlasApply','SE505_ACTION_PREREQUISITES_START',
 'SWYRLZ_E_REQUIREMENTS_505','SE511_MODEL_DOCK_VISIBILITY_END',
 'SE512_MODEL_VR_TRIGGER_GIZMO_END','SE512_QUEST_BROWSER_PICK_END',
 'SE512_DISPLAY_PLATFORM_END','sculpt-direction','sculpt-falloff',
 'platform-toggle','se512QuestTapPick','se512GizmoInput',
  'SE513_RIG_SKIN_MATH_END','SE513_RIG_WEIGHT_STUDIO_END',
  'swyrl-explicit-skin-v1','se513SkinMath','se513WeightStudio',
  'SE514_NATIVE_XR_RIG_END','SWYRL_ENGINE_IMMERSIVE_RIG_514',
  'se514RigXR.beforeDispatch','rig-weights','rig-pose-x-plus',
  'SE515_SPATIAL_VR_POLISH_END','SWYRL_ENGINE_VR_SPATIAL_POLISH_515',
  "name.includes('background')?8380", "['labs','Labs','labs']", "['rig','Bones','rig']", "['transform-menu','Transform','mesh']", 
  "['rig-weights','Weight painting']", 'se515SpatialPolish', 'se362PartCenter',
  'SE516_RIG_PRECISION_END','se516SkinPrecision','rig-select-mode',
  'SE517_PROJECT_LIBRARY_END',
 'SE522_SCULPT_BRUSH_MENU','SE522_SCULPT_SETTINGS','SE523_SCULPT_DIRECTION','SE524_SELECT_LASSO_SETTINGS','SE525_DISPLAY_DIVIDER','SE525_DISPLAY_NATIVE_PANELS','SE526_CREATE_DIVIDER','SE526_CREATE_CONTEXT','SE527_DRAW_ACTIONS','SE527_DRAW_STATE','SE527_DRAW_OUTLINE_ELIGIBILITY',
 'SE528_XR_PROJECT_DIALOG_START','SE528_XR_RAY_AND_PARAMETER_CONTROLS_START','SE528_ACCOUNT_PROJECT_REPAIR_START',
  'SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START','SE529_MY_PROJECTS_BROWSER_UI_START','SE529_MY_PROJECTS_BROWSER_CSS_START',
 'SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END','SE531_QUEST_MENU_GIZMO_ACCOUNT_END',
 'controllerFollowMenu:true',
 'SE521_PERSISTENT_EDIT_JOURNAL_END','SE521_MODEL_LAB_NATIVE_BRIDGE_END','SE521_MODEL_VR_LABS_END','swyrl-edit-journal-v1',
 'SE518_RIG_SCOPE_ACCESS_END','SE518_REVISION_CACHE_END','SE519_QUEST_BROWSER_TRANSFORM_END','SE520_QUEST_BROWSER_PICK_END','SE520_VR_INTERACTION_REPAIR_END','SE517_XR_PROJECT_BROWSER_END','se517XRProjects','project-open'
):assert needle in s,needle
subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_controller_palette_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_sculpt_menu_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_select_menu_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_display_menu_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_create_menu_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_draw_menu_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/model_vr_owner_qa_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/project_account_browser_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/uv_degenerate_regression_v11_531.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(root/'runtime/model_uv_cone_metric_v11_510.js')],check=True)
subprocess.run(['node',str(root/'tests/model_uv_cone_aware_v11_510.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/sorting_hat_proportion_v11_498.cjs'),str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,value in [('sourceVersion',m['name']),('finalBytes',len(raw)),
                  ('finalSha256',m['finalSha256']),('patches',m['patches'])]:
 assert receipt[key]==value,key
scene=json.loads((out/'scenes/model-atelier-sorting-hat.swyrl.json').read_text('utf8'))
assert scene['project']['canonicalId']=='sorting-hat'
assert len(scene['project']['modelAtelier']['parts'])==1
if args.request:
 req=json.loads((root/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.531'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_GIZMO_CONTROLLER_MENU'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert len(req.get('sourceCommit',''))==40
print('SE531_SOURCE_VERIFIED',json.dumps({'version':'v11.531','patches':508,
 'bytes':len(raw),'sha256':m['finalSha256'],
 'nativeSingleMesh':True,'originalStarterPreserved':True,'rigStudioUIIsolated':True,'connectedRigAndWeights':True,'uvDiagnosticExports':True,'uvTouchResize':True,'uvIslandAtlas':True}),flush=True)
