"""Deterministic 4096px wool/fur atlas and its matching tangent normal map."""
from pathlib import Path
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1]/'assets/models/wildwood-animals';r.mkdir(parents=True,exist_ok=True)
w,h=1024,2048;y,x=np.mgrid[0:h,0:w].astype(np.float32);rng=np.random.default_rng(1187)
colors=[];heights=[]
for tile in range(8):
 noise=rng.normal(0,1,(h,w)).astype(np.float32)
 if tile==0:
  fiber=np.sin(x*.46+4*np.sin(y*.013)+2*np.sin(x*.033+y*.018));fine=np.sin(x*1.2+y*.10+np.sin(y*.031)*3);value=.055*fiber+.021*fine+.014*noise;base=np.array([151,147,133]);height=.19*fiber+.07*fine+.04*noise
 elif tile==1:
  # Curl loops twist around staggered centers, with fine interlocking fibers.
  gx=(x+18*np.sin(y*.018))/48;gy=y/43;lx=(gx-np.floor(gx)-.5)*2;ly=(gy-np.floor(gy)-.5)*2;rad=np.sqrt(lx*lx+ly*ly);angle=np.arctan2(ly,lx);curl=np.cos(rad*11+angle*1.6+2*np.sin(gx*.3));value=.028*curl+.009*noise;base=np.array([232,222,201]);height=.20*curl+.035*noise
 elif tile==3:
  value=.018*np.sin(x*.2)*np.sin(y*.17)+.025*noise;base=np.array([164,150,139]);height=.14*noise
 elif tile==7:
  cx=x-w/2;cy=y-h/2;a=np.arctan2(cy,cx);rad=np.sqrt((cx/w)**2+(cy/h)**2);value=.09*np.sin(a*90+rad*40)+.025*noise;base=np.array([218,171,81]);height=.06*np.sin(a*90+rad*40)
 else:
  value=.025*np.sin(x*.5)*np.sin(y*.43)+.012*noise;base=np.array([[151,147,133],[232,222,201],[107,126,119],[164,150,139],[182,158,102],[122,153,147],[124,135,149],[218,171,81]][tile]);height=.08*np.sin(x*.5)*np.sin(y*.43)
 colors.append(np.uint8(np.clip(base[None,None,:]*(1+value[:,:,None]),0,255)));heights.append(height)
color=np.concatenate([np.concatenate(colors[:4],axis=1),np.concatenate(colors[4:],axis=1)],axis=0);normaltiles=[]
for height in heights:
 dy,dx=np.gradient(height);nx=-dx*.85;ny=dy*.85;nz=np.ones_like(nx);length=np.sqrt(nx*nx+ny*ny+nz*nz);normaltiles.append(np.uint8(np.clip(np.stack([nx/length,ny/length,nz/length],axis=-1)*127.5+127.5,0,255)))
normal=np.concatenate([np.concatenate(normaltiles[:4],axis=1),np.concatenate(normaltiles[4:],axis=1)],axis=0)
Image.fromarray(color).save(r/'wildwood-basecolor-4k.jpg',quality=91,subsampling=0,optimize=True)
Image.fromarray(normal).quantize(colors=128,dither=Image.Dither.NONE).save(r/'wildwood-normal-4k.png',optimize=True)
print([(p.name,p.stat().st_size) for p in r.iterdir()])
