/* SE434_SHEEP_VISIBLE_FRAME_RECOVERY_START */
// A crowded GPU frame is not an OS focus change. Keep explicit WebXR/browser
// visibility and input-release recovery authoritative; never alter head poses.
const se434VisibleRecovery={longVisibleGaps:0,lastGapMs:0,maxGapMs:0};
const se434PriorOnFrame=se211OnFrame;
se211OnFrame=function(){
 const now=performance.now(),gap=se211.lastFrame>0?now-se211.lastFrame:0;
 const session=se181XR.session,s=stSession;
 if(s&&!s.simulate&&s.buildings?.length>=16&&se195Gameplay()&&
    session?.visibilityState==='visible'&&se211.lastVisible==='visible'&&
    document.visibilityState==='visible'&&!se238NativeMenuOpen()&&
    !se211.pendingRelease&&now>=se211.returnUntil&&gap>=650&&gap<5000){
  se434VisibleRecovery.longVisibleGaps++;se434VisibleRecovery.lastGapMs=gap;
  se434VisibleRecovery.maxGapMs=Math.max(se434VisibleRecovery.maxGapMs,gap);
  // The original observer still runs, sees native focus, refreshes cosmetics
  // and handles real events. Avoid only its extra false 300ms input blackout.
  se211.lastFrame=now;
 }
 return se434PriorOnFrame.apply(this,arguments);
};
window.SWYRL_ENGINE_SHEEP_VISIBLE_RECOVERY_434=Object.freeze({
 diagnose:()=>({...se434VisibleRecovery,nativeHeadPoseUnchanged:true,
  explicitVisibilityAndInputReleasePreserved:true})
});
/* SE434_SHEEP_VISIBLE_FRAME_RECOVERY_END */
