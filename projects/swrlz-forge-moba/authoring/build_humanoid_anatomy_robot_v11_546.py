#!/usr/bin/env python3
"""§E v11.546: anatomical humanoid UV atlas and NEW surface-baked robot skin.

Authoring-only: true 3D mesh -> seam-aware anatomical shells -> one UV atlas ->
brand-new robotic paint. Never applies an old texture to changed UVs.
Preserves 3D triangle geometry and the historical user/project files.
"""
import base64
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import xatlas
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'
OUTPUT=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'
PAINT=ROOT/'assets/models/futuristic-humanoid-v11-546-anatomical-robot.png'
GUIDE=ROOT/'assets/models/futuristic-humanoid-v11-546-uv-guide-4096.png'
ANATOMY=ROOT/'assets/models/futuristic-humanoid-v11-546-anatomy-4096.png'
PREVIEW=ROOT/'docs/qa/futuristic-humanoid-v11-546-views.png'
REPORT=ROOT/'docs/qa/futuristic-humanoid-v11-546-metrics.json'
sys.path.insert(0,str(ROOT/'authoring'))
import build_humanoid_semantic_material_v11_544 as bakery
assert SOURCE.exists()

REGIONS=['head','chest','back','leftArm','rightArm','leftLeg','rightLeg']
PALETTE=[(239,68,68),(59,130,246),(59,130,246),
         (34,197,94),(234,179,8),(168,85,247),(249,115,22)]
RECT={
 'head':(.008,.015,.245,.475),
 'chest':(.252,.015,.610,.475),
 'back':(.616,.015,.992,.475),
 'torso':(.252,.015,.992,.475),
 'leftArm':(.010,.485,.495,.735),'rightArm':(.505,.485,.990,.735),
 'leftLeg':(.010,.745,.495,.990),'rightLeg':(.505,.745,.990,.990)
}
VERT_LIMIT=9000
TRI_COUNT=13932
PAINT_LIMIT=360000

def source():
    scene=json.loads(SOURCE.read_text('utf8'))
    part=scene['project']['modelAtelier']['parts'][0]
    m=part['topologyMesh']
    pos=np.asarray(m['positions'],np.float32).reshape(-1,3)
    inds=np.asarray(m['indices'],np.uint32).reshape(-1,3)
    welded,inverse=np.unique(pos,axis=0,return_inverse=True)
    tris=inverse[inds].astype(np.uint32)
    assert len(tris)==TRI_COUNT and len(welded)>4000
    return scene,part,welded,tris

def zone_ids(positions,faces,mode):
    centers=positions[faces].mean(axis=1)
    x,y,z=centers.T
    head=y>=4.08
    arms=(np.abs(x)>.69)&(y>3.30)&(~head)
    legs=y<=2.35
    labels=np.full(len(faces),'torso',dtype='<U12')
    labels[head]='head'
    labels[arms&(x<0)]='leftArm'
    labels[arms&(x>=0)]='rightArm'
    labels[legs&(x<0)]='leftLeg'
    labels[legs&(x>=0)]='rightLeg'
    if mode=='seven':
        torso=labels=='torso'
        labels[torso&(z>=0)]='chest'
        labels[torso&(z<0)]='back'
    return labels

def xatlas_group(pos,faces):
    used,inverse=np.unique(faces,return_inverse=True)
    coords=np.ascontiguousarray(pos[used],dtype=np.float32)
    idx=np.ascontiguousarray(inverse.reshape(-1,3),dtype=np.uint32)
    atlas=xatlas.Atlas()
    atlas.add_mesh(coords,idx)
    pack=xatlas.PackOptions()
    pack.resolution=1024
    pack.padding=7
    atlas.generate(pack_options=pack)
    vmap,f,uv=atlas[0]
    vmap=np.asarray(vmap,np.int64)
    f=np.asarray(f,np.uint32).reshape(-1,3)
    uv=np.asarray(uv,np.float64).reshape(-1,2)
    assert len(f)==len(faces)
    assert np.isfinite(uv).all()
    # Treat every input face as a geometrical fact, not an output face order.
    in_keys=Counter(tuple(sorted(map(tuple,coords[tri]))) for tri in idx)
    out_keys=Counter(tuple(sorted(map(tuple,coords[vmap[tri]]))) for tri in f)
    assert in_keys==out_keys,'The atlas changed source face geometry'
    return coords[vmap],f,uv,atlas.get_mesh_chart_count(0)

