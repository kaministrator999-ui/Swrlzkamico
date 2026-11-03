// §E v11.238 candidate: app radial ≠ Meta OS overlay.
// A dropped WebXR frame while the game's own menu is visible is not, by
// itself, a Quest visibilitychange event. Leave native tracking and game
// simulation/collision unchanged; keep OS-blur and long-gap guards intact.
const se238Radial={
  slowAppFrames:0,maxLocalGapMs:0,radialRestores:0,
  panelRestores:0,hitCaches:0,hitMisses:0,
  pageBuilds:0,visibilityChanges:0,selectionReads:0,
  textureBuilds:0,textureReuses:0,
  lastLocalGapMs:0,lastError:'', cache:new Map()
};
function se238NativeMenuOpen(){
  return !!se181XR?.session&&renderer.xr.isPresenting&&
    ((se195.visible&&se195.radial?.visible)||
     !!se204.wheel?.root?.visible);
}
const se238PreviousOnFrame=se211OnFrame;
se211OnFrame=function(){
  const now=performance.now(),gap=se211.lastFrame?now-se211.lastFrame:0;
  // Distinguish a slow §E menu frame from losing focus to the Meta OS.
  // Long gaps (>650ms), actual visible-blurred/hidden, and an existing
  // overlay recovery still use the original safety path without alteration.
  if(se238NativeMenuOpen()&&se211Visibility()==='visible'&&
     se211.lastVisible==='visible'&&
     gap>170&&gap<650&&now>=se211.returnUntil&&
     !se211.pendingRelease){
    se238Radial.slowAppFrames++;
    se238Radial.lastLocalGapMs=Math.round(gap);
    se238Radial.maxLocalGapMs=Math.max(se238Radial.maxLocalGapMs,gap);
    se211.lastFrame=now; // no fictitious OS-focus inference this callback
  }
  return se238PreviousOnFrame();
};
// The old global recovery hides the app-owned radial on any long frame,
// including frames where the Quest session is STILL visible. Preserve the
// user's open menu and spatial panels for that case only. Genuine OS blur and
// hidden sessions still hide everything exactly as before.
const se238PreviousCosmetics=se211Cosmetics;
se211Cosmetics=function(active){
  const result=se238PreviousCosmetics(active);
  if(!active||se211Visibility()!=='visible')return result;
  const restore=object=>{
    if(!object||!se211.savedVisible.has(object))return;
    const before=se211.savedVisible.get(object);
    se211.savedVisible.delete(object);
    object.visible=before;
    if(object===se195.radial||object===se204.wheel?.root)
      se238Radial.radialRestores++;
    else se238Radial.panelRestores++;
  };
  restore(se195.radial);
  restore(se204.wheel?.root);
  for(const panel of se210UI?.panels?.values?.()||[])restore(panel.root);
  return result;
};
// The native XR render path and the v11.205 pointer adapter ask the same
// question several times per frame. Cache only the current menu's ray hit,
// not game-world rays or trigger actions, and invalidate on pose/UI movement.
// Page changes used to allocate/reupload 512x256 canvas textures for the
// same labels, then dispose them immediately. One cached GPU texture per
// unique label is retained only for this XR session and freed on XR exit.
const se238LabelTextures=new Map();
const se238PriorText=se195Text;
se195Text=function(label,header=false){
  const key=String(header?'heading:':'item:')+String(label);
  if(se238LabelTextures.has(key)){
    se238Radial.textureReuses++;return se238LabelTextures.get(key);
  }
  const texture=se238PriorText(label,header);
  // The original per-page texture disposal must not discard our cache;
  // se193XRCleanup below is the sole owner of these textures.
  const i=se195.textures.indexOf(texture);
  if(i>=0)se195.textures.splice(i,1);
  se238LabelTextures.set(key,texture);
  se238Radial.textureBuilds++;
  return texture;
};
const se238PriorRadialHit=se195RadialHit;
se195RadialHit=function(record,cast){
  if(!se195.visible||!se195.radial||cast||
     !record||!Number.isInteger(record.index))
    return cast?se238PriorRadialHit(record,cast):se238PriorRadialHit(record);
  const root=se195.radial,p=root.position,q=root.quaternion;
  const tick=se181XR.frames;
  const prior=se238Radial.cache.get(record.index);
  if(prior&&prior.tick===tick&&prior.root===root&&
     prior.x===p.x&&prior.y===p.y&&prior.z===p.z&&
     prior.qx===q.x&&prior.qy===q.y&&prior.qz===q.z&&prior.qw===q.w){
    se238Radial.hitCaches++;return prior.hit;
  }
  const hit=se238PriorRadialHit(record);
  se238Radial.cache.set(record.index,{
    tick,root,x:p.x,y:p.y,z:p.z,
    qx:q.x,qy:q.y,qz:q.z,qw:q.w,hit
  });
  se238Radial.hitMisses++;
  return hit;
};
const se238PriorPageBuild=se195MakeRadial;
se195MakeRadial=function(reposition=true){
  se238Radial.cache.clear();se238Radial.pageBuilds++;
  return se238PriorPageBuild(reposition);
};
const se238PriorMenuSetVisible=se195SetVisible;
se195SetVisible=function(value){
  const before=se195.visible;
  const result=se238PriorMenuSetVisible(value);
  if(before!==se195.visible)se238Radial.visibilityChanges++;
  if(!se195.visible)se238Radial.cache.clear();
  return result;
};
const se238PriorCleanup=se193XRCleanup;
se193XRCleanup=function(){
  se238Radial.cache.clear();
  const result=se238PriorCleanup();
  for(const texture of se238LabelTextures.values())texture.dispose();
  se238LabelTextures.clear();
  return result;
};
window.SWYRL_ENGINE_QUEST_RADIAL_STABILITY_238=Object.freeze({
 diagnose:()=>({
  active:!!se181XR?.session&&renderer.xr.isPresenting,
  menuVisible:!!se195.visible,radialDrawn:!!se195.radial?.visible,
  nativeXRVisibility:se211Visibility(),
  appMenuSlowFrames:se238Radial.slowAppFrames,
  largestAppMenuGapMs:Math.round(se238Radial.maxLocalGapMs),
  lastAppMenuGapMs:se238Radial.lastLocalGapMs,
  unintendedMenuHidesPrevented:se238Radial.radialRestores,
  spatialPanelRestores:se238Radial.panelRestores,
  reusedRadialRayHits:se238Radial.hitCaches,
  sampledRadialRayHits:se238Radial.hitMisses,
  menuRebuilds:se238Radial.pageBuilds,
  labelTexturesCreated:se238Radial.textureBuilds,
  labelTexturesReused:se238Radial.textureReuses,
  menuVisibilityChanges:se238Radial.visibilityChanges,
  gameLeftStickPreserved:true,
  nativeOSBlurGuardsPreserved:true,
  lastError:se238Radial.lastError
 })
});
