// Cached geometry/material template from Clover's native saved mesh LOD.
// Only joint trees are cloned; collision and match state remain unchanged.
let atelierCloverTemplate=null;
function atelierCloverSheep(){
 if(!atelierCloverTemplate){
  const root=new THREE.Group();root.name='st-sheep';const skeleton=new THREE.Group();skeleton.name='CloverMeadowSheep';root.add(skeleton);const joints={};
  for(const [name,position] of Object.entries({stHead:[0,1.64,.79],stTail:[0,1.22,-1],stLeg0:[-.34,1.02,-.68],stLeg1:[.34,1.02,-.68],stLeg2:[-.33,1.06,.49],stLeg3:[.33,1.06,.49]})){const joint=new THREE.Group();joint.name=name;joint.position.fromArray(position);skeleton.add(joint);joints[name]=joint;}
  for(const part of ST_CLOVER_GAME_MODEL.parts){
   let parent=skeleton;const leg=part.name.match(/^(Fore|Hind) (left|right)/);
   if(leg)parent=joints['stLeg'+((leg[1]==='Fore'?2:0)+(leg[2]==='right'?1:0))];
   else if(part.name.startsWith('Tail ·'))parent=joints.stTail;
   else if(part.organicSurface.region!=='wool')parent=joints.stHead;
   const mesh=new THREE.Mesh(atelierSculptApply(geometry(part),part),material(part));mesh.name=part.name;mesh.userData.cloverPartId=part.id;mesh.position.fromArray(part.position).sub(parent===skeleton?new THREE.Vector3():parent.position);mesh.rotation.fromArray(part.rotation);mesh.scale.fromArray(part.scale);mesh.castShadow=mesh.receiveShadow=true;parent.add(mesh);
  }
  const bounds=new THREE.Box3().setFromObject(skeleton),fleece=skeleton.children.find(m=>m.isMesh&&m.userData.cloverPartId==='sheep-0');fleece.geometry.computeBoundingBox();const body=fleece.geometry.boundingBox,fit=Math.min(.46,.52/(body.max.x-body.min.x));skeleton.scale.setScalar(fit);skeleton.position.y=-bounds.min.y*fit;skeleton.userData.sourceModel=ST_CLOVER_GAME_MODEL.sourceModel;skeleton.userData.sourceTriangles=ST_CLOVER_GAME_MODEL.sourceTriangles;atelierCloverTemplate=root;
 }
 return atelierCloverTemplate.clone(true);
}
