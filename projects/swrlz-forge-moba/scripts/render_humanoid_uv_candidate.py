"""Create exact, matched diagnostic atlas and native starter candidate from new UVs."""
import base64,json,sys
from pathlib import Path
from PIL import Image, ImageDraw
source, out = Path(sys.argv[1]), Path(sys.argv[2])
before=json.loads(source.read_text())
after=json.loads((out/'candidate.untextured.json').read_text())
b=before['project']['modelAtelier']['parts'][0]
a=after['project']['modelAtelier']['parts'][0]
bm,am=b['topologyMesh'],a['topologyMesh']
assert bm['positions']==am['positions'] and bm['indices']==am['indices']
assert len(bm['uvs'])==len(am['uvs'])
def guide(mesh,dest):
    im=Image.new('RGB',(2048,2048),(17,25,35))
    draw=ImageDraw.Draw(im)
    p,u,ix=mesh['positions'],mesh['uvs'],mesh['indices']
    for k in range(0,len(ix),3):
        ids=ix[k:k+3]
        x,y,z=[sum(p[i*3+j] for i in ids)/3 for j in range(3)]
        color=(238,89,105) if y>4.12 else ((167,110,229) if x<0 else (241,125,69)) if y<2.39 else ((56,190,107) if x<0 else (232,187,69)) if abs(x)>.52 and 3.3<y<4.0 else (64,145,240)
        pts=[(round(u[2*i]*2047),round((1-u[2*i+1])*2047)) for i in ids]
        draw.polygon(pts,fill=tuple(int(t*.48) for t in color))
        draw.line(pts+[pts[0]],fill=color,width=1)
    im.save(dest,optimize=True)
guide(bm,out/'baseline-uv.png')
guide(am,out/'candidate-uv.png')
# Full-atlas checker includes texture bleed into gutters. This is a diagnostic
# texture only: existing artistic textures must be rebaked, never relabeled.
tex=Image.new('RGB',(1024,1024))
d=ImageDraw.Draw(tex)
for y in range(64):
    for x in range(64):
        d.rectangle((x*16,y*16,x*16+15,y*16+15),fill=(164,188,198) if (x+y)%2 else (102,125,140))
tex.save(out/'candidate-checker.png',optimize=True)
a['uvPaintPNG']='data:image/png;base64,'+base64.b64encode((out/'candidate-checker.png').read_bytes()).decode()
(out/'candidate.swyrl.json').write_text(json.dumps(after,separators=(',',':'),ensure_ascii=False))
print('SWRLZ_UV_CANDIDATE_NATIVE_SCENE_READY')
