/* SE520_VR_INTERACTION_REPAIR_START
 * Immersive WebXR only; all project, menu, grip and surface editing remain
 * owned by the existing native engine and controller profile.
 */
const se520QuestXRRepair=(()=>{
 'use strict';
 const stats={faces:0,triggerArmed:0,triggerActivated:0};
 const baseUpdate=se340UpdateGesture;
 se340UpdateGesture=function(...args){
  const g=se340XR.gesture;
  if(g?.se520DirectTrigger&&!g.se520Activated){
   const pose=se340GripPose(g.record);
   if(!pose||!g.record?.targetTracked||!g.record?.gripTracked)return;
   // Hand pose jitter at the moment of a trigger click must be a no-op.
   // A genuine held drag crosses 14mm; rebase the accumulated native pose
   // so the model does not jump when continuous preview activates.
   if(pose.position.distanceTo(g.hand.position)<.014)return;
   g.se520Activated=true;stats.triggerActivated++;
   g.hand.position.copy(pose.position);
   if(g.se390Pose){g.se390Pose.position.copy(pose.position);g.se390Pose.positionActive=false;}
   se340Notice('Trigger moving model · hold and move controller · release saves · B cancels.');
   return;
  }
  return baseUpdate.apply(this,args);
 };
 const baseFrame=se372Frame;
 se372Frame=function(s){
  const result=baseFrame.apply(this,arguments);
  const viewer=s.lastViewer,root=s.ui?.root;
  // Orient the ORIGINAL three-stage spatial menu every XR frame, including
  // while its Grip-based placement is being dragged. Never recenter its
  // position, reparent it, change active hit meshes or rotate model geometry.
  if(s.session&&se340VisibleSession()&&root?.visible&&
    viewer?.position?.isVector3&&root.parent&&
    viewer.position.distanceToSquared(root.getWorldPosition(new THREE.Vector3()))>.004){
   root.lookAt(viewer.position);
   root.updateWorldMatrix(true,true);
   stats.faces++;
  }
  return result;
 };
 return Object.freeze({inspect:()=>({facingFrames:stats.faces,
  triggerActivations:stats.triggerActivated,
  activeDirectTrigger:!!se340XR.gesture?.se520DirectTrigger,
  menuWorldPosition:se340XR.ui?.root?.getWorldPosition?.(new THREE.Vector3()).toArray()||null})});
})();
window.SWYRL_ENGINE_VR_INTERACTION_REPAIR_520=se520QuestXRRepair;
/* SE520_VR_INTERACTION_REPAIR_END */
