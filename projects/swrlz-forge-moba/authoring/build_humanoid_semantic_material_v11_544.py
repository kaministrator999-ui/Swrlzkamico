#!/usr/bin/env python3
"""§E v11.544: actual geometry -> UV semantic robotic mannequin material.

NOT an image guessed from the shape of atlas islands. Every painted texel
comes from a barycentric point ON the existing 3D humanoid and its 3D normal.
A head pixel can therefore only originate from head triangles: no faces on
chests or painted fingers on waist/side panels.

The xatlas UVs, indices, geometry, topology, and owner projects remain exact.
The source is the v11.542 sealed native scene, not an external UV picture.
Dependencies only run during authoring in GitHub Actions, never on Moto/Quest.
"""
import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json'
DEST=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json'
PAINT=ROOT/'assets/models/futuristic-humanoid-v11-544-surface-anchored.png'
DIAGNOSTIC=ROOT/'docs/qa/futuristic-humanoid-v11-544-region-diagnostic.png'
RENDER=ROOT/'docs/qa/futuristic-humanoid-v11-544-front-back-side.png'
SIZE=1024
MAX_EMBEDDED=360000
ZONES=('head','arm','torso','leg')

def smooth(a,b,v):
    t=np.clip((v-a)/(b-a),0,1)
    return t*t*(3-2*t)

def band(v,target,half,feather):
    return 1-smooth(half,half+feather,np.abs(v-target))

def ellipse(a,b):
    return np.clip(1-(a*a+b*b),0,1)**1.4

def blend(rgb,color,weight):
    w=np.clip(weight,0,1).reshape(-1,1)
    rgb[:]=rgb*(1-w)+np.asarray(color,dtype=np.float64)*w

def labels(pts):
    x,y,z=pts.T
    arm=(np.abs(x)>.69)&(y>3.30)
    head=y>=4.08
    leg=y<=2.35
    return np.where(head,0,np.where(arm,1,np.where(leg,3,2))).astype(np.uint8)

