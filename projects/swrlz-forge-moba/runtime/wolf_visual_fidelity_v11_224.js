// §E v11.224 · compact, native editable Astra wolf facial/coat refinements.
// Same detail source is placed on the Wolf Model starter and Sheep Tag wolves.
// Keep all original 4K fur, accessories, huge comet tail and original anatomy.
const SE224_WOLF_DETAILS=Object.freeze([
 {name:'Brow · left shadow ridge',kind:'sphere',group:'head',at:[-.255,2.61,.764],size:[.13,.038,.052],color:'#303d4c',rz:.14},
 {name:'Brow · right shadow ridge',kind:'sphere',group:'head',at:[.255,2.61,.764],size:[.13,.038,.052],color:'#303d4c',rz:-.14},
 {name:'Cheek · left swept ruff',kind:'cone',group:'head',at:[-.38,2.30,.58],size:[.145,.22,.105],color:'#a9b5b2',rz:-.38},
 {name:'Cheek · right swept ruff',kind:'cone',group:'head',at:[.38,2.30,.58],size:[.145,.22,.105],color:'#a9b5b2',rz:.38},
 {name:'Muzzle · pale bridge highlight',kind:'sphere',group:'head',at:[0,2.38,.785],size:[.16,.065,.18],color:'#d8d4c2'},
 {name:'Nose · sculpted charcoal',kind:'sphere',group:'head',at:[0,2.33,1.000],size:[.126,.075,.085],color:'#1c252b'},
 {name:'Muzzle · soft dark jawline',kind:'sphere',group:'jaw',at:[0,2.23,.84],size:[.175,.061,.23],color:'#414952'},
 {name:'Fang · left upper canine',kind:'cone',group:'jaw',at:[-.115,2.225,1.024],size:[.027,.068,.027],color:'#f2e8d7',rz:Math.PI},
 {name:'Fang · right upper canine',kind:'cone',group:'jaw',at:[.115,2.225,1.024],size:[.027,.068,.027],color:'#f2e8d7',rz:Math.PI},
 {name:'Neck · left mane sweep',kind:'cone',group:'body',at:[-.31,1.96,.30],size:[.18,.27,.12],color:'#a8b5b0',rz:-.18},
 {name:'Neck · right mane sweep',kind:'cone',group:'body',at:[.31,1.96,.30],size:[.18,.27,.12],color:'#a8b5b0',rz:.18},
 {name:'Chest · luminous ivory fur tuft',kind:'sphere',group:'body',at:[0,1.73,.55],size:[.24,.18,.09],color:'#cec9b9'}
]);
function se224WolfDetailPart(spec,i){
 const geometry=spec.kind==='cone'?new THREE.ConeGeometry(1,1,7,1):
  new THREE.SphereGeometry(1,10,7);
 geometry.scale(...spec.size);
 if(spec.rz)geometry.rotateZ(spec.rz);
 const non=geometry.toNonIndexed();
 const positions=Array.from(non.getAttribute('position').array);
 const uvs=Array.from(non.getAttribute('uv').array);
 const indices=Array.from({length:positions.length/3},(_,j)=>j);
 geometry.dispose();non.dispose();
 return {id:'wolf224-'+i,name:'Astra · '+spec.name,kind:'topologyMesh',
  position:spec.at.slice(),rotation:[0,0,0],scale:[1,1,1],
  color:spec.color,material:'matte',group:'Wolf · refined details',
  topologyMesh:{positions,uvs,indices},organicSurface:{species:'courier',region:'wolf224-'+spec.group},
  wolf224Joint:spec.group};
}
function se224WolfEnhanceModel(m){
 if(!m||!Array.isArray(m.parts)||m.parts.some(p=>p.id==='wolf224-0'))return m;
 const parts=SE224_WOLF_DETAILS.map(se224WolfDetailPart);
 m.parts.push(...parts);
 m.meshGroups=m.meshGroups||[];
 m.meshGroups.push({id:'wolf224-face-mane',name:'Astra · refined wolf expression',
  members:parts.map(p=>p.id)});
 return m;
}
function se224WolfGameVisual(root){
 if(!root||root.userData.wolf224Enhanced)return root;
 const head=root.getObjectByName('stHead'),tail=root.getObjectByName('stTail'),
  skeleton=root.getObjectByName('AstraCometCourier');
 if(!head||!tail||!skeleton)return root;
 // Add one jaw articulation, sharing the same approved wolf motion library.
 let jaw=head.getObjectByName('stJaw');
 if(!jaw){jaw=new THREE.Group();jaw.name='stJaw';jaw.position.set(0,.18,.42);head.add(jaw);}
 const parent={head,jaw,body:skeleton},origins={
  head:[0,2.12,.43],jaw:[0,2.30,.85],body:[0,0,0]
 };
 for(const key of ['head','jaw','body']){
  const specs=SE224_WOLF_DETAILS.filter(s=>s.group===key);
  const positions=[],normals=[],colors=[],indices=[];let offset=0;
  for(const spec of specs){
   const geom=spec.kind==='cone'?new THREE.ConeGeometry(1,1,7,1):new THREE.SphereGeometry(1,10,7);
   geom.scale(...spec.size);
   if(spec.rz)geom.rotateZ(spec.rz);
   const ctr=spec.at.map((v,i)=>v-origins[key][i]);
   geom.translate(...ctr);
   const g=geom.toNonIndexed(),pos=g.getAttribute('position'),norm=g.getAttribute('normal'),
    color=new THREE.Color(spec.color);
   for(let i=0;i<pos.count;i++){
    positions.push(pos.getX(i),pos.getY(i),pos.getZ(i));
    normals.push(norm.getX(i),norm.getY(i),norm.getZ(i));
    colors.push(color.r,color.g,color.b);indices.push(offset++);
   }
   g.dispose();geom.dispose();
  }
  if(!positions.length)continue;
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute('normal',new THREE.Float32BufferAttribute(normals,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  geo.setIndex(indices);
  const mat=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.87,metalness:0});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.name='Astra · enhanced '+key;mesh.castShadow=true;mesh.receiveShadow=true;
  mesh.userData.wolf224VisualOnly=true;parent[key].add(mesh);
 }
 root.userData.wolf224Enhanced=true;
 return root;
}
