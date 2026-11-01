// §E v11.202 — Quest Sheep Tag: rearward wide framing, joystick-only
// movement, low-cost building previews and stable cached collision snapshots.
// Native game authority, HMD tracking, touch input and editor 6DoF unchanged.
const se202={
 horizontal:22,vertical:25,defaultZoom:1.5,rearBias:3.5,
 snapshotsBuilt:0,snapshotsReused:0,
 previewStatusBypasses:0,previewReuses:0,previewFullChecks:0,
 previewState:null,obstacles:null,obstaclesSession:null,
 obstaclesVersion:-1,completedWalls:-1,
 noClickMoves:0,foundationRefreshes:0,foundationAt:0,
 lastFoundationPoint:null,foundationSession:null,foundationVersion:-1
};
// Camera stays world-anchored to the controlled sheep; the extra distance
// biases it toward the upper portion of the neutral headset view WITHOUT
// changing headset pitch, physical tracking, or free-look.
se200.horizontal=se202.horizontal;
se200.vertical=se202.vertical;
se200.defaultZoom=se202.defaultZoom;
const se202OldAnchor=se200CameraAnchor;
se200CameraAnchor=function(){
 const wanted=se202OldAnchor();
 const forward=new THREE.Vector3(Math.sin(se193.angle),0,Math.cos(se193.angle));
 return wanted.addScaledVector(forward,-se202.rearBias);
};
function se202ObstacleSnapshot(){
 const s=stSession;
 if(!se200Active()||!s)return stObstacles();
 // Ground walls stop being ground obstacles once fully built (v11.132).
 // Track that transition separately from structural navVersion changes.
 let elevatedWalls=0;
 for(const b of s.buildings)
  if(b.kind==='st-wall'&&b.hp>0&&b.progress>=1)elevatedWalls++;
 if(se202.obstaclesSession===s&&se202.obstaclesVersion===s.navVersion&&
    se202.completedWalls===elevatedWalls&&se202.obstacles){
  se202.snapshotsReused++;return se202.obstacles;
 }
 se202.obstacles=stObstacles();
 se202.obstaclesSession=s;se202.obstaclesVersion=s.navVersion;
 se202.completedWalls=elevatedWalls;se202.snapshotsBuilt++;
 return se202.obstacles;
}
function se202PreviewOwner(){
 if(se200Active()&&stSession){
  se202.previewStatusBypasses++;
  return stSession.controlledId;
 }
 return stUiView().controlledId;
}
function se202VisibleBuildings(){
 if(!se200Active()||!stSession)return stUiView().buildings||[];
 se202.previewStatusBypasses++;
 const result=[];
 // Respect the same authoritative visibility rule as stViewStatus:
 // no hidden farms are shown by the preview or its corridor guides.
 for(const b of stSession.buildings){
  if(b.hp<=0||b.mesh?.visible===false||!stSeenByRole(b))continue;
  result.push({
   id:b.id,kind:b.kind,pos:[b.pos.x,b.pos.y,b.pos.z],
   halfX:b.halfX,halfZ:b.halfZ,
   localHalfX:b.localHalfX,localHalfZ:b.localHalfZ,
   rotation:b.rotation,hp:b.hp
  });
 }
 return result;
}
function se202ShouldRefreshPreview(point){
 const s=stSession;
 if(!se200Active()||!s)return true;
 const now=performance.now();
 const key=[s.navVersion,stUi.build,stUi.rotation,s.controlledId,
  s.resources?.[s.controlledId]||0].join(':');
 const prior=se202.previewState;
 if(prior&&prior.session===s&&prior.key===key&&
    Math.abs(prior.x-point.x)<.07&&Math.abs(prior.z-point.z)<.07&&
    now-prior.at<520){
  se202.previewReuses++;return false;
 }
 se202.previewState={session:s,key,x:point.x,z:point.z,at:now};
 se202.previewFullChecks++;return true;
}
function se202FoundationFrame(){
 if(!se200Active()||!stUi.shown||!stSession)return;
 const s=stSession,now=performance.now();
 if(now-se202.foundationAt<650)return;
 se202.foundationAt=now;
 const unit=s.units.find(u=>u.id===s.controlledId);
 const p=unit?.pos||{x:stUi.focus.x,z:stUi.focus.z};
 if(se202.foundationSession===s&&se202.foundationVersion===s.navVersion&&
    se202.lastFoundationPoint&&
    Math.hypot(p.x-se202.lastFoundationPoint.x,p.z-se202.lastFoundationPoint.z)<1.7)
  return;
 const state={
  buildings:se202VisibleBuildings(),
  units:[{id:s.controlledId,controlled:true,pos:[p.x,p.y||0,p.z]}],
  selectedId:s.selectedId,role:s.role
 };
 stClarityUpdateOverlay(state);
 se202.foundationSession=s;se202.foundationVersion=s.navVersion;
 se202.lastFoundationPoint={x:p.x,z:p.z};
 se202.foundationRefreshes++;
}
const se202PreviousFrame=se193XRFrame;
se193XRFrame=function(){
 const result=se202PreviousFrame();
 se202FoundationFrame();
 return result;
};
function se202Reset(){
 se202.obstacles=null;se202.obstaclesSession=null;
 se202.obstaclesVersion=-1;se202.completedWalls=-1;
 se202.previewState=null;se202.foundationAt=0;
 se202.foundationSession=null;se202.foundationVersion=-1;
 se202.lastFoundationPoint=null;
}
const se202OldStart=se193XRStart;
se193XRStart=function(){se202Reset();return se202OldStart();};
const se202OldCleanup=se193XRCleanup;
se193XRCleanup=function(){se202Reset();return se202OldCleanup();};
window.SWYRL_ENGINE_SHEEP_VR_FOLLOW_INPUT_202=Object.freeze({
 diagnose:()=>({
  active:se200Active(),cameraBehind:se200.horizontal*se193.zoom+se202.rearBias,
  cameraAbove:se200.vertical*se193.zoom,
  eyePitchIndependent:true,joystickOnlyVR:true,
  noClickMoves:se202.noClickMoves,
  obstacleSnapshots:se202.snapshotsBuilt,obstacleReuse:se202.snapshotsReused,
  previewFullChecks:se202.previewFullChecks,
  previewSkipped:se202.previewReuses,
  statusBypasses:se202.previewStatusBypasses,
  foundationRefreshes:se202.foundationRefreshes
 })
});
