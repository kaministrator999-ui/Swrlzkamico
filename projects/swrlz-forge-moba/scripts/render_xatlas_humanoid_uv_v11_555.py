#!/usr/bin/env python3
"""Paint the *actual* xatlas UV coverage, preserving a wire-free material PNG."""
import base64,json,math
from collections import defaultdict
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
SCENE=R/'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
REPORT=R/'docs/qa/clean-topology-humanoid-v11-554.json'
PAINT=R/'assets/models/clean-topology-humanoid-v11-554-uv-test.png'
GUIDE=R/'assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png'
BG=(17,25,35)
COL={'head':(238,89,105),'torso':(64,145,240),
     'leftArm':(56,190,107),'rightArm':(232,187,69),
     'leftLeg':(167,110,229),'rightLeg':(241,125,69)}
def main():
    doc=json.loads(SCENE.read_text('utf8'))
    report=json.loads(REPORT.read_text('utf8'))
    part=doc['project']['modelAtelier']['parts'][0]
    mesh=part['topologyMesh'];p=mesh['positions'];uv=mesh['uvs'];ix=mesh['indices']
    assert report['uvAlgorithm']=='seamed-LSCM+verified-single-atlas-packer'
    assert len(ix)//3==report['triangles'] and len(p)//3==report['vertices']
    palette=Image.new('RGB',(1024,1024),BG)
    draw=ImageDraw.Draw(palette)
    for row in range(64):
        for col in range(64):
            n=(row+col)&1
            draw.rectangle((col*16,row*16,col*16+15,row*16+15),
                           fill=(164,188,198) if n else (102,125,140))
    mask=Image.new('L',(1024,1024),0)
    md=ImageDraw.Draw(mask)
    guide=Image.new('RGB',(2048,2048),BG)
    gd=ImageDraw.Draw(guide)
    label_uv=defaultdict(list)
    flipped=0;degenerate=0
    for i in range(0,len(ix),3):
        ids=ix[i:i+3]
        xyz=[p[3*j:3*j+3] for j in ids]
        mean=[sum(v[n] for v in xyz)/3 for n in range(3)]
        x,y,z=mean
        if y>4.12: name='head'
        elif y<2.39:name='leftLeg' if x<0 else 'rightLeg'
        elif abs(x)>.52 and 3.3<y<4.0:name='leftArm' if x<0 else 'rightArm'
        else:name='torso'
        pairs=[(uv[2*j],uv[2*j+1]) for j in ids]
        area=(pairs[1][0]-pairs[0][0])*(pairs[2][1]-pairs[0][1])-(pairs[2][0]-pairs[0][0])*(pairs[1][1]-pairs[0][1])
        if abs(area)<1.e-11:degenerate+=1
        if area<0:flipped+=1
        pts=[(round(u*1023),round((1-v)*1023)) for u,v in pairs]
        md.polygon(pts,fill=255)
        outline=[(round(u*2047),round((1-v)*2047)) for u,v in pairs]
        gd.line(outline+[outline[0]],fill=tuple(int(t*.52) for t in COL[name]),width=1)
        label_uv[name].append((sum(v[0] for v in pairs)/3,sum(v[1] for v in pairs)/3))
    final=Image.new('RGB',(1024,1024),BG)
    final.paste(palette,(0,0),mask)
    # No text and no UV wireframe are ever baked into the importable texture.
    PAINT.parent.mkdir(parents=True,exist_ok=True)
    final.save(PAINT,optimize=True)
    font=ImageFont.load_default()
    for name,points in label_uv.items():
        if len(points)<25:continue
        u=sorted(v[0] for v in points)[len(points)//2]
        v=sorted(v[1] for v in points)[len(points)//2]
        text=name.replace('Arm',' ARM').replace('Leg',' LEG').upper()
        gd.text((int(u*2047),int((1-v)*2047)),text,font=font,
                anchor='mm',fill='white',stroke_width=2,stroke_fill=BG)
    GUIDE.parent.mkdir(parents=True,exist_ok=True)
    guide.save(GUIDE,optimize=True)
    part['uvPaintPNG']='data:image/png;base64,'+base64.b64encode(PAINT.read_bytes()).decode('ascii')
    SCENE.write_text(json.dumps(doc,separators=(',',':'),ensure_ascii=False),'utf8')
    report['uvPaintMode']='xatlas-geometry-mask-true-checker'
    report['guideAnatomyLabels']=True
    report['uvDegenerateTriangles']=degenerate
    report['uvWindingNegativeTriangles']=flipped
    # xatlas may choose mirrored chart orientations; mirror count is
    # diagnostic, not an assertion that the mesh face winding changed.
    REPORT.write_text(json.dumps(report,indent=2)+'\n','utf8')
    assert degenerate<=15,('Degenerate UV triangles',degenerate)
    print('SE555_REAL_UV_PAINT_GUIDE_PASS',
          json.dumps({'tris':len(ix)//3,'degenerate':degenerate,
                      'texturePixels':1024,'guidePixels':2048,'labels':list(label_uv)}),
          flush=True)
if __name__=='__main__':main()
