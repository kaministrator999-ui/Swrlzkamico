#!/usr/bin/env node
// Actual native sculpt operators, native indexed validation/audit and Three169.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath, pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_sculpt_draw_v11_350.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2]))); assert.equal(THREE.REVISION,'169');
const source=name=>fs.readFileSync(path.join(ROOT,'runtime',name),'utf8');
const native=[source('model_atelier_sculpt_brush_v11_21.js'),source('model_atelier_surface_targeting_v11_22.js'),source('model_atelier_surface_lasso_v11_22.js'),source('model_atelier_brush_ops_v11_27.js'),source('model_atelier_topology_lod_v11_38.js'),source('model_atelier_topology_audit_v11_44.js')].join('\n');
const extension=source('model_vr_sculpt_draw_v11_350.js');
const clone=value=>JSON.parse(JSON.stringify(value));
function fixture(options={}){
 let document={parts:[{id:'sphere',name:'Native sphere',kind:'sphere',color:'#aa77cc',material:'matte',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]}]}, checkpoints=0,changes=0;
 const world=new THREE.Scene(),root=new THREE.Group();world.add(root);
 const undo=[],redo=[];
 const ctx={THREE,MODEL_ATELIER_LIMIT:400,MODEL_ATELIER_KINDS:['sphere','box','cone','cylinder'],window:{},panel:{hidden:false},modelRoot:root,world,renderer:{},selection:null,atelierHDDirty:false,
   model:()=>document,partById:id=>document.parts.find(p=>p.id===id),atelierLassoValid:()=>true,atelierRefineValid:()=>true,atelierLassoApply:()=>{},atelierRefineApply:g=>g,
   checkpoint:()=>{undo.push(clone(document));redo.length=0;checkpoints++;},signalEdited:()=>{changes++;ctx.renderParts();},close:()=>{ctx.panel.hidden=true;},
   checkPart:p=>p&&typeof p.id==='string'&&['sphere','topologyMesh'].includes(p.kind)&&['position','rotation','scale'].every(k=>Array.isArray(p[k])&&p[k].length===3&&p[k].every(n=>Number.isFinite(n)&&Math.abs(n)<=100))&&p.scale.every(n=>n>.005&&n<=20)&&ctx.nativeSculptValid(p)&&ctx.nativeTopologyValid(p),
   se340ModelBridge:{inspect:()=>({gesture:null}),select:id=>{ctx.selection=id;ctx.renderParts();return {ok:true};}},
   renderParts:()=>{for(const mesh of [...root.children]){mesh.removeFromParent();mesh.geometry?.dispose();mesh.material?.dispose();}for(const part of document.parts){let g=part.kind==='topologyMesh'?ctx.nativeTopologyGeometry(part):new THREE.SphereGeometry(.5,20,16);g=ctx.nativeSculptApply(g,part);const mesh=options.skin?new THREE.SkinnedMesh(g,new THREE.MeshStandardMaterial()):new THREE.Mesh(g,new THREE.MeshStandardMaterial());mesh.userData.atelierId=part.id;mesh.position.fromArray(part.position);mesh.rotation.set(...part.rotation);mesh.scale.fromArray(part.scale);root.add(mesh);if(options.skin){const n=g.attributes.position.count,skinWeight=new Float32Array(n*4);for(let i=0;i<n;i++)skinWeight[i*4]=1;g.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(new Uint16Array(n*4),4));g.setAttribute('skinWeight',new THREE.Float32BufferAttribute(skinWeight,4));const bone=new THREE.Bone();bone.position.set(.07,.12,.03);root.add(bone);root.updateMatrixWorld(true);const skeleton=new THREE.Skeleton([bone]);skeleton.calculateInverses();mesh.bind(skeleton,mesh.matrixWorld.clone());bone.rotation.y=document.pose||0;root.updateMatrixWorld(true);skeleton.update();}}root.updateMatrixWorld(true);},
 };
 vm.createContext(ctx);vm.runInContext(native+'\nglobalThis.nativeSculptValid=atelierSculptValid;globalThis.nativeTopologyValid=atelierTopologyValid;globalThis.nativeTopologyGeometry=atelierTopologyGeometry;globalThis.nativeSculptApply=atelierSculptApply;globalThis.audit=atelierTopologyAudit;globalThis.compileNativeMask=atelierLassoCompiledRegionMask;globalThis.nativeLassoValid=atelierLassoValid;',ctx);ctx.renderParts();
 vm.runInContext(extension+'\nglobalThis.surface=se350ModelSurface;',ctx);
 return {ctx,api:ctx.surface,root,document:()=>document,replace:d=>{document=clone(d);ctx.renderParts();},counts:()=>({checkpoints,changes}),undo,redo,step:back=>{const from=back?undo:redo,to=back?redo:undo;if(!from.length)return;to.push(clone(document));document=from.pop();ctx.renderParts();}};
}
const positions=f=>[...f.root.children.find(m=>m.isMesh).geometry.attributes.position.array].map(n=>n===0?0:n);
let checks=0;
for(const operation of ['push','smooth','flatten','inflate','pinch','translate']){
 const f=fixture(),before=clone(f.document()),original=positions(f),originalGeometry=f.root.children[0].geometry;
 assert.equal(f.api.sculptBegin('sphere',{operation,radius:.4,strength:.1}).ok,true);
 const nativeGeometry=f.root.children[0].geometry;assert.notEqual(nativeGeometry,originalGeometry);
 for(let n=0;n<8;n++)assert.equal(f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],delta:[.008,.003,0],dt:1/60}).ok,true);
 const preview=positions(f);assert.notDeepEqual(preview,original,operation+' must deform actual native vertices');
 assert.deepEqual(clone(f.document()),before,'Controller-held previews must not mutate saved data');assert.deepEqual(f.counts(),{checkpoints:0,changes:0});
 const result=f.api.sculptEnd();assert.equal(result.ok,true);assert.equal(result.changed,true);assert.deepEqual(f.counts(),{checkpoints:1,changes:1});
 assert.equal(f.ctx.nativeSculptValid(f.document().parts[0]),true);assert.deepEqual(positions(f),preview,'Committed sparse native edits must deterministically rebuild preview');
 const saved=clone(f.document());f.replace(saved);assert.deepEqual(positions(f),preview,'Native JSON roundtrip must preserve stroke');
 f.step(true);assert.deepEqual(clone(f.document()),before);assert.deepEqual(positions(f),original);f.step(false);assert.deepEqual(clone(f.document()),saved);checks++;
}
{
 const f=fixture(),before=clone(f.document()),original=positions(f);f.redo.push({example:'redo stays'});
 assert.equal(f.api.sculptBegin('sphere').ok,true);f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],dt:1/60});assert.equal(f.api.cancel('Tracking lost').cancelled,true);
 assert.deepEqual(clone(f.document()),before);assert.deepEqual(positions(f),original);assert.equal(f.redo.length,1);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});
 assert.equal(f.api.sculptBegin('sphere').ok,true);assert.equal(f.api.sculptEnd().changed,false);assert.equal(f.redo.length,1);
 assert.equal(f.api.sculptBegin('sphere',{radius:NaN}).ok,false);assert.equal(f.api.sculptBegin('sphere',{operation:'invented'}).ok,false);
 assert.equal(f.api.sculptBegin('sphere').ok,true);for(const sample of [{center:[Infinity,0,0],normal:[0,0,1]},{center:[0,0,.5],normal:[0,0,0]},{center:[0,0,.5],normal:[0,0,1],dt:-1}])assert.equal(f.api.sculptUpdate(sample).ok,false);f.api.cancel();checks++;
}
{
 const f=fixture();f.api.sculptBegin('sphere');f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],dt:.02});f.document().parts[0].color='#123456';assert.equal(f.api.sculptEnd().ok,false);assert.equal(f.document().parts[0].color,'#123456');assert.equal(f.document().parts[0].sculptVertexEdits,undefined);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});
 f.api.sculptBegin('sphere');f.replace({parts:[]});assert.equal(f.api.inspect().active,null);assert.equal(f.document().parts.length,0);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});checks++;
}
function draw(f,points=[[0,0,0],[.5,0,0],[.5,.5,0],[.25,.25,0],[0,.5,0]]){assert.equal(f.api.drawBegin({normal:[0,0,1]}).ok,true);for(const p of points)assert.equal(f.api.drawUpdate(p).ok,true);return f.api.drawEnd();}
{
 const f=fixture(),before=clone(f.document());const result=draw(f);assert.equal(result.ok,true);assert.equal(result.faces,3);assert.equal(result.vertices,5);assert.deepEqual(f.counts(),{checkpoints:1,changes:1});
 const face=f.document().parts.find(p=>p.id===result.id);assert.equal(face.kind,'topologyMesh');assert.equal(f.ctx.nativeTopologyValid(face),true);const audit=f.ctx.audit(face.topologyMesh);assert.equal(audit.boundaryEdges,5);assert.equal(audit.oppositeWindingErrors,0);assert.equal(audit.zeroAreaFaces,0);
 const saved=clone(f.document());f.replace(saved);f.step(true);assert.deepEqual(clone(f.document()),before);f.step(false);assert.deepEqual(clone(f.document()),saved);checks++;
}
{
 const f=fixture(),before=clone(f.document());f.redo.push({preserved:true});assert.equal(f.api.drawBegin().ok,true);f.api.drawUpdate([0,0,0]);f.api.drawUpdate([.1,0,.02]);f.api.cancel();assert.deepEqual(clone(f.document()),before);assert.equal(f.redo.length,1);
 assert.equal(draw(f,[[0,0,0],[.5,.5,0],[0,.5,0],[.5,0,0]]).reason,'OUTLINE_SELF_INTERSECTS');assert.deepEqual(clone(f.document()),before);
 assert.equal(draw(f,[[0,0,0],[.2,0,0],[.4,0,0]]).ok,false);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});assert.equal(f.root.children.some(c=>c.isLine),false);checks++;
}
for(const depth of [.15,-.15]){
 const f=fixture(),result=draw(f),before=clone(f.document());assert.equal(f.api.extrudeBegin(result.id).ok,true);assert.equal(f.api.extrudeUpdate(depth).ok,true);const preview=positions({...f,root:{children:[f.root.children.find(m=>m.userData?.atelierId===result.id)]}});assert.deepEqual(clone(f.document()),before);
 assert.equal(f.api.extrudeEnd().changed,true);assert.deepEqual(f.counts(),{checkpoints:2,changes:2});const part=f.document().parts.find(p=>p.id===result.id),audit=f.ctx.audit(part.topologyMesh);assert.equal(audit.boundaryEdges,0);assert.equal(audit.nonManifoldEdges,0);assert.equal(audit.zeroAreaFaces,0);assert.equal(audit.oppositeWindingErrors,0);assert.equal(part.topologyMesh.positions.length/3,10);assert.equal(part.topologyMesh.indices.length/3,16);
 assert.deepEqual([...f.root.children.find(m=>m.userData?.atelierId===result.id).geometry.attributes.position.array].map(n=>n===0?0:n),preview);const saved=clone(f.document());f.step(true);assert.deepEqual(clone(f.document()),before);f.step(false);assert.deepEqual(clone(f.document()),saved);checks++;
}
{
 const f=fixture(),result=draw(f),before=clone(f.document());f.redo.push({preserved:true});f.api.extrudeBegin(result.id);f.api.extrudeUpdate(.15);assert.equal(f.api.extrudeEnd(false).cancelled,true);assert.deepEqual(clone(f.document()),before);assert.equal(f.redo.length,1);
 f.api.extrudeBegin(result.id);f.api.extrudeUpdate(.15);f.api.extrudeUpdate(0);assert.equal(f.api.extrudeEnd().changed,false);assert.deepEqual(clone(f.document()),before);assert.deepEqual(f.counts(),{checkpoints:1,changes:1});
 assert.equal(f.api.extrudeBegin('sphere').ok,false);f.api.extrudeBegin(result.id);assert.equal(f.api.extrudeUpdate(Infinity).ok,false);assert.equal(f.api.extrudeUpdate(5).ok,false);f.ctx.close();assert.equal(f.api.inspect().active,null);assert.deepEqual(clone(f.document()),before);checks++;
}
{
 const f=fixture(),mesh=f.root.children[0];mesh.rotation.set(.3,.5,.1);mesh.scale.set(2,.7,1.5);f.root.rotation.set(.2,-.3,0);f.root.updateMatrixWorld(true);
 const local=new THREE.Vector3(.1,.2,.4),normal=new THREE.Vector3(.2,.1,1).normalize(),world=mesh.localToWorld(local.clone()),worldNormal=normal.clone().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld));
 const hit=f.api.localHit('sphere',{point:world.toArray(),normal:worldNormal.toArray()});assert.equal(hit.ok,true);assert.ok(new THREE.Vector3(...hit.center).distanceTo(local)<1e-10);assert.ok(new THREE.Vector3(...hit.normal).distanceTo(normal)<1e-10);checks++;
}

