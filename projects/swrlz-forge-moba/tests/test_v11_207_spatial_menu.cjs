// §E v11.207 · Quest Play spatial menu grab/pin/tilt/recenter; editor isolated.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 copy(v){return this.set(v.x,v.y,v.z)}
 clone(){return new V(this.x,this.y,this.z)}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 applyQuaternion(q){
  const x=this.x,y=this.y,z=this.z,qx=q.x,qy=q.y,qz=q.z,qw=q.w;
  const ix=qw*x+qy*z-qz*y,iy=qw*y+qz*x-qx*z,iz=qw*z+qx*y-qy*x,iw=-qx*x-qy*y-qz*z;
  this.x=ix*qw+iw*-qx+iy*-qz-iz*-qy;
  this.y=iy*qw+iw*-qy+iz*-qx-ix*-qz;
  this.z=iz*qw+iw*-qz+ix*-qy-iy*-qx;
  return this;
 }
}
class Q{
 constructor(x=0,y=0,z=0,w=1){Object.assign(this,{x,y,z,w})}
 clone(){return new Q(this.x,this.y,this.z,this.w)}
 copy(q){Object.assign(this,{x:q.x,y:q.y,z:q.z,w:q.w});return this}
 invert(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this}
 multiply(q){
  const a=this.clone();
  this.x=a.x*q.w+a.w*q.x+a.y*q.z-a.z*q.y;
  this.y=a.y*q.w+a.w*q.y+a.z*q.x-a.x*q.z;
  this.z=a.z*q.w+a.w*q.z+a.x*q.y-a.y*q.x;
  this.w=a.w*q.w-a.x*q.x-a.y*q.y-a.z*q.z;
  return this;
 }
}
let materialDisposals=0,geometryDisposals=0;
class Group{
 constructor(){this.children=[];this.userData={};this.position=new V();this.quaternion=new Q();
  this.scale={x:1,y:1,z:1,setScalar(n){this.x=this.y=this.z=n}};this.visible=true}
 add(o){this.children.push(o)}
 updateMatrixWorld(){}
 traverse(fn){fn(this);this.children.forEach(c=>c.traverse?c.traverse(fn):fn(c))}
}
class Geometry{dispose(){geometryDisposals++}}
class Material{constructor(o={}){Object.assign(this,o);this.opacity=o.opacity??1}dispose(){materialDisposals++}}
class Mesh extends Group{constructor(geometry,material){super();this.geometry=geometry;this.material=material}}
const state={game:true,overlay:false,now:1000,frame:0,positionCalls:0,
 nativeActionCalls:0,originalStickCalls:0,priorStart:0,priorCleanup:0};
const controller={
 position:new V(0,1,0),rotation:new Q(),
 updateMatrixWorld(){},
 getWorldPosition(out){return out.copy(this.position)},
 getWorldQuaternion(out){return out.copy(this.rotation)}
};
const right={controller,input:{handedness:'right',gamepad:{
 buttons:Array.from({length:6},()=>({pressed:false})),axes:[0,0,0,0]}},hit:false};
