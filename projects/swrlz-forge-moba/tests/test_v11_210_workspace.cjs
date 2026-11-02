// §E v11.210 · independent Quest gameplay panels, native cooldowns,
// button profiles, browser-local panel restore and modal/controller priority.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 set(x,y,z){Object.assign(this,{x,y,z});return this}
 clone(){return new V(this.x,this.y,this.z)}
 copy(v){return this.set(v.x,v.y,v.z)}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this}
 addScaledVector(v,t){this.x+=v.x*t;this.y+=v.y*t;this.z+=v.z*t;return this}
 dot(v){return this.x*v.x+this.y*v.y+this.z*v.z}
 lengthSq(){return this.dot(this)}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this}
 crossVectors(a,b){this.x=a.y*b.z-a.z*b.y;this.y=a.z*b.x-a.x*b.z;this.z=a.x*b.y-a.y*b.x;return this}
 applyQuaternion(q){return this}
}
class Q{
 constructor(x=0,y=0,z=0,w=1){Object.assign(this,{x,y,z,w})}
 copy(o){Object.assign(this,{x:o.x,y:o.y,z:o.z,w:o.w});return this}
 clone(){return new Q(this.x,this.y,this.z,this.w)}
 invert(){this.x=-this.x;this.y=-this.y;this.z=-this.z;return this}
 multiply(){return this}
 setFromRotationMatrix(){return this}
}
class M{lookAt(){return this}}
let disposedTex=0,disposedGeo=0,disposedMat=0,createdTex=0,draws=0,menuSelects=0,originalRaycast=0,oldSelect=0,oldRender=0,oldFrame=0,oldCleanup=0,oldStart=0,oldHaptic=0,oldSkill=0,oldOptions=0,oldActions=0;
class Geo{dispose(){disposedGeo++}}
class Mat{constructor(o){Object.assign(this,o)}dispose(){disposedMat++}}
class Tex{constructor(c){this.canvas=c;this.disposed=false;this.needsUpdate=false;createdTex++}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;disposedTex++}}
class Group{
 constructor(){this.children=[];this.position=new V();this.quaternion=new Q();this.userData={};this.visible=true;
 this.scale={x:1,y:1,z:1,setScalar(n){this.x=this.y=this.z=n}}}
 add(o){this.children.push(o)}
 traverse(fn){fn(this);for(const c of this.children)c.traverse?c.traverse(fn):fn(c)}
 updateMatrixWorld(){}
}
class Mesh extends Group{constructor(g,m){super();this.geometry=g;this.material=m;this.renderOrder=0}}
const canvasContext={
 createLinearGradient:()=>({addColorStop(){}}),clearRect(){},fillRect(){},
 strokeRect(){},fillText(){draws++},
};
const memory=new Map();
const localStorage={
 getItem:key=>memory.get(key)||null,
 setItem:(key,value)=>{memory.set(key,value)}
};
const scene={children:[],add(o){this.children.push(o)},remove(o){this.children=this.children.filter(x=>x!==o)}};
let now=2000,poseEye=new V(0,1.6,0),hitKind=null,uv={x:.5,y:.5};
const session={controlledId:'one',role:'sheep',elapsed:10,archive:{},selectedId:'hut1',
 rules:{split:true,totems:true,splitUnlock:2,buildSnap:.15,totemLimit:'cooldown'},
 resources:{one:125},units:[{id:'one',kind:'sheep',name:'Kami Sheep',archiveLevel:3}],
 buildings:[{id:'hut1',kind:'st-farm',owner:'one'}]};
let native={splitCooldownRemaining:7.6,splitUnlocked:true,totemCooldownRemaining:4.3,
 canTotem:false,totemUsed:false,density:5};
const record={input:{handedness:'right',gamepad:{buttons:
 Array.from({length:6},()=>({pressed:false})),axes:[0,0,0,0]}},
 controller:{
  position:new V(),quaternion:new Q(),updateMatrixWorld(){},
  getWorldPosition(out){return out.copy(this.position)},
  getWorldQuaternion(out){return out.copy(this.quaternion)}
 },
 se192:{dot:{position:new V(),visible:false,children:[{renderOrder:0}]},
 beam:{scale:{z:1}}}};
