#!/usr/bin/env python3
"""§E v11.542: xatlas unwrap for the continuous five-digit humanoid.

Consumes the previously validated v11.540 asset and produces a *new* v11.542
native starter. Welds display-only old UV seam duplicates before unwrapping;
keeps original geometric triangles, then bakes the existing PNG into the new
non-overlapping charts using trianglewise barycentric texture transfer.

No authoring dependencies are shipped to user devices. Existing saves and
v11.540 assets are untouched. No pseudo-UV cone/rim projection is used.
"""
import base64
from collections import defaultdict
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
import xatlas

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'
DEST=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json'
GUIDE=ROOT/'assets/models/futuristic-humanoid-v11-542-uv-guide.png'
ATLAS_SIZE=1024
PAINT_LIMIT=360000
VERT_LIMIT=9000
FACE_LIMIT=16000

def source_mesh():
    original=json.loads(SOURCE.read_text('utf8'))
    part=original['project']['modelAtelier']['parts'][0]
    src=part['topologyMesh']
    p=np.asarray(src['positions'],dtype=np.float32).reshape(-1,3)
    u=np.asarray(src['uvs'],dtype=np.float32).reshape(-1,2)
    f=np.asarray(src['indices'],dtype=np.int64).reshape(-1,3)
    # Native display has duplicates at the old atlas seams; real geometry
    # must have each 3D point only once during parameterization.
    welded, inverse=np.unique(p,axis=0,return_inverse=True)
    faces=inverse[f].astype(np.uint32)
    assert len(welded)>4000 and len(faces)>12000
    assert len(faces)<=FACE_LIMIT
    assert np.all(faces[:,0]!=faces[:,1]) and np.all(faces[:,1]!=faces[:,2])
    assert np.all(faces[:,0]!=faces[:,2])
    # Every welded triangle maps to its preexisting paint UV corner, allowing
    # transfer even when xatlas rotates or reorders that face.
    corner_uv={}
    for i,ids in enumerate(faces):
        key=tuple(sorted(int(k) for k in ids))
        assert key not in corner_uv,'duplicate geometry triangle'
        corner_uv[key]={int(idx):tuple(map(float,pt))
                        for idx,pt in zip(ids,u[f[i]])}
    return original,part,welded,faces,corner_uv

def unwrap(positions,faces):
    atlas=xatlas.Atlas()
    atlas.add_mesh(np.ascontiguousarray(positions,dtype=np.float32),
                   np.ascontiguousarray(faces,dtype=np.uint32))
    options=xatlas.PackOptions()
    options.resolution=ATLAS_SIZE
    options.padding=5
    atlas.generate(pack_options=options)
    vmap,new_f,uv=atlas[0]
    vmap=np.asarray(vmap,dtype=np.int64)
    new_f=np.asarray(new_f,dtype=np.int64).reshape(-1,3)
    uv=np.asarray(uv,dtype=np.float64).reshape(-1,2)
    if len(vmap)>VERT_LIMIT:
        raise ValueError('Atlas UV seams exceed native '+str(VERT_LIMIT)+
                         ' vertex limit: '+str(len(vmap)))
    assert len(new_f)==len(faces)
    assert np.isfinite(uv).all() and uv.min()>=-1e-7 and uv.max()<=1+1e-7
    assert np.isfinite(positions[vmap]).all()
    chart_count=atlas.get_mesh_chart_count(0)
    assert 2<=chart_count<=200,chart_count
    return positions[vmap],new_f,np.clip(uv,0,1),vmap,chart_count

