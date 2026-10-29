#!/usr/bin/env python3
"""Verify the exact release and freeze all previous runtime, patch and asset bytes."""
import argparse,hashlib,json,subprocess,gzip,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/passages_baseline_v11_87.json').read_text())
assert m['name']=='§wyrl§ Engine v11.88' and m['finalArtifact']=='swyrl_engine_v11_88.html'
assert m['patches']==old['patches']+['patches/v11_88_passages_controls_original_wolf.py'] and len(m['patches'])==120
assert len(old['sources'])==281
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode();receipt=json.loads((out/'SOURCE.json').read_text())
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
for token in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF','ENGINE · MAKER v11.88',"window.SWRLZ_FORGE_BUILD={version:'v11.88'",'<title>§wyrl§ Engine · Maker v11.88</title>','const ST_LANE_GAP = .75;','const stPassageCornerBase=stHouseSlideTarget;','sheepReachableControls','function atelierRefineCourierProject(', 'function stBuildInputFinish(', 'function stWalkStick(', 'function stSoftFogPaint(', 'duration:420,headstart:30']:
 assert token in html,token
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==56
assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(data)
assert {p:receipt['assets'][p] for p in old['assets']}==old['assets']
for path,meta in old['assets'].items():
 raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
scene=json.loads((out/'scenes/model-atelier-original-wolf-organic-v11-88.swyrl.json').read_text());assert scene==json.loads(gzip.decompress((root/'payload/courier-organic-v11-88.swyrl.json.gz').read_bytes()))
model=scene['project']['modelAtelier'];original=json.loads((root/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())['project']['modelAtelier'];parts={p['id']:p for p in model['parts']}
kept=[i for g in original['meshGroups'] if g['name'] in ['Comet tail and stardust','Couriers travelling gear'] for i in g['members']];assert len(kept)==37
for i in kept:assert parts[i]==next(p for p in original['parts'] if p['id']==i),i
assert len(parts)==102 and scene['project']['canonicalId']=='wolf-model'
for part in model['parts']:
 if 'topologyMesh' not in part:continue
 t=part['topologyMesh'];assert len(t['positions'])//3<=65536 and len(t['indices'])//3<=120000
 edges=collections.Counter(tuple(sorted(e)) for a,b,c in zip(t['indices'][::3],t['indices'][1::3],t['indices'][2::3]) for e in [(a,b),(b,c),(c,a)])
 assert set(edges.values())=={2},part['name']
assert sum(len(p['topologyMesh']['indices'])//3 for p in model['parts'] if 'topologyMesh' in p)>130000
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1188_RELEASE_VERIFIED',len(data),m['finalSha256'],120,56,'281_SOURCES_55_ASSETS_37_GEAR_TAIL_PARTS_PRESERVED')
