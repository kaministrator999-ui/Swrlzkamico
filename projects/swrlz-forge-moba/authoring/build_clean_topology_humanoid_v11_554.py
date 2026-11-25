#!/usr/bin/env python3
"""§E UV-first humanoid revision: quad-constructed, welded anatomical branches.

Build the actual connected surface before assigning the six readable UV regions.
Every torso/neck/shoulder/pelvis/palm/finger/toe junction is topologically
attached after positional UV-seam welding. UV seams duplicate coordinates but
never tear the physical surface. The original robotic humanoid is untouched.
"""
import base64
from collections import Counter,defaultdict,deque
import json,math
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'
OUTPUT=ROOT/'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
ATLAS=ROOT/'assets/models/clean-topology-humanoid-v11-554-uv-test.png'
GUIDE=ROOT/'assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png'
REPORT=ROOT/'docs/qa/clean-topology-humanoid-v11-554.json'
BOXES={
 'head':(.02,.035,.27,.465),
 'torso':(.305,.035,.98,.465),
 'leftArm':(.02,.525,.245,.965),
 'rightArm':(.265,.525,.49,.965),
 'leftLeg':(.51,.525,.735,.965),
 'rightLeg':(.755,.525,.98,.965),
}
PALETTE={'head':(169,199,209),'torso':(144,175,187),
 'leftArm':(149,185,183),'rightArm':(153,187,188),
 'leftLeg':(151,169,191),'rightLeg':(151,174,195)}
P=[];UV=[];Q=[];F=[];GROUP=[];QUADS=Counter()
def lerp(a,b,t):return a+(b-a)*t
def mix(a,b,t):return [lerp(x,y,t) for x,y in zip(a,b)]
def smooth(t):return t*t*(3.-2.*t)
def controls(points,subdiv=3):
    """C1 continuous Catmull-Rom anatomical profiles.

    The previous smoothstep-per-segment interpolation produced zero slope at
    every control station, visible as stacked rings on the skull and limbs.
    """
    out=[]
    for i in range(len(points)-1):
        p0=points[max(0,i-1)];p1=points[i]
        p2=points[i+1];p3=points[min(i+2,len(points)-1)]
        for j in range(subdiv):
            t=j/subdiv;t2=t*t;t3=t2*t
            out.append([.5*((2*b)+(-a+c)*t+
                         (2*a-5*b+4*c-d)*t2+
                         (-a+3*b-3*c+d)*t3)
                        for a,b,c,d in zip(p0,p1,p2,p3)])
    out.append(list(points[-1]))
    return out
def vertex(xyz,uv):
    assert len(xyz)==3 and len(uv)==2
    P.extend(round(float(x),6) for x in xyz)
    UV.extend(round(float(x),7) for x in uv)
    return len(P)//3-1
def face(name,a,b,c,d):
    assert len({a,b,c,d})==4,('index-degenerate quad',name)
    Q.append((name,(a,b,c,d)));QUADS[name]+=1
def uvloc(name,u,v):
    a,b,c,d=BOXES[name]
    return (lerp(a,c,u),lerp(b,d,v))
def ring(name,points,v,urange=(0.,1.)):
    n=len(points)
    return [vertex(points[i%n],uvloc(name,lerp(urange[0],urange[1],i/n),v))
            for i in range(n+1)]
def strip(name,a,b,reverse=False):
    n=len(a)-1
    assert len(b)==n+1
    for i in range(n):
        if reverse:face(name,a[i],a[i+1],b[i+1],b[i])
        else:face(name,a[i],b[i],b[i+1],a[i+1])
def gridloop(i0,i1,j0,j1):
    """A rectangular hole's actual ordered perimeter, with no corner repeats."""
    return ([(i,j0) for i in range(i0,i1)]+
            [(i1,j) for j in range(j0,j1)]+
            [(i,j1) for i in range(i1,i0,-1)]+
            [(i0,j) for j in range(j1,j0,-1)])
def boundary(nx,nz):
    # Start on posterior midline so the body UV seam is behind the mannequin.
    h=nx//2
    return ([(i,0) for i in range(h,nx)]+
            [(nx,j) for j in range(0,nz)]+
            [(i,nz) for i in range(nx,0,-1)]+
            [(0,j) for j in range(nz,0,-1)]+
            [(i,0) for i in range(0,h)])
