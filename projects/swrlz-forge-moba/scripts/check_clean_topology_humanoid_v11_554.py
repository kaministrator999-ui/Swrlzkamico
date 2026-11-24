#!/usr/bin/env python3
"""Independent native asset contract for the §E UV-first humanoid experiment."""
import base64,json,math,struct
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SCENE=R/'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
REPORT=R/'docs/qa/clean-topology-humanoid-v11-554.json'
PAINT=R/'assets/models/clean-topology-humanoid-v11-554-uv-test.png'
GUIDE=R/'assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png'
ORIGINAL=R/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'
def png(p,w,h):
    b=p.read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n',p
    assert struct.unpack('>II',b[16:24])==(w,h),(p,len(b))
    return b
def run():
    j=json.loads(SCENE.read_text('utf8'))
    r=json.loads(REPORT.read_text('utf8'))
    assert j['version']==11.554
    assert j['project']['canonicalId']==j['project']['template']=='clean-topology-humanoid'
    assert j['project']['modelAtelier']['parts'] and len(j['project']['modelAtelier']['parts'])==1
    part=j['project']['modelAtelier']['parts'][0];mesh=part['topologyMesh']
    p=mesh['positions'];uv=mesh['uvs'];ix=mesh['indices']
    assert 2000<=len(p)//3<=9000 and 2000<=len(ix)//3<=16000
    assert len(uv)==len(p)//3*2 and len(ix)%6==0
    assert all(isinstance(v,(int,float)) and math.isfinite(v) for v in p+uv)
    assert all(0<=v<=1 for v in uv)
    assert min(ix)>=0 and max(ix)<len(p)//3
    assert len(r['quads'])==6 and all(n>100 for n in r['quads'].values())
    assert sum(r['quads'].values())*2==len(ix)//3
    # Every two triangles must be the two halves of a real quad, not a
    # re-triangulated arbitrary UV polygon.
    for i in range(0,len(ix),6):
        ids=ix[i:i+6]
        assert len(set(ids))==4,('non-quad geometry',i)
        for a in set(ids):
            u,v=uv[a*2:a*2+2]
            assert (0<=u<=1 and 0<=v<=1)
    # Regions do not share UV rectangle interiors. Digit strips live inside
    # their corresponding arm rectangles, not on unrelated torso pixels.
    bounds=r['uvBoxes']
    assert len(bounds)==6
    rects=list(bounds.values())
    for i,a in enumerate(rects):
        assert 0<=a[0]<a[2]<=1 and 0<=a[1]<a[3]<=1
        for b in rects[i+1:]:
            assert min(a[2],b[2])<=max(a[0],b[0]) or min(a[3],b[3])<=max(a[1],b[1])
    assert base64.b64decode(part['uvPaintPNG'].split(',',1)[1])==png(PAINT,1024,1024)
    png(GUIDE,2048,2048)
    assert json.loads(ORIGINAL.read_text('utf8'))['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert r['quadFirst'] and r['originalRobotPreserved']
    assert r['revision']=='anatomical-pelvis-uv-v3'
    assert r['uvPaintMode']=='actual-UV-quad-island-masking'
    assert r['guideAnatomyLabels'] is True
    charts=r['uvCharts']
    for key in ('torsoFront','torsoBack','pelvis','headFront','headBack','crown'):
        assert charts.get(key,0)>6,('missing anatomy chart',key)
    assert sum(charts.values())==sum(r['quads'].values())
    # A real groin saddle is not a coplanar lower cap; verify the inner
    # pelvic geometry descends from the lateral hip crests.
    pelvis=[p[k:k+3] for k in range(0,len(p),3)
            if 2.02<p[k+1]<2.49 and abs(p[k])<.56]
    central=[v[1] for v in pelvis if abs(v[0])<.08 and abs(v[2])<.10]
    lateral=[v[1] for v in pelvis if .28<abs(v[0])<.44 and abs(v[2])<.20]
    assert central and lateral and max(lateral)-min(central)>.19,(
        'pelvic height variation missing',min(central or [0]),max(lateral or [0]))

    # Independent positional-weld check: UV seams are allowed, mesh cracks are not.
    from collections import Counter,defaultdict
    xyz=[tuple(p[k:k+3]) for k in range(0,len(p),3)]
    idmap={v:i for i,v in enumerate(sorted(set(xyz)))}
    verts=[idmap[v] for v in xyz]
    edges=Counter()
    for k in range(0,len(ix),6):
        a,b,c,d=ix[k],ix[k+1],ix[k+2],ix[k+5]
        welded=[verts[n] for n in (a,b,c,d)]
        assert len(set(welded))==4,('degenerate welded quad',k)
        for z in range(4):
            e=tuple(sorted((welded[z],welded[(z+1)%4])))
            edges[e]+=1
    assert all(n==2 for n in edges.values()),(
        'Open or nonmanifold physical seams',Counter(edges.values()))
    assert r['components']==1,r['components']
    qa=r['topologyAudit']
    assert qa['watertight'] and qa['connectedComponents']==1
    assert qa['openEdges']==qa['nonManifoldEdges']==0
    assert qa['weldedEdges']==len(edges)
    assert qa['weldedVertices']==len(idmap)
    print('SE554_CLEAN_TOPOLOGY_NATIVE_ASSET_PASS',json.dumps({
        'vertices':len(p)//3,'quads':sum(r['quads'].values()),
        'triangles':len(ix)//3,'uvRegions':len(bounds),'guide':2048}))
if __name__=='__main__':run()
