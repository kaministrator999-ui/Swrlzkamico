#!/usr/bin/env python3
"""§E v11.546: dependency-free source geometry, atlas and skin gate."""
import base64
from collections import Counter
import json,math,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'
N=R/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'
P=R/'assets/models/futuristic-humanoid-v11-546-anatomical-robot.png'
U=R/'assets/models/futuristic-humanoid-v11-546-uv-guide-4096.png'
A=R/'assets/models/futuristic-humanoid-v11-546-anatomy-4096.png'
M=R/'docs/qa/futuristic-humanoid-v11-546-metrics.json'
V=R/'docs/qa/futuristic-humanoid-v11-546-views.png'
def image(path,dim):
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert tuple(struct.unpack('>II',data[16:24]))==dim
    assert len(data)<10_000_000,(path,len(data))
    return data
def geometry(mesh):
    pos=[tuple(round(float(t),5) for t in mesh['positions'][i:i+3]) for i in range(0,len(mesh['positions']),3)]
    idx=mesh['indices']
    return Counter(tuple(sorted(pos[j] for j in idx[i:i+3])) for i in range(0,len(idx),3))
def main():
    prev=json.loads(O.read_text('utf8'));now=json.loads(N.read_text('utf8'))
    assert now['version']==11.546
    old=prev['project'];new=now['project']
    assert old['canonicalId']==new['canonicalId']=='robotic-humanoid-mannequin'
    a=old['modelAtelier']['parts'][0];b=new['modelAtelier']['parts'][0]
    for name in ('id','kind','position','rotation','scale','color','material'):
        assert a[name]==b[name],name
    o=a['topologyMesh'];n=b['topologyMesh']
    assert len(n['positions'])//3<=9000
    assert len(n['indices'])==len(o['indices'])==13932*3
    assert len(n['uvs'])==2*(len(n['positions'])//3)
    assert geometry(o)==geometry(n),'3D triangles were changed'
    assert all(math.isfinite(float(x)) and 0<=x<=1 for x in n['uvs'])
    assert n['uvs']!=o['uvs'],'Expected an actual new UV mapping'
    payload=base64.b64decode(b['uvPaintPNG'].split(',',1)[1],validate=True)
    assert payload==image(P,(1024,1024)),'Native paint differs from new baked PNG'
    assert len(b['uvPaintPNG'])<=360000
    image(U,(4096,4096));image(A,(4096,4096));image(V,(1560,606))
    assert not b.get('uvPaintRepeat') and not b.get('uvPaintOffset')
    metric=json.loads(M.read_text('utf8'))
    assert metric['vertices']<=9000 and metric['triangles']==13932
    assert metric['guideSize']==4096 and metric['originalGeometryUnchanged']
    assert len(metric['regionTriangles'])>=6
    # New xatlas path never combines front/back torso into a cylindrical sheet.
    # It may split each region into genuine relaxed UV charts to eliminate
    # foldovers around shoulders, fingers, ankles and scalp.
    assert metric['strategy'] in ('eight','seven'),metric['strategy']
    required={'chest','back','leftArm','rightArm','leftLeg','rightLeg'}
    required|=({'headFront','headBack'} if metric['strategy']=='eight' else {'head'})
    assert set(metric['regionTriangles'])==required,metric['regionTriangles']
    assert set(metric['uvShells'])==required,metric['uvShells']
    assert all(1<=metric['uvShells'][name]<=48 for name in required)
    assert metric['charts']==sum(metric['uvShells'].values()),'chart mismatch'
    assert 7<=metric['charts']<=120,metric['charts']
    assert metric['sharedEdgeSamples']>=0
    assert metric['conflictingSamples']<=80,('UV surface collisions',metric['conflictingSamples'])
    assert metric['conflictPct']<=.15,('UV overlap exceeds new quality budget',metric['conflictPct'])
    assert set(metric['conflictsByRegion']).issubset(required)
    # Front center of helmet must remain in the face/head region, not the
    # back-of-head or a torso island. Orientation within the actual chart is
    # controlled by xatlas and must NOT be faked with a shifted screenshot.
    pos=[n['positions'][i:i+3] for i in range(0,len(n['positions']),3)]
    uv=[n['uvs'][i:i+2] for i in range(0,len(n['uvs']),2)]
    helmet_front=[uv[i] for i,(x,y,z) in enumerate(pos)
                  if y>4.2 and z>.14 and abs(x)<.08]
    assert len(helmet_front)>20,'Missing frontal helmet geometry'
    face_box=(.008,.122) if metric['strategy']=='eight' else (.008,.245)
    assert all(face_box[0]-.002<=u<=face_box[1]+.002 for u,v in helmet_front),(
        'Front helmet not mapped into head-front island',helmet_front[:5])
    assert metric['coveredPct']>25
    assert metric['p95P5Density']<55
    assert len(N.read_bytes())<2_000_000
    print('SE546_ANATOMY_ROBOT_ASSETS_PASS',json.dumps({
        'vertices':len(n['positions'])//3,'triangles':13932,
        'geometryUnchanged':True,'newUV':True,'newSkin':True,
        'guideResolution':4096,'paintBytes':len(payload),
        'strategy':metric['strategy'],'charts':metric['charts']}))
if __name__=='__main__':main()