def disk(u,v,rx,rz):
    return (rx*u*math.sqrt(max(0.,1.-v*v/2)),
            rz*v*math.sqrt(max(0.,1.-u*u/2)))
def torso_geometry():
    nx,nz=14,10
    pelvis={}
    for j in range(nz+1):
        for i in range(nx+1):
            u=(i-nx/2)/(nx/2)
            v=(j-nz/2)/(nz/2)
            x,z=disk(u,v,.415,.237)
            # Sculpt an anatomical saddle instead of a flat skirt-shaped cap:
            # raised hip crests and a lowered groin between the thighs.
            y=2.24+.055*abs(u)**1.7-.075*(1-abs(u))*(1-.24*v*v)
            pelvis[i,j]=(x,y,z)
    outline=boundary(nx,nz)
    assert len(outline)==48
    start=[pelvis[p] for p in outline]
    angles=[math.atan2(z,x) for x,y,z in start]
    body=controls([
      [2.24,.415,.237],[2.43,.428,.253],[2.65,.352,.224],
      [2.94,.287,.200],[3.21,.337,.226],[3.44,.432,.256],
      [3.62,.472,.246],[3.77,.403,.220],[3.91,.176,.151],
      [4.08,.127,.117],[4.16,.119,.110]
    ],3)
    tr=[]
    for k,(y,rx,rz) in enumerate(body):
        blend=max(0.,1.-k/8.)**2
        points=(start if k==0 else
                [(rx*math.cos(t),y+(start[n][1]-2.24)*blend,
                  rz*math.sin(t)) for n,t in enumerate(angles)])
        tr.append(ring('torso',points,.095+.355*k/(len(body)-1)))
    # 12 x 6 quad sockets: exactly 36 surrounding edges, not intersecting
    # cylindrical image seams. Shoulders are true extrusions from the body.
    sockets={'rightArm':(6,18,16,22),'leftArm':(30,42,16,22)}
    for k in range(len(tr)-1):
        for n in range(48):
            hidden=any(a<=n<b and lo<=k<hi for a,b,lo,hi in sockets.values())
            if not hidden:face('torso',tr[k][n],tr[k+1][n],
                               tr[k+1][n+1],tr[k][n+1])
    shoulder={}
    for key,(a,b,lo,hi) in sockets.items():
        outline=gridloop(a,b,lo,hi)
        shoulder[key]=[tuple(P[3*tr[k][n]:3*tr[k][n]+3])
                       for n,k in outline]
        assert len(shoulder[key])==36
    # Bottom pelvis patch shares exact 3D positions with the body tube,
    # with two real 4 x 6 quad holes feeding the legs.
    openings={'leftLeg':(2,6,2,8),'rightLeg':(8,12,2,8)}
    idx={}
    b=BOXES['torso']
    for (i,j),p in pelvis.items():
        idx[i,j]=vertex(p,(lerp(b[0],b[2],.02+.96*i/nx),
                          lerp(b[1],b[3],.01+.06*j/nz)))
    for j in range(nz):
        for i in range(nx):
            hidden=any(x0<=i<x1 and y0<=j<y1
                       for x0,x1,y0,y1 in openings.values())
            if not hidden:face('torso',idx[i,j],idx[i+1,j],
                               idx[i+1,j+1],idx[i,j+1])
    hips={}
    for key,(a,b,c,d) in openings.items():
        hips[key]=[pelvis[p] for p in gridloop(a,b,c,d)]
        assert len(hips[key])==20
    return tr[-1],shoulder,hips

def cranial_surface(neck):
    bottom=[tuple(P[3*i:3*i+3]) for i in neck[:-1]]
    profile=controls([
      [4.16,.119,.110],[4.225,.158,.141],
      [4.315,.231,.202],[4.42,.257,.231],
      [4.56,.236,.210],[4.685,.158,.143],
      [4.748,.092,.083],[4.785,.040,.036]
    ],3)
    angles=[math.atan2(z,x) for x,y,z in bottom]
    rings=[]
    for k,(y,rx,rz) in enumerate(profile):
        p=(bottom if k==0 else [(rx*math.cos(t),y,rz*math.sin(t))
                                for t in angles])
        rings.append(ring('head',p,.025+.91*k/(len(profile)-1)))
        if k:strip('head',rings[k-1],rings[k])
    close_tip('head',rings[-1],(0,4.803,0),.98)

