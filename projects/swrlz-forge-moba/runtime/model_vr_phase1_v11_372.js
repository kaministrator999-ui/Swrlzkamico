/* SE372_MODEL_VR_PHASE1_START */
// Owner-tested phase 1: tactile selection sweep, spatial palette and transform feedback.
// Shares the native model document, account link, controller profile and sole XR loop.
const SE372_MENU_KEY='swyrl.model-vr.menu-placement.v1';
const se372AxisNames=['x','y','z'];
function se372ReadMenu(){
 try{const p=JSON.parse(localStorage.getItem(SE372_MENU_KEY)||'null');
  if(p&&[p.x,p.y,p.z].every(v=>Number.isFinite(v)&&Math.abs(v)<3))return p;
 }catch(_){}
 return {x:-.56,y:-.06,z:1.02};
}
function se372OrbitQuaternion(){
 const s=se340XR;
 return new THREE.Quaternion().setFromEuler(new THREE.Euler(s.pitch,s.yaw-s.baseYaw,0,'YXZ'));
}
function se372MenuPlace(viewer,reset=false){
 const s=se340XR;if(!s.ui||!viewer)return;
 if(s.se372MenuBase&&!reset){s.ui.root.visible=s.paletteVisible;return;}
 const p=reset?{x:-.56,y:-.06,z:1.02}:se372ReadMenu();
 const forward=viewer.forward.clone();forward.y=0;
 if(forward.lengthSq()<.001)forward.set(0,0,-1);
 forward.normalize();
 const right=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();
 s.ui.root.position.copy(viewer.position).addScaledVector(forward,p.z).addScaledVector(right,p.x);
 s.ui.root.position.y=THREE.MathUtils.clamp(viewer.position.y+p.y,.65,1.95);
 s.ui.root.lookAt(viewer.position);
 s.se372MenuBase={position:s.ui.root.position.clone(),quaternion:s.ui.root.quaternion.clone()};
 s.ui.root.visible=s.paletteVisible;s.ui.root.updateWorldMatrix(true,true);
}
function se372MenuOrbit(){
 const s=se340XR,b=s.se372MenuBase;
 if(!s.ui||!b||s.gesture?.kind==='menu')return;
 const q=se372OrbitQuaternion().invert(),c=s.rig.position;
 s.ui.root.position.copy(b.position).sub(c).applyQuaternion(q).add(c);
 s.ui.root.quaternion.copy(q).multiply(b.quaternion);
 s.ui.root.visible=s.paletteVisible;
 s.ui.root.updateWorldMatrix(true,true);
}
function se372MenuRemember(){
 const s=se340XR,b=s.se372MenuBase,a=s.anchor;
 if(!b||!a)return;
 const d=b.position.clone().sub(a.position);
 const p={x:d.dot(s.right),y:d.y,z:d.dot(s.forward)};
 if([p.x,p.y,p.z].every(v=>Number.isFinite(v)&&Math.abs(v)<3)){
  try{localStorage.setItem(SE372_MENU_KEY,JSON.stringify(p));}catch(_){}
 }
}
function se372MenuDragStart(record,pose){
 const s=se340XR;if(!s.ui?.root.visible||s.gesture)return false;
 const hit=se340Hit(record,false);if(!hit?.ui)return false;
 s.gesture={kind:'menu',record,hand:pose,start:s.ui.root.position.clone(),
  initial:s.ui.root.position.clone(),initialRotation:s.ui.root.quaternion.clone()};
 se340Notice('Moving VR menu · release Grip to place · B cancels.');
 se340Pulse(record,.15,15);return true;
}
function se372MenuDragUpdate(g,pose){
 se340XR.ui.root.position.copy(g.start).add(pose.position.clone().sub(g.hand.position));
 se340XR.ui.root.updateWorldMatrix(true,true);
}
function se372MenuDragFinish(g,commit){
 const s=se340XR,ui=s.ui;if(!ui)return;
 if(!commit){ui.root.position.copy(g.initial);ui.root.quaternion.copy(g.initialRotation);return;}
 // Store a baseline pose independent of model transforms and headset movement.
 const q=se372OrbitQuaternion(),center=s.rig.position;
 const pos=ui.root.position.clone().sub(center).applyQuaternion(q).add(center);
 const orientation=q.clone().multiply(ui.root.quaternion);
 s.se372MenuBase={position:pos,quaternion:orientation};
 se372MenuRemember();
}
function se372ResetMenu(){
 try{localStorage.removeItem(SE372_MENU_KEY);}catch(_){}
 const s=se340XR;
 s.se372MenuBase=null;
 se372MenuPlace(s.anchor||s.lastViewer,true);
 se372MenuOrbit();
 se340Notice('VR menu restored to its default side position.');
}
function se372SweepStart(record,before){
 const s=se340XR,hit=record.hit;
 if(s.gesture||!hit?.id||hit.ui||s.mode==='sculpt'||s.mode==='draw'||s.mode==='lasso')return;
 const chosen=new Set(se350Tools().selection().ids);
 s.se372Sweep={record,last:hit.id,stack:[hit.id],baseline:new Set(before),
  added:new Set(!before.includes(hit.id)&&chosen.has(hit.id)?[hit.id]:[]),lastAt:0};
}
function se372SweepFrame(s){
 const w=s.se372Sweep;if(!w)return;
 if(!s.inputSample?.buttons?.LT?.physical||!w.record.targetTracked||!se340VisibleSession()||s.gesture){
  s.se372Sweep=null;return;
 }
 // Reuse the already-throttled hover contact; do not raycast all model triangles
 // at 72/90Hz or rebuild any model geometry while sweeping.
 const id=w.record.hit?.id;
 if(!id||w.record.hit?.ui||id===w.last)return;
 const now=performance.now();if(now-w.lastAt<28)return;
 w.lastAt=now;w.last=id;
 const stack=w.stack,previous=stack[stack.length-2];
 if(id===previous){
  const removed=stack.pop();
  if(!stack.includes(removed)&&w.added.has(removed)&&se350Tools().selection().ids.includes(removed)){
   const result=se350Tools().select(removed,{additive:true});
   if(result?.ok!==false){w.added.delete(removed);se350Invalidate();}
  }
 }else{
  const selected=se350Tools().selection().ids;
  if(!selected.includes(id)){
   const result=se350Tools().select(id,{additive:true});
   if(result?.ok===false){se350Result(result,'',w.record);return;}
   w.added.add(id);se350Invalidate();se340Pulse(w.record,.11,12);
  }
  if(stack.length<128)stack.push(id);
 }
 const n=se350Tools().selection().ids.length;
 se340Notice(n+' meshes selected · reverse sweep to remove new selections.');
}
function se372MakeGizmo(){
 const s=se340XR,g=new THREE.Group();g.name='Model VR selection transform gizmo';
 g.userData.editorOnly=true;s.scene.add(g);
 const handles=[],owned=[];
 const colors=[0xf26e73,0x7ce8ad,0x71abfa],dirs=[
  new THREE.Vector3(1,0,0),new THREE.Vector3(0,1,0),new THREE.Vector3(0,0,1)];
 for(let i=0;i<3;i++){
  const color=colors[i],axis=se372AxisNames[i],dir=dirs[i];
  const material=new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide,transparent:true,opacity:.88,depthTest:false,depthWrite:false});
  owned.push(material);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.105,.004,6,56),material);
  if(i===0)ring.rotation.y=Math.PI/2;
  if(i===1)ring.rotation.x=Math.PI/2;
  ring.userData.se372Axis=axis;ring.userData.editorOnly=true;g.add(ring);handles.push(ring);owned.push(ring.geometry);
  const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.004,.004,.105,7),material);
  shaft.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir);
  shaft.position.copy(dir).multiplyScalar(.065);
  shaft.userData.se372Axis=axis;shaft.userData.editorOnly=true;g.add(shaft);handles.push(shaft);owned.push(shaft.geometry);
  const tip=new THREE.Mesh(new THREE.ConeGeometry(.012,.027,9),material);
  tip.quaternion.copy(shaft.quaternion);tip.position.copy(dir).multiplyScalar(.13);
  tip.userData.se372Axis=axis;tip.userData.editorOnly=true;g.add(tip);handles.push(tip);owned.push(tip.geometry);
 }
 const cube=new THREE.Mesh(new THREE.BoxGeometry(.024,.024,.024),
  new THREE.MeshBasicMaterial({color:0xffdeb1,depthTest:false,depthWrite:false}));
 cube.userData.editorOnly=true;cube.userData.se372Axis='uniform';
 g.add(cube);handles.push(cube);owned.push(cube.geometry,cube.material);
 g.renderOrder=9100;g.traverse(o=>{if(o.isMesh)o.renderOrder=9100;});
 s.se372Gizmo={root:g,handles,owned};g.visible=false;
}
function se372GizmoHit(record){
 const s=se340XR,p=s.se372Gizmo;
 if(!p?.root.visible||!['move','rotate','scale'].includes(s.mode))return null;
 const cast=se340Cast(record);if(!cast)return null;
 const hits=cast.intersectObjects(p.handles,false);
 const closest=hits.find(h=>h.object.userData?.se372Axis);
 if(!closest)return null;
 const axis=closest.object.userData.se372Axis;
 return axis==='uniform'&&s.mode!=='scale'?null:axis;
}
function se372GizmoFrame(s){
 if(!s.scene)return;
 if(!s.se372Gizmo)se372MakeGizmo();
 const g=s.se372Gizmo;
 const selected=se350Tools()?.selection?.();
 const visible=['move','rotate','scale'].includes(s.mode)&&!!selected?.ids?.length;
 g.root.visible=visible;
 if(!visible)return;
 const p=new THREE.Vector3(...(selected.pivot||[0,0,0])),root=se350Root();
 root.updateWorldMatrix(true,false);
 g.root.position.copy(root.localToWorld(p));
 g.root.quaternion.copy(root.getWorldQuaternion(new THREE.Quaternion()));
 // Disallow invisible mode handles from taking a grab.
 for(const h of g.handles){
  const axis=h.userData.se372Axis;
  h.visible=s.mode==='rotate'?h.geometry.type==='TorusGeometry':
   s.mode==='move'?h.geometry.type!=='TorusGeometry'&&axis!=='uniform':axis==='uniform';
 }
}
function se372GuideStart(g){
 if(!['move','rotate','scale'].includes(g.mode)||!g.record?.target)return;
 const container=new THREE.Group();container.name='Grip transform feedback';
 container.position.set(0,.03,-.17);
 container.quaternion.copy(se344AimQuat(g.record));
 const start=new THREE.AxesHelper(.066),live=new THREE.AxesHelper(.095);
 const ghost=start.material;if(ghost){ghost.transparent=true;ghost.opacity=.35;ghost.depthTest=false;}
 if(live.material)live.material.depthTest=false;
 container.add(start,live);g.record.target.add(container);
 g.se372Guide={container,start,live};se340XR.se372Guide=container;
}
function se372GuideUpdate(g,translation,rotation,scale){
 if(!g?.se372Guide)return;
 const guide=g.se372Guide;guide.live.quaternion.copy(rotation);
 if(g.mode==='move'){
  const shift=translation.clone().applyQuaternion(g.rootQuaternion);
  const parentQ=g.record.target.getWorldQuaternion(new THREE.Quaternion()).invert();
  guide.live.position.copy(shift.applyQuaternion(parentQ)).clampLength(0,.13);
 }else if(g.mode==='scale')guide.live.scale.setScalar(THREE.MathUtils.clamp(scale,.4,1.8));
}
function se372GuideStop(g){
 const guide=g?.se372Guide;if(!guide)return;
 guide.container.removeFromParent();
 for(const axis of [guide.start,guide.live]){
  axis.geometry?.dispose?.();
  if(Array.isArray(axis.material))axis.material.forEach(m=>m.dispose?.());
  else axis.material?.dispose?.();
 }
 se340XR.se372Guide=null;g.se372Guide=null;
}
function se372Constrain(g,translation,rotation){
 if(!g.axis||g.axis==='uniform')return;
 const axis=new THREE.Vector3(g.axis==='x'?1:0,g.axis==='y'?1:0,g.axis==='z'?1:0);
 if(g.mode==='move')translation.copy(axis).multiplyScalar(translation.dot(axis));
 if(g.mode==='rotate'){
  const v=new THREE.Vector3(rotation.x,rotation.y,rotation.z);
  const angle=2*Math.atan2(v.dot(axis),rotation.w);
  rotation.setFromAxisAngle(axis,angle);
 }
}
function se372Dispose(){
 const s=se340XR;
 se372GuideStop(s.gesture);s.se372Sweep=null;s.se372MenuBase=null;
 if(s.se372Gizmo){s.se372Gizmo.root.removeFromParent();
  for(const resource of s.se372Gizmo.owned)resource.dispose?.();
  s.se372Gizmo=null;
 }
}
async function se372ProjectAction(action){
 const s=se340XR;
 if(s.se372ProjectBusy){se340Notice('Project save already in progress.');return;}
 if(s.gesture){se340Notice('Release the active model grip before saving.',true);return;}
 s.se372ProjectBusy=true;
 try{
  if(action==='save-account'){
   if(!ready||!se176AccountConnected){
    if(!ready&&frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
    se340Notice('Account not connected. Sign in through §E first, then Save to account.',true);return;
   }
   se340Notice('Saving model and UV textures to your account…');
   const synced=await se371Save();
   se340Notice(synced?'Saved to account · open this version on other devices.':
    'Saved on this device; account sync not confirmed. Check account revision.',!synced);
  }else if(action==='save-local'){
   if(!se371HasSavedIdentity())await se371Clone(se371NewName(se371ProjectName()));
   else await se371SaveLocal();
   se340Notice('Project saved on this device.');
  }else if(action==='clone-project'){
   // Keep the active XR document borrowed. Store an independent project snapshot,
   // rather than replacing it while headset input is active.
   const row=se175Snapshot(),copy=structuredClone(row.data),newId=id();
   const name=se371NewName(se371ProjectName());
   copy.project={...copy.project,instanceId:newId,name,projectName:name,
     sourceStarterId:se371SourceId(),se371TemplateSource:false};
   delete copy.project.cloudRef;
   if(copy.project.levelPack?.schema==='se-levels-v1'){
    copy.project.levelProjectRoot='project-'+newId;
    for(const level of copy.project.levelPack.levels||[])if(level?.data?.project){
     Object.assign(level.data.project,{instanceId:newId,projectName:name,name,levelProjectRoot:'project-'+newId});
    }
   }
   await se175Store([{id:newId,name,starterId:se371SourceId(),
      updatedAt:new Date().toISOString(),data:copy}]);
   se340Notice('Cloned as '+name+' on this device · active VR model unchanged.');
  }
 }catch(error){se340Notice('Project operation failed: '+String(error?.message||error).slice(0,90),true);}
 finally{s.se372ProjectBusy=false;se340SyncUI();se340Publish();}
}
function se372Frame(s){
 se372MenuOrbit();
 se372GizmoFrame(s);
 se372SweepFrame(s);
}
/* SE372_MODEL_VR_PHASE1_END */
