// §E v11.213 · Sheep Tag Quest quick-wheel modal camera, head-up yaw and single pointer.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
class V{
 constructor(x=0,y=0,z=0){this.set(x,y,z)}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 setY(y){this.y=y;return this}
 copy(p){return this.set(p.x,p.y,p.z)}
 clone(){return new V(this.x,this.y,this.z)}
 addScaledVector(p,n){this.x+=p.x*n;this.y+=p.y*n;this.z+=p.z*n;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const len=Math.sqrt(this.lengthSq())||1;this.x/=len;this.y/=len;this.z/=len;return this}
}
class Mat{lookAt(eye,target,up){
 this.eye=eye.clone();this.target=target.clone();this.up=up.clone();return this
}}
class Q{setFromRotationMatrix(matrix){
 this.eye=matrix.eye.clone();this.target=matrix.target.clone();this.up=matrix.up.clone();
 return this
}}
class Root{
 constructor(){this.visible=false;this.position=new V();this.quaternion=new Q();this.updateCount=0}
 updateMatrixWorld(){this.updateCount++}
}
let time=1000,game=true,blurred=false,willPause=false,currentHead={
 eye:new V(0,1.7,0),forward:new V(0,-.9,-.435),roll:1.4};
const hud={};
const left={index:0,input:{handedness:'left'},ray:{visible:true},
 se192:{beam:{visible:true},dot:{visible:true}},
 se195:{halo:{visible:true},points:{visible:true}}};
const right={index:1,input:{handedness:'right'},ray:{visible:true},
 se192:{beam:{visible:true},dot:{visible:true}},
 se195:{halo:{visible:true},points:{visible:true}}};
const state={oldPos:0,oldShows:0,oldHides:0,oldIntent:0,oldCamera:0,
 oldGround:0,oldRay:0,oldHand:0,oldFrames:0,oldCleanup:0,
 groundVisible:false,groundHides:0,oldMenu:null,oldWheelOpen:false,
 orderClears:0};