const left={input:{handedness:'left',gamepad:{buttons:Array.from({length:6},()=>({pressed:false}))}}};
let game=true,menu=false,overlay=false,photo=false;
const workspace={
 console,Math,scene,localStorage,performance:{now:()=>now},
 THREE:{Vector3:V,Quaternion:Q,Matrix4:M,Group,Mesh,PlaneGeometry:Geo,
  MeshBasicMaterial:Mat,CanvasTexture:Tex,DoubleSide:2,SRGBColorSpace:'srgb',
  LinearFilter:'linear',MathUtils:{clamp:(x,a,b)=>Math.max(a,Math.min(b,x))}},
 document:{createElement:k=>{
  assert.equal(k,'canvas');return {width:0,height:0,getContext:()=>canvasContext}}},
 se193XRGameActive:()=>game,se195Active:()=>game,
 se205OverlayActive:()=>overlay,
 se191XRHeadPose:()=>({eye:poseEye.clone(),forward:new V(0,0,-1)}),
 se195:{mode:'game',page:'main',visible:false,photo:false},
 se195Options:()=>{oldOptions++;return [['more','SESSION'],['back','BACK']]},
 se195HandleAction:()=>{oldActions++;return true},
 se195SetVisible:v=>{workspace.se195.visible=v},
 se195Page:p=>{workspace.se195.page=p;workspace.se195.visible=true},
 se192InputRecord:side=>side==='right'?record:left,
 se192Pressed:(r,index)=>!!r?.input?.gamepad?.buttons?.[index]?.pressed,
 se192Ray:r=>({
  origin:new V(0,1,0),direction:new V(0,0,-1),
  ray:{intersectObject:obj=>obj.userData.se210Panel===hitKind?
    [{object:obj,distance:1.5,point:new V(.3,1,-1),uv}]:[]}
 }),
 se192Raycast:()=>{originalRaycast++;return {ground:true,distance:3}},
 se192Select:()=>{oldSelect++},
 se192RenderRay:()=>{oldRender++},
 se192Stick:()=>({x:.4,y:.2}),
 se193XRFrame:()=>{oldFrame++},
 se193XRStart:()=>{oldStart++},
 se193XRCleanup:()=>{oldCleanup++},
 se204:{holdMs:340,building:'st-farm',skill:'split',wheel:null,wheels:new Map()},
 se204WheelDispose:()=>{workspace.se204.wheels.clear();workspace.se204.wheel=null;},
 se195Text:label=>({label}),
 se204Haptic:()=>{oldHaptic++},
 se209OptionStatus:()=>{oldSkill++;return 'OLD'},
 se209RefreshWheel:()=>{menuSelects++},
 stSession:session,stUi:{buildingId:'hut1'},
 stArchiveStatus:()=>native,
 se205:{profile:'tactical'},
 se205ApplyCamera:p=>{workspace.se205.profile=p;return true},
 se210World:{mode:'balanced'},
 se210Quality:p=>{workspace.se210World.mode=p;return true},
 window:{SWYRL_ENGINE_QUEST_PERFORMANCE_210:{diagnose:()=>({
  fps:67,avgFrameMs:14.93,rendererDrawCalls:52,triangles:8390,
  gpuTextureCount:8,gpuGeometryCount:49,fogUpdateCpuMs:12.6,
  fogSampleCalls:8,cosmeticQuality:workspace.se210World.mode,autoReduced:false})}}
};
vm.createContext(workspace);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'sheep_xr_workspace_controls_v11_210.js'),'utf8'),workspace);
const inner=vm.runInContext('se210UI',workspace);
const stat=()=>workspace.window.SWYRL_ENGINE_QUEST_WORKSPACE_210.diagnose();
const fn=n=>vm.runInContext(n,workspace);
const nearly=(a,b)=>assert.ok(Math.abs(a-b)<.000001,a+' != '+b);
assert.equal(stat().bindingProfile,'classic');
assert.equal(stat().holdMs,340);
assert.equal(workspace.se204.holdMs,340);
assert.equal(stat().realMirrorCooldown.label,'8s RECHARGE');
assert.equal(stat().realTotemCooldown.label,'5s RECHARGE');
assert.equal(workspace.se209OptionStatus({type:'skill'},{id:'split'}),'8s RECHARGE');
assert.equal(workspace.se209OptionStatus({type:'skill'},{id:'totem'}),'5s RECHARGE');
native.splitCooldownRemaining=0;native.totemCooldownRemaining=0;
assert.equal(stat().realMirrorCooldown.label,'READY');
assert.equal(stat().realTotemCooldown.label,'NEED OWN 9-HOUSE CLUSTER');
native.canTotem=true;assert.equal(stat().realTotemCooldown.label,'READY');
native.totemUsed=true;session.rules.totemLimit='once';
assert.equal(stat().realTotemCooldown.label,'USED THIS MATCH');
session.rules.totemLimit='cooldown';native.totemUsed=false;
assert.equal(workspace.se209OptionStatus({type:'build'},{id:'st-farm'}),'OLD');
assert.equal(oldSkill,1,'existing build price authority unchanged');
// Native cooldown labels paint the SAME 384x192 texture as seconds elapse.
const cooldownArt={};
const current=fn('se210WheelStatusTexture')({type:'skill'},cooldownArt,'8s RECHARGE');
assert.ok(current?.canvas);
assert.equal(stat().cooldownTextureCreates,1);
assert.equal(stat().cooldownTextureUpdates,1);
const nextTick=fn('se210WheelStatusTexture')({type:'skill'},cooldownArt,'7s RECHARGE');
assert.strictEqual(nextTick,current,'reuses the existing cooldown texture');
assert.equal(stat().cooldownTextureCreates,1);
assert.equal(stat().cooldownTextureUpdates,2);
const repeated=fn('se210WheelStatusTexture')({type:'skill'},cooldownArt,'7s RECHARGE');
assert.strictEqual(repeated,current);
assert.equal(stat().cooldownTextureUpdates,2,'same second has no new GPU upload');
workspace.se204.wheels.set('skill',{root:{userData:{se209Decor:cooldownArt}}});
workspace.se204WheelDispose();
assert.equal(stat().cooldownTextureDisposals,1);
assert.equal(current.disposed,true);
session.archive=null;
assert.equal(stat().realMirrorCooldown.label,'STATE UNAVAILABLE',
 'never fabricate cooldown/readiness if native archive is missing');
