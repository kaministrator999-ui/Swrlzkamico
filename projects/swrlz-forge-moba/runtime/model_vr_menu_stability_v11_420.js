/* SE420_MODEL_VR_MENU_STABILITY_START
 * Source-owned patch on top of the existing XR controller pipeline.
 * Prefer actual panel button hits over the native 1.2m empty-ray fallback,
 * without stealing hits from a physically nearer native tool card.
 * Never parent menus to the model rig, viewer, or tracking controllers.
 */
(function se420ModelVRMenuStability(){
 'use strict';
 const quest=()=>se340XR.se413Quest;
 const live=()=>!!(quest()?.root?.parent&&quest()?.root?.visible&&se340VisibleSession());
 let hoverChanges=0,buttonPresses=0,questHits=0;
 function pick(record){
  const box=quest();
  if(!live()||!record?.targetTracked||!record?.target)return null;
  const cast=se340Cast(record);if(!cast)return null;
  box.root.updateWorldMatrix(true,true);
  const candidates=(box.folded?box.buttons:[...box.buttons,box.panel])
   .filter(item=>item.visible&&item.parent===box.root);
  const hit=cast.intersectObjects(candidates,false)[0];
  if(!hit)return null;
  questHits++;
  return {ui:true,quest:true,target:hit.object,
   action:hit.object.userData?.se340Action||null,
   distance:hit.distance,point:hit.point};
 }
 const beforeHit=se340Hit;
 se340Hit=function(record,precise=true){
  const existing=beforeHit.call(this,record,precise),tutorial=pick(record);
  if(!tutorial)return existing;
  if(existing?.quest)return existing;
  // Native fallback ray point is NOT physical geometry: allow clicks beyond
  // 1.2m, where the v11.413 distance comparison previously lost them.
  if((existing?.ui||existing?.id)&&Number.isFinite(existing.distance)
   &&existing.distance<tutorial.distance-.008)return existing;
  return tutorial;
 };
 const beforeTrigger=se340Trigger;
 se340Trigger=function(record,additive=false){
  const hit=record?.targetTracked?se340Hit(record,false):null,box=quest();
  if(hit?.quest&&hit.action&&box){
   box.pressedAction=hit.action;
   box.pressedUntilFrame=se340XR.frameCount+13;
   box.signature='';buttonPresses++;
  }
  return beforeTrigger.call(this,record,additive);
 };
 const beforeFrame=se340ModelXRFrameCore;
 se340ModelXRFrameCore=function(...args){
  const result=beforeFrame.apply(this,args),box=quest();
  if(!box)return result;
  const hovered=se340XR.controllers?.map(record=>record.hit)
   .find(hit=>hit?.quest&&hit?.action)?.action||null;
  if(box.hoverAction!==hovered){
   box.hoverAction=hovered;box.signature='';hoverChanges++;
  }
  if(box.pressedAction&&se340XR.frameCount>box.pressedUntilFrame){
   box.pressedAction=null;box.signature='';
  }
  // The tutorial remains directly scene-owned; camera orbit is free to
  // change the viewer, never this panel's transform.
  return result;
 };
 window.SWYRL_ENGINE_VR_MENU_STABILITY_420=Object.freeze({
  inspect:()=>({
   panelActive:live(),panelParentIsScene:quest()?.root?.parent===se340XR.scene,
   panelPositioned:!!quest()?.positioned,panelUserPositioned:!!quest()?.userPositioned,
   hoverAction:quest()?.hoverAction||null,pressedAction:quest()?.pressedAction||null,
   hoverChanges,buttonPresses,questHits,
   panelWorldScale:quest()?.root?.getWorldScale?.(new THREE.Vector3())?.toArray?.()||null,
   toolMenuWorldScale:se340XR.ui?.root?.getWorldScale?.(new THREE.Vector3())?.toArray?.()||null
  }),
  pick
 });
})();
 /* SE420_MODEL_VR_MENU_STABILITY_END */