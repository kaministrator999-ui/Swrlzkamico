"""Original Moonbell Wildwood layout + full-resolution painted ground source."""
from pathlib import Path
import copy,json,math,random
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
ROOT=Path(__file__).resolve().parents[1]
SIZE=4096
EXTENT=64
REGIONS=[('Pinewatch',-35,-35),('Moonflower',35,-35),('Amberglade',-35,35),('Willowmere',35,35)]
SPAWNS=[(-34,34),(34,34),(-34,-34),(34,-34),(-48,0),(48,0),(0,48),(0,-48)]
MARKETS=[(-51,-51),(51,-51),(-51,51),(51,51)]
PONDS=[(-45,-24),(24,-13),(-24,13),(45,24)]
LANES=[(-21,-35),(35,-21),(21,35),(-35,21)]
RING=[(0,-43),(35,-35),(43,0),(35,35),(0,43),(-35,35),(-43,0),(-35,-35),(0,-43)]

def build_scene():
    old=json.loads((ROOT/'scenes/sheep-tag-moonbell-archive.swyrl.json').read_text())
    scene=copy.deepcopy(old);scene['engine']='§wyrl§ Engine · Maker v11.79';scene['project']['name']='Sheep Tag · Moonbell Wildwood'
    scene['project']['sheepTag']['bounds']=EXTENT
    scene['project']['environmentSettings'].update(background='#c3deda',fogNear=180,fogFar=350)
    scene['scene']['background']='#c3deda'
    layers=['Ground & woodland roads','Spirit sanctuary & markets','Pinewatch · northwest','Moonflower · northeast','Amberglade · southwest','Willowmere · southeast','Sheep escape passages','Protected market plazas','Sheep & Astra hunter spawns']
    scene['editor']['layers']=[{'id':'wildwood-layer-'+str(i),'name':str(i+1).zfill(2)+' · '+name,'visible':True} for i,name in enumerate(layers)]
    scene['editor']['activeLayerId']='wildwood-layer-8';scene['scene']['actors']=[]
    prototypes={a['type']:a for a in old['scene']['actors']}
    serial=0
    def add(kind,name,x,z,scale=(1,1,1),yaw=0,layer=0):
        nonlocal serial
        serial+=1;a=copy.deepcopy(prototypes[kind]);a.update(id='wildwood-'+str(serial).zfill(3),name=name,position=[x,0,z],rotation=[0,yaw,0],scale=list(scale),editorLayerIds=['wildwood-layer-'+str(layer)],groupParentId=None,groupChildIds=[])
        scene['scene']['actors'].append(a);return a
    add('st-meadow','Moonbell Wildwood · 128 m buildable pasture',0,0,(1.6,1,1.6))
    add('st-pen','Moonbell Sanctuary · four rescue approaches',0,0,layer=1)
    for i,(x,z) in enumerate(MARKETS):
        add('st-shop',REGIONS[i][0]+' · travelling merchant',x,z,yaw=(math.pi if z<0 else 0),layer=1)
        add('st-zone',REGIONS[i][0]+' · protected market plaza',x,z,(1.5,1,1.5),layer=7)
    for i,(x,z) in enumerate(PONDS):
        region=(0 if x<0 else 1)+(2 if z>=0 else 0)
        add('st-pond',['Pinewatch spring','Moonflower pool','Amberglade lily pond','Willowmere lake'][i],x,z,(1.35,1,1.35),layer=region+2)
    for i,(x,z) in enumerate(LANES):
        # A true 1.0 m physical gap: sheep fit; hunters must go around.
        for sign in [-1,1]:add('st-rock','Escape passage '+str(i+1)+' · stone '+str(sign),x+sign*2.3,z,(1,.85,1),layer=6)
        for dz in [-3,0,3]:add('st-road','Escape passage '+str(i+1)+' · trail',x,z+dz,(.27,1,1),layer=6)
    for i in range(8):
        angle=(i+.5)*math.pi/4
        add('st-rock','Sanctuary waystone '+str(i+1),math.sin(angle)*12,math.cos(angle)*12,(.42,2.5,.42),yaw=angle,layer=1)
    rng=random.Random(1179)
    def segment_distance(x,z,a,b):
        dx=b[0]-a[0];dz=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
        return math.hypot(x-a[0]-t*dx,z-a[1]-t*dz)
    roads=[((0,0),p) for p in MARKETS+[(0,-59),(0,59),(-59,0),(59,0)]]+list(zip(RING,RING[1:]))
    def clear(x,z,r=2):
        if math.hypot(x,z)<16:return False
        if any(math.hypot(x-a,z-b)<12+r for _,a,b in REGIONS):return False
        if any(math.hypot(x-a,z-b)<7+r for a,b in SPAWNS+MARKETS+LANES):return False
        if any(math.hypot(x-a,z-b)<5+r for a,b in PONDS):return False
        if any(segment_distance(x,z,a,b)<3.5+r for a,b in roads):return False
        if any(a['type'] in ['st-tree','st-rock'] and math.hypot(x-a['position'][0],z-a['position'][2])<r+2.1 for a in scene['scene']['actors']):return False
        return True
    # Open gateways at the cardinal roads; a woodland edge frames the world.
    for side in [-1,1]:
        for t in range(-59,60,7):
            if abs(t)<9:continue
            for x,z in [(side*61,t),(t,side*61)]:
                if any(math.hypot(x-a['position'][0],z-a['position'][2])<4 for a in scene['scene']['actors'] if a['type']=='st-tree'):continue
                k=(0 if x<0 else 1)+(2 if z>=0 else 0)
                add('st-tree',REGIONS[k][0]+' · woodland edge',x,z,(1+rng.random()*.25,.9+rng.random()*.5,1+rng.random()*.25),yaw=rng.random()*math.tau,layer=k+2)
    # Authored, seeded groves leave broad readable loops and buildable glades.
    for n in range(900):
        if sum(a['type']=='st-tree' for a in scene['scene']['actors'])>=112:break
        x=round(rng.uniform(-57,57),2);z=round(rng.uniform(-57,57),2)
        if not clear(x,z):continue
        k=(0 if x<0 else 1)+(2 if z>=0 else 0);s=rng.uniform(.73,1.12)
        add('st-tree',REGIONS[k][0]+' · grove pine',x,z,(s,rng.uniform(.85,1.3),s),yaw=rng.random()*math.tau,layer=k+2)
    for k,(name,cx,cz) in enumerate(REGIONS):
        # Three outside boulders are navigation landmarks, not sealed glades.
        for i in range(3):
            angle=(i*1.7+.35)+(math.pi if cz<0 else 0)
            x=round(cx+math.cos(angle)*14,2);z=round(cz+math.sin(angle)*14,2)
            if clear(x,z,1):add('st-rock',name+' · mossy standing stone',x,z,(.8,1.45,.8),layer=k+2)
    for i,(x,z) in enumerate(LANES):
        for sign in [-1,1]:add('st-thorn','Escape passage '+str(i+1)+' · optional thorn risk',x+sign*5,z+4,(.8,1,.8),layer=6)
    old_sheep=[a for a in old['scene']['actors'] if a['type']=='st-sheep']
    for a,(x,z) in zip(old_sheep,SPAWNS):add('st-sheep',a['name'],x,z,layer=8)
    for a in [a for a in old['scene']['actors'] if a['type']=='st-wolf']:
        add('st-wolf',a['name'],a['position'][0],a['position'][2],yaw=a['rotation'][1],layer=8)
    (ROOT/'scenes/sheep-tag-wildwood-v11-79.swyrl.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
    print('WILDWOOD_NATIVE_SCENE',len(scene['scene']['actors']),'actors',sum(a['type']=='st-tree' for a in scene['scene']['actors']),'trees')

def paint_ground():
    rng=random.Random(1179);nrng=np.random.default_rng(1179)
    axis=np.linspace(-1,1,SIZE,dtype=np.float32);x=axis[None,:];z=axis[:,None]
    # Several noise bands plus real, full-resolution grass flecks provide
    # original 4K detail; this is not an enlarged low-resolution terrain image.
    noise=np.zeros((SIZE,SIZE),np.float32)
    for n,strength in [(24,9),(100,5),(420,2)]:
        small=Image.fromarray(nrng.integers(0,256,(n,n),dtype=np.uint8)).resize((SIZE,SIZE),Image.Resampling.BICUBIC)
        noise+=(np.asarray(small,dtype=np.float32)/255-.5)*strength
    noise+=nrng.normal(0,.8,(SIZE,SIZE)).astype(np.float32)
    east=(np.tanh(x*4)+1)/2;south=(np.tanh(z*4)+1)/2
    palettes=np.array([[83,121,97],[105,133,130],[142,151,91],[104,148,105]],dtype=np.float32)
    array=np.empty((SIZE,SIZE,3),np.uint8)
    for c in range(3):array[:,:,c]=np.clip(palettes[0,c]*(1-east)*(1-south)+palettes[1,c]*east*(1-south)+palettes[2,c]*(1-east)*south+palettes[3,c]*east*south+noise,0,255).astype(np.uint8)
    image=Image.fromarray(array);d=ImageDraw.Draw(image,'RGBA')
    def xy(p):return ((p[0]+EXTENT)/(EXTENT*2)*SIZE,(p[1]+EXTENT)/(EXTENT*2)*SIZE)
    def disc(x,z,r,fill,outline=None,width=1):
        px,py=xy((x,z));rr=r*SIZE/128;d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=fill,outline=outline,width=width)
    def line(points,width,color):d.line([xy(p) for p in points],fill=color,width=round(width*SIZE/128),joint='curve')
    # Feathered clearings and wide market plazas.
    for name,cx,cz in REGIONS:
        for radius in range(14,9,-1):disc(cx,cz,radius,(176,180,114,22))
    # Main spokes, an octagonal outer loop, and spur roads to merchants.
    roads=[([(0,0),p],3.1) for p in MARKETS+[(0,-62),(0,62),(-62,0),(62,0)]]+[(RING,2.6)]
    for points,width in roads:
        line(points,width+.8,(71,91,61,75));line(points,width+.3,(155,150,107,255));line(points,width,(194,184,137,255));line(points,width*.78,(205,195,152,200))
    for cx,cz in MARKETS:
        disc(cx,cz,5.2,(121,137,117,255));disc(cx,cz,4.9,(172,181,153,255),outline=(218,213,173,255),width=7)
        disc(cx,cz,3.8,None,outline=(137,160,145,255),width=12)
    # Central rescue court and compass mosaic.
    disc(0,0,10.4,(136,156,127,255));disc(0,0,9.9,(184,196,166,255),outline=(221,216,175,255),width=9)
    disc(0,0,8.2,None,outline=(117,153,142,255),width=7)
    for a in range(8):
        t=a*math.pi/4;points=[xy((math.sin(t)*10,math.cos(t)*10)),xy((math.sin(t+.06)*8.3,math.cos(t+.06)*8.3)),xy((math.sin(t-.06)*8.3,math.cos(t-.06)*8.3))];d.polygon(points,fill=(224,211,156,255))
    for cx,cz in PONDS:
        disc(cx,cz,5.2,(135,145,111,160));disc(cx,cz,4.5,(181,176,127,220))
    for cx,cz in LANES:
        line([(cx,cz-7),(cx,cz+7)],.95,(180,199,152,230))
        for zz in range(-6,7,2):disc(cx,cz+zz,.23,(214,216,184,255))
    # Full-resolution blades, gravel and flower heads, softly distributed
    # across the entire original texture (including the outer expansion).
    for i in range(155000):
        px=rng.randrange(SIZE);py=rng.randrange(SIZE);color=(207,215,149,36) if i%3 else (42,89,67,35)
        d.line([(px,py),(px+rng.choice([-1,0,1]),py-rng.randint(1,4))],fill=color,width=1)
    for i in range(13000):
        cx,cz=rng.choice([(a,b) for _,a,b in REGIONS]);a=rng.random()*math.tau;r=rng.uniform(10.5,14)
        px,py=xy((cx+math.cos(a)*r,cz+math.sin(a)*r));col=rng.choice([(241,219,151,190),(205,190,227,190),(225,233,204,170)])
        d.ellipse((px,py,px+2,py+2),fill=col)
    path=ROOT/'assets/sheep-tag/moonbell-wildwood-ground-4k.jpg';image.convert('RGB').save(path,quality=93,subsampling=0,optimize=True)
    print('WILDWOOD_ORIGINAL_4K_GROUND',path.stat().st_size,image.size)

if __name__=='__main__':build_scene();paint_ground()
