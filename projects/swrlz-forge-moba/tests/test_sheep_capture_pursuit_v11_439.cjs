'use strict';
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'../runtime/sheep_capture_pursuit_v11_439.js'),'utf8');
assert(!src.includes('requestAnimationFrame(')&&!src.includes('setAnimationLoop('));
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z);}
 distanceToSquared(p){return (this.x-p.x)**2+(this.y-p.y)**2+(this.z-p.z)**2;}
}
const sheep={id:'sheep',kind:'sheep',captured:false,invulnerableUntil:0,pos:new V(1.10,0,0)};
const wolf={id:'wolf',kind:'wolf',pos:new V(0,0,0),order:{action:'attack',id:'sheep'},botAt:0};
const wolf2={id:'wolf2',kind:'wolf',pos:new V(-1,0,0),order:{action:'attack',id:'sheep'},botAt:0};
const s={simulate:false,winner:null,elapsed:1,navVersion:0,units:[sheep,wolf,wolf2],rules:{headstart:0},buildings:[]};
let now=0,legacyApproach=0,botPlans=0,captures=0,blocked=false;
const sandbox={window:{},console,THREE:{Vector3:V},performance:{now:()=>++now},
 renderer:{xr:{isPresenting:true}},stSession:s,se437Solo:()=>true,
 stUnitRadius:u=>u.kind==='wolf'?.68:.27,
 stObstacles:()=>[],stSegmentClear:()=>!blocked,
 stLanesSheepApproach:()=>{legacyApproach++;return new V(9,0,9);},
 stLanesSegmentOccupant:()=>sheep,
 stBotWolf:()=>{botPlans++;},
 stCapture:u=>{u.captured=true;captures++;s.navVersion++;},
 stUpdateWolf:(u)=>{
  // Native movement tries a physical 0.09-unit step, but collision rejects it.
  sandbox.stLanesSegmentOccupant(u,u.pos,new V(u.pos.x+.09,0,0));
  // Reproduce existing native capture scan without mutating production source.
  for(const target of s.units)if(target.kind==='sheep'&&!target.captured&&
    s.elapsed>=target.invulnerableUntil&&
    Math.hypot(u.pos.x-target.pos.x,u.pos.z-target.pos.z)<1.05)sandbox.stCapture(target,u);
 },
 stUpdate:()=>sandbox.stUpdateWolf(wolf,.016)};
vm.createContext(sandbox);vm.runInContext(src,sandbox);
const diagnose=()=>sandbox.window.SWYRL_ENGINE_SHEEP_CAPTURE_PURSUIT_439.diagnose();
let p=sandbox.stLanesSheepApproach(wolf,sheep);
assert.equal(p.x,1.1,'moving sheep must be approached at its current position');
assert.equal(legacyApproach,0,'direct chase should not synchronously A* scan 9 spots');
blocked=true;assert.equal(sandbox.stLanesSheepApproach(wolf,sheep),null);
assert.equal(legacyApproach,0,'blocked Quest chase must not spam native A*');
blocked=false;assert.equal(sandbox.se439DirectChase(wolf,sheep.pos,{rules:s.rules,obstacles:[]}),true);
assert.equal(diagnose().directRoutes,1);
sandbox.stBotWolf(wolf);sandbox.stBotWolf(wolf2);
assert.equal(botPlans,1,'only one full wolf planning decision per tick');
assert.equal(diagnose().deferredWolfPlans,1);
s.elapsed+=.016;sandbox.stBotWolf(wolf2);assert.equal(botPlans,2);
// Actual centre distance is 1.10 > 1.05, but rejected 0.09 movement sweep
// crosses 1.05 and should yield one legal capture, not route-spam.
assert.equal(sheep.pos.x-wolf.pos.x,1.10);
sandbox.stUpdate(.016,0);
assert.equal(captures,1);
assert.equal(sheep.captured,true);
assert.equal(diagnose().sweptTags,1);
assert.equal(diagnose().actualCaptures,1);
assert.equal(diagnose().duplicateAttempts,0);
assert.equal(diagnose().maxCaptureFrameMs>0,true);
assert.equal(diagnose().navChangeCaptures,1);
// Captured flag protects against repeated wolf tags during pursuit.
sandbox.stUpdateWolf(wolf,.016);assert.equal(captures,1);
// Invulnerability remains authoritative; no instant recapture on rescue.
sheep.captured=false;sheep.invulnerableUntil=s.elapsed+3;
sandbox.stUpdateWolf(wolf,.016);assert.equal(captures,1);
sheep.invulnerableUntil=0;
// LAN simulation remains on untouched native capture/movement paths.
s.simulate=true;
sheep.captured=false;sandbox.stUpdateWolf(wolf,.016);
assert.equal(captures,1,'swept-contact behavior must not change LAN/simulation');
assert.equal(sandbox.stLanesSheepApproach(wolf,sheep).x,9,'legacy approach retained outside solo XR');
console.log('SE439 PASS: moving-sheep direct pursuit, bounded wolf plans, swept capture, one-shot guard, invulnerability and non-SOLO fallback');
