#!/usr/bin/env python3
"""§E Sorting Hat v11.485 — one native UV-painted, editable cloth mesh.

The eye sockets, brows, nose and mouth are signed displacement fields of the
same crown vertices, not additional shapes, eye holes, face cards or cutouts.
Brim and underside are also continuous strips in this single mesh part.
Deterministic standard-library PNG paint stays in the native 360k data-URI cap.
The first 49-part assembly is preserved in the v11.483 backup scene.
"""
import base64
import copy
import json
import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scenes/model-atelier-sorting-hat-v11-483-assembly.swyrl.json"
TARGET = ROOT / "scenes/model-atelier-sorting-hat.swyrl.json"
TAU = 2 * math.pi
ANGULAR = 96
# Each ring has a duplicated UV vertex along the hidden back meridian. Despite
# the UV seam, every component is connected through a *single* mesh surface.
# Tip -> crown: a continuous fabric hook, not the abrupt folded triangle
# seen on the first mobile render. Radii broaden gradually while the center
# traces a gentle rightward droop: the very end is below the upper crest.
# Keep eight rings so the single-mesh topology / UV indices remain identical.
TIP = [
    (2.735, .022, .955, -.270),  # softly rounded hanging end
    (2.790, .063, .920, -.268),
    (2.880, .112, .855, -.256),
    (2.987, .164, .775, -.238),
    (3.075, .225, .680, -.218),
    (3.095, .288, .555, -.192),  # rounded upper bend
    (3.020, .355, .440, -.168),
    (2.925, .418, .345, -.156),  # flows into the existing crown
]
BODY = [
    (.22,.875,.00,.00), (.43,.895,-.005,.005),
    (.75,.852,-.018,.00), (1.10,.760,-.036,-.018),
    (1.43,.715,-.035,-.025), (1.71,.676,-.028,-.032),
    (2.02,.625,-.015,-.06), (2.30,.560,.065,-.107),
    (2.58,.505,.19,-.14), (2.82,.451,.29,-.15),
]

def clamp(x, lo=0., hi=1.):
    return max(lo,min(hi,x))

def g(x,c,s):
    return math.exp(-((x-c)/s)**2)

def interp(y):
    for a,b in zip(BODY,BODY[1:]):
        if a[0] <= y <= b[0]:
            t=(y-a[0])/(b[0]-a[0])
            t=t*t*(3-2*t)
            return tuple(a[i]*(1-t)+b[i]*t for i in range(1,4))
    return BODY[0][1:] if y<BODY[0][0] else BODY[-1][1:]

def outer_point(y,theta,profile):
    radius,cx,cz=profile
    xnorm=math.cos(theta)
    sn=math.sin(theta)
    x=cx+radius*xnorm
    # Dents and ridges are a signed displacement of the cloth shell itself.
    front=max(0.,sn)**6
    wrinkle=(.038*math.sin(3*theta+3.4*y)
            +.023*math.sin(8*theta-6*y)
            +.011*math.sin(15*theta+2*y))
    displacement=radius*wrinkle
    for sign in (-1,1):
        cxeye=sign*.355
        # Eye = INWARD cloth depression. Never cut geometry / use black holes.
        displacement-=.168*g(x,cxeye,.202)*g(y,1.665,.132)*front
        # Eyebrow = a thick raised fold in the exact same fabric.
        brow_y=1.885+.075*sign*(x-cxeye)
        displacement+=.148*g(x,cxeye,.255)*g(y,brow_y,.105)*front
        # Gentle cheek and eye-corner crease.
        displacement-=.040*g(x,sign*.55,.095)*g(y,1.40,.26)*front
    # Nose emerges organically from the front cloth.
    displacement+=.114*g(x,.005,.152)*g(y,1.44,.310)*front
    displacement+=.049*g(x,0,.20)*g(y,1.20,.12)*front
    # Speaking mouth = a narrow recessed fold with soft built-in lips.
    mouth_y=1.105+.065*x
    displacement-=.170*g(x,0,.54)*g(y,mouth_y,.075)*front
    displacement+=.066*g(x,0,.57)*g(y,mouth_y+.104,.067)*front
    displacement+=.062*g(x,0,.51)*g(y,mouth_y-.120,.074)*front
    # Crown shoulder fabric compression and long natural irregular folds.
    displacement+=.058*g(y,2.15,.58)*math.sin(theta*3.2+y*5.7)
    displacement+=.035*g(y,.53,.26)*math.sin(theta*2.1+1.2)
    r=max(.008,radius+displacement)
    yy=y+.015*math.sin(theta*3.1+y*4.8)+.009*math.sin(theta*7-y*6)
    return (cx+r*xnorm,yy,cz+.93*r*sn)

