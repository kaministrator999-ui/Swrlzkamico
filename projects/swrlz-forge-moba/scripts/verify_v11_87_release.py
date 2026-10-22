#!/usr/bin/env python3
"""Seal organic animal starters while preserving all shipped lineage."""
import argparse,hashlib,json,subprocess,gzip
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/organic_animals_baseline_v11_86.json').read_text())
assert m['name']=='§wyrl§ Engine v11.87' and m['finalArtifact']=='swyrl_engine_v11_87.html'
assert m['patches']==old['patches']+['patches/v11_87_organic_animal_starters.py'] and len(m['patches'])==119
assert len(old['sources'])==277
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode();receipt=json.loads((out/'SOURCE.json').read_text())
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_87_ORGANIC_ANIMAL_STARTERS')==1
for token in ['function atelierAnimalBuild(', 'function atelierAnimalSurface(', 'function atelierAnimalStatus(', 'file.size>64_000_000', 'wildwood-4k', 'function stHouseSlideTarget(', 'const stHouseSlideUnits=new WeakSet();', '<title>§wyrl§ Engine · Maker v11.87</title>','ENGINE · MAKER v11.87',"window.SWRLZ_FORGE_BUILD={version:'v11.87'",'v11.87 · organic sheep & wolf model starters','sheepLargeControls', 'const stSevenMinuteRulesBase=stCleanRules;', 'duration:420,headstart:30', 'function stBuildInputFinish(', 'function stWalkStick(', 'function stWalkSnap(', 'stAbilityRing', 'function stBuildDragAim(', 'function stSoftFogPaint(', 'Use the left joystick to move.', 'function stMobileDrive(', 'function stMobileSync(', 'stMoveStick', 'function stSanctuaryRadius(','function stHuntReleased(','function stClarityGap(','stClarityUpdateOverlay(state)','createCourierHunter:atelierCourierHunter','speed:.35,outsideAllowance:2.5']:
    assert token in html,token
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==55
assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(data)
assert {p:receipt['assets'][p] for p in old['assets']}==old['assets']
for path,meta in old['assets'].items():
    raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
encoded=html.split('const ST_CANONICAL_PROJECT=',1)[1];decoded,_=json.JSONDecoder().raw_decode(encoded)
assert decoded==json.loads((out/'scenes/sheep-tag-seven-minute-v11-85.swyrl.json').read_text())
original=html.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1];_,end=json.JSONDecoder().raw_decode(original)
legacy=json.loads((root/'tests/comet_courier_baseline_v11_76.json').read_text());assert hashlib.sha256(original[:end].encode()).hexdigest()==legacy['originalCanonicalSha256']
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1187_RELEASE_VERIFIED',len(data),m['finalSha256'],119,55)
for species in ['sheep','wolf']:
    authored=json.loads(gzip.decompress((root/f'payload/organic-animals/{species}.swyrl.json.gz').read_bytes()))
    assert json.loads((out/f'scenes/model-atelier-organic-{species}-v11-87.swyrl.json').read_text())==authored
    parts=authored['project']['modelAtelier']['parts']
    assert parts and all(p['kind']=='topologyMesh' for p in parts)
    assert sum(len(p['topologyMesh']['indices'])//3 for p in parts)>150000
print('ORGANIC_ANIMALS_HOUSE_STEERING_AND_277_SOURCE_51_ASSET_PRESERVATION_PASS')
