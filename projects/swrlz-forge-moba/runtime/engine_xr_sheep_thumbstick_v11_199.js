// §E v11.199 — Sheep Tag immersive VR: left stick controls the animal,
// with an automatic, wider, tracked-eye follow camera. No new game clock,
// WebXR renderer, saved map mutations, or changes to desktop/mobile input.
const se199={
  defaultZoom:1.4,controlledId:null,movementFrames:0,releaseCount:0,
  cameraSnaps:0,lastDirection:null,lastError:''
};
function se199Gameplay(){
  return se195Gameplay()&&!!stSession&&!stSession.simulate;
}
function se199StickIntent(){
  const left=se192InputRecord('left');
  const stick=se192Stick(left); // Existing deadzone and device-specific axes.
  const strength=Math.min(1,Math.hypot(stick.x,stick.y));
  if(!left?.input?.gamepad||strength<.06)return {strength:0,x:0,z:0};
  // Forward is the strategic camera's view heading, not an arbitrary map axis.
  // Keep natural headset look independent of the sheep's direction of travel.
  const forward=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
  const right=new THREE.Vector3(-forward.z,0,forward.x);
  const direction=forward.multiplyScalar(-stick.y).addScaledVector(right,stick.x);
  if(direction.lengthSq()<.000001)return {strength:0,x:0,z:0};
  direction.normalize();
  return {strength,x:direction.x,z:direction.z};
}
function se199Drive(unit,dt,original){
  const s=stSession;
  if(!se199Gameplay()||!unit||unit.id!==s.controlledId)
    return original(unit,dt);
  if(paused||s.winner)return original(unit,dt);
  const intent=se199StickIntent();
  if(intent.strength===0){
    if(unit.order?.vrStick){stSetOrder(unit,null);se199.releaseCount++;}
    if(unit.captured&&se199.controlledId===unit.id)unit.spiritOrder=null;
    return original(unit,dt);
  }
  if(unit.kind==='wolf'&&s.elapsed<s.rules.headstart)
    return original(unit,dt);
  if(unit.isIllusion)return original(unit,dt);
  if(!unit.captured){
    const direction=new THREE.Vector3(intent.x,0,intent.z);
    const context={rules:s.rules,obstacles:stObstacles()};
    const radius=stUnitRadius(unit);
    let target=null;
    // Match the proven touch joystick: short sweep, then wall-slide.
    // Do not turn a thumbstick into a lengthy click-to-move detour.
    for(const distance of [1.2,.6,.3,.12]){
      const point=unit.pos.clone().addScaledVector(direction,distance);
      if(stSegmentClear(context,unit.pos,point,radius)){target=point;break;}
    }
    if(!target){
      const axes=Math.abs(intent.x)>Math.abs(intent.z)?['x','z']:['z','x'];
      for(const axis of axes){
        const point=unit.pos.clone();
        point[axis]+=intent[axis]*.35;
        if(point.distanceToSquared(unit.pos)>.0001&&
            stSegmentClear(context,unit.pos,point,radius)){
          target=point;break;
        }
      }
    }
    if(target){
      // Only begin one native order per continuous gesture. Updating the
      // destination in-place avoids re-pathing the entire map at XR FPS.
      if(!unit.order?.vrStick){
        unit.archiveRoute=null;
        stSetOrder(unit,{action:'move',x:target.x,z:target.z,vrStick:true});
      }else{
        unit.order.x=target.x;unit.order.z=target.z;
        unit.destination.copy(target);
      }
    }else if(unit.order?.vrStick)stSetOrder(unit,null);
  }else{
    const p=unit.spirit?.position;
    if(p){
      const pen=s.pen;
      unit.spiritOrder={
        x:THREE.MathUtils.clamp(p.x+intent.x,pen.x-pen.halfX+.8,pen.x+pen.halfX-.8),
        z:THREE.MathUtils.clamp(p.z+intent.z,pen.z-pen.halfZ+.8,pen.z+pen.halfZ-.8)
      };
    }
  }
  se199.lastDirection={x:intent.x,z:intent.z,strength:intent.strength};
  se199.movementFrames++;
  const originalSpeed=unit.speed;
  unit.speed=originalSpeed*intent.strength;
  try{return original(unit,dt);}finally{unit.speed=originalSpeed;}
}
const se199PreviousSheep=stUpdateSheep,se199PreviousWolf=stUpdateWolf;
stUpdateSheep=function(unit,dt){return se199Drive(unit,dt,se199PreviousSheep);};
stUpdateWolf=function(unit,dt){return se199Drive(unit,dt,se199PreviousWolf);};
// Override only the immersive Sheep camera adapter. This deliberately avoids
// the v11.195 left-stick camera-pan branch and preserves the v11.196 one-time
// XR reference-space snap/anchor and the v11.198 editor-only free-flight path.
se195FollowCamera=function(dt){
  if(!se199Gameplay())return;
  const s=stSession,unit=s.units.find(u=>u.id===s.controlledId);
  if(!unit?.pos)return;
  const pose=se191XRHeadPose();
  if(!pose)return;
  if(!se195.rigReady||se199.controlledId!==unit.id){
    const forward=pose.forward.clone().setY(0);
    if(forward.lengthSq()<.001)forward.set(0,0,-1);
    forward.normalize();
    se193.angle=Math.atan2(forward.x,forward.z);
    se193.focus.set(unit.pos.x,0,unit.pos.z);
    se193.follow=true;
    se193.zoom=se199.defaultZoom;
    const target=se193.focus.clone().addScaledVector(forward,-25*se193.zoom);
    target.y=17*se193.zoom;
    const delta=target.sub(pose.eye);
    if(delta.lengthSq()>.0004&&!se195MoveRig(delta.x,delta.y,delta.z))return;
    se195.rigReady=true;se195.rigAt=0;
    se199.controlledId=unit.id;se199.cameraSnaps++;
    return; // No uncomfortable 25m fly-in when the match starts.
  }
  const right=se192Stick(se192InputRecord('right'));
  if(!se195.photo){
    se193.angle+=right.x*dt*.70;
    se193.zoom=THREE.MathUtils.clamp(se193.zoom+right.y*dt*.55,1,2.5);
  }
  if(se193.follow){
    const target=new THREE.Vector3(unit.pos.x,0,unit.pos.z);
    se193.focus.lerp(target,Math.min(1,Math.max(0,dt)*8));
  }
  const bound=Number(s.rules?.bounds)||40;
  se193.focus.x=THREE.MathUtils.clamp(se193.focus.x,-bound,bound);
  se193.focus.z=THREE.MathUtils.clamp(se193.focus.z,-bound,bound);
  const forward=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
  const wanted=se193.focus.clone().addScaledVector(forward,-25*se193.zoom);
  wanted.y=17*se193.zoom;
  const delta=wanted.sub(pose.eye),maxStep=Math.max(0,dt*18);
  if(maxStep&&delta.length()>maxStep)delta.setLength(maxStep);
  if(delta.lengthSq()>.0004)se195MoveRig(delta.x,delta.y,delta.z);
};
const se199PreviousStart=se193XRStart;
se193XRStart=function(){
  se199PreviousStart();
  se199.controlledId=null;
  se199.movementFrames=0;se199.cameraSnaps=0;se199.releaseCount=0;
  se199.lastDirection=null;
  se193.zoom=se199.defaultZoom;
};
const se199PreviousCleanup=se193XRCleanup;
se193XRCleanup=function(){
  const s=stSession,unit=s?.units?.find(u=>u.id===s.controlledId);
  if(unit?.order?.vrStick)stSetOrder(unit,null);
  if(unit?.captured&&se199.controlledId===unit.id)unit.spiritOrder=null;
  se199.controlledId=null;se199.lastDirection=null;
  se199PreviousCleanup();
};
window.SWYRL_ENGINE_SHEEP_VR_THUMBSTICK_199=Object.freeze({
  diagnose:()=>({active:se199Gameplay(),trackedUnit:se199.controlledId,
    cameraFollow:se193.follow,zoom:se193.zoom,defaultZoom:se199.defaultZoom,
    movementFrames:se199.movementFrames,cameraSnaps:se199.cameraSnaps,
    releases:se199.releaseCount,lastDirection:se199.lastDirection,
    lastError:se199.lastError})
});
