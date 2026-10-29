"""Inspect the actual native GLB downloads, including embedded 4K maps."""
from pathlib import Path
import json,struct,hashlib,io,sys,gzip,math
from PIL import Image
root=Path(__file__).resolve().parents[1];out=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/organic-girl-tests')
for species in ['girl']:
 raw=(out/(species+'.glb')).read_bytes();magic,version,length=struct.unpack_from('<III',raw);assert (magic,version,length)==(0x46546c67,2,len(raw));size,tag=struct.unpack_from('<II',raw,12);assert tag==0x4e4f534a;doc=json.loads(raw[20:20+size]);at=20+size;size,tag=struct.unpack_from('<II',raw,at);assert tag==0x004e4942;binary=raw[at+8:at+8+size];assert len(doc['images'])==2 and len(doc['textures'])==2
 def view(index):
  v=doc['bufferViews'][index];return binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
 for i,name in enumerate(['festival-basecolor-4k.jpg','festival-normal-4k.png']):
  data=view(doc['images'][i]['bufferView']);assert data==(root/'assets/models/festival-girl'/name).read_bytes();assert Image.open(io.BytesIO(data)).size==(4096,4096)
 total=0
 for mesh in doc['meshes']:
  primitive=mesh['primitives'][0];attrs=primitive['attributes'];assert {'POSITION','NORMAL','TEXCOORD_0'}<=attrs.keys();pos=doc['accessors'][attrs['POSITION']];normal=doc['accessors'][attrs['NORMAL']];uv=doc['accessors'][attrs['TEXCOORD_0']];indices=doc['accessors'][primitive['indices']];assert pos['count']==normal['count']==uv['count'];assert indices['count']%3==0;values=struct.unpack('<'+'I'*indices['count'],view(indices['bufferView']));assert max(values)<pos['count'];assert len(pos['min'])==len(pos['max'])==3;total+=indices['count']//3
  for key in attrs:
   a=doc['accessors'][attrs[key]];vals=struct.unpack('<'+'f'*(len(view(a['bufferView']))//4),view(a['bufferView']));assert all(math.isfinite(v) for v in vals)
 source=json.loads(gzip.decompress(b''.join(p.read_bytes() for p in sorted((root/'payload/festival-girl').glob('organic-v11-91.swyrl.json.gz.part*')))))['project']['modelAtelier'];assert total==sum(len(p['topologyMesh']['indices'])//3 for p in source['parts']);assert len(doc['meshes'])==len(source['parts'])
 assert len(doc['meshes'])==353
 assert 'COLOR_0' in doc['meshes'][0]['primitives'][0]['attributes']
 for mesh,part in zip(doc['meshes'],source['parts']):
  if part.get('textureBinding'):
   material=doc['materials'][mesh['primitives'][0]['material']]
   assert material['pbrMetallicRoughness']['baseColorTexture']['index']==0
   if part['material']!='emissive':assert material['normalTexture']['scale']==part['textureBinding']['normalStrength']
 print('NATIVE_ORGANIC_GLB_GEOMETRY_UV_NORMALS_INDICES_EMBEDDED_4K_MAPS_PASS',species,len(raw),len(doc['meshes']),total)

 (out/'glb-receipt.json').write_text(json.dumps({'version':'v11.91','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'meshes':len(doc['meshes']),'triangles':total,'finiteGeometryAttributes':True,'indicesWithinBounds':True,'bodyVertexColors':True,'embedded4KColorAndNormalExact':True,'materialBindingsExact':True},indent=2)+'\n')
