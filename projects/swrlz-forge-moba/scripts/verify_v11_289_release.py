#!/usr/bin/env python3
"""§E v11.289: exact sealed 320-patch gauntlet release + native mesh smoke."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.289'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_289_SHORT_CLIFF_GAUNTLET'
EXPECTED_SHA='55ad1adf274728e665ff851a6eae6cd4ea730063f2a8ad6fca21cc643c029ca5'
EXPECTED_SIZE=8224606
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
args=parser.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine '+VERSION
assert manifest['finalArtifact']=='swyrl_engine_'+VERSION.replace('v','').replace('.','_')+'.html'
assert manifest['patches'][-1]=='patches/v11_289_short_cliff_gauntlet.py'
assert len(manifest['patches'])==320
assert manifest['finalBytes']==EXPECTED_SIZE
assert manifest['finalSha256']==EXPECTED_SHA

out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==EXPECTED_SIZE
assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_289_gauntlet.cjs')],check=True)
script=raw.decode('utf8')
for term in (
 MARKER,
 '<title>§wyrl§ Engine · Maker v11.289</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.289'",
 'function se289ExtendGauntletTopology(part){',
 'function se289ProjectGauntletUV(part){',
 'const gauntlet=se289ExtendGauntletTopology(stone);',
 'const vertices=se289ProjectGauntletUV(stone);',
 'model.parts=[stone];model.meshGroups=[];',
 'const scene=se212HandScene(),model=scene.project.modelAtelier;',
 'SWYRL_ENGINE_CLIFF_GAUNTLET_289',
 'short tapered gauntlet forearm',
 'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
):
 assert term in script,term
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
assert receipt['sourceVersion']==manifest['name']
assert receipt['finalBytes']==EXPECTED_SIZE and receipt['finalSha256']==EXPECTED_SHA
assert receipt['patches']==manifest['patches']
assert len(receipt['assets'])==71
for filename,details in receipt['assets'].items():
 data=(out/filename).read_bytes()
 assert len(data)==details['bytes'],filename
 assert hashlib.sha256(data).hexdigest()==details['sha256'],filename
assert (out/'assets/cliff-hand/cliff_pbr_atlas_384.jpg').stat().st_size==404577
if args.request:
 request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert request['releaseVersion']==VERSION
 assert request['deployMarker']==MARKER
 assert request['sourceIntegritySha256']==EXPECTED_SHA
 assert isinstance(request.get('sourceCommit'),str) and len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':VERSION,
  'patches':320,'assets':71,'htmlBytes':EXPECTED_SIZE,'sha256':EXPECTED_SHA,
  'geometry':'one connected short forearm and hand, mapped stone texture',
  'ownerPhoneVisualAcceptance':False},indent=2))
