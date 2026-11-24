#!/usr/bin/env python3
"""Verify real §E xatlas mesh geometry, distortion data and texture registration."""
import base64,hashlib,json,math,struct
from collections import Counter,defaultdict,deque
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
    assert struct.unpack('>II',b[16:24])==(w,h),p
    return b
def run():
    doc=json.loads(SCENE.read_text('utf8'))
    report=json.loads(REPORT.read_text('utf8'))
    assert doc['version']==11.554
    assert doc['project']['canonicalId']==doc['project']['template']=='clean-topology-humanoid'
    assert len(doc['project']['modelAtelier']['parts'])==1
    part=doc['project']['modelAtelier']['parts'][0]
    mesh=part['topologyMesh']
    pos=mesh['positions'];uv=mesh['uvs'];ix=mesh['indices']
    assert 2000<=len(pos)//3<=9000 and 2000<=len(ix)//3<=16000
    assert len(pos)%3==0 and len(uv)==len(pos)//3*2 and len(ix)%3==0
    assert all(isinstance(v,(float,int)) and math.isfinite(v) for v in pos+uv)
    assert all(-1e-7<=v<=1+1e-7 for v in uv)
    assert all(isinstance(i,int) and 0<=i<len(pos)//3 for i in ix)
    assert len(report['quads'])==6
    assert sum(report['quads'].values())*2==len(ix)//3
    assert report['revision']=='xatlas-anatomical-conformal-v4'
    assert report['uvAlgorithm']=='seamed-LSCM+verified-single-atlas-packer'
    assert report['uvMethod']=='LSCM+verified-chart-packing'
    assert report['uvPacking']=='deterministic-shelf'
    assert report['uvPaddingPixels']>=8
    assert report['uvLscmIterations']>=0
    assert report['uvPaintMode']=='xatlas-geometry-mask-true-checker'
    assert report['guideAnatomyLabels'] is True
    assert 1<=report['uvChartCount']<=92
    assert report['uvDegenerateTriangles']<=15
    assert report['uvAtlasSize'][0]>=1024 and report['uvAtlasSize'][1]>=1024
    assert report['uvTexelDensity']['trianglesChecked']>len(ix)//3*.98
    assert 1<=report['uvTexelDensity']['p95P05']<45
    assert base64.b64decode(part['uvPaintPNG'].split(',',1)[1])==png(PAINT,1024,1024)
    png(GUIDE,2048,2048)
    original=json.loads(ORIGINAL.read_text('utf8'))
    assert original['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert report['originalRobotPreserved'] is True
    # Check every physical triangle has positive area and is geometrically
    # manifold even though xatlas legitimately duplicates UV-seam vertices.
    xyz=[tuple(pos[i:i+3]) for i in range(0,len(pos),3)]
    unique={v:i for i,v in enumerate(sorted(set(xyz)))}
    weld=[unique[v] for v in xyz]
    edge=Counter();adj=defaultdict(set);area_bad=0
    for k in range(0,len(ix),3):
        tri=[weld[ix[k+i]] for i in range(3)]
        assert len(set(tri))==3,('degenerate 3D face',k)
        a,b,c=[xyz[ix[k+i]] for i in range(3)]
        v=[b[d]-a[d] for d in range(3)]
        w=[c[d]-a[d] for d in range(3)]
        mag=math.hypot(v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0])
        if mag<1.e-9:area_bad+=1
        for i in range(3):
            p,q=tri[i],tri[(i+1)%3]
            edge[tuple(sorted((p,q)))]+=1
            adj[p].add(q);adj[q].add(p)
    assert area_bad==0,('Geometrically degenerate triangles',area_bad)
    assert all(n==2 for n in edge.values()),('Open/nonmanifold seams',Counter(edge.values()))
    visited={weld[ix[0]]};stack=list(visited)
    while stack:
        k=stack.pop()
        for n in adj[k]:
            if n not in visited:visited.add(n);stack.append(n)
    assert len(visited)==len(unique),('Disconnected manifold components',len(visited),len(unique))
    assert report['topologyAudit']['connectedComponents']==1
    assert report['topologyAudit']['watertight']
    # Confirm waist/groin is an anatomical saddle, not a constant-height
    # rectangular panel or false texture cutout.
    pelvis=[xyz[i] for i in range(len(xyz))
            if 2.02<xyz[i][1]<2.49 and abs(xyz[i][0])<.56]
    central=[v[1] for v in pelvis if abs(v[0])<.08 and abs(v[2])<.10]
    lateral=[v[1] for v in pelvis if .28<abs(v[0])<.44 and abs(v[2])<.20]
    assert central and lateral and max(lateral)-min(central)>.10
    print('SE555_CONFORMAL_MESH_UV_AND_ANATOMY_PASS',json.dumps({
      'uvVertices':len(pos)//3,'triangles':len(ix)//3,
      'weldedVertices':len(unique),'charts':report['uvChartCount'],
      'openEdges':0,'densityP95P05':round(report['uvTexelDensity']['p95P05'],3),
      'textureSha256':hashlib.sha256(PAINT.read_bytes()).hexdigest(),
      'guideSha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest()}),flush=True)
if __name__=='__main__':run()
