#!/usr/bin/env node
// §E v11.450: preserve actual inspection pose during dock reflow, ensure
// Inset native previews have visible transient edges and Face tap can arm
// a preview without any implicit model commit.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(process.argv[2],'utf8');
const marker='SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW';
assert(html.includes(marker),'v11.451 release marker absent');
const segment=(a,b)=>{
 const begin=html.indexOf(a),end=html.indexOf(b,begin);
 assert(begin>=0&&end>begin,'Missing runtime segment '+a);
 return html.slice(begin,end+b.length);
};
const dock=segment('/* SE450_MODEL_DOCK_RESIZE_START */','/* SE450_MODEL_DOCK_RESIZE_END */');
const pose=segment('/* SE450_CAMERA_RESIZE_GUARD_START */','/* SE450_CAMERA_RESIZE_GUARD_END */');
let globalResizes=0;
const dockCtx=vm.createContext({window:{dispatchEvent:()=>globalResizes++},Event:class{}});
vm.runInContext(dock+'\nthis.notify=se450NotifyDockResized;',dockCtx);
dockCtx.notify('model');dockCtx.notify('model');
assert.equal(globalResizes,0,'Dock drag must never synthesize global resize events');
dockCtx.notify('materials');assert.equal(globalResizes,1,'Other editor resize still notifies existing listeners');
const grip=html.slice(html.indexOf('function dragResize(node,what,side,dir){'),html.indexOf('function addSeparator(parent,what,side,dir){'));
assert.equal((grip.match(/se450NotifyDockResized\(what\)/g)||[]).length,3,
 'Pointermove, pointerup and keyboard resize must use safe notifier');
assert(!grip.includes("window.dispatchEvent(new Event('resize'))"));

class V{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new V(this.x,this.y,this.z);}
 copy(v){Object.assign(this,v);return this;}
 equals(v){return this.x===v.x&&this.y===v.y&&this.z===v.z;}
}
const orbit={yaw:.31,pitch:-.22,distance:2.4},pan=new V(.4,.5,.6),detail=new V(1,2,3);
let camUpdates=0,refreshes=0,resizes=0;
const camera={aspect:1.8},ctx=vm.createContext({
 orbit,camera,atelierCameraPan:pan,atelierDetailTarget:detail,
 resize:()=>{resizes++;camera.aspect=1.3;orbit.distance=24;orbit.yaw=2;orbit.pitch=.7;pan.x=99;ctx.atelierDetailTarget=new V(6,7,8);},
 cameraUpdate:()=>camUpdates++,refresh:()=>refreshes++
});
vm.runInContext(pose+'\nthis.safeResize=resize;',ctx);
ctx.safeResize();
assert.equal(resizes,1);
assert.equal(camera.aspect,1.3,'Viewport projection aspect must still follow dock width');
assert.equal(orbit.distance,2.4,'Zoom distance must survive a sidebar drag');
assert.equal(orbit.yaw,.31);assert.equal(orbit.pitch,-.22);
assert(pan.equals(new V(.4,.5,.6)),'Pan must survive');
assert(ctx.atelierDetailTarget.equals(new V(1,2,3)),'Framing target must survive');
assert.equal(camUpdates,1);assert.equal(refreshes,1);
ctx.safeResize();
assert.equal(resizes,2,'Native sizing happens on each requested refresh');
assert.equal(orbit.distance,2.4,'Repeated resize still preserves zoom');
assert.equal(camera.aspect,1.3,'Repeated resize continues applying aspect updates');

const visible=segment('/* SE450_FACE_PREVIEW_VISIBILITY_START */','/* SE450_FACE_PREVIEW_VISIBILITY_END */');
let edgesDisposed=0,materialsDisposed=0,linesAdded=0;
class Edges{constructor(geo){this.from=geo;}dispose(){edgesDisposed++;}}
class Mat{dispose(){materialsDisposed++;}}
class Lines{constructor(geo,material){this.geometry=geo;this.material=material;this.userData={};} }
const mesh={children:[],add(o){o.parent=this;this.children.push(o);},remove(o){this.children=this.children.filter(x=>x!==o);o.parent=null;}};
const surface={getIndex:()=>({count:36}),getAttribute:()=>({count:8})};
const testCtx=vm.createContext({THREE:{EdgesGeometry:Edges,LineBasicMaterial:Mat,LineSegments:Lines}});
vm.runInContext(visible+'\nthis.add=se450PreviewOutlineAdd;this.clear=se450PreviewOutlineClear;',testCtx);
const record={mesh,geometry:surface};
testCtx.add(record);
assert.equal(mesh.children.length,1,'Native Inset preview edges must be visible');
assert.equal(mesh.children[0].renderOrder,180);
assert.equal(mesh.children[0].userData.se450Transient,true,'Preview overlay is never document data');
testCtx.clear(record);
assert.equal(mesh.children.length,0,'Cancel/Apply removes preview edges');
assert.equal(edgesDisposed,1);assert.equal(materialsDisposed,1,'Overlay GPU resources released');
testCtx.clear(record);assert.equal(edgesDisposed,1,'No double-dispose');

const armed=segment('/* SE450_ARMED_FACE_PREVIEW_START */','/* SE450_ARMED_FACE_PREVIEW_END */');
let state={selection:{partId:'cube',mode:'face',faceIds:[2,3]},preview:{active:false},
 operations:{inset:{available:true},extrude:{available:true}},convert:{available:false}};
const calls=[],queued=[],statusMsgs=[];
const api={inspect:()=>state,preview:(op,amount)=>{
 calls.push({op,amount});state.preview={active:true};return {ok:true,changed:false};
 }};
const armCtx=vm.createContext({
 se430BeginnerAPI:()=>api,
 se430BeginnerQueue:()=>calls.push({refresh:true}),
 document:{getElementById:()=>({value:'.2'})},
 queueMicrotask:fn=>queued.push(fn),
 status:(message)=>statusMsgs.push(message),window:{confirm:()=>true}
});
vm.runInContext(armed+'\nthis.arm=se450ArmFacePreview;this.pick=se450AfterPlanarFaceTap;',armCtx);
armCtx.arm('inset','cube');
const selected=armCtx.pick({ok:true,faceIds:[2,3]},2,'cube');
assert.equal(selected.ok,true);
assert.equal(calls.length,0,'No preview should execute before face-pick microtask');
for(const job of queued.splice(0))job();
assert.equal(calls.length,2);assert.equal(calls[0].op,'inset');
assert.equal(calls[0].amount.amount,.2);
assert.equal(calls.some(c=>'apply' in c),false,'Preview never commits model history');
assert.match(statusMsgs[0],/preview visible/i);
armCtx.pick({ok:true},2,'cube');assert.equal(queued.length,0,'Armed operation clears after preview');
assert(html.includes('se450ArmFacePreview(operation,partId);'),'No-face toolbar action must arm');
assert(html.includes('se450AfterPlanarFaceTap(se430ModelWorkshop.selectRegion'),'Native connected-face selection must trigger armed operation');
assert(html.includes('record.geometry=geometry;mesh.geometry=geometry;active=record;\n  se450PreviewOutlineAdd(record);'));
assert(html.includes('function restore(record){\n  se450PreviewOutlineClear(record);'),'Apply/Cancel must clean line overlay');
assert(html.includes('const priorRender=renderParts;'),'Native preview invalidation logic retained');
assert(html.includes("native.querySelector('#modelAtelierWorkshopApply').addEventListener('click'"),'Only native Apply commits');
console.log('SE450_CAMERA_INSET_PREVIEW_PASS: camera pose/zoom survives resize, native Inset is visible and armed, geometry stays uncommitted');
