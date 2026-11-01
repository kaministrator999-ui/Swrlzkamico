// §E v11.197 — tests new flat browser camera and exclusive fog painters.
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/sheep_visual_stability_v11_197.js'),'utf8');
new vm.Script(source,{filename:'sheep_visual_stability_v11_197.js'});
class V {
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 set(x,y,z){Object.assign(this,{x,y,z});return this;}
 clone(){return new V(this.x,this.y,this.z);}
}
const flags={snapshots:0,rings:[],painted:0,projections:0,cameraMoves:0};
const units=[
 {id:'mine',kind:'sheep',pos:new V(6,0,-4)},
 {id:'friend',kind:'sheep',pos:new V(11,0,12)},
 {id:'wolf',kind:'wolf',pos:new V(-5,0,-6)}
];
const ctx={
 window:{},Number,Math,Set,actors:[],
 THREE:{LinearMipmapLinearFilter:1008,MathUtils:{clamp:(n,min,max)=>Math.max(min,Math.min(max,n))}},
 stSession:{simulate:false,controlledId:'mine',selectedId:'friend',rules:{bounds:40},
  units,buildings:[{id:'farm',kind:'st-farm',pos:new V(4,0,4),hp:100}]},
 stUi:{keys:new Set(),follow:true,focus:new V(),zoom:1},
 stStatus:()=>{flags.snapshots++;return {units:[]};},
 stUpdateCamera:()=>{throw Error('legacy status-snapshot camera must not run')},
 stUiUpdateRings:status=>{flags.rings.push(status)},
 stSoftFogPaint:()=>{flags.painted++},
 se150Match:{active:false},
 se195Gameplay:()=>false,
 perspectiveCamera:{aspect:1.6,fov:45,up:new V(),position:new V(),
  lookAt(){flags.cameraMoves++},updateMatrixWorld(){},
  updateProjectionMatrix(){flags.projections++}},
 renderer:{info:{render:{calls:27}}}
};
const sandbox=vm.createContext(ctx);
vm.runInContext(source,sandbox);
function jsEval(code){return vm.runInContext(code,sandbox);}
jsEval('stUpdateCamera(.016)');
assert.equal(flags.snapshots,0,'camera must not serialize full AI and units every rendered frame');
assert.equal(ctx.stUi.focus.x,11);
assert.equal(ctx.stUi.focus.z,12);
assert.equal(flags.cameraMoves,1);
assert.equal(flags.projections,1);
assert.equal(flags.rings[0].units.length,2,'only selected/controlled rings are needed');
assert.equal(flags.rings[0].buildings.length,0);
assert.equal(jsEval('window.SWYRL_ENGINE_SHEEP_VISUAL_197.diagnose().avoidedFullStatusSnapshots'),1);
jsEval('stUpdateCamera(.016)');
assert.equal(flags.projections,1,'steady fov should not recalculate projection every frame');
assert.equal(flags.snapshots,0);
ctx.stUi.keys.add('d');
jsEval('stUpdateCamera(.05)');
assert.equal(ctx.stUi.follow,false,'WASD detaches follow mode');
assert(ctx.stUi.focus.x>11,'keyboard panning still moves camera');
ctx.stUi.keys.delete('d');
ctx.stSession.selectedId='farm';
jsEval('stUpdateCamera(0)');
assert.equal(flags.rings.at(-1).buildings.length,1,'selected farm marker remains intact');
assert.equal(flags.rings.at(-1).units.length,1,'controlled sheep remains visible');
ctx.stSession.fog={mesh:{position:{y:.23}}};
jsEval('stSoftFogPaint(stSession)');
assert.equal(flags.painted,1);
ctx.se150Match.active=true;
jsEval('stSoftFogPaint(stSession)');
assert.equal(flags.painted,1,'single team-fog compositor cannot be overwritten by solo painter');
assert.equal(jsEval('window.SWYRL_ENGINE_SHEEP_VISUAL_197.diagnose().multiplayerFogOverwritePrevented'),1);
ctx.se150Match.active=false;
jsEval('stSoftFogPaint(stSession)');
assert.equal(flags.painted,2,'solo fog resumes when LAN session ends');
ctx.se195Gameplay=()=>true;
const moved=flags.cameraMoves;
jsEval('stUpdateCamera(.016)');
assert.equal(flags.cameraMoves,moved,'2D tracking must stay inactive in immersive WebXR');
console.log('PASS V11.197 · native 2D sheep focus/pan/selection, avoided status snapshots, LAN fog painter exclusivity');
