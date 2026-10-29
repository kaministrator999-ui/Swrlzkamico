// Merge compatible native game meshes per animated joint. Authoring parts stay
// separate in the high resolution starter; game instances share cached buffers.
atelierCourierHunter=function(){
 if(!atelierFurredHunterTemplate){
  const root=new THREE.Group();root.name='st-wolf';const skeleton=new THREE.Group();skeleton.name='AstraCometCourier';root.add(skeleton);const joints={};
  for(const [name,position] of Object.entries({stHead:[0,2.12,.43],stTail:[0,1.13,-.73],stLeg0:[-.35,1.04,-.61],stLeg1:[.35,1.04,-.61],stLeg2:[-.36,1.72,.42],stLeg3:[.36,1.72,.42]})){const j=new THREE.Group();j.name=name;j.position.fromArray(position);skeleton.add(j);joints[name]=j;}
  const authored=ST_ASTRA_FURRED_GAME_MODEL,heads=new Set(authored.meshGroups.find(g=>g.name==='Face, ears and cheek ruff').members),tails=new Set(authored.meshGroups.find(g=>g.name==='Comet tail and stardust').members),batches=new Map();
  for(const p of authored.parts){let parent=skeleton;const id=p.id.replace(/^astra-fur-/,'');if(heads.has(id))parent=joints.stHead;else if(tails.has(id))parent=joints.stTail;else{const leg=id.match(/^astra-living-(fore|hind)-(-?1)/);if(leg)parent=joints['stLeg'+((leg[1]==='fore'?2:0)+(leg[2]==='1'?1:0))];}
   const key=JSON.stringify([parent.name,p.color,p.material,p.textureBinding,p.organicSurface?.region==='eye']);let batch=batches.get(key);if(!batch){batch={parent,part:p,positions:[],normals:[],uvs:[],indices:[],ids:[]};batches.set(key,batch);}
   const g=atelierSculptApply(geometry(p),p),matrix=new THREE.Matrix4().compose(new THREE.Vector3().fromArray(p.position).sub(parent===skeleton?new THREE.Vector3():parent.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3().fromArray(p.scale));g.applyMatrix4(matrix);const offset=batch.positions.length/3;batch.positions.push(...g.attributes.position.array);batch.normals.push(...g.attributes.normal.array);batch.uvs.push(...g.attributes.uv.array);batch.indices.push(...(g.index?Array.from(g.index.array):Array.from({length:g.attributes.position.count},(_,i)=>i)).map(i=>i+offset));batch.ids.push(p.id);g.dispose();
  }
  for(const b of batches.values()){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(b.positions,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(b.normals,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(b.uvs,2));g.setIndex(b.indices);g.computeBoundingSphere();const detailed=material(b.part),m=new THREE.MeshStandardMaterial({color:detailed.color,map:detailed.map,normalMap:detailed.normalMap,normalScale:detailed.normalScale,roughness:detailed.roughness,metalness:detailed.metalness,emissive:detailed.emissive,emissiveIntensity:detailed.emissiveIntensity,side:detailed.side});const mesh=new THREE.Mesh(g,m);mesh.name='Astra game · '+b.part.name;mesh.userData.courierPartIds=b.ids;mesh.castShadow=mesh.receiveShadow=true;b.parent.add(mesh);}
  const bounds=new THREE.Box3().setFromObject(skeleton);skeleton.scale.setScalar(.58);skeleton.position.y=-bounds.min.y*.58;skeleton.userData.sourceModel=authored.sourceModel;skeleton.userData.furred=true;atelierFurredHunterTemplate=root;
 }
 return atelierFurredHunterTemplate.clone(true);
};
let atelierFurredHunterTemplate=null;
