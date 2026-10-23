#!/usr/bin/env python3
"""Seal living Astra, Clover's native game model and compact corner controls."""
import argparse,hashlib,json,subprocess,gzip,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/living_animals_baseline_v11_88.json').read_text())
assert m['name']=='§wyrl§ Engine v11.89' and m['finalArtifact']=='swyrl_engine_v11_89.html'
assert m['patches']==old['patches']+['patches/v11_89_living_astra_clover_corner_controls.py'] and len(m['patches'])==121
assert len(old['sources'])==285
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode();receipt=json.loads((out/'SOURCE.json').read_text())
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
for token in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_89_LIVING_ASTRA_CLOVER','ENGINE · MAKER v11.89',"window.SWRLZ_FORGE_BUILD={version:'v11.89'",'<title>§wyrl§ Engine · Maker v11.89</title>','const ST_LANE_GAP = .75;','const stPassageCornerBase=stHouseSlideTarget;','sheepCornerControls','function atelierLivingSweep(', 'function atelierCloverSheep(', "if(type==='st-sheep')return ModelAtelier.createCloverSheep();", 'CloverMeadowSheep', 'duration:420,headstart:30']:
 assert token in html,token
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==58
assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(data)
assert {p:receipt['assets'][p] for p in old['assets']}==old['assets']
for path,meta in old['assets'].items():
 raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
scene=json.loads((out/'scenes/model-atelier-living-astra-v11-89.swyrl.json').read_text());assert scene==json.loads(gzip.decompress((root/'payload/living-astra-v11-89.swyrl.json.gz').read_bytes()))
model=scene['project']['modelAtelier'];original=json.loads((root/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())['project']['modelAtelier'];parts={p['id']:p for p in model['parts']}
kept=[i for g in original['meshGroups'] if g['name'] in ['Comet tail and stardust','Couriers travelling gear'] for i in g['members']];assert len(kept)==37
for i in kept:assert parts[i]==next(p for p in original['parts'] if p['id']==i),i
assert len(parts)==92 and scene['project']['canonicalId']=='wolf-model'
assert all(p['kind']=='topologyMesh' for p in model['parts'] if p['id'] not in kept)
for part in model['parts']:
 if 'topologyMesh' not in part:continue
 t=part['topologyMesh'];assert len(t['positions'])//3<=65536 and len(t['indices'])//3<=120000
 edges=collections.Counter(tuple(sorted(e)) for a,b,c in zip(t['indices'][::3],t['indices'][1::3],t['indices'][2::3]) for e in [(a,b),(b,c),(c,a)])
 assert set(edges.values())=={2},part['name']
clover=json.loads((out/'scenes/sheep-tag-clover-model-v11-89.swyrl.json').read_text())['project']['modelAtelier'];high=json.loads(gzip.decompress((root/'payload/organic-animals/sheep.swyrl.json.gz').read_bytes()))['project']['modelAtelier']
assert len(clover['parts'])==31 and clover['sourceTriangles']==275872 and sum(len(p['topologyMesh']['indices'])//3 for p in clover['parts'])==33087
assert [p['id'] for p in high['parts']]==[p['id'] for p in clover['parts']]
for a,b in zip(high['parts'],clover['parts']):assert {k:v for k,v in a.items() if k!='topologyMesh'}=={k:v for k,v in b.items() if k!='topologyMesh'}
embedded,_=json.JSONDecoder().raw_decode(html.split('const ST_CLOVER_GAME_MODEL=',1)[1]);assert embedded==clover
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1189_RELEASE_VERIFIED',len(data),m['finalSha256'],121,58,'285_SOURCES_56_ASSETS_37_GEAR_TAIL_PARTS_PRESERVED')
