// §E v11.309: use native target-ray pose in Arcane and remove BOTH ray renderers.
// v11.308 hid the se181 legacy line, but se192 renders an independent 3D
// tapered beam and reticle (and can apply saved per-controller yaw trim).
// Keep raycasts and spell direction live: only suppress visible objects.
const se309Ray={active:false,frames:0,suppressed:0};
function se309ArcaneRayless(){
 return !!se181XR.session&&renderer.xr.isPresenting&&
   currentProject?.kind===se279GameId;
}
function se309HideRayGraphics(record){
 if(!record)return;
 if(record.ray)record.ray.visible=false;
 if(record.se192){
  // The raw XR target-ray controller is the aim authority for Arcane.
  // Spatial Editor AIM trim remains owned by the other editor projects.
  record.se192.pivot.rotation.y=0;
  record.se192.beam.visible=false;
  record.se192.dot.visible=false;
  se309Ray.suppressed++;
 }
}
// Hide even if a later wrapper renders/reenables the tapered ray.
const se309PreviousRenderRay=se192RenderRay;
se192RenderRay=function(record,hit){
 if(se309ArcaneRayless()){
  se309HideRayGraphics(record);
  return; // native raycasts / trigger inputs are handled elsewhere
 }
 const extra=record?.se192;
 if(extra){
  extra.pivot.rotation.y=se192.savedAim[record.index]||0;
  if(se309Ray.active)extra.beam.visible=true;
 }
 const result=se309PreviousRenderRay(record,hit);
 // The old debug line never needs to overlap the spatial editor beam.
 if(extra&&record.ray)record.ray.visible=false;
 return result;
};
const se309PreviousVRFrame=se192VRFrame;
se192VRFrame=function(){
 const active=se309ArcaneRayless();
 // Fix the pose BEFORE hit tests, including when Arcane is first entered.
 if(active)for(const record of se181XR.controllers)
  if(record?.se192)record.se192.pivot.rotation.y=0;
 const out=se309PreviousVRFrame();
 if(active){
  // Post-frame guard for wrappers that may re-enable their beam geometry.
  for(const record of se181XR.controllers)se309HideRayGraphics(record);
 }else if(se309Ray.active){
  // Restore normal editor yaw trims and beam ownership after project switch.
  for(const record of se181XR.controllers){
   if(!record?.se192)continue;
   record.se192.pivot.rotation.y=se192.savedAim[record.index]||0;
   record.se192.beam.visible=true;
   if(record.ray)record.ray.visible=false;
  }
 }
 se309Ray.active=active;
 se309Ray.frames++;
 return out;
};
window.SWYRL_ENGINE_ARCANE_RAY_309=Object.freeze({
 status:()=>({active:se309ArcaneRayless(),frames:se309Ray.frames,
  suppressed:se309Ray.suppressed,aimSource:'native WebXR target ray',
  visualBeams:se309ArcaneRayless()?0:undefined})
});
