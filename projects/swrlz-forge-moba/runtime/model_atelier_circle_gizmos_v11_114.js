// §E v11.114 — direct-manipulation circular-cut gizmos on Android and desktop.
// Optional Radius / Depth viewport modes reuse the native hand-placed cut.
// The viewport guides are disposable, editor-only geometry; only Apply uses
// checkpoint(). A drag updates numeric controls and reconstructs Preview on up.
let atelierPrecisionGizmoGroup=null,atelierPrecisionGizmoDrag=null,
    atelierPrecisionGizmoFrame=0,atelierPrecisionGizmoPick=null;
const atelierPrecisionGizmoColors={radius:0xffd36a,depth:0xbe91ff};
function atelierPrecisionGizmoEnabled(mode){
 return document.getElementById('modelAtelierBoreGizmo'+mode)
  ?.getAttribute('aria-pressed')==='true';
}
function atelierPrecisionGizmoDispose(){
 const group=atelierPrecisionGizmoGroup;
 atelierPrecisionGizmoGroup=null;atelierPrecisionGizmoPick=null;
 if(!group)return;
 group.parent?.remove(group);
 group.traverse(o=>{
  o.geometry?.dispose?.();
  const mats=Array.isArray(o.material)?o.material:(o.material?[o.material]:[]);
  mats.forEach(m=>m?.dispose?.());
 });
 atelierHDDirty=true;
}
function atelierPrecisionGizmoQueue(){
 if(atelierPrecisionGizmoFrame)return;
 atelierPrecisionGizmoFrame=requestAnimationFrame(()=>{
  atelierPrecisionGizmoFrame=0;
  try{atelierPrecisionGizmoDraw();}
  catch(error){atelierPrecisionGizmoDispose();
   console.warn('Safe precision-cut gizmo refresh failed',error);}
 });
}
function atelierPrecisionGizmoContext(){
 if(!world||!camera||!renderer||!modelRoot)return null;
 if(!atelierPrecisionGizmoEnabled('Radius')&&!atelierPrecisionGizmoEnabled('Depth'))
  return null;
 const part=partById(selection);
 if(!part||!(['sphere','box','cylinder'].includes(part.kind)||
   part.kind==='topologyMesh'&&part.roundHolePlan))return null;
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===part.id);
 if(!mesh)return null;
 const which=document.getElementById('modelAtelierBoreWhich')?.value||'new';
 const existing=part.roundHolePlan;
 let plan=existing;
 const hit=atelierSculptHit?.partId===part.id?atelierSculptHit:null;
 if(!plan){
  if(!hit)return null;
  mesh.geometry.computeBoundingSphere();
  const center=mesh.geometry.boundingSphere.center.toArray();
  const initial=new THREE.Vector3(...hit.axis);
  if(part.kind==='sphere')
   initial.fromArray(hit.center).sub(new THREE.Vector3(...center));
  if(part.kind==='box'){
   const xyz=initial.toArray(),i=xyz.map(Math.abs).indexOf(Math.max(...xyz.map(Math.abs)));
   initial.set(i===0?Math.sign(xyz[0]):0,i===1?Math.sign(xyz[1]):0,
      i===2?Math.sign(xyz[2]):0);
  }
  if(part.kind==='cylinder'&&Math.abs(initial.y)<.86)return null;
  if(initial.lengthSq()<1e-10)return null;
  plan={surface:part.kind,radius:part.kind==='sphere'?
   mesh.geometry.boundingSphere.radius:part.kind==='box'?.5:1,
   center,axis:initial.normalize().toArray(),
   halfU:.5,halfV:.5,halfDepth:.5,holes:[]};
 }
 const editing=which.startsWith('hole-'),index=editing?Number(which.slice(5)):-1;
 if(editing&&!plan.holes[index])return null;
 const relocate=editing&&document.getElementById('modelAtelierBoreRelocate')?.checked;
 const pos=editing&&!relocate?
  {x:plan.holes[index].x,y:plan.holes[index].y}:
  hit?atelierBoreCoordinates(plan,hit.center):null;
 if(!pos)return null;
 const radius=Number(document.getElementById('modelAtelierBoreRadius')?.value);
 const depth=Number(document.getElementById('modelAtelierBoreDepth')?.value);
 const cap=Number(document.getElementById('modelAtelierBoreCap')?.value);
 if(![radius,depth,cap].every(Number.isFinite)||radius<=0)return null;
 const axis=new THREE.Vector3(...plan.axis).normalize();
 const helper=Math.abs(axis.y)<.9?new THREE.Vector3(0,1,0):new THREE.Vector3(1,0,0);
 const u=new THREE.Vector3().crossVectors(helper,axis).normalize();
 const v=new THREE.Vector3().crossVectors(axis,u).normalize();
 const center=new THREE.Vector3(...plan.center);
 const xyz=(x,y,z)=>center.clone().addScaledVector(u,x)
   .addScaledVector(v,y).addScaledVector(axis,z);
 const zAt=(x,y)=>plan.surface==='sphere'?
  Math.sqrt(Math.max(0,plan.radius**2-x*x-y*y)):plan.halfDepth;
 const z=zAt(pos.x,pos.y);
 mesh.updateMatrixWorld(true);
 return {part,mesh,plan,pos,radius,depth,cap,center,axis,u,v,xyz,zAt,z};
}
function atelierPrecisionGizmoDraw(){
 atelierPrecisionGizmoDispose();
 const ctx=atelierPrecisionGizmoContext();
 if(!ctx)return;
 const group=new THREE.Group();
 group.name='Precision cut · temporary viewport radius/depth gizmos';
 group.userData.atelierHelper=true;
 group.userData.precisionPreviewOnly=true;
 group.matrixAutoUpdate=false;
 group.matrix.copy(ctx.mesh.matrixWorld);
 world.add(group);
 const line=(positions,color,opacity=1)=>{
  const geometry=new THREE.BufferGeometry().setFromPoints(positions);
  const material=new THREE.LineBasicMaterial({
   color,depthTest:false,depthWrite:false,transparent:true,opacity});
  const display=new THREE.Line(geometry,material);
  display.renderOrder=998;display.userData.atelierHelper=true;
  group.add(display);
  return display;
 };
 const grip=(at,color,size)=>{
  const bead=new THREE.Mesh(
   new THREE.SphereGeometry(size,12,9),
   new THREE.MeshBasicMaterial({color,depthTest:false,depthWrite:false}));
  bead.position.copy(at);bead.renderOrder=1000;
  bead.userData.atelierHelper=true;
  group.add(bead);
 };
 const {pos,radius,depth,z,zAt,xyz}=ctx;
 let radiusPoints=[];
 const count=96;
 for(let k=0;k<=count;k++){
  const a=k*2*Math.PI/count,x=pos.x+radius*Math.cos(a),
   y=pos.y+radius*Math.sin(a);
  radiusPoints.push(xyz(x,y,zAt(x,y)+.005));
 }
 const zero=xyz(pos.x,pos.y,z+.02);
 const atRadius=xyz(pos.x+radius,pos.y,zAt(pos.x+radius,pos.y)+.012);
 const inward=xyz(pos.x,pos.y,z-depth);
 const worldPoint=q=>group.localToWorld(q.clone());
 if(atelierPrecisionGizmoEnabled('Radius')){
  line(radiusPoints,atelierPrecisionGizmoColors.radius,.97);
  grip(atRadius,atelierPrecisionGizmoColors.radius,Math.max(radius*.15,.025));
 }
 if(atelierPrecisionGizmoEnabled('Depth')){
  line([zero,inward],atelierPrecisionGizmoColors.depth,.93);
  const guide=new THREE.Line(new THREE.BufferGeometry().setFromPoints(
    [xyz(pos.x-radius*.16,pos.y,z-depth),xyz(pos.x+radius*.16,pos.y,z-depth)]),
   new THREE.LineBasicMaterial({color:atelierPrecisionGizmoColors.depth,
    depthTest:false,depthWrite:false}));
  guide.userData.atelierHelper=true;guide.renderOrder=999;group.add(guide);
  grip(inward,atelierPrecisionGizmoColors.depth,Math.max(radius*.15,.025));
 }
 group.updateMatrixWorld(true);
 atelierPrecisionGizmoGroup=group;
 atelierPrecisionGizmoPick={
  ctx,radiusPoints:radiusPoints.map(worldPoint),
  center:worldPoint(zero),radiusGrip:worldPoint(atRadius),
  depthGrip:worldPoint(inward)
 };
 atelierHDDirty=true;
}
function atelierPrecisionGizmoScreen(p){
 if(!renderer||!camera)return null;
 camera.updateMatrixWorld(true);
 const n=p.clone().project(camera);
 if(n.z<-.99||n.z>1)return null;
 const rect=renderer.domElement.getBoundingClientRect();
 return {x:rect.left+(n.x+1)*rect.width/2,
  y:rect.top+(1-n.y)*rect.height/2};
}
function atelierPrecisionGizmoHit(event){
 const pick=atelierPrecisionGizmoPick;
 if(!pick)return null;
 const distance=p=>p?Math.hypot(event.clientX-p.x,event.clientY-p.y):Infinity;
 const threshold=event.pointerType==='touch'?36:24;
 let radiusCandidate=null;
 if(atelierPrecisionGizmoEnabled('Radius')){
  for(const worldPoint of pick.radiusPoints){
   const point=atelierPrecisionGizmoScreen(worldPoint),d=distance(point);
   if(d<=threshold&&(!radiusCandidate||d<radiusCandidate.d))
    radiusCandidate={mode:'Radius',point,d};
  }
 }
 const depthPoint=atelierPrecisionGizmoScreen(pick.depthGrip);
 const depthCandidate=atelierPrecisionGizmoEnabled('Depth')&&
   distance(depthPoint)<=threshold?{mode:'Depth',point:depthPoint,d:distance(depthPoint)}:null;
 if(depthCandidate&&(!radiusCandidate||depthCandidate.d<radiusCandidate.d+7))
  return depthCandidate;
 return radiusCandidate;
}
function atelierPrecisionGizmoDown(event){
 if(atelierPrecisionGizmoDrag||!renderer||event.target!==renderer.domElement||
   event.button!==0||event.isPrimary===false||atelierSculptArmed)return;
 const selected=atelierPrecisionGizmoHit(event);
 if(!selected)return;
 const pick=atelierPrecisionGizmoPick;
 const c=atelierPrecisionGizmoScreen(pick.center);
 const mode=selected.mode,pt=selected.point;
 const vec=new THREE.Vector2(pt.x-c.x,pt.y-c.y);
 // Radius: drag outward from any point on the amber footprint.
 // Depth: track screen-projected inward axis; when front-facing it has
 // near-zero projection, so drag DOWN to deepen instead of freezing.
 if(mode==='Depth'&&vec.length()<10)vec.set(0,1);
 if(vec.length()<3)vec.set(1,0);
 const unit=vec.normalize();
 const scaled=mode==='Radius'?
  pick.ctx.radius/Math.max(8,Math.hypot(pt.x-c.x,pt.y-c.y)):
  pick.ctx.depth/Math.max(14,Math.hypot(pt.x-c.x,pt.y-c.y));
 const pixelToUnit=Math.min(.035,Math.max(.0004,scaled));
 atelierPrecisionGizmoDrag={
  id:event.pointerId,mode,startX:event.clientX,startY:event.clientY,
  unit,pixelToUnit,startValue:mode==='Radius'?pick.ctx.radius:pick.ctx.depth,
  partId:pick.ctx.part.id,changed:false};
 try{renderer.domElement.setPointerCapture?.(event.pointerId)}catch(_){}
 event.preventDefault();event.stopImmediatePropagation();
}
function atelierPrecisionGizmoMove(event){
 const drag=atelierPrecisionGizmoDrag;
 if(!drag||event.pointerId!==drag.id)return;
 const ctx=atelierPrecisionGizmoContext();
 if(!ctx||ctx.part.id!==drag.partId){
  atelierPrecisionGizmoDrag=null;
  atelierPrecisionGizmoQueue();
  return;
 }
 const dx=event.clientX-drag.startX,dy=event.clientY-drag.startY;
 const pixels=dx*drag.unit.x+dy*drag.unit.y;
 let value=drag.startValue+pixels*drag.pixelToUnit;
 if(drag.mode==='Radius'){
  value=Math.max(ctx.plan.radius*.025,
   Math.min(ctx.plan.radius*.29,value));
 }else{
  const floor=ctx.radius*Math.max(0,ctx.cap)+.01;
  const max=ctx.plan.surface==='sphere'?
   ctx.plan.radius*.82:ctx.plan.halfDepth*1.8;
  value=Math.max(floor,Math.min(max,value));
 }
 const field=document.getElementById('modelAtelierBore'+drag.mode);
 if(!field)return;
 if(Math.abs(value-Number(field.value))>.0001){
  if(!drag.changed&&atelierPrecisionCircleDraft){
   atelierPrecisionCircleClear();
  }
  drag.changed=true;
  field.value=value.toFixed(4);
  const output=document.getElementById('modelAtelierBoreInfo');
  if(output)output.textContent=drag.mode+' '+value.toFixed(3)+
   ' · dragging the viewport handle; Apply has not changed the model.';
  atelierPrecisionGizmoQueue();
 }
 event.preventDefault();event.stopImmediatePropagation();
}
function atelierPrecisionGizmoUp(event){
 const drag=atelierPrecisionGizmoDrag;
 if(!drag||event?.pointerId!==drag.id)return;
 atelierPrecisionGizmoDrag=null;
 try{renderer?.domElement?.releasePointerCapture?.(drag.id)}catch(_){}
 if(drag.changed){
  // Rebuild full validated candidate ONCE after touch release.
  const preview=document.getElementById('modelAtelierBorePreview');
  preview?.click();
 }
 atelierPrecisionGizmoQueue();
 event?.preventDefault?.();event?.stopImmediatePropagation?.();
}
function atelierPrecisionGizmoInstall(){
 const panel=document.getElementById('modelAtelierBoreTools');
 if(!panel||document.getElementById('modelAtelierBoreGizmoRadius'))return;
 const controls=document.createElement('div');
 controls.className='atelier-precision-gizmo-controls';
 controls.setAttribute('role','group');
 controls.setAttribute('aria-label','Interactive viewport handles for precision circle cutting');
 controls.innerHTML=
  '<strong>Adjust directly on the model</strong>'+
  '<div class="atelier-precision-gizmo-row">'+
  '<button type="button" id="modelAtelierBoreGizmoRadius" aria-pressed="false">🟡 Radius handle</button>'+
  '<button type="button" id="modelAtelierBoreGizmoDepth" aria-pressed="false">🟣 Depth handle</button></div>'+
  '<small>Toggle a handle, then drag its colored ring or grip in the viewport. Numbers update automatically. A validated mesh preview refreshes when you release. Neither drag nor preview saves a cut.</small>';
 const inputs=document.getElementById('modelAtelierBoreRadius');
 inputs?.closest('.atelier-pair')?.insertAdjacentElement('afterend',controls);
 for(const mode of ['Radius','Depth']){
  const button=document.getElementById('modelAtelierBoreGizmo'+mode);
  button?.addEventListener('click',()=>{
   const enabled=button.getAttribute('aria-pressed')!=='true';
   button.setAttribute('aria-pressed',String(enabled));
   if(enabled&&!atelierPrecisionGizmoContext()){
    const note=document.getElementById('modelAtelierBoreInfo');
    if(note)note.textContent='Pick a center on the mesh, or select a saved cut, to display the viewport '+mode.toLowerCase()+' gizmo.';
   }
   atelierPrecisionGizmoQueue();
  });
 }
 const schedule=()=>atelierPrecisionGizmoQueue();
 for(const key of ['Radius','Depth','Cap','Which','Relocate']){
  const el=document.getElementById('modelAtelierBore'+key);
  el?.addEventListener('input',schedule);
  el?.addEventListener('change',schedule);
 }
 for(const key of ['Preview','Apply','Hide']){
  document.getElementById('modelAtelierBore'+key)?.addEventListener('click',schedule);
 }
 document.getElementById('SculptBrushPick')?.addEventListener('click',schedule);
 document.addEventListener('pointerdown',atelierPrecisionGizmoDown,true);
 document.addEventListener('pointermove',atelierPrecisionGizmoMove,true);
 document.addEventListener('pointerup',atelierPrecisionGizmoUp,true);
 document.addEventListener('pointercancel',atelierPrecisionGizmoUp,true);
 window.addEventListener('resize',schedule);
 atelierPrecisionGizmoQueue();
}
