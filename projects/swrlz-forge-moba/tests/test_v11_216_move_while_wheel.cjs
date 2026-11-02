// §E v11.216 regression: movement must continue DURING A/X selection.
// Loads the actual v11.214 adapter then the minimal append-only v11.216 fix.
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
class Vec{
 constructor(x=0,y=0,z=0){this.set(x,y,z)}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 setY(y){this.y=y;return this}
 copy(v){return this.set(v.x,v.y,v.z)}
 clone(){return new Vec(this.x,this.y,this.z)}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this}
 addScaledVector(v,k){this.x+=v.x*k;this.y+=v.y*k;this.z+=v.z*k;return this}
}
class Matrix{lookAt(from,to,up){this.from=from.clone();this.to=to.clone();this.up=up.clone();return this}}
class Quat{setFromRotationMatrix(m){this.from=m.from.clone();this.to=m.to.clone();this.up=m.up.clone();return this}}
class WheelRoot{
 constructor(){this.visible=false;this.position=new Vec();this.quaternion=new Quat();this.updates=0}
 updateMatrixWorld(){this.updates++}
}
const unit={id:'sheep',pos:{x:0,y:0,z:0},order:{vrStick:true,action:'move'}};
const stSession={units:[unit],controlledId:'sheep'};
const left={index:0,ray:{visible:true},input:{handedness:'left',
 gamepad:{axes:[0,0,1,0]}},se192:{beam:{visible:true},dot:{visible:true}},
 se195:{halo:{visible:true},points:{visible:true}}};
const right={index:1,ray:{visible:true},input:{handedness:'right',
 gamepad:{axes:[0,0,.9,-.5]}},se192:{beam:{visible:true},dot:{visible:true}},
 se195:{halo:{visible:true},points:{visible:true}}};
