// Mock XR browser contract: no headset required; physical tracking tested on Quest.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/immersive_xr_gateway_v11_181.js'),'utf8');
class V3{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z}
 setFromMatrixPosition(){return this}
 transformDirection(){return this}
 lengthSq(){return 1}
 normalize(){return this}
 crossVectors(){return this}
 copy(){return this}
 addScaledVector(){return this}
 add(){return this}
}
class Node{
 constructor(){this.children=[];this.listeners={};this.position=new V3();this.material={dispose(){},color:{setHex(){}}};this.geometry={dispose(){}};this.scale={z:1};this.matrixWorld={};this.visible=true;this.isObject3D=true;this.userData={}}
 add(n){this.children.push(n);n.parent=this}
 remove(n){this.children=this.children.filter(x=>x!==n)}
 addEventListener(k,fn){(this.listeners[k]??=[]).push(fn)}
 removeEventListener(k,fn){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==fn)}
 updateMatrixWorld(){}
 getWorldPosition(out){out.y=1.6;return out}
 getWorldDirection(out){out.z=-1;return out}
 lookAt(){}
}
class BufferGeometry{setFromPoints(){return this}dispose(){}}
class Material{constructor(){this.color={setHex(){}}}dispose(){}}
class Texture{dispose(){}}
class Raycaster{intersectObject(){return []}intersectObjects(){return []}}
const canvas={getContext:()=>({fillRect(){},strokeRect(){},fillText(){},set fillStyle(_){},set strokeStyle(_){},set lineWidth(_){},set textAlign(_){},set font(_){} })};
const dom={id:'native-canvas'},scene=new Node(),helper={visible:true},orbit={enabled:true};
const perspectiveCamera=new Node(),originalCamera=new Node();
let requested=0,attached=0,selected=0,sessions=[],resized=0;
const xr={
 enabled:false,isPresenting:false,
 setReferenceSpaceType(value){assert.equal(value,'local-floor')},
 async setSession(s){attached++;this.isPresenting=true;this.current=s},
 getController(){return new Node()},
 getCamera(){return new Node()}
};
const renderer={xr,domElement:dom};
const navigator={xr:{
 async isSessionSupported(kind){assert.equal(kind,'immersive-vr');return true},
 requestSession(kind,opts){
  requested++;assert.equal(kind,'immersive-vr');assert.deepEqual(Array.from(opts.requiredFeatures),['local-floor']);
  const s={listeners:{},
   addEventListener(k,fn){(this.listeners[k]??=[]).push(fn)},
   async end(){xr.isPresenting=false;for(const fn of this.listeners.end||[])fn()}
  };sessions.push(s);return Promise.resolve(s);
 }
}};
const tools=[],modelPanel={hidden:true};
const bar={append(...nodes){tools.push(...nodes)}},buttons={};
const document={
 readyState:'loading',addEventListener(){},
 querySelector(sel){return sel==='.topbar'?bar:null},
 getElementById(id){return id==='modelAtelierPanel'?modelPanel:null},
 createElement(tag){if(tag==='canvas')return canvas;return {
  type:'',disabled:false,attributes:{},listeners:{},dataset:{},
  setAttribute(k,v){this.attributes[k]=v},
  addEventListener(k,fn){this.listeners[k]=fn}
 }}
};
const context={
 navigator,document,window:{addEventListener(){},SWYRL_VR_CONTROLS:{attachSession(s){assert(s)}}},
 console,THREE:{Vector3:V3,BufferGeometry,LineBasicMaterial:Material,Line:Node,
  CanvasTexture:Texture,Mesh:Node,PlaneGeometry:BufferGeometry,MeshBasicMaterial:Material,
  Raycaster,DoubleSide:2,SRGBColorSpace:'srgb'},
 renderer,scene,actors:[],orbit,transform:{getHelper:()=>helper},
 perspectiveCamera,camera:originalCamera,playing:false,simulating:false,
 $:id=>id==='viewport'?dom:null,resize(){resized++},
 rootGroupFor:o=>o,selectActor(){selected++},
 getComputedStyle:()=>({display:'block'}),
};
vm.createContext(context);vm.runInContext(source,context,{timeout:2000});
async function flush(){for(let i=0;i<8;i++)await Promise.resolve()}
(async()=>{
 const api=context.window.SWYRL_ENGINE_XR;
 assert(api,'status API exposed');
 assert.equal(api.read().mode,'browser-2d');
 assert.equal(requested,0,'no VR requested on page load');
 context.se181XRMount();
 await flush();
 assert.equal(requested,0,'capability checking never requests a session');
 assert.equal(api.read().supported,true);
 assert.equal(tools[0].id,'se181EnterVR');
 modelPanel.hidden=false;
 tools[0].listeners.click();
 await flush();
 assert.equal(requested,0,'do not open wrong scene while Model Atelier active');
 modelPanel.hidden=true;
 tools[0].listeners.click();
 assert.equal(requested,1,'session request called directly from user click');
 await flush();
 assert.equal(attached,1,'bound to existing renderer');
 assert.equal(api.read().mode,'immersive-vr');
 assert.equal(context.camera,perspectiveCamera);
 assert.equal(orbit.enabled,false);
 assert.equal(helper.visible,false);
 assert.equal(api.read().controllerRays,2);
 assert.equal(selected,0,'entry does not mutate scene');
 assert.equal(scene.children.length,3,'two controller rays and exit sign in native scene');
 await api.exit();
 await flush();
 assert.equal(api.read().mode,'browser-2d');
 assert.equal(api.read().active,false);
 assert.equal(api.read().controllerRays,0);
 assert.equal(scene.children.length,0,'XR objects detached');
 assert.equal(context.camera,originalCamera,'main editor camera restored');
 assert.equal(orbit.enabled,true);
 assert.equal(helper.visible,true);
 assert.equal(resized,1);
 tools[0].listeners.click();
 await flush();
 assert.equal(requested,2,'re-enter after exit');
 await sessions[1].end();
 await flush();
 assert.equal(api.read().active,false,'Quest/system exit restores browser');
 console.log('XR_BROWSER_SESSION_LIFECYCLE_PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
