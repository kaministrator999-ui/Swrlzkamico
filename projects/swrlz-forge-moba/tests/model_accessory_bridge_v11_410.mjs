#!/usr/bin/env node
// Native topology validators/factory and real Three math exercise the batch
// transaction, not a mirrored accessory or history implementation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_accessory_bridge_v11_410.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const read=name=>fs.readFileSync(path.join(ROOT,'runtime',name),'utf8');
const nativeSource=read('model_atelier.js'),bridge=read('model_accessory_bridge_v11_410.js'),recipe=read('model_accessory_geometry_v11_410.js');
function nativeFunction(name){const start=nativeSource.indexOf('function '+name+'(');assert(start>=0);let at=nativeSource.indexOf('{',start),depth=1;for(at++;depth;at++){if(nativeSource[at]==='{')depth++;else if(nativeSource[at]==='}')depth--;}return nativeSource.slice(start,at);}
const core=nativeFunction('checkPart').replace('function checkPart(','function nativeCheckPart(')+'\n'+nativeFunction('geometry').replace('function geometry(','function nativePrimitiveGeometry(');
const clone=value=>structuredClone(value),plain=value=>JSON.parse(JSON.stringify(value));
const same=(a,b,message)=>assert.deepEqual(plain(a),plain(b),message);
const original=(id='source-a')=>({id,name:'Original mesh',kind:'box',group:'Existing character',position:[.1,.2,.3],rotation:[.3,-.1,.5],scale:[.7,.9,.6],color:'#8877aa',material:'matte',
 textureBinding:{set:'astra-4k',tile:'leather',normalStrength:.6},uvPaint:'data:image/png;base64,AA==',uvPaintOffset:[.15,-.2],rigWeights:{hip:[.3,.7]}});
