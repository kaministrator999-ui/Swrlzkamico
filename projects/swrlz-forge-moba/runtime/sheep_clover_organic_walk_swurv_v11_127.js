// §E v11.127 — the real Model Atelier Clover sheep, reused in Sheep Tag.
// Make one reduced-density mobile runtime rig from the SAME organic shape
// generator, not an unrelated sheep silhouette or external downloaded model.
let st127SheepPrototype=null,st127SheepModelError=null;
function st127Hash(seed){
 let h=2166136261;for(const ch of String(seed))h=Math.imul(h^ch.charCodeAt(0),16777619);
 return (h>>>0)/4294967296;
}
function st127BuildOrganicPrototype(){
 if(st127SheepPrototype)return st127SheepPrototype;
 if(typeof atelierAnimalBuild!=='function'||typeof atelierAnimalSurface!=='function')return null;
 // At native editor resolution this organic body contains high-density
 // editable topology. Sample its *same* authored volumes at gameplay LOD,
 // build once and share mesh resources across all visible sheep.
 const original=atelierAnimalSurface;
 let data;
 try{
  atelierAnimalSurface=function(field,bounds,step){return original(field,bounds,Math.max(.072,step));};
  data=atelierAnimalBuild('sheep');
 }finally{atelierAnimalSurface=original;}
 const shared=new THREE.Group();
 shared.name='Clover · organic starter sheep';
 const makePivot=(name,at)=>{
  const p=new THREE.Group();p.name=name;p.position.set(...at);
  shared.add(p);return p;
 };
 const legs=[
  makePivot('stLeg0',[-.34,1.04,-.68]),
  makePivot('stLeg1',[.34,1.04,-.68]),
  makePivot('stLeg2',[-.34,1.10,.49]),
  makePivot('stLeg3',[.34,1.10,.49])
 ];
 const head=makePivot('stHead',[0,1.45,.86]);
 const tail=makePivot('stTail',[0,1.29,-.99]);
 const body=new THREE.Group();body.name='st127FleeceBody';shared.add(body);
 for(const part of data.parts){
  const d=part.topologyMesh;
  if(!d?.positions?.length||!d.indices?.length)continue;
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(d.positions,3));
  if(d.uvs?.length)geometry.setAttribute('uv',new THREE.Float32BufferAttribute(d.uvs,2));
  geometry.setIndex(d.indices);
  geometry.computeVertexNormals();
  const mat=new THREE.MeshStandardMaterial({
   color:part.color,roughness:part.organicSurface.region==='eye'?.23:.91,
   metalness:0,side:THREE.DoubleSide
  });
  const partMesh=new THREE.Mesh(geometry,mat);
  partMesh.name=part.name;
  partMesh.castShadow=true;partMesh.receiveShadow=true;
  const match=/^(Fore|Hind) (left|right)/.exec(part.name);
  if(match){
   const i=(match[1]==='Fore'?2:0)+(match[2]==='right'?1:0);
   const pivot=legs[i];
   partMesh.position.sub(pivot.position);
   pivot.add(partMesh);
  }else if(/^(Face |Left ear|Right ear|Left eye|Right eye|Nose |Mouth )/.test(part.name)){
   partMesh.position.sub(head.position);head.add(partMesh);
  }else if(/^Tail /.test(part.name)){
   partMesh.position.sub(tail.position);tail.add(partMesh);
  }else{body.add(partMesh);}
 }
 // Original Model Atelier is approx 2.1 world metres high; gameplay sheep
 // keeps the existing visual footprint and collision radius unchanged.
 shared.scale.setScalar(.53);
 st127SheepPrototype=shared;
 return shared;
}
const st127VisualBase=stMakeVisual;
stMakeVisual=function(type){
 const visual=st127VisualBase(type);
 if(type!=='st-sheep')return visual;
 try{
  const prototype=st127BuildOrganicPrototype();
  if(!prototype)return visual;
  // Retain original Sheep Tag actor/pivots and scene serialization; hide
  // only the outdated geometry, so legacy editor/capture rules remain valid.
  for(const child of visual.children)child.visible=false;
  const rig=prototype.clone(true);
  rig.visible=true;rig.userData.st127Organic=true;
  // Set the organic position independently: native scene keeps actor root.
  visual.add(rig);
  // No Object3D references in userData: authored save JSON stays acyclic.
  rig.userData.st127OrganicSource='model-atelier:Clover · Meadow Sheep';
 }catch(error){
  st127SheepModelError=String(error?.message||error);
  // Preserve a functioning, visible old sheep if device can't create model.
 }
 return visual;
};
// Animate only the rendered mesh; movement, hitboxes, routing, and sheep
// position always remain with the native physics/session code.
const st127AfterUpdateBase=stArchiveAfterUpdate;
stArchiveAfterUpdate=function(session,dt,t){
 st127AfterUpdateBase(session,dt,t);
 if(!session?.units||!Number.isFinite(session.elapsed))return;
 for(const unit of session.units){
  if(unit.kind!=='sheep'||unit.captured||unit.isIllusion)continue;
  const rig=unit.actor?.getObjectByName?.('Clover · organic starter sheep');
  if(!rig)continue;
  // native stLeg pivots have already received the real distance-based trot.
  // Pounce is animation-only and never teleports or changes pathfinding.
  const moving=(unit.walkBlend||0)>.32;
  const restricted=!!(unit.archiveOnUpper||unit.archiveFalling||
    unit.order?.action==='build'||unit.order?.action==='construct');
  if(!Number.isFinite(unit.st127NextPounce)){
   unit.st127Seed=st127Hash(unit.id||unit.name);
   unit.st127NextPounce=session.elapsed+6+unit.st127Seed*9;
  }
  if(!Number.isFinite(unit.st127PounceAt))unit.st127PounceAt=-Infinity;
  if(moving&&!restricted&&session.elapsed>=unit.st127NextPounce){
   const gapHash=st127Hash((unit.id||'sheep')+Math.floor(session.elapsed/2));
   unit.st127PounceAt=session.elapsed;
   unit.st127NextPounce=session.elapsed+8+gapHash*11;
   unit.st127PounceDirection=gapHash>.5?1:-1;
  }
  const phase=(session.elapsed-unit.st127PounceAt)/.57;
  const leap=phase>=0&&phase<1&&!restricted?Math.sin(Math.PI*phase):0;
  const bounce=moving&&!restricted?.023*Math.sin((unit.walkDistance||0)*17+unit.phase):0;
  // root local visual offset: physically harmless, no change to unit.pos.
  rig.position.set(leap*.042*(unit.st127PounceDirection||1),Math.max(0,bounce)+leap*.13,0);
  rig.rotation.set(leap*.095,leap*.13*(unit.st127PounceDirection||1),leap*.11*(unit.st127PounceDirection||1));
  const earHead=rig.getObjectByName('stHead');
  if(earHead)earHead.rotation.x+=Math.sin(session.elapsed*2.2+unit.phase)*.025+leap*.14;
 }
};