def texture_transfer(old_png,source_uv,uv,faces,vmap,old_offset):
    _,encoded=old_png.split(',',1)
    image=Image.open(BytesIO(base64.b64decode(encoded))).convert('RGB')
    old=np.asarray(image,dtype=np.uint8)
    size=ATLAS_SIZE
    out=np.zeros((size,size,3),dtype=np.uint8)
    covered=np.zeros((size,size),dtype=np.bool_)
    collision=0
    uv_px=np.stack([uv[:,0]*(size-1),(1-uv[:,1])*(size-1)],axis=1)
    for tri in faces:
        loc=uv_px[tri];cross=((loc[1,0]-loc[0,0])*(loc[2,1]-loc[0,1])-
                               (loc[2,0]-loc[0,0])*(loc[1,1]-loc[0,1]))
        if abs(cross)<1e-6:continue
        lo=np.maximum(np.floor(loc.min(axis=0)).astype(int)-1,0)
        hi=np.minimum(np.ceil(loc.max(axis=0)).astype(int)+1,size-1)
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),
                          np.arange(lo[1],hi[1]+1))
        w1=((xx-loc[0,0])*(loc[2,1]-loc[0,1])-
            (yy-loc[0,1])*(loc[2,0]-loc[0,0]))/cross
        w2=((yy-loc[0,1])*(loc[1,0]-loc[0,0])-
            (xx-loc[0,0])*(loc[1,1]-loc[0,1]))/cross
        w0=1-w1-w2
        inside=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
        if not inside.any():continue
        # The new triangle is mapped to the equivalent *original* geometric
        # triangle, including original seam-corner texture coordinates.
        key=tuple(sorted(int(vmap[i]) for i in tri))
        src=source_uv.get(key)
        if src is None:raise ValueError('Atlas changed the source face topology')
        old_uv=np.array([src[int(vmap[i])] for i in tri],dtype=np.float64)
        uu=w0*old_uv[0,0]+w1*old_uv[1,0]+w2*old_uv[2,0]
        vv=w0*old_uv[0,1]+w1*old_uv[1,1]+w2*old_uv[2,1]
        # Old atlas is OpenGL UV coordinates, PNG image begins at top-left.
        # Existing PNG Offset is accounted for in the baked pixels.
        px=np.clip(np.round((uu+old_offset[0])*(old.shape[1]-1)).astype(int),0,old.shape[1]-1)
        py=np.clip(np.round((1-(vv+old_offset[1]))*(old.shape[0]-1)).astype(int),0,old.shape[0]-1)
        out[yy[inside],xx[inside]]=old[py[inside],px[inside]]
        collision+=np.count_nonzero(covered[yy[inside],xx[inside]])
        covered[yy[inside],xx[inside]]=True
    coverage=np.count_nonzero(covered)
    assert coverage>size*size*.12,('atlas used area too low',coverage)
    # Pixel collision includes adjacent triangle raster edge rounding. Gross
    # self-overlap is still rejected by the independent geometric test.
    assert collision/max(1,coverage)<.25,('UV charts overlap too much',collision,coverage)
    # Bleed original edge colors 5px into atlas gutters to avoid mip seams.
    distance,nearest=distance_transform_edt(~covered,return_indices=True)
    pads=(distance<=5)&(~covered)
    out[pads]=out[nearest[0][pads],nearest[1][pads]]
    out[~(covered|pads)]=[196,205,213]
    png=BytesIO()
    Image.fromarray(out,mode='RGB').save(png,format='PNG',optimize=True)
    data=base64.b64encode(png.getvalue()).decode('ascii')
    if len(data)+22>PAINT_LIMIT:
        # The native material image field caps encoded bytes. Quantize the
        # largely flat sci-fi palette without altering the geometry/UVs.
        q=Image.fromarray(out,mode='RGB').quantize(colors=64)
        png=BytesIO();q.save(png,format='PNG',optimize=True)
        data=base64.b64encode(png.getvalue()).decode('ascii')
    assert len(data)+22<=PAINT_LIMIT,('native painted PNG exceeds limit',len(data))
    return 'data:image/png;base64,'+data,round(coverage/size**2,4),round(collision/max(1,coverage),4)