def surface_paint(points,normals):
    x,y,z=points.T
    nx,ny,nz=normals.T
    xa=np.abs(x)
    front=smooth(.10,.50,nz)
    back=smooth(.12,.50,-nz)
    side=smooth(.36,.82,np.abs(nx))
    zones=labels(points)
    head=(zones==0).astype(float)
    arms=(zones==1).astype(float)
    torso=(zones==2).astype(float)
    legs=(zones==3).astype(float)
    # White porcelain-aluminum base: all color is 3D-point driven, never
    # UV-island shape-driven. No painted words, fake detached head or hands.
    shade=3*np.sin(12*x+7*z)+2*np.cos(14*y-11*z)
    rgb=np.stack([222+shade,230+shade,235+shade],axis=1)
    rgb=np.clip(rgb,0,255)

    # Anatomical faceplate (front +Z only) with helmet temples, narrow real
    # eye slits, chin and mouth. The head mask is a world-space *3D region*.
    blend(rgb,(76,91,104),head*smooth(.11,.19,xa)*smooth(4.22,4.30,y)*.87)
    blend(rgb,(245,247,245),head*front*ellipse(x/.205,(y-4.44)/.30)*.9)
    blend(rgb,(35,48,60),head*front*
          ellipse((xa-.085)/.050,(y-4.47)/.031)*.96)
    blend(rgb,(35,215,219),head*front*
          ellipse((xa-.085)/.027,(y-4.468)/.015)*.95)
    blend(rgb,(78,95,105),head*front*
          band(y,4.294,.006,.008)*band(x,0,.055,.025)*.65)
    blend(rgb,(53,65,78),head*smooth(4.05,4.15,4.18-y)*.8)
    # Back of the head reads as a separate ceramic helmet, not a face.
    blend(rgb,(79,96,109),head*back*band(x,0,.045,.027)*smooth(4.30,4.49,y)*.75)
    blend(rgb,(24,193,199),head*back*band(x,0,.012,.012)*band(y,4.48,.06,.03)*.65)

    # Shoulder cuffs, elbow/wrist articulation and forearm armor.
    for joint,half in ((.85,.048),(1.45,.060),(2.06,.052),(2.40,.030)):
        blend(rgb,(56,68,81),arms*band(xa,joint,half,.025)*.90)
    # Narrow metallic forearm shields; joints stay dark.
    blend(rgb,(241,244,241),arms*smooth(1.54,1.65,xa)*(1-smooth(1.99,2.07,xa))*.70)
    # Subtle dark arm vents are on the *outer/top* actual arm surface.
    vent=arms*band(y,3.70,.04,.026)*smooth(.50,.9,side)
    vent*=smooth(.93,1.02,xa)*(1-smooth(1.36,1.41,xa))
    blend(rgb,(58,70,83),vent*.85)
    # A thin luminous seam runs along the actual forearm, not a painted hand.
    blend(rgb,(23,190,202),arms*front*band(y,3.64,.008,.017)*
          smooth(1.54,1.64,xa)*(1-smooth(1.98,2.02,xa))*.85)
    # Real four fingertips + thumb are at X>2.45; only tiny accents there.
    blend(rgb,(68,84,96),arms*smooth(2.44,2.52,xa)*
          band(xa,2.60,.014,.022)*.78)

    # Actual torso front (not an atlas rectangle guessed to be "chest").
    chest=torso*front*smooth(3.15,3.28,y)*(1-smooth(3.75,3.90,y))
    blend(rgb,(240,243,241),chest*(1-smooth(.45,.60,xa))*.66)
    # Plaque seam sloping down toward sternum at real 3D coordinates.
    yoke=3.51-.18*np.clip(xa/.51,0,1)
    blend(rgb,(77,91,104),chest*band(y,yoke,.008,.015)*
          (1-smooth(.53,.65,xa))*.80)
    blend(rgb,(60,73,87),torso*front*band(x,0,.019,.014)*
          smooth(3.21,3.38,y)*(1-smooth(3.65,3.73,y))*.75)
    blend(rgb,(27,207,209),torso*front*band(x,0,.035,.022)*
          band(y,3.54,.017,.023)*.92)

    # Mechanical abdominal insert and rib plate rows remain only on torso.
    core=torso*front*smooth(2.64,2.80,y)*(1-smooth(3.16,3.29,y))
    blend(rgb,(72,83,96),core*(1-smooth(.18,.33,xa))*.84)
    ribs=np.sin((y-2.70)*33)
    blend(rgb,(188,199,206),core*(1-smooth(.17,.30,xa))*
          smooth(.55,.90,ribs)*.66)
    # Lateral graphite ribs, a pelvic belt and joint segments.
    blend(rgb,(91,105,118),torso*side*smooth(2.78,2.93,y)*
          (1-smooth(3.64,3.80,y))*.61)
    blend(rgb,(64,78,90),torso*band(y,2.50,.055,.048)*.74)
    # The BACK is -Z. Central spine and its cyan markers cannot land on face.
    spine=torso*back*smooth(2.62,2.81,y)*(1-smooth(3.66,3.81,y))
    blend(rgb,(63,77,90),spine*band(x,0,.080,.057)*.85)
    spine_segments=(np.cos((y-2.71)*24)+1)/2
    blend(rgb,(30,198,201),spine*band(x,0,.014,.014)*
          smooth(.89,.99,spine_segments)*.9)

    # Real legs from 3D Y: thigh/shin armor and mechanical knee/ankle rings.
    for joint,half in ((2.18,.065),(1.03,.10),(.31,.05)):
        blend(rgb,(65,78,92),legs*band(y,joint,half,.026)*.90)
    blend(rgb,(245,246,242),legs*front*smooth(.42,.64,y)*
          (1-smooth(1.93,2.12,y))*.54)
    # Front shin plates are based on position + normal, not planar silhouette.
    shin=legs*front*smooth(.37,.55,y)*(1-smooth(.89,1.02,y))
    blend(rgb,(71,84,97),shin*band(xa,.36,.065,.055)*.83)
    blend(rgb,(33,204,208),shin*band(xa,.36,.010,.015)*
          band(y,.71,.16,.08)*.74)
    # Thigh armor trim; foot shell stays white with subtle toe seam.
    thigh=legs*front*smooth(1.20,1.41,y)*(1-smooth(1.89,2.09,y))
    blend(rgb,(82,96,109),thigh*band(xa,.37,.035,.043)*.5)
    blend(rgb,(37,189,197),thigh*band(y,1.73,.009,.015)*
          band(xa,.37,.060,.025)*.76)
    foot=legs*(1-smooth(.21,.34,y))*smooth(.12,.25,z)
    blend(rgb,(246,247,245),foot*.70)
    blend(rgb,(83,97,107),foot*band(y,.10,.009,.012)*.45)
    # Minimal 3D-space etched lines; seam continuity is automatic on xatlas.
    fine=np.minimum(
        np.abs(np.sin(18*x+3*y-8*z)),
        np.abs(np.sin(19*y+5*z)))
    etch=smooth(.028,.003,fine)
    blend(rgb,(145,162,172),(torso+arms+legs)*etch*.12)
    return np.clip(np.rint(rgb),0,255).astype(np.uint8),zones