def seam_aware_anatomical_group(pos,faces,name):
    """Unroll a connected anatomical surface using an explicit axial seam.

    Unlike xatlas.parametrize(), this maps the entire region at once. Every
    triangle unwraps its circular angle around the local face mean; vertices
    are duplicated ONLY when the angle crosses the chosen back/underside seam.
    The original 3D positions and triangle winding are never changed.
    """
    used,inverse=np.unique(faces,return_inverse=True)
    coords=np.ascontiguousarray(pos[used],dtype=np.float32)
    idx=np.ascontiguousarray(inverse.reshape(-1,3),dtype=np.uint32)
    arm=name in ('leftArm','rightArm')
    axial=0 if arm else 1
    if arm:
        # Axial X is horizontal shoulder-to-wrist in 3D. Use front (+Z) as
        # angular center and the rear (-Z) as the continuous seam.
        # A face near +Z must never land on the side of the atlas.
        theta=np.arctan2(coords[:,1]-3.67,coords[:,2])
    else:
        center_x=(-0.28 if name=='leftLeg' else
                  0.28 if name=='rightLeg' else 0.0)
        # The front (+Z) is precisely theta=0, back (-Z) is the seam.
        theta=np.arctan2(coords[:,0]-center_x,coords[:,2])
    theta=np.arctan2(np.sin(theta),np.cos(theta))
    phase=theta[idx]
    avg=np.arctan2(np.sin(phase).sum(axis=1),
                   np.cos(phase).sum(axis=1))
    wind=np.rint((avg[:,None]-phase)/(2*np.pi)).astype(np.int16)
    lo=float(coords[:,axial].min())
    length=float(np.ptp(coords[:,axial]))
    if length<1e-8:
        raise ValueError('Collapsed anatomical projection '+name)
    # Stable vertex/phase identity prevents artificial UV cracks caused by
    # rounding per-face trigonometric results independently.
    vertex_lookup={}
    outpos=[];outuv=[];outfaces=[]
    for tri,wrap in zip(idx,wind):
        outtri=[]
        for vertex,turn in zip(tri,wrap):
            source_vertex=int(vertex)
            phase_turn=int(turn)
            key=(source_vertex,phase_turn)
            mapped=vertex_lookup.get(key)
            if mapped is None:
                mapped=len(outpos)
                vertex_lookup[key]=mapped
                outpos.append(coords[source_vertex])
                outuv.append(((theta[source_vertex]+2*np.pi*phase_turn+
                               np.pi)/(2*np.pi),
                              (float(coords[source_vertex,axial])-lo)/length))
            outtri.append(mapped)
        outfaces.append(outtri)
    xyz=np.asarray(outpos,np.float32)
    uv=np.asarray(outuv,np.float64)
    f=np.asarray(outfaces,np.uint32)
    counts=shell_counts(uv,f,[name]*len(f))
    if counts.get(name)!=1:
        raise ValueError('Anatomical projection fragmented '+name+': '+
                         str(counts.get(name))+' shells')
    if len(xyz)>VERT_LIMIT:
        raise ValueError('Anatomical seam vertex budget exceeded for '+name)
    return xyz,f,uv,1

