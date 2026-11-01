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

const baseSpace={getOffsetReferenceSpace(transform){return {parent:this,transform,getOffsetReferenceSpace:this.getOffsetReferenceSpace};}};
let currentSpace=baseSpace,spaceWrites=0;
ctx.XRRigidTransform=class{constructor(position){this.position=position;}};
ctx.renderer.xr.getReferenceSpace=()=>currentSpace;
ctx.renderer.xr.setReferenceSpace=ref=>{currentSpace=ref;spaceWrites++;};
evaluate('se195.referenceBase=null;se195.referenceOffset.set(0,0,0);');
assert.equal(evaluate('se195MoveRig(1,2,3)'),true);
assert.equal(evaluate('se195MoveRig(1,0,-1)'),true);
assert.equal(spaceWrites,2,'reference space changes tracked');
assert.equal(currentSpace.parent,baseSpace,'both writes must reference the original XR base, not nest');
assert.deepEqual([currentSpace.transform.position.x,currentSpace.transform.position.y,currentSpace.transform.position.z],
 [-2,-2,-2],'offset uses accumulated inverse translation');
delete ctx.renderer.xr.getReferenceSpace;
delete ctx.renderer.xr.setReferenceSpace;
delete ctx.XRRigidTransform;

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

console.log('PASS V11.195 baseline');
const v196=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_sheep_stability_v11_196.js'),'utf8');
new vm.Script(v196,{filename:'engine_xr_sheep_stability_v11_196.js'});
let fly=0,grab=0;
ctx.se192MoveFrame=()=>{fly++};
ctx.se192GrabFrame=()=>{grab++};
vm.runInContext(v196,sandbox);
assert.equal(evaluate('se196FogRepair(stSession)'),true);
assert(f.mesh.position.y>=.23,'2D fog stays safely above meadow and shallow floor');
assert.equal(f.mesh.material.depthWrite,false,'fog cannot fight for depth buffer');
assert.equal(f.mesh.material.depthTest,true,'buildings can still occlude fog');
assert.equal(f.mesh.material.polygonOffset,true,'depth offset prevents z fighting');
assert.equal(evaluate('se196FogRepair(stSession)'),true,'fog setup is idempotent');
const origPaints=state.draws;
state.game=false;state.menu=false;
state.time=1700;
evaluate('stSoftFogPaint(stSession)');
state.time=1810;
evaluate('stSoftFogPaint(stSession)');
assert.equal(state.draws,origPaints+1,'2D fog redraw is coalesced');
state.time=1930;
evaluate('stSoftFogPaint(stSession)');
assert.equal(state.draws,origPaints+2,'2D fog continues to refresh after budget');
state.game=false;state.menu=true;
evaluate('se192MoveFrame(.016);se192GrabFrame({index:1})');
assert.equal(fly,0,'native editor flight cannot override Sheep Tag XR cinematic');
assert.equal(grab,0,'native editor grip cannot move authored actors during cinematic');
state.menu=false;
evaluate('se192MoveFrame(.016);se192GrabFrame({index:1})');
assert.equal(fly,1,'normal VR editor flight preserved');
assert.equal(grab,1,'normal VR editor grip preserved');
const radial={position:new V(),visible:true,lookAt(target){this.facing=target.clone();},
 updateMatrixWorld(){this.updated=true;}};
evaluate("se195.radial=null");
ctx.se192InputRecord=()=>null; // Head-relative fallback when Quest hand is not yet tracked.
ctx.testRadial=radial;
evaluate('se195.radial=testRadial;se195.visible=true;');
evaluate('se195PositionRadial(true)');
assert(radial.updated && radial.facing,'menu uses Object3D.lookAt(head) to face readable front');
assert.equal(radial.facing.x,cameraEye.eye.x);
assert.equal(radial.facing.y,cameraEye.eye.y);
const before=radial.position.clone();
cameraEye.eye=new V(6,2,9);
evaluate('se195PositionRadial(false)');
assert.equal(radial.position.distanceTo(before),0,'open radial stays still while pointing');
state.menu=true;state.game=false;
ctx.se195FocusSheep=()=>new V(0,0,0);
evaluate('se196.menuAnchored=false');
const moved=state.movement.length;
evaluate('se195MenuCamera(.016);se195MenuCamera(.016);');
assert.equal(state.movement.length,moved+1,'authored Sheep Tag cinematic repositions headset once, then stays anchored');
assert.equal(evaluate('se196.menuAnchored'),true);
state.menu=false;state.game=true;
evaluate('se195.rigReady=false;se193.zoom=1;');
const gameStart=state.movement.length;
evaluate('se195FollowCamera(.016)');
assert.equal(state.movement.length,gameStart+1,'gameplay camera snaps immediately to strategic position once');
assert.equal(evaluate('se196.gameSnaps'),1);
assert.equal(state.statusCalls,0,'camera never creates full stStatus snapshots every render frame');

state.game=false;state.menu=true;
const menuOptions=evaluate("se195Options('menu','main')");
assert(menuOptions.some(([action,label])=>action==='recenter'&&label==='REFOCUS'),'menu offers explicit VR recenter instead of camera flight');
assert(!menuOptions.some(([action])=>action==='cinema'),'no inert auto-flight camera toggle');
const previousSnaps=evaluate('se196.menuSnaps');
evaluate("se195HandleAction('recenter',null)");
assert.equal(evaluate('se196.menuSnaps'),previousSnaps+1,'REFOCUS is a working explicit camera adjustment');

console.log('PASS V11.196 · 2D fog separation/paint budget, unmoving right-hand radial, one-time cinematic & gameplay camera');

