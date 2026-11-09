#!/usr/bin/env python3
"""Targeted §E v11.362 model-controller-labels release verification."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_362_QUEST_CONTROLLER_HINTS'
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.362'
assert m['finalArtifact']=='swyrl_engine_v11_362.html'
assert len(m['patches'])==369 and m['patches'][-1]=='patches/v11_362_quest_controller_hints.py'
assert isinstance(m['finalBytes'],int) and m['finalBytes']>9_340_000
assert isinstance(m['finalSha256'],str) and len(m['finalSha256'])==64
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for token in [
 MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.362'",
 '<title>§wyrl§ Engine · Maker v11.362</title>',
 'SE362_CONTROLLER_HINTS_START','const se362LiveControllers=',
 'se362ControllerConnected(r);','se362ControllerDisconnected(r);','se362Frame(s);',
 '!record.se362Visual?.ready','se362CurrentBindings(s)',
 'assets/models/webxr-touch-v3/','async function se362LoadVisual(record,visual)',
 'function se362CleanLabel(action,s)','currentProfile?.()',
 'se356ApplyCameraOrbit','SE350_MODEL_VR_NATIVE_TOOLS_START',
 'SE360_MODEL_VR_MENU_MOTION_START','SE360_MODEL_VR_UI_START',
 'se355UVPopup','window.SWYRLZ_E_UV_POPUP=Object.freeze',
 'SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361',
]:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.362';source.version=11.362;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for source in ['runtime/model_vr_controller_hints_v11_362.js',
               'runtime/model_vr_workspace_v11_350.js','runtime/model_vr_input_profile_v11_350.js',
               'runtime/model_studio_vr_ui_v11_360.js']:
 subprocess.run(['node','--check',str(ROOT/source)],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,want in [('sourceVersion',m['name']),('finalBytes',m['finalBytes']),('finalSha256',m['finalSha256']),('patches',m['patches'])]:
 assert receipt[key]==want,key
for key in ['assets/models/webxr-touch-v3/left.json','assets/models/webxr-touch-v3/right.json','assets/models/webxr-touch-v3/LICENSE.md']:
 assert key in receipt['assets'] and (out/key).is_file(),key
for path,info in receipt['assets'].items():
 b=(out/path).read_bytes()
 assert len(b)==info['bytes'] and hashlib.sha256(b).hexdigest()==info['sha256'],path
if args.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.362'
 assert req['deployMarker']==MARKER
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert len(req['sourceCommit'])==40
print(json.dumps(dict(status='SEALED',version='v11.362',patches=len(m['patches']),
 bytes=len(data),sha256=m['finalSha256'],assets=len(receipt['assets']),
 physicalQuest2Acceptance=False),indent=2))

