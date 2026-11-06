#!/usr/bin/env python3
"""§E v11.292: sealed Cliff Hand wrist moss + material-only rock knuckles."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.292'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_292_CLIFF_WRIST_MOSS_KNUCKLES'
SHA='d1b9b3c700a9c9063c3f46de8cf71b68b5f029d9f0a690e1ac62d8175f4daabc'
SIZE=8252255
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
args=parser.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine '+VERSION
assert manifest['finalArtifact']=='swyrl_engine_v11_292.html'
assert len(manifest['patches'])==323
assert manifest['patches'][-2:]==[
 'patches/v11_291_hooded_vanguard_materials.py',
 'patches/v11_292_cliff_knuckle_wrist_moss.py'
]
assert manifest['finalBytes']==SIZE and manifest['finalSha256']==SHA
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
subprocess.run([
 sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')
],check=True)
subprocess.run([
 'node',str(ROOT/'scripts/test_v11_292_cliff_material.cjs')
],check=True)
body=raw.decode('utf8')
for term in (
 MARKER,
 '<title>§wyrl§ Engine · Maker v11.292</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.292'",
 'function se292WristMossKnuckleMaterial(part){',
 'function se292DrawKnuckleRelief(ctx,kind){',
 'function se292PaintAtlas(img){',
 "part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se292WristMossKnuckleMaterial(part):",
 'model.parts=[stone];model.meshGroups=[];',
 'function se291HeroMaterial(part){',
 'data-project-template="hooded-vanguard"',
 'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
):
 assert term in body,term
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
assert receipt['sourceVersion']==manifest['name']
assert receipt['patches']==manifest['patches']
assert receipt['finalBytes']==SIZE and receipt['finalSha256']==SHA
assert len(receipt['assets'])==71
for filename,meta in receipt['assets'].items():
 data=(out/filename).read_bytes()
 assert len(data)==meta['bytes'],filename
 assert hashlib.sha256(data).hexdigest()==meta['sha256'],filename
assert (out/'assets/cliff-hand/cliff_pbr_atlas_384.jpg').stat().st_size==404577
if args.request:
 q=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert q['releaseVersion']==VERSION
 assert q['deployMarker']==MARKER
 assert q['sourceIntegritySha256']==SHA
 assert isinstance(q.get('sourceCommit'),str) and len(q['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':VERSION,'patches':323,
 'assets':71,'htmlBytes':SIZE,'sha256':SHA,'knuckleMaps':4,'wristOnlyMoss':True,
 'meshExtraObjects':0,'HoodedVanguardPreserved':True,'ownerPhoneVisualAcceptance':False},indent=2))
