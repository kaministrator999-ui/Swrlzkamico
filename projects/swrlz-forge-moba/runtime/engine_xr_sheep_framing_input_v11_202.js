// §E v11.202 — Quest Sheep Tag: rearward wide framing, joystick-only
// movement, low-cost building previews and stable cached collision snapshots.
// Native game authority, HMD tracking, touch input and editor 6DoF unchanged.
const se202={
 horizontal:21,vertical:26,defaultZoom:1.4,rearBias:2.5,
 snapshotsBuilt:0,snapshotsReused:0,
 previewStatusBypasses:0,previewReuses:0,previewFullChecks:0,
 previewState:null,obstacles:null,obstaclesSession:null,
 obstaclesVersion:-1,completedWalls:-1,
 noClickMoves:0,foundationRefreshes:0,foundationAt:0,
 lastFoundationPoint:null,foundationSession:null,foundationVersion:-1,
 collisionRing:null,visualHalo:null,ringUnit:null,ringRadius:0,
 haloRadius:0,ringUpdates:0,ringCreations:0,ringDisposals:0
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
// The stock sheep wool/head visibly overhang its 0.27m gameplay radius.
// A BRIGHT cyan inside line is the exact collision radius used by pathfinding;
// a FAINT outer gold halo is only the visual model selector, not a blocker.
// This deliberately avoids mislabelling a model-sized circle as passability.
function se202RingDispose(){
 for(const ring of [se202.collisionRing,se202.visualHalo]){
  if(!ring)continue;
  scene.remove(ring);ring.geometry.dispose();ring.material.dispose();
  se202.ringDisposals++;
 }
 se202.collisionRing=se202.visualHalo=null;
 se202.ringUnit=null;se202.ringRadius=se202.haloRadius=0;
}
function se202ModelHalo(unit,radius){
 // Read the mesh bounds only on selection change, never per game frame.
 if(!unit.actor||typeof THREE.Box3!=='function')return Math.max(radius+.07,.73);
 const box=new THREE.Box3().setFromObject(unit.actor);
 const mid=unit.actor.getWorldPosition(new THREE.Vector3());
 const extents=[
  [box.min.x,box.min.z],[box.max.x,box.min.z],
  [box.min.x,box.max.z],[box.max.x,box.max.z]
 ];
 const visual=Math.max(...extents.map(([x,z])=>Math.hypot(x-mid.x,z-mid.z)));
 return Math.max(radius+.07,Number.isFinite(visual)?visual+.055:.73);
}
function se202CreateRing(radius,color,opacity,name){
 const mesh=new THREE.Mesh(
  new THREE.RingGeometry(Math.max(.01,radius-.028),radius,64),
  new THREE.MeshBasicMaterial({color,transparent:true,opacity,
   depthWrite:false,depthTest:false,side:THREE.DoubleSide,toneMapped:false})
 );
 mesh.name=name;mesh.userData.sheepTagPreview=true;
 mesh.renderOrder=999;mesh.rotation.x=-Math.PI/2;
 scene.add(mesh);
 return mesh;
}
function se202SheepRingFrame(){
 if(!se193XRGameActive()||!stSession){
  if(se202.collisionRing||se202.visualHalo)se202RingDispose();
  return;
 }
 const unit=stSession.units.find(u=>u.id===stSession.controlledId);
 if(!unit||unit.kind!=='sheep'||unit.captured||unit.isIllusion){
  if(se202.collisionRing||se202.visualHalo)se202RingDispose();
  return;
 }
 const radius=stUnitRadius(unit);
 if(!Number.isFinite(radius)||radius<=.04)return;
 if(se202.ringUnit!==unit||Math.abs(radius-se202.ringRadius)>.0001){
  se202RingDispose();
  se202.ringUnit=unit;se202.ringRadius=radius;
  se202.haloRadius=se202ModelHalo(unit,radius);
  se202.collisionRing=se202CreateRing(radius,0x70fff1,.9,
   'Sheep actual navigation collision radius');
  se202.visualHalo=se202CreateRing(se202.haloRadius,0xffdb85,.24,
   'Sheep model-size cosmetic selector (not collision)');
  se202.ringCreations++;
 }
 const x=unit.pos.x,z=unit.pos.z;
 const floorY=Number.isFinite(unit.pos.y)?unit.pos.y:terrainHeight(x,z);
 const y=floorY+.045;
 se202.collisionRing.position.set(x,y,z);
 se202.visualHalo.position.set(x,y+.003,z);
 se202.ringUpdates++;
}

const se202PreviousFrame=se193XRFrame;
se193XRFrame=function(){
 const result=se202PreviousFrame();
 se202FoundationFrame();
 se202SheepRingFrame();
 return result;
};
function se202Reset(){
 se202RingDispose();
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
  foundationRefreshes:se202.foundationRefreshes,
  collisionRadius:se202.ringRadius,visualHaloRadius:se202.haloRadius,
  ringUpdates:se202.ringUpdates,ringCreations:se202.ringCreations,
  ringDisposals:se202.ringDisposals
 })
});
