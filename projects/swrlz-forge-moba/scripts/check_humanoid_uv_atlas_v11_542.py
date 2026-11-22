#!/usr/bin/env python3
"""§E v11.542 asset regression using only Python standard library.

Checks that UV charting changes paint coordinates ONLY, not humanoid shape,
face topology, hand geometry, material presence or prior starter identity.
"""
import base64
from collections import Counter,defaultdict
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'
NEW=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json'
GUIDE=ROOT/'assets/models/futuristic-humanoid-v11-542-uv-guide.png'

def decode(path):
    sc=json.loads(path.read_text('utf8'))
    assert sc['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert sc['project']['kind']=='model-atelier'
    assert len(sc['project']['modelAtelier']['parts'])==1
    p=sc['project']['modelAtelier']['parts'][0]
    assert p['id']=='humanoid-body-unified' and p['kind']=='topologyMesh'
    return sc,p,p['topologyMesh']

def tri_mesh(mesh):
    xyz=mesh['positions']
    uv=mesh['uvs']
    idx=mesh['indices']
    assert len(xyz)%3==0 and len(uv)==len(xyz)//3*2 and len(idx)%3==0
    count=len(xyz)//3
    assert count<=9000 and len(idx)//3<=16000
    assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in xyz+uv)
    assert min(uv)>=0 and max(uv)<=1
    assert all(isinstance(i,int) and 0<=i<count for i in idx)
    points=[tuple(xyz[n:n+3]) for n in range(0,len(xyz),3)]
    faces=[tuple(idx[n:n+3]) for n in range(0,len(idx),3)]
    return points,faces,uv

def geometric_faces(points,faces):
    return Counter(tuple(sorted((points[a],points[b],points[c]))) for a,b,c in faces)

def areas(points,faces,uv):
    total_uv=0
    density=[]
    small=0
    edges=Counter()
    neighbors=defaultdict(set)
    for a,b,c in faces:
        x,y,z=points[a],points[b],points[c]
        ab=[y[i]-x[i] for i in range(3)]
        ac=[z[i]-x[i] for i in range(3)]
        world=.5*math.sqrt(sum(t*t for t in (
            ab[1]*ac[2]-ab[2]*ac[1],
            ab[2]*ac[0]-ab[0]*ac[2],
            ab[0]*ac[1]-ab[1]*ac[0]
        )))
        assert world>1e-10
        u0,v0=uv[2*a:2*a+2]
        u1,v1=uv[2*b:2*b+2]
        u2,v2=uv[2*c:2*c+2]
        area=.5*abs((u1-u0)*(v2-v0)-(v1-v0)*(u2-u0))
        if area<1e-10:small+=1
        else:density.append(area/world)
        total_uv+=area
        assert len({x,y,z})==3
        for e,f in ((x,y),(y,z),(z,x)):
            edges[tuple(sorted((e,f)))]+=1
            neighbors[e].add(f);neighbors[f].add(e)
    assert len(edges)>1000 and all(v==2 for v in edges.values()),'unclosed source surface'
    seen={next(iter(neighbors))}
    stack=list(seen)
    while stack:
        for point in neighbors[stack.pop()]:
            if point not in seen:
                seen.add(point);stack.append(point)
    assert len(seen)==len(neighbors),'disconnected humanoid parts'
    assert small<=max(3,len(faces)//1000),('collapsed UV faces',small)
    assert .12<total_uv<1.0,('UV coverage / overlap invalid',total_uv)
    density.sort()
    density_ratio=density[int(len(density)*.95)]/density[int(len(density)*.05)]
    assert density_ratio<100,('UV texel density badly uneven',density_ratio)
    return round(total_uv,4),round(density_ratio,2)

def check():
    previous,old_part,old_mesh=decode(OLD)
    new,part,mesh=decode(NEW)
    assert new['version']==11.542
    assert new['project']['modelAtelier']['schema']=='swyrl-model-atelier-v1'
    assert not new['project']['modelAtelier']['meshGroups']
    assert new['project']['modelAtelier']['poseFrames']==[]
    assert part['material']==old_part['material']=='silk'
    assert part['name'].endswith('relaxed non-overlapping paint atlas')
    assert part['uvPaintPNG'].startswith('data:image/png;base64,')
    b=base64.b64decode(part['uvPaintPNG'].split(',',1)[1],validate=True)
    assert b[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',b[16:24])==(1024,1024)
    assert len(part['uvPaintPNG'])<360000
    original,orig_faces,_=tri_mesh(old_mesh)
    points,faces,uv=tri_mesh(mesh)
    assert len(faces)==len(orig_faces)
    assert geometric_faces(points,faces)==geometric_faces(original,orig_faces),(
        'The UV update must not reshape, retopologize or remove fingers')
    assert len(set(points))<len(points),'UV seams must be split without splitting body geometry'
    total,ratio=areas(points,faces,uv)
    layout=GUIDE.read_bytes()
    assert layout[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',layout[16:24])==(2048,2048)
    assert len(layout)<4_000_000
    assert len(NEW.read_bytes())<2_000_000
    print('SE542_HUMANOID_UV_ASSET_OK',json.dumps({
        'uvVertices':len(points),'geometricVertices':len(set(points)),
        'triangles':len(faces),'oneBody':True,'uvArea':total,
        'densityP95ToP5':ratio,'pngBytes':len(b),
        'guideBytes':len(layout),'nativeProjectId':new['project']['canonicalId']}))

if __name__=='__main__':
    check()