def brim_point(theta,r,under=False):
    a=clamp((r-.86)/.75)
    varying=r*(1+.045*math.sin(3*theta+.45)+.031*math.sin(7*theta-.3))
    y=(.22-.13*a + .092*a*math.sin(theta*2+.4)
       +.087*a*math.sin(theta*5-1.1)
       +.108*a*g(math.cos(theta),-.91,.31)
       +.108*a*g(math.cos(theta),.90,.28)
       -.030*g(math.sin(theta),1,.32))
    if under:y-=.073
    return (varying*math.cos(theta),y,.90*varying*math.sin(theta))

def inner_point(y,theta):
    r,cx,cz=interp(clamp(y,.22,2.82))
    r=max(.065,r-.095)
    return (cx+r*math.cos(theta),y-.035,cz+.92*r*math.sin(theta))

def build_mesh():
    # Outermost cone tip down, flared brim across, return below its underside
    # and back up the inside: one topologically connected fabric skin.
    rows=[]
    for profile in TIP:
        y=profile[0]
        rows.append(("crown",y,profile[1:]))
    for i in range(52):
        y=2.82+( .22-2.82)*i/51
        rows.append(("crown",y,interp(y)))
    for i in range(6):
        r=.96+(1.61-.96)*i/5
        rows.append(("brim-upper",r,None))
    rows.append(("brim-lip",1.61,None))
    for i in range(6):
        r=1.49+(.77-1.49)*i/5
        rows.append(("brim-under",r,None))
    for i in range(8):
        y=.30+(2.80-.30)*i/7
        rows.append(("inner",y,None))
    assert len(rows)==81,len(rows)
    m={"positions":[],"uvs":[],"indices":[]}
    def vert(p,u,v):
        m["positions"].extend(round(x,5) for x in p)
        m["uvs"].extend((round(u,5),round(v,5)))
        return len(m["positions"])//3-1
    def point(row,theta):
        typ,value,profile=row
        if typ=="crown": return outer_point(value,theta,profile)
        if typ=="brim-upper":return brim_point(theta,value)
        if typ=="brim-lip":return brim_point(theta,value,True)
        if typ=="brim-under":return brim_point(theta,value,True)
        return inner_point(value,theta)
    for i,row in enumerate(rows):
        kind,a,_=row
        if kind=="crown":v=.28+.70*clamp((a-.20)/2.91)
        elif kind=="brim-upper":v=.28-.10*clamp((a-.875)/(.74))
        elif kind=="brim-lip":v=.15
        elif kind=="brim-under":v=.15-.075*clamp((1.61-a)/.84)
        else:v=.075-.068*clamp((a-.30)/2.5)
        for j in range(ANGULAR+1):
            theta=-math.pi/2+TAU*j/ANGULAR
            vert(point(row,theta),j/ANGULAR,v)
    stride=ANGULAR+1
    for i in range(len(rows)-1):
        for j in range(ANGULAR):
            a=i*stride+j;b=(i+1)*stride+j
            # Consistent outside (normal points outward for crown,
            # up across brim top, down beneath brim, inward in lining).
            m["indices"].extend((a,a+1,b,a+1,b+1,b))
    # Surface caps only at the pointed external tip and internal tip.
    outer_c=vert((TIP[0][2],TIP[0][0],TIP[0][3]),.5,.978)
    last=len(rows)-1
    internal_c=vert((.55,2.85,-.22),.5,.005)
    for j in range(ANGULAR):
        m["indices"].extend((outer_c,j+1,j))
        a=last*stride+j
        m["indices"].extend((internal_c,a,a+1))
    assert len(m["positions"])//3 < 9000
    assert len(m["indices"])//3 < 16000
    return m,rows

def png_rgb(w,h,pixels):
    raw=bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y*w*3:(y+1)*w*3])
    def chunk(name,data):
        return (struct.pack(">I",len(data))+name+data+
                struct.pack(">I",zlib.crc32(name+data)&0xffffffff))
    return (b"\x89PNG\r\n\x1a\n"+
            chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+
            chunk(b"IDAT",zlib.compress(bytes(raw),9))+
            chunk(b"IEND",b""))

