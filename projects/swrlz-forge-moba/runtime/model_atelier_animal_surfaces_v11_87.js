const atelierAnimalMaterialBase=material,atelierAnimalGeometryBase=geometry;
geometry=function(part){
 const g=atelierAnimalGeometryBase(part),s=part.organicSurface;if(!s)return g;
 if(s.species==='wolf'&&['coat','tail'].includes(s.region)){
  const p=g.attributes.position,colors=[],dark=new THREE.Color('#424c4d'),mid=new THREE.Color('#949994'),cream=new THREE.Color('#ddd5be');
  for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),back=THREE.MathUtils.smoothstep(y,1.14,1.55)*(1-THREE.MathUtils.smoothstep(z,.8,1.5)),throat=THREE.MathUtils.smoothstep(z,.45,1.2)*(1-THREE.MathUtils.smoothstep(y,1.32,1.74)),belly=1-THREE.MathUtils.smoothstep(y,.8,1.2);const color=mid.clone().lerp(dark,back*.88).lerp(cream,Math.max(throat,belly)*.88);const mask=THREE.MathUtils.smoothstep(z,1.07,1.5)*(1-THREE.MathUtils.smoothstep(Math.abs(x),.06,.24));color.lerp(cream,mask*.6);colors.push(color.r,color.g,color.b);}
  g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
 }
 return g;
};
material=function(part){
 const m=atelierAnimalMaterialBase(part);if(!part.organicSurface)return m;
 m.metalness=0;m.roughness=part.organicSurface.region==='eye'?.15:.84;
 if(['coat','tail'].includes(part.organicSurface.region)){m.vertexColors=true;m.color.set('#ffffff');}
 if(['wool','coat','tail'].includes(part.organicSurface.region)&&m.isMeshStandardMaterial){const physical=new THREE.MeshPhysicalMaterial({color:m.color,map:m.map,normalMap:m.normalMap,normalScale:m.normalScale,vertexColors:m.vertexColors,roughness:m.roughness,metalness:0,side:m.side});physical.sheen=.28;physical.sheenRoughness=.9;physical.sheenColor=new THREE.Color('#d8cfb9');return physical;}
 return m;
};
function atelierAnimalTextureSources(set){return set==='wildwood-4k'?{color:'assets/models/wildwood-animals/wildwood-basecolor-4k.jpg',normal:'assets/models/wildwood-animals/wildwood-normal-4k.png'}:atelierCourierSources;}
function atelierAnimalMap(type,tile,set='astra-4k'){
 const key=set+'|'+type+'|'+tile,imageKey=set+'|'+type;if(atelierCourierMaps.has(key))return atelierCourierMaps.get(key);
 let source=atelierCourierImages.get(imageKey);
 if(!source){source=new THREE.TextureLoader().load(atelierAnimalTextureSources(set)[type],()=>{for(const [key,map] of atelierCourierMaps)if(key.startsWith(imageKey+'|'))map.needsUpdate=true;atelierCourierTextureStatus();atelierHDDirty=true;renderer?.render(world,camera);},undefined,()=>status('Texture asset failed to load. Reload the published project.',true));source.colorSpace=type==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;source.anisotropy=Math.min(8,renderer?.capabilities.getMaxAnisotropy()||4);atelierCourierImages.set(imageKey,source);}
 const texture=source.clone();texture.needsUpdate=true;const [x,y,w,h]=atelierCourierRect(tile);texture.offset.set(x,y);texture.repeat.set(w,h);texture.wrapS=texture.wrapT=THREE.ClampToEdgeWrapping;atelierCourierMaps.set(key,texture);return texture;
}
atelierCourierMap=atelierAnimalMap;
function atelierAnimalStatus(){
 const data=model();if(!data?.parts.some(p=>p.organicSurface))return null;
 return {valid:validParts(data.parts)&&atelierGroupsValid(data.meshGroups||[],data.parts),species:data.parts[0].organicSurface.species,parts:data.parts.length,triangles:data.parts.reduce((sum,p)=>sum+p.topologyMesh.indices.length/3,0),meshes:modelRoot.children.filter(m=>m.isMesh&&m.userData.atelierId).map(m=>({id:m.userData.atelierId,vertices:m.geometry.attributes.position.count,triangles:(m.geometry.index?.count||0)/3,vertexColors:!!m.material.vertexColors,baseColorSize:[m.material.map?.image?.width||0,m.material.map?.image?.height||0],normalSize:[m.material.normalMap?.image?.width||0,m.material.normalMap?.image?.height||0]}))};
}
