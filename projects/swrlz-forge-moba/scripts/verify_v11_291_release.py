#!/usr/bin/env python3
"""§E v11.291 — seal-check and package Hooded Vanguard's native starter."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.291'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_291_HOODED_VANGUARD_MATERIALS'
SIZE=8245089
SHA='d0bfb2799c1650317768f0d128d1e9483ca4f53c427937892b6adeb4455ff1f5'

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
args=parser.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine '+VERSION
assert m['finalArtifact']=='swyrl_engine_v11_291.html'
assert m['finalBytes']==SIZE and m['finalSha256']==SHA
assert len(m['patches'])==322 and m['patches'][-1]=='patches/v11_291_hooded_vanguard_materials.py'

out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
html=raw.decode('utf8')

for term in (
 MARKER,
 '<title>§wyrl§ Engine · Maker v11.291</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.291'",
 'data-project-template="hooded-vanguard"',
 'function se291HeroScene(){',
 'function se291HeroMaterial(part){',
 'function se291OpenHero(force=false){',
 "mat=part.heroPBR?se291HeroMaterial(part):",
 'Vanguard / moving shoulder armor',
 'Vanguard / animated coat tails',
 "maps:['albedo','normal','roughness']",
 'model.rigging=null;',
 'SWYRL_ENGINE_HOODED_VANGUARD',
):
 assert term in html,term
assert 'SWYRL_ENGINE_CLIFF_GAUNTLET_290' in html
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/hooded_vanguard_v11_291.js')],check=True)

receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
assert receipt['sourceVersion']==m['name']
assert receipt['patches']==m['patches']
assert receipt['finalBytes']==SIZE and receipt['finalSha256']==SHA
assert len(receipt['assets'])==71
for filename,meta in receipt['assets'].items():
 data=(out/filename).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],filename
if args.request:
 q=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert q['releaseVersion']==VERSION
 assert q['deployMarker']==MARKER
 assert q['sourceIntegritySha256']==SHA
 assert isinstance(q.get('sourceCommit'),str) and len(q['sourceCommit'])==40
print(json.dumps({
 'status':'SEALED_SOURCE_VERIFIED','version':VERSION,
 'htmlBytes':SIZE,'sha256':SHA,'patches':322,'assets':71,
 'starter':'Hooded Vanguard / native 14-part modeled static study',
 'maps':'procedural UV color, normal, roughness (material-first)',
 'rigged':False,'ownerRealDeviceAcceptance':False
},indent=2))
