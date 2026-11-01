const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z)}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 setY(v){this.y=v;return this}
 addScaledVector(v,s){this.x+=v.x*s;this.y+=v.y*s;this.z+=v.z*s;return this}
 multiplyScalar(s){this.x*=s;this.y*=s;this.z*=s;return this}
 length(){return Math.hypot(this.x,this.y,this.z)}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 distanceToSquared(o){return (this.x-o.x)**2+(this.y-o.y)**2+(this.z-o.z)**2}
 normalize(){return this.multiplyScalar(1/(this.length()||1))}
 lerp(v,a){this.x+=(v.x-this.x)*a;this.y+=(v.y-this.y)*a;this.z+=(v.z-this.z)*a;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 setLength(n){return this.normalize().multiplyScalar(n)}
}
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
const unit={id:'sheep1',kind:'sheep',pos:new V(),speed:5,order:null,destination:null};
const session={controlledId:unit.id,units:[unit],simulate:false,winner:null,elapsed:10,
 rules:{bounds:60,headstart:0},pen:{x:0,z:0,halfX:8,halfZ:8}};
const left={input:{gamepad:{axes:[0,0]}}},right={input:{gamepad:{axes:[0,0]}}};
const frame={forward:new V(0,0,-1),eye:new V(0,2,0)};
let baseUpdates=0,orders=0,moveRigCalls=0,gameActive=true,passable=true;
const ctx={
 THREE:{Vector3:V,MathUtils:{clamp}},Math,window:{},
 stSession:session,paused:false,
 se193:{angle:Math.PI,focus:new V(),follow:true,zoom:1},
 se195:{rigReady:true,rigAt:0,photo:false},
 se195Gameplay:()=>gameActive,
 se192InputRecord:side=>side==='left'?left:right,
 se192Stick:r=>({x:r.input.gamepad.axes[0],y:r.input.gamepad.axes[1]}),
 se191XRHeadPose:()=>frame,
 se195MoveRig:(x,y,z)=>{moveRigCalls++;frame.eye.addScaledVector(new V(x,y,z),1);return true;},
 stObstacles:()=>[],stUnitRadius:()=>.4,stSegmentClear:()=>passable,
 stSetOrder:(u,o)=>{orders++;u.order=o;u.destination=o?new V(o.x,0,o.z):null;},
 stUpdateSheep:(u,dt)=>{baseUpdates++;if(u.order?.action==='move')u.pos.copy(u.destination);},
 stUpdateWolf:()=>{},se193XRStart:()=>{},se193XRCleanup:()=>{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime','engine_xr_sheep_thumbstick_v11_199.js'),'utf8'),ctx);
ctx.se193XRStart();assert.equal(ctx.se193.zoom,1.4);
ctx.se195.rigReady=false;ctx.se195FollowCamera(.016);
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_VR_THUMBSTICK_199.diagnose().cameraSnaps,1);
assert.equal(ctx.se193.follow,true);assert.ok(Math.abs(frame.eye.z-35)<.001);
assert.ok(Math.abs(frame.eye.y-23.8)<.001);
left.input.gamepad.axes=[0,-1];ctx.stUpdateSheep(unit,.016);
assert.ok(unit.pos.z<-.5,'left stick forward moves the sheep ahead');
assert.equal(ctx.se193.follow,true,'moving sheep must not detach follow');
const first=orders;ctx.stUpdateSheep(unit,.016);
assert.equal(orders,first,'continuous input reuses the same native order');
ctx.se195FollowCamera(.016);assert.equal(ctx.se193.follow,true);
left.input.gamepad.axes=[1,0];ctx.stUpdateSheep(unit,.016);
assert.ok(unit.pos.x>.5,'screen right maps to +X when looking -Z');
left.input.gamepad.axes=[0,0];ctx.stUpdateSheep(unit,.016);
assert.equal(unit.order,null);assert.ok(ctx.window.SWYRL_ENGINE_SHEEP_VR_THUMBSTICK_199.diagnose().releases>0);
const before=unit.pos.clone();passable=false;left.input.gamepad.axes=[0,-1];
ctx.stUpdateSheep(unit,.016);assert.equal(unit.pos.z,before.z,'obstacles block movement');
gameActive=false;const preOrders=orders;ctx.stUpdateSheep(unit,.016);
assert.equal(orders,preOrders,'normal 2D play never uses VR orders');
gameActive=true;passable=true;ctx.stUpdateSheep(unit,.016);assert.ok(unit.order);
ctx.se193XRCleanup();assert.equal(unit.order,null,'VR exit cancels held movement');
console.log(JSON.stringify({pass:true,checks:14,baseUpdates,orders,moveRigCalls}));
