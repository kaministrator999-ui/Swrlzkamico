// §E v11.136 · stabilize sheep-origin drag against a moving follow camera,
// coalesce per-capture nav invalidation, and spread GPU visual disposal across
// animation frames without delaying destruction or changing game rules.
const st136Perf={captureBatches:0,removals:0,navCoalesced:0,retired:0,disposed:0,queuePeak:0,gridSkips:0};
let st136CaptureDepth=0,st136PendingNavigation=false;
const st136InvalidateNative=stInvalidateNavigation;
stInvalidateNavigation=function(){
 if(st136CaptureDepth){st136PendingNavigation=true;st136Perf.navCoalesced++;return;}
 return st136InvalidateNative();
};
function st136RemoveCapturedBuildings(s,ownerId){
 if(!s)return;
 st136CaptureDepth++;st136Perf.captureBatches++;
 try{
  for(const b of s.buildings){
   if(b.owner===ownerId&&b.hp>0){stRemoveBuilding(b);st136Perf.removals++;}
  }
 }finally{
  st136CaptureDepth--;
  if(!st136CaptureDepth&&st136PendingNavigation){
   st136PendingNavigation=false;
   st136InvalidateNative();
  }
 }
}
const st136RetiredVisuals=[];
function st136RetireBuildingVisual(mesh){
 if(!mesh)return;
 // The building disappears immediately and is excluded from all collision,
 // fog and raycast queries. Only expensive GPU resource disposal is deferred.
 mesh.removeFromParent();
 st136RetiredVisuals.push(mesh);
 st136Perf.retired++;
 st136Perf.queuePeak=Math.max(st136Perf.queuePeak,st136RetiredVisuals.length);
}
function st136DrainRetiredVisuals(max=2){
 let count=0;
 while(st136RetiredVisuals.length&&count<max){
  const mesh=st136RetiredVisuals.shift();
  stDisposeVisual(mesh);
  count++;st136Perf.disposed++;
 }
 return count;
}
const st136UpdateNative=stUpdate;
stUpdate=function(dt,t){
 // Keep disposal draining after a win as long as the engine runs frames.
 const result=st136UpdateNative(dt,t);
 st136DrainRetiredVisuals(2);
 return result;
};
const st136StopNative=stStop;
stStop=function(...args){
 const result=st136StopNative(...args);
 st136DrainRetiredVisuals(Infinity);
 return result;
};
// Refresh the old and new rays with the SAME current camera. The old
// v11.135 anchor ray was recorded before follow-camera movement, so it
// introduced artificial displacement even with a stationary finger.
function st136StableAimTarget(anchor,x,y){
 const sheep=st135SheepPosition();
 if(!sheep||!anchor)return null;
 const originRay=stTouchPlacementOriginalGround(anchor.x,anchor.y);
 const fingerRay=stTouchPlacementOriginalGround(x,y);
 if(!originRay||!fingerRay)return null;
 const target=new THREE.Vector3(
  sheep.x+fingerRay.x-originRay.x,0,
  sheep.z+fingerRay.z-originRay.z);
 if(!Number.isFinite(target.x)||!Number.isFinite(target.z))return null;
 target.y=terrainHeight(target.x,target.z);
 return Number.isFinite(target.y)?target:null;
}
// Grid meshes are costly to reconstruct on phones. A repeat pointer event
// within the same validated snapped footprint requires no new GPU buffers.
// Every new snapped destination, obstacle/nav version or validity DOES redraw.
let st136LastGridKey=null;
const st136GridNative=stPlacementGridUpdate;
stPlacementGridUpdate=function(){
 const s=stSession,fit=stUi.placement,guide=stPlacementGridState.guide;
 if(!s||!fit?.corners?.length||!stUi.build){
  st136LastGridKey=null;return st136GridNative();
 }
 const key=[stUi.build,fit.x,fit.z,fit.rotation??stUi.rotation,
  fit.ok,s.navVersion,s.rules.buildSnap].join('|');
 if(guide?.root?.visible&&st136LastGridKey===key){
  st136Perf.gridSkips++;return;
 }
 st136LastGridKey=key;
 return st136GridNative();
};
const st136StatusNative=stUiStatus;
stUiStatus=function(){
 return {...st136StatusNative(),sheepPerf:{
  ...st136Perf,visualDisposalPending:st136RetiredVisuals.length
 }};
};
