#!/usr/bin/env python3
"""§E v11.288 — targeted sealed source, smooth topology, atlas and JS verification."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
args=parser.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_288_SMOOTH_CLIFF_PBR'
assert m['name']=='§wyrl§ Engine v11.288'
assert m['finalArtifact']=='swyrl_engine_v11_288.html'
assert m['patches'][-1]=='patches/v11_288_smooth_cliff_pbr.py'
assert len(m['patches'])==319
assert m['finalBytes']==8221626
assert m['finalSha256']=='e9862396dd559208637d2b073155fd69b959716cb303e83519d520f44102d859'

out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
html=raw.decode('utf8')
for term in (
 MARKER,
 '<title>§wyrl§ Engine · Maker v11.288</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.288'",
 'function se288SmoothCliffHandScene(){',
 'return se288SmoothCliffHandScene();',
 'const scene=se212HandScene(),model=scene.project.modelAtelier;',
 'model.parts=[stone];model.meshGroups=[];',
 'se220RigValidate(model.rigging)||model.rigging.bones.length!==17',
 'function se288ProjectCliffUV(part){',
 'function se288CliffMaterial(part){',
 'stone.cliffPBR={atlas:',
 "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se288CliffMaterial(part):",
 'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
 '<strong>Plain Hand Base · Smooth Cliff Hand</strong>',
 'STARTER MODEL · SMOOTH HAND / ROCK MATERIAL / 17-BONE RIG',
):
 assert term in html,term
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
assert receipt['sourceVersion']==m['name']
assert receipt['finalSha256']==m['finalSha256']
assert receipt['finalBytes']==m['finalBytes']
assert receipt['patches']==m['patches']
assert len(receipt['assets'])==71
for name,metadata in receipt['assets'].items():
 data=(out/name).read_bytes()
 assert len(data)==metadata['bytes'],name
 assert hashlib.sha256(data).hexdigest()==metadata['sha256'],name
atlas=out/'assets/cliff-hand/cliff_pbr_atlas_384.jpg'
assert atlas.read_bytes()[:3]==bytes((255,216,255))
assert atlas.stat().st_size==404577
if args.request:
 q=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert q['releaseVersion']=='v11.288'
 assert q['deployMarker']==MARKER
 assert q['sourceIntegritySha256']==m['finalSha256']
 assert isinstance(q.get('sourceCommit'),str) and len(q['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.288',
 'parts':1,'modeledCracks':0,'modeledStones':0,'nativeRigBones':17,
 'materialAtlas':atlas.name,'patches':319,'assets':71,
 'htmlBytes':m['finalBytes'],'sha256':m['finalSha256'],
 'ownerPhoneVisualAcceptance':False},indent=2))