session.archive={};
const options=workspace.se195Options('game','more');
assert.equal(options.at(-1)[0],'workspacePage');
assert.equal(workspace.se195Options('game','workspace').length,7);
assert.equal(workspace.se195Options('game','bindings').length,6);
assert.equal(workspace.se195Options('editor','main').length,2,'editor untouched');
workspace.se195HandleAction('workspacePage',record);
assert.equal(workspace.se195.page,'workspace');
workspace.se195HandleAction('workspaceCamera',record);
assert.equal(workspace.se195.visible,false);
assert.equal(scene.children.length,1);
assert.equal(stat().panels.length,1);
assert.equal(stat().panels[0].name,'camera');
assert.equal(stat().panelBuilds,1);
workspace.se195HandleAction('workspaceBuild',record);
workspace.se195HandleAction('workspaceSkills',record);
workspace.se195HandleAction('workspaceMetrics',record);
workspace.se195HandleAction('workspaceControls',record);
assert.equal(stat().panels.length,5,'five independent panel roots coexist');
assert.equal(scene.children.length,5);
assert.equal(createdTex,6,'five panel textures plus one reusable native cooldown texture');
assert.ok(draws>24,'panels contain useful metrics and control text');
const oldBuilds=stat().panelBuilds;
workspace.se195HandleAction('workspaceCamera',record);
assert.equal(stat().panelBuilds,oldBuilds,'reopening panel reuses assets');
const camera=inner.panels.get('camera'),controls=inner.panels.get('controls');
assert.equal(camera.root.children.length,2);
assert.equal(camera.mesh.userData.se210Panel,'camera');
assert.equal(camera.placed,true);
assert.equal(camera.root.visible,true);
hitKind='camera';
assert.equal(workspace.se192Raycast(record).ui,'se210:camera',
 'game raycast stops at panel instead of sheep world');
