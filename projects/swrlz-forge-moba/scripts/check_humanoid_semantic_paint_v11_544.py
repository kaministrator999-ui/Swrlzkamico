#!/usr/bin/env python3
"""§E v11.544: independent body/UV and atlas texture-landing regression."""
import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json'
NEW=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json'
PNG=ROOT/'assets/models/futuristic-humanoid-v11-544-surface-anchored.png'
DIAGNOSTIC=ROOT/'docs/qa/futuristic-humanoid-v11-544-region-diagnostic.png'
RENDER=ROOT/'docs/qa/futuristic-humanoid-v11-544-front-back-side.png'
sys.path.insert(0,str(ROOT/'authoring'))
from build_humanoid_semantic_material_v11_544 import surface_paint,labels

def main():
    a=json.loads(OLD.read_text('utf8'))
    b=json.loads(NEW.read_text('utf8'))
    assert b['version']==11.544
    assert a['project']['canonicalId']==b['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert a['project']['template']==b['project']['template']
    assert a['project']['modelAtelier']['schema']==b['project']['modelAtelier']['schema']
    assert len(a['project']['modelAtelier']['parts'])==len(b['project']['modelAtelier']['parts'])==1
    ap=a['project']['modelAtelier']['parts'][0]
    bp=b['project']['modelAtelier']['parts'][0]
    for attr in ('id','kind','position','rotation','scale','color','material','topologyMesh'):
        assert ap[attr]==bp[attr],('Never rewrite geometry/UV data',attr)
    assert len(bp['topologyMesh']['positions'])==8792*3
    assert len(bp['topologyMesh']['indices'])==13932*3
    assert len(bp['topologyMesh']['uvs'])==8792*2
    assert len(bp['uvPaintPNG'])<=360000
    assert bp.get('uvPaintOffset') is None and bp.get('uvPaintRepeat') is None
    prefix,encoded=bp['uvPaintPNG'].split(',',1)
    assert prefix=='data:image/png;base64'
    data=base64.b64decode(encoded,validate=True)
    assert data==PNG.read_bytes(),'Shipped PNG must match exact native texture'
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    assert struct.unpack('>II',data[16:24])==(1024,1024)
    material=Image.open(BytesIO(data)).convert('RGB')
    assert material.getpixel((512,512))!=(0,255,255),'Wireframe contamination'
    colors=np.asarray(material)
    assert colors.shape==(1024,1024,3)
    assert colors.min()<35 and colors.max()>235,('robotic palette',colors.min(),colors.max())
    assert DIAGNOSTIC.exists() and Image.open(DIAGNOSTIC).size==(1024,1024)
    assert RENDER.exists() and Image.open(RENDER).size==(1560,606)
    # Semantic 3D probes: the face detail is produced exclusively by a point
    # above the neck, NEVER by a UV island that merely looks head-shaped.
    coords=np.array([
        [.085,4.47,.23],[-.085,4.47,.23], # two front-head eye loci
        [.085,3.54,.17],                # chest, NOT face
        [0,3.0,-.16],                  # back, NOT face
        [2.59,3.65,.02],[-2.59,3.65,.02], # actual fingertip sides
        [.37,1.0,.15],[-.37,1.0,.15],  # knee loci
    ],np.float64)
    normals=np.array([[0,0,1],[0,0,1],[0,0,1],[0,0,-1],
                      [1,0,0],[-1,0,0],[0,0,1],[0,0,1]],np.float64)
    rgb,zone=surface_paint(coords,normals)
    assert zone.tolist()==[0,0,2,2,1,1,3,3],('semantic anatomy mapping',zone)
    assert int(rgb[0,1])>int(rgb[0,0]) and int(rgb[0,1])>150,('head eyes not lit',rgb[0])
    assert np.max(np.abs(rgb[0].astype(int)-rgb[2].astype(int)))>60,('chest erroneously inherits face paint')
    # A true front/back render: UV-mapped pixels from geometry, not a photo.
    view=np.asarray(Image.open(RENDER).convert('RGB'))
    # Confirm all projections include visible model content rather than blank.
    for i in range(3):
        image=view[36:,i*520:(i+1)*520]
        differing=np.count_nonzero(np.max(np.abs(image.astype(int)-[19,26,41]),axis=2)>30)
        assert differing>4000,('empty projection',i,differing)
    print('SE544_SURFACE_PAINT_GEOMETRY_AND_UV_OK',json.dumps({
        'geometryAndUVIdentical':True,'materialBytes':len(data),
        'parts':1,'uvVertices':8792,'triangles':13932,
        'zones':[int(x) for x in zone],'frontBackSideQA':True,'nativeProjectId':b['project']['canonicalId']
    }),flush=True)

if __name__=='__main__':main()
