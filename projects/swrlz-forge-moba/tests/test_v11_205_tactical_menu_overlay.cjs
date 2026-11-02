// §E v11.205 — tactically-framed Sheep Tag Quest + crisp, modal pointer UX.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 clone(){return new V(this.x,this.y,this.z)}
 copy(a){return Object.assign(this,{x:a.x,y:a.y,z:a.z})}
 set(x,y,z){return Object.assign(this,{x,y,z})}
 add(a){this.x+=a.x;this.y+=a.y;this.z+=a.z;return this}
 addScaledVector(a,f){this.x+=a.x*f;this.y+=a.y*f;this.z+=a.z*f;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this}
 crossVectors(a,b){this.x=a.y*b.z-a.z*b.y;this.y=a.z*b.x-a.x*b.z;this.z=a.x*b.y-a.y*b.x;return this}
}
let removed=0;
class Obj{
 constructor(){this.children=[];this.userData={};this.position=new V();this.scale={x:1,y:1,z:1,setScalar(n){this.x=this.y=this.z=n}};
  this.rotation={z:0};this.visible=true;}
 add(o){this.children.push(o);o.parent=this}
 traverse(fn){fn(this);for(const o of this.children)o.traverse?o.traverse(fn):fn(o)}
}
class Geo{dispose(){removed++}setAttribute(){}}
class Material{
 constructor(o={}){Object.assign(this,o);this.color={setHex(n){this.value=n}};this.opacity=o.opacity??1}
 dispose(){removed++}
}
class Mesh extends Obj{constructor(geo,material){super();this.geometry=geo;this.material=material}}
class Points extends Mesh{}
let now=1000,frameCount=0,priorHit=0,priorActions=0,priorFog=0,priorTeamFog=0,priorCamera=0,
 priorInput=0,priorRay=0,priorCleanup=0,priorStart=0,priorMenus=0,flushed=0;
const scene={added:[],add(m){this.added.push(m)},remove(){}};
const left={index:0,input:{handedness:'left',gamepad:{buttons:Array.from({length:5},()=>({pressed:false}))}},
 se192:{beam:{visible:true,scale:{z:4},material:new Material()},dot:new Obj()}};
const right={index:1,input:{handedness:'right',gamepad:{buttons:Array.from({length:5},()=>({pressed:false})),hapticActuators:[{pulse:()=>{flushed++;}}]}},
 se192:{beam:{visible:true,scale:{z:4},material:new Material()},dot:new Obj()}};
