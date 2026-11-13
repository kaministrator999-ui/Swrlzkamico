#!/usr/bin/env python3
"""Verify source-sealed touch and VR transform-handle accessibility.

The deployment path rebuilds and verifies exact source, syntax and packaged
assets. Focused native modeling/camera tests can additionally run against an
already available Three r169 module. No dependency is downloaded here and no
unrelated browser/game regression suite is launched.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v11.433'
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_433_CAMERA_PREFERENCES_TOUCH_GIZMOS'
ap = argparse.ArgumentParser()
ap.add_argument('--output', required=True)
ap.add_argument('--request', action='store_true')
ap.add_argument('--three-module', default=os.environ.get('SWYRLZ_THREE_MODULE'),
                help='Optional existing Three r169 ES module for native modeling/camera tests')
args = ap.parse_args()
m = json.loads((ROOT / 'source-manifest.json').read_text())
assert m['name'] == '§wyrl§ Engine ' + VERSION
assert m['finalArtifact'] == 'swyrl_engine_v11_433.html'
assert len(m['patches']) == 410
assert m['patches'][-5:] == [
    'patches/v11_425_level_observer_feedback_guard.py',
    'patches/v11_430_model_studio_visual_workshop.py',
    'patches/v11_431_model_gizmo_access.py',
    'patches/v11_432_mobile_camera_orbit.py',
    'patches/v11_433_model_camera_preferences.py']
assert m['finalBytes'] > 9_623_744
assert re.fullmatch('[0-9a-f]{64}', m['finalSha256'])

out = Path(args.output).resolve()
subprocess.run([sys.executable, str(ROOT / 'build_space.py'), '--output', str(out)], check=True)
data = (out / 'index.html').read_bytes()
assert data == (out / 'modeler.html').read_bytes()
assert len(data) == m['finalBytes']
assert hashlib.sha256(data).hexdigest() == m['finalSha256']
html = data.decode()
for token in [
    MARKER, 'SE433_CAMERA_PREFS_START', 'se433CameraPrefs.install(panel);',
    'touchRadius:28,mouseRadius:12', 'window.SWYRL_ENGINE_MODEL_GIZMO_ACCESS=ModelAtelier.gizmoAccess;',
    'gizmoAccess:se431GizmoAccess', 'se431GizmoAccess.refresh();', 'se431GizmoAccess.pick(e)', 'SE431_MODEL_GIZMO_ACCESS_START', 'SE431_MODEL_VR_GIZMO_ACCESS_START', "window.SWRLZ_FORGE_BUILD={version:'v11.433'",
    '<title>§wyrl§ Engine · Maker v11.433</title>',
    'workshop:se430ModelWorkshop', 'camera:se430ModelCamera',
    'window.SWYRL_MODEL_TEACHING=Object.freeze',
    'SE430_MODEL_VR_MANUAL_WORKSHOP_START', 'SE430_MODEL_VR_VISUAL_TEACHING',
    'SE410_ACCESSORY_GEOMETRY_START', 'SE410_MODEL_ACCESSORY_BRIDGE_START',
    'SE410_MODEL_VR_ACCESSORY_WORKSHOP_START', 'SE410_MODEL_VR_ACCESSORY_UI',
    'vrAccessory:se410ModelAccessory', 'se410AccessoryFrame(s,dt)',
    '...se410AccessoryUI(),...se430VRUI(),creationActive:',
    'SE390_MODEL_VR_QUICK_CREATE_START', 'SE390_MODEL_VR_GRAB_POSE_START',
    'SE390_MODEL_VR_FLUENT_TOOLS_START', 'SE390_MODEL_VR_FLUENT_UI',
    'SE390_MODEL_VR_HOTKEY_HINTS_START', 'vrCreate:se390ModelCreate',
    'se390CreationFrame(s,dt)', 'se390BeginGrab(record,purpose,pose)',
    'SE376_VR_SELECTOR_LASSO_START', 'SE374_MODEL_VR_OWNER_FEEDBACK_START',
    'SE372_MODEL_VR_PHASE1_START', 'SWYRL_ENGINE_ADVANCED_GRAPHICS_380',
    'SWYRL_ENGINE_SHEEP_XR_GUEST_381', 'SWYRL_ENGINE_SHEEP_VR_Y_MENU_391',
    'se378Blockout', 'se366ImportAuthored', 'se356ApplyCameraOrbit',
    'SE362_CONTROLLER_HINTS_START', 'SWYRL_ENGINE_SAFE_PROJECTS_371',
    'SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411', 'se411PlanSheepBuild(unit)',
    'se411ChooseSheepBase(unit)', 'se411Pending=se411Active()']:
    assert token in html, token
for token in ['SWYRL_ENGINE_TUTORIAL_412', 'SE413_SATCHEL_VR_QUEST_START', 'SE414_SATCHEL_NATIVE_TOOL_REFERENCES_START', 'drawGuideIcon:(ctx,action,x,y,size,color)', 'SE415_MODEL_VR_ICONOGRAPHY', 'SE416_SATCHEL_ACADEMY_START', 'SE416_SATCHEL_VR_COACH_START', 'SE416_SATCHEL_NATIVE_BRIDGE_START', 'highlightTutorialAction:', 'SE417_MODEL_VR_OBJECT_INDEX_UI', 'SE417_MODEL_VR_OBJECT_INDEX_START', 'SE421_MODEL_VR_MENU_STABILITY_START', 'SE422_PROJECT_TUTORIAL_HUB_RECOVERY_START', 'SE423_PROJECT_MENU_RECOVERY_START', 'SE423_LEVEL_SELECTOR_RECOVERY_START', 'SE424_SHEEP_MENU_SCOPE_START', 'SE425_LEVEL_UI_OBSERVER_GUARD', 'SWYRL_ENGINE_SHEEP_TEAM_SETUP_416', 'SE419_SHEEP_CONGESTION_BUDGET_START', 'SWYRL_ENGINE_SHEEP_SETUP_MENU_420']:
    assert token in html, token
assert html.count("const se420PreviousShow=se416Show;")==1
assert "bar.nextSibling!==currentPlay" not in html
for marker in [
    'SE430_MODEL_MESH_OPERATIONS_START', 'SE430_MODEL_WORKSHOP_BRIDGE_START',
    'SE430_MODEL_STUDIO_CAMERA_START', 'SE430_MODEL_TEACHING_START',
    'SE430_MODEL_STUDIO_CAMERA_STYLE_START',
    'SE430_MODEL_VR_MANUAL_WORKSHOP_START', 'SE430_MODEL_VR_VISUAL_TEACHING',
    'SE410_ACCESSORY_GEOMETRY_START', 'SE410_MODEL_ACCESSORY_BRIDGE_START',
    'SE410_MODEL_VR_ACCESSORY_WORKSHOP_START', 'SE410_MODEL_VR_ACCESSORY_UI']:
    assert html.count(marker) == 1, marker
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.433';source.version=11.433;") == 5
subprocess.run([sys.executable, str(ROOT / 'scripts/check_inline_js_syntax_v11_266.py'),
                str(out / 'index.html')], check=True)
subprocess.run(['node', str(ROOT / 'tests/model_camera_preferences_v11_433.mjs'), str(out / 'index.html')], check=True)

runtime_files = [
    'model_camera_preferences_v11_433.js',
    'model_gizmo_access_v11_431.js', 'model_vr_gizmo_access_v11_431.js',
    'model_mesh_operations_v11_430.js', 'model_studio_workshop_bridge_v11_430.js',
    'model_studio_camera_v11_430.js', 'model_studio_teaching_v11_430.js',
    'model_studio_beginner_ui_v11_430.js', 'model_studio_vr_ui_v11_430.js',
    'model_vr_manual_workshop_v11_430.js',
    'model_vr_quick_create_v11_390.js', 'model_vr_grab_v11_390.js',
    'model_vr_fluent_tools_v11_390.js', 'model_vr_hotkey_hints_v11_390.js',
    'model_vr_input_profile_v11_390.js',
    'model_accessory_geometry_v11_410.js', 'model_accessory_bridge_v11_410.js',
    'model_vr_accessory_workshop_v11_410.js',
    'sheep_vr_y_tools_radial_v11_391.js', 'sheep_quest_bot_frame_budget_v11_411.js']
for name in runtime_files:
    p = ROOT / 'runtime' / name
    subprocess.run(['node', '--check', str(p)], check=True)
    source = p.read_text()
    assert 'requestAnimationFrame(' not in source, name
    assert 'setAnimationLoop(' not in source, name

subprocess.run(['node', str(ROOT / 'tests/model_component_selection_v11_430.mjs'), str(out / 'index.html')], check=True)
subprocess.run(['node', str(ROOT / 'tests/model_project_clone_identity_v11_430.mjs'), str(out / 'index.html')], check=True)
subprocess.run(['node', str(ROOT / 'tests/model_studio_teaching_v11_430.mjs')], check=True)

# Preserve the existing bounded deployment checks for the current game/input
# integrations. This does not launch their full historical browser suites.
for name in ['test_sheep_vr_y_menu_v11_391.cjs', 'test_sheep_quest_ai_frame_budget_v11_411.cjs']:
    subprocess.run(['node', str(ROOT / 'tests' / name)], check=True)
native_tests = 'NOT_REQUESTED'
if args.three_module:
    three = Path(args.three_module).expanduser().resolve()
    assert three.is_file(), 'Local Three ES module is missing: ' + str(three)
    for name in ['model_mesh_operations_v11_430.mjs',
                 'model_studio_workshop_bridge_v11_430.mjs',
                 'model_studio_camera_v11_430.mjs',
                 'model_vr_ui_preservation_v11_430.mjs',
                 'model_gizmo_access_v11_431.mjs',
                 'model_vr_gizmo_access_v11_431.mjs']:
        command=['node', str(ROOT / 'tests' / name), str(three)]
        if name=='model_gizmo_access_v11_431.mjs':
            command.append(str(out/'index.html'))
        subprocess.run(command, check=True)
    native_tests = 'PASS'

receipt = json.loads((out / 'SOURCE.json').read_text())
for key, want in [('sourceVersion', m['name']), ('patches', m['patches']),
                  ('finalBytes', m['finalBytes']), ('finalSha256', m['finalSha256'])]:
    assert receipt[key] == want, key
assert len(receipt['assets']) == 77
for name, info in receipt['assets'].items():
    content = (out / name).read_bytes()
    assert len(content) == info['bytes'], name
    assert hashlib.sha256(content).hexdigest() == info['sha256'], name
assert len([p for p in out.rglob('*') if p.is_file()]) == 81
if args.request:
    request = json.loads((ROOT / 'DEPLOY_REQUEST.json').read_text())
    assert request['releaseVersion'] == VERSION
    assert request['deployMarker'] == MARKER
    assert request['sourceIntegritySha256'] == m['finalSha256']
    assert re.fullmatch('[0-9a-f]{40}', request['sourceCommit'])
print(json.dumps({'status': 'SEALED_SOURCE_VERIFIED', 'version': VERSION,
                  'patches': len(m['patches']), 'bytes': len(data),
                  'sha256': m['finalSha256'], 'assets': 77,
                  'nativeWorkshopTests': native_tests,
                  'physicalHeadsetAcceptance': False}, indent=2))
