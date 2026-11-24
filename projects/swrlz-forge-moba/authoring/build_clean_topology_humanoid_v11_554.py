#!/usr/bin/env python3
"""Author a separate UV-first quad-loop humanoid starter for the native §E Modeler.

One editable topologyMesh with deliberately distinct structural components. Ring
surfaces are laid out as regular quads before triangulation; the UV coordinates
follow those loops instead of being reprojected from triangulated geometry.
The older robotic humanoid and all account projects remain byte-for-byte intact.
"""
import base64
from collections import Counter
from io import BytesIO
import json, math
from pathlib import Path
from PIL import Image, ImageDraw

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
P=[];UV=[];F=[];GROUP=[];QUADS=Counter()
def clamp(v):return min(1.,max(0.,v))
def interp(a,b,t):return [x*(1-t)+y*t for x,y in zip(a,b)]
def sample_controls(controls,subdiv=3):
    rows=[]
    for k in range(len(controls)-1):
        for j in range(subdiv):
            t=j/subdiv
            # Geometry is smooth and deterministic; UV order is independent
            # of the resulting vertices' positions.
            t=t*t*(3-2*t)
            rows.append(interp(controls[k],controls[k+1],t))
    rows.append(list(controls[-1]))
    return rows
def ring_surface(name,rows,sides,box,orient,flip=False):
    """Uniform all-quad rings, with one intentional U seam per component."""
    xmin,ymin,xmax,ymax=box
    start=len(P)//3
    for k,row in enumerate(rows):
        cx,cy,cz,r1,r2=row
        for n in range(sides+1):
            ang=math.tau*n/sides
            ca,sa=math.cos(ang),math.sin(ang)
            if orient=='vertical':
                xyz=(cx+ca*r1,cy,cz+sa*r2)
            elif orient=='horizontal':
                xyz=(cx,cy+ca*r1,cz+sa*r2)
            else:raise ValueError(orient)
            P.extend(round(float(x),5) for x in xyz)
            UV.extend((round(xmin+(xmax-xmin)*n/sides,6),
                       round(ymax-(ymax-ymin)*k/(len(rows)-1),6)))
    for k in range(len(rows)-1):
        for n in range(sides):
            a=start+k*(sides+1)+n;b=a+sides+1
            if flip:F.extend((a,b,a+1,a+1,b,b+1))
            else:F.extend((a,a+1,b,a+1,b+1,b))
            GROUP.extend((name,name));QUADS[name]+=1
def head():
    # A sphere is sculpted into a head without modifying its longitude/latitude
    # topology or rectangular, uninterrupted sphere UV chart.
    rows=[]
    for k in range(1,25):
        theta=math.pi*k/25
        sn,cs=math.sin(theta),math.cos(theta)
        y=4.415+.345*cs
        taper=1-.22*max(0.,-cs)
        rows.append([0,y,0,.245*sn*taper,.225*sn])
    # Slightly fuller cheeks + a narrower sculpted chin: rings remain regular.
    ring_surface('head',rows,32,BOXES['head'],'vertical',False)
def torso():
    controls=[
      [0,2.25,0,.304,.195],[0,2.45,0,.357,.230],
      [0,2.65,0,.306,.205],[0,2.94,0,.287,.200],
      [0,3.21,0,.334,.227],[0,3.44,0,.429,.255],
      [0,3.62,0,.472,.245],[0,3.77,0,.408,.223],
      [0,3.91,0,.175,.152],[0,4.08,0,.127,.118],
      [0,4.16,0,.119,.110]
    ]
    ring_surface('torso',sample_controls(controls,3),32,BOXES['torso'],'vertical',True)
def arms(side):
    key='leftArm' if side<0 else 'rightArm'
    controls=[
      [side*.46,3.64,0,.19,.191],[side*.60,3.65,0,.208,.191],
      [side*.83,3.65,0,.176,.164],[side*1.08,3.65,0,.147,.139],
      [side*1.34,3.65,0,.105,.105],[side*1.43,3.65,0,.100,.095],
      [side*1.69,3.65,0,.139,.132],[side*1.95,3.65,0,.082,.080],
      [side*2.08,3.65,0,.076,.086],[side*2.18,3.65,0,.072,.119],
      [side*2.31,3.65,0,.050,.135],[side*2.36,3.65,0,.036,.127]
    ]
    b=BOXES[key]
    main=(b[0],b[1],b[0]+(b[2]-b[0])*.74,b[3])
    ring_surface(key,sample_controls(controls,3),20,main,'horizontal',side<0)
    # Five individually selectable-in-UV finger strips, including thumb.
    # The fingers are separate surface components, not distorted torso charts.
    for digit in range(5):
        thumb=digit==4
        z=(.145 if thumb else -.106+digit*.072)
        y=(3.57 if thumb else 3.65)
        length=(.145 if thumb else [.180,.234,.223,.173][digit])
        x0=(2.17 if thumb else 2.34)
        rows=[]
        for k in range(6):
            t=k/5
            rows.append([side*(x0+length*t),y+(t*.035 if thumb else 0),
                        z+(t*.074 if thumb else 0),
                        .036*(1-.52*t),.028*(1-.50*t)])
        x0uv=b[0]+(b[2]-b[0])*(.77+digit*.042)
        x1uv=b[0]+(b[2]-b[0])*(.802+digit*.042)
        ring_surface(key,rows,8,(x0uv,b[1]+.045*(b[3]-b[1]),
                                   x1uv,b[3]-.065*(b[3]-b[1])),
                     'horizontal',side<0)
