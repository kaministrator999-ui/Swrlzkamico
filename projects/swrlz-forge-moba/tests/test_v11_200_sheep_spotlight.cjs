const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 clone(){return new V(this.x,this.y,this.z)}
 copy(v){Object.assign(this,{x:v.x,y:v.y,z:v.z});return this}
 set(x,y,z){Object.assign(this,{x,y,z});return this}
 setY(y){this.y=y;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 addScaledVector(v,a){this.x+=v.x*a;this.y+=v.y*a;this.z+=v.z*a;return this}
 multiplyScalar(a){this.x*=a;this.y*=a;this.z*=a;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 length(){return Math.sqrt(this.lengthSq())}
 normalize(){return this.multiplyScalar(1/(this.length()||1))}
 setLength(s){return this.normalize().multiplyScalar(s)}
 lerp(v,a){return this.addScaledVector(v.clone().sub(this),a)}
}
const unit={id:'sheep',kind:'sheep',pos:new V(),speed:6,order:null,actor:{rotation:{y:0}},
 captured:false,isIllusion:false};
const session={controlledId:unit.id,units:[unit],rules:{bounds:60,headstart:0},
  elapsed:10,buildings:[],winner:null,simulate:false,pen:{x:0,z:0,halfX:9,halfZ:9}};
const left={input:{gamepad:{axes:[0,0]}}},right={input:{gamepad:{axes:[0,0]}}};
const headset={eye:new V(0,2,0),forward:new V(0,0,-1)};
let originalSheep=0,old199=0,writes=0,obstacleReads=0,routeCalls=0;
let inside=false,blocked=false,paused=false;
const ctx={THREE:{Vector3:V,MathUtils:{clamp:(x,a,b)=>Math.max(a,Math.min(b,x))}},
 Math,window:{},stSession:session,se199:{releaseCount:0,movementFrames:0},
 se193:{angle:Math.PI,zoom:1,focus:new V(),follow:true},
 se195:{rigReady:false,rigAt:0,photo:false},
 se199Gameplay:()=>inside,paused:false,
 se199StickIntent:()=>{
  const [x,y]=left.input.gamepad.axes,a=ctx.se193.angle;
  const fx=Math.sin(a),fz=Math.cos(a),length=Math.hypot(x,y);
  const worldX=fx*(-y)-fz*x,worldZ=fz*(-y)+fx*x;
  return {x:length?worldX/length:0,z:length?worldZ/length:0,
    strength:Math.min(1,length)};
 },
 se150Match:{active:false,role:'host'},
 se192InputRecord:side=>side==='left'?left:right,
 se192Stick:r=>({x:r.input.gamepad.axes[0],y:r.input.gamepad.axes[1]}),
 se191XRHeadPose:()=>headset,
 se195MoveRig:(x,y,z)=>{writes++;headset.eye.add(new V(x,y,z));return true;},
 stUpdateSheep:()=>{old199++},stUpdateWolf:()=>{},
 se199PreviousSheep:()=>{originalSheep++},se199PreviousWolf:()=>{},
 stSetOrder:(u,o)=>{routeCalls++;u.order=o},
 stObstacles:()=>{obstacleReads++;return session.buildings},
 stUnitRadius:()=>.5,stSegmentClear:(_ctx,_from,to)=>!blocked&&
      !session.buildings.some(b=>Math.abs(to.x-b.x)<.7&&Math.abs(to.z-b.z)<.7),
 stPlaceUnit:()=>{},
 se193XRSnapFollow:()=>{ctx.se195.rigReady=false;ctx.se193.follow=true;},
 se193XRStart:()=>{},se193XRCleanup:()=>{}};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime','engine_xr_sheep_spotlight_v11_200.js'),'utf8'),ctx);
ctx.se193XRStart();
inside=true;ctx.se195FollowCamera(.016);
assert.equal(writes,1,'one snap on match entry');
assert.equal(ctx.se193.follow,true);
const initial=headset.eye.clone();
const focusToEye=initial.clone().sub(unit.pos);
const front=new V(Math.sin(ctx.se193.angle),0,Math.cos(ctx.se193.angle));
const rightVec=new V(-front.z,0,front.x);
assert.ok(Math.abs(focusToEye.x*rightVec.x+focusToEye.z*rightVec.z)<1e-5,
 'no sideways sheep offset');
assert.ok(Math.abs(focusToEye.y-26*1.4)<1e-5,'high top-down position');
assert.ok(ctx.window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200.diagnose().overheadAngleDegrees>=60);
// Simulate natural physical head translation. The sheep did not move.
// A fixed anchor must not move the VR reference space to fight HMD tracking.
headset.eye.x+=.3;headset.eye.y+=.2;
for(let i=0;i<100;i++)ctx.se195FollowCamera(.016);
assert.equal(writes,1,'head motion while idle causes zero camera writes');
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200.diagnose().idleFrames,100);
left.input.gamepad.axes=[0,-1];
for(let i=0;i<15;i++){ctx.stUpdateSheep(unit,.016);ctx.se195FollowCamera(.016);}
assert.ok(unit.pos.z<-.3,'forward thumbstick moves sheep');
assert.equal(routeCalls,0,'no pathfinding orders from stick');
assert.equal(old199,0,'old v11.199 drive bypassed in VR');
assert.ok(writes>1,'camera follows sheep from its anchor');
const sheepPos=unit.pos.clone(); const writesAfterMove=writes;
left.input.gamepad.axes=[0,0];
session.buildings=Array.from({length:18},(_,i)=>({x:30+i,z:30}));
for(let i=0;i<200;i++){ctx.stUpdateSheep(unit,.016);ctx.se195FollowCamera(.016);}
assert.equal(unit.pos.z,sheepPos.z,'stick release stops sheep');
assert.equal(routeCalls,0,'house building never runs gamepad A* routes');
const idleAfterCatchup=writes;
// After follow smoothing completes there should be no continuing HMD correction.
for(let i=0;i<200;i++)ctx.se195FollowCamera(.016);
assert.equal(writes,idleAfterCatchup,'no camera rocking at rest after placing houses');
left.input.gamepad.axes=[1,0];ctx.stUpdateSheep(unit,.016);
assert.ok(unit.pos.x>.01,'strafe right works');
left.input.gamepad.axes=[0,-1];blocked=true;const before=unit.pos.clone();
ctx.stUpdateSheep(unit,.016);assert.equal(unit.pos.z,before.z,'wall collision blocks movement');
blocked=false;ctx.se193XRSnapFollow();
ctx.se195FollowCamera(.016);assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200.diagnose().cameraSnaps,2);
inside=false;const count=originalSheep;ctx.stUpdateSheep(unit,.016);
assert.equal(originalSheep,count,'normal mode skips VR direct-drive original');
assert.equal(old199,1,'normal game still calls existing v11.199 owner');
console.log(JSON.stringify({pass:true,checks:17,worldUpdates:originalSheep,
  referenceWrites:writes,buildingCount:session.buildings.length,
  obstacleReads,routeCalls,moveFrames:ctx.window.SWYRL_ENGINE_SHEEP_VR_SPOTLIGHT_200.diagnose().joystickMoveFrames}));
