"""Deterministic native 4096px textile, skin, iris, hair and leather atlases."""
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]/'assets/models/festival-girl';root.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1191);w,h=1024,2048;y,x=np.mgrid[0:h,0:w];u=x/(w-1);v=y/(h-1);color=np.zeros((4096,4096,3),np.uint8);normal=np.zeros_like(color)
for k in range(8):
 noise=rng.normal(0,1,(h,w)).astype(np.float32)
 if k==0: # porcelain skin: restrained pore breakup, clean anime shading
  height=(np.sin(x*1.41)*np.sin(y*1.17)+noise*.3)*.00028;rgb=np.stack([253+noise*.3,248+noise*.4,247+noise*.4],-1)
 elif k in (1,2):
  weave=np.sin(x*np.pi/2)*np.sin(y*np.pi/2);threads=np.sin(x*.8)+np.sin(y*.8);height=weave*.0012+threads*.00045
  embroidery=(np.sin(u*28*np.pi+np.sin(v*12*np.pi)*.8)**18)*(np.cos(v*32*np.pi)**16)
  height+=embroidery*.004;shade=248+weave*2+noise*.3;rgb=np.stack([shade,shade,shade],-1);rgb-=embroidery[:,:,None]*np.array([4,8,16]);
 elif k==3:
  grain=np.sin(x*.47+np.sin(y*.33))*np.sin(y*.51)+noise*.35;height=grain*.0014;shade=238+grain*3;rgb=np.stack([shade,shade,shade],-1)
 elif k==4:
  height=(np.sin(u*40*np.pi+np.sin(v*10*np.pi)*.5)**20)*.002;shade=250+np.sin(u*8*np.pi)*3;rgb=np.stack([shade,shade*.99,shade*.96],-1)
 elif k==5:
  flow=u+.006*np.sin(v*18)+.003*np.sin(v*37);strands=np.sin(flow*380*np.pi)+.5*np.sin(flow*750*np.pi);height=strands*.0008;shade=237+strands*4+14*np.exp(-((u-.42)/.17)**2);rgb=np.stack([shade,shade,shade],-1)
 elif k==6:
  height=(np.sin(x*.8)*np.sin(y*.8))*.001;shade=245+np.sin(v*8)*2;rgb=np.stack([shade,shade,shade],-1)
 else:
  dx=(u-.5)*2;dy=(v-.5)*2;r=np.sqrt(dx*dx+dy*dy);angle=np.arctan2(dy,dx);fibers=(np.sin(angle*119+r*29)+np.sin(angle*73-r*17))*.5
  ring=np.exp(-((r-.57)/.2)**2);dark=np.clip((r-.8)/.2,0,1);rgb=np.stack([170+70*ring+fibers*11,82+90*ring+fibers*9,72+20*ring+fibers*8],-1);rgb*=1-dark[:,:,None]*.55;rgb*=.68+.32*np.clip(v*1.6,0,1)[:,:,None];height=fibers*.001
 gy,gx=np.gradient(height);n=np.stack([-gx*80,-gy*80,np.ones_like(gx)],-1);n/=np.sqrt((n*n).sum(-1))[:,:,None];n=((n*.5+.5)*255).clip(0,255).astype(np.uint8);top=(k//4)*h;left=(k%4)*w;color[top:top+h,left:left+w]=rgb.clip(0,255).astype(np.uint8);normal[top:top+h,left:left+w]=n
Image.fromarray(color).save(root/'festival-basecolor-4k.jpg',quality=96,subsampling=0,optimize=True)
Image.fromarray(normal).save(root/'festival-normal-4k.png',optimize=True)
print('FESTIVAL_NATIVE_4K_COLOR_NORMAL_ATLASES',[(p.name,p.stat().st_size) for p in root.iterdir()])
