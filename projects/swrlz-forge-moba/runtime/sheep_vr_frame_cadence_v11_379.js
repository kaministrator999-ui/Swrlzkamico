// §E v11.379 — Sheep Tag Quest: distinguish a slow app frame from OS focus
// loss. WebXR owns the frame loop, stereo compositor and headset tracking.
// All counters are observational; no new render/simulation loop is created.
const se379Frame={
  sceneGaps:0,lastSceneGapMs:0,maxSceneGapMs:0,
  lastPreset:'auto',lastXRScale:.72,framebufferChoices:0
};
const se379PreviousOnFrame=se211OnFrame;
se211OnFrame=function(){
  const now=performance.now();
  const gap=se211.lastFrame>0?now-se211.lastFrame:0;
  const playingSheep=se195Gameplay()&&!!stSession&&!stSession.simulate;
  // Quest can miss several WebXR callbacks while the page is still
  // visibly presenting Sheep Tag. A 170-650ms game hitch alone is not
  // proof that the Quest OS owns focus. The v11.211 fallback previously
  // suppressed game camera/controller updates for ANOTHER 300ms here.
  // Keep explicit XR visibility changes, actual pending-input release,
  // startup/resume recovery and >650ms loss-of-callback safeguards intact.
  if(playingSheep&&!se238NativeMenuOpen()&&
     se211Visibility()==='visible'&&se211.lastVisible==='visible'&&
     document.visibilityState==='visible'&&
     !se211.pendingRelease&&now>=se211.returnUntil&&
     gap>170&&gap<650){
    se379Frame.sceneGaps++;
    se379Frame.lastSceneGapMs=Math.round(gap);
    se379Frame.maxSceneGapMs=Math.max(se379Frame.maxSceneGapMs,gap);
    // The immediately following original observer still runs and refreshes
    // visibility/cosmetics. Only its incorrect OS-blur inference is avoided.
    se211.lastFrame=now;
  }
  return se379PreviousOnFrame();
};
// v11.195 hard-coded Sheep Tag's XR eye framebuffer to .72 for EVERY
// graphics preset. Honor the preset selected BEFORE entering VR so Low
// and High really differ in immersive mode; do not realloc in-session.
// Other games, 2D graphics, native eye matrices and headset refresh remain.
const se379PreviousFramebuffer=se191XRPrepareFramebuffer;
se191XRPrepareFramebuffer=function(){
  if(currentProject?.kind!=='sheep-tag')return se379PreviousFramebuffer();
  const prefs=performancePrefs||{};
  const preset=String(prefs.preset||'auto');
  const scales={mobile:.58,low:.60,medium:.72,high:.86,auto:.72};
  const chosen=preset==='custom'
    ?Math.min(.90,Math.max(.55,Number(prefs.renderScale)||.72))
    :(scales[preset]??.72);
  se191XR.framebufferScale=chosen;
  se379Frame.lastPreset=preset;
  se379Frame.lastXRScale=chosen;
  se379Frame.framebufferChoices++;
  // Invoke the v11.191 native framebuffer setter; the v11.195 wrapper
  // would overwrite the chosen value back to the fixed .72 every time.
  return se195OriginalFramebuffer();
};
const se379PreviousCleanup=se193XRCleanup;
se193XRCleanup=function(...args){
  se379Frame.lastSceneGapMs=0;
  return se379PreviousCleanup(...args);
};
window.SWYRL_ENGINE_SHEEP_VR_CADENCE_379=Object.freeze({
  diagnose:()=>({
    active:se195Gameplay(),
    visibleGameplayGapsNotMistakenForOSBlur:se379Frame.sceneGaps,
    lastVisibleGameGapMs:se379Frame.lastSceneGapMs,
    worstVisibleGameGapMs:Math.round(se379Frame.maxSceneGapMs),
    graphicsPresetAtVREntry:se379Frame.lastPreset,
    xrFramebufferScaleAtEntry:se379Frame.lastXRScale,
    xrFramebufferSelections:se379Frame.framebufferChoices,
    framebufferChangesRequireVRReentry:true,
    nativeXRVisibility:se211Visibility(),
    headsetCompositorAndRefreshUnchanged:true,
    gameClockAndJoystickMappingUnchanged:true
  })
});
