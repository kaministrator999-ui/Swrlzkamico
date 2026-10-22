// Reuse Astra's saved native parts and material atlas in Sheep Tag. Geometry
// and materials are built once; hunter instances have independent joint trees.
let atelierCourierHunterTemplate=null;
function atelierCourierHunter(){
 if(!atelierCourierHunterTemplate){
  const root=new THREE.Group();root.name='st-wolf';
  const skeleton=new THREE.Group();skeleton.name='AstraCometCourier';root.add(skeleton);
  const joints={};
  for(const [name,position] of Object.entries({stHead:[0,2.12,.43],stTail:[0,1.13,-.73],stLeg0:[-.35,1.04,-.61],stLeg1:[.35,1.04,-.61],stLeg2:[-.36,1.72,.42],stLeg3:[.36,1.72,.42]})){
   const joint=new THREE.Group();joint.name=name;joint.position.fromArray(position);skeleton.add(joint);joints[name]=joint;
  }
  const authored=COMET_COURIER_PROJECT.project.modelAtelier;
  const heads=new Set(authored.meshGroups.find(g=>g.name==='Face, ears and cheek ruff').members);
  const tails=new Set(authored.meshGroups.find(g=>g.name==='Comet tail and stardust').members);
  for(const p of authored.parts){
   let parent=skeleton;
   if(heads.has(p.id))parent=joints.stHead;
   else if(tails.has(p.id))parent=joints.stTail;
   else{
    const leg=p.name.match(/^(?:Fox · (foreleg|hock|haunch)|(?:Paw|Toe|Claw) · (front|back)) (-?1)(?: |$)/);
    if(leg){const front=(leg[1]==='foreleg'||leg[2]==='front'),right=leg[3]==='1';parent=joints['stLeg'+((front?2:0)+(right?1:0))];}
   }
   const mesh=new THREE.Mesh(atelierSculptApply(geometry(p),p),material(p));
   mesh.name=p.name;mesh.userData.courierPartId=p.id;
   mesh.position.fromArray(p.position).sub(parent===skeleton?new THREE.Vector3():parent.position);
   mesh.rotation.fromArray(p.rotation);mesh.scale.fromArray(p.scale);
   mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);
  }
  // Fit the existing hunter's world scale and put the actual paw soles on
  // local ground. The logical actor/collider/root transform stays unchanged.
  const bounds=new THREE.Box3().setFromObject(skeleton);
  skeleton.scale.setScalar(.58);skeleton.position.y=-bounds.min.y*.58;
  atelierCourierHunterTemplate=root;
 }
 return atelierCourierHunterTemplate.clone(true);
}