def legs(side):
    key='leftLeg' if side<0 else 'rightLeg'
    x=side*.315
    controls=[
        [x,2.36,0,.160,.175],[x,2.25,0,.204,.208],
        [x,2.05,0,.222,.225],[x,1.86,0,.220,.214],
        [x,1.62,0,.177,.182],[x,1.44,0,.133,.129],
        [x,1.32,0,.119,.121],[x,1.10,-.005,.157,.160],
        [x,.92,-.021,.161,.161],[x,.70,-.008,.122,.128],
        [x,.43,0,.087,.090],[x,.30,.015,.090,.098],
        [x,.21,.13,.112,.118],[x,.16,.27,.115,.120],
        [x,.13,.37,.106,.105],[x,.125,.46,.063,.072],
    ]
    # Leg skin follows ankle-to-toe sweep with one predictable longitudinal
    # UV direction and NO procedural sawtooth boundary cuts.
    ring_surface(key,sample_controls(controls,2),24,BOXES[key],'vertical',False)
def texture():
    s=1024
    img=Image.new('RGB',(s,s),(20,28,38))
    d=ImageDraw.Draw(img)
    for name,(u0,v0,u1,v1) in BOXES.items():
        l=int(u0*s);r=int(u1*s);top=int((1-v1)*s);bottom=int((1-v0)*s)
        base=PALETTE[name]
        d.rectangle((l,top,r,bottom),fill=base)
        # Regular twenty-cell grid is intentional distortion diagnostic. No
        # text or UV wireframe is baked into the model's material.
        for i in range(1,20):
            x=round(l+(r-l)*i/20)
            d.line((x,top,x,bottom),fill=tuple(max(0,c-19) for c in base),width=1)
        for i in range(1,22):
            y=round(top+(bottom-top)*i/22)
            d.line((l,y,r,y),fill=tuple(max(0,c-18) for c in base),width=1)
        d.rectangle((l,top,r,bottom),outline=(55,207,222),width=3)
    ATLAS.parent.mkdir(parents=True,exist_ok=True)
    img.save(ATLAS,optimize=True)
    return ATLAS.read_bytes()
def guide():
    s=2048
    im=Image.new('RGB',(s,s),(15,23,36));draw=ImageDraw.Draw(im)
    pal={'head':(239,95,95),'torso':(87,155,243),
         'leftArm':(64,197,115),'rightArm':(231,184,63),
         'leftLeg':(168,110,231),'rightLeg':(244,125,76)}
    for t in range(0,len(F),3):
        inds=F[t:t+3]
        pts=[(round(UV[i*2]*s),round((1-UV[i*2+1])*s)) for i in inds]
        draw.line(pts+[pts[0]],fill=pal[GROUP[t//3]],width=1)
    GUIDE.parent.mkdir(parents=True,exist_ok=True)
    im.save(GUIDE,optimize=True)
def main():
    head();torso();arms(-1);arms(1);legs(-1);legs(1)
    assert len(P)//3<9000 and len(F)//3<16000
    assert len(UV)==len(P)//3*2 and all(0<=v<=1 for v in UV)
    assert all(0<=i<len(P)//3 for i in F)
    assert len(QUADS)==6
    # UV edges are predictable rectangular ring coordinates, with no
    # image-derived sawtooth or variable triangle density in UV space.
    blob=texture();guide()
    scene=json.loads(BASE.read_text('utf8'))
    project=scene['project']
    project['name']='Clean Topology Humanoid · UV-First'
    project['canonicalId']='clean-topology-humanoid'
    project['template']='clean-topology-humanoid'
    atelier=project['modelAtelier']
    atelier['name']='Clean Topology Humanoid · Quad-Loop Sculpt Base'
    atelier['reference']=(
        'Experimental UV-first T-pose humanoid. Quad-indexed contour rings define '
        'an ellipsoid head, torso, two arms, five digits per hand and two legs '
        'with curved feet. Original UV seam locations remain stable when '
        'sculpting vertices. Separate surface components at anatomical junctions '
        'are intentional; this is not a single welded manifold and is unrigged. '
        'Neutral checker diagnostic skin reveals stretching; replace it freely.')
    part=atelier['parts'][0]
    part.update(id='clean-topology-humanoid-base',
        name='Clean Topology Humanoid · uniform quad-loop UV mesh',
        group='Humanoid · UV-first',kind='topologyMesh',
        color='#b0c3d0',material='matte',
        topologyMesh={'positions':P,'uvs':UV,'indices':F},
        uvPaintPNG='data:image/png;base64,'+base64.b64encode(blob).decode('ascii'))
    scene['version']=11.554
    scene['engine']='§wyrl§ Engine · Maker v11.552 / UV-First Starter v11.554'
    OUTPUT.write_text(json.dumps(scene,separators=(',',':'),ensure_ascii=False),'utf8')
    report={'version':'v11.554','vertices':len(P)//3,'triangles':len(F)//3,
            'quads':dict(QUADS),'components':6+10,
            'uvBoxes':BOXES,'textureSize':1024,'guideSize':2048,
            'originalRobotPreserved':True,'quadFirst':True}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('SE554_UV_FIRST_AUTHOR_PASS',json.dumps(report),flush=True)
if __name__=='__main__':main()
