#!/usr/bin/env python3
"""Verify the exact source-sealed §E satchel tutorial, stationary Quest and inherited runtimes.

The deploy path checks source integrity, syntax, packaging and the preserved
Quest Y shortcut. Native geometry/transaction tests can also be run locally
with --three-module or SWYRLZ_THREE_MODULE pointing to Three 0.169.0's ES module.
No external dependency is downloaded by this verifier.
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
VERSION = 'v11.416'
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_416_MODEL_VR_OBJECT_INDEX'
ap = argparse.ArgumentParser()
ap.add_argument('--output', required=True)
ap.add_argument('--request', action='store_true')
ap.add_argument('--three-module', default=os.environ.get('SWYRLZ_THREE_MODULE'),
                help='Optional local Three 0.169.0 ES module for native accessory tests')
args = ap.parse_args()
m = json.loads((ROOT / 'source-manifest.json').read_text())
assert m['name'] == '§wyrl§ Engine ' + VERSION
assert m['finalArtifact'] == 'swyrl_engine_v11_415.html'
assert len(m['patches']) == 397
assert m['patches'][-7:] == [
    'patches/v11_410_model_vr_accessory_workshop.py',
    'patches/v11_411_sheep_quest_ai_frame_budget.py',
    'patches/v11_412_apprentice_satchel_tutorial.py',
    'patches/v11_413_satchel_vr_tutorial.py',
    'patches/v11_414_satchel_native_tool_button_references.py',
    'patches/v11_415_model_vr_iconography.py',
    'patches/v11_416_model_vr_object_index.py']
assert m['finalBytes'] > 9_675_331
assert re.fullmatch('[0-9a-f]{64}', m['finalSha256'])

out = Path(args.output).resolve()
subprocess.run([sys.executable, str(ROOT / 'build_space.py'), '--output', str(out)], check=True)
data = (out / 'index.html').read_bytes()
assert data == (out / 'modeler.html').read_bytes()
assert len(data) == m['finalBytes']
assert hashlib.sha256(data).hexdigest() == m['finalSha256']
html = data.decode()
for token in [
    MARKER, "window.SWRLZ_FORGE_BUILD={version:'v11.416'",
    '<title>§wyrl§ Engine · Maker v11.416</title>',
    'SE410_ACCESSORY_GEOMETRY_START', 'SE410_MODEL_ACCESSORY_BRIDGE_START',
    'SE410_MODEL_VR_ACCESSORY_WORKSHOP_START', 'SE410_MODEL_VR_ACCESSORY_UI',
    'vrAccessory:se410ModelAccessory', 'se410AccessoryFrame(s,dt)',
    '...se410AccessoryUI(),creationActive:',
    'SWYRL_ENGINE_TUTORIAL_412', 'se412Tutorials', 'se412Panel',
    'SE413_SATCHEL_VR_QUEST_START', 'SWYRL_ENGINE_TUTORIAL_VR_413',
    'se413PaintDemo', 'se413Examples', 'se413InstallSatchelVR',
    'SE414_SATCHEL_NATIVE_TOOL_REFERENCES_START', 'SWYRL_E_SATCHEL_BUTTON_GUIDE_414',
    'drawGuideIcon:(ctx,action,x,y,size,color)', 'se414ToolGuide',
    'SE415_MODEL_VR_ICONOGRAPHY', 'se414Icons',
    'SE416_MODEL_VR_OBJECT_INDEX_UI', 'SE416_MODEL_VR_OBJECT_INDEX_START',
    'se416IndexAction(action,record)', 'se416IndexState(s,entries,selectedIds)',
    'se416UpdateHighlights(s,entries,selectedIds)', 'se416DisposeHighlights(s)',
    'SE390_MODEL_VR_QUICK_CREATE_START', 'SE390_MODEL_VR_GRAB_POSE_START',
    'SE390_MODEL_VR_FLUENT_TOOLS_START', 'SE390_MODEL_VR_FLUENT_UI',
    'SE390_MODEL_VR_HOTKEY_HINTS_START', 'vrCreate:se390ModelCreate',
    'se390CreationFrame(s,dt)', 'se390BeginGrab(record,purpose,pose)',
    'SE376_VR_SELECTOR_LASSO_START', 'SE374_MODEL_VR_OWNER_FEEDBACK_START',
    'SE372_MODEL_VR_PHASE1_START', 'SWYRL_ENGINE_ADVANCED_GRAPHICS_380',
    'SWYRL_ENGINE_SHEEP_XR_GUEST_381', 'SWYRL_ENGINE_SHEEP_VR_Y_MENU_391',
    'se378Blockout', 'se366ImportAuthored', 'se356ApplyCameraOrbit',
    'SE362_CONTROLLER_HINTS_START', 'SWYRL_ENGINE_SAFE_PROJECTS_371']:
    assert token in html, token
for token in ['SWYRL_ENGINE_SHEEP_AI_FRAME_BUDGET_411','se411PlanSheepBuild(unit)','se411ChooseSheepBase(unit)','se411Pending=se411Active()']:
    assert token in html, token
for marker in ['SE410_ACCESSORY_GEOMETRY_START', 'SE410_MODEL_ACCESSORY_BRIDGE_START',
               'SE410_MODEL_VR_ACCESSORY_WORKSHOP_START', 'SE410_MODEL_VR_ACCESSORY_UI']:
    assert html.count(marker) == 1, marker
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.416';source.version=11.415;") == 5
subprocess.run([sys.executable, str(ROOT / 'scripts/check_inline_js_syntax_v11_266.py'),
                str(out / 'index.html')], check=True)
runtime_files = [f'{name}_v11_390.js' for name in [
    'model_vr_quick_create', 'model_vr_grab', 'model_vr_fluent_tools',
    'model_vr_hotkey_hints', 'model_vr_input_profile', 'model_studio_vr_ui']]
runtime_files += [
    'sheep_quest_bot_frame_budget_v11_411.js',
    'model_accessory_geometry_v11_410.js', 'model_accessory_bridge_v11_410.js',
    'model_studio_vr_ui_v11_410.js', 'model_vr_accessory_workshop_v11_410.js',
    'sheep_vr_y_tools_radial_v11_391.js',
    'model_satchel_vr_quest_v11_413.js',
    'model_satchel_tool_references_v11_414.js',
    'model_vr_object_index_v11_416.js']
for name in runtime_files:
    p = ROOT / 'runtime' / name
    subprocess.run(['node', '--check', str(p)], check=True)
    assert 'requestAnimationFrame(' not in p.read_text(), name
    assert 'setAnimationLoop(' not in p.read_text(), name
subprocess.run(['node', '--check', str(ROOT / 'runtime/model_satchel_tutorial_v11_412.js')], check=True)
assert (ROOT / 'runtime/model_satchel_tutorial_v11_412.css').is_file()
assert (ROOT / 'runtime/model_satchel_tutorial_v11_413.css').is_file()
assert (ROOT / 'runtime/model_satchel_tool_references_v11_414.css').is_file()
subprocess.run([sys.executable, str(ROOT / 'tests/test_model_vr_iconography_v11_415.py')], check=True)
subprocess.run([sys.executable, str(ROOT / 'tests/test_model_vr_object_index_v11_416.py')], check=True)
subprocess.run(['node', str(ROOT / 'tests/satchel_button_references_v11_414.cjs')], check=True)
subprocess.run(['node', str(ROOT / 'tests/test_sheep_vr_y_menu_v11_391.cjs')], check=True)
subprocess.run(['node', str(ROOT / 'tests/test_sheep_quest_ai_frame_budget_v11_411.cjs')], check=True)
native_tests = 'NOT_REQUESTED'
if args.three_module:
    three = Path(args.three_module).expanduser().resolve()
    assert three.is_file(), 'Local Three ES module is missing: ' + str(three)
    for name in ['model_accessory_geometry_v11_410.mjs', 'model_accessory_bridge_v11_410.mjs']:
        subprocess.run(['node', str(ROOT / 'tests' / name), str(three)], check=True)
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
                  'nativeAccessoryTests': native_tests,
                  'physicalHeadsetAcceptance': False}, indent=2))