def convex_single_shell_unwrap(pos,faces,name):
    """Unfold an articulated limb as ONE injective disk, not 30+ islands.

    Seam cutting supplies a topological disk. Its ordered border is mapped
    around a convex ellipse. Positive discrete harmonic weights place internal
    vertices inside that boundary: unlike cylindrical projection, different
    fingers/feet cannot fold into one another in UV space on a disk topology.
    """
    xyz,f,seed,_=seam_aware_anatomical_group(pos,faces,name)
    edge_counts=Counter()
    for tri in f:
        for i in range(3):
            a,b=map(int,(tri[i],tri[(i+1)%3]))
            edge_counts[tuple(sorted((a,b)))]+=1
    boundary=[edge for edge,n in edge_counts.items() if n==1]
    around={}
    for a,b in boundary:
        around.setdefault(a,[]).append(b)
        around.setdefault(b,[]).append(a)
    if not around or any(len(v)!=2 for v in around.values()):
        raise ValueError(name+' single-chart border is not a manifold loop')
    start=min(around,key=lambda i:(float(seed[i,1]),float(seed[i,0])))
    order=[start];previous=-1;current=start
    for _ in range(len(around)-1):
        choices=[v for v in around[current] if v!=previous]
        if not choices:raise ValueError(name+' boundary did not close')
        nxt=choices[0];order.append(nxt)
        previous,current=current,nxt
        if current==start:raise ValueError(name+' boundary loops overlap')
    if start not in around[current] or len(set(order))!=len(around):
        raise ValueError(name+' UV cut has multiple boundaries, not one disk')
    border=np.asarray(order,np.int64)
    successors=np.roll(border,-1)
    edge_lengths=np.linalg.norm(xyz[successors]-xyz[border],axis=1)
    if (edge_lengths<1e-7).any():raise ValueError(name+' collapsed boundary')
    arc=np.concatenate(([0],np.cumsum(edge_lengths[:-1])))
    phase=2*np.pi*arc/edge_lengths.sum()
    # Rotate the strictly convex boundary towards the known cylindrical U/V
    # directions so existing anatomical frame continuity is preserved.
    reference=seed[border]-seed[border].mean(axis=0)
    direction=np.sum((reference[:,0]+1j*reference[:,1])*
                     np.exp(-1j*phase))
    angle=float(np.angle(direction))
    ring=np.column_stack((np.cos(phase+angle),np.sin(phase+angle)))
    # Long oval (U width > V height), fitted without subsequent UV rotation.
    targets=np.column_stack((.5+.5*ring[:,0],.5+.29*ring[:,1]))
    nv=len(xyz)
    boundary_mask=np.zeros(nv,np.bool_);boundary_mask[border]=True
    movable=np.where(~boundary_mask)[0]
    lookup=np.full(nv,-1,np.int64);lookup[movable]=np.arange(len(movable))
    boundary_uv=np.zeros((nv,2),np.float64);boundary_uv[border]=targets
    rows=[];cols=[];data=[];rhs=np.zeros((len(movable),2),np.float64)
    adjacency=[[] for _ in range(nv)]
    for a,b in edge_counts:
        w=1.0  # Uniform positive Tutte weights avoid micro-geometry overconstraint
        adjacency[a].append((b,w));adjacency[b].append((a,w))
    for vertex in movable:
        row=int(lookup[vertex]);weighted=adjacency[vertex]
        rows.append(row);cols.append(row);data.append(sum(w for _,w in weighted))
        for other,weight in weighted:
            if boundary_mask[other]:rhs[row]+=weight*boundary_uv[other]
            else:
                rows.append(row);cols.append(int(lookup[other]));data.append(-weight)
    L=coo_matrix((data,(rows,cols)),shape=(len(movable),len(movable))).tocsr()
    relaxed=boundary_uv.copy()
    relaxed[movable]=np.column_stack((spsolve(L,rhs[:,0]),spsolve(L,rhs[:,1])))
    if not np.isfinite(relaxed).all():raise ValueError(name+' harmonic solve nonfinite')
    # Face orientation must be consistent, without UV fold-overs.
    q=relaxed[f]
    signed=(q[:,1,0]-q[:,0,0])*(q[:,2,1]-q[:,0,1])-(q[:,1,1]-q[:,0,1])*(q[:,2,0]-q[:,0,0])
    print('SE546_HARMONIC_AREAS',name,
          {'positive':int(np.count_nonzero(signed>1e-12)),
           'negative':int(np.count_nonzero(signed< -1e-12)),
           'tiny_1e10':int(np.count_nonzero(np.abs(signed)<1e-10)),
           'tiny_1e14':int(np.count_nonzero(np.abs(signed)<1e-14)),
           'min_abs':float(np.min(np.abs(signed))),
           'p01_abs':float(np.percentile(np.abs(signed),1))},flush=True)
    if min(np.count_nonzero(signed>1e-12),np.count_nonzero(signed< -1e-12))>0:
        raise ValueError(name+' chart contains flipped faces')
    if np.count_nonzero(np.abs(signed)<1e-14)>3:
        raise ValueError(name+' harmonic chart has collapsed triangles')
    return xyz,f,relaxed,1

