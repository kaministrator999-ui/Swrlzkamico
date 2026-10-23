#!/usr/bin/env python3
"""Seal the saved girl snapshot, connected anime sculpt and 4K material bundle."""
import argparse,collections,gzip,hashlib,json,math,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve();m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/anime_girl_baseline_v11_90.json').read_text())
assert m['name']=='§wyrl§ Engine v11.91' and m['finalArtifact']=='swyrl_engine_v11_91.html'
assert len(m['patches'])==123 and m['patches']==old['patches']+['patches/v11_91_organic_anime_girl.py']
assert len(old['sources'])==294
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
raw=(out/'index.html').read_bytes();html=raw.decode();receipt=json.loads((out/'SOURCE.json').read_text());assert len(raw)==m['finalBytes'] and hashlib.sha256(raw).hexdigest()==m['finalSha256'];assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(raw) and receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==64
for token in ['SWYRL_ENGINE_DEPLOY_MARKER: V11_91_ORGANIC_ANIME_GIRL',"window.SWRLZ_FORGE_BUILD={version:'v11.91'",'<title>§wyrl§ Engine · Maker v11.91</title>','data-project-template="festival-girl-saved"','function atelierAnimeGirlBody(', 'function atelierAnimeFrame(',"p.organicSurface?.species==='anime'",'256_000_000']:
 assert token in html,token
for path,meta in old['assets'].items():assert receipt['assets'][path]==meta and len((out/path).read_bytes())==meta['bytes'] and hashlib.sha256((out/path).read_bytes()).hexdigest()==meta['sha256'],path
saved=json.loads((out/'scenes/model-atelier-girl-saved-v11-90.swyrl.json').read_text());assert saved==json.loads(gzip.decompress((root/'payload/festival-girl/saved-v11-90.swyrl.json.gz').read_bytes()))
constant,_=json.JSONDecoder().raw_decode(html.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1]);assert saved==constant and len(saved['project']['modelAtelier']['parts'])==283
scene=json.loads((out/'scenes/model-atelier-organic-anime-girl-v11-91.swyrl.json').read_text());assert scene==json.loads(gzip.decompress(b''.join(p.read_bytes() for p in sorted((root/'payload/festival-girl').glob('organic-v11-91.swyrl.json.gz.part*')))));assert scene['project']['canonicalId']=='organic-anime-girl'
model=scene['project']['modelAtelier'];assert len(model['parts'])==353 and len({p['id'] for p in model['parts']})==353;assert all(p['kind']=='topologyMesh' for p in model['parts']);assert model['assemblies']==saved['project']['modelAtelier']['assemblies']
for part in model['parts']:
 t=part['topologyMesh'];count=len(t['positions'])//3;assert count<=300000 and len(t['indices'])//3<=600000;assert len(t['positions'])%3==0 and len(t['uvs'])==count*2 and len(t['indices'])%3==0;assert all(math.isfinite(v) and abs(v)<=100 for v in t['positions']);assert all(0<=v<count for v in t['indices'])
body=model['parts'][0];assert body['id']=='girl-organic-body';t=body['topologyMesh'];assert 350000<len(t['indices'])//3<600000
edges=collections.Counter(tuple(sorted(e)) for a,b,c in zip(t['indices'][::3],t['indices'][1::3],t['indices'][2::3]) for e in [(a,b),(b,c),(c,a)]);assert set(edges.values())=={2},collections.Counter(edges.values())
parent=list(range(len(t['positions'])//3))
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
for a,b in edges:
 a,b=find(a),find(b)
 if a!=b:parent[b]=a
assert len({find(i) for i in range(len(parent))})==1,'Body, head, hands and feet must be connected'
assert min(t['positions'][1::3])<.06 and max(t['positions'][1::3])>4.44 and min(t['positions'][::3])< -1.08 and max(t['positions'][::3])>1.08
assert sum(p['organicSurface']['region']=='nail' for p in model['parts'])==10 and sum(p['id'].startswith('girl-fiber-') for p in model['parts'])==72
assert len(model['parts'][-1]['topologyMesh']['indices'])>10000
for name in ['festival-basecolor-4k.jpg','festival-normal-4k.png']:
 data=(out/'assets/models/festival-girl'/name).read_bytes();assert len(data)>1000000
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]);print('SWRLZ_V1191_RELEASE_VERIFIED',len(raw),m['finalSha256'],123,64,'294_PREVIOUS_SOURCES_60_ASSETS_EXACT','ONE_CLOSED_CONNECTED_BODY',len(t['positions'])//3,len(t['indices'])//3,'TOTAL_TRIANGLES',sum(len(p['topologyMesh']['indices'])//3 for p in model['parts']))