function fixture({parts=[original()],limit=400}={}){
 let document={name:'Original character',parts:clone(parts),extra:{rig:{pose:[1,2,3]},textures:['preserve']}},token=1,revision=0,uuid=0,checkpoints=0,changes=0,factoryCalls=0;
 const root=new THREE.Group(),world=new THREE.Scene(),undo=[],redo=[],allocated=[];world.add(root);
 root.position.set(.3,1.1,-.4);root.rotation.set(.2,.1,.3);root.scale.set(.8,1.1,1.4);
 const ctx={THREE,structuredClone,crypto:{randomUUID:()=>String(++uuid).padStart(32,'0')},MODEL_ATELIER_LIMIT:limit,
  MODEL_ATELIER_KINDS:['sphere','box','cylinder','cone'],MODEL_ATELIER_MATERIALS:['matte','silk','gloss','metal','emissive'],
  modelRoot:root,world,selection:parts[0]?.id||null,atelierMeshIds:parts[0]?[parts[0].id]:[],panel:{hidden:false},
  model:()=>document,partById:id=>document.parts.find(p=>p.id===id),nativeGesture:null,groupGesture:null,surfaceGesture:null,createPending:null,
  checkpoint:()=>{undo.push(JSON.stringify(document.parts));redo.length=0;checkpoints++;},close:()=>{ctx.panel.hidden=true;return 'native-close';}};
 vm.createContext(ctx);vm.runInContext(core+'\n'+read('model_atelier_topology_lod_v11_38.js'),ctx);
 ctx.checkPart=p=>ctx.nativeCheckPart(p)&&ctx.atelierTopologyValid(p);
 const nativeFactory=p=>p.kind==='topologyMesh'?ctx.atelierTopologyGeometry(p):ctx.nativePrimitiveGeometry(p);
 ctx.atelierCourierBaseGeometry=p=>{factoryCalls++;if(ctx.factoryFaultAt===factoryCalls)throw Error('factory unavailable');const g=nativeFactory(p);allocated.push(g);return g;};
 function render(){
  for(const m of [...root.children]){root.remove(m);m.geometry.dispose();m.material.dispose();}
  for(const p of document.parts){const m=new THREE.Mesh(nativeFactory(p),new THREE.MeshStandardMaterial());m.userData.atelierId=p.id;m.position.fromArray(p.position);m.rotation.set(...p.rotation);m.scale.fromArray(p.scale);root.add(m);}
  root.updateWorldMatrix(true,true);revision++;
 }
 ctx.signalEdited=()=>{changes++;render();};
 ctx.se340ModelBridge={inspect:()=>({open:!ctx.panel.hidden,documentToken:token,revision,gesture:ctx.nativeGesture})};
 ctx.se350ModelTools={inspect:()=>({gesture:ctx.groupGesture}),syncSelection:()=>{assert(ctx.atelierMeshIds.every(id=>document.parts.some(p=>p.id===id)));ctx.selection=ctx.atelierMeshIds.at(-1)||null;}};
 ctx.se350ModelSurface={inspect:()=>({active:ctx.surfaceGesture})};ctx.se390ModelCreate={inspect:()=>({pending:ctx.createPending})};
 render();vm.runInContext(recipe+'\n'+bridge+'\nglobalThis.api=se410ModelAccessory;',ctx);
 return {ctx,api:ctx.api,root,world,undo,redo,allocated,render,document:()=>document,counts:()=>({checkpoints,changes,factoryCalls}),
  replace:next=>{document=clone(next);token++;render();},
  step:back=>{const from=back?undo:redo,to=back?redo:undo;if(!from.length)return;to.push(JSON.stringify(document.parts));document.parts=JSON.parse(from.pop());ctx.selection=null;ctx.atelierMeshIds=[];render();}};
}
let groups=0;
{
 const f=fixture(),before=clone(f.document()),d=f.api.draft(),preview=f.api.preview(d);
 assert.equal(d.ok,true);assert(Object.isFrozen(d));assert(Object.isFrozen(d.parameters));assert(Object.isFrozen(d.transform));
 assert.equal(preview.ok,true);assert(preview.parts.length>=5&&preview.parts.length<=32);assert.equal(f.counts().factoryCalls,preview.parts.length);
 for(const {part,geometry} of preview.parts){assert.equal(part.kind,'topologyMesh');assert.equal(f.ctx.checkPart(part),true);assert(geometry.isBufferGeometry);assert.equal(geometry.attributes.position.count,part.topologyMesh.positions.length/3);assert.equal(geometry.index.count,part.topologyMesh.indices.length);same([...geometry.attributes.uv.array],part.topologyMesh.uvs.map(Math.fround));assert.equal(f.root.children.some(m=>m.geometry===geometry),false,'Ghosts stay outside the native projection');}
 let disposed=0;for(const p of preview.parts)p.geometry.addEventListener('dispose',()=>disposed++);
 same(f.document(),before);assert.equal(f.counts().checkpoints,0);f.api.cancel(d);assert.equal(disposed,0,'Returned preview geometries belong to the caller');for(const p of preview.parts)p.geometry.dispose();assert.equal(disposed,preview.parts.length);groups++;
}
{
 const f=fixture(),before=clone(f.document()),d=f.api.draft({width:.72,height:.81,emblem:'leaf'},{position:[.5,.7,-.2],rotation:[.15,-.3,.25],scale:[.6,.6,.6]});
 const preview=f.api.preview(d),expected=preview.parts.map(p=>clone(p.part));for(const p of preview.parts)p.geometry.dispose();
 const result=f.api.commit(d,d.documentToken);assert.equal(result.ok,true);assert.equal(f.counts().checkpoints,1);assert.equal(f.counts().changes,1);assert.equal(result.ids.length,expected.length);
 const committed=f.document().parts.slice(before.parts.length);same(f.document().parts.slice(0,before.parts.length),before.parts);same(f.document().extra,before.extra);
 assert.equal(new Set(committed.map(p=>p.group)).size,1);assert.equal(new Set(result.ids).size,expected.length);same(f.ctx.atelierMeshIds,result.ids);assert.equal(f.ctx.selection,result.ids.at(-1));
 const allowed=['id','name','kind','group','position','rotation','scale','color','material','topologyMesh'].sort();
 for(let i=0;i<committed.length;i++){assert.notEqual(committed[i].id,expected[i].id);expected[i].id=committed[i].id;same(committed[i],expected[i]);assert.equal(f.ctx.checkPart(committed[i]),true);same(Object.keys(committed[i]).sort(),allowed);}
 const saved=clone(f.document());assert.equal(f.api.commit(d).ok,false);assert.equal(f.counts().checkpoints,1);f.step(true);same(f.document(),before);f.step(false);same(f.document(),saved);
 const exported=JSON.stringify(f.document()),imported=JSON.parse(exported);assert(imported.parts.every(p=>f.ctx.checkPart(p)));same(imported,saved,'Portable native source/UV/material descriptors round trip without recipe fields');
 result.parts[0].topologyMesh.positions[0]=99;assert.notEqual(committed[0].topologyMesh.positions[0],99,'Commit result does not alias saved topology');groups++;
}
{
 const f=fixture(),before=clone(f.document());f.redo.push('unchanged history');const a=f.api.draft();a.transform.position[1]=.9;
 const b=f.api.rebuild(a,{width:1.1,depth:.42,detail:false,emblem:'star'});assert.equal(b.ok,true);same(b.transform.position,[0,.9,0]);assert.equal(b.documentToken,a.documentToken);assert.equal(f.api.commit(a).ok,false);
 assert.equal(f.api.rebuild(b,{width:NaN}).ok,false);assert.equal(f.api.inspect().pending.count>0,true,'Bad parameter updates retain a valid preview');
 assert.equal(f.api.cancel(b,'User canceled').cancelled,true);assert.equal(f.api.inspect().pending,null);same(f.document(),before);assert.equal(f.redo.length,1);assert.equal(f.counts().checkpoints,0);groups++;
}
{
 const f=fixture(),before=clone(f.document());
 for(const transform of [{position:[NaN,0,0]},{rotation:[101,0,0]},{scale:[1,2,1]},{scale:[0,0,0]},{scale:[21,21,21]},{scale:[()=>1,1,1]}])assert.equal(f.api.draft({},transform).ok,false);
 for(const params of [{width:NaN},{bodyColor:'red'},{emblem:'invented'}])assert.equal(f.api.draft(params).ok,false);
 assert.equal(f.api.commit({ok:true,documentToken:1}).ok,false);const d=f.api.draft();d.transform.position[0]=Infinity;assert.equal(f.api.preview(d).ok,false);assert.equal(f.api.commit(d).ok,false);d.transform.position[0]=0;d.transform.scale[1]=.5;assert.equal(f.api.commit(d).ok,false);
 same(f.document(),before);assert.equal(f.counts().checkpoints,0);groups++;
}
{
 const f=fixture(),d=f.api.draft();f.redo.push('keep');f.document().parts[0].rigWeights.hip[0]=.5;assert.equal(f.api.commit(d).ok,false);assert.equal(f.api.inspect().pending,null);assert.equal(f.document().parts[0].rigWeights.hip[0],.5);assert.equal(f.redo.length,1);assert.equal(f.counts().checkpoints,0);
 const e=f.api.draft();f.render();assert.equal(f.api.rebuild(e,{width:1}).ok,false);groups++;
}
{
 for(const mutation of [f=>f.document().parts.reverse(),f=>{f.document().parts=[...f.document().parts];},f=>{f.ctx.modelRoot=new THREE.Group();}]){
  const f=fixture({parts:[original(),original('source-b')]}),d=f.api.draft();mutation(f);assert.equal(f.api.commit(d).ok,false);assert.equal(f.counts().checkpoints,0);
 }
 const f=fixture(),d=f.api.draft();f.replace({name:'Replacement',parts:[original('replacement')],extra:{}});const before=clone(f.document());assert.equal(f.api.commit(d).ok,false);same(f.document(),before);
 const e=f.api.draft();assert.equal(f.api.commit(e,e.documentToken+1).ok,false);assert.equal(f.api.inspect().pending,null);groups++;
}
{
 const f=fixture(),before=clone(f.document());
 for(const key of ['nativeGesture','groupGesture','surfaceGesture','createPending']){f.ctx[key]={active:true};assert.equal(f.api.draft().ok,false);f.ctx[key]=null;}
 const d=f.api.draft();f.ctx.groupGesture={active:true};assert.equal(f.api.commit(d).ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);f.ctx.groupGesture=null;assert.equal(f.api.commit(d).ok,true);groups++;
}
{
 const probe=fixture(),p=probe.api.draft(),count=probe.api.inspect().pending.count;probe.api.cancel(p);
 const f=fixture({limit:count}),before=clone(f.document());f.redo.push('keep');assert.equal(f.api.draft().ok,false);same(f.document(),before);assert.equal(f.redo.length,1);assert.equal(f.counts().checkpoints,0);
 const exact=fixture({limit:count+1}),d=exact.api.draft();assert.equal(exact.api.commit(d).ok,true);assert.equal(exact.document().parts.length,count+1);groups++;
}
{
 const f=fixture(),d=f.api.draft();f.ctx.factoryFaultAt=3;let disposed=0;
 const native=f.ctx.atelierCourierBaseGeometry;f.ctx.atelierCourierBaseGeometry=p=>{const g=native(p);g.addEventListener('dispose',()=>disposed++);return g;};
 assert.equal(f.api.preview(d).ok,false);assert.equal(disposed,2,'A partial native preview failure disposes every allocated ghost');assert.equal(f.counts().checkpoints,0);assert.equal(f.api.inspect().pending.count>0,true);groups++;
}
{
 const f=fixture(),before=clone(f.document()),d=f.api.draft(),preview=f.api.preview(d);let disposed=0;preview.parts[0].geometry.addEventListener('dispose',()=>disposed++);
 preview.parts[0].part.topologyMesh.positions[0]=99;preview.parts[0].part.color='#000000';const again=f.api.preview(d);assert.notEqual(again.parts[0].part.topologyMesh.positions[0],99);assert.notEqual(again.parts[0].part.color,'#000000');
 for(const p of again.parts)p.geometry.dispose();assert.equal(f.ctx.close(),'native-close');assert.equal(f.api.inspect().pending,null);assert.equal(f.api.commit(d).ok,false);assert.equal(f.api.draft().ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);assert.equal(disposed,0);for(const p of preview.parts)p.geometry.dispose();groups++;
}
console.log('MODEL_ACCESSORY_BRIDGE_V11_410_PASS',JSON.stringify({groups,three:THREE.REVISION,topologyFactory:true,transactions:'one native checkpoint',savedSchema:'ordinary topology parts only',history:'cancel/Undo/Redo preserved'}));
