"""Validate actual authored topology and high resolution image assets."""
from pathlib import Path
import collections,gzip,json,math,hashlib
from PIL import Image
r=Path(__file__).resolve().parents[1];evidence=[]
for species in ['sheep','wolf']:
 data=json.loads(gzip.decompress((r/f'payload/organic-animals/{species}.swyrl.json.gz').read_bytes()));m=data['project']['modelAtelier'];total=0
 assert data['project']['canonicalId']==species+'-model'
 for p in m['parts']:
  assert p['kind']=='topologyMesh' and p['organicSurface']['species']==species
  t=p['topologyMesh'];pos=t['positions'];idx=t['indices'];n=len(pos)//3;assert len(pos)%3==0 and n<=65536 and len(idx)%3==0 and len(idx)//3<=120000;assert all(math.isfinite(x) for x in pos+t['uvs']);assert len(t['uvs'])==n*2;assert all(isinstance(i,int) and 0<=i<n for i in idx)
  for a,b,c in zip(idx[::3],idx[1::3],idx[2::3]):assert len({a,b,c})==3
  total+=len(idx)//3
 body=m['parts'][0]['topologyMesh'];edges=collections.Counter();adj=collections.defaultdict(set)
 for a,b,c in zip(body['indices'][::3],body['indices'][1::3],body['indices'][2::3]):
  for u,v in [(a,b),(b,c),(c,a)]:edges[tuple(sorted((u,v)))]+=1;adj[u].add(v);adj[v].add(u)
 seen=set();stack=[next(iter(adj))]
 while stack:
  x=stack.pop()
  if x in seen:continue
  seen.add(x);stack.extend(adj[x]-seen)
 assert len(seen)==len(adj),'Main organic body has disconnected volumes'
 assert all(n==2 for n in edges.values()),'Main organic body has an open or non-manifold edge'
 assert total>150000
 groups=m['meshGroups'];members=[v for g in groups for v in g['members']];assert all(2<=len(g['members'])<=32 for g in groups);assert len(set(members))==len(members)
 evidence.append({'species':species,'parts':len(m['parts']),'triangles':total,'mainBodyVertices':len(body['positions'])//3,'mainBodyTriangles':len(body['indices'])//3,'mainBodyOneConnectedWatertightSurface':True})
for p in (r/'assets/models/wildwood-animals').glob('*'):assert Image.open(p).size==(4096,4096)
print('ORGANIC_WELDED_TOPOLOGY_CLOSED_CONNECTED_BODY_NATIVE_GROUPS_AND_4K_ASSETS_PASS',json.dumps(evidence))
