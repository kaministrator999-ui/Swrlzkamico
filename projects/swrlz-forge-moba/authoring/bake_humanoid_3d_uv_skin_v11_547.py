#!/usr/bin/env python3
"""§E 11.547: TRUE world-surface robotic paint baked to the exact v11.546 UVs.

Unlike a guessed PNG atlas, every texel is evaluated on the mannequin's 3D
triangles using barycentric position and welded surface normal. The UV mapping,
mesh, indices, and historic saved projects remain untouched.

Deliverables: 4096px and 2048px importable RGB material, 1024px compressed
native-size material, front/back/side model render, and a JSON proof.
No cyan UV triangles, text, checker, or painted island outline in material PNG.
"""
import base64,hashlib,json,sys
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'authoring'))
import build_humanoid_semantic_material_v11_544 as baker
import build_humanoid_anatomy_robot_v11_546 as anatomy

SOURCE=ROOT/'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'
DEST=ROOT/'assets/models'
QA=ROOT/'docs/qa'
NAME='futuristic-humanoid-v11-547-3d-surface-skin'
FOUR=DEST/(NAME+'-4096.png')
TWO=DEST/(NAME+'-2048.png')
NATIVE=DEST/(NAME+'-1024.png')
VIEW=QA/(NAME+'-front-back-side.png')
REPORT=QA/(NAME+'-validation.json')
MAX_ASSET_BYTES=10_000_000
MAX_NATIVE_CHARS=360000