def close_tip(name,rim,xyz,v=.04,urange=(0.,1.)):
    n=len(rim)-1
    assert n%2==0
    center=vertex(xyz,uvloc(name,lerp(*urange,.5),v))
    for i in range(0,n,2):
        face(name,rim[i],rim[i+1],rim[i+2],center)

def capgrid(name,nx,nz,position,rect,holes):
    """Quadrangulated end of a tube with true openings for outgoing digits."""
    a,b,c,d=rect
    indices={}
    for j in range(nz+1):
        for i in range(nx+1):
            xyz=position(i,j)
            indices[i,j]=vertex(xyz,uvloc(name,lerp(a,c,i/nx),
                                          lerp(b,d,j/nz)))
    for j in range(nz):
        for i in range(nx):
            hidden=any(x0<=i<x1 and y0<=j<y1
                       for x0,x1,y0,y1 in holes.values())
            if not hidden:face(name,indices[i,j],indices[i+1,j],
                               indices[i+1,j+1],indices[i,j+1])
    per=boundary(nx,nz)
    assert len(per)==2*(nx+nz)
    return ([position(*p) for p in per],
            {key:[position(*p) for p in gridloop(*spec)]
             for key,spec in holes.items()})

def hand_and_arm(side,key,socket):
    arm_box=BOXES[key]
    cx=3.65
    # Hand cap has four independent finger apertures and one thumb aperture.
    holes={str(i):(1+2*i,2+2*i,4,7) for i in range(4)}
    holes['thumb']=(7,9,1,2)
    def handpos(i,j):
        u=(i-5)/5;v=(j-4)/4
        z,y=disk(u,v,.137,.089)
        return (side*2.337,cx+y,z)
    endloop,digits=capgrid(key,10,8,handpos,(.672,.045,.822,.95),holes)
    assert len(endloop)==36
    socket_y=sum(p[1] for p in socket)/len(socket)
    socket_z=sum(p[2] for p in socket)/len(socket)
    source_angles=[math.atan2(p[2]-socket_z,p[1]-socket_y) for p in socket]
    # Smooth shoulder/biceps/elbow/forearm transition, preserving 36 quad
    # longitudinal loops. Do not create a separate floating shoulder sphere.
    armprofile=controls([
      [.60,.200,.194],[.78,.198,.185],[.99,.167,.157],
      [1.25,.121,.117],[1.39,.108,.102],[1.59,.140,.134],
      [1.79,.122,.115],[2.00,.088,.088],[2.16,.078,.101],
      [2.26,.075,.121]
    ],2)
    rings=[ring(key,socket,.94,(.01,.654))]
    for k,(x,ry,rz) in enumerate(armprofile):
        blend=smooth(min(1.,(k+1)/6.))
        target=[(side*x,lerp(socket_y,cx,blend)+ry*math.cos(t),rz*math.sin(t))
                for t in source_angles]
        points=[mix([a[0]+side*.045*(k+1),a[1],a[2]],b,blend)
                for a,b in zip(socket,target)]
        rings.append(ring(key,points,.94-(k+1)*.87/(len(armprofile)+1),
                          (.01,.654)))
        strip(key,rings[-2],rings[-1])
    terminal=ring(key,endloop,.055,(.01,.654))
    strip(key,rings[-1],terminal)
    # Separate cap vertices are exact coincident positions: physically
    # welded by construction, UV boundaries remain properly distinct.
    for digit,perimeter in digits.items():
        thumb=(digit=='thumb')
        index=4 if thumb else int(digit)
        center=[sum(p[d] for p in perimeter)/len(perimeter)
                for d in range(3)]
        n=len(perimeter)
        center_y=center[1];center_z=center[2]
        angle=[math.atan2(p[2]-center_z,p[1]-center_y)
               for p in perimeter]
        strip_u=(.834+.032*index,.861+.032*index)
        digit_rings=[ring(key,perimeter,.91,strip_u)]
        length=(.153 if thumb else (.174,.216,.212,.175)[index])
        for k in range(1,7):
            t=k/6
            rad_y=.032*(1-.68*t)
            rad_z=.026*(1-.63*t)
            p=[(side*(2.337+length*t),
                center_y-(.056*t if thumb else 0)+rad_y*math.cos(a),
                center_z+(.084*t if thumb else 0)+rad_z*math.sin(a))
                for a in angle]
            digit_rings.append(ring(key,p,.91-.81*t,strip_u))
            strip(key,digit_rings[-2],digit_rings[-1])
        final=(side*(2.337+length+.012),
               center_y-(.061 if thumb else 0),
               center_z+(.09 if thumb else 0))
        close_tip(key,digit_rings[-1],final,.055,strip_u)

