/* SE531_QUEST_MENU_GIZMO_ACCOUNT_START */
(function(){
 'use strict';
 const T=THREE,stats={menuFrames:0,axisFrames:0,capturedFrames:0};
 const priorOrbit=se372MenuOrbit;
 let lastMenu=null;
 se372MenuOrbit=function(...args){
  const s=se340XR,root=s.ui?.root,left=se350Record('left');
  const pose=left?.gripTracked&&left?.targetTracked?se340GripPose(left):null;
  const viewer=s.lastViewer;
  if(!s.session||!root||!pose||!viewer?.position?.isVector3||!viewer?.forward?.isVector3)
   return priorOrbit.apply(this,args);
  // Follow controller TRANSLATION, not wrist roll/pitch/yaw.
  const forward=viewer.forward.clone();forward.y=0;
  if(forward.lengthSq()<.01)forward.set(0,0,-1);
  forward.normalize();
  const right=new T.Vector3().crossVectors(forward,new T.Vector3(0,1,0)).normalize();
  const goal=pose.position.clone().addScaledVector(forward,.74)
   .addScaledVector(right,.075).add(new T.Vector3(0,.20,0));
  const dt=Math.max(0,Math.min(.05,s.frameDt||.016)),alpha=1-Math.exp(-dt*18);
  if(lastMenu!==root||root.position.distanceToSquared(goal)>.5)root.position.copy(goal);
  else root.position.lerp(goal,alpha);
  const face=viewer.position.clone();face.y=root.position.y;
  if(face.distanceToSquared(root.position)>.004)root.lookAt(face);
  root.scale.setScalar(.86);root.visible=s.paletteVisible;
  root.updateWorldMatrix(true,true);lastMenu=root;stats.menuFrames++;
 };
 // Reflow the SAME native UI and ray-hit targets after its own animations.
 const priorCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=priorCreate(options),root=ui.root;
  const rail=root.getObjectByName('Model VR · far-right primary tools');
  const sub=root.getObjectByName('Model VR · operation submenu');
  const details=root.getObjectByName('Model VR · native modifier panel');
  const params=details?.getObjectByName('§E · contextual parameter toolbar');
  const banner=details?.getObjectByName('§E · contextual sculpt brush guide');
  const modal=root.getObjectByName('§E · Project and confirmation dialog');
  const oldUpdate=ui.update,oldTick=ui.tick,oldPress=ui.press;
  function layout(){
   const state=ui.inspect?.()||{},third=(state.drawerProgress||0)>.01;
   const second=(state.submenuProgress||0)>.01;
   const modalOpen=!!ui.isModalOpen?.();
   if(rail)rail.position.x=third?-.408:second?-.127:0;
   if(sub)sub.position.x=third?-.165:.14;
   if(details)details.position.x=.285;
   if(params)params.position.set(0,-.505,.093);
   if(banner)banner.visible=false;
   if(modal)modal.position.set(0,0,.19);
   if(modalOpen){
    if(rail)rail.visible=false;
    if(sub)sub.visible=false;
    if(details)details.visible=false;
   }
   root.updateWorldMatrix(true,true);
  }
  layout();
  return Object.freeze({...ui,
   update:function(...args){const result=oldUpdate.apply(this,args);layout();return result;},
   tick:function(...args){const result=oldTick.apply(this,args);layout();return result;},
   press:function(...args){const result=oldPress.apply(this,args);layout();return result;},
   inspect:()=>({...ui.inspect(),se531Layout:'head-facing / wrist-independent'})
  });
 };
 // Consume every frame of a captured Trigger until physical release,
 // instead of letting the native profile dispatch other actions during drag.
 const priorDispatch=se350Dispatch;
 se350Dispatch=function(sample){
  if(!sample||!Array.isArray(sample.events))return priorDispatch(sample);
  const captured=new Set(se512GizmoInput.inspect().captured.map(c=>c.key));
  if(!captured.size&&!se340XR.gesture&&
     ['grab','move','rotate','scale'].includes(se340XR.mode)){
   for(const record of se340XR.controllers||[]){
    const key=record?.input?.handedness==='left'?'LT':'RT';
    if(sample.buttons?.[key]?.physical&&record?.targetTracked&&record?.gripTracked&&
       se374GizmoContact(record)?.gizmo)captured.add(key);
   }
  }
  if(!captured.size)return priorDispatch(sample);
  stats.capturedFrames++;
  return priorDispatch({...sample,events:sample.events.filter(e=>
   !Array.isArray(e.keys)||!e.keys.some(k=>captured.has(k)))});
 };
 // Grip displacement projected to a captured gizmo axis gives a continuous
 // reversible translation regardless of ray direction after first contact.
 const priorPose=se390UpdatePose;
 se390UpdatePose=function(g,pose,gain){
  if(!g?.se512Trigger||g.kind!=='group'||g.mode!=='move'||
     !['x','y','z'].includes(g.axis))return priorPose.apply(this,arguments);
  if(!pose?.position?.isVector3||!g.record?.gripTracked||!g.record?.targetTracked)return;
  let state=g.se531Axis;
  if(!state){
   const axis=g.axis==='x'?new T.Vector3(1,0,0):g.axis==='y'?
    new T.Vector3(0,1,0):new T.Vector3(0,0,1);
   const world=axis.clone().applyQuaternion(g.rootQuaternion).normalize();
   const localOrigin=new T.Vector3().applyMatrix4(g.rootInverse);
   const localAxis=world.clone().applyMatrix4(g.rootInverse).sub(localOrigin);
   state=g.se531Axis={last:pose.position.clone(),world,localAxis,total:0,frames:0};
  }
  const fine=Number.isFinite(gain)?T.MathUtils.clamp(gain,.02,1):1;
  const step=pose.position.clone().sub(state.last).dot(state.world);
  state.last.copy(pose.position);
  if(Number.isFinite(step))state.total=T.MathUtils.clamp(state.total+step*fine,-100,100);
  const translation=state.localAxis.clone().multiplyScalar(state.total);
  if(se340XR.snap)for(let i=0;i<3;i++)translation.setComponent(
   i,Math.round(translation.getComponent(i)/.01)*.01);
  const rotation=new T.Quaternion();
  se372Constrain(g,translation,rotation);
  se372GuideUpdate(g,translation,rotation,1);
  const result=se350Tools().updateGroup({translation:translation.toArray(),rotation:[0,0,0,1],scale:1});
  if(result?.ok===false)se340CancelGesture(result.error||'Constrained Trigger drag canceled.');
  else {state.frames++;stats.axisFrames++;}
 };
 window.SWYRL_ENGINE_QUEST_INTERACTIONS_531=Object.freeze({inspect:()=>({
  ...stats,axis:se340XR.gesture?.se531Axis?
   {name:se340XR.gesture.axis,frames:se340XR.gesture.se531Axis.frames}:null,
  menuVisible:!!se340XR.ui?.root?.visible,
  dialog:se340XR.ui?.dialogInspect?.().active||''
 })});
})();
/* SE531_QUEST_MENU_GIZMO_ACCOUNT_END */