def model():
    scene=json.loads(SOURCE.read_text('utf8'))
    part=scene['project']['modelAtelier']['parts'][0]
    t=part['topologyMesh']
    xyz=np.asarray(t['positions'],dtype=np.float64).reshape(-1,3)
    uv=np.asarray(t['uvs'],dtype=np.float64).reshape(-1,2)
    faces=np.asarray(t['indices'],dtype=np.int64).reshape(-1,3)
    assert len(xyz)==8792 and len(faces)==13932
    assert part['id']=='humanoid-body-unified'
    assert np.isfinite(xyz).all() and np.isfinite(uv).all()
    # Calculate continuous, area-weighted surface normals across UV seam
    # duplicates by welding equal 3D positions for *normals only*.
    _,inv=np.unique(xyz,axis=0,return_inverse=True)
    welded=np.zeros((inv.max()+1,3),dtype=np.float64)
    tris=xyz[faces]
    fn=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
    for k in range(3):
        np.add.at(welded,inv[faces[:,k]],fn)
    mag=np.linalg.norm(welded,axis=1)
    welded/=np.maximum(mag[:,None],1e-12)
    return scene,part,xyz,uv,faces,welded[inv]

def bake(xyz,uv,faces,normals):
    width=SIZE
    out=np.zeros((width,width,3),dtype=np.uint8)
    region=np.full((width,width),255,dtype=np.uint8)
    covered=np.zeros((width,width),dtype=np.bool_)
    uvp=np.column_stack((uv[:,0],1-uv[:,1]))*(width-1)
    collisions=0
    for inds in faces:
        local=uvp[inds]
        cross=((local[1,0]-local[0,0])*(local[2,1]-local[0,1])-
               (local[2,0]-local[0,0])*(local[1,1]-local[0,1]))
        if abs(cross)<1e-8:
            raise ValueError('UV triangle collapsed')
        lo=np.maximum(np.floor(local.min(axis=0)).astype(int)-1,0)
        hi=np.minimum(np.ceil(local.max(axis=0)).astype(int)+1,width-1)
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),
                          np.arange(lo[1],hi[1]+1))
        w1=((xx-local[0,0])*(local[2,1]-local[0,1])-
            (yy-local[0,1])*(local[2,0]-local[0,0]))/cross
        w2=((yy-local[0,1])*(local[1,0]-local[0,0])-
            (xx-local[0,0])*(local[1,1]-local[0,1]))/cross
        w0=1-w1-w2
        valid=(w0>=-1e-6)&(w1>=-1e-6)&(w2>=-1e-6)
        if not valid.any():continue
        # Barycentric world-space samples, NOT a UV-island guess.
        p=w0[valid,None]*xyz[inds[0]]+w1[valid,None]*xyz[inds[1]]+w2[valid,None]*xyz[inds[2]]
        n=w0[valid,None]*normals[inds[0]]+w1[valid,None]*normals[inds[1]]+w2[valid,None]*normals[inds[2]]
        n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-10)
        rgb,tags=surface_paint(p,n)
        py=yy[valid];px=xx[valid]
        collisions+=int(np.count_nonzero(covered[py,px]))
        out[py,px]=rgb
        region[py,px]=tags
        covered[py,px]=True
    used=int(np.count_nonzero(covered))
    assert used>width*width*.25,used
    assert collisions/max(used,1)<.15,('unsafe UV overlaps',collisions,used)
    counts=Counter(region[covered].tolist())
    assert all(counts[i]>8000 for i in range(4)),('missing anatomy paint',counts)
    # Bleed each edge color into its 5-pixel mip gutter.
    distance,indices=distance_transform_edt(~covered,return_indices=True)
    pad=(distance<=5)&(~covered)
    out[pad]=out[indices[0][pad],indices[1][pad]]
    region[pad]=region[indices[0][pad],indices[1][pad]]
    out[~(covered|pad)]=[200,205,209]
    return out,region,{
        'coveredPct':round(used/(width*width)*100,2),
        'overlaps':collisions,
        'regionTexels':{name:int(counts[i]) for i,name in enumerate(ZONES)}
    }