const unit={id:'sheep',kind:'sheep',order:{action:'move',vrStick:true}};
const session={role:'sheep',controlledId:'sheep',units:[unit]};
const sandbox={
 console,Math,THREE:{Vector3:V,Matrix4:Mat},
 se181XR:{session:{visibilityState:'visible'},controllers:[left,right]},
 renderer:{xr:{isPresenting:true}},
 se204:{wheel:null},
 stSession:session,
 se200:{stickHeld:true},
 se193XRGameActive:()=>game,
 se204Gameplay:()=>game,
 se205OverlayActive:()=>blurred,
 se211Paused:()=>willPause,
 se191XRHeadPose:()=>currentHead,
 se192InputRecord:side=>side==='left'?left:right,
 se204WheelPosition:()=>{state.oldPos++},
 se204WheelShow:type=>{
  state.oldShows++;
  sandbox.se204.wheel={type,root:new Root()};
  sandbox.se204.wheel.root.visible=true;
  sandbox.se204WheelPosition();
 },
 se204WheelHide:()=>{
  state.oldHides++;if(sandbox.se204.wheel)sandbox.se204.wheel.root.visible=false;
  sandbox.se204.wheel=null;
 },
 se199StickIntent:()=>{state.oldIntent++;return {strength:1,x:.6,z:.8}},
 se195FollowCamera:()=>{state.oldCamera++},
 stSetOrder:(actor,order)=>{state.orderClears++;actor.order=order},
 se203GroundGuideHide:()=>{
  state.groundHides++;state.groundVisible=false;
  right.se192.beam.visible=true;
 },
 se203GroundFromForwardRay:()=>{
  state.oldGround++;state.groundVisible=true;return new V(6,0,4)
 },
 se195UpdateHand:()=>{state.oldHand++},
 se192RenderRay:(rec)=>{
  state.oldRay++;rec.se192.beam.visible=true;rec.se192.dot.visible=true;
  rec.se195.halo.visible=true;rec.se195.points.visible=true;
  if(rec===right)sandbox.se203GroundFromForwardRay(rec);
 },
 se193XRFrame:()=>{
  state.oldFrames++;
  sandbox.se195FollowCamera(.016);
  sandbox.se199StickIntent();
  for(const rec of [left,right])sandbox.se192RenderRay(rec);
 },
 se193XRCleanup:()=>{state.oldCleanup++},
 performance:{now:()=>time},
 window:{}
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_sheep_wheel_modal_camera_ray_v11_213.js'),'utf8'),sandbox);
const diag=()=>sandbox.window.SWYRL_ENGINE_SHEEP_WHEEL_COMFORT_213.diagnose();
const near=(a,b,label)=>assert.ok(Math.abs(a-b)<.00001,label+': '+a+' != '+b);
// Normal game still moves and follows, but the extra hand aura stays hidden.
sandbox.se193XRFrame();
assert.equal(state.oldCamera,1);
assert.equal(state.oldIntent,1);
assert.equal(state.oldGround,1);
assert.equal(state.groundVisible,true);
assert.equal(left.se195.halo.visible,false);
assert.equal(right.se195.halo.visible,false);
assert.equal(diag().wheelOpen,false);
assert.equal(state.oldHand,0,'secondary beam particles no longer uploaded during gameplay');
// A HOLD opens a modal, canceling the old joystick move order once.
sandbox.se204WheelShow('build');
assert.equal(diag().wheelOpen,true);
assert.equal(diag().menuType,'build');
assert.equal(diag().enteringModal,1);
assert.equal(state.orderClears,1);
assert.equal(unit.order,null);
assert.equal(sandbox.se200.stickHeld,false);
assert.equal(state.oldShows,1);
assert.equal(state.oldPos,0,'new wheel placement owns the origin, not legacy pitched lookAt');
let wheel=sandbox.se204.wheel.root;
near(wheel.position.x,0,'start center x');
near(wheel.position.y,1.625,'head-level wheel y');
near(wheel.position.z,-1.08,'front-of-head horizontal distance');
near(wheel.quaternion.eye.y,wheel.quaternion.target.y,'horizontal yaw-only facing, no pitch');
near(wheel.quaternion.up.y,1,'stable global upright');
assert.equal(wheel.quaternion.eye.z,0,'face true viewer eye, not towards sheep');
// v11.203's extra virtual link is blocked; no HUD/controller ray draws behind it.
const moves=state.oldCamera,stick=state.oldIntent,ground=state.oldGround;
sandbox.se193XRFrame();
assert.equal(state.oldCamera,moves,'no world reference-space camera chase during wheel');
assert.equal(state.oldIntent,stick,'joystick movement disabled without visiting old intent');
assert.equal(state.oldGround,ground,'forward-ground ray cannot spawn behind wheel');
assert.equal(state.groundVisible,false);
assert.equal(left.se192.beam.visible,false);
assert.equal(right.se192.beam.visible,false);
assert.equal(left.se192.dot.visible,false);
assert.equal(right.se192.dot.visible,false);
assert.equal(left.ray.visible,false);
assert.equal(right.ray.visible,false);
assert.equal(left.se195.halo.visible,false);
assert.equal(right.se195.points.visible,false);
assert.equal(diag().underlyingBuildGuideSuppressed>0,true);
assert.equal(diag().cameraFollowFramesSuppressed>0,true);
assert.equal(diag().joystickFramesSuppressed>0,true);
// Move the real headset, pan yaw and roll: wheel follows head XYZ with yaw only.
currentHead={eye:new V(2,2.2,-1),forward:new V(.9,-.4,0),roll:-1.2};
time+=16;sandbox.se193XRFrame();
wheel=sandbox.se204.wheel.root;
near(wheel.position.x,3.08,'menu follows head right x');
near(wheel.position.y,2.125,'menu follows head up');
near(wheel.position.z,-1,'menu follows head z');
near(wheel.quaternion.eye.y,wheel.quaternion.target.y,'head pitch and roll cannot rotate menu');
assert.ok(wheel.updateCount>=3);
assert.equal(diag().yawOnlyMenu,true);
assert.equal(diag().headsetTrackingUnchanged,true);
// Looking vertically down shouldn't flip the menu or change yaw abruptly.
currentHead.forward.set(0,-1,0);time+=16;
sandbox.se193XRFrame();
near(wheel.position.x,3.08,'keep valid last yaw while looking down');
assert.ok(diag().verticalHeadGazeFallbacks>=1);
// Skill wheel gets identical behavior.
sandbox.se204WheelHide();
assert.equal(diag().wheelOpen,false);
assert.equal(state.groundVisible,false);
assert.equal(right.se192.beam.visible,true);
assert.equal(diag().leavingModal,1);
const postMoves=state.oldCamera;
sandbox.se193XRFrame();
assert.equal(state.oldCamera,postMoves+1,'camera tracking resumes after closing wheel');
assert.equal(state.oldIntent,stick+1,'left stick gameplay resumes after closing');
assert.equal(state.oldGround,ground+1,'normal single ground build guide resumes');
sandbox.se204WheelShow('skill');
assert.equal(diag().menuType,'skill');
assert.equal(diag().enteringModal,2);
sandbox.se193XRFrame();
assert.equal(left.se192.beam.visible,false);
assert.equal(right.se192.beam.visible,false);
sandbox.se204WheelHide();
assert.equal(diag().leavingModal,2);
// Meta Camera system overlay takes precedence over application wheel.
sandbox.se204WheelShow('build');
blurred=true;sandbox.se193XRFrame();
assert.equal(diag().wheelOpen,false,'browser focus loss takes priority');
blurred=false;willPause=true;sandbox.se193XRFrame();
assert.equal(diag().wheelOpen,false,'v11.211 post-OS recovery takes priority');
willPause=false;sandbox.se193XRFrame();
assert.equal(diag().wheelOpen,true);
sandbox.se204WheelHide();
// Editor/modeler controls are not changed; their controller effects still work.
game=false;
right.se195.halo.visible=true;
sandbox.se192RenderRay(right,{});
assert.equal(right.se195.halo.visible,true);
sandbox.se195UpdateHand(right,1,2);
assert.equal(state.oldHand,1);
const editorMotion=state.oldIntent,editorCamera=state.oldCamera;
sandbox.se193XRFrame();
assert.equal(state.oldCamera,editorCamera+1);
assert.equal(state.oldIntent,editorMotion+1);
sandbox.se193XRCleanup();
assert.equal(state.oldCleanup,1);
assert.equal(diag().wheelOpen,false);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_213_quest_sheep_upright_modal_one_ray.py'),'utf8');
assert.ok(patch.includes('V11_213_SHEEP_QUEST_UPRIGHT_WHEEL_SINGLE_RAY'));
assert.ok(!patch.includes('renderer.xr.setReferenceSpace('),'no headset reference-space overwrite');
assert.ok(!patch.includes('se181XR.session.end('));
console.log(JSON.stringify({pass:true,checks:53,modalOpens:diag().enteringModal,
 menuMoves:diag().uprightWheelFrames,stoppedPreviousMoves:diag().previousJoystickOrdersStopped,
 cameraBlocked:diag().cameraFollowFramesSuppressed,extraRayBlocks:diag().underlyingBuildGuideSuppressed,
 glowsMuted:diag().duplicateControllerAuraSuppressed,restores:diag().pointerRestores}));
