#!/usr/bin/env python3
"""Freeze history, seal solid blockers and validate native fur/ear topology."""
import argparse,hashlib,json,subprocess,gzip,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/solid_fur_baseline_v11_89.json').read_text())
assert m['name']=='§wyrl§ Engine v11.90' and m['finalArtifact']=='swyrl_engine_v11_90.html'
assert m['patches']==old['patches']+['patches/v11_90_solid_blockers_furred_astra.py'] and len(m['patches'])==122
assert len(old['sources'])==290
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode();receipt=json.loads((out/'SOURCE.json').read_text())
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
for token in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_90_SOLID_BLOCKERS_FURRED_ASTRA','ENGINE · MAKER v11.90',"window.SWRLZ_FORGE_BUILD={version:'v11.90'",'<title>§wyrl§ Engine · Maker v11.90</title>','stLanesEjection=()=>null;','function stSolidRoute(', 'const ST_ASTRA_FURRED_GAME_MODEL=', 'function atelierCloverSheep(', 'CloverMeadowSheep', 'duration:420,headstart:30','128_000_000']:
 assert token in html,token
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==60
assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(data)
assert {p:receipt['assets'][p] for p in old['assets']}==old['assets']
for path,meta in old['assets'].items():
 raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
scene=json.loads((out/'scenes/model-atelier-furred-astra-v11-90.swyrl.json').read_text());assert scene==json.loads(gzip.decompress((root/'payload/furred-astra-v11-90.swyrl.json.gz').read_bytes()))
model=scene['project']['modelAtelier'];original=json.loads((root/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())['project']['modelAtelier'];parts={p['id']:p for p in model['parts']}
kept=[i for g in original['meshGroups'] if g['name'] in ['Comet tail and stardust','Couriers travelling gear'] for i in g['members']];assert len(kept)==37
for i in kept:assert parts[i]==next(p for p in original['parts'] if p['id']==i),i
assert len(parts)==96 and scene['project']['canonicalId']=='wolf-model'
assert not any(p['name'].startswith('Ear · outer') for p in model['parts'])
fur_count=0
for part in model['parts']:
 if 'topologyMesh' not in part:continue
 t=part['topologyMesh'];assert len(t['positions'])//3<=65536 and len(t['indices'])//3<=120000
 edges=collections.Counter(tuple(sorted(e)) for a,b,c in zip(t['indices'][::3],t['indices'][1::3],t['indices'][2::3]) for e in [(a,b),(b,c),(c,a)])
 assert set(edges.values())=={2},part['name']
 if part['organicSurface']['region']=='fur3d':fur_count+=len(t['positions'])//(38*3)
 if part['organicSurface']['region']=='face':
  adj=collections.defaultdict(set)
  for a,b in edges:adj[a].add(b);adj[b].add(a)
  seen={next(iter(adj))};q=list(seen)
  while q:
   a=q.pop()
   for b in adj[a]-seen:seen.add(b);q.append(b)
  assert len(seen)==len(adj),'Cranium and both ears must form one connected welded surface'
  assert max(t['positions'][1::3])>3.2
assert fur_count==1100,fur_count
low=json.loads((out/'scenes/sheep-tag-furred-wolf-v11-90.swyrl.json').read_text())['project']['modelAtelier'];assert len(low['parts'])==96
assert sum(len(p['topologyMesh']['indices'])//3 for p in low['parts'] if 'topologyMesh' in p)==53555
embedded,_=json.JSONDecoder().raw_decode(html.split('const ST_ASTRA_FURRED_GAME_MODEL=',1)[1]);assert embedded==low
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1190_RELEASE_VERIFIED',len(data),m['finalSha256'],122,60,'290_SOURCES_58_ASSETS_37_GEAR_TAIL_PARTS_PRESERVED',fur_count,'CLOSED_FUR_LOCKS_WELDED_EARS')