def single_chart_group(pos,faces):
    """Parameterize an anatomical surface as one chart without xatlas chart splitting.

    A disconnected or closed region is rejected rather than silently producing
    a misleading 'continuous' UV shell.
    """
    used,inverse=np.unique(faces,return_inverse=True)
    coords=np.ascontiguousarray(pos[used],dtype=np.float32)
    idx=np.ascontiguousarray(inverse.reshape(-1,3),dtype=np.uint32)
    # Unlike Atlas.generate(), parametrize() does not partition the surface
    # into arbitrary charts. Boundary/seam design remains explicit.
    vmap,f,uv=xatlas.parametrize(coords,idx)
    vmap=np.asarray(vmap,np.int64)
    f=np.asarray(f,np.uint32).reshape(-1,3)
    uv=np.asarray(uv,np.float64).reshape(-1,2)
    if not len(f)==len(faces) or not np.isfinite(uv).all():
        raise ValueError('Single-chart parameterization invalid')
    before=Counter(tuple(sorted(map(tuple,coords[tri]))) for tri in idx)
    after=Counter(tuple(sorted(map(tuple,coords[vmap[tri]]))) for tri in f)
    if before!=after:raise ValueError('Single-chart parameterization altered geometry')
    lo=uv.min(axis=0);span=uv.max(axis=0)-lo
    if np.min(span)<1e-9:raise ValueError('Collapsed single-chart UV')
    uv=(uv-lo)/span.max()
    # A single parameterization call is not proof of one connected chart.
    # Verify the returned topology before accepting it.
    counts=shell_counts(uv,f,['region']*len(f))
    if counts.get('region')!=1:
        raise ValueError('Parameterization produced '+str(counts.get('region'))+' disconnected UV shells')
    return coords[vmap],f,uv,1

def fit(uv,rect,lock_orientation=False):
    # Isotropic transform: retain xatlas's internal angular/distortion metrics.
    umin=uv.min(axis=0);umax=uv.max(axis=0)
    length=np.maximum(umax-umin,1e-8)
    ax,ay,bx,by=rect
    rw,rh=bx-ax,by-ay
    # Choose orientation that fits most tightly without anisotropic stretch.
    a=min(rw/length[0],rh/length[1])
    b=min(rw/length[1],rh/length[0])
    if b>a and not lock_orientation:
        coords=np.column_stack((uv[:,1],1-uv[:,0]))
        bounds=np.array([length[1],length[0]])
        base=coords.min(axis=0)
        scale=b
    else:
        coords=uv;base=umin;bounds=length;scale=a
    slack=(np.array([rw,rh])-bounds*scale)/2
    return np.column_stack((np.full(len(uv),ax+slack[0]),
                            np.full(len(uv),ay+slack[1])))+(coords-base)*scale

def make_atlas(positions,triangles,mode):
    labels=zone_ids(positions,triangles,mode)
    parts=[];faces_out=[];uv_out=[];group_names=[];charts=0;count=0
    for name in (REGIONS if mode=='seven' else ['head','torso','leftArm','rightArm','leftLeg','rightLeg']):
        original=triangles[labels==name]
        if not len(original):raise ValueError('Missing anatomy '+name)
        # Arms and legs have one manifold UV-cut boundary apiece, verified
        # from exact source triangles. Convex harmonic mapping preserves each
        # as one connected chart without overlapping articulated fingers.
        if name in ('leftArm','rightArm','leftLeg','rightLeg'):
            p,f,uv,c=convex_single_shell_unwrap(positions,original,name)
        else:
            p,f,uv,c=seam_aware_anatomical_group(positions,original,name)
        if name=='head':
            # U is circumference, V is crown-to-chin. A horizontal 2:1
            # unrolled head gives a centered front visor at U ~= 0.5.
            uv[:,0]*=2.0
        base=count;count+=len(p);charts+=c
        if count>VERT_LIMIT:raise ValueError('UV vertex budget exceeded: '+str(count))
        parts.append(p);faces_out.append(f+base)
        uv_out.append(fit(uv,RECT[name],lock_orientation=True))
        group_names.extend([name]*len(f))
    outpos=np.concatenate(parts,axis=0)
    outfaces=np.concatenate(faces_out,axis=0)
    outuv=np.concatenate(uv_out,axis=0)
    assert len(outfaces)==len(triangles)
    orig=Counter(tuple(sorted(map(tuple,positions[tri]))) for tri in triangles)
    new=Counter(tuple(sorted(map(tuple,outpos[tri]))) for tri in outfaces)
    assert orig==new, 'Geometrical triangles altered during unwrap'
    return outpos,outfaces,outuv,group_names,charts