{
 const f=fixture({skin:true});
 // Actual attached skin and bone both move with the borrowed workbench.
 f.root.position.set(.5,1.2,-1.5);f.root.rotation.set(.2,.4,-.1);f.root.scale.set(.6,.6,.6);f.root.updateMatrixWorld(true);
 f.ctx.se340ModelBridge.select=()=>({ok:true});
 const before=clone(f.document());assert.equal(f.api.sculptBegin('sphere',{radius:.4,strength:.1}).ok,true);
 const live=f.root.children.find(m=>m.isSkinnedMesh);assert.equal(live.isSkinnedMesh,true);
 for(let i=0;i<4;i++)assert.equal(f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],dt:1/60}).ok,true);
 const preview=[...live.geometry.attributes.position.array].map(n=>n===0?0:n);assert.deepEqual(clone(f.document()),before);
 assert.equal(f.api.sculptEnd().changed,true);assert.deepEqual(positions(f),preview);assert.deepEqual(f.counts(),{checkpoints:1,changes:1});
 f.step(true);assert.deepEqual(clone(f.document()),before);f.document().pose=.4;f.ctx.renderParts();
 assert.equal(f.api.sculptBegin('sphere').reason,'SCULPT_REQUIRES_BIND_POSE');assert.deepEqual(f.counts(),{checkpoints:1,changes:1});checks++;
}
{
 const f=fixture({skin:true});f.api.sculptBegin('sphere');f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],dt:.02});
 const live=f.root.children.find(m=>m.isSkinnedMesh);live.skeleton.bones[0].rotation.y=.4;live.skeleton.bones[0].updateMatrixWorld(true);live.skeleton.update();
 assert.equal(f.api.sculptEnd().ok,false,'A pose change must invalidate a bind-space stroke');assert.equal(f.document().parts[0].sculptVertexEdits,undefined);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});checks++;
}


