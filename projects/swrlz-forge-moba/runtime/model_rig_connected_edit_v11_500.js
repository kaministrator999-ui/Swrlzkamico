/* §E v11.500 — select bone, see its real skin-weighted vertices, drag
   connected rest joints with locked lengths. One existing GPU skinning scene. */
const se500RigEdit=(()=>{
 'use strict';
 const $=id=>panel?.querySelector('#'+id);
 const validRig=()=>se220RigAvailable()&&se220Rig()?.schema==='swyrl-cloth-skin-v1';
 const inRig=()=>panel&&!panel.hidden&&panel.dataset.se496Studio==='rig'&&validRig();
 const math=se500RestMath;
 let stage=null,drag=null,overlay=null,history=[],lastRig=null;
 let threshold=.12,showWeights=true,lockLength=true;
 const ray=new THREE.Raycaster(),xy=new THREE.Vector2();
 const point=new THREE.Vector3(),worldPos=new THREE.Vector3();
 function meshList(){
  if(!modelRoot||!validRig())return [];
  const target=se220Rig().targetPartId;
  return modelRoot.children.filter(o=>o.isSkinnedMesh&&o.userData?.atelierId===target&&
   o.geometry?.getAttribute('skinIndex')&&o.geometry?.getAttribute('skinWeight'));
 }
 function forgetOverlay(){
  if(overlay?.root?.parent)overlay.root.parent.remove(overlay.root);
  overlay?.points?.geometry?.dispose();
  overlay?.points?.material?.dispose();
  overlay=null;
 }
 function collectWeights(){
  const rig=se220Rig(),id=se220Joint,boneIndex=rig.bones.findIndex(b=>b.id===id);
  if(boneIndex<0)return {entries:[],total:0};
  const entries=[];
  for(const mesh of meshList()){
   const g=mesh.geometry,p=g.getAttribute('position'),idx=g.getAttribute('skinIndex'),w=g.getAttribute('skinWeight');
   if(!p||!idx||!w||p.count!==idx.count||p.count!==w.count)continue;
   for(let i=0;i<p.count;i++){
    const indices=[idx.getX(i),idx.getY(i),idx.getZ(i),idx.getW(i)];
    const weights=[w.getX(i),w.getY(i),w.getZ(i),w.getW(i)];
    const value=math.weightOf(indices,weights,boneIndex);
    if(value>=threshold)entries.push({mesh,index:i,weight:value});
   }
  }
  return {entries,total:entries.length};
 }
 function refreshOverlay(force=false){
  const enabled=inRig()&&showWeights;
  if(!enabled){if(overlay)overlay.root.visible=false;return;}
   // Explicitly compare identity too, not just stringified model references.
  if(force||!overlay||overlay.rig!==se220Rig()||overlay.bone!==se220Joint||
   overlay.threshold!==threshold||overlay.scene!==modelRoot){
   forgetOverlay();
   const {entries,total}=collectWeights();
   const max=3500,step=Math.max(1,Math.ceil(entries.length/max));
   const samples=entries.filter((v,i)=>i%step===0).slice(0,max);
   const g=new THREE.BufferGeometry();
   g.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(samples.length*3),3));
   const colors=new Float32Array(samples.length*3);
   for(let i=0;i<samples.length;i++){
    const strength=samples[i].weight;
    colors[i*3]=.18+.82*strength;
    colors[i*3+1]=.94-.65*strength;
    colors[i*3+2]=1-.35*strength;
   }
   g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
   const material=new THREE.PointsMaterial({size:6.5,sizeAttenuation:false,vertexColors:true,
    opacity:.96,transparent:true,depthTest:false,depthWrite:false});
   const points=new THREE.Points(g,material);points.name='Weighted mesh vertices';
   points.renderOrder=442;points.frustumCulled=false;
   points.raycast=()=>{}; // never steal bone picking
   const root=new THREE.Group();root.name='§E Selected Bone Weight Preview';
   root.userData.se500Weights=true;root.add(points);modelRoot.add(root);
   overlay={root,points,samples,total,bone:se220Joint,rig:se220Rig(),threshold,scene:modelRoot};
  }
  overlay.root.visible=true;
  overlay.scene.updateMatrixWorld(true);
  const toModel=new THREE.Matrix4().copy(modelRoot.matrixWorld).invert();
  const positions=overlay.points.geometry.getAttribute('position');
  for(let i=0;i<overlay.samples.length;i++){
   const item=overlay.samples[i],mesh=item.mesh;
   const vertex=point.fromBufferAttribute(mesh.geometry.getAttribute('position'),item.index);
   if(typeof mesh.applyBoneTransform==='function')mesh.applyBoneTransform(item.index,vertex);
   vertex.applyMatrix4(mesh.matrixWorld).applyMatrix4(toModel);
   positions.setXYZ(i,vertex.x,vertex.y,vertex.z);
  }
  positions.needsUpdate=true;
  overlay.points.geometry.computeBoundingSphere();
  const counter=$('se500WeightsCount');
  if(counter)counter.textContent=overlay.total+' influenced vertices'+
   (overlay.samples.length<overlay.total?' · showing '+overlay.samples.length:'')+
   ' at ≥'+Math.round(threshold*100)+'% weight';
 }
 function refreshSelected(){
  const r=se220Rig();if(!r)return;
  if(lastRig!==r){history=[];lastRig=r;forgetOverlay();}
  const undo=$('se500UndoRest');if(undo)undo.disabled=!history.length;
  const name=r.bones.find(b=>b.id===se220Joint)?.label||se220Joint;
  const label=$('se500Selected');if(label)label.textContent='Selected: '+name;
  for(let i=0;i<3;i++){
   const v=$('se496Rest'+i),rest=r.bones.find(b=>b.id===se220Joint)?.rest;
   if(v&&rest)v.value=rest[i].toFixed(3);
  }
  const info=$('se500MoveHelp');
  if(info)info.textContent=lockLength?
   'Drag a joint. Its segment length stays fixed and every child follows. Root moves the whole rig.':
   'Drag a joint to translate it and every child. The parent segment may change length.';
  refreshOverlay();
 }
 function install(){
  const native=se220R('Studio'),author=$('se496BoneAuthoring');
  if(!native||!author||$('se500BoneControls'))return;
  const block=document.createElement('section');block.id='se500BoneControls';
  block.innerHTML='<strong>Connected bone editing</strong>'+
   '<small id="se500Selected" aria-live="polite">Select a joint in the viewport</small>'+
   '<label class="se500-check"><input id="se500WeightsToggle" type="checkbox" checked> Show attached mesh vertices</label>'+
   '<label>Minimum bone influence <output id="se500ThresholdValue">12%</output>'+
   '<input id="se500Threshold" type="range" min="0.01" max="0.95" step="0.01" value="0.12"></label>'+
   '<small id="se500WeightsCount" aria-live="polite"></small>'+ 
   '<small>Color: cyan = light influence · pink = stronger influence</small>'+
   '<label class="se500-check"><input id="se500LockLength" type="checkbox" checked> Keep bone length (move connected chain)</label>'+
   '<div class="se500-actions"><button type="button" id="se500UndoRest">Undo bone placement</button>'+
   '<button type="button" id="se500RefreshVertices">Refresh weights</button></div>'+
   '<small id="se500MoveHelp"></small>';
  author.prepend(block);
  $('se500WeightsToggle').addEventListener('change',e=>{
   showWeights=e.target.checked;refreshOverlay(true);
  });
  $('se500Threshold').addEventListener('input',e=>{
   threshold=Math.max(.01,Math.min(.95,Number(e.target.value)||.12));
   $('se500ThresholdValue').textContent=Math.round(threshold*100)+'%';
   refreshOverlay(true);
  });
  $('se500LockLength').addEventListener('change',e=>{
   lockLength=e.target.checked;refreshSelected();
  });
  $('se500RefreshVertices').addEventListener('click',()=>refreshOverlay(true));
  $('se500UndoRest').addEventListener('click',undo);
  const joint=se220R('Joint');
  joint?.addEventListener('change',()=>queueMicrotask(()=>{refreshOverlay(true);refreshSelected();}));
  // Capture before the v11.496 single-joint input handler. Always move its
  // subtree instead of leaving children at their former world coordinates.
  for(let axis=0;axis<3;axis++){
   $('se496Rest'+axis)?.addEventListener('change',event=>{
    if(!inRig())return;
    event.stopImmediatePropagation();
    const b=se220Rig().bones.find(b=>b.id===se220Joint),v=Number(event.target.value);
    if(!b||!Number.isFinite(v))return;
    const target=b.rest.slice();target[axis]=v;
    const base=math.snapshot(se220Rig());
    if(!moveFromSnapshot(base,target,true))status('That joint position exceeds rig bounds.',true);
    else{
     history.push(base);if(history.length>20)history.shift();
     se220RigTouched('Moved connected bone chain. Save Project to retain placement.');
    }
    refreshSelected();
   },true);
  }
  refreshSelected();
 }
 function syncRestTransform(){
  const r=se220Rig();
  if(!r||!se220Bones||!se220Skeleton||!modelRoot)return;
  const map=new Map(r.bones.map(b=>[b.id,b]));
  for(const spec of r.bones){
   const bone=se220Bones[spec.id],parent=spec.parent?map.get(spec.parent):null;
   if(!bone)continue;
   const ref=parent?parent.rest:[0,0,0];
   bone.position.set(spec.rest[0]-ref[0],spec.rest[1]-ref[1],spec.rest[2]-ref[2]);
   bone.rotation.set(0,0,0);
  }
  modelRoot.updateMatrixWorld(true);
  se220Skeleton.calculateInverses();
  for(const mesh of modelRoot.children){
   if(!mesh.isSkinnedMesh)continue;
   mesh.updateMatrixWorld(true);
   mesh.bind(se220Skeleton,mesh.matrixWorld.clone());
  }
  // Always recompute inverse bind matrices at neutral; then restore pose.
  se220RigPose(r.pose);
 }
 function moveFromSnapshot(base,target,quiet=false){
  const r=se220Rig();
  if(!r||!base)return false;
  math.apply(r,base);
  const next=math.solve(r,se220Joint,target,lockLength);
  if(!next){syncRestTransform();return false;}
  math.apply(r,next);
  if(!se220RigValidate(r)){
   math.apply(r,base);syncRestTransform();return false;
  }
  syncRestTransform();
  if(!quiet)refreshSelected();
  return true;
 }
 function undo(){
  if(!inRig()||!history.length)return;
  const prior=history.pop(),rig=se220Rig();
  math.apply(rig,prior);syncRestTransform();
  se220RigTouched('Rest joint placement restored.');
  refreshOverlay(true);refreshSelected();
 }
 function selectable(event){
  if(!inRig()||!renderer?.domElement||!camera||event.button!==0)return null;
  const group=modelRoot?.children.find(o=>o.name==='§E Rig Controls');
  if(!group?.visible)return null;
  const rect=renderer.domElement.getBoundingClientRect();
  if(!rect.width||!rect.height)return null;
  const xp=event.clientX-rect.left,yp=event.clientY-rect.top;
  // A generous fingertip-sized 2D radius makes small skeleton pivots usable on phones.
  let best=null,score=Infinity;
  for(const bone of se220Rig().bones){
   const object=se220Bones?.[bone.id];if(!object)continue;
   const pos=object.getWorldPosition(worldPos).clone().project(camera);
   if(pos.z>1||pos.z< -1)continue;
   const px=(pos.x+1)*rect.width/2,py=(1-pos.y)*rect.height/2;
   const dist=Math.hypot(px-xp,py-yp);
   if(dist<(event.pointerType==='touch'?32:23)&&dist<score){
    score=dist;best=bone.id;
   }
  }
  if(best)return best;
  xy.set(xp/rect.width*2-1,1-yp/rect.height*2);
  ray.setFromCamera(xy,camera);
  return ray.intersectObjects(group.children.filter(x=>x.isMesh&&x.visible),false)[0]?.object?.userData?.se499BoneId||null;
 }
 function rayOnPlane(event,plane){
  const rect=renderer.domElement.getBoundingClientRect();
  xy.set(2*(event.clientX-rect.left)/rect.width-1,1-2*(event.clientY-rect.top)/rect.height);
  ray.setFromCamera(xy,camera);
  const world=new THREE.Vector3();
  if(!ray.ray.intersectPlane(plane,world))return null;
  return world;
 }
 function eventTarget(event){
  const world=rayOnPlane(event,drag.plane);
  if(!world)return null;
  world.add(drag.grabOffset);
  return modelRoot.worldToLocal(world);
 }
 function down(event){
  // Do not intercept floating rig UI or camera controls above the canvas.
  if(event.target!==renderer?.domElement)return;
  const id=selectable(event);if(!id||drag)return;
  se220Playing=false;se220Joint=id;
  const joint=se220R('Joint');if(joint)joint.value=id;
  se220RigJointUI();se496MiniStudios.refresh();
  const bone=se220Bones[id];
  const pivot=bone.getWorldPosition(new THREE.Vector3());
  const normal=camera.getWorldDirection(new THREE.Vector3());
  drag={pointer:event.pointerId,start:[event.clientX,event.clientY],
   initial:pivot.clone(),plane:new THREE.Plane().setFromNormalAndCoplanarPoint(normal,pivot),
   base:math.snapshot(se220Rig()),moved:false,valid:true,
   grabOffset:new THREE.Vector3(),scene:modelRoot,rig:se220Rig(),id};
  const grab=rayOnPlane(event,drag.plane);
  if(grab)drag.grabOffset.copy(pivot).sub(grab);
  stage?.setPointerCapture?.(event.pointerId);
  event.preventDefault();event.stopImmediatePropagation();
  refreshOverlay(true);refreshSelected();
 }
 function moving(event){
  if(!drag||event.pointerId!==drag.pointer)return;
  event.preventDefault();event.stopImmediatePropagation();
  if(Math.hypot(event.clientX-drag.start[0],event.clientY-drag.start[1])<5&&!drag.moved)return;
  drag.moved=true;
  if(modelRoot!==drag.scene||se220Rig()!==drag.rig){cancel();return;}
  const target=eventTarget(event);
  if(!target)return;
  drag.valid=moveFromSnapshot(drag.base,target,true);
  refreshOverlay();
 }
 function up(event){
  if(!drag||event.pointerId!==drag.pointer)return;
  event.preventDefault();event.stopImmediatePropagation();
  try{stage?.releasePointerCapture?.(event.pointerId);}catch{}
  const task=drag;drag=null;
  if(!task.moved){refreshSelected();return;}
  if(!task.valid){
   math.apply(task.rig,task.base);syncRestTransform();status('Connected joint move exceeded supported bounds.',true);
  }else{
   history.push(task.base);if(history.length>20)history.shift();
   se220RigTouched('Connected bone rest position updated. Save Project to retain.');
  }
  refreshSelected();refreshOverlay(true);
 }
 function cancel(){
  if(!drag)return;
  const original=drag;drag=null;
  try{stage?.releasePointerCapture?.(original.pointer);}catch{}
  if(original.rig===se220Rig()){
   math.apply(original.rig,original.base);syncRestTransform();
  }
  refreshSelected();
 }
 function attach(){
  const scene=panel?.querySelector('.atelier-scene');
  if(!scene||scene===stage)return;
  stage=scene;
  // Parent capture phase runs ahead of the existing v11.499 canvas picker.
  stage.addEventListener('pointerdown',down,true);
  stage.addEventListener('pointermove',moving,true);
  stage.addEventListener('pointerup',up,true);
  stage.addEventListener('pointercancel',cancel,true);
 }
 const priorBind=se220RigBind;
 se220RigBind=function(...args){
  forgetOverlay();
  const out=priorBind.apply(this,args);
  if(inRig())refreshOverlay(true);
  return out;
 };
 const priorPose=se220RigPose;
 se220RigPose=function(...args){
  const out=priorPose.apply(this,args);
  if(inRig()&&overlay)refreshOverlay();
  return out;
 };
 const priorRefresh=se220RigRefresh;
 se220RigRefresh=function(...args){
  const out=priorRefresh.apply(this,args);
  if(inRig()){
   install();refreshSelected();
  }else if(overlay)overlay.root.visible=false;
  return out;
 };
 const priorOpen=open;
 open=function(...args){
  const out=priorOpen.apply(this,args);
  if(out!==false){attach();install();refreshSelected();}
  return out;
 };
 const priorClose=close;
 close=function(...args){cancel();forgetOverlay();history=[];lastRig=null;return priorClose.apply(this,args);};
 document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&drag){cancel();event.stopImmediatePropagation();}
 });
 return Object.freeze({refresh:()=>{attach();install();refreshSelected();},
  status:()=>({attached:!!stage,selected:se220Joint,vertices:overlay?.total||0,
   displayed:overlay?.samples.length||0,locked:lockLength,dragging:!!drag})});
})();
window.SWYRL_ENGINE_RIG_CONNECTED_EDIT_500=se500RigEdit;
