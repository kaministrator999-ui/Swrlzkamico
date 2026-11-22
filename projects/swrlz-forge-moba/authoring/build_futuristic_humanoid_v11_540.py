#!/usr/bin/env python3
"""§E v11.540 original humanoid anatomy and five-digit hands.

Generate a single connected watertight model surface at build time, with
finer sampling around each palm and finger. Preserve native six-island UVs
and the embedded original §E material atlas; none of the authoring libraries
run on the user's phone or Quest.
"""
import copy
import importlib.util
import json
from pathlib import Path
import time

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from skimage.measure import marching_cubes
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json'
OUTPUT=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'
start=time.time()

def axis(parts):
    values=[]
    for lo,hi,step in parts:
        values.extend(np.arange(lo,hi,step,dtype=np.float32).tolist())
    values.append(parts[-1][1])
    return np.unique(np.asarray(values,dtype=np.float32))

# Selective grid: preserve joint/body efficiency, sample the hand silhouettes
# finely along all three axes. Nonuniform physical coordinates are restored
# after marching cubes (sampling indices are not assumed to be world units).
x=axis([(-2.85,-2,.024),(-2,2,.055),(2,2.85,.024)])
y=axis([(-.14,3.28,.057),(3.28,4.02,.022),(4.02,5,.057)])
z=axis([(-.66,-.21,.052),(-.21,.38,.022),(.38,.8,.052)])
X,Y,Z=x[:,None,None],y[None,:,None],z[None,None,:]
field=np.full((len(x),len(y),len(z)),10,dtype=np.float32)

def smooth_union(d,k):
    global field
    h=np.maximum(k-np.abs(field-d),0)/k
    field=np.minimum(field,d)-h*h*k*.25

def ellipsoid(center,radii,k=.07):
    d=(np.sqrt(((X-center[0])/radii[0])**2+
               ((Y-center[1])/radii[1])**2+
               ((Z-center[2])/radii[2])**2)-1)*min(radii)
    smooth_union(d,k)

def segment(a,b,r0,r1=None,k=.04,depth=1.):
    if r1 is None:
        r1=r0
    vec=np.asarray(b,dtype=np.float32)-np.asarray(a,dtype=np.float32)
    t=np.clip(((X-a[0])*vec[0]+(Y-a[1])*vec[1]+
               (Z-a[2])*vec[2])/(vec@vec),0,1)
    d=np.sqrt((X-a[0]-t*vec[0])**2+
              (Y-a[1]-t*vec[1])**2+
              ((Z-a[2]-t*vec[2])/depth)**2)-(r0+(r1-r0)*t)
    smooth_union(d,k)

def rounded_box(center,radii,r,k):
    dx=np.abs(X-center[0])-radii[0]
    dy=np.abs(Y-center[1])-radii[1]
    dz=np.abs(Z-center[2])-radii[2]
    d=(np.sqrt(np.maximum(dx,0)**2+
               np.maximum(dy,0)**2+
               np.maximum(dz,0)**2)+
       np.minimum(np.maximum(dx,np.maximum(dy,dz)),0)-r)
    smooth_union(d,k)

