const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new V(this.x,this.y,this.z)}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 distanceToSquared(v){return (this.x-v.x)**2+(this.y-v.y)**2+(this.z-v.z)**2}
}
let made=0,disposed=0;
const s={simulate:false,controlledId:'player',elapsed:0,winner:null,units:[],buildings:[]};
const player={id:'player',kind:'sheep',pos:new V(-8,0,-8),home:new V(0,0,0)};
const bot={id:'bot',kind:'sheep',pos:new V(1,0,0),home:new V(1,0,0),botIndex:1};
s.units=[player,bot];
s.buildings=[{owner:'player',hp:20,pos:new V(-9,0,-8)}];
const sandbox={THREE:{Vector3:V},window:{},stSession:s,renderer:{xr:{isPresenting:true}},
 paused:false,performance:{now:()=>0},stDisposeVisual:()=>{disposed++},
 stMakeSpirit:()=>({serial:++made}),stStop:()=>{},stUpdate:()=>{},
 stCapture:unit=>{unit.captured=true},console};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(require('node:path').join(__dirname,'../runtime/sheep_territory_capture_v11_437.js'),'utf8'),sandbox);
assert.equal(vm.runInContext('se437BaseAllowed(stSession.units[1],new THREE.Vector3(-9,0,-8))',sandbox),false);
assert.equal(vm.runInContext('se437BuildAllowed(stSession.units[1],-10,-9)',sandbox),false);
assert.equal(vm.runInContext('se437BaseCandidates(stSession.units[1]).length',sandbox),13);
assert.equal(vm.runInContext('se437BaseAllowed(stSession.units[1],new THREE.Vector3(20,0,18))',sandbox),true);
s.elapsed=1;sandbox.stUpdate();assert.equal(made,1);
const pooled=sandbox.stMakeSpirit();assert.equal(pooled.serial,1);assert.equal(made,1);
const state=sandbox.window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_436.diagnose();
assert.equal(state.poolHits,1);assert.equal(state.warmed,1);
s.elapsed=2;sandbox.stUpdate();assert.equal(made,2);
sandbox.stCapture(bot,null);assert.equal(bot.captured,true);
sandbox.stStop();assert.equal(disposed,1);
assert.equal(sandbox.window.SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_436.diagnose().captures,1);
console.log('SE437 PASS: individual territory, forbidden player plots, warmed spirit use, disposal, capture diagnostics');
