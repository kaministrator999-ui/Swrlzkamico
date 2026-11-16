/* SE476_RESUME_CAMERA_START */
// Same original ModelAtelier closure, same orbit and camera primitives.
// Restores view-only navigation, never mesh data/history/UV geometry.
window.SWYRL_ENGINE_STARTUP_CAMERA_476=Object.freeze({
 restore(saved){
  if(!saved||!camera||!panel||panel.hidden||se340ModelBridge?.isBorrowed?.())return false;
  const p=saved.position,t=saved.target;
  if(![p,t].every(a=>Array.isArray(a)&&a.length===3&&a.every(v=>Number.isFinite(v)&&Math.abs(v)<100000)))return false;
  const dx=p[0]-t[0],dy=p[1]-t[1],dz=p[2]-t[2],distance=Math.hypot(dx,dy,dz);
  if(!(distance>.25&&distance<10000))return false;
  if(['perspective','orthographic'].includes(saved.projection)){
   se430ModelCamera.setProjection(saved.projection);
  }
  atelierDetailTarget=new THREE.Vector3(t[0],t[1],t[2]);
  atelierCameraPan.set(0,0,0);
  orbit.distance=distance;
  orbit.yaw=Math.atan2(dx,dz);
  orbit.pitch=THREE.MathUtils.clamp(Math.asin(Math.max(-1,Math.min(1,dy/distance))),-1.54,1.54);
  cameraUpdate();
  se430ModelCamera.refresh();
  return true;
 }
});
/* SE476_RESUME_CAMERA_END */