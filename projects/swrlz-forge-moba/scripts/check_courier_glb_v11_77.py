"""Validate the actual native GLB export, including geometry buffers and embedded 4K images."""
import sys,json,struct,io,math
from PIL import Image
b=open(sys.argv[1],'rb').read();magic,version,size=struct.unpack_from('<III',b);assert magic==0x46546c67 and version==2 and size==len(b)
n,kind=struct.unpack_from('<II',b,12);assert kind==0x4e4f534a;d=json.loads(b[20:20+n]);length,kind=struct.unpack_from('<II',b,20+n);assert kind==0x004e4942;data=b[28+n:];assert len(data)==length
assert len(d['meshes'])==106 and len(d['nodes'])==106 and len(d['images'])==2
for image in d['images']:
 v=d['bufferViews'][image['bufferView']];raw=data[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 im=Image.open(io.BytesIO(raw));assert im.size==(4096,4096);print('GLB_EMBEDDED_4K_IMAGE',image['mimeType'],len(raw))
triangles=0
for a in d['accessors']:
 v=d['bufferViews'][a['bufferView']];start=v.get('byteOffset',0);end=start+v['byteLength'];assert 0<=start<end<=d['buffers'][0]['byteLength'];assert a['count']>0
 if a['componentType']==5126:
  for x in struct.iter_unpack('<f',data[start:end]):assert math.isfinite(x[0])
for m in d['meshes']:
 p=m['primitives'][0];assert {'POSITION','NORMAL','TEXCOORD_0'}<=set(p['attributes']);count=d['accessors'][p['indices']]['count'];assert count%3==0;triangles+=count//3
assert triangles>50000
assert sum('baseColorTexture' in m['pbrMetallicRoughness'] for m in d['materials'])>=6
print('COURIER_GLB_REAL_MESH_UV_NORMAL_MATERIAL_AND_4K_TEXTURES_PASS',len(b),triangles)
