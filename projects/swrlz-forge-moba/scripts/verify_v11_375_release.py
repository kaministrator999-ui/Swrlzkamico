#!/usr/bin/env python3
"""Sealed v11.375 Quest VR menu drag, group bounds, gizmo hover and project access."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_375_CHAT_TURNAROUND_BLOCKOUT'
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.375'
assert manifest['finalArtifact']=='swyrl_engine_v11_375.html'
assert len(manifest['patches'])==382 and manifest['patches'][-1]=='patches/v11_375_chat_turnaround_blockout.py'
assert manifest['finalBytes']==9468304
assert manifest['finalSha256']=='11ef4d9be97e14e661e7b9bb9cd9bd94d03a6f100ea25e099b2f7ab151a88679'
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
html=data.decode('utf8')
for token in [
    MARKER,
    "window.SWRLZ_FORGE_BUILD={version:'v11.375'",
    '<title>§wyrl§ Engine · Maker v11.375</title>',
    'se364DrawAlignedPaint','se364ExportAlignedPaint','se364ExportSlideCorrection',
    'SWYRL_ENGINE_HAND_REFERENCE_FIT_365',
    'SWYRL_ENGINE_STONE_HAND_ANATOMY_367',
    'se367CliffField','se367AnatomicalRockScene',
    'se365RefinedRockScene', 'se365WebXRAnatomy',
    'se364UVSaveAligned','se364UVSaveCorrection',
    'swyrl-model-uv-alignment-correction-v1',
    'se336SlideOffset','se336UVLayout','se355UVPopup',
    'se366NativeToArt','se366ArtToNative','se366DrawMarker',
    'se366BakeArtwork','se366ImportAuthored','se366AuthorGuide',
    'se366AutoAlignCamera','se366AngleFromView','se366CaptureSlide',
    'swyrl-model-uv-author-marker-v1','se366MarkerTools',
    'SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361',
    'SWYRL_ENGINE_WEBXR_CLIFF_369',
    'SWYRL_ENGINE_CLIFF_POLISH_370',
    'se370PolishedCliffMaterial','se370BakeTiles','se370SurfaceUV',
    'return se370PolishedCliffMaterial(part);',
    'se369CliffFromXRScene','se369MapReferenceVertex',
    "part?.cliffPBR?.variant==='webxr-cliff'",
    'se281RockScene=se367AnatomicalRockScene;',
    'SE362_CONTROLLER_HINTS_START',
    'window.SWYRL_ENGINE_SAFE_PROJECTS_371',
    'se371Clone', 'se371SaveLocal', 'se371CloudLinks',
    'se371HasSavedIdentity', 'se371ProjectNotice',
    'SE372_MODEL_VR_PHASE1_START', 'se372SweepFrame', 'se372SweepStart',
    'SE374_MODEL_VR_OWNER_FEEDBACK_START','se374GroupBoundary','se374GizmoContact',
    'SE375_IMAGE_TO_MODEL_START','function se375Blockout()',
    'function se375Install()', 'function se375Run()',
    'se372GuideStart', 'se372MenuDragStart', 'se372MenuPlace',
    'se372ProjectAction', 'se372Constrain', "'save-account'",

]:
    assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.375';source.version=11.374;")==5
# The project save handlers must be in the same authenticated Chat-host closure
# as cloudRefs, RPC and the existing on-device library.
assert html.index("const PROTOCOL='swrlz-forge-chat-v1'") < html.index('const se371CloudLinks=new Map();')
assert html.index('const se371CloudLinks=new Map();') < html.index('if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
assert 'id="se371ProjectSave"' in html
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
# Focused current interaction and existing account-revision checks only.
subprocess.run(['node','--check',str(ROOT/'runtime/model_vr_phase1_v11_372.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/project_safe_save_v11_371.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_372_model_vr_phase1.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_371_safe_projects.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_373_sweep_handoff.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_vr_feedback_v11_374.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_374_quest_vr_feedback.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_375_image_blockout.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,want in [('sourceVersion',manifest['name']),('finalBytes',manifest['finalBytes']),
                 ('finalSha256',manifest['finalSha256']),('patches',manifest['patches'])]:
    assert receipt[key]==want,key
if args.request:
    req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
    assert req['releaseVersion']=='v11.375'
    assert req['deployMarker']==MARKER
    assert req['sourceIntegritySha256']==manifest['finalSha256']
    assert len(req['sourceCommit'])==40
print(json.dumps(dict(status='SEALED',version='v11.375',
  patches=len(manifest['patches']),bytes=len(data),
  sha256=manifest['finalSha256'],physicalDeviceAcceptance=False),indent=2))
