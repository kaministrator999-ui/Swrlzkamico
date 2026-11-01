// §E v11.198 — mock native Quest controller, 6DoF grab, axis-gizmo and flight.
// Tests state and actions, not a claim of physical headset performance.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_editor_controls_v11_198.js'),'utf8');
new vm.Script(source,{filename:'engine_xr_editor_controls_v11_198.js'});
class V {
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}
 clone(){return new V(this.x,this.y,this.z);}
 copy(v){return this.set(v.x,v.y,v.z);}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 setY(y){this.y=y;return this;}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 addScaledVector(v,n){this.x+=v.x*n;this.y+=v.y*n;this.z+=v.z*n;return this;}
 multiplyScalar(n){this.x*=n;this.y*=n;this.z*=n;return this;}
 lerp(v,n){this.x+=(v.x-this.x)*n;this.y+=(v.y-this.y)*n;this.z+=(v.z-this.z)*n;return this;}
 normalize(){const n=this.length()||1;return this.multiplyScalar(1/n);}
 dot(v){return this.x*v.x+this.y*v.y+this.z*v.z;}
 crossVectors(a,b){return this.set(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);}
 lengthSq(){return this.dot(this);}
 length(){return Math.sqrt(this.lengthSq());}
 distanceTo(v){return this.clone().sub(v).length();}
 toArray(){return [this.x,this.y,this.z];}
}
let transactions=0,commits=0,selectionCount=0,flyDelta=[],worldHand=new V(.2,1,-.5);
let hit=null;const buttons=new Set();
const actor={isObject3D:true,visible:true,position:new V(2,0,3),
 userData:{actorType:'box'},parent:null,updateMatrixWorld(){},
 getWorldPosition(v){return v.copy(this.position)}};
const rightCtl={updateMatrixWorld(){},getWorldPosition(v){return v.copy(worldHand)}};
const right={index:1,input:{handedness:'right'},controller:rightCtl};
const left={index:0,input:{handedness:'left'},controller:{}};
const m={version:'1'};
const ctx={THREE:{Vector3:V,MathUtils:{clamp:(v,min,max)=>Math.max(min,Math.min(max,v)),degToRad:v=>v*Math.PI/180}},
 window:{},localStorage:{getItem:()=>null,setItem(k,v){m[k]=v}},
 actors:[actor],selected:actor,scene:{},Number,Math,Map,Set,JSON,
 se181XR:{session:{},controllers:[left,right]},
 renderer:{xr:{isPresenting:true}},
 playing:false,simulating:false,se193:{editorCaptureOpen:false},se195:{visible:false,photo:false,mode:'editor',page:'main',referenceBase:null,referenceOffset:new V()},
 se195Active:()=>true,se193XRGameActive:()=>false,se193XRMenuActive:()=>false,
 se195Mode:()=> 'editor',se195Options:()=>[],se195HandleAction:()=>false,
 se195Page:p=>{ctx.se195.page=p;},se195SetVisible:v=>{ctx.se195.visible=v;},
 se192:{mode:'edit',inputSamples:0,turnLatched:false,lastTurn:0},
 se192Pressed:(record,index)=>record===right&&index===1&&buttons.has('grip')||
  record===left&&index===3&&buttons.has('boost')||
  record===left&&index===1&&buttons.has('vertical'),
 se192Raycast:()=>hit,se192Select:()=>{selectionCount++},
 se192GrabFrame:()=>{},se192MoveFrame:()=>{},
 se192VRFrame:()=>{},se192VRStart:()=>{},se192VRCleanup:()=>{},
 se192Ray:()=>({direction:new V(0,0,-1),origin:new V(0,0,3),ray:{intersectObjects:()=>[]}}),
 se192InputRecord:side=>side==='left'?left:right,
 se192Stick:rec=>rec===left?{x:0,y:-1}:{x:0,y:0},
 se191XRHeadPose:()=>({eye:new V(0,1,0),forward:new V(0,0,-1)}),
 se195MoveRig:(x,y,z)=>{flyDelta.push([x,y,z]);return true;},
 se192SnapTurn:()=>true,
 beginTransaction:()=>{transactions++},commitTransaction:()=>{commits++},
 rebuildHierarchy:()=>{},syncInspector:()=>{},refreshDebug:()=>{},
 selectActor:()=>{selectionCount++},
 se193XRCapture:()=>true,
 performance:{now:()=>1000},document:{},se192PanelsVisible:()=>{}
};
const sandbox=vm.createContext(ctx);vm.runInContext(source,sandbox);
function evaluate(s){return vm.runInContext(s,sandbox);}
assert.equal(evaluate('se198Editor()'),true);
let options=evaluate("se195Options('editor','main')");
assert.deepEqual(Array.from(options,x=>x[0]),['select','gizmos','flight','place','help']);
assert.equal(evaluate('se195HandleAction("faster",null)'),true);
assert.equal(evaluate('se198.speed'),6.4);
assert.equal(evaluate('se195HandleAction("slower",null)'),true);
assert.equal(evaluate('se198.speed'),3.2);
assert.equal(evaluate('se195HandleAction("turnAngle",null)'),true);
assert.equal(evaluate('se198.turnDegrees'),30);
assert(m['swyrl.xr.editor.fly.v2'].includes('30'),'per-device settings saved');
hit={object:actor,distance:1};
buttons.add('grip');
evaluate('se198GrabFrame(se192InputRecord("right"))');
assert.equal(transactions,0,'no undo transaction until object actually moves');
worldHand=new V(.5,1.2,-1.3);
evaluate('se198GrabFrame(se192InputRecord("right"))');
assert.equal(transactions,1);
assert(actor.position.x>2 && actor.position.y>0 && actor.position.z<3,
 'world tracked motion must change X/Y/Z together');
