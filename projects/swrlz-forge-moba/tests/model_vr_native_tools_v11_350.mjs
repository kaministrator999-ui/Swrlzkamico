#!/usr/bin/env node
// Native bridge contracts with real Three math; no browser/XR mocks are shipped.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_native_tools_v11_350.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const bridgeSource=fs.readFileSync(path.join(ROOT,'runtime/model_vr_bridge_v11_344.js'),'utf8');
const toolsSource=fs.readFileSync(path.join(ROOT,'runtime/model_vr_native_tools_v11_350.js'),'utf8');
const workspaceSource=fs.readFileSync(path.join(ROOT,'runtime/model_vr_workspace_v11_340.js'),'utf8');
const clone=value=>JSON.parse(JSON.stringify(value));
function fixture(rebuildOnSelect=false,geometryOffset=[0,0,0],skinned=false){
 const world=new THREE.Scene(),root=new THREE.Group(),stage=new THREE.Group();
 world.add(new THREE.Group(),root,new THREE.Group());root.position.set(.7,1.2,-.4);root.rotation.set(.1,.2,.3);root.scale.set(1.1,.9,1.2);
 const initial=[{id:'part-a',name:'Native part A',position:[1,2,3],rotation:[.2,-.1,.3],scale:[1,1,1],color:'#8e63ce',radius:.4},
  {id:'part-b',name:'Native part B',position:[-1,0,0],rotation:[0,0,0],scale:[.8,.9,1],color:'#55bbcc',radius:.25}];
 let document={parts:clone(initial)},checkpoints=0,edits=0;
 const undo=[],redo=[],assembly=new THREE.Matrix4().makeRotationY(.4).setPosition(3,.5,-2);
 const matrixFor=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));
 const context={THREE,window:{SWYRL_ENGINE_WORKSPACES:{usingScratch:()=>false}},panel:{hidden:false},renderer:{},world,modelRoot:root,currentProject:{name:'Native test model'},
  model:()=>document,partById:id=>document.parts.find(p=>p.id===id),selection:null,undo,redo,atelierHDDirty:false,atelierMeshIds:[],atelierMeshAdding:true,atelierGroupScope:'group',atelierGroupCurrent:null,
  checkPart:p=>p&&['position','rotation','scale'].every(k=>Array.isArray(p[k])&&p[k].length===3&&p[k].every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=100))&&p.scale.every(n=>n>.005&&n<=20),
  select:id=>{context.selection=id;if(rebuildOnSelect)context.renderParts()},refreshList:()=>{},refreshInspector:()=>{},close:()=>{context.panel.hidden=true},checkpoint:()=>{undo.push(clone(document));redo.length=0;checkpoints++},
  signalEdited:()=>{edits++;context.renderParts()},historyStep:backward=>{const from=backward?undo:redo,to=backward?redo:undo;to.push(clone(document));document=from.pop();context.renderParts()},
  renderParts:()=>{
   for(const child of [...context.modelRoot.children])child.removeFromParent();
   for(const part of document.parts){
    const geometry=new THREE.BoxGeometry(.4,.5,.3);geometry.translate(...geometryOffset);
    let mesh,bone;
    if(skinned&&part.id==='part-a'){
     const count=geometry.getAttribute('position').count,weights=new Float32Array(count*4);
     for(let i=0;i<count;i++)weights[i*4]=1;
     geometry.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(new Uint16Array(count*4),4));
     geometry.setAttribute('skinWeight',new THREE.Float32BufferAttribute(weights,4));
     bone=new THREE.Bone();context.modelRoot.add(bone);
     mesh=new THREE.SkinnedMesh(geometry,new THREE.MeshStandardMaterial({color:part.color}));
    }else mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:part.color}));
    mesh.userData.atelierId=part.id;mesh.name=part.name;mesh.matrixAutoUpdate=false;
    mesh.matrix.copy(assembly.clone().multiply(matrixFor(part)));context.modelRoot.add(mesh);
    if(bone){context.modelRoot.updateWorldMatrix(true,true);const skeleton=new THREE.Skeleton([bone]);skeleton.calculateInverses();mesh.bind(skeleton,mesh.matrixWorld.clone());}
   }
  },
  structuredClone};
 context.renderParts();vm.createContext(context);vm.runInContext(bridgeSource+'\n'+toolsSource+'\nglobalThis.bridge=se340ModelBridge;globalThis.tools=se350ModelTools;',context);
 return {context,api:context.bridge,tools:context.tools,world,root,stage,initial,assembly,matrixFor,document:()=>document,replace:value=>{document=clone(value);context.currentProject={name:'Replacement model'};context.renderParts()},counts:()=>({checkpoints,edits})};
}
const equalMatrix=(a,b)=>a.elements.forEach((v,i)=>assert.ok(Math.abs(v-b.elements[i])<1e-9,`matrix element ${i}: ${v} != ${b.elements[i]}`));
let checks=0;
{
 const f=fixture(true),t=f.tools,originalMeshes=[...f.root.children];
 assert.equal(t.select('part-a').ok,true);assert.deepEqual(clone(t.selection().ids),['part-a']);
 assert.equal(t.select('part-b',{additive:true}).ok,true);assert.deepEqual(clone(t.selection().ids),['part-a','part-b']);
 assert.equal(f.root.children[0],originalMeshes[0],'Selection must not rebuild native skinned geometry');
 assert.equal(f.context.selection,'part-b');assert.equal(f.context.atelierMeshAdding,true);
 t.select('part-a',{additive:true});assert.deepEqual(clone(t.selection().ids),['part-b']);
 t.select('part-b',{additive:true});assert.deepEqual(clone(t.selection().ids),[]);assert.equal(f.context.selection,null);
 assert.equal(t.select('missing').ok,false);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 const f=fixture(),t=f.tools,initial=clone(f.document()),matrices=f.root.children.map(mesh=>mesh.matrix.clone());
 t.select('part-a');t.select('part-b',{additive:true});
 assert.equal(t.beginGroup().ok,true);
 for(let i=1;i<=30;i++)assert.equal(t.updateGroup({translation:[i/100,.2,-.1]}).ok,true);
 assert.deepEqual(f.document(),initial,'Preview cannot change saved descriptors');assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 for(const [i,mesh]of f.root.children.entries())equalMatrix(mesh.matrix,new THREE.Matrix4().makeTranslation(.3,.2,-.1).multiply(matrices[i]));
 assert.equal(t.endGroup().changed,true);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});
 for(const [i,mesh]of f.root.children.entries())equalMatrix(mesh.matrix,new THREE.Matrix4().makeTranslation(.3,.2,-.1).multiply(matrices[i]));
 assert.equal(t.endGroup().changed,false);assert.equal(f.api.undo().changed,true);assert.deepEqual(f.document(),initial);
 assert.equal(f.api.redo().changed,true);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});checks++;
}
{
 const f=fixture(),t=f.tools,matrices=f.root.children.map(mesh=>mesh.matrix.clone());
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.4,.1,0]});assert.equal(t.cancel('Tracking lost').cancelled,true);
 f.root.children.forEach((mesh,i)=>equalMatrix(mesh.matrix,matrices[i]));assert.deepEqual(f.document().parts,f.initial);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 t.beginGroup(['part-a','part-b']);assert.equal(t.endGroup().changed,false);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 t.beginGroup(['part-a']);t.updateGroup({translation:[.4,0,0]});t.endGroup();f.api.undo();const redo=f.api.inspect().redoDepth;
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.1,0,0]});t.cancel();assert.equal(f.api.inspect().redoDepth,redo);checks++;
}
{
 // Equivalent Euler rotations must not be normalized into a spurious edit.
 const f=fixture(),t=f.tools;f.document().parts[0].rotation=[Math.PI*2+.2,2.1,Math.PI*2-.3];f.context.renderParts();
 const rotation=[...f.document().parts[0].rotation];
 t.beginGroup(['part-a','part-b'],'two-hand');t.updateGroup({translation:[.2,0,0]});
 assert.equal(t.updateGroup({rotation:[0,0,0,-1]}).changed,false);assert.equal(t.endGroup().changed,false);
 assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 t.beginGroup(['part-a','part-b'],'move');t.updateGroup({translation:[.2,0,0]});t.endGroup();
 assert.deepEqual(clone(f.document().parts[0].rotation),rotation,'Move must retain exact source Euler representation');checks++;
}
for(const mode of ['rotate','scale','two-hand']){
 const f=fixture(false,[1.7,.6,-.8]),t=f.tools,matrices=f.root.children.map(mesh=>mesh.matrix.clone());
 const begun=t.beginGroup(['part-a','part-b'],mode),pivot=new THREE.Vector3(...begun.pivot);
 const q=mode==='scale'?new THREE.Quaternion():new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.55);
 const scale=mode==='rotate'?1:1.25,translation=mode==='two-hand'?[.2,-.1,.3]:[0,0,0];
 const delta={rotation:q.toArray(),scale,translation};
 assert.equal(t.updateGroup(delta).ok,true);
 const d=new THREE.Matrix4().makeTranslation(...translation).multiply(new THREE.Matrix4().makeTranslation(...pivot.toArray()))
  .multiply(new THREE.Matrix4().makeRotationFromQuaternion(q)).multiply(new THREE.Matrix4().makeScale(scale,scale,scale))
  .multiply(new THREE.Matrix4().makeTranslation(...pivot.clone().negate().toArray()));
 f.root.children.forEach((mesh,i)=>equalMatrix(mesh.matrix,d.clone().multiply(matrices[i])));
 assert.deepEqual(f.document().parts,f.initial);assert.equal(t.endGroup().changed,true);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});
 f.root.children.forEach((mesh,i)=>equalMatrix(mesh.matrix,d.clone().multiply(matrices[i])));
 assert.equal(f.api.undo().changed,true);assert.deepEqual(f.document().parts,f.initial);checks++;
}
{
 const f=fixture(),t=f.tools;assert.equal(t.beginGroup(['part-a'],'move').ok,true);
 for(const delta of [{translation:[NaN,0,0]},{translation:[101,0,0]},{scale:0},{rotation:[0,0,0,0]},
  {rotation:[0,0,0,2]},{rotation:new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.2).toArray()},
  {position:[0,0,0]},{translation:[1,2]}])assert.equal(t.updateGroup(delta).ok,false);
 assert.equal(t.updateGroup({translation:[.2,0,0]}).ok,true);t.cancel();
 assert.equal(t.beginGroup(['part-a','part-a']).ok,false);assert.equal(t.beginGroup(['missing']).ok,false);
 assert.equal(t.beginGroup(['part-a'],'sculpt').ok,false);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 const f=fixture(),t=f.tools;t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,0,0]});
 f.document().parts[1].color='#eeeeee';assert.equal(t.endGroup().ok,false);assert.equal(f.document().parts[1].color,'#eeeeee');
 assert.deepEqual(f.document().parts[0].position,f.initial[0].position);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,0,0]});
 const replacement={parts:[{...clone(f.initial[1]),id:'new-document'}]};f.replace(replacement);
 assert.equal(t.endGroup().changed,false);assert.deepEqual(f.document(),replacement);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 const f=fixture(),t=f.tools;t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,0,0]});
 f.context.renderParts();assert.equal(t.inspect().gesture,null);assert.deepEqual(f.document().parts,f.initial);
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,0,0]});f.context.close();assert.equal(t.inspect().gesture,null);
 assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 // A native assembly with nonuniform scale can turn group rotation into shear.
 // Saved descriptors cannot represent it: reject the whole preview atomically.
 const f=fixture(),t=f.tools,mesh=f.root.children[0];mesh.matrix.premultiply(new THREE.Matrix4().makeScale(2,1,.7));
 const original=f.root.children.map(mesh=>mesh.matrix.clone());t.beginGroup(['part-a','part-b'],'two-hand');
 const q=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),.5);
 assert.equal(t.updateGroup({rotation:q.toArray()}).reason,'MODEL_GROUP_SHEAR_UNSUPPORTED');
 f.root.children.forEach((mesh,i)=>equalMatrix(mesh.matrix,original[i]));assert.equal(t.endGroup().changed,false);
 assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 // Attached native skin with sibling bones must visibly move with the group,
 // restore its inverse-bind behavior on cancel, and rebind once on commit.
 const f=fixture(false,[0,0,0],true),t=f.tools,scene=new THREE.Scene();scene.add(f.stage);f.api.borrowRoot(f.stage);
 f.stage.position.set(.2,1.4,-1.1);f.stage.rotation.y=.3;f.stage.scale.setScalar(.6);
 const skin=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a'),update=skin.updateMatrixWorld,own=Object.hasOwn(skin,'updateMatrixWorld');
 const frame=()=>{scene.updateMatrixWorld(true);for(const mesh of f.root.children)if(mesh.isSkinnedMesh)mesh.skeleton.update();};
 const vertex=mesh=>mesh.getVertexPosition(0,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld);
 frame();const before=vertex(skin),oldWorld=skin.matrixWorld.clone(),bind=skin.bindMatrix.clone();
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,.1,-.1]});t.projection();frame();
 const expected=before.clone().applyMatrix4(oldWorld.clone().invert()).applyMatrix4(skin.matrixWorld);
 assert.ok(vertex(skin).distanceTo(expected)<1e-8);assert.ok(skin.bindMatrix.equals(bind));assert.deepEqual(f.document().parts,f.initial);
 t.cancel();frame();assert.ok(vertex(skin).distanceTo(before)<1e-8);assert.equal(skin.updateMatrixWorld,update);assert.equal(Object.hasOwn(skin,'updateMatrixWorld'),own);
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.2,.1,-.1]});frame();assert.equal(t.endGroup().changed,true);frame();
 const committed=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a');assert.ok(vertex(committed).distanceTo(expected)<1e-8);
 assert.equal(skin.updateMatrixWorld,update);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});f.api.releaseRoot();checks++;
}
{
 const f=fixture(false,[0,0,0],true),t=f.tools,skin=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a'),update=skin.updateMatrixWorld;
 t.beginGroup(['part-a','part-b']);t.updateGroup({translation:[.3,0,0]});f.replace({parts:[{...clone(f.initial[1]),id:'replacement'}]});
 assert.equal(skin.updateMatrixWorld,update);assert.equal(Object.hasOwn(skin,'updateMatrixWorld'),false);assert.equal(t.inspect().gesture,null);checks++;
}
{
 const f=fixture(),t=f.tools;t.select('part-a');t.select('part-b',{additive:true});f.api.borrowRoot(f.stage);
 assert.equal(t.refreshSelection().reason,'MODEL_ROOT_STILL_BORROWED');f.api.releaseRoot();
 assert.equal(t.refreshSelection().refreshed,true);assert.deepEqual(clone(t.selection().ids),['part-a','part-b']);
 assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 const replacement={parts:[clone(f.initial[1])]};f.replace(replacement);assert.deepEqual(clone(t.selection().ids),['part-b']);
 assert.equal(t.inspect().primaryId,'part-b');t.select(null);assert.deepEqual(clone(t.selection().ids),[]);checks++;
}
console.log('MODEL_VR_NATIVE_TOOLS_V11_350_PASS',JSON.stringify({checks,three:THREE.REVISION,selection:'native additive IDs; no rebuild',transactions:'one checkpoint for selected group',attachedSkin:'preview/cancel/commit/invalidation',shear:'atomic rejection'}));