{
 const f=fixture({skin:true}),result=draw(f),before=clone(f.document());
 assert.equal(f.api.extrudeBegin(result.id).ok,true);assert.equal(f.api.extrudeUpdate(.1).ok,true);
 const mesh=f.root.children.find(m=>m.userData?.atelierId===result.id);assert.equal(mesh.isSkinnedMesh,true);assert.equal(mesh.geometry.attributes.skinWeight.count,mesh.geometry.attributes.position.count);
 for(let i=0;i<mesh.geometry.attributes.position.count;i++){const p=mesh.getVertexPosition(i,new THREE.Vector3());assert.ok(p.toArray().every(Number.isFinite));}
 assert.equal(f.api.extrudeEnd().changed,true);const saved=clone(f.document());assert.equal(f.ctx.audit(saved.parts.find(p=>p.id===result.id).topologyMesh).boundaryEdges,0);
 f.step(true);assert.deepEqual(clone(f.document()),before);f.step(false);assert.deepEqual(clone(f.document()),saved);checks++;
}


function lasso(f,points=[[-.2,-.2,.45],[.2,-.2,.45],[.2,.2,.45],[-.2,.2,.45]]){assert.equal(f.api.lassoBegin('sphere',{normal:[0,0,1]}).ok,true);for(const p of points)assert.equal(f.api.lassoUpdate(p).ok,true);return f.api.lassoEnd();}
{
 const f=fixture(),before=clone(f.document()),original=positions(f),result=lasso(f);assert.equal(result.ok,true);assert.equal(f.document().parts.length,1,'A region must not create a mesh face');assert.equal(result.pins,4);
 assert.deepEqual(f.counts(),{checkpoints:1,changes:1});assert.equal(f.ctx.nativeLassoValid(f.document().parts[0]),true);assert.deepEqual(positions(f),original,'A zero-morph region saves a selection without changing geometry');
 const region=f.document().parts[0].sculptLassos[0],mask=f.ctx.compileNativeMask(f.document().parts[0],region);assert.equal(region.id,result.regionId);assert.equal(f.api.inspect().selectedRegionId,result.regionId);
 assert.ok(region.pins.every(p=>Number.isInteger(p.tri)&&p.bary.length===3&&Math.abs(p.bary.reduce((n,v)=>n+v,0)-1)<1e-5));
 const saved=clone(f.document());f.replace(saved);f.step(true);assert.deepEqual(clone(f.document()),before);f.step(false);assert.deepEqual(clone(f.document()),saved);
 assert.equal(f.api.sculptBegin('sphere',{radius:.8,strength:.2}).regionId,result.regionId);for(let i=0;i<8;i++)assert.equal(f.api.sculptUpdate({center:[0,0,.5],normal:[0,0,1],dt:1/60}).ok,true);
 const preview=positions(f);let changedInside=0,outside=0;
 for(let i=0;i<original.length;i+=3){const p=original.slice(i,i+3),changed=p.some((n,k)=>Math.abs(n-preview[i+k])>1e-7);if(!mask.contains(p)){outside++;assert.equal(changed,false,'VR sculpt must preserve every vertex outside native lasso mask');}else if(changed)changedInside++;}
 assert.ok(outside>0&&changedInside>0);assert.equal(f.api.sculptEnd().changed,true);assert.deepEqual(positions(f),preview);assert.deepEqual(f.counts(),{checkpoints:2,changes:2});
 const sculpted=clone(f.document());f.step(true);assert.deepEqual(clone(f.document()),saved);f.step(false);assert.deepEqual(clone(f.document()),sculpted);
 assert.equal(f.api.sculptBegin('sphere',{radius:.8}).ok,true);f.api.sculptUpdate({center:[0,0,-.5],normal:[0,0,-1],dt:.05});assert.equal(f.api.sculptEnd().changed,false,'A front surface region must not edit matching back-side footprint');
 assert.equal(f.api.lassoSelect('sphere',null).ok,true);assert.equal(f.api.inspect().selectedRegionId,null);assert.equal(f.api.sculptBegin('sphere',{radius:.8}).regionId,null);f.api.cancel();checks++;
}
{
 const f=fixture(),before=clone(f.document());f.redo.push({preserved:true});assert.equal(f.api.lassoBegin('sphere').ok,true);f.api.lassoUpdate([0,0,.5]);f.api.lassoUpdate([.1,0,.5]);assert.equal(f.api.lassoEnd(false).cancelled,true);assert.deepEqual(clone(f.document()),before);assert.equal(f.redo.length,1);
 assert.equal(lasso(f,[[0,0,.45],[.3,.3,.45],[0,.3,.45],[.3,0,.45]]).ok,false);assert.deepEqual(f.counts(),{checkpoints:0,changes:0});assert.deepEqual(clone(f.document()),before);
 assert.equal(lasso(f,[[2,2,2],[2.5,2,2],[2.5,2.5,2],[2,2.5,2]]).reason,'LASSO_PIN_MISSED_SURFACE');assert.equal(f.root.children.some(m=>m.children.some(c=>c.isLine)),false);
 assert.equal(f.api.lassoSelect('sphere','missing').ok,false);checks++;
}
{
 const f=fixture({skin:true});assert.equal(lasso(f).ok,true);const before=clone(f.document());assert.equal(f.api.lassoBegin('sphere').ok,true);f.api.lassoUpdate([0,0,.5]);const live=f.root.children.find(m=>m.isSkinnedMesh);live.skeleton.bones[0].rotation.y=.4;live.skeleton.bones[0].updateMatrixWorld(true);assert.equal(f.api.lassoEnd().ok,false);assert.deepEqual(clone(f.document()),before);assert.deepEqual(f.counts(),{checkpoints:1,changes:1});checks++;
}

console.log(JSON.stringify({ok:true,checks,operations:['push','smooth','flatten','inflate','pinch','translate'],nativeUndo:true,outlineFace:true,closedPositiveNegativeExtrusion:true,bindPoseSkinnedSculpt:true,posedSkinRejected:true,bindPoseOutlineExtrusion:true,nativeLassoPins:true,lassoConstrainedSculpt:true}));