def leg(side,key,opening):
    center=[sum(p[d] for p in opening)/len(opening)
            for d in range(3)]
    theta=[math.atan2(p[2]-center[2],p[0]-center[0])
           for p in opening]
    line=controls([
      [side*.235,2.185,0,.177,.180],
      [side*.255,2.09,0,.196,.202],
      [side*.278,1.99,0,.212,.215],
      [side*.316,1.84,0,.225,.218],
      [side*.325,1.62,0,.177,.183],
      [side*.325,1.42,0,.126,.132],
      [side*.325,1.31,0,.116,.120],
      [side*.327,1.12,-.012,.150,.159],
      [side*.327,.91,-.020,.158,.163],
      [side*.326,.71,-.004,.120,.128],
      [side*.326,.43,0,.086,.093],
      [side*.326,.29,.015,.089,.097],
      [side*.326,.205,.13,.105,.119],
      [side*.326,.151,.285,.115,.115],
      [side*.326,.130,.425,.068,.072],
      [side*.326,.128,.471,.035,.040]
    ],2)
    rings=[ring(key,opening,.955)]
    for k,(x,y,z,rx,rz) in enumerate(line):
        last=line[max(0,k-1)];following=line[min(len(line)-1,k+1)]
        ty=following[1]-last[1];tz=following[2]-last[2]
        length=math.hypot(ty,tz) or 1
        by=tz/length;bz=-ty/length
        p=[(x+rx*math.cos(a),y+rz*math.sin(a)*by,
            z+rz*math.sin(a)*bz) for a in theta]
        blend=smooth(min(1.,(k+1)/7.))
        p=[mix([a[0],a[1]-.045*(k+1),a[2]],b,blend)
           for a,b in zip(opening,p)]
        rings.append(ring(key,p,.955-(k+1)*.875/(len(line)+1)))
        strip(key,rings[-2],rings[-1],reverse=True)
    close_tip(key,rings[-1],(side*.326,.125,.513),.055)

def assemble():
    end,shoulders,hips=torso_geometry()
    cranial_surface(end)
    hand_and_arm(-1,'leftArm',shoulders['leftArm'])
    hand_and_arm(1,'rightArm',shoulders['rightArm'])
    leg(-1,'leftLeg',hips['leftLeg'])
    leg(1,'rightLeg',hips['rightLeg'])
    smooth_welded_junctions()
    return anatomy_uv_charts()

def smooth_welded_junctions():
    # Smooth the shared physical mesh, NOT its duplicated UV seam vertices.
    # Localized passes blend the armpit, hip and groin surfaces into the limbs.
    # Preserve fingers, feet and the overall torso silhouette.
    coords=[tuple(P[i:i+3]) for i in range(0,len(P),3)]
    unique={p:i for i,p in enumerate(dict.fromkeys(coords))}
    verts=list(unique);ids=[unique[p] for p in coords]
    adj=[set() for p in verts]
    for _,q in Q:
        for a,b in zip(q,q[1:]+q[:1]):
            a,b=ids[a],ids[b];adj[a].add(b);adj[b].add(a)
    def weight(p):
        x,y,z=p;x=abs(x)
        hip=math.exp(-((y-2.24)/.31)**4)*math.exp(-((x-.26)/.32)**4)
        shoulder=math.exp(-((y-3.54)/.35)**4)*math.exp(-((x-.48)/.35)**4)
        head=.40*math.exp(-((y-4.52)/.34)**4)
        return max(hip,shoulder,head)
    weights=[weight(p) for p in verts]
    for iteration in range(8):
        updated=[]
        for i,p in enumerate(verts):
            near=adj[i]
            if not near:updated.append(p);continue
            avg=[sum(verts[j][d] for j in near)/len(near) for d in range(3)]
            updated.append(tuple(mix(p,avg,.46*weights[i])))
        verts=updated
    P[:]=[round(v,6) for i in ids for v in verts[i]]