def guide_image(uv,faces):
    s=2048
    img=Image.new('RGB',(s,s),(18,26,39))
    d=ImageDraw.Draw(img)
    # Fine neutral checker makes island shapes and empty margins legible.
    for y in range(0,s,128):
        for x in range(0,s,128):
            if (x//128+y//128)%2==0:d.rectangle((x,y,x+127,y+127),fill=(27,38,51))
    coords=np.rint(np.column_stack((uv[:,0],1-uv[:,1]))*(s-1)).astype(int)
    # Draw each triangle only once. Wireframe remains a diagnostic overlay,
    # not a texture to import on the model.
    for ids in faces:
        p=[tuple(map(int,coords[i])) for i in ids]
        d.line([p[0],p[1],p[2],p[0]],fill=(45,225,223),width=1)
    GUIDE.parent.mkdir(parents=True,exist_ok=True)
    img.save(GUIDE,format='PNG',optimize=True)

def audit(positions,faces,uv):
    # Triangle area/density measures whether the mapping is usable for paint,
    # rather than merely within numeric 0..1 UV bounds.
    xyz=positions[faces]
    p=uv[faces]
    wa=np.linalg.norm(np.cross(xyz[:,1]-xyz[:,0],xyz[:,2]-xyz[:,0]),axis=1)*.5
    ua=np.abs(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]))*.5
    assert (wa>1e-9).all(),'zero-area source triangles'
    assert np.count_nonzero(ua<1e-10)<max(3,len(ua)*.001),'UV triangles collapsed'
    total_uv=float(np.sum(ua))
    assert .12<total_uv<1.00,('poor atlas utilization / overlaps',total_uv)
    density=ua/wa
    valid=density>1e-8
    ratio=float(np.percentile(density[valid],95)/np.percentile(density[valid],5))
    assert ratio<100,('severe texel density distortion',ratio)
    return {'uvArea':round(total_uv,4),'p95ToP5Density':round(ratio,2)}

def main():
    scene,part,vertices,faces,old_uv=source_mesh()
    baked,new_faces,uv,vmap,charts=unwrap(vertices,faces)
    previous=part['uvPaintPNG']
    png,occupancy,collisions=texture_transfer(
        previous,old_uv,uv,new_faces,vmap,part.get('uvPaintOffset',[0,0]))
    metrics=audit(baked,new_faces,uv)
    mesh=part['topologyMesh']
    mesh['positions']=np.round(baked,5).ravel().tolist()
    mesh['uvs']=np.round(uv,6).ravel().tolist()
    mesh['indices']=new_faces.astype(int).ravel().tolist()
    part['uvPaintPNG']=png
    part.pop('uvPaintOffset',None)
    part.pop('uvPaintRepeat',None)
    part['name']='Futuristic Humanoid · relaxed non-overlapping paint atlas'
    scene['engine']='§wyrl§ Engine · Maker v11.542'
    scene['version']=11.542
    scene['project']['name']='Futuristic Humanoid · UV-Ready Detailed Hands'
    scene['project']['modelAtelier']['name']='Futuristic Humanoid · Paint-Ready UV Atlas'
    scene['project']['modelAtelier']['reference']=(
      'One continuous five-digit robotic humanoid. xatlas-relaxed and packed '
      'native UVs with separate real chart seams and reprojection of the existing '
      'satin / graphite / teal material PNG. No hat-style front/back/brim atlas. '
      'Original geometry proportions and face count remain unchanged. Not skinned.')
    DEST.write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')),'utf8')
    guide_image(uv,new_faces)
    print('SE542_RELAXED_UV_ATLAS_BAKED',json.dumps({
      'charts':charts,'originalGeometricVertices':len(vertices),
      'uvVertices':len(baked),'triangles':len(new_faces),
      'occupancy':occupancy,'rasterCollisions':collisions,
      'materialChars':len(png),'sceneBytes':DEST.stat().st_size,
      'guideBytes':GUIDE.stat().st_size,**metrics}),flush=True)

if __name__=='__main__':
    main()