def paint(w):
    pixels=bytearray()
    for py in range(w):
        v=1.-py/(w-1)
        # The outer crown is an intentionally legible continuous UV chart.
        height=.20+2.91*(v-.28)/.70
        for px in range(w):
            u=px/(w-1)
            theta=-math.pi/2+TAU*u
            sn=math.sin(theta)
            front=max(0,sn)**6
            radius,_,_=interp(clamp(height,.22,2.82))
            x=radius*math.cos(theta)
            weave=1.2*math.sin(px*.51)+1.1*math.cos(py*.57)
            grain=2.8*math.sin(px*.082+py*.021)*math.sin(py*.17-px*.065)
            folds=6*math.sin(5.2*theta+height*3.5)+4*math.cos(theta*8-height*2.6)
            wear=6.5*math.sin(theta*2.3+2*height)+2.8*math.sin(py*.046+px*.029)
            tint=weave+grain+folds+wear
            # Gradual shadow *inside dents*, not dark rectangles or eye holes.
            if v>.28:
                for sign in (-1,1):
                    eye=g(x,sign*.355,.218)*g(height,1.655,.145)*front
                    brow=g(x,sign*.355,.28)*g(height,1.875,.105)*front
                    tint-=33*eye
                    tint+=14*brow
                mouth=g(x,0,.53)*g(height,1.105+.065*x,.082)*front
                tint-=41*mouth
                tint+=10*g(x,0,.52)*g(height,1.19,.07)*front
                tint+=8*g(x,0,.49)*g(height,.97,.075)*front
                tint+=9*g(x,0,.18)*g(height,1.39,.29)*front
                # Rear repairs are painted into the material, not separate meshes.
                back=max(0,-sn)**6
                for uc,vc,rx,ry,shift in ((.10,.58,.066,.078,9),(.92,.45,.040,.059,-7)):
                    du=min(abs(u-uc),1-abs(u-uc))
                    profile=max(du/rx,abs(v-vc)/ry)
                    if profile<1:
                        tint+=shift*(1-.25*profile)*back
                    if .84<profile<.92 and ((px//9+py//11)%3)<2:
                        tint+=11*back
            else:
                # Same UV image handles brim and lining without adding geometry.
                tint+=-5+5*math.sin(u*TAU*4)+4*math.sin(py*.06)
                seam=abs(v-.192)
                tint+=9*g(seam,0,.005)
                if abs(v-.202)<.003 and (px//13)%3==0:tint+=12
            # Tobacco-brown woven aged cloth with soft pigment variation.
            rgb=(118+tint*1.05,86+tint*.87,58+tint*.73)
            for color in rgb:
                val=int(clamp(color,12,238))
                pixels.append(4*round(val/4))  # compressible subtle fabric grain
    return png_rgb(w,w,pixels)

def build_texture():
    for res in (768,640,512):
        data=png_rgb(1,1,b"\x00\x00\x00") if False else paint(res)
        uri="data:image/png;base64,"+base64.b64encode(data).decode("ascii")
        if len(uri)<=360000:
            return uri,res,len(data)
    raise AssertionError("Unable to fit baked cloth paint under native texture limit")

def make():
    scene=json.loads(SOURCE.read_text("utf8"))
    assert len(scene["project"]["modelAtelier"]["parts"])==49
    geometry,rows=build_mesh()
    texture,dimension,pngbytes=build_texture()
    part={"id":"sorting-hat-one-sculpt","name":"Sorting Hat · unified sculpted cloth surface",
          "group":"Single cloth mesh","kind":"topologyMesh",
          "position":[0,0,0],"rotation":[0,0,0],"scale":[1,1,1],
          "color":"#ffffff","material":"matte","topologyMesh":geometry,
          "uvPaintPNG":texture}
    model=scene["project"]["modelAtelier"]
    model["parts"]=[part]
    model["meshGroups"]=[]
    model["reference"]=(
        "One original editable connected cloth mesh. Eyes are dents, NOT holes; "
        "eyebrows, nose and talking-mouth recess are sculpted into the same surface, "
        "with UV-painted shadows and wrinkles. Bent tip, double-sided wavy brim, "
        "lining and rear repair cloth are all regions of this sole mesh. "
        "Source: owner-supplied Sorting Hat sketch and multi-view fabric study. "
        "The v11.483 49-object assembly remains backed up in Git history/scene."
    )
    model["name"]="The Sorting Hat · One Cloth Mesh"
    model["editedAt"]="local"
    scene["project"]["name"]="The Sorting Hat"
    scene["project"]["canonicalId"]="sorting-hat"
    scene["project"]["template"]="sorting-hat"
    scene["engine"]="§wyrl§ Engine · Maker v11.485"
    scene["version"]=11.485
    output=json.dumps(scene,ensure_ascii=False,separators=(",",":"))+"\n"
    TARGET.write_text(output,"utf8")
    tris=len(geometry["indices"])//3
    verts=len(geometry["positions"])//3
    # User's key anatomical correction: blind/continuous topology across
    # all face dents, no separate eye, brow, mouth or nose mesh parts.
    assert len(model["parts"])==1 and len(geometry["uvs"])==verts*2
    assert tris<16000 and verts<9000
    assert all(0<=j<verts for j in geometry["indices"])
    assert texture.startswith("data:image/png;base64,") and len(texture)<=360000
    assert len({tuple(geometry["positions"][i:i+3]) for i in range(0,len(geometry["positions"]),3)})>6500
    print(json.dumps({"status":"SORTING_HAT_ONE_CLOTH_PASS",
                      "parts":1,"verts":verts,"triangles":tris,
                      "angularRows":len(rows),"pngSize":pngbytes,
                      "paintResolution":dimension,"paintURIChars":len(texture),
                      "sceneBytes":len(output.encode("utf8"))}),flush=True)

if __name__=="__main__":
    make()
