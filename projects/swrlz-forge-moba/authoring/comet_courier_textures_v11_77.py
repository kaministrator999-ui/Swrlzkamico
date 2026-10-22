"""Author original 4096px painted material atlases (no source image upscaling)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
root=Path(__file__).resolve().parents[1]/'assets/models/comet-courier';root.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1177);W,H=1024,2048
palette=[(29,57,85),(231,235,218),(21,112,124),(93,48,39),(191,139,56),(97,222,231),(31,49,95),(238,166,46)]
atlas=Image.new('RGB',(4096,4096));heights=Image.new('L',(4096,4096))
for k,base in enumerate(palette):
 y,x=np.mgrid[0:H,0:W];noise=rng.normal(0,1.2,(H,W));grain=np.sin(x*.63+y*.13)*.7
 if k in [0,1,5]:
  shade=8*np.sin(y/H*np.pi)+3*np.sin(x/117+y/325)+noise+grain
 elif k==2:shade=2.1*np.sin(x*np.pi/3)+2.4*np.sin(y*np.pi/4)+noise
 elif k==3:shade=3*np.sin(x/23)*np.sin(y/29)+rng.normal(0,3,(H,W))
 elif k==4:shade=8*np.sin(x/160)+rng.normal(0,1.5,(H,W))
 else:shade=5*np.sin(y/170)+noise
 a=np.clip(np.array(base)[None,None,:]+shade[:,:,None],0,255).astype('uint8');tile=Image.fromarray(a);height=Image.fromarray(np.clip(128+shade*2,0,255).astype('uint8'));d=ImageDraw.Draw(tile);hd=ImageDraw.Draw(height)
 if k in [0,1,5]:
  for _ in range(12500):
   xx=int(rng.integers(-18,W+18));yy=int(rng.integers(-90,H));length=int(rng.integers(20,95));sway=int(10*np.sin(xx/180+yy/500));tone=int(rng.integers(-15,18));col=tuple(max(0,min(255,c+tone)) for c in base)
   pts=[(xx,yy),(xx+sway//2,yy+length//2),(xx+sway,yy+length)];d.line(pts,fill=col,width=int(rng.integers(1,3)));hd.line(pts,fill=128+tone*3,width=2)
 if k==2:
  for yy in range(40,H,256):
   for xx in range(0,W,128):
    d.line([(xx,yy),(xx+32,yy+40),(xx,yy+80),(xx-32,yy+40),(xx,yy)],fill=(114,174,157),width=2);hd.line([(xx,yy),(xx+32,yy+40),(xx,yy+80)],fill=166,width=2)
  for yy in [18,H-20]:d.line((10,yy,W-10,yy),fill=(204,170,83),width=4)
 if k==3:
  for xx in [18,W-20]:
   d.line((xx,10,xx,H-10),fill=(47,28,27),width=5)
   for yy in range(14,H-14,20):d.line((xx+8,yy,xx+8,yy+8),fill=(200,152,91),width=3);hd.line((xx+8,yy,xx+8,yy+8),fill=180,width=3)
  for _ in range(550):
   xx=int(rng.integers(W));yy=int(rng.integers(H));d.line((xx,yy,xx+int(rng.integers(3,18)),yy-2),fill=(113,68,47),width=1)
 if k in [4,6]:
  for yy in range(128,H,256):
   for xx in range(128,W,256):
    col=(240,206,128) if k==4 else (110,160,176);d.line([(xx,yy-22),(xx+10,yy),(xx,yy+22),(xx-10,yy),(xx,yy-22)],fill=col,width=2)
 if k==5:
  for yy in range(120,H,340):
   d.line([(80,yy),(280,yy+100),(520,yy+50),(800,yy+220)],fill=(186,251,239),width=3)
   for xx,dy in [(80,0),(280,100),(520,50),(800,220)]:d.ellipse((xx-5,yy+dy-5,xx+5,yy+dy+5),fill=(246,255,230))
 if k==7:
  # Radial amber fibers; oval eye geometry supplies the final shape.
  for a0 in np.linspace(0,np.pi*2,900):
   rr=rng.uniform(.65,.98);pts=[(W/2+np.cos(a0)*W*.22,H/2+np.sin(a0)*H*.22),(W/2+np.cos(a0)*W*.49*rr,H/2+np.sin(a0)*H*.49*rr)];d.line(pts,fill=(int(rng.integers(130,230)),int(rng.integers(75,150)),27),width=1)
 atlas.paste(tile,((k%4)*W,(k//4)*H));heights.paste(height,((k%4)*W,(k//4)*H))
# Build a genuine tangent-space normal map from the authored 4K relief.
h=np.asarray(heights.filter(ImageFilter.GaussianBlur(.8)),dtype=np.float32)/255;dy,dx=np.gradient(h);v=np.dstack((-dx*1.8,dy*1.8,np.ones_like(h)));v/=np.linalg.norm(v,axis=2)[:,:,None];normal=Image.fromarray(np.clip((v*.5+.5)*255,0,255).astype('uint8'))
atlas.save(root/'astra-basecolor-4k.jpg',quality=94,subsampling=0,optimize=True);normal.quantize(colors=128,method=Image.Quantize.FASTOCTREE).save(root/'astra-normal-4k.png',optimize=True)
for p in root.iterdir():
 with Image.open(p) as im:print(p.name,im.size,p.stat().st_size)