def anatomy():
    global field
    # Anatomical planes, but no disconnected pectoral, elbow or hip objects.
    # Subtle contour transitions replace the previous melted-shoulder bulges.
    ellipsoid((0,3.54,0),(.43,.43,.249),.082)
    ellipsoid((0,3.18,0),(.32,.41,.19),.085)
    ellipsoid((0,2.64,-.005),(.329,.31,.21),.08)
    ellipsoid((0,2.43,-.02),(.325,.212,.209),.06)
    segment((0,3.8,0),(0,4.22,0),.118,.100,.045)
    ellipsoid((0,4.49,-.012),(.225,.303,.217),.067)
    ellipsoid((0,4.335,.086),(.166,.166,.14),.033)
    ellipsoid((0,4.365,.125),(.184,.172,.12),.023)

    for side in (-1,1):
        s=side
        ellipsoid((s*.493,3.642,-.005),(.204,.179,.19),.076)
        segment((s*.52,3.64,0),(s*1.38,3.64,0),.155,.098,.075,.91)
        ellipsoid((s*.84,3.645,.005),(.22,.137,.153),.045)
        segment((s*1.39,3.64,0),(s*2.075,3.64,0),.109,.071,.041)
        ellipsoid((s*1.68,3.64,.002),(.23,.115,.114),.037)
        segment((s*1.98,3.64,0),(s*2.125,3.64,0),.071,.064,.035)
        # A broad but rounded palm merges into the wrist, not a mitten tip.
        rounded_box((s*2.255,3.64,0),(.133,.094,.039),.041,.046)

        # Distinct index/middle/ring/pinky shafts. Their proximal phalanges
        # fuse to the palm; the three tapered sections and individual rounded
        # tips remain separated in front/back elevation.
        offsets=(.088,.033,-.028,-.086)
        lengths=(.235,.292,.270,.215)
        origins=(2.359,2.370,2.360,2.347)
        for finger,(dy,length,origin) in enumerate(zip(offsets,lengths,origins)):
            spread=(finger-1.5)*(-.010)
            a=(s*origin,3.64+dy,.002)
            knuckle=(s*(origin+.060),3.64+dy+spread*.34,.004)
            middle=(s*(origin+length*.57),3.64+dy+spread*.66,.005)
            tip=(s*(origin+length),3.64+dy+spread,.005)
            radius=(.024,.028,.026,.022)[finger]
            segment(a,knuckle,radius,radius*.92,.012,.82)
            segment(knuckle,middle,radius*.92,radius*.78,.009,.82)
            segment(middle,tip,radius*.78,radius*.65,.008,.88)
            ellipsoid((s*(origin+length-.007),
                       3.64+dy+spread,.005),(.018,.019,.019),.009)
            ellipsoid((s*2.315,3.64+dy,-.002),(.043,.027,.042),.016)

        # Opposable fifth digit bends below the palm, visibly separate from
        # the four fingertip silhouettes (but welded via continuous surface).
        segment((s*2.18,3.57,.037),(s*2.294,3.485,.086),
                .048,.034,.032)
        segment((s*2.294,3.485,.086),(s*2.405,3.405,.106),
                .034,.024,.010)
        ellipsoid((s*2.399,3.41,.104),(.021,.020,.020),.012)

        # Slimmer pelvic contour; clean thigh/knee/calf/ankle flow.
        ellipsoid((s*.29,2.286,-.014),(.182,.21,.199),.075)
        segment((s*.296,2.21,0),(s*.323,1.408,0),.196,.132,.080,.98)
        ellipsoid((s*.33,1.92,.02),(.173,.252,.177),.063)
        ellipsoid((s*.326,1.317,.035),(.132,.113,.117),.028)
        segment((s*.33,1.25,-.02),(s*.331,.35,0),.12,.076,.034,.96)
        ellipsoid((s*.332,1.03,-.054),(.141,.216,.139),.055)
        ellipsoid((s*.331,.203,.14),(.137,.118,.281),.045)
        rounded_box((s*.33,.091,.338),(.134,.040,.13),.027,.04)
        for toe in range(5):
            ellipsoid((s*(.331+(toe-2)*.053),
                       .082,.45-abs(toe-1)*.021),
                      (.027,.032,.066),.018)

    # Integrated shallow joint seam relief, not extra armor meshes.
    for height,width,depth in ((1.32,.034,.008),(.34,.035,.006)):
        field+=depth*np.exp(-((Y-height)/width)**2)*np.exp(
            -((np.abs(X)-.33)/.19)**4)*np.exp(-((Z-.095)/.09)**2)
    for wrist in (1.39,2.06):
        field+=.004*np.exp(-((np.abs(X)-wrist)/.020)**2)*np.exp(
            -((Y-3.64)/.13)**4)

def verify_topology(vertices,faces):
    # Explicit manifold + connected checks before generating UV duplicates.
    edges=np.sort(np.concatenate((faces[:,(0,1)],faces[:,(1,2)],
                                   faces[:,(2,0)])),axis=1)
    _,counts=np.unique(edges,axis=0,return_counts=True)
    assert len(counts)>1000 and np.all(counts==2),'non-manifold / open model'
    ii=np.concatenate((faces[:,0],faces[:,1],faces[:,2]))
    jj=np.concatenate((faces[:,1],faces[:,2],faces[:,0]))
    adj=coo_matrix((np.ones(len(ii)),(ii,jj)),
                   shape=(len(vertices),len(vertices)))
    assert connected_components(adj+adj.T)[0]==1,'disconnected body shells'
    return (adj+adj.T).tocsr()

