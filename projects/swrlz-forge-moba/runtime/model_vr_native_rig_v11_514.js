/* SE514_NATIVE_XR_RIG_START
   Immersive rigging belongs to §E's existing WebXR scene, native spatial
   menu + profile-driven controller pipeline. No DOM overlay or new menu. */
const se514RigXR=(()=>{
 'use strict';
 let handles=null,drag=null,lastRig=null,lastRoot=null;
 let paintMode='add',radius=.18,strength=.16,undoStack=[],previous=new Map();
 const sphere=new THREE.SphereGeometry(.022,12,8);
 const material=new THREE.MeshBasicMaterial({color:0x7bf7db,depthTest:false,depthWrite:false});
 const pickedMaterial=new THREE.MeshBasicMaterial({color:0xffd28b,depthTest:false,depthWrite:false});
 const shaftGeometry=new THREE.CylinderGeometry(.003,.004,1,8);
 const shaftMaterial=new THREE.MeshBasicMaterial({color:0x66a5c9,transparent:true,opacity:.73,depthTest:false});
 const tempA=new THREE.Vector3(),tempB=new THREE.Vector3(),posedPoint=new THREE.Vector3();
 const isRig=()=>se220RigAvailable()&&se220Rig()?.schema==='swyrl-cloth-skin-v1'&&
  !!se220Bones&&!!se220Skeleton&&!!modelRoot;
 const isMode=()=>['rig','rig-weight'].includes(se340XR.mode);
 const selected=()=>isRig()?se220Rig().bones.find(b=>b.id===se220Joint):null;
 const valid=()=>isRig()&&se340VisibleSession()&&se340XR.scene&&se340XR.session;
 const handKey=r=>r?.input?.handedness==='left'?'LT':'RT';
 const physical=(s,k)=>!!s?.buttons?.[k]?.physical;
 function message(t,bad=false){se340Notice(t,bad);se340Publish();}
 function uiState(){
  const rig=isRig()?se220Rig():null,b=selected();
  return {rigAvailable:!!rig,rigBoneName:b?.label||'Select bone',rigBoneId:b?.id||'',
   rigBoneCount:rig?.bones?.length||0,rigBoneIndex:b?rig.bones.findIndex(x=>x.id===b.id)+1:0,
   rigPaintMode:paintMode,rigRadius:radius,rigStrength:strength,
   rigPainting:!!drag,rigUndo:undoStack.length>0};
 }
 function dispose(){
  if(handles?.group?.parent)handles.group.removeFromParent();
  handles=null;lastRig=null;lastRoot=null;previous.clear();
 }
 function init(){
  dispose();undoStack=[];drag=null;
  if(!valid())return;
  const g=new THREE.Group();g.name='§E Immersive Rig Joints (viewport gizmos)';
  g.userData.editorOnly=true;g.userData.se514RigHandles=true;
  se340XR.scene.add(g);handles={group:g,pivots:[],shafts:[]};
 }
 function syncHandles(){
  if(!valid()||!isMode()){if(handles)handles.group.visible=false;return;}
  if(!handles)init();
  const rig=se220Rig();
  if(lastRig!==rig||lastRoot!==modelRoot||handles.pivots.length!==rig.bones.length){
   for(const item of [...handles.pivots,...handles.shafts])item.removeFromParent();
   handles.pivots=[];handles.shafts=[];lastRig=rig;lastRoot=modelRoot;
   for(const spec of rig.bones){
    const dot=new THREE.Mesh(sphere,material);dot.name='Joint · '+spec.label;
    dot.frustumCulled=false;dot.renderOrder=9102;dot.userData.se514Joint=spec.id;
    handles.group.add(dot);handles.pivots.push(dot);
    if(spec.parent){
     const line=new THREE.Mesh(shaftGeometry,shaftMaterial);line.name='Bone link · '+spec.label;
     line.frustumCulled=false;line.renderOrder=9101;line.userData.se514Link=spec.id;
     handles.group.add(line);handles.shafts.push({id:spec.id,parent:spec.parent,mesh:line});
    }
   }
  }
  handles.group.visible=true;
  modelRoot.updateWorldMatrix(true,true);
  for(let i=0;i<rig.bones.length;i++){
   const spec=rig.bones[i],object=se220Bones[spec.id],dot=handles.pivots[i];
   if(!object){dot.visible=false;continue;}
   dot.visible=true;dot.position.copy(object.getWorldPosition(tempA));
   dot.material=spec.id===se220Joint?pickedMaterial:material;
  }
  for(const item of handles.shafts){
   const child=se220Bones[item.id],parent=se220Bones[item.parent];
   if(!child||!parent){item.mesh.visible=false;continue;}
   const a=child.getWorldPosition(tempA),b=parent.getWorldPosition(tempB);
   const len=a.distanceTo(b);if(len<1e-5){item.mesh.visible=false;continue;}
   item.mesh.visible=true;item.mesh.position.copy(a).add(b).multiplyScalar(.5);
   item.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),a.sub(b).normalize());
   item.mesh.scale.set(1,len,1);
  }
  handles.group.updateWorldMatrix(true,true);
 }
 function choose(id){
  const rig=se220Rig();if(!rig?.bones?.some(b=>b.id===id))return false;
  se220Playing=false;se220Joint=id;
  const select=se220R('Joint');if(select)select.value=id;
  se220RigJointUI();
  message('Selected joint '+rig.bones.find(b=>b.id===id).label+' · Right Grip rotates pose.');
  se340SyncUI();return true;
 }
 function cycle(direction){
  const rig=se220Rig();if(!isRig())return false;
  const n=rig.bones.length,i=Math.max(0,rig.bones.findIndex(b=>b.id===se220Joint));
  return choose(rig.bones[(i+direction+n)%n].id);
 }
 function pickBone(record){
  if(!handles?.group?.visible)return null;
  const ray=se340Cast(record);if(!ray)return null;
  handles.group.updateWorldMatrix(true,true);
  return ray.intersectObjects(handles.pivots,true)[0]?.object?.userData?.se514Joint||null;
 }
 function posePreview(gesture){
  if(!valid()||se220Rig()!==gesture.rig||se220Joint!==gesture.id)return false;
  const now=se340GripPose(gesture.record);
  if(!now)return false;
  const delta=now.quaternion.clone().multiply(gesture.hand.clone().invert());
  const world=delta.multiply(gesture.world);
  const local=gesture.parent.clone().invert().multiply(world);
  const e=new THREE.Euler().setFromQuaternion(local,'XYZ');
  const angles=[e.x,e.y,e.z].map(v=>THREE.MathUtils.clamp(v,-2.8,2.8));
  if(!angles.every(Number.isFinite))return false;
  gesture.rig.pose[gesture.id]=angles;
  se220RigPose(gesture.rig.pose);se220RigJointUI();return true;
 }
 function beginPose(record){
  if(!valid()||se340XR.mode!=='rig'||record?.input?.handedness!=='right'||
     se340XR.gesture||!selected())return false;
  const pose=se340GripPose(record),bone=se220Bones[se220Joint];
  if(!pose||!bone)return false;
  modelRoot.updateWorldMatrix(true,true);
  se220Playing=false;
  const rig=se220Rig(),base=structuredClone(rig.pose);
  const parent=bone.parent?.getWorldQuaternion(new THREE.Quaternion())||new THREE.Quaternion();
  se340XR.gesture={kind:'se514-rig-pose',record,id:se220Joint,rig,base,
   hand:pose.quaternion.clone(),world:bone.getWorldQuaternion(new THREE.Quaternion()),parent};
  message('Pose '+selected().label+' · turn Right Grip · release commits · B cancels.');
  return true;
 }
 function finishPose(record){
  const g=se340XR.gesture;if(g?.kind!=='se514-rig-pose'||g.record!==record)return false;
  if(!valid()||!record.gripTracked||g.rig!==se220Rig()){cancelPose();return false;}
  posePreview(g);
  const after=structuredClone(g.rig.pose),before=g.base;
  se340XR.gesture=null;
  if(JSON.stringify(after)===JSON.stringify(before))return true;
  g.rig.pose=before;se220RigRemember();g.rig.pose=after;
  undoStack.push({kind:'pose',rig:g.rig,old:before});if(undoStack.length>20)undoStack.shift();
  se220RigTouched('Immersive bone pose saved. Save Project to retain.');
  message('Pose applied · '+g.id+' · Undo restores previous joint rotation.');
  return true;
 }
 function cancelPose(){
  const g=se340XR.gesture;if(g?.kind!=='se514-rig-pose')return false;
  if(g.rig===se220Rig()){g.rig.pose=g.base;se220RigPose(g.rig.pose);se220RigJointUI();}
  return true; // Native se340CancelGesture still owns cancellation of the gesture.
 }
 function nudge(action){
  if(!valid()||!selected())return false;
  const m=/^rig-pose-([xyz])-(plus|minus)$/.exec(action);if(!m)return false;
  const rig=se220Rig(),axis='xyz'.indexOf(m[1]),step=(m[2]==='plus'?1:-1)*THREE.MathUtils.degToRad(5);
  const before=structuredClone(rig.pose),rot=rig.pose[se220Joint]?.slice()||[0,0,0];
  rot[axis]=THREE.MathUtils.clamp(rot[axis]+step,-2.8,2.8);
  rig.pose[se220Joint]=rot;
  if(!se220RigValidate(rig)){rig.pose=before;return false;}
  rig.pose=before;se220RigRemember();rig.pose[se220Joint]=rot;
  se220Playing=false;se220RigPose(rig.pose);se220RigJointUI();
  undoStack.push({kind:'pose',rig,old:before});if(undoStack.length>20)undoStack.shift();
  se220RigTouched('Immersive joint '+m[1].toUpperCase()+' pose changed by 5°.');
  message(selected().label+' · '+m[1].toUpperCase()+' '+Math.round(rot[axis]*180/Math.PI)+'°');return true;
 }
 function skinTarget(){
  if(!valid())return null;
  const rig=se220Rig(),part=partById(rig.targetPartId),
    mesh=modelRoot.children.find(o=>o.isSkinnedMesh&&o.userData?.atelierId===rig.targetPartId);
  const pos=part?.topologyMesh?.positions,attr=mesh?.geometry?.getAttribute('position');
  const idx=mesh?.geometry?.getAttribute('skinIndex'),w=mesh?.geometry?.getAttribute('skinWeight');
  if(!mesh||!part||!Array.isArray(pos)||!attr||!idx||!w||pos.length!==attr.count*3||
   idx.count!==attr.count||w.count!==attr.count||attr.count>120000)return null;
  return {rig,part,mesh,positions:pos,vertices:attr.count,idx,w};
 }
 function snapshotSkin(target){
  const indices=[],weights=[];
  for(let i=0;i<target.vertices;i++){
   indices.push(target.idx.getX(i),target.idx.getY(i),target.idx.getZ(i),target.idx.getW(i));
   weights.push(target.w.getX(i),target.w.getY(i),target.w.getZ(i),target.w.getW(i));
  }
  return {schema:'swyrl-explicit-skin-v1',indices,weights};
 }
 function gpu(target,skin){
  if(!target?.mesh?.parent||target.mesh.geometry.getAttribute('skinWeight')!==target.w)return false;
  for(let i=0;i<target.vertices;i++){
   const n=i*4;target.idx.setXYZW(i,...skin.indices.slice(n,n+4));
   target.w.setXYZW(i,...skin.weights.slice(n,n+4));
  }
  target.idx.needsUpdate=true;target.w.needsUpdate=true;target.mesh.skeleton?.update();return true;
 }
 function paintSample(session){
  const s=se340XR;
  if(!valid()||!isMode()||s.mode!=='rig-weight'||se220Rig()!==session.target.rig||
   partById(session.target.part.id)!==session.target.part||
   !session.record.targetTracked){cancelPaint();return false;}
  const hit=se340Hit(session.record,true);
  if(!hit?.id||hit.id!==session.target.rig.targetPartId||hit.ui)return false;
  session.target.mesh.updateWorldMatrix(true,false);
  const point=hit.point.clone().applyMatrix4(session.target.mesh.matrixWorld.clone().invert());
  if(session.last&&session.last.distanceToSquared(point)<(radius*.15)**2)return true;
  session.last=point;
  const pose=i=>{
   posedPoint.fromBufferAttribute(session.target.mesh.geometry.getAttribute('position'),i);
   if(typeof session.target.mesh.applyBoneTransform==='function')session.target.mesh.applyBoneTransform(i,posedPoint);
   return posedPoint.toArray();
  };
  const result=se513SkinMath.region(session.target.positions,session.working.indices,session.working.weights,
   point.toArray(),radius,session.index,session.mode==='add'?strength:-strength,
   session.target.rig.bones.length,pose);
  if(!result){cancelPaint();message('Weight edit stopped: invalid mesh or skin data.',true);return false;}
  if(result.changed){
   session.working={schema:'swyrl-explicit-skin-v1',indices:result.indices,weights:result.weights};
   session.changed+=result.changed;
   if(!gpu(session.target,session.working)){cancelPaint();return false;}
  }
  return true;
 }
 function beginPaint(record){
  if(!valid()||se340XR.mode!=='rig-weight'||drag||!selected()||
     record?.input?.handedness!=='right')return false;
  const target=skinTarget();if(!target){message('Weight painting needs matching editable topology (up to 120k vertices).',true);return false;}
  const hit=se340Hit(record,true);if(hit?.ui||hit?.id!==target.rig.targetPartId)return false;
  const old=snapshotSkin(target),index=target.rig.bones.findIndex(b=>b.id===se220Joint);
  if(index<0||!se513SkinMath.validSkin(old,target.vertices,target.rig.bones.length)){
   message('Rig weight data is invalid. No edit applied.',true);return false;}
  drag={record,target,index,id:se220Joint,mode:paintMode,initial:old,
   authored:target.part.skinning?structuredClone(target.part.skinning):null,
   working:{schema:old.schema,indices:old.indices.slice(),weights:old.weights.slice()},
   last:null,changed:0};
  paintSample(drag);
  message('Painting '+paintMode+' influence · release Trigger commits · B cancels.');
  return true;
 }
 function cancelPaint(){
  const old=drag;drag=null;
  if(old&&old.target.mesh.parent)gpu(old.target,old.initial);
  return !!old;
 }
 function finishPaint(){
  const d=drag;drag=null;if(!d)return false;
  if(!d.changed)return true;
  if(!valid()||!d.record.targetTracked||!d.record.gripTracked||
   se220Rig()!==d.target.rig||partById(d.target.part.id)!==d.target.part||
   !se513SkinMath.validSkin(d.working,d.target.vertices,d.target.rig.bones.length)){
   gpu(d.target,d.initial);message('Weight edit canceled because tracking or model changed.',true);return false;}
  checkpoint();
  d.target.part.skinning={schema:'swyrl-explicit-skin-v1',indices:d.working.indices.slice(),weights:d.working.weights.slice()};
  undoStack.push({kind:'weight',target:d.target,old:d.initial,authored:d.authored});
  if(undoStack.length>20)undoStack.shift();
  se220RigTouched('Immersive bone weight stroke saved. Save Project to retain.');
  message('Saved '+d.changed+' real weight updates · Undo available in Rigging.');return true;
 }
 function undoRig(){
  if(drag){cancelPaint();message('Discarded uncommitted weight stroke.');return true;}
  if(se340XR.gesture?.kind==='se514-rig-pose'){se340CancelGesture('Pose canceled.');return true;}
  const item=undoStack.pop();if(!item)return false;
  if(item.kind==='pose'){
   if(se220Rig()!==item.rig)return false;
   item.rig.pose=item.old;se220RigPose(item.rig.pose);se220RigJointUI();
   if(se220PoseHistory.length)se220PoseHistory.pop();
  }else{
   if(se220Rig()!==item.target.rig||partById(item.target.part.id)!==item.target.part)return false;
   gpu(item.target,item.old);
   if(item.authored)item.target.part.skinning=structuredClone(item.authored);
   else delete item.target.part.skinning;
   // The corresponding native checkpoint is the last one if no external
   // edit intervened. Match and consume it to prevent double undo.
   const prior=undo.at(-1);if(typeof prior==='string'){
    try{const parts=JSON.parse(prior),p=parts.find(x=>x.id===item.target.part.id);
      if(JSON.stringify(p?.skinning||null)===JSON.stringify(item.authored||null))undo.pop();
    }catch(_){}
   }
  }
  se220RigTouched('Reverted previous immersive rig edit.');
  message('Rigging edit undone without rebuilding or leaving the VR workspace.');return true;
 }
 function action(command){
  const s=se340XR;
  if(command==='rig'){
   if(!valid()){message('Open a model with a valid cloth skeleton before Rigging.',true);return true;}
   if(s.gesture)se340CancelGesture('Switched to Rigging.');cancelPaint();
   s.mode='rig';s.page='rig';se220Playing=false;
   if(!selected())choose(se220Rig().bones[0].id);
   message('Rigging · Trigger selects a joint · Right Grip rotates its pose.');
   se340SyncUI();return true;
  }
  if(!command.startsWith('rig-'))return false;
  if(!valid()){message('This project has no editable rig.',true);return true;}
  if(command==='rig-weights'){if(s.gesture)se340CancelGesture();s.mode='rig-weight';s.page='rig-weights';message('Weight painting · select bone, then hold Right Trigger on the mesh.');}
  else if(command==='rig-weight-stop'){cancelPaint();s.mode='rig';s.page='rig';message('Weight brush off · bone posing restored.');}
  else if(command==='rig-prev')cycle(-1);
  else if(command==='rig-next')cycle(1);
  else if(command==='rig-weight-add'||command==='rig-weight-erase'){cancelPaint();paintMode=command.endsWith('add')?'add':'erase';message('Weight brush '+paintMode+'. Hold Right Trigger on the mesh.');}
  else if(command.startsWith('rig-radius-')){radius=THREE.MathUtils.clamp(radius*(command.endsWith('plus')?1.25:.8),.02,1.5);message('Weight radius '+radius.toFixed(3));}
  else if(command.startsWith('rig-strength-')){strength=THREE.MathUtils.clamp(strength+(command.endsWith('plus')?.03:-.03),.01,.5);message('Weight step '+Math.round(strength*100)+'%');}
  else if(command==='rig-undo'){if(!undoRig())message('No VR rig edit to undo.');}
  else if(/^rig-pose-[xyz]-(plus|minus)$/.test(command))nudge(command);
  else return false;
  se340SyncUI();se340Publish();return true;
 }
 function beforeDispatch(sample){
  const s=se340XR,suppress=new Set();
  if(!valid()||sample?.cancel||sample?.resetRequired||sample?.profileChanged||!se340VisibleSession()){
   if(drag){suppress.add(handKey(drag.record));cancelPaint();}
  }else{
   if(drag){
    const key=handKey(drag.record);
    if(!physical(sample,key)||!drag.record.targetTracked||!drag.record.gripTracked){
     if(!physical(sample,key)&&drag.record.targetTracked&&drag.record.gripTracked)finishPaint();
     else cancelPaint();
     suppress.add(key);
    }else if(s.frameCount%3===0)paintSample(drag);
   }else if(s.mode==='rig-weight'){
    const r=se350Record('right'),key='RT',down=physical(sample,key);
    if(down&&!previous.get(r)&&r?.targetTracked&&r.gripTracked&&beginPaint(r))suppress.add(key);
   }
  }
  for(const r of s.controllers||[])previous.set(r,physical(sample,handKey(r)));
  if(!suppress.size)return sample;
  return {...sample,events:(sample.events||[]).filter(e=>{
   if(!['select','multiselect','stroke','sample'].includes(e.action))return true;
   return !(e.keys||[]).some(k=>suppress.has(k));
  })};
 }
 function exit(){cancelPaint();cancelPose();dispose();undoStack=[];}
 return Object.freeze({uiState,valid,isMode,init,syncHandles,choose,pickBone,beginPose,
  posePreview,finishPose,cancelPose,action,beforeDispatch,undoRig,cancelPaint,exit,
  inspect:()=>({...uiState(),joints:handles?.pivots.length||0,painting:!!drag,poseGesture:se340XR.gesture?.kind==='se514-rig-pose'})});
})();
const se514PriorStage=se340MakeStage;
se340MakeStage=function(...args){const out=se514PriorStage.apply(this,args);se514RigXR.init();return out;};
const se514PriorTrigger=se340Trigger;
se340Trigger=function(record,additive=false){
 if(se514RigXR.valid()&&se340XR.mode==='rig'&&!additive){
  const hit=se340Hit(record,false);if(hit?.ui)return se514PriorTrigger.apply(this,arguments);
  const id=se514RigXR.pickBone(record);if(id)return se514RigXR.choose(id);
 }
 return se514PriorTrigger.apply(this,arguments);
};
const se514PriorBeginGesture=se340BeginGesture;
se340BeginGesture=function(record,purpose='grab'){
 if(purpose==='grab'&&se514RigXR.valid()&&se340XR.mode==='rig'&&record?.input?.handedness==='right')
  return se514RigXR.beginPose(record);
 return se514PriorBeginGesture.apply(this,arguments);
};
const se514PriorUpdateGesture=se340UpdateGesture;
se340UpdateGesture=function(...args){
 se514RigXR.syncHandles();
 if(se340XR.gesture?.kind==='se514-rig-pose'){
  if(!se514RigXR.posePreview(se340XR.gesture))se340CancelGesture('Rig pose stopped safely.');
  return;
 }
 return se514PriorUpdateGesture.apply(this,args);
};
const se514PriorFinishGesture=se340FinishGesture;
se340FinishGesture=function(record){
 if(se340XR.gesture?.kind==='se514-rig-pose')return se514RigXR.finishPose(record);
 return se514PriorFinishGesture.apply(this,arguments);
};
const se514PriorCancelGesture=se340CancelGesture;
se340CancelGesture=function(...args){
 se514RigXR.cancelPaint();
 se514RigXR.cancelPose();
 return se514PriorCancelGesture.apply(this,args);
};
const se514PriorAction=se340ModelXRAction;
se340ModelXRAction=function(command,record=null){
 if(command==='rig'||command.startsWith('rig-'))return se514RigXR.action(command);
 if(command==='undo'&&se514RigXR.isMode()&&se514RigXR.undoRig()){
  se340SyncUI();return true;
 }
 return se514PriorAction.apply(this,arguments);
};
const se514PriorDispatch=se350Dispatch;
se350Dispatch=function(sample){return se514PriorDispatch(se514RigXR.beforeDispatch(sample));};
const se514PriorCleanup=se340Cleanup;
se340Cleanup=function(...args){se514RigXR.exit();return se514PriorCleanup.apply(this,args);};
window.SWYRL_ENGINE_IMMERSIVE_RIG_514=se514RigXR;
/* SE514_NATIVE_XR_RIG_END */
