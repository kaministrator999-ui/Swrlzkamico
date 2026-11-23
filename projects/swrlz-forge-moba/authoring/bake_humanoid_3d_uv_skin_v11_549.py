#!/usr/bin/env python3
"""v11.549: surface-registered high-detail AEGIS armor, native UV bake.

The earlier generated concept atlas has no pixel-to-surface correspondence;
its visual language (pearl panels, black inset mechanics, cyan emitters)
is reconstructed directly in world space on the actual 11.546 mesh.
Do not pretend 2D silhouette registration transfers semantic details.
"""
import json
import numpy as np
import bake_humanoid_3d_uv_skin_v11_548 as prev
base=prev.base
b=base.baker
base.NAME="futuristic-humanoid-v11-549-surface-registered-aegis"
base.FOUR=base.DEST/(base.NAME+"-4096.png")
base.TWO=base.DEST/(base.NAME+"-2048.png")
base.NATIVE=base.DEST/(base.NAME+"-1024.png")
base.VIEW=base.QA/(base.NAME+"-front-back-side.png")
base.REPORT=base.QA/(base.NAME+"-validation.json")

def surface_skin(points,normals):
    rgb,tags=prev.surface_skin(points,normals)
    rgb=rgb.astype(float)
    x,y,z=points.T
    nx,ny,nz=normals.T
    xa=np.abs(x)
    front=b.smooth(.12,.50,nz)
    back=b.smooth(.12,.50,-nz)
    side=b.smooth(.28,.72,np.abs(nx))
    head=(tags==0).astype(float)
    arm=(tags==1).astype(float)
    torso=(tags==2).astype(float)
    leg=(tags==3).astype(float)
    band=b.band
    smooth=b.smooth
    def paint(color,w):
        b.blend(rgb,color,np.clip(w,0,1))
    # Metallic bevels: a narrow specular rim and a neighboring graphite inset.
    def bevel(mask,coordinate,center,half,soft=.009):
        paint((27,39,49),mask*band(coordinate,center,half,soft)*.88)
        paint((249,251,248),mask*band(coordinate,center+half+.012,.007,.012)*.70)
        paint((113,136,149),mask*band(coordinate,center-half-.011,.006,.012)*.65)
    # Helmet: shell segments, temple vent, luminous sensor strip, rear socket.
    for h in (4.65,4.27):
        bevel(head*front,y,h,.009,.013)
    paint((24,35,46),head*side*band(y,4.47,.15,.05)*.86)
    for h in (4.38,4.45,4.52):
        paint((120,141,150),head*side*band(y,h,.008,.009)*.53)
    paint((25,235,236),head*front*band(y,4.478,.010,.008)*band(x,0,.145,.035)*.97)
    paint((20,32,42),head*back*band(x,0,.085,.03)*band(y,4.46,.27,.09)*.81)
    paint((29,212,224),head*back*band(x,0,.014,.009)*band(y,4.44,.095,.025)*.89)
    # Neck: dark collar gaskets and small raised-looking articulation.
    for h in (4.09,4.16,4.22):
        bevel(head+torso,y,h,.008,.009)
    # Chest: paired overlapping shell segments, inset negative-space seams.
    chest=torso*front*band(y,3.54,.34,.14)
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        arch=3.81-.50*np.clip(u/.58,0,1)**1.55
        bevel(chest*band(u,.31,.30,.11),y,arch,.011,.010)
        ridge=3.43+.17*np.clip((u-.20)/.40,0,1)**1.5
        bevel(torso*front*band(u,.39,.25,.11),y,ridge,.010,.011)
        # Mechanical undercut at shoulder socket.
        paint((28,39,49),torso*front*band(u,.54,.035,.025)*band(y,3.61,.20,.12)*.85)
        paint((31,226,229),torso*front*band(u,.53,.010,.013)*band(y,3.58,.105,.07)*.84)
        # Symmetric micro-fasteners; placed in 3D, not in UV island coordinates.
        for sy in (3.64,3.45):
            paint((52,66,76),torso*front*band(u,.34,.012,.012)*band(y,sy,.012,.012)*.86)
            paint((213,232,237),torso*front*band(u,.34,.004,.006)*band(y,sy,.004,.006)*.83)
    # Central recessed energy core with glass rim and segmented emitter.
    core=torso*front*band(y,3.51,.23,.06)
    paint((18,30,41),core*band(x,0,.118,.033)*.93)
    paint((96,126,140),core*band(x,0,.086,.018)*.88)
    paint((25,43,53),core*band(x,0,.062,.017)*.95)
    paint((23,229,232),core*band(x,0,.027,.014)*band(y,3.52,.15,.038)*.97)
    paint((191,253,250),core*band(x,0,.008,.006)*band(y,3.52,.13,.034)*.86)
    # Abdominal ribs: inset carbon underlay, ceramic bevel and small indicators.
    for sy in (3.15,3.055,2.96,2.865):
        rib=torso*front*band(x,0,.24,.06)
        bevel(rib,y,sy,.013,.010)
        paint((24,184,199),rib*band(x,0,.012,.008)*band(y,sy,.008,.007)*.74)
    # Pelvis: converging V armor, side actuator accents.
    v=2.50-.22*np.clip(xa/.53,0,1)
    bevel(torso*front*band(xa,.29,.24,.10),y,v,.012,.014)
    paint((24,41,52),torso*front*band(x,0,.085,.04)*band(y,2.40,.11,.07)*.85)
    paint((28,223,225),torso*front*band(x,0,.016,.012)*band(y,2.41,.065,.028)*.85)
    # Back: scapula plate borders and detailed power-spine structure.
    paint((24,37,47),torso*back*band(x,0,.115,.04)*band(y,3.14,.57,.18)*.94)
    paint((128,154,166),torso*back*band(x,0,.079,.022)*band(y,3.14,.51,.16)*.72)
    for sy in (2.82,2.98,3.14,3.30,3.46,3.62):
        paint((25,220,227),torso*back*band(x,0,.023,.015)*band(y,sy,.023,.015)*.94)
        paint((226,252,250),torso*back*band(x,0,.008,.008)*band(y,sy,.010,.009)*.70)
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        scap=3.78-.46*np.clip(u/.60,0,1)**1.5
        bevel(torso*back*band(u,.35,.29,.13),y,scap,.012,.013)
        for sy in (3.38,3.25,3.12):
            bevel(torso*back*band(u,.28,.13,.08),y,sy,.009,.009)
        paint((32,203,215),torso*back*band(u,.50,.015,.012)*band(y,3.43,.16,.09)*.77)
    # Arms: joint gasket rings and segmented long-armor shells.
    for ax in (.77,1.01,1.47,1.88,2.20,2.43):
        bevel(arm,xa,ax,.015,.011)
    for ax in (1.20,1.72,2.26):
        paint((35,50,61),arm*front*band(xa,ax,.23,.08)*band(y,3.75,.039,.022)*.80)
        paint((29,232,231),arm*front*band(xa,ax,.19,.06)*band(y,3.76,.012,.010)*.94)
        paint((235,247,248),arm*front*band(xa,ax,.18,.05)*band(y,3.79,.005,.008)*.63)
    # Leg: thigh shields, carbon knee assemblies, long illuminated shins.
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        edge=1.86-.39*np.clip((u-.19)/.36,0,1)
        bevel(leg*front*band(u,.38,.20,.12),y,edge,.013,.012)
    for h in (2.15,1.20,1.00,.30):
        bevel(leg,y,h,.019,.014)
    paint((29,43,54),leg*front*band(y,1.08,.10,.035)*band(xa,.38,.11,.07)*.91)
    paint((183,206,214),leg*front*band(y,1.08,.062,.026)*band(xa,.38,.074,.048)*.83)
    paint((31,53,65),leg*front*band(xa,.36,.082,.039)*band(y,.66,.32,.14)*.87)
    paint((112,147,158),leg*front*band(xa,.36,.051,.027)*band(y,.66,.28,.11)*.86)
    paint((20,227,231),leg*front*band(xa,.36,.018,.012)*band(y,.66,.245,.09)*.98)
    paint((210,255,250),leg*front*band(xa,.36,.005,.006)*band(y,.66,.21,.08)*.68)
    # Light industrial machining speckle only within dark hardware.
    grain=np.sin(73*x+17*z)*np.cos(69*y-13*z)
    paint((111,129,139),(torso+arm+leg)*side*smooth(.75,.96,grain)*.07)
    return np.clip(np.rint(rgb),0,255).astype(np.uint8),tags

base.surface_skin=surface_skin
if __name__=="__main__":
    base.main()
    report=json.loads(base.REPORT.read_text("utf8"))
    report["version"]="v11.549"
    report["designMethod"]="concept art interpreted as 3D-anchored hard-surface design; not pixel transfer"
    report["assets"]={
        "4kMaterial":str(base.FOUR.relative_to(base.ROOT)),
        "2kMaterial":str(base.TWO.relative_to(base.ROOT)),
        "nativeMaterial":str(base.NATIVE.relative_to(base.ROOT)),
        "renderProof":str(base.VIEW.relative_to(base.ROOT)),
        "validation":str(base.REPORT.relative_to(base.ROOT))
    }
    base.REPORT.write_text(json.dumps(report,indent=2)+"\n","utf8")
