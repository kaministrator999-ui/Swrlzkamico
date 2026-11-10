/* SE390_MODEL_VR_GRAB_POSE_START */
// Pure gesture math. Only transient state on the gesture is updated; native
// descriptors, history, scene resources and the XR loop remain caller-owned.
function se390BeginPose(g,pose){
 if(!g||!pose?.position?.isVector3||!pose?.quaternion?.isQuaternion||
    !g.rootInverse?.isMatrix4||!g.rootQuaternion?.isQuaternion)
  throw TypeError('A tracked pose and native-root basis are required.');
 const finite=values=>values.every(Number.isFinite);
 if(!finite(pose.position.toArray())||!finite(pose.quaternion.toArray())||
    !finite(g.rootInverse.elements)||!finite(g.rootQuaternion.toArray())||
    pose.quaternion.lengthSq()<1e-12||g.rootQuaternion.lengthSq()<1e-12)
  throw TypeError('The gesture pose must be finite.');
 const basis=g.rootQuaternion.clone().normalize();
 g.se390Pose={
  inverse:g.rootInverse.clone(),basis,inverseBasis:basis.clone().invert(),
  position:pose.position.clone(),quaternion:pose.quaternion.clone().normalize(),height:pose.position.y,
  translation:new THREE.Vector3(),rotation:new THREE.Quaternion(),logScale:0,
  positionActive:false,rotationActive:false,heightActive:false,gain:null
 };
 return g.se390Pose;
}
function se390PoseCandidate(g,pose,options={}){
 let state=g?.se390Pose;
 if(!state)state=se390BeginPose(g,pose);
 if(!pose?.position?.isVector3||!pose?.quaternion?.isQuaternion||
    !pose.position.toArray().every(Number.isFinite)||!pose.quaternion.toArray().every(Number.isFinite)||
    pose.quaternion.lengthSq()<1e-12)
  throw TypeError('A finite tracked pose is required.');
 const gain=Number.isFinite(options.gain)?THREE.MathUtils.clamp(options.gain,0,1):1;
 const dt=Number.isFinite(options.dt)?THREE.MathUtils.clamp(options.dt,0,.05):0;
 const mode=g.mode,nowQ=pose.quaternion.clone().normalize();
 const rebased=state.gain!==null&&Math.abs(state.gain-gain)>1e-12;
 if(rebased){
  // A precision clutch changes future movement speed. Re-evaluating an old
  // total at the new gain would jump the already-previewed geometry.
  state.position.copy(pose.position);state.quaternion.copy(nowQ);state.height=pose.position.y;
 }
 state.gain=gain;
 if(!rebased){
  const fine=gain<1,positionThreshold=fine?.0005:.0015,angleThreshold=fine?.001:.003;
  if(mode==='move'||mode==='grab'){
   if(state.positionActive||pose.position.distanceTo(state.position)>=positionThreshold){
    const previous=state.position.clone().applyMatrix4(state.inverse);
    const next=pose.position.clone().applyMatrix4(state.inverse);
    state.translation.add(next.sub(previous).multiplyScalar(gain));
    state.position.copy(pose.position);state.positionActive=true;
   }
  }
  if(mode==='rotate'||mode==='grab'){
   if(state.rotationActive||nowQ.angleTo(state.quaternion)>=angleThreshold){
    const world=nowQ.clone().multiply(state.quaternion.clone().invert());
    const local=state.inverseBasis.clone().multiply(world).multiply(state.basis);
    const delta=new THREE.Quaternion().slerp(local,gain);
    state.rotation.premultiply(delta).normalize();
    state.quaternion.copy(nowQ);state.rotationActive=true;
   }
  }
  if(mode==='scale'){
   const dy=pose.position.y-state.height;
   if(state.heightActive||Math.abs(dy)>=positionThreshold){
    state.logScale+=2.4*dy*gain;state.height=pose.position.y;state.heightActive=true;
   }
  }else if(mode==='grab'){
   const axis=Number.isFinite(options.scaleAxis)?THREE.MathUtils.clamp(options.scaleAxis,-1,1):0;
   state.logScale-=axis*dt*1.4*gain;
  }
 }
 state.logScale=THREE.MathUtils.clamp(state.logScale,-Math.log(10000),Math.log(10000));
 if(Math.abs(state.logScale)<1e-12)state.logScale=0;
 for(let i=0;i<3;i++)if(Math.abs(state.translation.getComponent(i))<1e-12)state.translation.setComponent(i,0);
 // Normalize the sign as well as length: q and -q are the same pose, and
 // exact return-to-origin must remain a native no-op rather than a new edit.
 if(state.rotation.w<0)state.rotation.set(-state.rotation.x,-state.rotation.y,-state.rotation.z,-state.rotation.w);
 if(Math.hypot(state.rotation.x,state.rotation.y,state.rotation.z)<1e-12)state.rotation.identity();
 const translation=state.translation.clone(),rotation=state.rotation.clone();
 let scale=Math.exp(state.logScale);
 if(options.snap){
  for(let i=0;i<3;i++)translation.setComponent(i,Math.round(translation.getComponent(i)/.01)*.01||0);
  const degrees=Number.isFinite(options.snapDegrees)?THREE.MathUtils.clamp(options.snapDegrees,1,90):15;
  const step=THREE.MathUtils.degToRad(degrees),euler=new THREE.Euler().setFromQuaternion(rotation,'XYZ');
  euler.set(...euler.toArray().slice(0,3).map(value=>Math.round(value/step)*step));
  rotation.setFromEuler(euler);
  scale=Math.max(.05,1+Math.round((scale-1)/.05)*.05);
 }
 return {translation:translation.toArray(),rotation:rotation.toArray(),scale};
}
/* SE390_MODEL_VR_GRAB_POSE_END */