buttons.delete('grip');
evaluate('se198GrabFrame(se192InputRecord("right"))');
assert.equal(commits,1);
assert(Math.abs(actor.position.z-2.2)<1e-8,'pull controller back .8m pulls object toward the player');
assert.equal(actor.userData.spawnPos[2],2.2);
assert.equal(evaluate('se198.grab'),null,'releasing grip clears state');
ctx.se195.visible=true;
buttons.add('grip');evaluate('se198GrabFrame(se192InputRecord("right"))');
assert.equal(evaluate('se198.grab'),null,'opening radial prevents grabbing through menus');
buttons.delete('grip');ctx.se195.visible=false;
const numeric=evaluate('se198AxisParam({origin:new THREE.Vector3(0,0,5),direction:new THREE.Vector3(.5,0,-1).normalize()},new THREE.Vector3(0,0,0),new THREE.Vector3(1,0,0))');
assert(Math.abs(numeric-2.5)<1e-8,'ray-axis projection supports precise gizmo selection');
const nearParallel=evaluate('se198AxisParam({origin:new THREE.Vector3(1,0,0),direction:new THREE.Vector3(1,0,0)},new THREE.Vector3(),new THREE.Vector3(1,0,0))');
assert.equal(nearParallel,null,'parallel ray cannot cause a position explosion');
evaluate('se198FlyFrame(.016)');
assert(flyDelta.length===1 && flyDelta[0][2]<0,'editor free-flight uses the stable rig');
const z=flyDelta[0][2];ctx.se192Pressed=(record,i)=>record===left&&i===3;
evaluate('se198FlyFrame(.016)');
assert(evaluate('se198.boosts')>0,'left thumbstick click boosts flight');
assert(Math.abs(flyDelta.at(-1)[2])>Math.abs(z),'speed boost accelerates flight');
ctx.playing=true;const prior=flyDelta.length;
evaluate('se198FlyFrame(.016)');
assert.equal(flyDelta.length,prior,'game Play mode never runs editor locomotion');
ctx.playing=false;ctx.se195.visible=true;
evaluate('se198FlyFrame(.016)');
assert.equal(flyDelta.length,prior,'open menu does not move editor');
assert.equal(evaluate('se198.velocity.lengthSq()'),0,'menu flight cancellation clears velocity');
assert(!source.includes('renderer.setAnimationLoop('),'single engine render loop preserved');
assert(!source.includes('requestAnimationFrame('),'no hidden update loop');
console.log('PASS V11.198 · 6DoF toward-hand grab, native transaction, modal guard, axis projection, boosted smooth flight, persisted options');
