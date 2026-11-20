/* SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_START */
/* Native WebXR only. Keep the existing XR loop, model transaction and menu. */
(function(){
 'use strict';
 const T=THREE;
 const previousPose=se390UpdatePose;
 const stats={rayFrames:0,gripFallbacks:0,controllerMenuFrames:0};
 const axisVector=axis=>axis==='x'?new T.Vector3(1,0,0):
  axis==='y'?new T.Vector3(0,1,0):axis==='z'?new T.Vector3(0,0,1):null;
 const getRay=record=>se340Cast(record)?.ray||null;
 const localDelta=(g,world)=>{
  const origin=new T.Vector3().applyMatrix4(g.rootInverse);
  return world.clone().applyMatrix4(g.rootInverse).sub(origin);
 };
 function makeState(g,pose){
  const ray=getRay(g.record);if(!ray)return null;
  const axis=axisVector(g.axis),worldAxis=axis?.clone().applyQuaternion(g.rootQuaternion).normalize()||null;
  const pivot=se340XR.se372Gizmo?.root?.getWorldPosition(new T.Vector3())||
   ray.at(.75,new T.Vector3());
  // An axis plane must contain the axis and face the controller ray.
  // When aimed nearly parallel to an axis, grip delta is used instead.
  let normal=worldAxis?ray.direction.clone().addScaledVector(worldAxis,
   -ray.direction.dot(worldAxis)):ray.direction.clone();
  if(normal.lengthSq()<.01)normal=null;
  if(normal)normal.normalize();
  const plane=normal?new T.Plane().setFromNormalAndCoplanarPoint(normal,pivot):null;
  const initial=plane?ray.intersectPlane(plane,new T.Vector3()):null;
  return {axis,worldAxis,pivot,plane,lastPoint:initial,lastGrip:pose.position.clone(),
   translation:new T.Vector3(),rotation:new T.Quaternion(),logScale:0,gain:null,
   lastRayMode:!!initial};
 }
 se390UpdatePose=function(g,pose,gain){
  if(!g?.se512Trigger||g.kind!=='group'||!['move','rotate','scale'].includes(g.mode))
   return previousPose.apply(this,arguments);
  if(!g.record?.targetTracked||!g.record?.gripTracked)return;
  const state=g.se530Continuous||(g.se530Continuous=makeState(g,pose));
  if(!state)return;
  const ray=getRay(g.record),point=state.plane&&ray?
   ray.intersectPlane(state.plane,new T.Vector3()):null;
  const useRay=!!point&&(!state.worldAxis||
   Math.abs(ray.direction.dot(state.plane.normal))>.09);
  const fine=Number.isFinite(gain)?T.MathUtils.clamp(gain,.02,1):1;
  if(state.gain!==null&&(Math.abs(state.gain-fine)>.0001||
      state.lastRayMode!==useRay)){
   // Rebase on precision or solver change without moving the object.
   state.lastPoint=useRay?point:null;
   state.lastGrip.copy(pose.position);
   state.gain=fine;state.lastRayMode=useRay;return;
  }
  state.gain=fine;state.lastRayMode=useRay;
  let worldStep;
  if(useRay&&state.lastPoint)worldStep=point.clone().sub(state.lastPoint);
  else{worldStep=pose.position.clone().sub(state.lastGrip);stats.gripFallbacks++;}
  state.lastPoint=useRay?point:null;state.lastGrip.copy(pose.position);
  if(g.mode==='move'){
   if(state.worldAxis)worldStep.copy(state.worldAxis).multiplyScalar(
    worldStep.dot(state.worldAxis));
   state.translation.add(localDelta(g,worldStep.multiplyScalar(fine)));
  }else if(g.mode==='rotate'&&state.axis&&state.worldAxis){
   const last=useRay&&point?point.clone().sub(worldStep).sub(state.pivot):null;
   const next=useRay?point.clone().sub(state.pivot):null;
   if(last&&next&&last.lengthSq()>.00001&&next.lengthSq()>.00001){
    const angle=Math.atan2(state.worldAxis.dot(last.clone().cross(next)),
      last.dot(next))*fine;
    const dq=new T.Quaternion().setFromAxisAngle(state.axis,T.MathUtils.clamp(angle,-.4,.4));
    state.rotation.premultiply(dq).normalize();
   }else{
    const spin=pose.quaternion.clone().multiply(g.hand.quaternion.clone().invert());
    const local=g.rootQuaternion.clone().invert().multiply(spin).multiply(g.rootQuaternion);
    const a=2*Math.atan2(new T.Vector3(local.x,local.y,local.z).dot(state.axis),local.w);
    state.rotation.setFromAxisAngle(state.axis,a*fine);
   }
  }else if(g.mode==='scale'){
   const direction=state.worldAxis||new T.Vector3(0,1,0);
   state.logScale=T.MathUtils.clamp(state.logScale+worldStep.dot(direction)*fine*3.2,-4,4);
  }
  const translation=state.translation.clone(),rotation=state.rotation.clone();
  let scale=Math.exp(state.logScale);
  if(se340XR.snap){
   for(let i=0;i<3;i++)translation.setComponent(i,Math.round(translation.getComponent(i)/.01)*.01);
   if(g.mode==='rotate'&&state.axis){
    const a=2*Math.atan2(new T.Vector3(rotation.x,rotation.y,rotation.z).dot(state.axis),rotation.w);
    const snap=T.MathUtils.degToRad(se340XR.inputSample?.thresholds.snapDegrees||15);
    rotation.setFromAxisAngle(state.axis,Math.round(a/snap)*snap);
   }
   scale=1+Math.round((scale-1)/.05)*.05;
  }
  se372Constrain(g,translation,rotation);
  se372GuideUpdate(g,translation,rotation,scale);
  const result=se350Tools().updateGroup({translation:translation.toArray(),
    rotation:rotation.toArray(),scale});
  if(result?.ok===false)se340CancelGesture(result.error||'Transform preview canceled.');
  else stats.rayFrames++;
 };
 // The console moves with the LEFT grip at a fixed comfortable offset;
 // all three native tool tiers and their hit targets remain one UI group.
 const previousOrbit=se372MenuOrbit;
 se372MenuOrbit=function(...args){
  const s=se340XR,root=s.ui?.root,left=se350Record('left');
  const pose=left?.gripTracked&&left?.targetTracked?se340GripPose(left):null;
  if(!s.session||!root||!pose)return previousOrbit.apply(this,args);
  const location=new T.Vector3(.08,.22,-.72).applyQuaternion(pose.quaternion);
  root.position.copy(pose.position).add(location);
  if(s.lastViewer?.position?.isVector3&&
     root.position.distanceToSquared(s.lastViewer.position)>.01)
   root.lookAt(s.lastViewer.position);
  // Constant physical distance and high-resolution CanvasTextures prevent
  // shrinking into a distant, unreadable world-anchored menu.
  root.scale.setScalar(.94);
  root.visible=s.paletteVisible;
  root.updateWorldMatrix(true,true);
  stats.controllerMenuFrames++;
 };
 // Controller-following panels no longer have a separate world-space Grip
 // placement transaction. Left Grip keeps its native viewport-pan behavior.
 se372MenuDragStart=function(){return false;};
 const previousCreate=se340CreateModelVRUI;
 se340CreateModelVRUI=function(options){
  const ui=previousCreate(options),details=ui.root.getObjectByName('Model VR · native modifier panel');
  if(!details)return ui;
  const canvas=document.createElement('canvas');canvas.width=1400;canvas.height=240;
  const ctx=canvas.getContext('2d');
  if(!ctx)return ui;
  const texture=new T.CanvasTexture(canvas);texture.colorSpace=T.SRGBColorSpace;
  texture.minFilter=T.LinearFilter;texture.magFilter=T.LinearFilter;
  const material=new T.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,
   depthWrite:false,toneMapped:false,side:T.DoubleSide});
  const geometry=new T.PlaneGeometry(.55,.091);
  const banner=new T.Mesh(geometry,material);banner.position.set(0,-.348,.09);
  banner.renderOrder=8670;banner.frustumCulled=false;banner.visible=false;
  banner.name='§E · contextual sculpt brush guide';banner.userData.editorOnly=true;
  details.add(banner);
  let activeOperation=null,disposed=false,lastRender='';
  const pretty=id=>String(id||'').replace(/^sculpt-/,'').replaceAll('-',' ').toUpperCase();
  function render(){
   const s=JSON.stringify([activeOperation,se340XR.sculptDirection,se340XR.brushRadius,se340XR.brushStrength]);
   if(s===lastRender)return;lastRender=s;
   ctx.clearRect(0,0,canvas.width,canvas.height);
   ctx.fillStyle='#1d2d3e';ctx.fillRect(0,0,canvas.width,canvas.height);
   ctx.strokeStyle='#7bb2a7';ctx.lineWidth=8;ctx.strokeRect(5,5,canvas.width-10,canvas.height-10);
   const inwards=se340XR.sculptDirection==='in';
   ctx.fillStyle='#b8f2df';ctx.font='700 54px system-ui';
   const label=activeOperation==='sculpt-push'?
    'PUSH / PULL · '+(inwards?'PUSH IN':'PULL OUT'):pretty(activeOperation);
   ctx.fillText('SCULPT · '+label,42,88);
   ctx.fillStyle='#f2f7ff';ctx.font='38px system-ui';
   ctx.fillText('Use native Direction · Falloff · Radius · Strength controls',42,169);
   texture.needsUpdate=true;
  }
  const originalPress=ui.press,originalUpdate=ui.update,originalInspect=ui.inspect,
   originalDispose=ui.dispose;
  function tidy(){
   const info=originalInspect();
   const sculpt=!!activeOperation?.startsWith('sculpt-')&&
    info?.settingsOpen&&info?.drawerProgress>.01;
   banner.visible=sculpt;
   if(sculpt)render(); // Preserve native Direction, Falloff, Radius and Strength actions.
  }
  function press(target){
   const mesh=target?.object||target,action=mesh?.userData?.se340Action;
   if(mesh?.userData?.se445MenuRole==='submenu')activeOperation=action||null;
   else if(mesh?.userData?.se445MenuRole==='primary'||
      action==='se445-close-settings'||action==='se445-close-submenu')activeOperation=null;
   const result=originalPress(target);tidy();return result;
  }
  function update(next){const result=originalUpdate(next);tidy();return result;}
  function dispose(){if(!disposed){disposed=true;banner.removeFromParent();
    texture.dispose();material.dispose();geometry.dispose();}
   return originalDispose();
  }
  return Object.freeze({...ui,press,update,dispose,
   inspect:()=>({...originalInspect(),activeSculptOperation:activeOperation,
     controllerFollowMenu:true})});
 };
 window.SWYRL_ENGINE_VR_CONTROLLER_PALETTE_530=Object.freeze({inspect:()=>({
  ...stats,menuFollowsLeft:!!se350Record('left')?.gripTracked,
  transformActive:!!se340XR.gesture?.se530Continuous})});
})();
/* SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END */