const ctx={
 console,Math,performance:{now:()=>state.now},
 THREE:{Vector3:V,Quaternion:Q,Mesh,PlaneGeometry:Geometry,RingGeometry:Geometry,
  MeshBasicMaterial:Material,DoubleSide:2,MathUtils:{clamp:(x,min,max)=>Math.max(min,Math.min(max,x))}},
 se195:{mode:'game',page:'main',visible:true,photo:false,radial:null,buttons:[]},
 se193XRGameActive:()=>state.game,se205OverlayActive:()=>state.overlay,
 se192InputRecord:side=>side==='right'?right:null,
 se192Pressed:(record,index)=>!!record?.input?.gamepad?.buttons[index]?.pressed,
 se192Stick:()=>{state.originalStickCalls++;return {x:.4,y:.2}},
 se195Text:label=>({text:label}),
 se195PositionRadial:force=>{
  if(force&&ctx.se195.radial){
   state.positionCalls++;ctx.se195.radial.position.set(0,1,-1);
   ctx.se195.radial.quaternion.copy(new Q());
  }
 },
 se195RadialHit:rec=>rec?.hit?{ui:'se195:buildPage',point:new V(),distance:1}:null,
 se195Options:(mode,page)=>{
  if(page==='more')return [['pause','PAUSE'],['restart','RESTART'],['stop','STOP'],['back','BACK']];
  return mode==='editor'?[['select','SELECT']]:[['buildPage','BUILD'],['more','SESSION']];
 },
 se195HandleAction:()=>{state.nativeActionCalls++;return true},
 se195MakeRadial:reposition=>{
  const old=ctx.se195.radial,root=new Group();
  root.name='Quest menu page '+ctx.se195.page;
  if(old&&!reposition){root.position.copy(old.position);root.quaternion.copy(old.quaternion)}
  ctx.se195.radial=root;ctx.se195.buttons=[];
  if(reposition)ctx.se195PositionRadial(true);
 },
 se195Page:page=>{ctx.se195.page=page;ctx.se195MakeRadial(false);ctx.se195.visible=true},
 se193XRFrame:()=>{state.frame++;return 'frame'},
 se193XRStart:()=>{state.priorStart++},
 se193XRCleanup:()=>{state.priorCleanup++},
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_sheep_world_pinned_panels_v11_207.js'),'utf8'),ctx);
const own=vm.runInContext('se207',ctx),diag=()=>ctx.window.SWYRL_ENGINE_SHEEP_VR_SPATIAL_207.diagnose();
const nearly=(a,b,label)=>assert.ok(Math.abs(a-b)<.00001,label+': '+a+' vs '+b);
ctx.se195MakeRadial(true);
const originalRoot=ctx.se195.radial;
assert.equal(diag().available,true);
assert.equal(diag().menuPagesDecorated,1);
assert.equal(originalRoot.children.length,2,'label and rim cached on menu root');
assert.equal(originalRoot.children[0].name,'§E native VR menu grip label');
assert.equal(originalRoot.children[1].name,'§E menu grab outline');
assert.equal(originalRoot.scale.x,.86,'preserve original compact menu size');
assert.equal(state.positionCalls,1);
ctx.se207Decorate();
assert.equal(originalRoot.children.length,2,'no duplicate GPU mesh after reuse');
assert.equal(diag().menuCacheReuses,1);
assert.equal(ctx.se195Options('game','more').at(-1)[0],'layoutPage');
assert.equal(ctx.se195Options('game','layout').length,5);
assert.equal(ctx.se195Options('editor','more').length,4,'editor menu options unchanged');
ctx.se195HandleAction('layoutPage',right);
assert.equal(ctx.se195.page,'layout');
assert.equal(ctx.se195.radial.children.length,2);
// Reset to fresh menu for grip tests.
ctx.se195Page('main');
let panel=ctx.se195.radial;
right.hit=false;right.input.gamepad.buttons[1].pressed=true;
state.now+=16;ctx.se193XRFrame();
assert.equal(diag().grabbing,false,'grip misses do not grab menus');
assert.equal(diag().gripMisses,1);
right.input.gamepad.buttons[1].pressed=false;
state.now+=16;ctx.se193XRFrame();
right.hit=true;right.input.gamepad.buttons[1].pressed=true;
state.now+=16;ctx.se193XRFrame();
assert.equal(diag().grabbing,true,'grip while aiming at menu starts grab');
assert.equal(diag().gripStarts,1);
assert.equal(diag().pinned,false);
assert.equal(panel.userData.se207GrabOutline.material.opacity,.7);
assert.equal(ctx.se192Stick(right).x,0,'no sheep camera orbit while gripping menu');
controller.position.set(2,1,1);
state.now+=50;ctx.se193XRFrame();
nearly(panel.position.x,2,'controller 6DoF horizontal translation');
nearly(panel.position.y,1,'maintain vertical relative offset');
nearly(panel.position.z,0,'controller depth translation');
const turn=Math.PI/4;controller.rotation=new Q(0,Math.sin(turn),0,Math.cos(turn));
state.now+=16;ctx.se193XRFrame();
nearly(panel.quaternion.y,Math.sin(turn),'controller tilt/orbit changes panel orientation');
nearly(panel.position.x,1,'controller rotation applies local menu offset');
assert.ok(diag().gripMoves>=2);
right.input.gamepad.axes[3]=-1;
state.now+=50;ctx.se193XRFrame();
assert.ok(diag().scale>1,'right thumbstick resizes held panel');
assert.equal(diag().resizes>=1,true);
right.input.gamepad.axes[3]=0;right.input.gamepad.buttons[1].pressed=false;
state.now+=16;ctx.se193XRFrame();
assert.equal(diag().grabbing,false);
assert.equal(diag().pinned,true,'grip release pins world panel');
assert.equal(diag().gripReleases,1);
assert.equal(panel.userData.se207GrabOutline.material.opacity,.07);
const pinned=panel.position.clone(),q=panel.quaternion.clone(),scale=panel.scale.x;
ctx.se195Page('capture');
panel=ctx.se195.radial;
nearly(panel.position.x,pinned.x,'page switch preserves pinned x');
nearly(panel.position.z,pinned.z,'page switch preserves pinned z');
nearly(panel.quaternion.y,q.y,'page switch preserves rotation');
nearly(panel.scale.x,scale,'page switch preserves chosen size');
const before=state.positionCalls;
ctx.se195PositionRadial(true);
assert.equal(state.positionCalls,before,'pinned world panel never re-centers itself');
ctx.se195HandleAction('layoutPage',right);
assert.equal(ctx.se195.page,'layout');
ctx.se195HandleAction('sizePlus',right);
assert.ok(diag().scale>1,'layout menu size actions work');
ctx.se195HandleAction('sizeMinus',right);
assert.ok(diag().scale<=1.08);
ctx.se195HandleAction('pin',right);
assert.equal(ctx.se195.page,'main');
assert.equal(diag().pinned,true);
ctx.se195HandleAction('unpin',right);
assert.equal(ctx.se195.page,'main');
assert.equal(diag().pinned,false,'Recenter clears pin');
assert.equal(diag().scale,1);
assert.ok(state.positionCalls>before);
nearly(ctx.se195.radial.position.z,-1,'Recenter restores safe UI front-of-head');
assert.ok(diag().recenters>=1);
// Quest system overlays cannot accidentally begin a pin gesture.
state.overlay=true;right.input.gamepad.buttons[1].pressed=true;
state.now+=16;ctx.se193XRFrame();
assert.equal(diag().grabbing,false);
assert.equal(diag().available,false);
state.overlay=false;right.input.gamepad.buttons[1].pressed=false;
state.now+=16;ctx.se193XRFrame();
const beforeEditor=state.positionCalls;
ctx.se195.mode='editor';state.game=false;
right.input.gamepad.buttons[1].pressed=true;state.now+=16;ctx.se193XRFrame();
assert.equal(diag().grabbing,false,'editor grip remains its own tool');
ctx.se195PositionRadial(true);assert.equal(state.positionCalls,beforeEditor+1);
ctx.se195.mode='game';state.game=true;
right.input.gamepad.buttons[1].pressed=false;state.now+=16;ctx.se193XRFrame();
ctx.se193XRStart();
assert.equal(state.priorStart,1);
assert.equal(diag().pinned,false,'new XR session never persists stale world anchor');
ctx.se193XRCleanup();
assert.equal(state.priorCleanup,1);
assert.equal(diag().scale,1);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_207_sheep_vr_world_pinned_panels.py'),'utf8');
assert.ok(patch.includes('V11_207_SHEEP_QUEST_SPATIAL_MENU'));
assert.ok(!patch.includes('stUi.rotation='),'no gameplay house rotations');
console.log(JSON.stringify({pass:true,checks:47,grips:diag().gripStarts,
 moves:diag().gripMoves,panelsDecorated:diag().menuPagesDecorated,
 resizes:diag().resizes,recenters:diag().recenters}));