def export_png(arr,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    mem=BytesIO()
    Image.fromarray(arr,'RGB').save(mem,format='PNG',optimize=True)
    data=mem.getvalue()
    # Use indexed color palette only if needed to honor the native part limit;
    # keep exact RGB appearance when it already fits.
    if len(base64.b64encode(data))+22>MAX_EMBEDDED:
        im=Image.fromarray(arr,'RGB').quantize(colors=96,
             method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE)
        mem=BytesIO(); im.save(mem,format='PNG',optimize=True)
        data=mem.getvalue()
    assert len(base64.b64encode(data))+22<=MAX_EMBEDDED,('texture over native limit',len(data))
    path.write_bytes(data)
    return data

def render_view(color,xyz,uv,faces,axis,back):
    # Orthographic, UV-material-sampled renderer using a depth buffer. This
    # independent projection is the exact 3D->texture placement QA receipt.
    width=520;height=570
    if axis=='front':
        xx=(-xyz[:,0] if back else xyz[:,0]);depth=(-xyz[:,2] if back else xyz[:,2])
    else:
        xx=xyz[:,2];depth=xyz[:,0]
    yp=xyz[:,1]
    # Full T-pose fits; arms are horizontal along X.
    if axis=='front':
        sx=(xx+2.95)/5.90*(width-1)
    else:
        sx=(xx+.52)/1.04*(width-1)
    sy=(4.95-yp)/4.95*(height-1)
    screen=np.column_stack((sx,sy))
    framebuffer=np.full((height,width,3),[19,26,41],dtype=np.uint8)
    zbuf=np.full((height,width),-np.inf,dtype=np.float64)
    tex=np.asarray(color,dtype=np.uint8)
    h,w=tex.shape[:2]
    for face in faces:
        pos=screen[face];dep=depth[face]
        cross=((pos[1,0]-pos[0,0])*(pos[2,1]-pos[0,1])-
               (pos[2,0]-pos[0,0])*(pos[1,1]-pos[0,1]))
        if abs(cross)<1e-7:continue
        lo=np.maximum(np.floor(pos.min(axis=0)).astype(int)-1,0)
        hi=np.minimum(np.ceil(pos.max(axis=0)).astype(int)+1,[width-1,height-1])
        if lo[0]>hi[0] or lo[1]>hi[1]:continue
        px,py=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
        b=((px-pos[0,0])*(pos[2,1]-pos[0,1])-
           (py-pos[0,1])*(pos[2,0]-pos[0,0]))/cross
        c=((py-pos[0,1])*(pos[1,0]-pos[0,0])-
           (px-pos[0,0])*(pos[1,1]-pos[0,1]))/cross
        a=1-b-c
        inside=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)
        if not inside.any():continue
        z=a*dep[0]+b*dep[1]+c*dep[2]
        inside&=z>zbuf[py,px]
        if not inside.any():continue
        uvp=uv[face]
        u=a[inside]*uvp[0,0]+b[inside]*uvp[1,0]+c[inside]*uvp[2,0]
        v=a[inside]*uvp[0,1]+b[inside]*uvp[1,1]+c[inside]*uvp[2,1]
        tx=np.clip(np.rint(u*(w-1)).astype(int),0,w-1)
        ty=np.clip(np.rint((1-v)*(h-1)).astype(int),0,h-1)
        framebuffer[py[inside],px[inside]]=tex[ty,tx]
        zbuf[py[inside],px[inside]]=z[inside]
    return Image.fromarray(framebuffer,'RGB')

