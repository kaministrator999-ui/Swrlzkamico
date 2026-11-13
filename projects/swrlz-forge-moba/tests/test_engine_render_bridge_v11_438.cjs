'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/engine_simulation_render_bridge_v11_438.js'),'utf8');
assert(!source.includes('requestAnimationFrame('));
assert(!source.includes('setAnimationLoop('));
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z);}
 distanceToSquared(p){return (this.x-p.x)**2+(this.y-p.y)**2+(this.z-p.z)**2;}
}
let now=0,legacy=0,nativeTicks=0,nativeRenders=0;
const grid=new Uint8Array(25);grid[12]=1; // center wall
const session={simulate:false,winner:null,controlledId:'player',
 elapsed:2,navVersion:3,units:[],buildings:[]};
const bot={id:'bot',kind:'sheep',captured:false,path:[],pathVersion:-1,
 pos:new V(-2,0,-2),pathTarget:null,repathAt:0};
session.units=[{id:'player'},bot];
let worker=null;
class FakeWorker {
 constructor(url){worker=this;this.url=url;this.sent=[];this.terminated=false;}
 postMessage(message){this.sent.push(message);if(message.kind==='hello')
  this.onmessage({data:{kind:'ready'}});}
 terminate(){this.terminated=true;}
}
const sandbox={window:{},console,Map,Set,Uint8Array,Worker:FakeWorker,
 THREE:{Vector3:V},Blob:class Blob {constructor(parts){this.parts=parts;}},
 URL:{createObjectURL:()=> 'blob:bridge',revokeObjectURL:()=>{}},
 renderer:{xr:{isPresenting:true},render(){nativeRenders++;return 'rendered';}},
 ST_GRID:1,stSession:session,stNavigation:()=>({extent:2,width:5,blocked:grid}),
 stPath:()=>{legacy++;return [new V(0,0,0)]},
 se437Solo:s=>!!s&&!s.simulate,
 performance:{now:()=>++now},
 stStart:()=>true,stStop:()=>{sandbox.stSession=null;return true;},
 stUpdate:()=>{nativeTicks++;return 'updated';}
};
vm.createContext(sandbox);vm.runInContext(source,sandbox);
const getStats=()=>sandbox.window.SWYRL_ENGINE_RENDER_BRIDGE_438.diagnose();
// First route creates Worker. Handshake is synchronous in this test harness.
let route=vm.runInContext('se438Route(stSession.units[1],stSession.units[1].pos,new THREE.Vector3(2,0,2),0.5)',sandbox);
assert(Array.isArray(route)&&route.length===0);
assert.equal(legacy,0);
const message=worker.sent.find(m=>m.kind==='route');
assert(message,'numeric A* job must be posted');
assert.equal(message.blocked.byteLength,25);
assert.equal(grid[12],1,'native nav array must not be transferred or cleared');
// Exercise the actual pure worker source, not a mocked route calculation.
const workerSource=vm.runInContext('se438WorkerSource',sandbox);
let reply=null;
const workerVm={postMessage:m=>{reply=m;},Uint8Array,Float64Array,Int32Array,Math,Infinity};
vm.createContext(workerVm);
vm.runInContext(workerSource,workerVm);
vm.runInContext('onmessage',workerVm)({data:message});
assert.equal(reply.kind,'result');
assert.equal(reply.id,message.id);
assert(reply.path&&reply.path.length>0,'wall route should exist');
assert(reply.path.every(([x,z])=>!(x===0&&z===0)),'route cannot cross blocked center');
bot.pathVersion=session.navVersion;bot.pathTarget=new V(2,0,2);
worker.onmessage({data:reply});
assert.equal(bot.path.length,reply.path.length);
assert.equal(getStats().workerCompleted,1);
assert.equal(getStats().pendingRoutes,0);
// No-worker branch for local player and non-XR editor; existing path stays native.
assert.equal(vm.runInContext('se438Route(stSession.units[0],new THREE.Vector3(),new THREE.Vector3(1,0,1),.5)',sandbox).length,1);
sandbox.renderer.xr.isPresenting=false;
assert.equal(vm.runInContext('se438Route(stSession.units[1],new THREE.Vector3(),new THREE.Vector3(1,0,1),.5)',sandbox).length,1);
assert.equal(legacy,2);
sandbox.renderer.xr.isPresenting=true;
// Stale and cancelled paths must not mutate the next match.
bot.path=[];bot.pathVersion=-1;
vm.runInContext('se438Route(stSession.units[1],stSession.units[1].pos,new THREE.Vector3(1,0,1),.5)',sandbox);
const stale=worker.sent.filter(m=>m.kind==='route').at(-1);
sandbox.stStop();
worker.onmessage({data:{kind:'result',id:stale.id,path:[[99,99]]}});
assert.equal(bot.path.length,0);
assert(getStats().staleRoutes>=1);
assert.equal(sandbox.stUpdate(.016,0),'updated');
assert.equal(sandbox.renderer.render(), 'rendered');
assert.equal(nativeTicks,1);
assert.equal(nativeRenders,1);
assert.equal(getStats().renderCalls,1);
assert.equal(getStats().gpuAndCompositorTimesNotMeasured,true);
console.log('SE438 PASS: nonblocking numeric A*, native fallback, stale-session discard, render/update preservation and CPU diagnostics');
