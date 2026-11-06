#!/usr/bin/env python3
"""§E v11.290: verify a sealed one-piece Cliff Hand gauntlet and mapped PBR."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='v11.290'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_290_CLIFF_GAUNTLET_LOAD_MATERIAL'
SIZE=8229895
SHA='b7a8ade38caa3bbc5ee2ae6319c75c8352149ac7d0aa4e37699b89e75e08709f'
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
args=parser.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine '+VERSION
assert m['finalArtifact']=='swyrl_engine_v11_290.html'
assert len(m['patches'])==321
assert m['patches'][-1]=='patches/v11_290_cliff_gauntlet_load_material.py'
assert m['finalBytes']==SIZE and m['finalSha256']==SHA
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'scripts/test_v11_290_cliff_gauntlet.cjs')],check=True)
html=raw.decode('utf8')
for term in (
 MARKER,
 '<title>§wyrl§ Engine · Maker v11.290</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.290'",
 'function se290GauntletField(){',
 'function se290BuildGauntletSurface(part){',
 'const gauntlet=se290BuildGauntletSurface(stone);',
 'const vertices=se290GauntletUV(stone);',
 'function se290CliffMaterial(part){',
 "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
 'model.parts=[stone];model.meshGroups=[];',
 'se217OrganicHandSkin(se217FingerSpec,math)',
 'SWYRL_ENGINE_CLIFF_GAUNTLET_290',
 'assets/cliff-hand/cliff_pbr_atlas_384.jpg',
):
 assert term in html,term
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
assert receipt['sourceVersion']==m['name']
assert receipt['patches']==m['patches']
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
print(json.dumps({
 'status':'SEALED_SOURCE_VERIFIED','version':VERSION,'patches':321,'assets':71,
 'htmlBytes':SIZE,'sha256':SHA,
 'hand':'native anatomical SDF and short integral forearm, one rigged mesh',
 'material':'warm dimensional rock PBR from existing 384px owner atlas',
 'ownerRealDeviceAcceptance':False
},indent=2))
