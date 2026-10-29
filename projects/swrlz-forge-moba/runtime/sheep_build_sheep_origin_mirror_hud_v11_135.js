// §E v11.135 — keep the hologram at the controlled sheep until deliberate
// meadow input, then translate it from that origin instead of teleporting to
// the HUD finger. The host's native stCanBuild/stUiCommand remains authoritative.
let st135AimState=null;
function st135SheepPosition(){
 const s=stSession,u=s?.units?.find(unit=>unit.id===s.controlledId);
 return u?.kind==='sheep'&&!u.captured?u.pos.clone():null;
}
function st135SeedSheepGhost(){
 if(!stUi.build||!stUi.preview||!stSession)return false;
 // Camera/touch code normally requires valid finger-ground context. Selection
 // has no ground gesture yet; don't let an invalid skill-button ray hide it.
 const gesture=stTouchPlacement.gesture,context=stTouchPlacement.context;
 stTouchPlacement.gesture=null;stTouchPlacement.context=null;
 let ready=false;
 try{ready=st126SeedAtSheep();}
 finally{stTouchPlacement.gesture=gesture;stTouchPlacement.context=context;}
 if(!ready)return false;
 const sheep=st135SheepPosition();
 if(sheep){
  stUi.preview.position.set(sheep.x,terrainHeight(sheep.x,sheep.z),sheep.z);
  stUi.preview.visible=true;
 }
 // The placement grid is for a confirmed destination, not a detached grid
 // appearing under the skill ring before the player aims a building.
 if(stPlacementGridState.guide)stPlacementGridState.guide.root.visible=false;
 if(stUi.footprint)stUi.footprint.visible=false;
 return true;
}
function st135KeepSheepGhostDuringPointer(){
 // sheep_touch_offset's camera loop otherwise re-rays the held finger each
 // frame and overwrites the preview, including while the finger is on HUD.
 return stBuildInput.pointer!==null;
}
function st135SetAimWorld(event,point){
 if(!point||![point.x,point.z].every(Number.isFinite))return false;
 const x=event.clientX,y=event.clientY;
 stTouchPlacementContext(event);
 Object.assign(stTouchPlacement,{
  rawScreen:[x,y],targetScreen:[x,y],offsetPx:0,clamped:false,
  ground:[point.x,terrainHeight(point.x,point.z),point.z],
  valid:true,reason:null
 });
 // Native preview performs the actual grid snap, collision/resource and
 // footprint checks. No building is created during a pointer move.
 stUiPlacePreview(point);
 const fit=stUi.placement;
 stTouchPlacement.fit=fit?{
  x:fit.x,z:fit.z,rotation:fit.rotation??stUi.rotation,
  ok:!!fit.ok,corners:fit.corners?structuredClone(fit.corners):null
 }:null;
 stTouchPlacement.valid=!!fit?.ok&&stTouchPlacementClearCanvas(x,y);
 stTouchPlacement.reason=stTouchPlacement.valid?null:fit?.reason||'Choose clear meadow ground.';
 return stTouchPlacement.valid;
}
function st135HandleBuildAim(event){
 const g=stTouchPlacement.gesture;
 if(!g||!stTouchPlacementEnabled())return;
 const id=event.pointerId,x=event.clientX,y=event.clientY;
 const sheep=st135SheepPosition();
 if(!sheep)return;
 if(!st135AimState||st135AimState.pointer!==id||st135AimState.session!==stSession){
  // The first meadow contact only establishes a drag anchor. This prevents
  // absolute screen-ray coordinates near the HUD from moving the ghost away.
  const ground=stTouchPlacementOriginalGround(x,y);
  st135AimState={pointer:id,session:stSession,origin:sheep,
   x,y,ground,hasMoved:false};
  stBuildInput.startX=x;stBuildInput.startY=y;stBuildInput.moved=false;
  st135SeedSheepGhost();stTouchPlacement.valid=false;
  return;
 }
 const anchor=st135AimState;
 if(Math.hypot(x-anchor.x,y-anchor.y)<=8&&!anchor.hasMoved){
  stBuildInput.moved=false;return;
 }
 anchor.hasMoved=true;stBuildInput.moved=true;
 const here=stTouchPlacementOriginalGround(x,y);
 if(!here||!anchor.ground){
  stTouchPlacement.valid=false;
  stTouchPlacement.reason='Drag onto clear meadow ground.';
  return;
 }
 const target=new THREE.Vector3(
  anchor.origin.x+here.x-anchor.ground.x,0,
  anchor.origin.z+here.z-anchor.ground.z
 );
 target.y=terrainHeight(target.x,target.z);
 st135SetAimWorld(event,target);
}
function st135TapPlacement(event){
 // Preserve the old single-tap ground-to-build shortcut, without moving the
 // preview to the skill button or authorizing an unvalidated placement.
 if(!stTouchPlacementClearCanvas(event.clientX,event.clientY))return false;
 const point=stTouchPlacementOriginalGround(event.clientX,event.clientY);
 return st135SetAimWorld(event,point);
}
function st135CommitPreview(){
 const fit=stUi.placement;
 if(!stSession||!stUi.build||!stTouchPlacement.valid||!fit?.ok)return;
 // The committed site must be the SAME site indicated by the hologram/grid.
 // Native stUiCommand still validates owner, cost, reachability, clearance.
 return stUiCommand('build',{
  kind:stUi.build,x:fit.x,z:fit.z,rotation:fit.rotation??stUi.rotation
 });
}
// Enforce discoverability in the actual phone HUD, not merely the engine's
// internal ability-state flags. No abilities are enabled against map rules.
const st135AbilityRefreshBase=stUiRefreshArchive;
stUiRefreshArchive=function(state,controlled,building,mayBuild,now){
 const out=st135AbilityRefreshBase(state,controlled,building,mayBuild,now);
 if(state?.role==='sheep'&&stUi.shown&&!state.simulate){
  const ring=$('stAbilityRing');
  for(const id of ['stSplit','stTotem']){
   const button=$(id);if(!button)continue;
   if(ring&&button.parentElement!==ring)ring.appendChild(button);
   button.hidden=false;
   button.setAttribute('data-st135-sheep-ability','');
  }
 }
 return out;
};