def shell_counts(uv,faces,region_names):
    """Count connected UV face components per anatomical region.

    Connectivity requires matching UV endpoints on a shared geometric edge;
    touching at a single UV vertex is not enough to join shells.
    """
    parent=np.arange(len(faces),dtype=np.int64)
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def union(a,b):
        a=find(a);b=find(b)
        if a!=b:parent[b]=a
    edges={}
    for i,(face,name) in enumerate(zip(faces,region_names)):
        for k in range(3):
            a,b=(int(face[k]),int(face[(k+1)%3]))
            key=(name,tuple(sorted((a,b))))
            if key in edges:union(i,edges[key])
            else:edges[key]=i
    counts={}
    for i,name in enumerate(region_names):
        counts.setdefault(name,set()).add(find(i))
    return {name:len(roots) for name,roots in counts.items()}

def continuous_shell_gate(uv,faces,region_names):
    counts=shell_counts(uv,faces,region_names)
    # Each of the six anatomical regions is a single connected UV shell.
    required={'head':1,'torso':1,'chest':1,'back':1,
              'leftArm':1,'rightArm':1,'leftLeg':1,'rightLeg':1}
    violations={k:{'actual':v,'maximum':required[k]} for k,v in counts.items()
                if v>required[k]}
    return counts,violations

def audit(pos,faces,uv):
    tri=pos[faces];m=uv[faces]
    world=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
    uv_a=m[:,1]-m[:,0];uv_b=m[:,2]-m[:,0]
    area=np.abs(uv_a[:,0]*uv_b[:,1]-uv_a[:,1]*uv_b[:,0])*.5
    print('SE546_ATLAS_AREA_DIAGNOSTIC',
          {'nearZero1e10':int(np.count_nonzero(area<1e-10)),
           'nearZero1e13':int(np.count_nonzero(area<1e-13)),
           'min':float(area.min()),'p05':float(np.percentile(area,5))},flush=True)
    assert world.min()>1e-10 and np.count_nonzero(area<1e-13)<14,'collapsed atlas'
    uv_total=float(area.sum())
    density=area/world
    ratio=float(np.percentile(density,95)/np.percentile(density,5))
    print('SE546_DENSITY_DIAGNOSTIC',ratio,flush=True)
    assert 0.12<uv_total<.97,('poor atlas area',uv_total)
    assert ratio<110,('severe unequal texel density',ratio)
    assert np.isfinite(uv).all() and uv.min()>=0 and uv.max()<=1
    return {'uvArea':round(uv_total,4),'p95P5Density':round(ratio,2)}

