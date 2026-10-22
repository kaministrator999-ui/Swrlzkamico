// Original 128 m Wildwood terrain. Old 80 m saved meadows retain their visual.
let stWildwoodGroundTexture=null;
function stWildwoodVisual(){
 const root=new THREE.Group();
 if(!stWildwoodGroundTexture){
  stWildwoodGroundTexture=new THREE.TextureLoader().load('assets/sheep-tag/moonbell-wildwood-ground-4k.jpg');
  stWildwoodGroundTexture.colorSpace=THREE.SRGBColorSpace;
  stWildwoodGroundTexture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
 }
 // Keep the native 80 m prefab coordinate system. Its saved 1.6× X/Z
 // transform makes 128 m, including creator imports which generate a floor.
 const ground=new THREE.Mesh(new THREE.PlaneGeometry(80,80),new THREE.MeshStandardMaterial({map:stWildwoodGroundTexture,color:'#ffffff',roughness:.98,metalness:0}));
 ground.name='MoonbellWildwoodGround';ground.rotation.x=-Math.PI/2;ground.position.y=.04;ground.receiveShadow=true;root.add(ground);
 const base=new THREE.Mesh(new THREE.BoxGeometry(80,.22,80),new THREE.MeshStandardMaterial({color:'#526e5d',roughness:1}));base.position.y=-.65;root.add(base);
 return root;
}
function stWildwoodStyle(actor){
 if(currentProject.kind!=='sheep-tag'||stRules().bounds!==64)return;
 const kind=actor.userData.actorType;if(kind!=='st-tree')return;
 const region=(actor.position.x<0?0:1)+(actor.position.z>=0?2:0);
 const colors=[['#285f56','#3d7c69','#83a98b'],['#526b81','#71899b','#a7b6b9'],['#6c7846','#949958','#bcc07c'],['#367d68','#629c7c','#9dc49a']][region];
 let i=0;actor.traverse(o=>{if(o.isMesh&&o.geometry.type==='ConeGeometry')o.material.color.set(colors[i++%3]);});
}
function stWildwoodMapStatus(){
 const ground=actors.find(a=>a.userData.actorType==='st-meadow')?.getObjectByName('MoonbellWildwoodGround');
 const size=ground?new THREE.Box3().setFromObject(ground).getSize(new THREE.Vector3()):null;
 return {sourceScene:ST_ARCHIVE_SOURCE_SCENE,bounds:stRules().bounds,width:stRules().bounds*2,depth:stRules().bounds*2,
  groundSize:size?[size.x,size.z]:[80,80],
  textureSize:ground?[ground.material.map.image?.width||0,ground.material.map.image?.height||0]:null,
  actorCount:actors.length,regions:stRules().bounds===64?['Pinewatch','Moonflower','Amberglade','Willowmere']:[],
  layerCount:editorLayers.length};
}
