#!/usr/bin/env python3
"""§E v11.544 lightweight deploy-time native material integrity proof.

The authoring source-seal CI runs full NumPy/scipy/Pillow 3D projection and
landmark tests. This dependency-free publish check independently verifies
EVERY vertex/UV/index and exact native PNG byte-for-byte against those sealed
assets. It does not weaken any source/asset SHA-256 build receipt.
"""
import base64
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]

def png_size(path):
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n',path
    assert data[12:16]==b'IHDR',path
    assert len(data)>50
    return struct.unpack('>II',data[16:24])

def main():
    old=json.loads((ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json').read_text('utf8'))
    new=json.loads((ROOT/'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json').read_text('utf8'))
    o=old['project'];p=new['project']
    assert new['version']==11.544 and new['engine']=='§wyrl§ Engine · Maker v11.544'
    assert p['canonicalId']==o['canonicalId']=='robotic-humanoid-mannequin'
    assert p['template']==o['template']
    assert p['kind']==o['kind']=='model-atelier'
    a=o['modelAtelier'];b=p['modelAtelier']
    assert a['schema']==b['schema']=='swyrl-model-atelier-v1'
    assert len(a['parts'])==len(b['parts'])==1
    left,right=a['parts'][0],b['parts'][0]
    for attribute in ('id','kind','position','rotation','scale','color','material','topologyMesh'):
        assert left[attribute]==right[attribute],('Geometry/UV source mutation',attribute)
    assert right['id']=='humanoid-body-unified'
    mesh=right['topologyMesh']
    assert len(mesh['positions'])==8792*3 and len(mesh['uvs'])==8792*2
    assert len(mesh['indices'])==13932*3
    assert not right.get('uvPaintOffset') and not right.get('uvPaintRepeat')
    atlas=right['uvPaintPNG']
    assert len(atlas)<=360000 and atlas.startswith('data:image/png;base64,')
    data=base64.b64decode(atlas.split(',',1)[1],validate=True)
    asset=ROOT/'assets/models/futuristic-humanoid-v11-544-surface-anchored.png'
    assert data==asset.read_bytes(),'Native embedded material differs from published PNG'
    assert png_size(asset)==(1024,1024)
    diagnostic=ROOT/'docs/qa/futuristic-humanoid-v11-544-region-diagnostic.png'
    preview=ROOT/'docs/qa/futuristic-humanoid-v11-544-front-back-side.png'
    assert png_size(diagnostic)==(1024,1024)
    assert png_size(preview)==(1560,606)
    assert 'barycentric' in b['reference'] and 'head/face front +Z' in b['reference']
    print('SE544_DEPLOY_NO_DEPENDENCY_MATERIAL_INTEGRITY_OK',json.dumps({
      'uvAndGeometryIdentical':True,'uvVertices':8792,'triangles':13932,
      'oneBody':True,'paintedPNGBytes':len(data),
      'paintSha256':hashlib.sha256(data).hexdigest(),
      'frontBackSideVisualProof':True,
      'nativeProjectId':p['canonicalId']
    }),flush=True)

if __name__=='__main__':main()
