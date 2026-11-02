// §E v11.204: Quest Play-only house/skill hold-to-select, tap-repeat and lanes.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 clone(){return new V(this.x,this.y,this.z)}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 copy(a){this.x=a.x;this.y=a.y;this.z=a.z;return this}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 addScaledVector(v,n){this.x+=v.x*n;this.y+=v.y*n;this.z+=v.z*n;return this}
 crossVectors(a,b){this.x=a.y*b.z-a.z*b.y;this.y=a.z*b.x-a.x*b.z;this.z=a.x*b.y-a.y*b.x;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){let n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this}
}
let geometryDisposed=0,materialDisposed=0;
class G{constructor(...args){this.args=args}dispose(){geometryDisposed++}}
class Mat{
 constructor(o={}){Object.assign(this,o);this.color={setHex:v=>{this.hex=v}}}
 dispose(){materialDisposed++}
}
class Group{
 constructor(){this.children=[];this.userData={};this.position=new V();this.visible=true;this.rotation={};
  this.scale={setScalar(v){this.value=v}};}
 add(o){this.children.push(o);o.parent=this}
 traverse(fn){fn(this);this.children.forEach(c=>c.traverse?c.traverse(fn):fn(c))}
 lookAt(p){this.target=p.clone()}
 updateMatrixWorld(){}
}
class Mesh extends Group{constructor(g,m){super();this.geometry=g;this.material=m}}
const scene={children:[],add(x){this.children.push(x)},remove(x){this.children=this.children.filter(c=>c!==x)}};
const session={
 role:'sheep',controlledId:'one',selectedId:'one',winner:null,navVersion:2,
 units:[{id:'one',kind:'sheep',captured:false,isIllusion:false,pos:new V(0,0,0)}],
 buildings:[],rules:{buildSnap:.15,split:true,totems:true},resources:{one:150}
};
const left={index:0,input:{handedness:'left',gamepad:{buttons:Array.from({length:6},()=>({pressed:false})),axes:[0,0,0,0]}},se192:{dot:{visible:true},beam:{visible:true,scale:{z:100}}}};
const right={index:1,ground:new V(0,0,0),input:{handedness:'right',gamepad:{buttons:Array.from({length:6},()=>({pressed:false})),axes:[0,0,0,0]}},se192:{dot:{visible:true},beam:{visible:true,scale:{z:100}}}};
let now=1000,originalFrame=0,originalA=0,originalX=0,originalSelect=0,originalRay=0,originalStick=0;
let commands=[],nativePreviews=0,chooses=0,clears=0,hud=0,feedback=[],oldCleanup=0,oldStart=0;
const ui={build:null,preview:null,placement:null,placementPoint:null,rotation:Math.PI/2,buildingId:null};
const ctx={console,Math,scene,performance:{now:()=>now},
 THREE:{Vector3:V,Group,Mesh,CircleGeometry:G,RingGeometry:G,PlaneGeometry:G,
  MeshBasicMaterial:Mat,DoubleSide:2},
 stSession:session,stUi:ui,stUiBuildNames:{'st-farm':'House','st-income':'Income','st-fort':'Fort'},
 stUiRules:()=>session.rules,terrainHeight:(x,z)=>0.01*x,
 stUiView:()=>({role:'sheep',controlledId:'one',units:session.units}),
 stUiCommand:(type,payload)=>{
  commands.push({type,payload});
  if(type==='build'){
   if(session.buildings.some(b=>Math.abs(b.x-payload.x)<2.4&&Math.abs(b.z-payload.z)<2.4))
    return {ok:false,reason:'Already occupied'};
   session.buildings.push({x:payload.x,z:payload.z,kind:payload.kind});
   session.navVersion++;session.resources.one-=5;return {ok:true};
  }
  if(type==='split')return {ok:session.rules.split};
  if(type==='totem')return {ok:session.rules.totems};
  return {ok:true};
 },
 stUiChooseBuild:kind=>{
  chooses++;ui.build=ui.build===kind?null:kind;
  if(ui.build){ui.preview={};ctx.stUiPlacePreview(new V(0,0,0));}
 },
 stUiClearPreview:()=>{clears++;ui.preview=null;ui.placement=null;ui.placementPoint=null},
 stUiPlacePreview:p=>{
  nativePreviews++;
  ui.placementPoint=p.clone();
  const snap=session.rules.buildSnap;
  const x=Math.round(p.x/snap)*snap,z=Math.round(p.z/snap)*snap;
  const hit=session.buildings.some(b=>Math.abs(b.x-x)<2.4&&Math.abs(b.z-z)<2.4);
  ui.placement={ok:!hit,kind:ui.build,x,z,rotation:ui.rotation};
 },
 stRefreshHUD:()=>{hud++},
 stUiFeedback:()=>{},
 se193:{angle:0},
 se193XRGameActive:()=>true,
 se192InputRecord:side=>side==='left'?left:right,
 se192Pressed:(rec,index)=>!!rec?.input?.gamepad?.buttons?.[index]?.pressed,
 se195Text:()=>({mock:'shared-quest-texture'}),
 se195:{visible:false,photo:false},
 se195SetVisible:v=>{ctx.se195.visible=!!v},
 se191XRHeadPose:()=>({eye:new V(0,3,0),forward:new V(0,0,1)}),
 se193XRFeedback:r=>feedback.push(r),
 se193XRGameGround:r=>r.ground,
 se193XRGameSelect:()=>{throw Error('tap building must use native command receipts, no indirect old click-to-move')},
 se192XRGamepadButton:(rec,button)=>{if(button==='a')originalA++;else if(button==='x')originalX++;return true},
 se192Raycast:()=>{originalRay++;return {empty:true}},
 se192Select:()=>{originalSelect++},
 se192RenderRay:()=>{},
 se192Stick:()=>{originalStick++;return {x:.5,y:.2}},
 se193XRFrame:()=>{originalFrame++},
 se193XRStart:()=>{oldStart++},
 se193XRCleanup:()=>{oldCleanup++},
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_sheep_rapid_grid_wheels_v11_204.js'),'utf8'),ctx);
const internal=vm.runInContext('se204',ctx);
const diag=()=>ctx.window.SWYRL_ENGINE_SHEEP_QUICK_GRID_204.diagnose();
const frame=()=>ctx.se193XRFrame();
const press=(rec,v)=>{rec.input.gamepad.buttons[4].pressed=v};
const tap=(rec,ms=75)=>{press(rec,true);frame();now+=ms;frame();press(rec,false);frame()};
const hold=(rec,ms=400)=>{press(rec,true);frame();now+=ms;frame()};
const release=rec=>{press(rec,false);frame()};
assert.equal(diag().gameplay,true);
assert.equal(ctx.se192XRGamepadButton(right,'a'),true);
assert.equal(ctx.se192XRGamepadButton(left,'x'),true);
assert.equal(originalA+originalX,0,'native cycle/X-menu presses intercepted only during Sheep Tag Play');
tap(right);
assert.equal(session.buildings.length,0,'tap without house does not construct');
assert.ok(feedback.at(-1).reason.includes('Hold A'));
hold(right);
assert.equal(diag().menuType,'build','holding A opens building radial');
assert.equal(internal.wheel.selected,0,'first chooser highlights Farm, not Cancel');
assert.equal(ctx.se192Stick(right).x,0,'right-stick camera orbit suppressed during radial selection');
assert.equal(ctx.se192Raycast(right).ui,'se204:block','radial blocks terrain targets');
ctx.se192Select(right);assert.equal(originalSelect,0);
ctx.se192RenderRay(right,{});
assert.equal(right.se192.dot.visible,false,'world reticle suppressed while wheel is open');
assert.ok(right.se192.beam.scale.z<=1,'controller beam shortened inside radial');
release(right);
assert.equal(ui.build,'st-farm');
assert.equal(ui.rotation,0,'Play-mode houses are never rotated');
assert.equal(diag().pitch,3.6);
assert.equal(diag().anchor.x,0);
assert.equal(diag().anchor.z,0);
assert.equal(diag().menuType,null);
right.ground=new V(3.7,0,-3.3);
ctx.stUiPlacePreview(right.ground);
assert.equal(ui.placement.x,3.6,'first house snapped to 3.6m grid');
assert.equal(ui.placement.z,-3.6,'grid anchors in both axes');
const priorPreview=nativePreviews;
ctx.stUiPlacePreview(new V(3.8,0,-3.5));
assert.equal(nativePreviews,priorPreview,'unchanged snapped cell skips redundant geometry');
assert.ok(diag().previewSkipped>=1);
tap(right);
assert.equal(session.buildings.length,1,'A tap builds exactly once');
assert.equal(session.buildings[0].x,3.6);
assert.equal(session.buildings[0].z,-3.6);
assert.equal(session.buildings[0].kind,'st-farm');
assert.equal(ui.build,'st-farm','successful build keeps the same house equipped');
assert.equal(ui.placement.ok,false,'now-occupied cell turns red immediately');
right.ground=new V(7.4,0,-3.5);tap(right);
assert.equal(session.buildings.length,2,'second A tap builds same house without menu');
assert.equal(session.buildings[1].x,7.2);
assert.equal(session.buildings[1].z,-3.6);
assert.ok(Math.abs(session.buildings[1].x-session.buildings[0].x-3.6)<1e-6,
 'adjacent farms create 1.2 world-unit passable lanes');
right.ground=new V(7.4,0,-3.5);tap(right);
assert.equal(session.buildings.length,2,'occupied cells never place a duplicate');
assert.ok(diag().blocked>=1);
assert.equal(ui.build,'st-farm','blocked taps do not deselect');
// Open same wheel again, choose Income on right stick (0 degrees).
right.se192.dot.visible=true;hold(right);
right.input.gamepad.axes[2]=1;right.input.gamepad.axes[3]=0;frame();
assert.equal(internal.wheel.selected,1);
release(right);
assert.equal(ui.build,'st-income');
assert.equal(ui.rotation,0);
assert.equal(diag().equippedHouse,'st-income');
assert.ok(diag().menuReuses>=1,'radial graphics reused, not recreated');
// Ability wheel uses LEFT X; right stick still selects its options.
right.input.gamepad.axes[2]=0;right.input.gamepad.axes[3]=0;
hold(left);
assert.equal(diag().menuType,'skill');
release(left);
assert.equal(diag().equippedAbility,'split','skill selection independent from house tool');
assert.equal(ui.build,'st-income');
tap(left);
assert.equal(commands.at(-1).type,'split');
assert.equal(commands.at(-1).payload.angle,0);
assert.equal(diag().skillUses,1);
hold(left);
right.input.gamepad.axes[2]=1;right.input.gamepad.axes[3]=0;frame();
assert.equal(internal.wheel.selected,1,'right-stick selects totem in skill radial');
release(left);
assert.equal(diag().equippedAbility,'totem');
session.selectedId='owned-house';ui.buildingId='owned-house';tap(left);
assert.equal(commands.at(-1).type,'totem');
assert.equal(commands.at(-1).payload.id,'owned-house');
session.rules.totems=false;
const usedBefore=commands.length;tap(left);
assert.equal(commands.length,usedBefore,'disabled abilities are never sent to authority');
session.rules.totems=true;
// Main wrist controls retained separately on B; editor uses original input.
ctx.se204MenuToggle();assert.equal(ctx.se195.visible,true);
ctx.se204MenuToggle();assert.equal(ctx.se195.visible,false);
session.role='wolf';
ctx.se192XRGamepadButton(right,'a');
assert.equal(originalA,1,'wolf buttons retain original behavior');
session.role='sheep';
ctx.se204EquipBuilding('st-fort');
session.rules.buildSnap=3;
internal.anchor={x:0,z:0};
const coarse=ctx.se204GridPoint(new V(6.1,0,0));
assert.equal(coarse.x,6,'native coarse 3m map uses aligned 6m lattice');
assert.equal(diag().pitch,6);
assert.equal(internal.wheelBuilds,2,'only house and ability radial meshes created');
const oldDisposals=diag().menuDisposals;
ctx.se193XRCleanup();
assert.equal(oldCleanup,1);
assert.equal(internal.wheels.size,0);
assert.ok(diag().menuDisposals>=oldDisposals+2,'radial meshes disposed on XR cleanup');
assert.ok(geometryDisposed>=10&&materialDisposed>=10,'GPU geometry/materials freed');
assert.equal(diag().equippedHouse,null);
assert.equal(diag().equippedAbility,null);
assert.equal(scene.children.length,0);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_204_sheep_vr_rapid_grid_wheels.py'),'utf8');
assert.ok(patch.includes('if(se204RapidEnabled())se204AfterBuild()'),
 'right trigger retains the selected house after a successful placement');
assert.ok(patch.includes('else if(se204Gameplay())se204MenuToggle()'),
 'right B still opens the full native tools menu');
assert.ok(patch.includes('se204.anchor?.x')&&patch.includes('se204.anchor?.z'),
 'visual grid lines align with actual snapped houses');
assert.ok(patch.includes('stPlacementGridPositions(guide.ticks,tickPositions)'),
 'dense fine-grid tick marks suppressed in rapid mode');
console.log(JSON.stringify({pass:true,checks:52,houses:session.buildings.length,
 commands:commands.length,gridSamples:diag().gridSamples,
 skippedPreviews:diag().previewSkipped,menuBuilds:diag().menuBuilds,
 menuReuses:diag().menuReuses,disposed:geometryDisposed}));