let active=true,blurred=false,paused=false,frame=0,clearedOrders=0;
let stickCalls=0,followCalls=0,groundCalls=0,hideGround=0,renderCalls=0;
let oldHandCalls=0,sceneYaw=0,sceneZoom=1,eye=new Vec(0,1.7,0);
let headForward=new Vec(0,-.35,-.936),roll=.7;
const sandbox={
 Math,console,THREE:{Vector3:Vec,Matrix4:Matrix},
 se181XR:{controllers:[left,right],session:{visibilityState:'visible'}},
 renderer:{xr:{isPresenting:true}},
 se204:{wheel:null},
 se200:{stickHeld:true},
 stSession,
 se193XRGameActive:()=>active,
 se204Gameplay:()=>active,
 se205OverlayActive:()=>blurred,
 se211Paused:()=>paused,
 se191XRHeadPose:()=>({eye,forward:headForward,roll}),
 se204WheelPosition:()=>{},
 se204WheelShow:type=>{
  sandbox.se204.wheel={type,root:new WheelRoot()};
  sandbox.se204.wheel.root.visible=true;
  sandbox.se204WheelPosition();
 },
 se204WheelHide:()=>{
  if(sandbox.se204.wheel)sandbox.se204.wheel.root.visible=false;
  sandbox.se204.wheel=null;
 },
 se192InputRecord:side=>side==='left'?left:right,
 // v11.204 independently intercepts the RIGHT stick for camera controls
 // during the A/X menu; the wheel still reads RAW right axes.
 se192Stick:record=>{
  if(sandbox.se204.wheel&&record===right)return {x:0,y:0};
  const a=record.input.gamepad.axes;return {x:a[2],y:a[3]};
 },
 se199StickIntent:()=>{
  stickCalls++;
  return {strength:1,x:left.input.gamepad.axes[2],z:.25};
 },
 se195FollowCamera:()=>{
  followCalls++;
  const stick=sandbox.se192Stick(right);
  sceneYaw+=stick.x;
  sceneZoom+=stick.y;
  eye.x=unit.pos.x;eye.z=unit.pos.z;
 },
 stSetOrder:(u,order)=>{clearedOrders++;u.order=order},
 se203GroundGuideHide:()=>{
  hideGround++;
  left.se192.dot.visible=false;
  right.se192.dot.visible=false;
 },
 se203GroundFromForwardRay:()=>{
  groundCalls++;
  return new Vec(8,0,5);
 },
 se195UpdateHand:()=>{oldHandCalls++},
 se192RenderRay:(record)=>{
  renderCalls++;
  record.se192.beam.visible=true;record.se192.dot.visible=true;
  record.se195.halo.visible=true;record.se195.points.visible=true;
  if(record===right)sandbox.se203GroundFromForwardRay(record);
 },
 se193XRFrame:()=>{
  frame++;
  const move=sandbox.se199StickIntent();
  if(move.strength>.05){
   unit.pos.x+=.16*move.x;unit.pos.z+=.16*move.z;
  }
  sandbox.se195FollowCamera(.016);
  for(const rec of [left,right])sandbox.se192RenderRay(rec);
 },
 se193XRCleanup:()=>{},
 window:{}
};
vm.createContext(sandbox);
for(const file of [
 'engine_xr_sheep_wheel_modal_camera_ray_v11_214.js',
 'engine_xr_sheep_live_wheel_v11_216.js'
]){
 const src=fs.readFileSync(path.join(__dirname,'..','runtime',file),'utf8');
 vm.runInContext(src,sandbox,{filename:file});
}
const view=()=>sandbox.window.SWYRL_ENGINE_SHEEP_LIVE_WHEEL_216.diagnose();
const previous=()=>sandbox.window.SWYRL_ENGINE_SHEEP_WHEEL_COMFORT_214.diagnose();
const nearly=(a,b,msg)=>assert.ok(Math.abs(a-b)<.000001,msg+': '+a+' != '+b);
const tick=()=>sandbox.se193XRFrame();
assert.equal(view().wheelOpen,false);
assert.equal(view().sheepMovementAllowed,true);
assert.equal(view().leftStickOwnsSheep,true);
assert.equal(view().rightStickSelectsWheel,true);
assert.equal(view().headsetPoseUnchanged,true);
tick();
nearly(unit.pos.x,.16,'left stick moves normally');
assert.equal(stickCalls,1);
assert.equal(followCalls,1);
assert.ok(sceneYaw>.8,'right stick normally orbits camera');
const beforeOpen=unit.pos.x;
const yaw=sceneYaw,zoom=sceneZoom,oldMoveOrder=unit.order;
sandbox.se204WheelShow('build');
assert.equal(view().wheelOpen,true);
assert.equal(previous().menuType,'build');
assert.equal(view().wheelOpensWithoutMovementCancellation,1);
assert.equal(clearedOrders,0,'opening A radial must not cancel running sheep');
assert.strictEqual(unit.order,oldMoveOrder);
assert.equal(sandbox.se200.stickHeld,true,'active VR left stick not reset');
assert.equal(sandbox.se204.wheel.root.visible,true);
const startFollow=followCalls,startMove=stickCalls;
for(let i=0;i<9;i++)tick();
assert.equal(stickCalls,startMove+9,'native movement still sampled each frame');
assert.equal(followCalls,startFollow+9,'camera continues tracking running sheep');
assert.ok(unit.pos.x>beforeOpen+1,'sheep travels appreciably while radial open');
nearly(eye.x,unit.pos.x,'camera follows sheep not stale pre-wheel coordinate');
nearly(sceneYaw,yaw,'right stick does not orbit when selecting');
nearly(sceneZoom,zoom,'right stick does not zoom when selecting');
assert.equal(right.input.gamepad.axes[2],.9,'raw right stick still available to choose sector');
const wheel=sandbox.se204.wheel.root;
nearly(wheel.position.x,eye.x,'wheel travels with changing headset origin');
nearly(wheel.position.y,eye.y-.075,'upright comfortable menu height');
nearly(wheel.position.z,eye.z-1.08,'wheel remains in front after moving');
nearly(wheel.quaternion.from.y,wheel.quaternion.to.y,'no camera pitch in wheel orientation');
assert.equal(wheel.quaternion.up.y,1);
assert.equal(wheel.visible,true);
assert.ok(wheel.updates>=9);
assert.equal(right.se192.beam.visible,false,'no second building beam behind radial');
assert.equal(left.se192.beam.visible,false);
assert.equal(right.se195.halo.visible,false,'no redundant hand-beam aura');
assert.equal(left.ray.visible,false);
assert.equal(groundCalls,1,'building guide never respawns while A menu open');
assert.ok(hideGround>0);
assert.equal(previous().joystickFramesSuppressed,0);
assert.equal(previous().cameraFollowFramesSuppressed,0);
assert.ok(view().wheelMovementFrames>=9);
assert.ok(view().wheelCameraFollowFrames>=9);
assert.equal(clearedOrders,0);
// Head tilt/yaw only changes menu position/yaw, not real HMD tracking.
roll=-1.1;headForward=new Vec(.9,-.4,.3);
tick();
nearly(wheel.quaternion.from.y,wheel.quaternion.to.y,'menu stays level on headset roll');
assert.equal(view().headsetPoseUnchanged,true);
// Close building menu; restore ordinary camera orbit and ground ray.
sandbox.se204WheelHide();
assert.equal(view().wheelOpen,false);
const priorMove=unit.pos.x;
tick();
assert.ok(unit.pos.x>priorMove,'movement uninterrupted after menu closes');
assert.ok(sceneYaw>yaw+.8,'right camera orbit resumes after release');
assert.ok(groundCalls>=2,'normal forward building ray resumes outside wheel');
// X ability selector must have same live movement and single-ray behavior.
const skillStart=unit.pos.x,skillFollow=followCalls;
sandbox.se204WheelShow('skill');
for(let i=0;i<4;i++)tick();
assert.ok(unit.pos.x>skillStart+.5,'X ability wheel also permits running');
assert.equal(followCalls,skillFollow+4);
nearly(sceneZoom,zoom+right.input.gamepad.axes[3],'X selection never zooms camera');
assert.equal(right.se192.beam.visible,false);
sandbox.se204WheelHide();
// Unrelated editor mode maintains native controllers.
active=false;
const editorIntent=stickCalls,editorFollow=followCalls;
tick();
assert.equal(stickCalls,editorIntent+1);
assert.equal(followCalls,editorFollow+1);
right.se195.halo.visible=true;
sandbox.se195UpdateHand(right,.5,1);
assert.equal(oldHandCalls,1);
assert.equal(right.se195.halo.visible,true);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_216_sheep_live_move_wheel.py'),'utf8');
assert.ok(patch.includes('V11_216_SHEEP_LIVE_MOVE_WHILE_SELECTING'));
assert.ok(!patch.includes('setReferenceSpace('));
assert.ok(!patch.includes('stUi.rotation='));
console.log(JSON.stringify({
 pass:true,checks:50,finalSheepX:Number(unit.pos.x.toFixed(2)),
 cameraFollowFrames:view().wheelCameraFollowFrames,
 movingWheelFrames:view().wheelMovementFrames,
 oldStickOrdersCanceled:clearedOrders,
 nativeFrameCount:frame,rayGuideBlocks:previous().underlyingBuildGuideSuppressed
}));
