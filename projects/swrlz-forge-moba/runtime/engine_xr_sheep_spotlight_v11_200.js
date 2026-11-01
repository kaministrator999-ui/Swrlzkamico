// §E v11.200 — Sheep Tag VR: stabilized sheep-anchored overhead spotlight.
// Preserve true Quest headset look; never force/pitch the tracked head.
// No new scene, renderer, simulation clock, or persistence of authored actors.
const se200={
  horizontal:14,vertical:26,defaultZoom:1.4,
  trackedUnit:null,applied:new THREE.Vector3(),anchorReady:false,
  cameraSnaps:0,referenceWrites:0,idleFrames:0,moveFrames:0,
  collidedFrames:0,buildingsAtLastFrame:0,spiritHeld:false,
  stickHeld:false,lastError:''
};
function se200Active(){
  return se199Gameplay()&&!(typeof se150Match!=='undefined'&&
    se150Match.active&&se150Match.role==='guest');
}
function se200MoveUnit(unit,dt,next){
  const s=stSession;
  if(!se200Active()||!unit||unit.id!==s.controlledId)
    return next(unit,dt);
  const intent=se199StickIntent();
  const enabled=!paused&&!s.winner&&!unit.isIllusion&&
    !(unit.kind==='wolf'&&s.elapsed<s.rules.headstart);
  if(!enabled||intent.strength<.06){
    if(se200.stickHeld){se199.releaseCount++;se200.stickHeld=false;}
    if(se200.spiritHeld){unit.spiritOrder=null;se200.spiritHeld=false;}
    // Original gameplay still performs rescue, capture and build completion.
    return next(unit,dt);
  }
  se200.stickHeld=true;
  // Direct human input cancels click-to-move / autonomous build approach.
  // Unlike v11.199, this does not issue a fresh A* route every XR game tick.
  if(unit.order){
    stSetOrder(unit,null);
  }
  if(unit.captured){
    const spirit=unit.spirit?.position,pen=s.pen;
    if(spirit){
      unit.spiritOrder={
        x:THREE.MathUtils.clamp(spirit.x+intent.x,pen.x-pen.halfX+.8,pen.x+pen.halfX-.8),
        z:THREE.MathUtils.clamp(spirit.z+intent.z,pen.z-pen.halfZ+.8,pen.z+pen.halfZ-.8)
      };
      se200.spiritHeld=true;
    }
  }else{
    const step=Math.min(.05,Math.max(0,Number(dt)||0))*unit.speed*intent.strength;
    if(step>0){
      // Reuse the native current obstacles once per simulation tick. Swept
      // collision with a short step keeps houses solid even when FPS drops.
      const context={rules:s.rules,obstacles:stObstacles()};
      const radius=stUnitRadius(unit),before=unit.pos.clone();
      const dx=intent.x*step,dz=intent.z*step;
      const clear=(x,z)=>stSegmentClear(context,unit.pos,{x,z},radius);
      let x=before.x,z=before.z;
      if(clear(before.x+dx,before.z+dz)){x+=dx;z+=dz;}
      else if(Math.abs(dx)>=Math.abs(dz)){
        if(clear(before.x+dx,before.z))x+=dx;
        if(clear(x,before.z+dz))z+=dz;
      }else{
        if(clear(before.x,before.z+dz))z+=dz;
        if(clear(before.x+dx,z))x+=dx;
      }
      if(x!==before.x||z!==before.z){
        unit.pos.x=x;unit.pos.z=z;
        unit.actor.rotation.y=Math.atan2(x-before.x,z-before.z);
        stPlaceUnit(unit);se200.moveFrames++;
      }else{se200.collidedFrames++;}
    }
  }
  se199.movementFrames++;
  se199.lastDirection={x:intent.x,z:intent.z,strength:intent.strength};
  return next(unit,dt);
}
// Call the original authoritative Sheep Tag update beneath v11.199's
// pathfinding drive; this prevents competing move orders on each tick.
const se200OldVRSheep=stUpdateSheep,se200OldVRWolf=stUpdateWolf;
stUpdateSheep=function(unit,dt){
  if(!se200Active())return se200OldVRSheep(unit,dt);
  return se200MoveUnit(unit,dt,se199PreviousSheep);
};
stUpdateWolf=function(unit,dt){
  if(!se200Active())return se200OldVRWolf(unit,dt);
  return se200MoveUnit(unit,dt,se199PreviousWolf);
};
function se200CameraAnchor(){
  const front=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
  const wanted=se193.focus.clone().addScaledVector(front,-se200.horizontal*se193.zoom);
  wanted.y=se193.focus.y+se200.vertical*se193.zoom;
  return wanted; // Exactly zero lateral offset from the controlled sheep.
}
se195FollowCamera=function(dt){
  if(!se200Active())return;
  const s=stSession,unit=s.units.find(u=>u.id===s.controlledId);
  if(!unit?.pos)return;
  const timeStep=Math.min(.05,Math.max(0,Number(dt)||0));
  if(!se195.rigReady||!se200.anchorReady||se200.trackedUnit!==unit.id){
    const pose=se191XRHeadPose();
    if(!pose)return;
    const heading=pose.forward.clone().setY(0);
    // Looking nearly straight down has ambiguous yaw: retain last heading.
    if(heading.lengthSq()>.01){
      heading.normalize();se193.angle=Math.atan2(heading.x,heading.z);
    }
    se193.zoom=se200.defaultZoom;
    se193.follow=true;
    se193.focus.set(unit.pos.x,unit.pos.y||0,unit.pos.z);
    const wanted=se200CameraAnchor();
    const offset=wanted.clone().sub(pose.eye);
    if(offset.lengthSq()>.0004&&!se195MoveRig(offset.x,offset.y,offset.z))return;
    se200.applied.copy(wanted);
    se200.anchorReady=true;se200.trackedUnit=unit.id;
    se195.rigReady=true;se195.rigAt=0;se200.cameraSnaps++;
    return; // No repeated relocation during match play.
  }
  const right=se192Stick(se192InputRecord('right'));
  if(!se195.photo){
    se193.angle+=right.x*timeStep*.70;
    se193.zoom=THREE.MathUtils.clamp(se193.zoom+right.y*timeStep*.55,1,2.5);
  }
  if(se193.follow){
    const target=new THREE.Vector3(unit.pos.x,unit.pos.y||0,unit.pos.z);
    se193.focus.lerp(target,1-Math.exp(-timeStep*9));
  }
  const bound=Number(s.rules?.bounds)||40;
  se193.focus.x=THREE.MathUtils.clamp(se193.focus.x,-bound,bound);
  se193.focus.z=THREE.MathUtils.clamp(se193.focus.z,-bound,bound);
  const wanted=se200CameraAnchor();
  // Never chase the live HMD eye after the initial snap. Head movement is
  // owned by WebXR and must not feed back into headset-space translation.
  const remaining=wanted.sub(se200.applied);
  if(remaining.lengthSq()<.000625){se200.idleFrames++;return;}
  const delta=remaining.multiplyScalar(1-Math.exp(-timeStep*9));
  const maxStep=timeStep*13;
  if(maxStep>0&&delta.length()>maxStep)delta.setLength(maxStep);
  if(delta.lengthSq()<.000004){se200.idleFrames++;return;}
  if(se195MoveRig(delta.x,delta.y,delta.z)){
    se200.applied.add(delta);se200.referenceWrites++;
  }else se200.lastError='XR reference space translation unavailable';
};
const se200PreviousSnap=se193XRSnapFollow;
se193XRSnapFollow=function(){
  se200.anchorReady=false;se200.trackedUnit=null;
  return se200PreviousSnap();
};
const se200PreviousStart=se193XRStart;
se193XRStart=function(){
  se200PreviousStart();
  se200.anchorReady=false;se200.trackedUnit=null;
  se200.applied.set(0,0,0);
  se200.cameraSnaps=se200.referenceWrites=se200.idleFrames=0;
  se200.moveFrames=se200.collidedFrames=0;
  se200.spiritHeld=se200.stickHeld=false;
  se200.lastError='';
};
const se200PreviousCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se200.anchorReady=false;se200.trackedUnit=null;
  se200.spiritHeld=se200.stickHeld=false;
  return se200PreviousCleanup();
};
window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200=Object.freeze({
  diagnose:()=>({
    active:se200Active(),trackedUnit:se200.trackedUnit,
    follow:se193.follow,zoom:se193.zoom,
    overheadAngleDegrees:Math.round(Math.atan2(se200.vertical,se200.horizontal)*180/Math.PI),
    cameraSnaps:se200.cameraSnaps,
    followReferenceWrites:se200.referenceWrites,idleFrames:se200.idleFrames,
    joystickMoveFrames:se200.moveFrames,collidedFrames:se200.collidedFrames,
    buildings:stSession?.buildings?.length||0,lastError:se200.lastError
  })
});