def surface_skin(points,normals):
    """Color is a continuous function of the 3D surface, NEVER of UV 2D shape."""
    x,y,z=points.T
    nx,ny,nz=normals.T
    xa=np.abs(x)
    s=baker.smooth
    band=baker.band
    tags=baker.labels(points)
    head=(tags==0).astype(float)
    arm=(tags==1).astype(float)
    torso=(tags==2).astype(float)
    leg=(tags==3).astype(float)
    front=s(.08,.40,nz)
    back=s(.08,.40,-nz)
    side=s(.28,.77,np.abs(nx))

    # Clean pearl ceramic-metal undercoat with soft 3D-space grain only.
    grain=2.8*np.sin(6.3*x+4.1*z)+1.6*np.cos(8.9*y-3.2*x)
    rgb=np.stack([225+grain,233+grain,237+grain],axis=1)
    def paint(color,weight):
        baker.blend(rgb,color,weight)

    # Faceless sensor helmet: dark lateral shell and ONE narrow front visor.
    paint((91,105,118),head*side*band(y,4.46,.14,.10)*.53)
    paint((42,55,69),head*front*band(y,4.47,.043,.021)*band(x,0,.155,.056)*.90)
    paint((30,216,223),head*front*band(y,4.478,.007,.009)*band(x,0,.112,.031)*.96)
    paint((63,78,89),head*back*band(x,0,.055,.045)*band(y,4.49,.20,.12)*.66)
    paint((55,70,81),head*band(y,4.095,.029,.024)*.84)
    paint((31,193,204),head*back*band(x,0,.012,.017)*band(y,4.48,.035,.028)*.65)

    # Torso outer chassis only at anatomical flank, not random UV rectangle.
    flank=torso*side*band(xa,.46,.095,.075)*band(y,3.13,.53,.22)
    paint((66,80,93),flank*.69)
    # Angled collar-to-sternum mechanical plate seams in world coordinates.
    yoke=3.77-.34*np.clip(xa/.56,0,1)
    paint((75,89,99),torso*front*band(y,yoke,.009,.015)*
          (1-s(.55,.69,xa))*band(y,3.52,.40,.31)*.72)
    paint((246,247,242),torso*front*band(xa,.24,.19,.11)*
          band(y,3.47,.26,.17)*.40)
    # Narrow central sternum structure / self-contained cyan power light.
    paint((47,62,75),torso*front*band(x,0,.077,.045)*band(y,3.52,.20,.12)*.78)
    paint((30,211,221),torso*front*band(x,0,.023,.019)*band(y,3.55,.033,.025)*.95)
    # Three short abdominal rib slots, not a painted circle around the waist.
    for rib in (3.11,3.015,2.92):
        paint((76,91,103),torso*front*band(y,rib,.013,.014)*
              band(x,0,.15,.065)*.79)
    # Waist is smooth ceramic with small side mechanical gussets.
    paint((75,92,103),torso*side*band(y,2.56,.035,.034)*.58)

    # Back chassis: a single spine rail and discreet cyan illumination.
    paint((52,65,79),torso*back*band(x,0,.075,.048)*
          band(y,3.10,.54,.19)*.88)
    for sy in (2.82,3.03,3.24,3.45,3.62):
        paint((39,207,219),torso*back*band(x,0,.022,.020)*
              band(y,sy,.015,.015)*.92)
    paint((80,96,107),torso*back*band(y,3.67,.017,.022)*
          band(x,0,.40,.15)*.78)
    # Subtle armor split lines off the spine, connected across UV seams.
    for sy in (3.05,3.43):
        diagonal=sy-.11*np.clip(xa/.53,0,1)
        paint((87,103,115),torso*back*band(y,diagonal,.010,.016)*
              band(xa,.24,.21,.14)*.48)

    # Bilateral arms: geometric joint bands and shaped ceramic forearms.
    for ax,width in ((.84,.045),(1.45,.055),(2.06,.040),(2.40,.023)):
        paint((56,68,81),arm*band(xa,ax,width,.027)*.89)
    paint((246,248,244),arm*band(xa,1.78,.27,.16)*.33)
    paint((80,98,108),arm*side*band(xa,1.11,.23,.14)*.42)
    paint((42,203,214),arm*front*band(y,3.66,.008,.012)*
          s(1.55,1.68,xa)*(1-s(1.96,2.06,xa))*.84)
    paint((77,91,101),arm*band(y,3.69,.023,.016)*
          band(xa,1.68,.22,.09)*.31)

    # Legs: separate hip, knee, ankle articulation; no giant circular markings.
    for joint,width in ((2.18,.058),(1.04,.070),(.30,.040)):
        paint((61,74,88),leg*band(y,joint,width,.032)*.83)
    paint((243,246,245),leg*front*band(y,1.66,.33,.20)*.41)
    # Kneecap inset follows each thigh's REAL 3D orientation, not 2D ellipses.
    paint((63,79,92),leg*front*band(y,1.075,.058,.052)*
          band(xa,.39,.085,.055)*.69)
    paint((225,231,236),leg*front*band(y,1.06,.038,.045)*
          band(xa,.39,.060,.050)*.68)
    # Long shin metal inset + restrained vertical cyan channel.
    paint((84,100,110),leg*front*band(xa,.37,.060,.055)*
          band(y,.68,.26,.12)*.73)
    paint((34,207,217),leg*front*band(xa,.37,.012,.015)*
          band(y,.68,.19,.13)*.90)
    paint((84,97,109),leg*back*band(y,1.52,.25,.13)*
          band(xa,.36,.08,.07)*.41)
    paint((245,248,247),leg*(1-s(.12,.27,y))*.44)
    paint((63,83,94),leg*band(y,.15,.011,.014)*.43)

    # Thin manufactured panel engraving, low-contrast and 3D continuous.
    fine=np.minimum(np.abs(np.sin(17*x+6*z)),np.abs(np.sin(22*y-4*z)))
    paint((146,158,169),(torso+arm+leg)*s(.020,.005,fine)*.11)
    return np.clip(np.rint(rgb),0,255).astype(np.uint8),tags

def decode_scene():
    obj=json.loads(SOURCE.read_text('utf8'))
    part=obj['project']['modelAtelier']['parts'][0]
    mesh=part['topologyMesh']
    pos=np.asarray(mesh['positions'],dtype=np.float64).reshape(-1,3)
    uv=np.asarray(mesh['uvs'],dtype=np.float64).reshape(-1,2)
    faces=np.asarray(mesh['indices'],dtype=np.int64).reshape(-1,3)
    assert obj['version']==11.546
    assert obj['project']['canonicalId']=='robotic-humanoid-mannequin'
    assert part['id']=='humanoid-body-unified'
    assert len(pos)==8902 and len(faces)==13932
    assert uv.shape==(len(pos),2) and np.isfinite(pos).all()
    assert ((uv>=0)&(uv<=1)).all()
    return obj,pos,uv,faces,anatomy.normals(pos,faces)