def mesh():
    vertices,faces,_,_=marching_cubes(field,level=0,allow_degenerate=False)
    for dim,coords in enumerate((x,y,z)):
        vertices[:,dim]=np.interp(vertices[:,dim],
                                  np.arange(len(coords)),coords)
    adj=verify_topology(vertices,faces)
    adj.data.fill(1)
    degree=np.asarray(adj.sum(axis=1)).ravel()
    # Taubin pass smooths sampling stair-step while retaining hand size.
    for strength in (.25,-.255,.25,-.255):
        vertices+=strength*(adj.dot(vertices)/degree[:,None]-vertices)
    vtk_points=vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(
        vertices.astype('float32'),deep=True))
    poly=vtk.vtkPolyData()
    poly.SetPoints(vtk_points)
    cells=vtk.vtkCellArray()
    legacy=np.column_stack((np.full(len(faces),3),faces)).astype(
        np.int64).ravel()
    cells.SetCells(len(faces),numpy_to_vtk(
        legacy,deep=True,array_type=vtk.VTK_ID_TYPE))
    poly.SetPolys(cells)
    # Edge-collapse simplification preserves a single manifold surface while
    # retaining fingertip geometry. Do not change to vertex clustering.
    reduction=vtk.vtkDecimatePro()
    reduction.SetPreserveTopology(True)
    reduction.SetSplitting(False)
    reduction.SetBoundaryVertexDeletion(False)
    reduction.SetTargetReduction(.49)
    reduction.SetInputData(poly)
    reduction.Update()
    result=reduction.GetOutput()
    vertices=vtk_to_numpy(result.GetPoints().GetData())
    faces=vtk_to_numpy(result.GetPolys().GetConnectivityArray()).reshape(-1,3)
    verify_topology(vertices,faces)
    assert len(vertices)<=7500 and len(faces)<=15000
    return vertices,faces

def finger_topology(vertices,faces):
    # Four *separated* fingertips per hand at x > 2.53. Connected hand
    # topology is still verified by verify_topology on the full geometry.
    connections=np.concatenate((faces[:,(0,1)],faces[:,(1,2)],
                                faces[:,(2,0)]))
    result={}
    for side,name in ((-1,'left'),(1,'right')):
        ids=np.where((side*vertices[:,0]>2.53)&
                     (vertices[:,1]>3.51)&(vertices[:,1]<3.81)&
                     (np.abs(vertices[:,2])<.15))[0]
        remap=np.full(len(vertices),-1,dtype=int)
        remap[ids]=np.arange(len(ids))
        edges=remap[connections]
        edges=edges[np.all(edges>=0,axis=1)]
        mat=coo_matrix((np.ones(len(edges)),
                        (edges[:,0],edges[:,1])),
                       shape=(len(ids),len(ids)))
        n,labels=connected_components(mat+mat.T)
        assert n>=4,(name,'four distinct fingers not visible',n)
        assert np.any((side*vertices[:,0]>2.37)&
                      (vertices[:,1]<3.45)&
                      (vertices[:,1]>3.36)),(name,'thumb missing')
        result[name]={'fingerTips':n,'verticesBeyondKnuckles':len(ids)}
    return result

def main():
    anatomy()
    vertices,faces=mesh()
    fingers=finger_topology(vertices,faces)
    # Keep the original native UV six-island atlas implementation, which is
    # already compatible with modeler material painting.
    spec=importlib.util.spec_from_file_location(
        'se538_baker',ROOT/'authoring/build_futuristic_humanoid_v11_538.py')
    prior_module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior_module)
    packed_v,packed_uv,packed_faces=prior_module.six_island_uv(
        vertices,faces)
    assert len(packed_v)<=9000 and len(packed_faces)<=16000
    scene=json.loads(PRIOR.read_text('utf8'))
    part=scene['project']['modelAtelier']['parts'][0]
    part['name']='Futuristic Humanoid · anatomical body with five-finger hands'
    part['topologyMesh']={
        'positions':np.round(packed_v,5).ravel().tolist(),
        'uvs':np.round(packed_uv,6).ravel().tolist(),
        'indices':packed_faces.astype(int).ravel().tolist(),
    }
    scene['engine']='§wyrl§ Engine · Maker v11.540'
    scene['version']=11.540
    scene['project']['name']='Futuristic Humanoid · Refined Hands + Anatomy'
    model=scene['project']['modelAtelier']
    model['name']='Futuristic Humanoid · Articulated Hand Silhouette'
    model['reference']=(
       'Original one-piece organic-futuristic humanoid in T-pose. Four '
       'separate tapered fingertips and one opposable thumb per hand; '
       'continuous welded surface, refined athletic anatomy, six-island '
       'editable UVs and embedded original sci-fi PNG material. This is '
       'a modeling starter, not a skinned skeleton or rigged animation.')
    scene['project']['canonicalId']='robotic-humanoid-mannequin'
    OUTPUT.write_text(json.dumps(scene,ensure_ascii=False,separators=(',',':')),
                      encoding='utf8')
    print('SE540_FIVE_FINGER_HUMANOID_BAKED',
          json.dumps({'parts':1,'uvVertices':len(packed_v),
                      'geometricVertices':len(vertices),
                      'triangles':len(faces),'fingers':fingers,
                      'sceneBytes':OUTPUT.stat().st_size,
                      'elapsed':round(time.time()-start,2)}),
          flush=True)

if __name__=='__main__':
    main()
