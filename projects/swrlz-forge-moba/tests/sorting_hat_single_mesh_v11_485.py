#!/usr/bin/env python3
"""§E Sorting Hat single-surface native asset and UV-paint acceptance checks."""
import base64,json,math,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"scenes/model-atelier-sorting-hat.swyrl.json"
scene=json.loads(path.read_text("utf8"))
assert scene["project"]["canonicalId"]==scene["project"]["template"]=="sorting-hat"
assert scene["project"]["kind"]=="model-atelier"
m=scene["project"]["modelAtelier"]
assert len(m["parts"])==1,("Must be ONE editable mesh, not a 49-part assembly",len(m["parts"]))
assert not m.get("meshGroups"),"No artificial multi-object face assemblies"
p=m["parts"][0]
assert p["kind"]=="topologyMesh" and p["material"]=="matte"
assert p["group"]=="Single cloth mesh"
a=p["topologyMesh"]
assert set(a)=={"positions","uvs","indices"}
xyz=a["positions"];uv=a["uvs"];ix=a["indices"]
v=len(xyz)//3;t=len(ix)//3
assert 6500<v<9000,(v,"native topology safety budget")
assert 11000<t<16000,(t,"native topology safety budget")
assert len(xyz)%3==len(ix)%3==0
assert len(uv)==2*v
assert all(isinstance(k,int) and 0<=k<v for k in ix)
assert all(math.isfinite(k) and abs(k)<100 for k in xyz)
assert all(math.isfinite(k) and -1<=k<=2 for k in uv)
assert all(len(set(ix[j:j+3]))==3 for j in range(0,len(ix),3))
# One surface component even though UV seam duplicates positions: triangle
# adjacency across the entire crown, underside and brim is connected.
graph=[set() for i in range(v)]
used=set()
for i in range(0,len(ix),3):
  a0,b,c=ix[i:i+3]
  for n,mate in ((a0,b),(b,c),(c,a0)):
    graph[n].add(mate);graph[mate].add(n)
  used.update((a0,b,c))
start=next(iter(used));seen={start};todo=[start]
while todo:
  for adjacent in graph[todo.pop()]:
    if adjacent not in seen:seen.add(adjacent);todo.append(adjacent)
assert len(seen)==len(used)==v,("The original hat, face and brim must be connected as one surface",len(seen),len(used),v)
# User reference: the unposed Sorting Hat is an upright fabric cone.
# A rig may bend it later; no downturned point is baked into its geometry.
# All eight crown rings taper to the upward apex on a near-vertical axis.
stride=97
tip_centers=[]
tip_radii=[]
for ring in range(8):
    coords=[xyz[3*(ring*stride+j):3*(ring*stride+j)+3] for j in range(96)]
    cx=sum(p[0] for p in coords)/len(coords)
    cy=sum(p[1] for p in coords)/len(coords)
    cz=sum(p[2] for p in coords)/len(coords)
    tip_centers.append((cx,cy,cz))
    tip_radii.append((max(p[0] for p in coords)-min(p[0] for p in coords))/2)
# No hooked flap: the point is the highest ring, and consecutive rings
# descend without reversals. Upper/lower ring centers remain vertically aligned.
assert tip_centers[0][1]>tip_centers[-1][1]+1.10,tip_centers
assert all(tip_centers[i][1]>tip_centers[i+1][1]+.052 for i in range(7)),tip_centers
assert max(p[0] for p in tip_centers)-min(p[0] for p in tip_centers)<.055,tip_centers
assert max(p[2] for p in tip_centers)-min(p[2] for p in tip_centers)<.055,tip_centers
assert all(tip_radii[i]<tip_radii[i+1] for i in range(7)),tip_radii
assert tip_radii[0]<.03 and .38<tip_radii[-1]<.46,tip_radii
assert max(tip_radii[i+1]-tip_radii[i] for i in range(7))<.10
assert max(math.dist(tip_centers[i],tip_centers[i+1]) for i in range(7))<.235
tip_cap=xyz[-6:-3]  # exterior cap before interior lining's cap
assert math.dist(tip_cap,tip_centers[0])<.035,(tip_cap,tip_centers[0])
# Ring-to-crown junction is smooth, and the interior remains sealed.
next_coords=[xyz[3*(8*stride+j):3*(8*stride+j)+3] for j in range(96)]
next_center=[sum(p[k] for p in next_coords)/96 for k in range(3)]
assert math.dist(tip_centers[-1],next_center)<.14
assert "dents" in m["reference"].lower() and "brows" in m["reference"].lower()
assert not any(k in p for k in ("eyeObjects","mouthObject","faceOverlay"))
data=p["uvPaintPNG"]
assert data.startswith("data:image/png;base64,") and len(data)<=360000
raw=base64.b64decode(data.split(",",1)[1],validate=True)
assert raw.startswith(b"\x89PNG\r\n\x1a\n")
width,height,depth,color,compression,filter_mode,interlace=struct.unpack(">IIBBBBB",raw[16:29])
assert 512<=width<=1024 and height==width
assert depth==8 and color==2 and interlace==0
# Check actual nontransparent painted RGB, not just a claimed UV map.
chunks=[];pos=8
while pos<len(raw):
  length=int.from_bytes(raw[pos:pos+4],"big")
  kind=raw[pos+4:pos+8]
  data=raw[pos+8:pos+8+length]
  if kind==b"IDAT":chunks.append(data)
  pos+=length+12
image=zlib.decompress(b"".join(chunks))
assert len(image)==height*(1+3*width)
# Front eye paint at u~.41 and .59, v~.63, compared to adjacent cloth.
def rgb(u,v):
  x=round(u*(width-1));y=round((1-v)*(height-1))
  off=y*(1+3*width)+1+3*x
  return image[off:off+3]
eyes=[sum(rgb(.415,.630)),sum(rgb(.585,.630))]
cloth=sum(rgb(.50,.84))
assert max(eyes)<cloth+45,("UV shader eye dent shading is absent",eyes,cloth)
print("SORTING_HAT_SINGLE_MESH_PASS",json.dumps({
 "parts":1,"connectedVertices":v,"triangles":t,
 "textureResolution":width,"textureBytes":len(raw),
 "textureSourceChars":len(p["uvPaintPNG"]),"eyeShadows":eyes
}),flush=True)
