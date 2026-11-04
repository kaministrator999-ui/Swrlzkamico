// §E v11.271 — targeted browser/VR LAN visibility and auto-discovery tests.
// No network/GPU assertions: simulated callbacks verify routing into native LAN.
const fs=require('fs'),path=require('path'),vm=require('vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../runtime/sheep_lan_visibility_autofind_v11_271.js'),'utf8');
const nodes=new Map();
function node(tag,id=''){
 const n={tagName:tag,id,style:{},textContent:'',parentElement:null,
   classList:{contains:()=>false,add(){}},setAttribute(){},addEventListener(k,fn){this['_on'+k]=fn;},
   appendChild(child){child.parentElement=this;nodes.set(child.id,child);return child;},
   querySelector(sel){return nodes.get(sel.slice(1))||null;},
   after(child){nodes.set(child.id,child);},remove(){}};
 return n;
}
const start=node('button','st141StartGame');
const actual=node('div','runtimePanel');actual.querySelector=function(sel){
 if(sel==='#st141StartGame')return start;
 if(sel==='#se146LanOpen')return nodes.get('se146LanOpen')||null;
 return null;
};
const panel=node('div','previewPanel');
panel.querySelector=function(sel){if(sel==='#se271PreviewLan')return nodes.get('se271PreviewLan')||null;return null;};
const preview=node('section','st141MenuPreview');
preview.classList.contains=c=>c==='st141-preview';
preview.querySelector=sel=>sel==='.st141-menu-panel'?panel:null;
const overlay=node('section','st141RuntimeMenu');
overlay.querySelector=sel=>sel==='.st141-menu-panel'?actual:
 sel==='#se146LanOpen'?nodes.get('se146LanOpen'):null;
const heading=node('b'),refresh=node('button');
const listHead=node('div');listHead.after=child=>nodes.set(child.id,child);
const browser=node('div','se146LanScreen');
browser.querySelector=sel=>sel==='.se146-list-head b'?heading:
 sel==='#se146LanRefresh'?refresh:
 sel==='#se271LanHint'?nodes.get('se271LanHint'):
 sel==='.se146-list-head'?listHead:null;
const head=node('head');const doc={
 head,createElement(tag){
  const el=node(tag);
  if(tag==='canvas')el.getContext=()=>({
   fillStyle:'',strokeStyle:'',lineWidth:0,font:'',textAlign:'',textBaseline:'',
   fillRect(){},strokeRect(){},fillText(){}
  });
  return el;
 },
 getElementById(id){return nodes.get(id)||null;},
 querySelector(sel){return nodes.get(sel.slice(1))||null;}
};
let probeCount=0,openCount=0,installCount=0,pageCalls=0;
class Vec{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vec(this.x,this.y,this.z)}
 copy(v){this.x=v.x;this.y=v.y;this.z=v.z;return this}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}
 normalize(){const k=Math.sqrt(this.lengthSq())||1;this.x/=k;this.y/=k;this.z/=k;return this}
 crossVectors(a,b){this.set(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);return this}
 addScaledVector(v,k){this.x+=v.x*k;this.y+=v.y*k;this.z+=v.z*k;return this}
 add(v){return this.addScaledVector(v,1)}
}
class Group{constructor(){this.position=new Vec();}add(){}lookAt(){}updateMatrixWorld(){}}
class Geo{dispose(){}}
class Mat{dispose(){}}
class Tex{dispose(){}}
class Mesh{constructor(g,m){this.geometry=g;this.material=m}}
const seLevels={
 preview:null,playingMenu:false,overlay:null,
};
const ctx={
 window:{},document:doc,console,Promise,performance:{now:()=>4000},setTimeout,
 location:{protocol:'https:'},
 renderer:{xr:{isPresenting:false}},
 scene:{add(){},remove(){}},
 THREE:{Vector3:Vec,Group,PlaneGeometry:Geo,MeshBasicMaterial:Mat,CanvasTexture:Tex,Mesh,SRGBColorSpace:'srgb',DoubleSide:2,LinearFilter:1},
 seLevels,
 seLevelsOwns:()=>true,seLevelsCurrent:()=>({role:'menu'}),
 playing:false,simulating:false,stSession:null,
 seLevelsEnsureUI(){seLevels.preview=preview;},
 seLevelsPlayMenu(){seLevels.playingMenu=true;seLevels.overlay=overlay;ctx.se146Install(overlay);return true;},
 se146Install(){installCount++;nodes.set('se146LanOpen',node('button','se146LanOpen'));ctx.se146Lan.root=browser;},
 se146Open(){openCount++;ctx.se146Lan.active=true;return true;},
 se146Scan:async()=>true,
 se146Lan:{active:false,root:null},
 se159:{connected:true,rooms:new Map()},
 se159Start:()=>Promise.resolve(true),se159Probe(){probeCount++;},
 se159Draw(){},
 se193XRMenuActive:()=>true,
 se195:{mode:'menu',page:'main',visible:true},
 se195RadialHit:()=>null,se195HandleAction:()=>{pageCalls++;return true;},
 se191XRHeadPose:()=>({eye:new Vec(),forward:new Vec(0,0,-1)}),
 se193XRFrame:()=>undefined,se193XRCleanup:()=>undefined,
};
vm.runInNewContext(source,ctx,{filename:'sheep_lan_visibility_autofind_v11_271.js'});
assert.equal(ctx.seLevels.preview,null);
ctx.seLevelsEnsureUI();
assert.ok(nodes.get('se271PreviewLan'),'editor preview LAN launch button missing');
nodes.get('se271PreviewLan')._onclick({stopPropagation(){},preventDefault(){}});
assert.equal(openCount,1,'preview must actually launch runtime multiplayer browser');
assert.equal(heading.textContent,'AUTO-FIND OPEN GAMES');
assert.equal(nodes.get('se146LanOpen').textContent,'LOCAL LAN · FIND GAMES');
assert.ok(installCount>0);
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271.diagnose().runtimeOpen,true);
// New VR main-menu tile must be visible and hit-testable independently.
ctx.renderer.xr.isPresenting=true;ctx.se193XRFrame();
const status=ctx.window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271.diagnose();
assert.equal(status.vrTile,true,'controller-selectable LAN tile not created');
const hit=ctx.se195RadialHit({}, {ray:{intersectObject:()=>[{distance:.8,point:new Vec()}]}});
assert.equal(hit?.ui,'se195:lanPage');
ctx.se195HandleAction('lanPage',{});
assert.equal(pageCalls,1);
ctx.se195.page='lan';
ctx.se193XRFrame(); // should dispose tile away from main page
assert.equal(ctx.window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271.diagnose().vrTile,false);
Promise.resolve().then(()=>{
 assert.ok(probeCount>=1,'the multiplayer browser must probe existing live directory');
 console.log('QUEST_LAN_271_VISIBILITY_AUTOFIND_OK',
  {preview:true,button:true,vrTile:true,probeCount,openCount,pageCalls});
}).catch(e=>{console.error(e);process.exitCode=1;});