def measure_surface_uv_conflicts(pos,uv,faces,names,size=512,threshold=.035):
    """Count geometrically unrelated surfaces mapped to identical UV texels.

    Adjacent triangles in an otherwise valid single UV chart can both rasterize
    their shared edge pixel, so a raw duplicate-pixel count is NOT a valid UV
    overlap detector. Compare interpolated 3D positions at coincident texels.
    """
    stored=np.zeros((size,size,3),np.float32)
    filled=np.zeros((size,size),np.bool_)
    repeated=0;separated=0;largest=0.;by_region=Counter()
    uvp=np.column_stack((uv[:,0],1-uv[:,1]))*(size-1)
    for f,name in zip(faces,names):
        a=uvp[f]
        cross=(a[1,0]-a[0,0])*(a[2,1]-a[0,1])-(a[2,0]-a[0,0])*(a[1,1]-a[0,1])
        if abs(cross)<1e-8:continue
        lo=np.maximum(np.floor(a.min(axis=0)).astype(int)-1,0)
        hi=np.minimum(np.ceil(a.max(axis=0)).astype(int)+1,size-1)
        xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
        b=((xx-a[0,0])*(a[2,1]-a[0,1])-(yy-a[0,1])*(a[2,0]-a[0,0]))/cross
        c=((yy-a[0,1])*(a[1,0]-a[0,0])-(xx-a[0,0])*(a[1,1]-a[0,1]))/cross
        d=1-b-c
        valid=(b>=-1e-6)&(c>=-1e-6)&(d>=-1e-6)
        if not valid.any():continue
        py=yy[valid];px=xx[valid]
        world=(b[valid,None]*pos[f[1]]+c[valid,None]*pos[f[2]]+
               d[valid,None]*pos[f[0]])
        overlap=filled[py,px]
        if overlap.any():
            repeated+=int(overlap.sum())
            delta=np.linalg.norm(stored[py[overlap],px[overlap]]-world[overlap],axis=1)
            nconflict=int(np.count_nonzero(delta>threshold))
            separated+=nconflict;by_region[name]+=nconflict
            largest=max(largest,float(delta.max(initial=0)))
        stored[py,px]=world;filled[py,px]=True
    return {'samples':size,'sharedEdgeSamples':repeated-separated,
            'conflictingSamples':separated,
            'conflictsByRegion':dict(by_region),
            'maxOverlapWorldDistance':round(largest,4),
            'conflictPct':round(100*separated/max(1,int(filled.sum())),4)}


def new_skin(p,n):
    x,y,z=p.T;nx,ny,nz=n.T;ax=np.abs(x)
    smooth=bakery.smooth;band=bakery.band;ellipse=bakery.ellipse
    # Full replacement palette; no human eyes, lips, face or drawn-on hands.
    v=3*np.sin(7*x+2*z)+2*np.cos(9*y+3*x)
    rgb=np.stack((220+v,229+v,235+v),axis=1)
    head=y>=4.08;arm=(ax>.69)&(y>3.30)&(~head);leg=y<=2.35;torso=~(head|arm|leg)
    tags=bakery.labels(p)
    front=smooth(.08,.45,nz);back=smooth(.08,.45,-nz)
    side=smooth(.25,.72,np.abs(nx))
    def layer(col,w):bakery.blend(rgb,col,w)
    # Faceless sealed shell with one thin optical band, not a human portrait.
    layer((47,61,76),head*front*band(y,4.48,.042,.020)*.89)
    layer((38,197,209),head*front*band(y,4.49,.006,.008)*.80)
    layer((89,104,114),head*side*band(y,4.47,.045,.033)*.60)
    layer((59,70,82),head*back*band(x,0,.047,.034)*.72)
    layer((38,190,204),head*back*band(x,0,.008,.014)*band(y,4.47,.08,.05)*.85)
    layer((48,61,72),head*band(y,4.10,.027,.022)*.77)
    # White exterior torso with dark inner chassis and layered armor structure.
    chest=torso*front
    yoke=3.55-.21*np.clip(ax/.52,0,1)
    layer((67,78,92),chest*band(y,yoke,.016,.025)*.84)
    layer((51,65,78),chest*band(x,0,.092,.069)*band(y,3.46,.21,.16)*.86)
    layer((25,214,219),chest*ellipse(x/.065,(y-3.51)/.075)*.91)
    layer((244,244,240),chest*band(ax,.30,.17,.12)*band(y,3.53,.21,.15)*.46)
    layer((69,83,97),chest*band(x,0,.15,.10)*band(y,2.92,.25,.17)*.77)
    layer((156,174,183),chest*band(x,0,.13,.10)*smooth(.71,.95,np.cos((y-2.78)*42))*.47)
    layer((64,78,93),torso*side*band(y,3.17,.38,.13)*.63)
    layer((55,69,83),torso*band(y,2.52,.047,.040)*.71)
    # Back: broad shoulder plate, segmented spine, cobalt/cyan channels.
    layer((79,93,109),torso*back*band(x,0,.12,.10)*band(y,3.13,.53,.24)*.83)
    layer((35,206,216),torso*back*band(x,0,.023,.012)*
          smooth(.88,.97,np.cos((y-2.70)*28))*band(y,3.12,.50,.18)*.96)
    layer((238,240,239),torso*back*band(ax,.30,.16,.10)*band(y,3.45,.30,.22)*.35)
    # Arms: silver forearm casings, dark articulated joint bands and inset lights.
    for value,width in ((.84,.038),(1.43,.075),(2.07,.047),(2.40,.027)):
        layer((54,68,81),arm*band(ax,value,width,.023)*.91)
    layer((242,245,241),arm*band(ax,1.80,.20,.12)*.44)
    layer((59,74,88),arm*band(y,3.72,.040,.030)*band(ax,1.17,.23,.14)*.62)
    layer((31,209,214),arm*band(y,3.65,.009,.014)*
          band(ax,1.79,.19,.10)*front*.83)
    # Legs and feet: shaped knee guards and shin plates.
    for value,width in ((2.18,.062),(1.04,.080),(.29,.048)):
        layer((55,70,81),leg*band(y,value,width,.035)*.88)
    layer((239,243,243),leg*front*band(y,1.65,.35,.22)*.56)
    layer((66,80,92),leg*front*band(ax,.36,.073,.061)*band(y,.82,.19,.11)*.79)
    layer((31,204,212),leg*front*band(ax,.36,.013,.013)*band(y,.76,.18,.12)*.85)
    layer((47,58,69),leg*back*band(ax,.39,.055,.040)*band(y,1.46,.25,.18)*.67)
    layer((238,244,245),leg*(1-smooth(.10,.29,y))*.50)
    layer((43,190,201),leg*front*band(y,.14,.010,.012)*.58)
    # Sharp controlled engraved grooves: painted detail, not bogus geometry.
    seam=np.minimum(np.abs(np.sin(19*x+7*z)),np.abs(np.sin(22*y-3*z)))
    layer((137,155,165),(torso.astype(float)+arm.astype(float)+leg.astype(float))*
          smooth(.035,.008,seam)*.10)
    return np.clip(np.rint(rgb),0,255).astype(np.uint8),tags