def anatomy_uv_charts():
    """Split UV coordinates, never 3D faces, into paintable anatomical views.

    Six region boxes contain separate front/back torso, pelvis, facial,
    back-of-head and crown subcharts. UV seams duplicate vertices at the
    exact same 3D positions, so the mesh remains physically watertight.
    """
    global P,UV,Q
    oldp=P[:];olduv=UV[:];oldq=Q[:]
    newp=[];newuv=[];newq=[];cache={}
    counts=Counter()
    def original(n):
        return oldp[3*n:3*n+3],olduv[2*n:2*n+2]
    def normalized(name,n):
        pos,uv=original(n)
        a,b,c,d=BOXES[name]
        return pos,((uv[0]-a)/(c-a),(uv[1]-b)/(d-b))
    def select(name,quad):
        if name not in ('torso','head'):return name
        positions=[original(i)[0] for i in quad]
        if name=='torso' and all(normalized(name,i)[1][1]<.081 for i in quad):
            return 'pelvis'
        if name=='head' and max(p[1] for p in positions)>4.761:
            return 'crown'
        avg=sum(normalized(name,i)[1][0] for i in quad)/4
        return name+('Front' if .25<avg<.75 else 'Back')
    def remap(name,chart,i):
        pos,(u,v)=normalized(name,i)
        if chart in ('torsoFront','torsoBack','headFront','headBack'):
            if chart.endswith('Front'):
                col=(u-.25)/.5
            else:
                col=(u-.75)/.5 if u>=.75-1.e-6 else (u+.25)/.5
            col=max(0.,min(1.,col))
            if name=='head':
                left,right=(.025,.485) if chart=='headFront' else (.515,.975)
                row=.045+.86*v
            else:
                left,right=(.015,.485) if chart=='torsoFront' else (.515,.985)
                row=.165+.815*(v-.095)/.355
            return uvloc(name,left+(right-left)*col,row)
        if chart=='pelvis':
            return uvloc(name,.02+.96*u,.015+.115*v/.08)
        if chart=='crown':
            x,y,z=pos
            return uvloc(name,.37+.26*x/.255,.932+.055*z/.23)
        return original(i)[1]
    for name,quad in oldq:
        chart=select(name,quad)
        counts[chart]+=1
        indices=[]
        for i in quad:
            pos,_=original(i)
            new=remap(name,chart,i)
            key=(i,round(new[0],7),round(new[1],7))
            if key not in cache:
                cache[key]=len(newp)//3
                newp.extend(pos);newuv.extend(new)
            indices.append(cache[key])
        newq.append((name,tuple(indices)))
    P[:]=newp;UV[:]=newuv;Q[:]=newq
    required={'headFront','headBack','crown','torsoFront','torsoBack','pelvis'}
    if not required.issubset(counts):
        raise ValueError('Missing UV anatomy charts '+str(required-set(counts)))
    return dict(counts)