def diagnostic(rgb,tags):
    palette=np.array([[221,76,76],[245,186,65],[69,202,136],[88,135,235]],np.uint8)
    img=np.full(rgb.shape,[26,32,45],dtype=np.uint8)
    for i in range(4):img[tags==i]=palette[i]
    DIAGNOSTIC.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(img,'RGB').save(DIAGNOSTIC,optimize=True)

def main():
    scene,part,xyz,uv,faces,normals=model()
    texture,regions,metrics=bake(xyz,uv,faces,normals)
    blob=export_png(texture,PAINT)
    # Validate geometry-derived semantic atlas independently of the rendered
    # PNG: each colored texel was sampled from a 3D position and normal.
    diagnostic(texture,regions)
    renders=[
       ('FRONT +Z',render_view(texture,xyz,uv,faces,'front',False)),
       ('BACK -Z',render_view(texture,xyz,uv,faces,'front',True)),
       ('LEFT SIDE',render_view(texture,xyz,uv,faces,'side',False))]
    proof=Image.new('RGB',(520*3,606),(19,26,41))
    draw=ImageDraw.Draw(proof)
    for i,(title,im) in enumerate(renders):
        proof.paste(im,(i*520,36))
        draw.text((i*520+12,12),title,fill=(220,233,239))
    RENDER.parent.mkdir(parents=True,exist_ok=True)
    proof.save(RENDER,'PNG',optimize=True)
    part['uvPaintPNG']='data:image/png;base64,'+base64.b64encode(blob).decode('ascii')
    part.pop('uvPaintOffset',None);part.pop('uvPaintRepeat',None)
    part['name']='Futuristic Humanoid · surface-anchored robotic paint'
    scene['engine']='§wyrl§ Engine · Maker v11.544'
    scene['version']=11.544
    scene['project']['name']='Futuristic Humanoid · Mapped Robot Material'
    scene['project']['modelAtelier']['name']='Futuristic Humanoid · True 3D-Anchored Material'
    scene['project']['modelAtelier']['reference']=(
      'One continuous five-digit humanoid with unchanged xatlas-relaxed 84-chart '
      'UVs. Every paint texel is computed by barycentric interpolation of '
      'the original real 3D surface, with body-region semantics in local 3D '
      'coordinates: head/face front +Z, chest +Z, back -Z, horizontal arms +X/-X, '
      'legs below hips. No manually guessed 2D atlas island anatomy. Original '
      'geometry, UV indices, coordinates, and saved projects are preserved. '
      'Not rigged. v11.544 repaired procedural material can be restored on '
      'the v11.542 UV-compatible selected mesh via UV Editor.')
    DEST.write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')),'utf8')
    print('SE544_GEOMETRY_ANCHORED_MATERIAL_OK',json.dumps({
      'textureBytes':len(blob),'embeddedChars':len(part['uvPaintPNG']),
      'previewBytes':RENDER.stat().st_size,
      'diagnosticBytes':DIAGNOSTIC.stat().st_size,
      'triangles':len(faces),'uvVertices':len(xyz),**metrics}),flush=True)

if __name__=='__main__':main()
