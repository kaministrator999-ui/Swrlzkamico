'use strict';
/* §E v11.490 — verify native skinned render fallback and project-specific workspace. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'../runtime/model_atelier_rig_workspace_v11_490.js'),'utf8');
let bound=0,made=0,restored=0;
const store=new Map(),part={id:'sorting-hat-one-sculpt'},data={parts:[part]};
const rig={schema:'swyrl-cloth-skin-v1',targetPartId:part.id,activeClip:'idle',duration:2,
 clips:{idle:{duration:2,timeline:[{time:0,pose:{}},{time:2,pose:{}}]}}};
const copy=()=>({copy(){}});
const raw={isMesh:true,isSkinnedMesh:false,userData:{atelierId:part.id},name:'hat',
 position:copy(),rotation:copy(),scale:copy(),visible:true,castShadow:false,receiveShadow:false,
 geometry:{dispose(){}},material:{dispose(){}}};
const root={children:[raw],remove(x){this.children.splice(this.children.indexOf(x),1)},
 add(x){this.children.push(x)}};
const panel={hidden:false,dataset:{se251RightCollapsed:'false'},
 querySelector:()=>null,contains:()=>false};
const ctx={window:{addEventListener:()=>{},SWYRL_ENGINE_STARTUP_CAMERA_476:{restore:()=>{restored++;return true}},
 SWYRL_E_UNIFIED_TOOLS:{current:()=>({category:'Sculpt',mode:'Vertex'}),select:()=>{}}},
 localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)},
 model:()=>data,currentProject:{instanceId:'hat-saved-id'},
 modelRoot:root,panel,selection:part.id,partById:id=>id===part.id?part:null,select:()=>{},
 se220RigAvailable:()=>true,se220Rig:()=>rig,se220Time:0,se220Playing:false,
 se220R:()=>null,se489SelectClip:()=>{},se220RigPose:()=>{},se220RigRefresh:()=>{},
 se220RigInterpolate:()=>({}),se220RigBind:()=>{bound++},
 se220RigMesh:()=>({isSkinnedMesh:true,userData:{},position:copy(),rotation:copy(),scale:copy()}),
 renderParts:()=>{},open:()=>true,close:()=>true,cameraUpdate:()=>{},
 se430ModelCamera:{inspect:()=>({ready:true,position:[1,3,6],target:[0,2,0],
 projection:'perspective',view:'orbit'}),setView:()=>{}},
 document:{addEventListener:()=>{}},requestAnimationFrame:()=>{},setTimeout:()=>0,
 clearTimeout:()=>{},status:()=>{},structuredClone,console};
vm.createContext(ctx);vm.runInContext(src,ctx);
const api=ctx.window.SWYRL_ENGINE_MODEL_WORKSPACE_490;
ctx.renderParts();
assert.equal(root.children[0].isSkinnedMesh,true,'rigged cloth must have GPU skin');
assert.equal(bound,1,'rebind skeleton after correcting plain Mesh');
assert.equal(api.persist(),true);
assert.ok(store.has('swrlz.engine.modeler.workspace.v2:hat-saved-id'));
assert.equal(data.editorWorkspace.selectedPart,part.id);
assert.equal(api.restore(),true);assert.equal(restored,1);
console.log('SE490_MODEL_RIG_WORKSPACE_PASS');
