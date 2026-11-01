// §E v11.192: focused native spatial editor contracts without Chromium.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const raw=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_spatial_editor_v11_192.js'),'utf8');
new vm.Script(raw,{filename:'engine_xr_spatial_editor_v11_192.js'});
class Vec{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 clone(){return new Vec(this.x,this.y,this.z)}
 copy(v){return this.set(v.x,v.y,v.z)}
 addScaledVector(v,n){this.x+=v.x*n;this.y+=v.y*n;this.z+=v.z*n;return this}
 add(v){return this.addScaledVector(v,1)}
 sub(v){return this.addScaledVector(v,-1)}
 multiplyScalar(s){this.x*=s;this.y*=s;this.z*=s;return this}
 divideScalar(s){return this.multiplyScalar(1/s)}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 length(){return Math.sqrt(this.lengthSq())}
 normalize(){return this.divideScalar(this.length()||1)}
 distanceTo(v){return this.clone().sub(v).length()}
 crossVectors(a,b){return this.set(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x)}
 negate(){return this.multiplyScalar(-1)}
 setFromMatrixPosition(){return this}
 transformDirection(){return this}
 toArray(){return [this.x,this.y,this.z]}
 fromArray(a){return this.set(...a)}
}
class Obj {
 constructor(){this.children=[];this.visible=true;this.position=new Vec();this.scale=new Vec(1,1,1);this.rotation={y:0};this.quaternion={setFromUnitVectors(){}};this.userData={};this.matrixWorld={};this.isObject3D=true}
 add(x){this.children.push(x);x.parent=this}
 remove(x){this.children=this.children.filter(a=>a!==x)}
 updateMatrixWorld(){}
 getWorldPosition(v){return v.copy(this.position)}
 worldToLocal(v){return v}
 lookAt(){}
 traverse(fn){fn(this);for(const c of this.children.slice())c.traverse?.(fn)}
}
class Geo{dispose(){}setAttribute(k,v){this[k]=v;return this}setIndex(v){this.index=v;return this}computeVertexNormals(){}}
class Mat{constructor(o){this.map=o?.map;this.color={setHex(){}}}dispose(){}}
class Mesh extends Obj{constructor(g,m){super();this.geometry=g;this.material=m}}
class Raycaster{constructor(origin,dir){this.ray={origin,direction:dir,intersectPlane:(_,target)=>target.set(0,0,-2)}}intersectObject(){return []}intersectObjects(){return []}}
const scene=new Obj(),parent=new Obj(),label=new Obj();
label.name='WorkspaceStationLabel';label.isSprite=true;label.material={map:{id:1}};label.scale.set(2,.5,1);parent.add(label);scene.add(parent);
const controllers=[0,1].map(index=>({
 index,controller:new Obj(),ray:{visible:true},input:{handedness:index?'right':'left',gamepad:{axes:[0,0,0,0],buttons:[{},{}]}}
}));
const ref={getOffsetReferenceSpace(transform){return {transform}}};
const xr={isPresenting:true,getReferenceSpace:()=>ref,setReferenceSpace(v){this.last=v}};
const written={};let begin=0,committed=0,selectedCount=0;
const ctx={console,
 localStorage:{getItem:k=>written[k]||null,setItem:(k,v)=>written[k]=v},
 scene,actors:[],se181XR:{controllers,session:{id:1},exitSurface:null,selectedCount:0},
 se191XRHeadPose:()=>({eye:new Vec(0,1.6,0),forward:new Vec(0,0,-1)}),
 se191XRRayHit:r=>({ground:true,distance:2,point:new Vec(0,0,-2)}),
 se181XRExit(){},rootGroupFor:x=>x,
 currentProject:{},renderer:{xr},perspectiveCamera:new Obj(),
 playing:false,simulating:false,selected:null,
 window:{},document:{getElementById(){return null},createElement(){return {getContext(){return {fillRect(){},strokeRect(){},fillText(){},set fillStyle(v){},set strokeStyle(v){},set lineWidth(v){},set textAlign(v){},set textBaseline(v){},set font(v){}}}}}},
 performance:{now:()=>1000},XRRigidTransform:class{constructor(position,orientation){this.position=position;this.orientation=orientation}},
 THREE:{Group:Obj,Mesh,BufferGeometry:Geo,Float32BufferAttribute:class{constructor(arr,dim){this.arr=arr;this.dim=dim}},
  MeshBasicMaterial:Mat,PlaneGeometry:Geo,RingGeometry:Geo,CanvasTexture:Mat,
  Vector3:Vec,Plane:class{constructor(normal,d){this.normal=normal;this.d=d}},Raycaster,
  DoubleSide:2,SRGBColorSpace:'srgb',MathUtils:{clamp:(x,a,b)=>Math.max(a,Math.min(b,x)),degToRad:x=>x*Math.PI/180}},
 beginTransaction(){begin++},commitTransaction(){committed++},
 selectActor(x){ctx.selected=x;selectedCount++},rebuildHierarchy(){},syncInspector(){},refreshDebug(){},
 createPrefab(){},XREvent:null
};
vm.createContext(ctx);vm.runInContext(raw,ctx);
const evals=source=>vm.runInContext(source,ctx);
assert.deepEqual(Array.from(evals("Object.keys(window.SWYRL_ENGINE_VR_EDITOR.diagnose())")).includes('controllerHands'),true);
const positions=Array.from(evals("se192TaperGeometry().position.arr"));
assert.equal(positions.length,4*10*3,'tapered beam should have four radius rings');
assert(Math.hypot(positions[0],positions[1])<.001,'beam starts in a tiny point');
assert(Math.hypot(positions[30],positions[31])>.004,'beam thickens at middle');
assert(Math.hypot(positions.at(-3),positions.at(-2))<.001,'beam tapers at far end');
evals("se192PrepareRay(se181XR.controllers[0]);se192PrepareRay(se181XR.controllers[1]);");
assert.equal(controllers[0].ray.visible,false);
assert.equal(controllers[1].ray.visible,false);
assert.equal(evals("se192.beams.length"),2);
const hit=evals("se192Raycast(se181XR.controllers[0])");
assert(hit.point&&hit.distance>0,'the visible ray must produce a hit point');
evals("se192RenderRay(se181XR.controllers[0],se192Raycast(se181XR.controllers[0]))");
assert.equal(evals("se192.cursors.length"),2);
evals("se192FreezeBillboards()");
assert.equal(label.visible,false,'camera-facing label hidden in XR');
assert.equal(evals("se192.sprites.length"),1);
assert.equal(parent.children.length,2,'fixed mesh replaces moving sprite');
evals("se192RestoreBillboards()");
assert.equal(label.visible,true);
assert.equal(parent.children.length,1,'fixed mesh removed on exit');
evals("se192MoveBy(1,0,-2)");
assert.equal(xr.last.transform.position.x,-1);
assert.equal(xr.last.transform.position.z,2);
evals("se192SnapTurn(.2)");
assert(Number.isFinite(xr.last.transform.orientation.w),'snap turn must be finite');
controllers[0].input.gamepad.axes=[0,0,.5,-.75];
evals("se192MoveFrame(.05)");
assert(evals("se192.inputSamples")>0,'locomotion must update from thumbstick');
evals("se192AimRead()");
evals("se192XRGamepadButton(se181XR.controllers[0],'x')");
assert.equal(evals("se192.panelVisible"),false);
evals("se192Action('aimRight',se181XR.controllers[0])");
assert(JSON.parse(written['swyrl.xr.aim.v1'])[0]>.005,'aim trim must be saved');
const actor=new Obj();actor.name='Editor test actor';actor.userData={actorType:'rock',id:'a1'};
scene.add(actor);ctx.actors.push(actor);ctx.selected=actor;
controllers[1].input.gamepad.buttons[1]={pressed:true,value:1};
evals("se192PrepareRay(se181XR.controllers[1]);se192GrabFrame(se181XR.controllers[1]);");
assert.equal(begin,1,'native drag transaction begins once');
evals("se192GrabFrame(se181XR.controllers[1])");
controllers[1].input.gamepad.buttons[1]={pressed:false,value:0};
evals("se192GrabFrame(se181XR.controllers[1])");
assert.equal(committed,1,'native drag commits once');
console.log('SE192_NATIVE_VR_EDITOR_UNIT_PASS');
