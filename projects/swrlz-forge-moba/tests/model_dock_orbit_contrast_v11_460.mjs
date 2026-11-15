#!/usr/bin/env node
// §E v11.458: verify screenshot regressions, not just styling strings.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const js=fs.readFileSync(new URL('../runtime/model_viewport_stability_v11_458.js',import.meta.url),'utf8');
const css=fs.readFileSync(new URL('../runtime/model_viewport_stability_v11_458.css',import.meta.url),'utf8');
new vm.Script(js,{filename:'model_viewport_stability_v11_458.js'});
assert(css.includes('--se320-right:0px!important'),'Hidden inspector must release its grid track');
assert(css.includes('--se320-left:34px!important'),'Collapsed hierarchy must release its grid track');
assert(css.includes('width:28px!important'),'Touch splitters need a usable drag target');
assert(!js.includes('setInterval(')&&!js.includes('renderParts('),'Do not add an independent render loop or rebuild during preview');
assert(!js.includes('checkpoint(')&&!js.includes('se430ModelCamera.frame('),'No hidden Undo or framing reset');
let disposed=0,frames=0,cameraMoves=0;
class Vector3 {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 length(){return Math.hypot(this.x,this.y,this.z);}
 distanceTo(b){return Math.hypot(this.x-b.x,this.y-b.y,this.z-b.z);}
}
class Box3 {
 setFromObject(mesh){this.mesh=mesh;return this;}
 isEmpty(){return false;}
 getCenter(out){return out.set(...this.mesh.center);}
 getSize(out){return out.set(...this.mesh.size);}
}
class EdgesGeometry {constructor(source){this.source=source;}dispose(){disposed++;}}
class LineBasicMaterial {constructor(settings){this.settings=settings;}dispose(){disposed++;}}
class LineSegments {constructor(geometry,material){this.geometry=geometry;this.material=material;this.userData={};}}
const mesh={isMesh:true,userData:{atelierId:'cube'},center:[0,1,0],size:[1,1,1],
 geometry:{index:{count:36}},children:[],
 material:{userData:{atelierViewportClone:true}},
 add(x){x.parent=this;this.children.push(x);},
 remove(x){this.children=this.children.filter(y=>x!==y);x.parent=null;}};
const part={id:'cube'},root={children:[mesh],updateWorldMatrix(){}};
const events={};
const orbit={yaw:.62,pitch:.23,distance:2.15},before={...orbit};
let worldTarget=null;
const sandbox=vm.createContext({
 THREE:{Vector3,Box3,EdgesGeometry,LineBasicMaterial,LineSegments},
 modelRoot:root,selection:'cube',atelierCameraInterior:false,orbit,
 atelierDetailTarget:null,atelierCameraPan:{x:0,y:0,z:0,set(x,y,z){this.x=x;this.y=y;this.z=z;}},
 atelierViewModeFor:()=> 'solid',
 atelierViewModeApply:()=>mesh,
 partById:id=>id==='cube'?part:null,
 se430ModelCamera:{inspect:()=>({target:worldTarget||[0,2.35,0]})},
 cameraUpdate:()=>{cameraMoves++;},
 window:{addEventListener:(type,handler)=>{events[type]=handler;}},
 queueMicrotask:f=>f(),requestAnimationFrame:f=>{frames++;f();}
});
vm.runInContext(js,sandbox);
assert.equal(typeof sandbox.window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458.refresh,'function');
sandbox.atelierViewModeApply(mesh,part);
assert.equal(mesh.children.length,1,'Selected solid mesh gets exactly one edge overlay');
assert.equal(mesh.children[0].material.settings.color,0x18354e,'Dark contrast against pale cube');
assert.equal(mesh.children[0].material.settings.depthTest,true,'Rear edges remain occluded');
const existing=mesh.children[0];
sandbox.window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458.refresh();
assert.equal(mesh.children[0],existing,'No per-frame edge allocations for unchanged geometry');
mesh.geometry={index:{count:48}};
sandbox.window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458.refresh();
assert.notEqual(mesh.children[0],existing,'Inset/extrude geometry produces current outline');
assert.equal(disposed,2,'Outdated edge geometry and material are disposed');
events['swrlz:model-workshop-change']({detail:{message:'Applied extrude to native geometry.',selection:{partId:'cube',mode:'face'},preview:{active:false}}});
assert.equal(cameraMoves,1,'Detached orbit pivot reanchors after a completed geometry commit');
assert.equal(sandbox.atelierDetailTarget.y,1);
assert.equal(sandbox.atelierCameraPan.y,0);
assert.deepEqual(orbit,before,'Orbit yaw pitch zoom remain exactly unchanged');
worldTarget=[0,1,0];
events['swrlz:model-workshop-change']({detail:{message:'Applied inset to native geometry.',selection:{partId:'cube',mode:'face'},preview:{active:false}}});
assert.equal(cameraMoves,1,'Already correct orbit target must not be snapped repeatedly');
sandbox.selection='other';
sandbox.window.SWYRL_ENGINE_MODEL_VIEW_STABILITY_458.refresh();
assert.equal(mesh.children.length,0,'Unselected mesh contour is removed');
assert.equal(disposed,4);
if(process.argv[2]){
 const html=fs.readFileSync(process.argv[2],'utf8');
 for(const value of ['SWYRL_ENGINE_DEPLOY_MARKER: V11_460_NATIVE_VIEW_MENU',
  "window.SWRLZ_FORGE_BUILD={version:'v11.460'",
  'SE458_MODEL_VIEWPORT_STABILITY_START',
  'SE458_DOCK_AND_MODEL_CONTRAST_START',
  "if(d.rightCollapsed){d.left=Math.max(145,Math.min(d.left,budget));return;}",
  "const other=side==='left'",
  'node.setPointerCapture?.(e.pointerId)',
  'V11_457_CONVERSION_NO_FACE_GATE',
  'SE454_INSET_TOP_STEPS_START'])assert(html.includes(value),'Integrated engine lacks '+value);
}
console.log('SE458_DOCK_ORBIT_CONTRAST_PASS: collapsing inspector releases width, touch grip accessible, cached dark edges dispose, post-edit orbit pivot corrected without zoom/rotation reset');
