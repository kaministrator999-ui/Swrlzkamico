// §E v11.239 — eliminate the OLD native editor actor raycast in Sheep Tag XR.
// The old engine (v11.181) still intersected every scene actor and all nested
// meshes for BOTH controllers EVERY XR frame, even in game Play. §E v11.192+
// already provides a separate authoritative controller/gameplay input path.
// Keep the native EXIT VR target working, preserve editing raycasts outside
// Sheep Tag, and never change headset pose, reference space or projection.
const se239XR={
  gameplayRaySamples:0,legacyActorRaycastsSkipped:0,
  exitHits:0,session:null,lastAt:0,frameSamples:0,
  gapsOver20ms:0,gapsOver35ms:0,gapsOver70ms:0,
  longestGapMs:0,lastGapMs:0,
  recent:new Array(60),recentCount:0,recentIndex:0,
  uiOpenGapCount:0,normalGapCount:0,
  lastError:''
};
const se239ExitRay=new THREE.Raycaster(
 new THREE.Vector3(),new THREE.Vector3(0,0,-1),.05,24
);
const se239NativeRay=se181XRRaycast;
se181XRRaycast=function(record){
  if(!renderer.xr.isPresenting||!se181XR.session||
     !se193XRGameActive())return se239NativeRay(record);
  // During Play, native editor selection is disabled already by v11.181.
  // Preserve target selection of the unique always-available EXIT VR panel.
  se239XR.gameplayRaySamples++;
  const panel=se181XR.exitSurface;
  if(!panel?.visible||!record?.controller){
    se239XR.legacyActorRaycastsSkipped++;return null;
  }
  const controller=record.controller;
  controller.updateMatrixWorld(true);
  se239ExitRay.ray.origin.setFromMatrixPosition(controller.matrixWorld);
  se239ExitRay.ray.direction.set(0,0,-1)
    .transformDirection(controller.matrixWorld).normalize();
  const hit=se239ExitRay.intersectObject(panel,false)[0];
  se239XR.legacyActorRaycastsSkipped++;
  if(hit){se239XR.exitHits++;return {exit:true,distance:hit.distance};}
  return null;
};
const se239PriorXRRender=se181XRRender;
se181XRRender=function(){
  const game=renderer.xr.isPresenting&&se193XRGameActive();
  const session=se181XR.session;
  const now=performance.now();
  if(session!==se239XR.session){
    se239XR.session=session;se239XR.lastAt=0;
    se239XR.recentCount=0;se239XR.recentIndex=0;
  }
  if(!game){
    se239XR.lastAt=0;
    return se239PriorXRRender();
  }
  const gap=se239XR.lastAt?now-se239XR.lastAt:0;
  se239XR.lastAt=now;
  if(gap>0&&gap<30000){
    se239XR.frameSamples++;
    se239XR.lastGapMs=gap;
    se239XR.longestGapMs=Math.max(se239XR.longestGapMs,gap);
    if(gap>20)se239XR.gapsOver20ms++;
    if(gap>35)se239XR.gapsOver35ms++;
    if(gap>70)se239XR.gapsOver70ms++;
    if(gap>35){
      if(se195.visible||se204.wheel?.root?.visible)se239XR.uiOpenGapCount++;
      else se239XR.normalGapCount++;
    }
    se239XR.recent[se239XR.recentIndex]=gap;
    se239XR.recentIndex=(se239XR.recentIndex+1)%se239XR.recent.length;
    se239XR.recentCount=Math.min(se239XR.recentCount+1,se239XR.recent.length);
  }
  return se239PriorXRRender();
};
const se239PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se239XR.session=null;se239XR.lastAt=0;
  return se239PriorCleanup();
};
window.SWYRL_ENGINE_QUEST_HEADTURN_239=Object.freeze({
 diagnose:()=>{
  let sum=0;
  for(let i=0;i<se239XR.recentCount;i++)sum+=se239XR.recent[i]||0;
  return {
    active:renderer.xr.isPresenting&&se193XRGameActive(),
    nativeHeadTrackingChanged:false,stereoViewChanged:false,
    physicsChanged:false,controllerMappingChanged:false,
    editorRaycastsPreserved:true,exitVrTargetPreserved:true,
    gameRaySamples:se239XR.gameplayRaySamples,
    duplicateActorRaycastsPrevented:se239XR.legacyActorRaycastsSkipped,
    exitPanelHits:se239XR.exitHits,
    frameSamples:se239XR.frameSamples,
    recentMeanCallbackGapMs:se239XR.recentCount?
      +(sum/se239XR.recentCount).toFixed(2):0,
    gapOver20ms:se239XR.gapsOver20ms,
    gapOver35ms:se239XR.gapsOver35ms,
    gapOver70ms:se239XR.gapsOver70ms,
    worstCallbackGapMs:+se239XR.longestGapMs.toFixed(1),
    lastCallbackGapMs:+se239XR.lastGapMs.toFixed(1),
    largeGapsWhileMenuOpen:se239XR.uiOpenGapCount,
    largeGapsWithoutMenu:se239XR.normalGapCount,
    lastError:se239XR.lastError
  };
 }
});
