// §E v11.191: focused WebXR arrival diagnostics contract, no Chromium install.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_black_screen_recovery_v11_191.js'),'utf8');
new vm.Script(code,{filename:'xr-recovery-v11.191.js'});
class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this}
 addScaledVector(v,s){this.x+=v.x*s;this.y+=v.y*s;this.z+=v.z*s;return this}
 add(v){this.x+=v.x;this.y+=v.y;this.z+=v.z;return this}
 clone(){return new V(this.x,this.y,this.z)}
 crossVectors(a,b){this.x=a.y*b.z-a.z*b.y;this.y=a.z*b.x-a.x*b.z;this.z=a.x*b.y-a.y*b.x;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const len=Math.sqrt(this.lengthSq())||1;this.x/=len;this.y/=len;this.z/=len;return this}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
}
class Disposable{dispose(){this.disposed=true}}
class CanvasTexture extends Disposable{constructor(canvas){super();this.canvas=canvas}}
class PlaneGeometry extends Disposable{constructor(w,h){super();this.w=w;this.h=h}}
class Material extends Disposable{constructor(props){super();this.props=props}}
class Mesh{
 constructor(geometry,material){this.geometry=geometry;this.material=material;this.position=new V();this.visible=true}
 lookAt(target){this.target=target}
}
class XRTransform{constructor(position){this.position=position}}
const ref={getOffsetReferenceSpace(transform){this.lastTransform=transform;return {kind:'offset',transform}}};
const xr={isPresenting:true,refSpace:null,
 getReferenceSpace:()=>ref,setReferenceSpace(space){this.refSpace=space},
 setFramebufferScaleFactor(scale){this.framebufferScale=scale},
 getCamera(){return {
  updateMatrixWorld(){},
  getWorldPosition(v){return v.set(0,1.6,14.1)},
  getWorldDirection(v){return v.set(0,0,-1)}
 }}};
const context={console,
 currentProject:{environment:'dragon-den',teleportZones:[{id:'arrival',position:[2,.12,13.5]}]},
 scene:{nodes:[],add(v){this.nodes.push(v)},remove(v){this.nodes=this.nodes.filter(x=>x!==v)}},
 renderer:{xr},perspectiveCamera:{},XRRigidTransform:XRTransform,
 THREE:{Vector3:V,CanvasTexture,PlaneGeometry,MeshBasicMaterial:Material,Mesh,DoubleSide:2,SRGBColorSpace:'srgb'},
 document:{createElement(tag){assert.equal(tag,'canvas');return {width:0,height:0,
  getContext(){return {clearRect(){},fillRect(){},strokeRect(){},fillText(){},
   set fillStyle(v){},set strokeStyle(v){},set lineWidth(v){},set textAlign(v){},set font(v){}}}
 }}},
 se181XR:{session:{id:1},controllers:[],exitPanel:new Mesh(new PlaneGeometry(.69,.24),new Material({})),viewerAnchored:false},
 se181XRNote(){},se181XRRaycast(){return {distance:4}},
 se181XRExit(){context.exits++},exits:0,
 performance:{now(){return context.clock}},clock:1500,
 setTimeout(fn){context.watchdogFn=fn;return 123},clearTimeout(id){context.clearId=id},
 window:{}
};
context.se181XR.exitPanel.visible=false;
vm.createContext(context);vm.runInContext(code,context);
function run(js){return vm.runInContext(js,context)}
assert.equal(run('se191XRZone().source'),'project arrival zone');
assert.equal(run('se191XRInstallLanding()'),true);
assert.equal(xr.refSpace.kind,'offset');
assert.deepEqual({...ref.lastTransform.position},{x:-2,y:-.12,z:-13.5});
context.currentProject={environment:'dragon-den',teleportZones:[]};
assert.deepEqual(Array.from(run('se191XRZone().position')),[0,.02,14.1]);
context.currentProject={environment:'other-game',teleportZones:[]};
assert.deepEqual(Array.from(run('se191XRZone().position')),[0,0,0]);
run('se191XRPrepareFramebuffer()');
assert.equal(xr.framebufferScale,.8);
run('se191XRMakeBeacon()');
assert.equal(context.scene.nodes.length,1);
assert.equal(run('!!se191XR.beacon'),true);
run('se191XRStartWatchdog(se181XR.session)');
run('se191XRRenderFrame()');
assert.equal(run('se191XR.frames'),1);
assert.equal(run('se191XR.beacon.visible'),true);
assert.equal(context.se181XR.exitPanel.visible,true);
context.watchdogFn();
assert.equal(context.exits,0,'watchdog must not exit when XR frames arrived');
context.clock=15000;run('se191XRRenderFrame()');
assert.equal(run('se191XR.beacon.visible'),false,'intro fades when headset renders');
context.clock=20000;run('se191XRStartWatchdog(se181XR.session)');
context.watchdogFn();
assert.equal(context.exits,1,'no headset frames must return to the editor');
run('se191XRCleanup()');
assert.equal(context.scene.nodes.length,0);
assert.equal(run('se191XR.beacon'),null);
assert.equal(run('se191XR.referenceSpaceOffset'),false);
const controller={index:0};context.controller=controller;
context.rayCalls=0;context.se181XRRaycast=()=>{context.rayCalls++;return {distance:3}};
context.clock=100;
run('se191XRRayHit(controller)');
context.clock=150;run('se191XRRayHit(controller)');
assert.equal(context.rayCalls,1,'controller ray must be cached for 95ms');
context.clock=200;run('se191XRRayHit(controller)');
assert.equal(context.rayCalls,2);
console.log('SE191_XR_ARRIVAL_DIAGNOSTICS_PASS');