def normals(pos,faces):
    welded,inv=np.unique(pos,axis=0,return_inverse=True)
    v=np.zeros((len(welded),3),np.float64)
    q=pos[faces];f=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0])
    for k in range(3):np.add.at(v,inv[faces[:,k]],f)
    v/=np.maximum(np.linalg.norm(v,axis=1)[:,None],1e-12)
    return v[inv]

def export_guides(uv,faces,region_names):
    s=4096;xy=np.rint(np.column_stack((uv[:,0],1-uv[:,1]))*(s-1)).astype(np.int32)
    colors=dict(zip(REGIONS,PALETTE))
    colors['torso']=(59,130,246)  # same blue as app's region 2
    for p,anatomical in ((GUIDE,False),(ANATOMY,True)):
        canvas=Image.new('RGB',(s,s),(19,31,48))
        painter=ImageDraw.Draw(canvas)
        for ids,name in zip(faces,region_names):
            pts=[tuple(map(int,xy[k])) for k in ids]
            shade=colors[name] if anatomical else tuple(int(k*.19) for k in colors[name])
            painter.polygon(pts,fill=shade)
            painter.line(pts+[pts[0]],fill=(208,238,241) if anatomical else (45,229,225),width=1)
        # Numbered region legend is drawn onto exported GUIDES, not onto the
        # robotic material: labels cannot accidentally appear on the model.
        order=['head','torso','chest','back','leftArm','rightArm','leftLeg','rightLeg']
        visible=set(region_names)
        try:font=ImageFont.truetype('DejaVuSans.ttf',52)
        except OSError:font=ImageFont.load_default()
        for number,name in enumerate((n for n in order if n in visible),1):
            x0,y0,x1,y1=RECT[name]
            cx=int((x0+x1)*s/2);cy=int((y0+y1)*s/2)
            label=str(number).zfill(2)+' '+name.upper()
            bounds=painter.textbbox((0,0),label,font=font)
            w=bounds[2]-bounds[0];h=bounds[3]-bounds[1]
            painter.rounded_rectangle((cx-w//2-24,cy-h//2-23,
                                      cx+w//2+24,cy+h//2+23),
                                     radius=14,fill=(13,21,35),
                                     outline=colors[name],width=5)
            painter.text((cx-w/2-bounds[0],cy-h/2-bounds[1]),
                         label,font=font,fill=(245,249,252))
        p.parent.mkdir(parents=True,exist_ok=True)
        canvas.save(p,format='PNG',optimize=True)
        assert p.stat().st_size<10_000_000,(p,p.stat().st_size)

def main():
    scene,part,positions,faces=source()
    errors=[];result=None
    for kind in ('six','seven'):
        try:
            candidate=make_atlas(positions,faces,kind)
            metrics=audit(*candidate[:3])
            shells,violations=continuous_shell_gate(candidate[2],candidate[1],candidate[3])
            if violations:raise ValueError('continuous shell criteria not met: '+str(violations))
            result=(candidate,dict(metrics,uvShells=shells),kind);break
        except (ValueError,AssertionError) as e:
            errors.append(kind+': '+str(e))
            print('SE546_ATLAS_ATTEMPT_REJECTED',errors[-1],flush=True)
    if result is None:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps({'version':'v11.546','status':'rejected','candidateFailures':errors},indent=2)+'\n','utf8')
        raise ValueError('Cannot make safe anatomical atlas: '+str(errors))
    (xyz,idx,uv,region,charts),metrics,kind=result
    # Native format rounds 3D positions to 5 and UVs to 6 decimal places.
    xyz=np.round(xyz.astype(np.float64),5)
    uv=np.round(uv,6)
    bakery.SIZE=1024
    bakery.surface_paint=new_skin
    baked,regions,paint_metrics=bakery.bake(xyz,uv,idx.astype(np.int64),normals(xyz,idx))
    collision_metrics=measure_surface_uv_conflicts(xyz,uv,idx,region)
    blob=bakery.export_png(baked,PAINT)
    assert len(base64.b64encode(blob))+22<=PAINT_LIMIT
    export_guides(uv,idx,region)
    previews=[('FRONT',bakery.render_view(baked,xyz,uv,idx,'front',False)),
              ('BACK',bakery.render_view(baked,xyz,uv,idx,'front',True)),
              ('SIDE',bakery.render_view(baked,xyz,uv,idx,'side',False))]
    im=Image.new('RGB',(1560,606),(19,26,41));d=ImageDraw.Draw(im)
    for i,(name,pic) in enumerate(previews):
        im.paste(pic,(i*520,36));d.text((i*520+12,14),name,fill=(236,245,249))
    PREVIEW.parent.mkdir(parents=True,exist_ok=True);im.save(PREVIEW,'PNG',optimize=True)
    mesh=part['topologyMesh']
    mesh['positions']=xyz.ravel().tolist()
    mesh['indices']=idx.astype(int).ravel().tolist()
    mesh['uvs']=uv.ravel().tolist()
    part['name']='Futuristic Humanoid · anatomy-mapped new robotic shell'
    part['uvPaintPNG']='data:image/png;base64,'+base64.b64encode(blob).decode('ascii')
    part.pop('uvPaintRepeat',None);part.pop('uvPaintOffset',None);part.pop('uvArtMarker',None)
    scene['version']=11.546
    scene['engine']='§wyrl§ Engine · Maker v11.546'
    scene['project']['name']='Futuristic Humanoid · Anatomical Robot'
    scene['project']['modelAtelier']['name']='Futuristic Humanoid · Anatomy UV + Robot Skin'
    scene['project']['modelAtelier']['reference']=(
      'One continuous five-digit humanoid, 13,932 original 3D triangles. '
      'Head and torso authored as coherent UV shells, with xatlas-separated articulated limb islands in '+kind+
      ' true 3D regions. New ceramic/graphite/cyan robotic skin baked from '
      'actual local 3D positions and normals; no old atlas texture transferred. '
      '4096px UV wireframe and 4096px anatomical UV guide are available. '
      'No rigging or geometry sculpt applied.')
    OUTPUT.write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')),'utf8')
    record={'version':'v11.546','strategy':kind,'charts':charts,
        'vertices':len(xyz),'triangles':len(idx),'originalGeometryUnchanged':True,
        'regionTriangles':dict(Counter(region)),'paintBytes':len(blob),
        'guideSize':4096,'legacyCandidatesRejected':errors,
        **metrics,**paint_metrics,**collision_metrics}
    REPORT.write_text(json.dumps(record,indent=2)+'\n','utf8')
    print('SE546_ANATOMICAL_ROBOT_BAKED',json.dumps(record),flush=True)

if __name__=='__main__':main()