for(const r of [left,right]){
 r.se192.dot.scale={setScalar(n){this.value=n}};
 r.se192.dot.children=[{renderOrder:10002},{renderOrder:10002}];
}
const ctx={
 console,Math,scene,performance:{now:()=>now},
 THREE:{Vector3:V,Group:Obj,Mesh,Points,RingGeometry:Geo,PlaneGeometry:Geo,
  BufferGeometry:Geo,BufferAttribute:class{constructor(a,n){this.a=a;this.n=n}},
  MeshBasicMaterial:Material,PointsMaterial:Material,DoubleSide:2,AdditiveBlending:3},
 renderer:{xr:{isPresenting:true}},
 se181XR:{session:{visibilityState:'visible'}},
 se200:{vertical:6.5,horizontal:21},se202:{vertical:6.5,rearBias:2.5},
 se203:{vertical:6.5},se193:{zoom:1.4},
 se195:{mode:'game',page:'main',visible:false,radial:null,buttons:[],lastAction:''},
 se195Active:()=>true,
 se195Options:()=>[['follow','FOLLOW'],['free','FREE'],['buildPage','BUILD'],['capturePage','CAPTURE'],['more','SESSION']],
 se195HandleAction:()=>{priorActions++;return true},
 se195MakeRadial:()=>{
  priorMenus++;
  const root=new Obj();root.name='old Quest wrist menu';
  ctx.se195.radial=root;
  ctx.se195.buttons=[0,1,2].map(i=>{
   const m=new Mesh(new Geo(),new Material({opacity:1}));
   m.position=new V(i*.25,-.1,.013);m.userData.se195Action=['follow','free','buildPage'][i];
   root.add(m);return m;
  });
  scene.add(root);
 },
 se195Page:p=>{ctx.se195.page=p;ctx.se195MakeRadial(false);ctx.se195.visible=true},
 se195RadialHit:record=>{
  priorHit++;
  if(!record?.menuPoint)return null;
  return {point:record.menuPoint.clone(),button:record.menuButton,
   distance:1.12,ui:'se195:'+(record.menuButton?.userData.se195Action||'block')};
 },
 se192InputRecord:side=>side==='right'?right:left,
 se192Ray:()=>({origin:new V(0,1,0),direction:new V(0,0,-1)}),
 se192RenderRay:(record)=>{
  priorRay++;record.se192.dot.position.set(0,0,-9);
  record.se192.dot.visible=true;
 },
 stSoftFogPaint:()=>{priorFog++},se156PaintTeamFog:()=>{priorTeamFog++},
 se195FollowCamera:()=>{priorCamera++},
 se204:{
  buttons:{left:{held:false,opened:false},right:{held:false,opened:false}},
  wheel:null
 },
 se204WheelHide:()=>{ctx.se204.wheel=null},
 se192Pressed:(rec,index)=>!!rec?.input?.gamepad?.buttons[index]?.pressed,
 se204InputFrame:()=>{priorInput++},
 se193XRFrame:()=>{frameCount++;ctx.se204InputFrame()},
 se193XRStart:()=>{priorStart++},se193XRCleanup:()=>{priorCleanup++},
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime','engine_xr_play_menu_camera_polish_v11_205.js'),'utf8'),ctx);
const state=()=>ctx.window.SWYRL_ENGINE_SHEEP_VR_POLISH_205.diagnose();
assert.equal(ctx.se200.vertical,18,'default is tactical, not shallow');
assert.equal(ctx.se202.vertical,18);
assert.equal(ctx.se203.vertical,18);
assert.equal(state().profile,'tactical');
assert.ok(state().tacticalAngle>35&&state().tacticalAngle<43);
assert.equal(ctx.se195Options('game','main').length,6,'VIEW added without removing gameplay controls');
assert.equal(ctx.se195Options('game','view')[0][0],'viewTactical');
assert.equal(ctx.se195Options('game','view')[1][0],'viewForward');
assert.equal(ctx.se195Options('editor','main').length,5,'editor options unchanged');
ctx.se195HandleAction('viewPage',right);
assert.equal(ctx.se195.page,'view');
ctx.se195HandleAction('viewForward',right);
assert.equal(ctx.se200.vertical,10);
assert.equal(state().profile,'forward');
assert.equal(ctx.se195.page,'main');
ctx.se195HandleAction('viewTactical',right);
assert.equal(ctx.se200.vertical,18);
assert.equal(ctx.se202.vertical,18);
ctx.se195HandleAction('more',right);
assert.equal(priorActions,1,'unknown actions delegate to native menu behavior');
// Cached radial root: polish one time per root, no repeated meshes on visits.
ctx.se195MakeRadial(true);
const root=ctx.se195.radial;
assert.equal(root.scale.x,.86,'compact menu');
assert.equal(state().menuPagesDecorated,4);
assert.equal(root.userData.se205Decor,true);
assert.equal(root.userData.se205Vfx.glints.geometry instanceof Geo,true);
assert.equal(root.userData.se205Vfx.backs.length,3);
const childCount=root.children.length;
ctx.se195MakeRadial(false);
assert.equal(ctx.se195.radial.children.length,childCount,'all visual elements allocated once per root');
assert.equal(root.children.length,childCount,'menu visuals remain on old root');
ctx.se195.visible=true;ctx.se195.radial.visible=true;
right.menuButton=ctx.se195.buttons[1];right.menuPoint=new V(.23,-.1,-1.1);
left.menuButton=null;left.menuPoint=new V(-.2,-.1,-1.15);
ctx.se192RenderRay(right,{ui:'se195:free'});
assert.equal(right.se192.dot.visible,true);
assert.ok(Math.abs(right.se192.dot.position.z+1.083)<.0001,
 'reticle is just in FRONT of actual hit, not 9m behind modal buttons');
assert.equal(right.se192.dot.children[0].renderOrder,10510);
assert.equal(right.se192.beam.scale.z,1.12);
assert.equal(right.se192.beam.material.color.value,0x9affdf,
 'hover focus visible and distinct from game world');
ctx.se192RenderRay(left,{ui:'se195:block'});
assert.equal(left.se192.beam.material.color.value,0x6ee7ff,
 'left controller keeps cyan when hitting backplate');
now+=100;ctx.se193XRFrame();
assert.equal(state().selectedMenuButton,'free');
assert.equal(ctx.se195.buttons[1].material.opacity,1,'hover brightens instead of dimming');
assert.ok(ctx.se195.buttons[1].scale.x>1.09);
assert.equal(ctx.se195.buttons[1].userData.se205Glow.material.opacity,.63);
assert.ok(flushed>=1,'optional haptic on focus transition');
const nEffects=state().menuParticleFrames;
now+=100;ctx.se193XRFrame();
assert.ok(state().menuParticleFrames>nEffects,'subtle cached animation without new geometry');
ctx.se195.visible=false;
ctx.se192RenderRay(left,{ground:true,distance:8});
assert.equal(left.se192.beam.material.color.value,0x6ee7ff);
assert.equal(left.se192.dot.children[0].renderOrder,10002,
 'menu reticle elevated only while the menu is open');
// Native Quest system overlay: keep camera rig and speculative inputs idle.
ctx.se181XR.session.visibilityState='visible-blurred';
ctx.se204.buttons.right.held=true;
ctx.se204.buttons.left.held=true;
ctx.se204.wheel={};
ctx.se204InputFrame();
assert.equal(ctx.se204.wheel,null);
assert.equal(ctx.se204.buttons.right.held,false);
assert.equal(ctx.se204.buttons.left.held,false);
const oldCamera=priorCamera;
ctx.se195FollowCamera(.016);
assert.equal(priorCamera,oldCamera,'no tracked-rig translation under OS overlay');
ctx.stSoftFogPaint({});
ctx.se156PaintTeamFog({});
assert.equal(priorFog,0);assert.equal(priorTeamFog,0);
now+=100;ctx.se193XRFrame();
assert.equal(state().overlayTransitions,1);
assert.ok(state().overlayInputSkipped>0);
assert.ok(state().overlayCameraSkipped>0);
assert.ok(state().overlayFogSkipped>=2);
ctx.se181XR.session.visibilityState='visible';
// A button held while overlay disappears should not become a new build.
right.input.gamepad.buttons[4].pressed=true;
ctx.se204InputFrame();
assert.equal(priorInput,2,'held OS overlay input suppressed after return');
right.input.gamepad.buttons[4].pressed=false;
ctx.se204InputFrame();
assert.equal(priorInput,3,'normal input resumes only after controller release');
ctx.se195FollowCamera(.016);
assert.equal(priorCamera,oldCamera+1);
ctx.stSoftFogPaint({});
ctx.se156PaintTeamFog({});
assert.equal(priorFog,1);assert.equal(priorTeamFog,1);
ctx.se193XRStart();
assert.equal(priorStart,1);
assert.equal(state().profile,'tactical');
ctx.se193XRCleanup();
assert.equal(priorCleanup,1);
const patch=fs.readFileSync(path.join(__dirname,'..','patches','v11_205_sheep_tactical_menu_pointer_overlay.py'),'utf8');
assert.ok(patch.includes("c.width=384;c.height=192"),'cached Quest text resolution raised');
assert.ok(patch.includes('g.scale(.75,.75)'), 'corresponding draw transform raised');
assert.ok(patch.includes('V11_205_SHEEP_TACTICAL_MENU_POINTER_OVERLAY'));
console.log(JSON.stringify({pass:true,checks:48,menuDecorated:state().menuPagesDecorated,
 hovered:state().menuHoverChanges,overlayFrames:state().overlayFrames,
 menuPointers:state().menuPointerFrames,particles:state().menuParticleFrames}));
