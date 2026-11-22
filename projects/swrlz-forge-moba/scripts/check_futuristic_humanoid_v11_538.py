#!/usr/bin/env python3
"""§E v11.538 baked continuous humanoid source acceptance (standard-library only)."""
import base64
from collections import Counter
import json
from pathlib import Path
import struct
import sys
import zlib

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json'


def check():
    scene=json.loads(ASSET.read_text('utf8'))
    assert scene['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert scene['project']['kind']=='model-atelier'
    model=scene['project']['modelAtelier']
    assert model['schema']=='swyrl-model-atelier-v1'
    assert len(model['parts'])==1
    assert not model['meshGroups'] and not model['poseFrames']
    p=model['parts'][0]
    assert p['id']=='humanoid-body-unified' and p['kind']=='topologyMesh'
    assert p['color']=='#ffffff' and p['material']=='silk'
    mesh=p['topologyMesh']; xyz=mesh['positions']; uv=mesh['uvs']; ix=mesh['indices']
    v=len(xyz)//3; faces=len(ix)//3
    assert 2000<=v<=9000 and len(xyz)==3*v
    assert 4000<=faces<=16000 and len(ix)==3*faces
    assert len(uv)==2*v and min(uv)>=0 and max(uv)<=1
    assert all(isinstance(i,int) and 0<=i<v for i in ix)
    assert min(xyz[0::3])<-2.38 and max(xyz[0::3])>2.38
    assert max(xyz[1::3])>4.65 and min(xyz[1::3])<.10
    # Account for UV seam vertex duplication when inspecting geometric topology.
    welded={}
    for n in range(v):
        point=tuple(xyz[3*n:3*n+3])
        welded[n]=point
    edges=Counter()
    adj={}
    for a,b,c in zip(ix[0::3],ix[1::3],ix[2::3]):
        pts=[welded[a],welded[b],welded[c]]
        assert len(set(pts))==3, 'Collapsed geometry triangle'
        for i,j in ((0,1),(1,2),(2,0)):
            u,w=pts[i],pts[j]
            edges[(u,w) if u<w else (w,u)]+=1
            adj.setdefault(u,set()).add(w)
            adj.setdefault(w,set()).add(u)
    assert len(edges)>1000
    assert all(n==2 for n in edges.values()),'Geometric mesh must be closed/watertight'
    discovered={next(iter(adj))}
    todo=list(discovered)
    while todo:
        for nxt in adj[todo.pop()]:
            if nxt not in discovered:
                discovered.add(nxt);todo.append(nxt)
    assert len(discovered)==len(adj),'All geometric shell vertices must be connected'
    # Six fixed atlas islands, each region must actually be occupied.
    tiles=set()
    for u,w in zip(uv[0::2],uv[1::2]):
        tiles.add((min(2,int(u*3)),min(1,int(w*2))))
    assert tiles=={(a,b) for a in range(3) for b in range(2)},tiles
    data=p['uvPaintPNG']
    assert data.startswith('data:image/png;base64,') and len(data)<360000
    png=base64.b64decode(data.partition(',')[2],validate=True)
    assert png[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',png[16:24])
    assert (width,height)==(1024,1024)
    assert len(ASSET.read_bytes())<2_000_000
    print('SE538_UNIFIED_SOURCE_OK',json.dumps({
        'parts':1,'vertices':v,'triangles':faces,
        'geometricComponents':1,'openEdges':0,
        'atlasSize':[width,height],'atlasCharacters':len(data),
        'sceneBytes':ASSET.stat().st_size,
    }))


if __name__=='__main__':
    check()
