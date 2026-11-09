#!/usr/bin/env python3
"""Sealed v11.365 Cliff Hand and Rock Hand WebXR anatomy calibration."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_365_HAND_REFERENCE_FIT'
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.365'
assert manifest['finalArtifact']=='swyrl_engine_v11_365.html'
assert len(manifest['patches'])==372 and manifest['patches'][-1]=='patches/v11_365_hand_reference_fit.py'
assert isinstance(manifest['finalBytes'],int) and manifest['finalBytes']>9_360_000
assert isinstance(manifest['finalSha256'],str) and len(manifest['finalSha256'])==64
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
html=data.decode('utf8')
for token in [
    MARKER,
    "window.SWRLZ_FORGE_BUILD={version:'v11.365'",
    '<title>§wyrl§ Engine · Maker v11.365</title>',
    'se364DrawAlignedPaint','se364ExportAlignedPaint','se364ExportSlideCorrection',
    'SE365', 'SWYRL_ENGINE_HAND_REFERENCE_FIT_365',
    'se365RefinedRockScene', 'se365WebXRAnatomy',
    'se364UVSaveAligned','se364UVSaveCorrection',
    'swyrl-model-uv-alignment-correction-v1',
    'se336SlideOffset','se336UVLayout','se355UVPopup',
    'SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361',
    'SE362_CONTROLLER_HINTS_START',
]:
    assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.365';source.version=11.364;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_uv_aligned_export_v11_364.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/hand_reference_fit_v11_365.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_365_webxr_rock_anatomy.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_365_cliff_anatomy_fit.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,want in [('sourceVersion',manifest['name']),('finalBytes',manifest['finalBytes']),
                 ('finalSha256',manifest['finalSha256']),('patches',manifest['patches'])]:
    assert receipt[key]==want,key
if args.request:
    req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
    assert req['releaseVersion']=='v11.365'
    assert req['deployMarker']==MARKER
    assert req['sourceIntegritySha256']==manifest['finalSha256']
    assert len(req['sourceCommit'])==40
print(json.dumps(dict(status='SEALED',version='v11.365',
  patches=len(manifest['patches']),bytes=len(data),
  sha256=manifest['finalSha256'],physicalDeviceAcceptance=False),indent=2))
