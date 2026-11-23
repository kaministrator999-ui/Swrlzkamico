#!/usr/bin/env python3
"""v11.548: detailed 3D-continuous mannequin finish on unchanged v11.546 UV."""
import numpy as np
import bake_humanoid_3d_uv_skin_v11_547 as base
from PIL import Image
base.NAME='futuristic-humanoid-v11-548-finished-robot-skin'
base.FOUR=base.DEST/(base.NAME+'-4096.png')
base.TWO=base.DEST/(base.NAME+'-2048.png')
base.NATIVE=base.DEST/(base.NAME+'-1024.png')
base.VIEW=base.QA/(base.NAME+'-front-back-side.png')
base.REPORT=base.QA/(base.NAME+'-validation.json')
original=base.surface_skin
def surface_skin(points,normals):
    rgb,tags=original(points,normals)
    x,y,z=points.T
    xa=np.abs(x)
    nz=normals[:,2]
    nx=normals[:,0]
    smooth=base.baker.smooth
    band=base.baker.band
    front=smooth(.04,.43,nz)
    back=smooth(.04,.43,-nz)
    side=smooth(.30,.75,np.abs(nx))
    head=(tags==0).astype(float)
    torso=(tags==2).astype(float)
    arm=(tags==1).astype(float)
    leg=(tags==3).astype(float)
    rgb=rgb.astype(float)
    def paint(color,w):
        base.baker.blend(rgb,color,np.clip(w,0,1))
    # Pearl alloy segmented by layered graphite seams following anatomy.
    # Chest shield: paired asymmetric sweep lines with narrow inset metallic rim.
    chest=torso*front*band(y,3.54,.32,.17)
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        shield=3.78-.55*np.clip(u/.59,0,1)**1.65
        paint((37,53,65),chest*band(y,shield,.014,.012)*band(u,.32,.31,.10)*.86)
        paint((127,155,167),chest*band(y,shield-.026,.008,.012)*band(u,.32,.30,.10)*.72)
        # side armor sockets with curved double line
        curve=3.38+.25*np.clip((u-.31)/.32,0,1)**2
        paint((43,58,72),torso*front*band(y,curve,.019,.016)*band(u,.43,.16,.10)*.85)
        paint((31,186,200),torso*front*band(y,curve+.032,.005,.010)*band(u,.44,.13,.10)*.64)
    # Sternum module: charcoal mount, pearl inset and cyan light.
    paint((40,55,70),torso*front*band(x,0,.115,.035)*band(y,3.48,.23,.06)*.88)
    paint((170,196,204),torso*front*band(x,0,.074,.022)*band(y,3.48,.19,.04)*.84)
    paint((34,215,226),torso*front*band(x,0,.018,.010)*band(y,3.49,.095,.03)*.95)
    # Abdominal plated segments: separate floating ribs and narrow joints.
    for sy in (3.13,3.01,2.89):
        width=.23-(3.13-sy)*.18
        paint((48,64,77),torso*front*band(y,sy,.012,.010)*band(x,0,width,.04)*.87)
        paint((174,194,203),torso*front*band(y,sy+.027,.006,.010)*band(x,0,width-.035,.04)*.54)
    # Pelvis V-shaped shield with dark edge and brushed center.
    hipline=2.48-.17*np.clip(xa/.48,0,1)
    paint((47,62,76),torso*front*band(y,hipline,.015,.016)*band(xa,.26,.24,.10)*.85)
    paint((157,182,191),torso*front*band(y,hipline+.030,.009,.012)*band(xa,.25,.22,.10)*.65)
    # Rear scapula wings, center spine and flanking vents.
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        sweep=3.74-.42*np.clip(u/.56,0,1)
        paint((47,62,76),torso*back*band(y,sweep,.014,.017)*band(u,.31,.26,.11)*.85)
        paint((162,187,196),torso*back*band(y,sweep+.035,.009,.011)*band(u,.31,.25,.10)*.62)
        for sy in (3.33,3.20,3.07):
            paint((40,54,68),torso*back*band(y,sy,.018,.013)*band(u,.25,.11,.06)*.72)
    # Deliberate mechanical segmentation on each shoulder and arm.
    for a in (.74,1.04,1.49,1.83,2.19):
        paint((41,54,68),arm*band(xa,a,.014,.015)*.83)
        paint((147,171,181),arm*band(xa,a+.030,.008,.012)*.59)
    for a in (1.14,1.74):
        paint((48,65,77),arm*front*band(xa,a,.24,.10)*band(y,3.75,.038,.021)*.69)
        paint((31,208,220),arm*front*band(xa,a,.17,.08)*band(y,3.76,.007,.010)*.91)
    # Hand plating is deliberately subtle to avoid tiny UV island noise.
    paint((79,97,109),arm*band(xa,2.45,.040,.024)*.66)
    # Leg thigh armor: V seams and narrow beveled edges.
    for sign in (-1,1):
        u=np.maximum(0,sign*x)
        seam=1.84-.35*np.clip((u-.22)/.35,0,1)
        paint((49,65,78),leg*front*band(y,seam,.015,.014)*band(u,.40,.19,.10)*.77)
        paint((150,178,188),leg*front*band(y,seam+.027,.008,.012)*band(u,.40,.19,.10)*.59)
    # Knee caps with upper and lower socket, clear separation.
    for ky in (1.18,.94):
        paint((47,62,77),leg*front*band(y,ky,.021,.016)*band(xa,.39,.14,.07)*.83)
    paint((177,201,210),leg*front*band(y,1.06,.055,.027)*band(xa,.39,.080,.042)*.65)
    # Shin armor tapered engraving and paired light channels.
    paint((45,62,77),leg*front*band(xa,.34,.072,.045)*band(y,.62,.30,.13)*.70)
    paint((177,200,210),leg*front*band(xa,.34,.047,.033)*band(y,.62,.27,.12)*.78)
    paint((30,216,224),leg*front*band(xa,.34,.009,.011)*band(y,.62,.20,.10)*.94)
    # Back-of-leg actuator stripes.
    paint((55,73,85),leg*back*band(xa,.38,.044,.034)*band(y,.65,.28,.14)*.65)
    # Head stays featureless, except a deliberate visor and shell segmentation.
    paint((48,65,79),head*front*band(y,4.49,.040,.022)*band(x,0,.17,.045)*.86)
    paint((34,222,229),head*front*band(y,4.50,.007,.008)*band(x,0,.135,.036)*.97)
    paint((54,70,84),head*side*band(y,4.50,.15,.07)*.56)
    # Avoid photographic facial features, UV grid lines or arbitrary stickers.
    return np.clip(np.rint(rgb),0,255).astype(np.uint8),tags
base.surface_skin=surface_skin
if __name__=='__main__':
    base.main()
    # Single source of truth: authoring emits paths for verification and publishing.
    import json
    report=json.loads(base.REPORT.read_text('utf8'))
    report['assets']={
        '4kMaterial':str(base.FOUR.relative_to(base.ROOT)),
        '2kMaterial':str(base.TWO.relative_to(base.ROOT)),
        'nativeMaterial':str(base.NATIVE.relative_to(base.ROOT)),
        'renderProof':str(base.VIEW.relative_to(base.ROOT)),
        'validation':str(base.REPORT.relative_to(base.ROOT)),
    }
    base.REPORT.write_text(json.dumps(report,indent=2)+'\n','utf8')