def audit_and_orient():
    """UV seams can duplicate vertices, but the 3D surface has no open edges."""
    positions=[tuple(P[i:i+3]) for i in range(0,len(P),3)]
    weld={}
    geometry=[]
    for p in positions:
        if p not in weld:weld[p]=len(weld)
        geometry.append(weld[p])
    edge_faces=defaultdict(list)
    for fi,(group,face_ids) in enumerate(Q):
        physical=[geometry[n] for n in face_ids]
        if len(set(physical))!=4:
            raise ValueError(('Degenerate quad in welded 3D geometry',group,fi))
        for k in range(4):
            a=physical[k];b=physical[(k+1)%4]
            edge_faces[tuple(sorted((a,b)))].append((fi,a,b))
    boundary=[(edge,len(inc)) for edge,inc in edge_faces.items() if len(inc)!=2]
    if boundary:raise ValueError('Non-manifold/open 3D edges: '+repr(boundary[:12])+
                                  ' count='+str(len(boundary)))
    adj=defaultdict(list)
    for records in edge_faces.values():
        (i,a,b),(j,c,d)=records
        # Shared physical edges must be traversed in opposite directions.
        same=(a==c and b==d)
        adj[i].append((j,int(same)))
        adj[j].append((i,int(same)))
    flips={0:0};todo=deque([0])
    while todo:
        i=todo.popleft()
        for j,parity in adj[i]:
            wanted=flips[i]^parity
            if j in flips:
                if flips[j]!=wanted:raise ValueError('Non-orientable quad junction')
            else:flips[j]=wanted;todo.append(j)
    if len(flips)!=len(Q):
        raise ValueError('Disconnected 3D surface components: '+str(len(Q)-len(flips)))
    triangles=[]
    for fi,(name,quad_ids) in enumerate(Q):
        a,b,c,d=quad_ids
        if flips[fi]:a,b,c,d=a,d,c,b
        triangles.append((name,(a,b,c)))
        triangles.append((name,(a,c,d)))
    volume=0.
    for name,(a,b,c) in triangles:
        A=positions[a];B=positions[b];C=positions[c]
        volume+=(A[0]*(B[1]*C[2]-B[2]*C[1])+
                 A[1]*(B[2]*C[0]-B[0]*C[2])+
                 A[2]*(B[0]*C[1]-B[1]*C[0]))/6.
    if abs(volume)<.1:raise ValueError('Degenerate welded volume '+str(volume))
    if volume<0:
        triangles=[(name,(a,c,b)) for name,(a,b,c) in triangles]
    for name,t in triangles:
        F.extend(t);GROUP.append(name)
    report={'weldedVertices':len(weld),'weldedEdges':len(edge_faces),
            'openEdges':0,'nonManifoldEdges':0,'connectedComponents':1,
            'watertight':True,'oriented':True,'signedVolume':round(abs(volume),5)}
    return report

def texture():
    """Paint the ACTUAL UV surfaces, not the six bounding rectangles.

    Front/back panels, pelvis, scalp, arm cores and fingers are visible as
    separate islands on the diagnostic skin. The no-text artwork is genuinely
    importable as the model texture, without wireframe or region names.
    """
    size=1024
    background=Image.new('RGB',(size,size),(18,26,36))
    mask=Image.new('L',(size,size),0)
    dm=ImageDraw.Draw(mask)
    colors={
      'head':(181,210,216),'torso':(143,175,189),
      'leftArm':(147,192,183),'rightArm':(148,187,187),
      'leftLeg':(155,172,192),'rightLeg':(160,174,196)}
    for name,quad in Q:
        polygon=[(round(UV[2*i]*size),round((1-UV[2*i+1])*size))
                 for i in quad]
        dm.polygon(polygon,fill=255)
    grid=Image.new('RGB',(size,size),(18,26,36))
    dg=ImageDraw.Draw(grid)
    for name,(u0,v0,u1,v1) in BOXES.items():
        x0=round(u0*size);x1=round(u1*size)
        y0=round((1-v1)*size);y1=round((1-v0)*size)
        col=colors[name]
        dg.rectangle((x0,y0,x1,y1),fill=col)
        dark=tuple(max(0,c-21) for c in col)
        for k in range(1,32):
            x=round(lerp(x0,x1,k/32))
            dg.line((x,y0,x,y1),fill=dark,width=1)
        for k in range(1,34):
            y=round(lerp(y0,y1,k/34))
            dg.line((x0,y,x1,y),fill=dark,width=1)
    # No labels are painted into the actual texture; chart boundaries and
    # empty gutters remain clear after the geometric UV mask is applied.
    background.paste(grid,(0,0),mask)
    # Front and rear panels have an actual empty UV gutter, unlike the old
    # misleading six full colored rectangles.
    for u,v in ((.145,.29),(.6425,.29)):
        pixel=background.getpixel((round(u*size),round((1-v)*size)))
        if pixel!=(18,26,36):
            raise ValueError(('Actual anatomical UV chart gutter missing',u,v,pixel))
    ATLAS.parent.mkdir(parents=True,exist_ok=True)
    background.save(ATLAS,optimize=True)
    return ATLAS.read_bytes()
