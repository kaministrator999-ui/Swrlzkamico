#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const js=fs.readFileSync(new URL('../runtime/model_wire_clarity_v11_462.js',import.meta.url),'utf8');
new vm.Script(js);
let disposed=0,rebuilt=0;
const color=()=>({value:0,setHex(v){this.value=v;}});
class Mat{
 constructor(args={}){Object.assign(this,args);this.userData={};this.color=color();}
 clone(){const m=new Mat(this);m.userData={...this.userData};return m;}
 dispose(){disposed++;}
}
class Edges{
 constructor(geo,angle){this.geo=geo;this.angle=angle;}
 clone(){return new Edges(this.geo,this.angle);}
 dispose(){disposed++;}
}
class Triangles extends Edges{}
class Lines{constructor(geo,mat){this.geometry=geo;this.material=mat;this.userData={};}}
const authored=new Mat({flatShading:false});
const mesh={isMesh:true,geometry:{getIndex:()=>({count:36}),getAttribute:()=>({count:24})},
 userData:{atelierId:'cube',se455OriginalMaterial:authored},material:authored,children:[],
 add(c){this.children.push(c);c.parent=this;},remove(c){this.children.splice(this.children.indexOf(c),1);c.parent=null;}};
let mode='wireframe',preview=false;
const window={addEventListener(){}};
const ctx=vm.createContext({THREE:{MeshBasicMaterial:Mat,LineBasicMaterial:Mat,
 EdgesGeometry:Edges,WireframeGeometry:Triangles,LineSegments:Lines,DoubleSide:2},
 window,modelRoot:{children:[mesh]},selection:null,
 se461LowPolyEditable:()=>true,atelierViewModeFor:()=>mode,
 atelierViewModeApply:()=>mesh,atelierViewRebuild:()=>rebuilt++,
 se430BeginnerAPI:()=>({inspect:()=>({preview:{active:preview}})}),
 se430BeginnerInstall:()=>{},partById:()=>({id:'cube',kind:'topologyMesh'}),
 queueMicrotask:fn=>fn(),status:()=>{},Object});
vm.runInContext(js,ctx);
const api=window.SWYRL_ENGINE_WIRES_462;assert(api);
assert.equal(api.inspect().triangles,false);
ctx.atelierViewModeApply(mesh,{id:'cube',kind:'topologyMesh'});
assert(mesh.material.userData.se462DepthOnly);
assert(mesh.children.some(x=>x.geometry instanceof Edges&&!(x.geometry instanceof Triangles)));
assert(!mesh.children.some(x=>x.geometry instanceof Triangles));
assert(mesh.children.find(x=>x.userData.se462Primary).material.depthTest);
assert.equal(api.setOption('triangles',true),true);
assert.equal(rebuilt,1);
ctx.atelierViewModeApply(mesh,{id:'cube',kind:'topologyMesh'});
assert(mesh.children.some(x=>x.geometry instanceof Triangles));
assert(disposed>0);
assert.equal(api.setOption('hidden',true),true);
ctx.atelierViewModeApply(mesh,{id:'cube',kind:'topologyMesh'});
assert(mesh.children.some(x=>x.name==='Hidden wire guide'&&x.material.opacity<.3));
ctx.selection='cube';api.refresh();
assert.equal(mesh.children.find(x=>x.userData.se462Primary).material.color.value,0x63ffe1);
mode='shaded';mesh.material=authored;
ctx.atelierViewModeApply(mesh,{id:'cube',kind:'topologyMesh'});
assert.equal(mesh.material.flatShading,true);
assert.equal(authored.flatShading,false);
preview=true;assert.equal(api.setOption('triangles',false),false);
assert.equal(api.inspect().triangles,true);
if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const s of ["window.SWRLZ_FORGE_BUILD={version:'v11.462'",
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE',
 'SE462_MODEL_WIRE_CLARITY_START','SE462_VIEW_AND_DOCK_STYLES_START',
 'SE461_HARD_SURFACE_ORBIT_START','SE460_NATIVE_VIEW_COMMANDS_START',
 'Math.max(240,Math.min(330,Math.round(width*.35)))'])
 assert(html.includes(s),'Missing integrated '+s);
}
console.log('SE462_WIRES_PASS: filter, triangles, hidden edges, contrast, authored material and active preview');