workspace.se192Select(record);
assert.equal(oldSelect,0,'world select blocked behind panel');
assert.equal(workspace.se205.profile,'forward','panel center action toggles camera view');
assert.equal(stat().panelSelections,1);
workspace.se192RenderRay(record,{ground:true});
assert.equal(record.se192.dot.visible,true);
assert.equal(record.se192.dot.children[0].renderOrder,10900);
assert.ok(record.se192.beam.scale.z===1.5,'beam terminates at panel');
uv={x:.10,y:.95};
workspace.se192Select(record);
assert.equal(camera.follow,true,'panel follow toggle in top left');
poseEye=new V(3,1.6,0);
now+=18;workspace.se193XRFrame();
assert.ok(camera.root.position.x>2,'head-follow panel updates every XR frame');
uv={x:.91,y:.11};workspace.se192Select(record);
assert.ok(camera.scale>1,'panel has resize button');
uv={x:.91,y:.93};workspace.se192Select(record);
assert.equal(camera.root.visible,false,'close only selected independent panel');
assert.equal(scene.children.length,5);
assert.equal(controls.root.visible,true,'unrelated pane remains open');
const stored=JSON.parse(memory.get(inner.prefKey));
assert.equal(stored.layout.camera.open,false);
assert.equal(stored.layout.controls.open,true);
hitKind='controls';uv={x:.5,y:.5};
const beforeProfile=stat().bindingProfile;
workspace.se192Select(record);
assert.equal(beforeProfile,'classic');
assert.equal(stat().bindingProfile,'sticks');
assert.equal(stat().holdMs,280);
assert.equal(workspace.se204.holdMs,280);
record.input.gamepad.buttons[3].pressed=true;
assert.equal(fn('se210Held')(record,'right'),true);
record.input.gamepad.buttons[3].pressed=false;
record.input.gamepad.buttons[4].pressed=true;
assert.equal(fn('se210Held')(record,'right'),false,'stick profile ignores A');
record.input.gamepad.buttons[4].pressed=false;
workspace.se195HandleAction('bindHybrid',record);
assert.equal(stat().bindingProfile,'hybrid');
assert.equal(stat().holdMs,450);
record.input.gamepad.buttons[4].pressed=true;
left.input.gamepad.buttons[3].pressed=true;
assert.equal(fn('se210Held')(record,'right'),true);
assert.equal(fn('se210Held')(left,'left'),true);
record.input.gamepad.buttons[4].pressed=false;left.input.gamepad.buttons[3].pressed=false;
workspace.se195HandleAction('bindClassic',record);
assert.equal(stat().bindingProfile,'classic');
workspace.se204Haptic(record);
assert.equal(oldHaptic,1);
workspace.se195HandleAction('toggleHaptic',record);
workspace.se204Haptic(record);
assert.equal(oldHaptic,1,'haptic switch works');
workspace.se195HandleAction('holdSpeed',record);
assert.equal(stat().holdMs,450,'hold duration cycle');
workspace.se195HandleAction('workspaceMetrics',record);
hitKind='metrics';uv={x:.5,y:.5};
workspace.se192Select(record);
assert.equal(workspace.se210World.mode,'performance',
 'camera panel does not own cosmetic quality, metrics panel does');
const oldPaint=stat().panelPaints;
now+=1000;workspace.se193XRFrame();
assert.ok(stat().panelPaints>oldPaint,'stats data updated at about 1Hz');
const oldWrites=stat().storageWrites;
record.input.gamepad.buttons[1].pressed=true;
hitKind='skills';uv={x:.5,y:.5};
now+=17;workspace.se193XRFrame();
assert.equal(!!inner.grabbing,true,'grip on independent panel begins 6DoF grab');
const skill=inner.panels.get('skills'),xBefore=skill.root.position.x;
record.controller.position.set(1,1,0);
now+=17;workspace.se193XRFrame();
assert.ok(skill.root.position.x>xBefore,'controller translation changes panel world position');
assert.equal(workspace.se192Stick(record).x,0,'camera orbit inhibited during panel grab');
record.input.gamepad.buttons[1].pressed=false;
now+=17;workspace.se193XRFrame();
assert.equal(inner.grabbing,null,'release pins panel');
assert.ok(stat().storageWrites>oldWrites,'pin persisted head-relative');
const saved=JSON.parse(memory.get(inner.prefKey));
assert.ok(saved.layout.skills.offset.every(v=>Math.abs(v)<3));
const beforeDispose=stat().panelDisposals;
assert.equal(workspace.se193XRCleanup(),undefined);
assert.equal(oldCleanup,1);
assert.equal(scene.children.length,0);
assert.equal(stat().panelDisposals,beforeDispose+5);
assert.equal(disposedTex,6,'five spatial panel textures and the earlier cooldown texture disposed');
assert.equal(disposedGeo,10);
assert.equal(disposedMat,10);
assert.equal(stat().panels.length,0);
workspace.se193XRStart();
assert.equal(oldStart,1);
assert.ok(inner.panels.has('controls'),'saved visible panels restored on new XR session');
assert.ok(inner.panels.has('skills'));
assert.equal(inner.panels.has('camera'),false,'closed panel stays closed');
assert.ok(stat().storedLayoutCount>=5);
assert.equal(stat().editorControlsUntouched,true);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_210_quest_comprehensive_polish.py'),'utf8');
assert.ok(patch.includes("const pressed=se210Held(record,side);"));
assert.ok(patch.includes("!se210PanelHit(se192InputRecord('right'))"));
console.log(JSON.stringify({pass:true,checks:81,panels:stat().panelBuilds,
 repaints:stat().panelPaints,storageWrites:stat().storageWrites,
 controls:stat().bindingProfile,disposeCount:disposedTex}));