def guide():
    size=2048
    im=Image.new('RGB',(size,size),(15,23,36));d=ImageDraw.Draw(im)
    colors={'head':(239,95,95),'torso':(87,155,243),
      'leftArm':(64,197,115),'rightArm':(231,184,63),
      'leftLeg':(168,110,231),'rightLeg':(244,125,76)}
    for k in range(0,len(F),3):
        points=[(round(UV[F[k+i]*2]*size),
                 round((1-UV[F[k+i]*2+1])*size)) for i in range(3)]
        d.line(points+[points[0]],fill=colors[GROUP[k//3]],width=1)
    # Labels and anatomy descriptions belong on the guide, NEVER the painted
    # skin. Labels identify the view and which direction is the head/waist.
    labels=[
      ('FACE',( .029,.40)),('HEAD BACK',(.153,.40)),
      ('SCALP',(.100,.463)),
      ('CHEST FRONT',(.317,.431)),('TORSO BACK',(.652,.431)),
      ('WAIST / GROIN',(.38,.087)),
      ('LEFT ARM / PALM',(.024,.938)),('RIGHT ARM / PALM',(.269,.938)),
      ('LEFT LEG / INSTEP',(.515,.938)),('RIGHT LEG / INSTEP',(.759,.938))]
    for txt,(u,v) in labels:
        d.text((int(u*size),int((1-v)*size)),txt,fill=(255,255,255),
               stroke_width=2,stroke_fill=(15,23,36))
    GUIDE.parent.mkdir(parents=True,exist_ok=True)
    im.save(GUIDE,optimize=True)

def main():
    charts=assemble()
    assert len(P)//3<=9000 and len(F)==0
    assert len(Q)*2<=16000
    assert len(UV)==len(P)//3*2 and all(0<=x<=1 for x in UV)
    audit=audit_and_orient()
    assert all(0<=i<len(P)//3 for i in F)
    assert len(QUADS)==6
    paint=texture();guide()
    scene=json.loads(BASE.read_text('utf8'))
    project=scene['project'];project['name']='Clean Topology Humanoid · UV-First'
    project['canonicalId']=project['template']='clean-topology-humanoid'
    atelier=project['modelAtelier']
    atelier['name']='Clean Topology Humanoid · Welded Quad-Loop Sculpt Base'
    atelier['reference']=(
      'UV-first sculptable T-pose humanoid with one welded watertight quad '
      'surface. Procedural shoulders, neck, crotch, fingers, thumb, crown '
      'and toes are topologically connected. Sculpted groin, waist and hips '
      'connect to both upper thighs. Separate front/back torso, face/scalp '
      'and pelvis UV subcharts remain within six anatomical regions. '
      'Regular checker skin diagnoses stretching. Unrigged test starter.')
    part=atelier['parts'][0]
    part.update(id='clean-topology-humanoid-base',
      name='Clean Topology Humanoid · connected quad-loop UV mesh',
      group='Humanoid · UV-first',kind='topologyMesh',
      color='#b0c3d0',material='matte',
      topologyMesh={'positions':P,'uvs':UV,'indices':F},
      uvPaintPNG='data:image/png;base64,'+base64.b64encode(paint).decode('ascii'))
    scene['version']=11.554
    scene['engine']='§wyrl§ Engine · Maker v11.552 / UV-First Starter revision'
    OUTPUT.write_text(json.dumps(scene,separators=(',',':'),ensure_ascii=False),'utf8')
    report={'version':'v11.554','revision':'anatomical-curves-pre-xatlas-v4',
      'vertices':len(P)//3,'triangles':len(F)//3,
      'quads':dict(QUADS),'components':1,
      'uvBoxes':BOXES,'uvCharts':charts,'uvPaintMode':'actual-UV-quad-island-masking',
      'guideAnatomyLabels':True,'textureSize':1024,'guideSize':2048,
      'originalRobotPreserved':True,'quadFirst':True,
      'junctionSmoothing':'welded-local-eight-pass','limbSocketBlend':True,
      'topologyAudit':audit}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('SE554_UV_FIRST_WELDED_AUTHOR_PASS',json.dumps(report),flush=True)
if __name__=='__main__':main()