def save_image(image,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    buf=BytesIO()
    image.save(buf,'PNG',optimize=True)
    if len(buf.getvalue())>MAX_ASSET_BYTES:
        # Preserve actual 4096 pixels while using an indexed color palette
        # to keep static hosting under its 10 MB per-file limit.
        image=image.quantize(colors=224,method=Image.Quantize.FASTOCTREE,
                             dither=Image.Dither.NONE)
        buf=BytesIO();image.save(buf,'PNG',optimize=True)
    data=buf.getvalue()
    assert len(data)<MAX_ASSET_BYTES,(path,len(data))
    path.write_bytes(data)
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

def qa_render(texture,pos,uv,faces):
    proof=Image.new('RGB',(1560,606),(19,26,41))
    pen=ImageDraw.Draw(proof)
    for i,(name,ax,back) in enumerate((('FRONT +Z','front',False),
                                        ('BACK -Z','front',True),
                                        ('SIDE','side',False))):
        img=baker.render_view(texture,pos,uv,faces,ax,back)
        proof.paste(img,(i*520,36))
        pen.text((i*520+10,12),name,fill=(230,241,248))
    save_image(proof,VIEW)

def main():
    scene,pos,uv,faces,norm=decode_scene()
    old_scene_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    old_material=scene['project']['modelAtelier']['parts'][0]['uvPaintPNG']
    # Explicit no-mutation: only produce texture and QA files, no mesh changes.
    baker.surface_paint=surface_skin
    baker.SIZE=4096
    texture,tags,metrics=baker.bake(pos,uv,faces,norm)
    data4=save_image(Image.fromarray(texture,'RGB'),FOUR)
    img=Image.fromarray(texture,'RGB')
    down2=img.resize((2048,2048),Image.Resampling.LANCZOS)
    data2=save_image(down2,TWO)
    down1=img.resize((1024,1024),Image.Resampling.LANCZOS)
    # Native 1024px follows the existing 360k embedded chars cap.
    native_buf=BytesIO();down1.save(native_buf,'PNG',optimize=True)
    if len(base64.b64encode(native_buf.getvalue()))+22>MAX_NATIVE_CHARS:
        down1=down1.quantize(colors=96,method=Image.Quantize.FASTOCTREE,
                            dither=Image.Dither.NONE)
        native_buf=BytesIO();down1.save(native_buf,'PNG',optimize=True)
    data=native_buf.getvalue()
    assert len(base64.b64encode(data))+22<=MAX_NATIVE_CHARS,('native paint too big',len(data))
    NATIVE.write_bytes(data)
    data1={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    qa_render(np.asarray(Image.open(NATIVE).convert('RGB')),pos,uv,faces)
    probe_pos=np.array([
       [0.,4.47,.25],[0.,3.47,.30],[0.,3.47,-.30],
       [1.75,3.66,.14],[-1.75,3.66,.14],
       [.37,.68,.18],[-.37,.68,.18]],dtype=np.float64)
    probe_norm=np.array([[0,0,1],[0,0,1],[0,0,-1],
                         [0,0,1],[0,0,1],[0,0,1],[0,0,1]],dtype=np.float64)
    probe_colors,probe_tags=surface_skin(probe_pos,probe_norm)
    assert list(map(int,probe_tags))==[0,2,2,1,1,3,3]
    assert (abs(probe_colors[3].astype(int)-probe_colors[4].astype(int))<10).all()
    assert (abs(probe_colors[5].astype(int)-probe_colors[6].astype(int))<10).all()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==old_scene_hash
    assert scene['project']['modelAtelier']['parts'][0]['uvPaintPNG']==old_material
    report={'version':'v11.547','sourceSceneVersion':'v11.546',
            'sourceSceneSha256':old_scene_hash,'triangles':len(faces),
            'uvVertices':len(pos),'uvCoordinatesModified':False,
            'geometryModified':False,'oldMaterialOverwritten':False,
            'mapping':'barycentric 3D position + welded surface normal -> exact native UV triangle',
            '4kMaterial':{'size':[4096,4096],**data4},
            '2kMaterial':{'size':[2048,2048],**data2},
            'nativeMaterial':{'size':[1024,1024],**data1},
            'triangulationPaintedIntoTexture':False,
            'renderProof':VIEW.name,'regionTags':list(map(int,probe_tags)),**metrics}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('SE547_TRUE_3D_SURFACE_SKIN_OK',json.dumps(report),flush=True)

if __name__=='__main__':
    main()
