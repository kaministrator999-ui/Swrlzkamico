#!/usr/bin/env node
// Native bridge contracts with real Three math; no browser/XR mocks are shipped.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_v11_340.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const bridgeSource=fs.readFileSync(path.join(ROOT,'runtime/model_vr_bridge_v11_340.js'),'utf8');
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
  model:()=>document,partById:id=>document.parts.find(p=>p.id===id),selection:null,undo,redo,atelierHDDirty:false,atelierMeshAdding:true,atelierGroupScope:'group',
  checkPart:p=>p&&['position','rotation','scale'].every(k=>Array.isArray(p[k])&&p[k].length===3&&p[k].every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=100))&&p.scale.every(n=>n>.005&&n<=20),
  select:id=>{context.selection=id;if(rebuildOnSelect)context.renderParts()},close:()=>{context.panel.hidden=true},checkpoint:()=>{undo.push(clone(document));redo.length=0;checkpoints++},
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
 context.renderParts();vm.createContext(context);vm.runInContext(bridgeSource+'\nglobalThis.bridge=se340ModelBridge;',context);
 return {context,api:context.bridge,world,root,stage,initial,assembly,matrixFor,document:()=>document,replace:value=>{document=clone(value);context.currentProject={name:'Replacement model'};context.renderParts()},counts:()=>({checkpoints,edits})};
}
const equalMatrix=(a,b)=>a.elements.forEach((v,i)=>assert.ok(Math.abs(v-b.elements[i])<1e-9,`matrix element ${i}: ${v} != ${b.elements[i]}`));
let checks=0;
{
 const f=fixture(),{api,root,stage,world}=f,mesh=root.children[0],original=mesh.matrix.clone(),parentIndex=world.children.indexOf(root),pose={p:root.position.clone(),q:root.quaternion.clone(),s:root.scale.clone(),m:root.matrix.clone()};
 const helper=new THREE.BoxHelper(mesh);helper.userData.atelierHelper=true;root.add(helper);let disposal=0;mesh.geometry.addEventListener('dispose',()=>disposal++);mesh.material.addEventListener('dispose',()=>disposal++);
 assert.equal(api.borrowRoot(stage).ok,true);assert.equal(root.parent,stage);assert.equal(helper.visible,false);assert.equal(api.inspect().borrowed,true);
 assert.equal(api.select('part-a').ok,true);assert.equal(f.context.atelierMeshAdding,false);assert.equal(f.context.atelierGroupScope,'child');assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 assert.equal(api.begin('part-a','move').ok,true);
 for(let n=1;n<=20;n++)assert.equal(api.update({position:[1+n/20,2.3,3]}).ok,true);
 assert.deepEqual(f.document().parts,f.initial,'Live preview must not mutate native saved data');assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 equalMatrix(mesh.matrix,f.assembly.clone().multiply(f.matrixFor({...f.initial[0],position:[2,2.3,3]})));
 assert.equal(api.cancel().cancelled,true);equalMatrix(mesh.matrix,original);assert.equal(mesh.matrixAutoUpdate,false);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 assert.equal(api.releaseRoot().ok,true);assert.equal(root.parent,world);assert.equal(world.children.indexOf(root),parentIndex);assert.deepEqual(root.position.toArray(),pose.p.toArray());assert.ok(root.quaternion.equals(pose.q));assert.ok(root.scale.equals(pose.s));assert.equal(helper.visible,true);assert.equal(disposal,0,'XR release must not dispose native projection resources');checks++;
}
{
 const f=fixture(),api=f.api;
 assert.equal(api.begin('part-a','move').ok,true);api.update({position:[1+1e-8,2,3]});assert.equal(api.end().changed,false);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});
 assert.equal(api.begin('part-a','move').ok,true);api.update({position:[1.4,2,3]});assert.equal(api.end().changed,true);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});assert.equal(api.end().changed,false,'Repeated release cannot duplicate a checkpoint');
 const committed=clone(f.document());assert.equal(api.undo().changed,true);assert.deepEqual(f.document().parts,f.initial);assert.equal(api.inspect().redoDepth,1);
 api.begin('part-a','move');api.update({position:[1.9,2,3]});api.cancel('Tracking lost');assert.equal(api.inspect().redoDepth,1,'Cancelled gesture cannot erase Redo');assert.equal(api.redo().changed,true);assert.deepEqual(f.document(),committed);
 api.begin('part-a','move');api.end();assert.equal(api.inspect().undoDepth,1,'No-op grip must not consume Undo');api.undo();assert.deepEqual(f.document().parts,f.initial);checks++;
}
{
 const f=fixture(),api=f.api;
 for(const [mode,key,value]of [['rotate','rotation',[.4,.2,-.1]],['scale','scale',[1.25,1.25,1.25]]]){
  api.begin('part-a',mode);assert.equal(api.update({[key]:value}).ok,true);api.end();const part=clone(f.document().parts[0]);assert.deepEqual(part[key],value);assert.deepEqual(f.document().parts[1],f.initial[1]);assert.equal(part.color,f.initial[0].color);assert.equal(part.radius,f.initial[0].radius);api.undo();assert.deepEqual(f.document().parts,f.initial);
 }
 api.begin('part-a','move');for(const bad of [{position:[NaN,0,0]},{position:[Infinity,0,0]},{position:[101,0,0]},{position:[1,2]},{scale:[0,1,1]},{scale:[1.1,1,1]},{name:'not a transform'}])assert.equal(api.update(bad).ok,false);
 api.cancel();assert.deepEqual(f.document().parts,f.initial);assert.equal(api.begin('missing','move').ok,false);assert.equal(api.begin('part-a','sculpt').ok,false);checks++;
}
{
 const f=fixture(),api=f.api;api.begin('part-a','move');api.update({position:[2,2,3]});
 const replacement={parts:[{...clone(f.initial[1]),id:'replacement',name:'Replacement untouched'}]};f.replace(replacement);assert.equal(api.end().changed,false);assert.deepEqual(f.document(),replacement);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});assert.equal(api.inspect().gesture,null);checks++;
}
{
 const f=fixture(),api=f.api;api.begin('part-a','move');api.update({position:[2,2,3]});f.document().parts[0].color='#eeeeee';assert.equal(api.end().ok,false);assert.equal(f.document().parts[0].color,'#eeeeee');assert.deepEqual(f.document().parts[0].position,f.initial[0].position);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 const f=fixture(),api=f.api;api.borrowRoot(f.stage);const foreign=new THREE.Group();foreign.add(f.root);assert.equal(api.releaseRoot().reason,'MODEL_ROOT_OWNERSHIP_CHANGED');assert.equal(f.root.parent,foreign,'Release cannot steal a projection owned elsewhere');checks++;
}
{
 const f=fixture(),api=f.api;api.borrowRoot(f.stage);api.begin('part-a','move');api.update({position:[2,2,3]});f.context.close();assert.equal(api.inspect().borrowed,false);assert.equal(f.root.parent,f.world);assert.deepEqual(f.document().parts,f.initial);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
{
 const f=fixture(true),old=f.root.children[0];assert.equal(f.api.begin('part-a','move').ok,true);const active=f.root.children[0];assert.notEqual(active,old,'Native selection rebuild fixture must replace the derived mesh');
 assert.equal(f.api.update({position:[1.6,2,3]}).ok,true);equalMatrix(active.matrix,f.assembly.clone().multiply(f.matrixFor({...f.initial[0],position:[1.6,2,3]})));
 assert.equal(f.api.end().changed,true);assert.deepEqual(clone(f.document().parts[0].position),[1.6,2,3]);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});checks++;
}
{
 // A controller's world-space delta must survive a native assembly basis,
 // including a quarter-turn and nonuniform parent scales.
 const context={THREE,window:{},ModelAtelier:{}};
 vm.createContext(context);
 vm.runInContext(workspaceSource+'\nglobalThis.gripBasis=se340GripBasis;',context);
 const world=new THREE.Scene(),root=new THREE.Group();
 root.position.set(2,.5,-3);root.rotation.y=Math.PI/2;root.scale.set(2,.5,1.25);world.add(root);
 const assembly=new THREE.Matrix4().compose(new THREE.Vector3(1,.3,-.6),
  new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,0,1),Math.PI/2),new THREE.Vector3(.7,1.4,.9));
 const part={position:[.2,1,-.3],rotation:[.2,-.1,.3],scale:[.8,.9,1.1]};
 const compose=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));
 const mesh=new THREE.Mesh(new THREE.BoxGeometry(.2,.2,.2));mesh.matrixAutoUpdate=false;
 mesh.matrix.copy(assembly.clone().multiply(compose(part)));root.add(mesh);world.updateMatrixWorld(true);
 const basis=context.gripBasis(mesh,part),expected=root.matrixWorld.clone().multiply(assembly);
 equalMatrix(basis.inverse.clone().invert(),expected);
 const hand=new THREE.Vector3(.4,1.2,-.8),movement=new THREE.Vector3(.11,.03,-.02);
 const delta=hand.clone().add(movement).applyMatrix4(basis.inverse).sub(hand.clone().applyMatrix4(basis.inverse));
 const next={...part,position:part.position.map((value,index)=>value+delta.getComponent(index))};
 const beforeCenter=new THREE.Vector3().setFromMatrixPosition(expected.clone().multiply(compose(part)));
 const afterCenter=new THREE.Vector3().setFromMatrixPosition(expected.clone().multiply(compose(next)));
 assert.ok(afterCenter.sub(beforeCenter).distanceTo(movement)<1e-9,'Assembly must not rotate or rescale the physical controller translation');
 const axis=new THREE.Vector3(1,0,0).applyQuaternion(basis.quaternion).normalize();
 assert.ok(axis.distanceTo(new THREE.Vector3(1,0,0).transformDirection(expected))<1e-9,'Rotation basis must include the assembly orientation');
 checks++;
}
for(const mode of ['rotate','scale']){
 // Chat loft/topology geometry can be off-centre while its descriptor has a
 // zero position. Rotate and Scale must preserve that visible part's pivot.
 const f=fixture(false,[1.7,.6,-.8]),api=f.api;
 api.borrowRoot(f.stage);f.root.updateWorldMatrix(true,true);
 const mesh=f.root.children[0];mesh.geometry.computeBoundingBox();
 const center=mesh.geometry.boundingBox.getCenter(new THREE.Vector3());
 const before=clone(f.initial[0]),next=clone(before);
 const pivotBefore=center.clone().applyMatrix4(mesh.matrixWorld);
 if(mode==='rotate')next.rotation=[.5,-.4,.2];else next.scale=before.scale.map(value=>value*1.4);
 const offset=part=>center.clone().multiply(new THREE.Vector3(...part.scale))
  .applyQuaternion(new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)));
 next.position=new THREE.Vector3(...before.position).add(offset(before)).sub(offset(next)).toArray();
 assert.equal(api.begin('part-a',mode).ok,true);
 const field=mode==='rotate'?'rotation':'scale';
 assert.equal(api.update({[field]:next[field]}).ok,true,'Rotate/Scale must derive its own pivot compensation');
 assert.deepEqual(f.document().parts,f.initial,'Pivot preview must not write saved descriptors');
 const active=f.root.children[0];active.updateWorldMatrix(true,false);
 assert.ok(center.clone().applyMatrix4(active.matrixWorld).distanceTo(pivotBefore)<1e-8,'Off-centre native geometry pivot moved during preview');
 assert.equal(api.update({[field]:next[field],position:next.position.map((value,index)=>value+(index===0?.02:0))}).ok,false,'Unrelated translation cannot masquerade as Rotate/Scale pivot compensation');
 assert.equal(api.end().changed,true);assert.deepEqual(f.counts(),{checkpoints:1,edits:1});
 assert.ok(new THREE.Vector3(...f.document().parts[0].position).distanceTo(new THREE.Vector3(...next.position))<1e-9);
 assert.deepEqual(clone(f.document().parts[0][field]),next[field]);assert.deepEqual(f.document().parts[1],f.initial[1]);
 const committed=f.root.children[0];committed.updateWorldMatrix(true,false);
 assert.ok(center.clone().applyMatrix4(committed.matrixWorld).distanceTo(pivotBefore)<1e-8,'Off-centre native geometry pivot moved after commit');
 assert.equal(api.undo().changed,true);assert.deepEqual(f.document().parts,f.initial);api.releaseRoot();checks++;
}
{
 // Native hand/wolf rigs use attached SkinnedMesh with sibling bones. Its
 // ordinary inverse-bind update otherwise cancels a live mesh-matrix move.
 const f=fixture(false,[0,0,0],true),api=f.api,xrScene=new THREE.Scene();
 f.stage.position.set(.2,1.4,-1.1);f.stage.rotation.y=.3;f.stage.scale.setScalar(.6);xrScene.add(f.stage);api.borrowRoot(f.stage);
 const skin=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a'),update=skin.updateMatrixWorld,ownUpdate=Object.hasOwn(skin,'updateMatrixWorld');
 const frame=()=>{xrScene.updateMatrixWorld(true);for(const mesh of f.root.children)if(mesh.isSkinnedMesh)mesh.skeleton.update();};
 const vertex=mesh=>mesh.getVertexPosition(0,new THREE.Vector3()).applyMatrix4(mesh.matrixWorld);
 frame();const before=vertex(skin),bind=skin.bindMatrix.clone(),skeleton=skin.skeleton,positions=skin.geometry.getAttribute('position').array;
 const oldWorld=skin.matrixWorld.clone();api.begin('part-a','move');api.update({position:[1.4,2,3]});frame();
 const expected=before.clone().applyMatrix4(oldWorld.clone().invert()).applyMatrix4(skin.matrixWorld);
 assert.ok(vertex(skin).distanceTo(expected)<1e-8,'Attached skin preview did not follow the controller transform');
 assert.ok(skin.bindMatrix.equals(bind));assert.equal(skin.skeleton,skeleton);assert.equal(skin.geometry.getAttribute('position').array,positions);assert.deepEqual(f.document().parts,f.initial);
 api.cancel();frame();assert.ok(vertex(skin).distanceTo(before)<1e-8);assert.equal(skin.updateMatrixWorld,update);assert.equal(Object.hasOwn(skin,'updateMatrixWorld'),ownUpdate);
 api.begin('part-a','move');api.update({position:[1.4,2,3]});frame();assert.equal(api.end().changed,true);frame();
 assert.equal(skin.updateMatrixWorld,update,'Committed old projection retained a transient skin hook');
 const committed=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a');
 assert.ok(vertex(committed).distanceTo(expected)<1e-8,'Skin commit/rebind differs from its controller preview');
 assert.deepEqual(f.counts(),{checkpoints:1,edits:1});api.releaseRoot();f.world.updateMatrixWorld(true);committed.skeleton.update();
 assert.equal(f.root.parent,f.world);assert.equal(committed.updateMatrixWorld,update);checks++;
}
{
 const f=fixture(false,[0,0,0],true),api=f.api;
 const skin=f.root.children.find(mesh=>mesh.userData?.atelierId==='part-a'),update=skin.updateMatrixWorld,ownUpdate=Object.hasOwn(skin,'updateMatrixWorld');
 api.begin('part-a','move');api.update({position:[1.4,2,3]});
 const replacement={parts:[{...clone(f.initial[1]),id:'skin-replacement'}]};f.replace(replacement);
 assert.equal(skin.updateMatrixWorld,update,'Invalidated old skin retained a hook into a former model');assert.equal(Object.hasOwn(skin,'updateMatrixWorld'),ownUpdate);
 assert.deepEqual(f.document(),replacement);assert.deepEqual(f.counts(),{checkpoints:0,edits:0});checks++;
}
console.log('MODEL_VR_NATIVE_BRIDGE_V11_340_PASS',JSON.stringify({checks,three:THREE.REVISION,actualThreeMath:true,gestureTransactions:'commit once; cancel/noop preserve history',nativeRootOwnership:'restored; no borrowed disposal'}));
