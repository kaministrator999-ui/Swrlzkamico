/* SE513_RIG_WEIGHT_STUDIO_START
   Real per-vertex skin weight edits, on the existing SkinnedMesh and
   current project's topology. The brush is armed explicitly so ordinary
   joint selection, orbit, and rest-joint dragging remain untouched. */
const se513WeightStudio=(()=>{
 'use strict';
 const $=id=>panel?.querySelector('#'+id);
 let armed=false,mode='add',radius=.18,strength=.16,drag=null,installedPanel=null;
 const ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
 const posedPoint=new THREE.Vector3();
 const activeRig=()=>panel&&!panel.hidden&&panel.dataset.se496Studio==='rig'&&
  se220RigAvailable()&&se220Rig()?.schema==='swyrl-cloth-skin-v1';
 function target(){
  if(!activeRig()||!modelRoot)return null;
  const rig=se220Rig(),part=partById(rig.targetPartId);
  const mesh=modelRoot.children.find(o=>o.isSkinnedMesh&&o.userData?.atelierId===rig.targetPartId);
  const positions=part?.topologyMesh?.positions;
  const g=mesh?.geometry,pi=g?.getAttribute('position'),ii=g?.getAttribute('skinIndex'),ww=g?.getAttribute('skinWeight');
  if(!part||!mesh||!Array.isArray(positions)||!pi||!ii||!ww||
   positions.length!==pi.count*3||pi.count!==ii.count||pi.count!==ww.count)return null;
  return {rig,part,mesh,positions,indices:ii,weights:ww,vertices:pi.count};
 }
 function info(text,warning=false){
  const n=$('se513PaintStatus');if(n)n.textContent=text;
  if(warning)status(text,true);
 }
 function arm(next){
  if(drag)cancel();
  armed=!!next;
  const btn=$('se513PaintArm');
  if(btn){btn.textContent=armed?'Stop painting weights':'Paint selected bone weights';btn.setAttribute('aria-pressed',String(armed));}
  info(armed?'Trigger/tap and drag on the mesh to change this bone\'s actual skin weights. Camera and bone picking return when stopped.':
    'Weight brush off. Joint selection and the camera are available.');
 }
 function install(){
  const host=$('se500BoneControls');
  if(!host||$('se513WeightStudio'))return;
  const section=document.createElement('section');section.id='se513WeightStudio';
  section.innerHTML='<strong>Editable bone influence</strong>'+
   '<small>Changes actual four-bone skinning, not just vertex colors. Works on any mesh with matching editable topology.</small>'+
   '<label>Brush radius <output id="se513RadiusValue">0.18</output>'+
   '<input id="se513PaintRadius" type="range" min="0.02" max="1.5" step="0.02" value="0.18"></label>'+
   '<label>Weight step <output id="se513StrengthValue">16%</output>'+
   '<input id="se513PaintStrength" type="range" min="0.01" max="0.5" step="0.01" value="0.16"></label>'+
   '<div class="se513WeightActions"><button type="button" id="se513PaintMode">Mode: Add influence</button>'+
   '<button type="button" id="se513PaintArm" aria-pressed="false">Paint selected bone weights</button></div>'+
   '<small id="se513PaintStatus" aria-live="polite">Paint while in Rigging mode. Undo uses native model history.</small>';
  host.insertAdjacentElement('afterend',section);
  $('se513PaintRadius').addEventListener('input',e=>{radius=Number(e.target.value);$('se513RadiusValue').textContent=radius.toFixed(2);});
  $('se513PaintStrength').addEventListener('input',e=>{strength=Number(e.target.value);$('se513StrengthValue').textContent=Math.round(strength*100)+'%';});
  $('se513PaintMode').addEventListener('click',()=>{if(drag)cancel();
   mode=mode==='add'?'erase':'add';$('se513PaintMode').textContent=mode==='add'?'Mode: Add influence':'Mode: Erase influence';
  });
  $('se513PaintArm').addEventListener('click',()=>arm(!armed));
 }
 function pick(event,mesh){
  const rect=renderer?.domElement?.getBoundingClientRect();
  if(!rect?.width||!rect?.height||!camera)return null;
  const x=event.clientX,y=event.clientY;
  if(x<rect.left||x>rect.right||y<rect.top||y>rect.bottom)return null;
  ndc.set(2*(x-rect.left)/rect.width-1,1-2*(y-rect.top)/rect.height);
  camera.updateMatrixWorld(true);mesh.updateWorldMatrix(true,false);
  ray.setFromCamera(ndc,camera);
  const hit=ray.intersectObject(mesh,false)[0];
  return hit?.point?.clone?.().applyMatrix4(mesh.matrixWorld.clone().invert())||null;
 }
 function gpu(session){
  const mesh=session.mesh,idx=mesh.geometry.getAttribute('skinIndex'),w=mesh.geometry.getAttribute('skinWeight');
  if(!idx||!w||idx.count!==session.vertices||w.count!==session.vertices)return false;
  const skin=session.working;
  for(let i=0;i<session.vertices;i++){
   const p=i*4;
   idx.setXYZW(i,skin.indices[p],skin.indices[p+1],skin.indices[p+2],skin.indices[p+3]);
   w.setXYZW(i,skin.weights[p],skin.weights[p+1],skin.weights[p+2],skin.weights[p+3]);
  }
  idx.needsUpdate=true;w.needsUpdate=true;
  mesh.skeleton?.update();
  return true;
 }
 function apply(event){
  const session=drag;if(!session)return false;
  if(modelRoot!==session.root||se220Rig()!==session.rig||
    target()?.mesh!==session.mesh||se220Joint!==session.boneId){cancel();return false;}
  const point=pick(event,session.mesh);if(!point)return false;
  if(session.last&&point.distanceToSquared(session.last)<Math.pow(radius*.2,2))return true;
  session.last=point.clone();
  const pose=(i)=>{
   const v=posedPoint.fromBufferAttribute(session.mesh.geometry.getAttribute('position'),i);
   if(typeof session.mesh.applyBoneTransform==='function')session.mesh.applyBoneTransform(i,v);
   return [v.x,v.y,v.z];
  };
  const change=(mode==='add'?1:-1)*strength;
  const result=se513SkinMath.region(session.positions,session.working.indices,session.working.weights,
   point.toArray(),radius,session.boneIndex,change,session.rig.bones.length,pose);
  if(!result){cancel();info('Weight edit rejected: invalid skin data or vertex selection.',true);return false;}
  if(result.changed){
   session.working={schema:'swyrl-explicit-skin-v1',indices:result.indices,weights:result.weights};
   session.changed+=result.changed;
   if(!gpu(session)){cancel();return false;}
  }
  info('Painting '+session.boneId+' · '+session.changed+' influenced vertex updates · release to save.');
  return true;
 }
 function start(event){
  if(!armed||drag||!activeRig()||event.target!==renderer?.domElement||
    (event.button!==undefined&&event.button!==0)||event.isPrimary===false)return;
  const data=target(),boneIndex=data?.rig.bones.findIndex(b=>b.id===se220Joint);
  if(!data||boneIndex<0){info('Choose an editable rigged mesh and a bone first.',true);return;}
  const p=pick(event,data.mesh);if(!p)return;
  const indices=[],weights=[];
  for(let i=0;i<data.vertices;i++){
   indices.push(data.indices.getX(i),data.indices.getY(i),data.indices.getZ(i),data.indices.getW(i));
   weights.push(data.weights.getX(i),data.weights.getY(i),data.weights.getZ(i),data.weights.getW(i));
  }
  const initial={schema:'swyrl-explicit-skin-v1',indices,weights};
  if(!se513SkinMath.validSkin(initial,data.vertices,data.rig.bones.length)){
   info('Skin influences are invalid. Refusing to paint or overwrite this mesh.',true);return;
  }
  drag={pointer:event.pointerId,root:modelRoot,rig:data.rig,part:data.part,mesh:data.mesh,
   boneId:se220Joint,boneIndex,vertices:data.vertices,positions:data.positions,initial,
   working:{schema:initial.schema,indices:indices.slice(),weights:weights.slice()},last:null,changed:0};
  event.preventDefault();event.stopImmediatePropagation();
  try{renderer.domElement.setPointerCapture?.(event.pointerId);}catch(_){}
  apply(event);
 }
 function move(event){
  if(!drag||event.pointerId!==drag.pointer)return;
  event.preventDefault();event.stopImmediatePropagation();
  apply(event);
 }
 function finish(event){
  if(!drag||event.pointerId!==drag.pointer)return;
  event.preventDefault();event.stopImmediatePropagation();
  try{renderer?.domElement?.releasePointerCapture?.(event.pointerId);}catch(_){}
  const done=drag;drag=null;
  if(!done.changed)return;
  if(!se513SkinMath.validSkin(done.working,done.vertices,done.rig.bones.length)||
      modelRoot!==done.root||se220Rig()!==done.rig||partById(done.part.id)!==done.part){
   gpu({...done,working:done.initial});
   info('Weight edit canceled because the rig or topology changed.',true);return;
  }
  // Save only after successful preview, exactly one native undo step per stroke.
  checkpoint();
  done.part.skinning={schema:'swyrl-explicit-skin-v1',
   indices:done.working.indices.slice(),weights:done.working.weights.slice()};
  signalEdited();se500RigEdit.refresh();
  $('se500RefreshVertices')?.click();
  info('Saved '+done.changed+' vertex updates to the current project. Undo restores the previous weights.');
 }
 function cancel(){
  const old=drag;drag=null;
  if(old){try{renderer?.domElement?.releasePointerCapture?.(old.pointer);}catch(_){}
   if(old.mesh.parent)gpu({...old,working:old.initial});
  }
  info('Weight brush canceled; no project data changed.');
 }
 function attach(){
  if(!panel||panel===installedPanel)return;
  installedPanel=panel;
  panel.addEventListener('pointerdown',start,true);
  panel.addEventListener('pointermove',move,true);
  panel.addEventListener('pointerup',finish,true);
  panel.addEventListener('pointercancel',cancel,true);
 }
 const previousRefresh=se220RigRefresh;
 se220RigRefresh=function(...args){
  const out=previousRefresh.apply(this,args);
  if(activeRig()){install();attach();}
  else if(armed)arm(false);
  return out;
 };
 const previousOpen=open;
 open=function(...args){const out=previousOpen.apply(this,args);if(out!==false){install();attach();}return out;};
 const previousClose=close;
 close=function(...args){cancel();arm(false);return previousClose.apply(this,args);};
 document.addEventListener('keydown',event=>{
  if(drag&&event.key==='Escape'){cancel();event.preventDefault();event.stopImmediatePropagation();}
 },true);
 return Object.freeze({install,arm,cancel,inspect:()=>({armed,mode,radius,strength,
  active:!!drag,updates:drag?.changed||0})});
})();
window.SWYRL_ENGINE_RIG_WEIGHT_STUDIO_513=se513WeightStudio;
/* SE513_RIG_WEIGHT_STUDIO_END */
