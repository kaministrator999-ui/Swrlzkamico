// §E v11.195 focused Quest XR logic checks (no fake headset).
// Validate modal menu priority, camera origin delta, fog throttling, menu policy.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const script=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_sheep_stability_v11_195.js'),'utf8');
new vm.Script(script,{filename:'engine_xr_sheep_stability_v11_195.js'});
class V {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z);}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 setY(v){this.y=v;return this;}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this;}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this;}
 addScaledVector(v,k){this.x+=v.x*k;this.y+=v.y*k;this.z+=v.z*k;return this;}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 multiplyScalar(n){this.x*=n;this.y*=n;this.z*=n;return this;}
 length(){return Math.hypot(this.x,this.y,this.z);}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z;}
 distanceTo(v){return this.clone().sub(v).length();}
 setLength(n){const l=this.length()||1;return this.multiplyScalar(n/l);}
 lerp(v,t){this.x+=(v.x-this.x)*t;this.y+=(v.y-this.y)*t;this.z+=(v.z-this.z)*t;return this;}
 normalize(){const n=this.length()||1;return this.multiplyScalar(1/n);}
 crossVectors(a,b){return this.set(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);}
}
const cameraEye={eye:new V(5,2,8),forward:new V(0,-.3,-1)};
const state={xr:true,game:true,menu:false,time:1000,rayCount:0,draws:0,movement:[],input:[],statusCalls:0};
const scene={add(){},remove(){},updateMatrixWorld(){}};
const THREE={Vector3:V,MathUtils:{clamp:(v,a,b)=>Math.max(a,Math.min(b,v))},LinearFilter:'linear',
 Plane:class{},Raycaster:class{},Group:class{},Quaternion:class{},Matrix4:class{}};
const ctx={THREE,scene,window:{},performance:{now:()=>state.time},Number,Math,Map,Set,
 se181XR:{session:{},controllers:[]},renderer:{xr:{isPresenting:true}},currentProject:{kind:'sheep-tag'},
 se193:{follow:true,focus:new V(),angle:0,zoom:1,ready:false,editorCaptureOpen:false},
 se191XR:{framebufferScale:.8},se191XRPrepareFramebuffer:()=>{},
 se192:{panel:null,panelButtons:[],panelTextures:[],panelVisible:false},
 stSession:{controlledId:'one',rules:{bounds:40},units:[{id:'one',pos:new V(3,0,1)}]},
 se193XRGameActive:()=>state.game,
 se193XRMenuActive:()=>state.menu,
 se192InputRecord:()=>({index:1}),
 se192Stick:()=>({x:0,y:0}),
 se191XRHeadPose:()=>({eye:cameraEye.eye.clone(),forward:cameraEye.forward.clone()}),
 se192MoveBy:(x,y,z)=>{state.movement.push({x,y,z});return true;},
 stStatus:()=>{state.statusCalls++;return {}},
 stCreateFog:()=>{},stSoftFogPaint:()=>{state.draws++},
 se156PaintTeamFog:()=>{},stUpdateCamera:()=>{},stRefreshHUD:()=>{},stUiDrawMinimap:()=>{},
 se192Raycast:()=>{state.rayCount++;return {object:{name:'underlying house'},distance:8}},
 se193XRGameSelect:()=>{state.rayCount++;return true},
 se192Select:()=>{state.rayCount++;return true},
 se192XRGamepadButton:()=>false,
 se192RenderRay:()=>{},se193XRSnapFollow:()=>{},
 se193XRCameraFrame:()=>{},se193XRCapture:()=>true,
 se193XRStart:()=>{},se193XRCleanup:()=>{},se193XRFrame:()=>{},
 se192Ray:()=>({origin:new V(0,1,0),direction:new V(0,0,-1),
  ray:{far:140,intersectObjects:()=>[],intersectObject:()=>[]}}),
 se193XRGameGround:()=>new V(0,0,-4),
 se181XRMakeExitPanel:()=>{throw Error('duplicate exit invoked')},
 se191XRMakeBeacon:()=>{throw Error('duplicate beacon invoked')},
 se192CreatePanel:()=>{throw Error('large menu invoked')},
 se193XRPanelFor:()=>{},se193XRPanelHit:()=>{},
 se193XRAction:()=>{},se192Action:()=>{},se193XRDisposePanel:()=>{},
 se192PanelsVisible:()=>{},document:{getElementById:()=>null},
 paused:false,actors:[],seLevelsMenuActors:()=>[],stRules:()=>({bounds:40}),
 seLevels:{playingMenu:false},seLevelsOwns:()=>false,seLevelsCurrent:()=>({role:'menu'})
};
const sandbox=vm.createContext(ctx);
vm.runInContext(script,sandbox);
function evaluate(s){return vm.runInContext(s,sandbox);}
const menu=evaluate("se195Options('menu','main')");
assert.equal(menu.length,5);
assert.equal(menu.some(([action])=>action==='exit'),false,'Meta system controls exit');
assert.equal(evaluate("se195Options('game','main')").length,5);
assert(evaluate("se195Options('game','capture')").some(x=>x[0]==='photo'));
evaluate("se195FollowCamera(.02)");
assert(state.movement.length>0,'strategic camera must adjust tracked eye');
assert(state.movement.at(-1).x<0,'sheep x=3 to eye x=5 should recenter left');
assert(state.movement.at(-1).z>0,'camera should relocate behind the sheep');
assert.equal(state.statusCalls,0,'follow camera must read native session, not serialize stStatus per XR frame');
const old=state.rayCount;
const fast=evaluate('se192Raycast({index:1})');
assert(fast.ground && fast.distance>0,'gameplay beam ray should be cheap terrain target');
assert.equal(state.rayCount,old,'ray-frame must not recursively test scene actors');
evaluate('se195PreciseSelection=true');
const precise=evaluate('se192Raycast({index:1})');
assert(precise.object,'trigger path still selects exact scene objects');
assert(state.rayCount>old);
evaluate('se195PreciseSelection=false;se195.visible=true;');
const blocked=evaluate('se192Raycast({index:1})');
assert.equal(blocked.ui,'se195:block','visible radial blocks laser through to scenery');
const previous=state.rayCount;
assert.equal(evaluate('se195Select({index:1})'),true,'menu misses consume trigger');
assert.equal(state.rayCount,previous,'menu cannot select background house');
evaluate('se195.visible=false;');
const f={width:40,mesh:{position:{y:.055},material:{}},canvas:{width:150,height:150},
 softMemory:{width:150,height:150},texture:{}};
ctx.stSession.fog=f;
evaluate('se195.lastFogSession=stSession;se195.fogAt=0;');
evaluate('stSoftFogPaint(stSession)');
state.time=1200;evaluate('stSoftFogPaint(stSession)');
assert.equal(state.draws,1,'fog repaint coalesced inside 290ms budget');
state.time=1420;evaluate('stSoftFogPaint(stSession)');
assert.equal(state.draws,2,'fog eventually refreshes');
evaluate('se195FogPrepare(stSession)');
assert(f.mesh.position.y>=.17,'stereo fog must stand off from meadow');
assert(f.mesh.material.polygonOffset,'fog depth offset required');
assert.equal(f.canvas.width,120,'fog canvas capped at 3x logical grid width when world=80 units');
evaluate('se181XRMakeExitPanel();se191XRMakeBeacon();se192CreatePanel();');
assert.equal(ctx.se192.panelVisible,false,'legacy long panels disabled');
console.log('PASS V11.195 · menu-modal ray, Quest follow recenter, cheap ray, fog and no duplicate exit');
