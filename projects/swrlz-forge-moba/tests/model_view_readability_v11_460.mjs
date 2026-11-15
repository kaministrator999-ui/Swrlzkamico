#!/usr/bin/env node
// v11.455: source-safe model display modes, visible cap and camera preservation.
import fs from 'node:fs';import assert from 'node:assert/strict';import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
for(const required of [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_460_NATIVE_VIEW_MENU',
 "window.SWRLZ_FORGE_BUILD={version:'v11.460'",
 "const atelierViewModes=['shaded','solid','wireframe','overlay','xray','flat','clay'];",
 "let atelierViewGlobal='solid',atelierViewOverrides=new Map();",
 'new THREE.MeshStandardMaterial({','transparent:false,opacity:1,depthTest:true,depthWrite:true,',
 'new THREE.EdgesGeometry(mesh.geometry,18)',
 'new THREE.LineSegments(geometry,material)',
 'window.se455PreviewTintAdd?.(record)',
 'window.se455PreviewTintClear?.(record)',
 'SE455_VIEW_READABILITY_CSS_START',
 'SE455_NATIVE_SURFACE_SHADING_START'
])assert(html.includes(required),'Missing model readability integration: '+required);
const start='/* SE455_VIEW_READABILITY_START */',end='/* SE455_VIEW_READABILITY_END */';
const a=html.indexOf(start),b=html.indexOf(end,a);
assert(a>=0&&b>a);
const script=html.slice(a,b+end.length);
new vm.Script(script,{filename:'model_view_readability_v11_455.js'});
const sources={preview:true},runs={rebuild:0,material:0,refresh:0};
const mesh={isMesh:true,userData:{atelierId:'cube'},children:[],material:{userData:{}},remove(x){
 this.children.splice(this.children.indexOf(x),1);
}};
const calls=[],bridge={inspect:()=>({mode:calls.at(-1)||'solid',camera:'orbit'}),setMode:x=>(calls.push(x),true),setCamera:x=>(calls.push('camera:'+x),true)};
const context=vm.createContext({
 se430BeginnerInstall:()=>{},
 se430BeginnerAPI:()=>({inspect:()=>({preview:{active:sources.preview}})}),
 atelierViewGlobal:'solid',atelierViewOverrides:new Map(),
 atelierCameraInterior:false,
 atelierViewRebuild:()=>runs.rebuild++,
 atelierViewModeApply:()=>{runs.material++;},
 renderPreview:()=>runs.refresh++,
 modelRoot:{children:[mesh]},partById:()=>({id:'cube',kind:'topologyMesh'}),
 se430ModelCamera:{inspect:()=>({view:'orbit'}),setView:()=>true},
 window:{SWYRL_ENGINE_MODEL_VIEW:bridge},status:()=>{}
});
vm.runInContext(script,context);
assert.equal(context.window.SWYRL_ENGINE_VIEW_READABILITY_455.version,'v11.455');
// This is the early/pre-install context. UI display changes must delegate
// through a native mounted selector; never touch the private renderer here.
assert.equal(context.window.SWYRL_ENGINE_VIEW_READABILITY_455.choose('overlay'),true);
assert.equal(calls.at(-1),'overlay','Quick-menu click delegates to native bridge');
assert.equal(runs.rebuild,0,'No parallel scene rebuild in outer quick menu');
assert.equal(runs.material,0,'Private renderer not accessed in outer quick menu');
sources.preview=false;
assert.equal(context.window.SWYRL_ENGINE_VIEW_READABILITY_455.choose('wireframe'),true);
assert.equal(calls.at(-1),'wireframe');
assert.equal(context.window.SWYRL_ENGINE_VIEW_READABILITY_455.choose('wrong'),false);
assert(script.includes("window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode"),
 'Current mode is read from the native bridge');
const a2=html.indexOf('/* SE455_TRANSIENT_FACE_HIGHLIGHT_START */'),b2=html.indexOf('/* SE455_TRANSIENT_FACE_HIGHLIGHT_END */',a2);
assert(a2>=0&&b2>a2);
const script2=html.slice(a2,b2+'/* SE455_TRANSIENT_FACE_HIGHLIGHT_END */'.length);
new vm.Script(script2,{filename:'model_view_tint_v11_455.js'});
let freed=0;
class Geometry{setAttribute(k,v){this[k]=v;}computeVertexNormals(){}dispose(){freed++;}}
class Material{constructor(properties){this.properties=properties;}dispose(){freed++;}}
class Mesh{constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};}}
const sourceMesh={children:[],add(child){this.children.push(child);child.parent=this;},
 remove(child){this.children.splice(this.children.indexOf(child),1);child.parent=null;}};
const sandbox=vm.createContext({window:{},THREE:{BufferGeometry:Geometry,Float32BufferAttribute:class{constructor(data,grain){this.data=data;this.grain=grain;}},MeshBasicMaterial:Material,Mesh,DoubleSide:2}});
vm.runInContext(script2,sandbox);
const preview={operation:'inset',selectedFaces:[0,1],data:{indices:[0,1,2,0,2,3],positions:[-1,1,-1,1,1,-1,1,1,1,-1,1,1]},mesh:sourceMesh};
sandbox.window.se455PreviewTintAdd(preview);
assert.equal(sourceMesh.children.length,1,'Visible inner cap during Inset');
assert.equal(sourceMesh.children[0].material.properties.opacity,.14);
assert.equal(sourceMesh.children[0].material.properties.depthWrite,false);
sandbox.window.se455PreviewTintClear(preview);
assert.equal(sourceMesh.children.length,0);
assert.equal(freed,2,'No GPU resource leaks after Cancel or Apply');
sandbox.window.se455PreviewTintClear(preview);
assert.equal(freed,2,'Idempotent cleanup');
console.log('SE455_VIEW_READABILITY_PASS: opaque modes, angle-filtered edges, active-preview-safe mode selection, reusable cap tint and disposal');
