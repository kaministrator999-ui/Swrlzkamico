#!/usr/bin/env python3
"""Sealed v11.370 anatomy-preserving Cliff material polish, isolated from Rocky Hand."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_370_CLIFF_STONE_SURFACE_POLISH'
ap=argparse.ArgumentParser()
ap.add_argument('--output',required=True)
ap.add_argument('--request',action='store_true')
args=ap.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.370'
assert manifest['finalArtifact']=='swyrl_engine_v11_370.html'
assert len(manifest['patches'])==377 and manifest['patches'][-1]=='patches/v11_370_cliff_surface_polish.py'
assert manifest['finalBytes']==9420154
assert manifest['finalSha256']=='3fba8f65dbf9bc1b84ddda64257dbfe1ea463fa19f33f57611aec44b4c68b512'
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
html=data.decode('utf8')
for token in [
    MARKER,
    "window.SWRLZ_FORGE_BUILD={version:'v11.370'",
    '<title>§wyrl§ Engine · Maker v11.370</title>',
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
]:
    assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.370';source.version=11.370;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_uv_aligned_export_v11_364.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/hand_reference_fit_v11_365.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_uv_art_marker_v11_366.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_366_uv_marker.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_365_webxr_rock_anatomy.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_365_cliff_anatomy_fit.cjs')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/stone_hand_anatomy_v11_367.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_367_full_rock_hand.cjs')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_367_connected_cliff.cjs')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/webxr_cliff_stone_v11_369.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_369_webxr_cliff_clone.cjs')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/webxr_cliff_material_polish_v11_370.js')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_370_cliff_material.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,want in [('sourceVersion',manifest['name']),('finalBytes',manifest['finalBytes']),
                 ('finalSha256',manifest['finalSha256']),('patches',manifest['patches'])]:
    assert receipt[key]==want,key
if args.request:
    req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
    assert req['releaseVersion']=='v11.370'
    assert req['deployMarker']==MARKER
    assert req['sourceIntegritySha256']==manifest['finalSha256']
    assert len(req['sourceCommit'])==40
print(json.dumps(dict(status='SEALED',version='v11.370',
  patches=len(manifest['patches']),bytes=len(data),
  sha256=manifest['finalSha256'],physicalDeviceAcceptance=False),indent=2))
