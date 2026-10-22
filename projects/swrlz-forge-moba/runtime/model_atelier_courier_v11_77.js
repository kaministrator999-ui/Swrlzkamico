// Shared 4K images, per-region UV transforms, saved native bindings and binary glTF export.
const atelierCourierTiles=['fur','ivory','cloth','leather','brass','comet','lapis','amber'];
const atelierCourierRoughness=[.79,.78,.78,.57,.29,.44,.58,.23];
const atelierCourierSources={color:'assets/models/comet-courier/astra-basecolor-4k.jpg',normal:'assets/models/comet-courier/astra-normal-4k.png'};
const atelierCourierImages=new Map(),atelierCourierMaps=new Map();
function atelierCourierBindingValid(p){const t=p.textureBinding;return t===undefined||!!t&&typeof t==='object'&&!Array.isArray(t)&&Object.keys(t).sort().join('|')==='normalStrength|set|tile'&&t.set==='astra-4k'&&atelierCourierTiles.includes(t.tile)&&Number.isFinite(t.normalStrength)&&t.normalStrength>=0&&t.normalStrength<=2;}
function atelierCourierRect(tile){const k=atelierCourierTiles.indexOf(tile),pad=8;return [(k%4)/4+pad/4096,1-(Math.floor(k/4)+1)/2+pad/4096,1/4-pad*2/4096,1/2-pad*2/4096];}
function atelierCourierMap(type,tile){
 const key=type+'|'+tile;if(atelierCourierMaps.has(key))return atelierCourierMaps.get(key);
 let source=atelierCourierImages.get(type);
 if(!source){source=new THREE.TextureLoader().load(atelierCourierSources[type],()=>{for(const [key,map] of atelierCourierMaps)if(key.startsWith(type+'|'))map.needsUpdate=true;atelierCourierTextureStatus();atelierHDDirty=true;renderer?.render(world,camera);},undefined,()=>status('Texture asset failed to load. Reload the published project.',true));source.colorSpace=type==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;source.anisotropy=Math.min(8,renderer?.capabilities.getMaxAnisotropy()||4);atelierCourierImages.set(type,source);}
 const texture=source.clone();texture.needsUpdate=true;const [x,y,w,h]=atelierCourierRect(tile);texture.offset.set(x,y);texture.repeat.set(w,h);texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;atelierCourierMaps.set(key,texture);return texture;
}
function material(part){
 const base=atelierCourierBaseMaterial(part),b=part.textureBinding;if(!b)return base;
 const m=base.clone();m.map=atelierCourierMap('color',b.tile);
 if(m.isMeshStandardMaterial||m.isMeshPhysicalMaterial){m.normalMap=atelierCourierMap('normal',b.tile);m.normalScale.set(b.normalStrength,b.normalStrength);m.roughness=atelierCourierRoughness[atelierCourierTiles.indexOf(b.tile)];if(b.tile==='brass')m.metalness=.72;}
 m.userData.atelierAtlas='astra-4k';m.userData.atelierTile=b.tile;return m;
}
function atelierCourierTextureStatus(){const el=$m('AtlasStatus');if(!el)return;const images=[...atelierCourierImages.values()].map(t=>t.image);el.textContent=images.length===2&&images.every(i=>i?.width===4096&&i?.height===4096)?'4K base color + 4K normal map loaded · shared atlas images.':'Shared 4096 × 4096 material atlas · loading when assigned.';}
function atelierCourierRefresh(){const p=partById(selection),group=p&&atelierGroupOf(p.id);$m('GroupNameDeck').hidden=!group;if(group)$m('GroupName').value=group.name;$m('AtlasDeck').hidden=!p;if(p){$m('AtlasTile').value=p.textureBinding?.tile||'none';$m('AtlasNormal').value=p.textureBinding?.normalStrength??.65;}atelierCourierTextureStatus();}
async function atelierCourierGLB(){
 if(!modelRoot)return;const chunks=[],views=[],accessors=[],meshes=[],nodes=[],materials=[],materialKeys=new Map();let length=0;
 const add=data=>{const bytes=data instanceof Uint8Array?data:new Uint8Array(data.buffer,data.byteOffset,data.byteLength);const padding=(4-length%4)%4;if(padding){chunks.push(new Uint8Array(padding));length+=padding;}const index=views.length;views.push({buffer:0,byteOffset:length,byteLength:bytes.byteLength});chunks.push(bytes);length+=bytes.byteLength;return index;};
 const attribute=(array,type,componentType,bounds=false)=>{const view=add(array),n=type==='VEC3'?3:type==='VEC2'?2:1,a={bufferView:view,componentType,count:array.length/n,type};if(bounds){a.min=Array(n).fill(Infinity);a.max=Array(n).fill(-Infinity);for(let i=0;i<array.length;i++){const k=i%n;a.min[k]=Math.min(a.min[k],array[i]);a.max[k]=Math.max(a.max[k],array[i]);}}accessors.push(a);return accessors.length-1;};
 const textured=model().parts.some(p=>p.textureBinding);const images=[];
 if(textured)for(const [type,mime] of [['color','image/jpeg'],['normal','image/png']]){const response=await fetch(atelierCourierSources[type]);if(!response.ok)throw Error('Texture download failed');images.push({bufferView:add(new Uint8Array(await response.arrayBuffer())),mimeType:mime,name:type+' 4096px atlas'});}
 for(const mesh of modelRoot.children.filter(o=>o.isMesh&&o.userData.atelierId)){
  const p=partById(mesh.userData.atelierId);if(!p)continue;mesh.updateMatrixWorld(true);const g=mesh.geometry,pos=g.attributes.position,normal=g.attributes.normal,uv=g.attributes.uv,col=g.attributes.color,positions=[],normals=[],uvs=[],colors=[],nm=new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld),rect=p.textureBinding?atelierCourierRect(p.textureBinding.tile):[0,0,1,1];
  for(let i=0;i<pos.count;i++){const q=new THREE.Vector3().fromBufferAttribute(pos,i).applyMatrix4(mesh.matrixWorld);positions.push(q.x,q.y,q.z);const n=normal?new THREE.Vector3().fromBufferAttribute(normal,i).applyMatrix3(nm).normalize():new THREE.Vector3(0,1,0);normals.push(n.x,n.y,n.z);const u=uv?.getX(i)||0,v=uv?.getY(i)||0;uvs.push(rect[0]+u*rect[2],1-(rect[1]+v*rect[3]));if(col)colors.push(col.getX(i),col.getY(i),col.getZ(i));}
  const attrs={POSITION:attribute(new Float32Array(positions),'VEC3',5126,true),NORMAL:attribute(new Float32Array(normals),'VEC3',5126),TEXCOORD_0:attribute(new Float32Array(uvs),'VEC2',5126)};if(colors.length)attrs.COLOR_0=attribute(new Float32Array(colors),'VEC3',5126);
  const key=JSON.stringify([p.color,p.material,p.textureBinding,p.hdFinish?.style]);let mi=materialKeys.get(key);
  if(mi===undefined){mi=materials.length;materialKeys.set(key,mi);const m=mesh.material,c=m.color||new THREE.Color('#ffffff'),mat={name:p.name+' surface',doubleSided:true,pbrMetallicRoughness:{baseColorFactor:[c.r,c.g,c.b,1],metallicFactor:m.metalness||0,roughnessFactor:m.roughness??.8}};if(p.textureBinding){mat.pbrMetallicRoughness.baseColorTexture={index:0};if(m.normalMap)mat.normalTexture={index:1,scale:p.textureBinding.normalStrength};}if(p.material==='emissive'){mat.emissiveFactor=[.65,.9,1];if(p.textureBinding)mat.emissiveTexture={index:0};}materials.push(mat);}
  const index=g.index?new Uint32Array(g.index.array):Uint32Array.from({length:pos.count},(_,i)=>i);meshes.push({name:p.name,primitives:[{attributes:attrs,indices:attribute(index,'SCALAR',5125),material:mi}]});nodes.push({name:p.name,mesh:meshes.length-1});
 }
 const doc={asset:{version:'2.0',generator:'§wyrl§ Engine v11.77 native textured mesh export'},scene:0,scenes:[{name:currentProject.name,nodes:nodes.map((_,i)=>i)}],nodes,meshes,materials,buffers:[{byteLength:length}],bufferViews:views,accessors};if(textured){doc.images=images;doc.textures=[{source:0,sampler:0},{source:1,sampler:0}];doc.samplers=[{magFilter:9729,minFilter:9987,wrapS:33071,wrapT:33071}];}
 let json=new TextEncoder().encode(JSON.stringify(doc));const jp=(4-json.length%4)%4,jbuf=new Uint8Array(json.length+jp);jbuf.fill(32);jbuf.set(json);const bp=(4-length%4)%4,bin=new Uint8Array(length+bp);let at=0;for(const c of chunks){bin.set(c,at);at+=c.length;}const output=new Uint8Array(12+8+jbuf.length+8+bin.length),dv=new DataView(output.buffer);dv.setUint32(0,0x46546c67,true);dv.setUint32(4,2,true);dv.setUint32(8,output.length,true);dv.setUint32(12,jbuf.length,true);dv.setUint32(16,0x4e4f534a,true);output.set(jbuf,20);const bo=20+jbuf.length;dv.setUint32(bo,bin.length,true);dv.setUint32(bo+4,0x004e4942,true);output.set(bin,bo+8);download('astra-comet-courier.glb',output,'model/gltf-binary');status('Textured GLB exported with real geometry, UVs, materials and embedded 4K images.');
}
function atelierCourierInstall(){
 $m('CourierStudio').addEventListener('click',()=>{const studio=panel.classList.toggle('courier-studio');$m('CourierStudio').textContent=studio?'Edit model':'Studio view';$m('CourierStudio').setAttribute('aria-pressed',String(studio));});
 $m('GroupRename').addEventListener('click',()=>{const p=partById(selection),g=p&&atelierGroupOf(p.id),name=$m('GroupName').value.trim();if(!g||!name||name.length>100){status('Choose an assembly and a name up to 100 characters.',true);return;}checkpoint();g.name=name;signalEdited();select(p.id);});
 $m('AtlasApply').addEventListener('click',()=>{const p=partById(selection);if(!p)return;const tile=$m('AtlasTile').value,next={...p};if(tile==='none')delete next.textureBinding;else next.textureBinding={set:'astra-4k',tile,normalStrength:Number($m('AtlasNormal').value)};if(!checkPart(next)){status('Texture binding rejected.',true);return;}checkpoint();if(next.textureBinding)p.textureBinding=next.textureBinding;else delete p.textureBinding;signalEdited();select(p.id);});
 $m('ExportGLB').addEventListener('click',()=>atelierCourierGLB().catch(e=>status('GLB export failed: '+e.message,true)));
}
// Preserve old projects verbatim; new atlas lofts use winding-consistent smooth normals.
function geometry(part){
 const g=atelierCourierBaseGeometry(part);
 if(part.textureBinding&&part.kind==='loft'&&!part.hdFinish&&g.index){const a=g.index.array;for(let i=0;i<a.length;i+=3){const t=a[i+1];a[i+1]=a[i+2];a[i+2]=t;}g.computeVertexNormals();}
 return g;
}
function atelierCourierCamera(view){
 const presets={front:[0,.08],back:[Math.PI,.08],left:[-Math.PI/2,.08],right:[Math.PI/2,.08],three:[.46,.14],hero:[.32,.10]};if(!presets[view]||!camera||!modelRoot)return false;
 const box=new THREE.Box3();for(const mesh of modelRoot.children)if(mesh.isMesh&&mesh.userData.atelierId){mesh.updateMatrixWorld(true);box.expandByObject(mesh);}if(box.isEmpty())return false;
 const center=box.getCenter(new THREE.Vector3()),[yaw,pitch]=presets[view];atelierDetailTarget=center;atelierCameraPan.set(0,0,0);orbit={yaw,pitch,distance:5};cameraUpdate();
 const inverse=camera.quaternion.clone().invert(),tanY=Math.tan(camera.fov*Math.PI/360),tanX=tanY*camera.aspect;let distance=.5;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const q=new THREE.Vector3(x,y,z).sub(center).applyQuaternion(inverse);distance=Math.max(distance,Math.abs(q.x)/tanX+q.z,Math.abs(q.y)/tanY+q.z);}
 orbit.distance=distance*1.12+.15;cameraUpdate();return true;
}
