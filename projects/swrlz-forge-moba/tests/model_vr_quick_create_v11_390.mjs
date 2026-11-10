#!/usr/bin/env node
// Native transaction checks with the real Three math and the native primitive
// factory/core part validator, not a second implementation of VR creation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath, pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_quick_create_v11_390.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_vr_quick_create_v11_390.js'),'utf8');
const nativeSource=fs.readFileSync(path.join(ROOT,'runtime/model_atelier.js'),'utf8');
function nativeFunction(name){const start=nativeSource.indexOf('function '+name+'(');assert(start>=0);let at=nativeSource.indexOf('{',start),depth=1;for(at++;depth;at++){if(nativeSource[at]==='{')depth++;else if(nativeSource[at]==='}')depth--;}return nativeSource.slice(start,at);}
const nativeCore=nativeFunction('checkPart')+'\n'+nativeFunction('geometry').replace('function geometry(','function atelierCourierBaseGeometry(');
const clone=value=>structuredClone(value);
const plain=value=>JSON.parse(JSON.stringify(value));
const same=(actual,expected,message)=>assert.deepEqual(plain(actual),plain(expected),message);
const part=(id='part-a',kind='box')=>({id,name:'Existing '+id,kind,position:[.2,.4,-.1],rotation:[.1,0,.3],scale:[.5,.6,.7],color:'#aa77cc',material:'matte',group:'Existing'});
function fixture(parts=[part(),part('part-b','sphere')],{limit=400,assemblies={}}={}){
 let document={name:'Native model',parts:clone(parts)},token=1,revision=0,uuid=0,checkpoints=0,changes=0,factoryCalls=0;
 const world=new THREE.Scene(),root=new THREE.Group();world.add(root);root.position.set(.7,1.2,-.4);root.rotation.set(.1,.2,.3);root.scale.set(.8,1.3,1.1);
 const undo=[],redo=[];
 const ctx={THREE,structuredClone,crypto:{randomUUID:()=>String(++uuid).padStart(32,'0')},MODEL_ATELIER_LIMIT:limit,
  MODEL_ATELIER_KINDS:['sphere','box','cylinder','cone','topologyMesh','loft'],MODEL_ATELIER_MATERIALS:['matte','silk','gloss','metal','emissive'],
  panel:{hidden:false},modelRoot:root,world,selection:parts[0]?.id||null,atelierMeshIds:parts[0]?[parts[0].id]:[],
  model:()=>document,partById:id=>document.parts.find(p=>p.id===id),nativeGesture:null,groupGesture:null,surfaceGesture:null,
  checkpoint:()=>{undo.push(clone(document));redo.length=0;checkpoints++;},
  close:()=>{ctx.panel.hidden=true;return 'native-close';},
 };
 vm.createContext(ctx);vm.runInContext(nativeCore,ctx);
 const nativeFactory=ctx.atelierCourierBaseGeometry;
 ctx.atelierCourierBaseGeometry=p=>{factoryCalls++;return nativeFactory(p);};
 function render(){
  for(const mesh of [...root.children]){root.remove(mesh);mesh.geometry.dispose();mesh.material.dispose();}
  for(const p of document.parts){
   const mesh=new THREE.Mesh(nativeFactory(p),new THREE.MeshStandardMaterial());mesh.userData.atelierId=p.id;
   mesh.position.fromArray(p.position);mesh.rotation.set(...p.rotation);mesh.scale.fromArray(p.scale);mesh.updateMatrix();
   const assembly=assemblies[p.group];if(assembly){mesh.matrix.premultiply(assembly);mesh.matrixAutoUpdate=false;}
   root.add(mesh);
  }
  root.updateWorldMatrix(true,true);revision++;
 }
 ctx.signalEdited=()=>{changes++;render();};
 ctx.se340ModelBridge={inspect:()=>({open:!ctx.panel.hidden,documentToken:token,revision,gesture:ctx.nativeGesture}),
  projection:()=>({ready:true,meshes:root.children.map(mesh=>({id:mesh.userData.atelierId,mesh}))})};
 ctx.se350ModelTools={inspect:()=>({gesture:ctx.groupGesture}),syncSelection:()=>{
  assert(ctx.atelierMeshIds.every(id=>document.parts.some(p=>p.id===id)));ctx.selection=ctx.atelierMeshIds.at(-1)||null;
 }};
 ctx.se350ModelSurface={inspect:()=>({active:ctx.surfaceGesture})};
 render();vm.runInContext(source+'\nglobalThis.api=se390ModelCreate;',ctx);
 return {ctx,api:ctx.api,root,world,undo,redo,document:()=>document,counts:()=>({checkpoints,changes,factoryCalls}),
  render,replace:next=>{document=clone(next);token++;render();},reparentRoot:()=>{ctx.modelRoot=new THREE.Group();},
  step:back=>{const from=back?undo:redo,to=back?redo:undo;if(!from.length)return;to.push(clone(document));document=from.pop();ctx.selection=null;ctx.atelierMeshIds=[];render();}};
}
let groups=0;
for(const [kind,geometryType] of [['box','BoxGeometry'],['sphere','SphereGeometry'],['cylinder','CylinderGeometry'],['cone','ConeGeometry']]){
 const f=fixture(),before=clone(f.document()),draft=f.api.draft(kind),start=f.counts();
 assert.equal(draft.ok,true);assert.equal(draft.kind,kind);assert.equal(f.ctx.checkPart(draft.part),true);
 const preview=f.api.previewGeometry(draft);assert.equal(preview.ok,true);assert.equal(preview.geometry.type,geometryType);assert.equal(f.counts().factoryCalls,start.factoryCalls+1);
 let disposed=0;preview.geometry.addEventListener('dispose',()=>disposed++);f.api.cancel(draft);assert.equal(disposed,0,'Caller owns the returned preview geometry');preview.geometry.dispose();assert.equal(disposed,1);
 same(f.document(),before);assert.equal(f.counts().checkpoints,0);assert.equal(f.counts().changes,0);groups++;
}
{
 const f=fixture(),before=clone(f.document()),draft=f.api.draft('box',{name:'New block',color:'#1188aa',material:'silk'});
 draft.part.position=[1,2,-3];draft.part.rotation=[.2,-.1,.4];draft.part.scale=[.3,.4,.5];
 const expected=clone(draft.part),result=f.api.commit(draft,draft.documentToken);assert.equal(result.ok,true);assert.equal(result.changed,true);
 assert.notEqual(result.id,expected.id);same(result.ids,[result.id]);const actual=f.document().parts.at(-1);expected.id=result.id;
 same(actual,expected);assert.equal(f.ctx.checkPart(actual),true);same(f.ctx.atelierMeshIds,[result.id]);assert.equal(f.ctx.selection,result.id);
 assert.equal(f.counts().checkpoints,1);assert.equal(f.counts().changes,1);const saved=clone(f.document());
 assert.equal(f.api.commit(draft).ok,false,'A confirmed draft is single use');assert.equal(f.counts().checkpoints,1);
 f.step(true);same(f.document(),before);f.step(false);same(f.document(),saved);groups++;
}
{
 const f=fixture(),before=clone(f.document());f.redo.push({history:'keep'});
 const draft=f.api.draft('sphere');draft.part.position=[.3,.7,.2];assert.equal(f.api.cancel(draft,'B canceled').cancelled,true);
 assert.equal(f.api.inspect().pending,null);assert.equal(f.api.commit(draft).ok,false);same(f.document(),before);assert.equal(f.redo.length,1);assert.equal(f.counts().checkpoints,0);
 const a=f.api.draft('box'),b=f.api.draft('cone');assert.equal(f.api.cancel(a).cancelled,false);assert.equal(f.api.inspect().pending.kind,'cone');assert.equal(f.api.commit(a).ok,false);assert.equal(f.api.commit(b).ok,true);groups++;
}
{
 const f=fixture(),before=clone(f.document());
 for(const [kind,options] of [['invented',{}],['sphere',{scale:[0,1,1]}],['box',{scale:[21,1,1]}],['cone',{position:[NaN,0,0]}],['sphere',{position:[101,0,0]}],['sphere',{color:'red'}],['box',{material:'plastic'}],['sphere',{name:''}],['sphere',{name:'n'.repeat(101)}],['box',{scale:()=>1}]]){
  assert.equal(f.api.draft(kind,options).ok,false,kind+JSON.stringify(options));
 }
 const d=f.api.draft('box');d.part.kind='sphere';assert.equal(f.api.previewGeometry(d).ok,false);assert.equal(f.api.commit(d).ok,false);
 d.part.kind='box';d.part.position=[Infinity,0,0];assert.equal(f.api.commit(d).ok,false);d.part.position=[0,0,0];d.part.name={malformed:true};assert.equal(f.api.commit(d).ok,false);
 assert.equal(f.api.commit({ok:true,part:part('forged')}).ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);groups++;
}
{
 const f=fixture(),draft=f.api.draft('cylinder');f.redo.push({keep:true});f.document().parts[0].color='#123456';
 assert.equal(f.api.commit(draft).ok,false,'Unannounced source edits invalidate confirmation');assert.equal(f.document().parts[0].color,'#123456');assert.equal(f.api.inspect().pending,null);assert.equal(f.redo.length,1);assert.equal(f.counts().checkpoints,0);
 const next=f.api.draft('box');f.render();assert.equal(f.api.commit(next).ok,false,'Native rebuild invalidates a stale draft');groups++;
}
{
 const f=fixture(),draft=f.api.draft('cone');f.replace({name:'Replacement',parts:[part('replacement')]});const before=clone(f.document());
 assert.equal(f.api.commit(draft).ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);
 const d=f.api.draft('sphere');assert.equal(f.api.commit(d,d.documentToken+1).ok,false);assert.equal(f.api.inspect().pending,null);groups++;
}
{
 const f=fixture(),before=clone(f.document());
 for(const flag of ['nativeGesture','groupGesture','surfaceGesture']){f.ctx[flag]={active:true};assert.equal(f.api.draft('box').ok,false);assert.equal(f.api.duplicate(['part-a']).ok,false);f.ctx[flag]=null;}
 const d=f.api.draft('box');f.ctx.groupGesture={active:true};assert.equal(f.api.commit(d).ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);f.ctx.groupGesture=null;assert.equal(f.api.commit(d).ok,true);groups++;
}
{
 const complex=part('part-a','topologyMesh');Object.assign(complex,{textureBinding:{set:'astra-4k',tile:'fur',normalStrength:.7},uvPaint:'data:image/png;base64,AA==',uvPaintOffset:[.1,-.2],
  topologyMesh:{positions:[0,0,0,1,0,0,0,1,0],uvs:[0,0,1,0,0,1],indices:[0,1,2]},sculptVertexEdits:[{indices:[0],moves:[[.1,0,0]],resolution:'source'}],rigWeights:{thumb:[.7,.3]}});
 const f=fixture([complex,part('part-b','loft')]),before=clone(f.document());const result=f.api.duplicate(['part-a','part-b'],{translation:[.12,-.04,.08]});assert.equal(result.ok,true);assert.equal(result.ids.length,2);
 assert.equal(f.counts().checkpoints,1);assert.equal(f.counts().changes,1);same(f.ctx.atelierMeshIds,result.ids);assert.equal(f.ctx.selection,result.ids[1]);
 for(let i=0;i<2;i++){const original=before.parts[i],copy=f.document().parts[i+2],expected=clone(original);expected.id=copy.id;expected.name=original.name+' copy';expected.position=original.position.map((v,k)=>v+[.12,-.04,.08][k]);same(copy,expected);assert.notEqual(copy.id,original.id);}
 same(f.document().parts.slice(0,2),before.parts);assert.notEqual(f.document().parts[2].topologyMesh,complex.topologyMesh);
 const saved=clone(f.document());f.step(true);same(f.document(),before);f.step(false);same(f.document(),saved);f.document().parts[2].topologyMesh.uvs[0]=.4;assert.equal(f.document().parts[0].topologyMesh.uvs[0],0);groups++;
}
{
 const a=part();a.group='Animated assembly';a.rotation=[Math.PI*2+.2,-.1,.3];const b=part('part-b');b.group='Animated assembly';
 const assembly=new THREE.Matrix4().compose(new THREE.Vector3(3,.8,-2),new THREE.Quaternion().setFromEuler(new THREE.Euler(.2,.4,-.15)),new THREE.Vector3(.8,1.6,1.2));
 const f=fixture([a,b],{assemblies:{'Animated assembly':assembly}}),before=f.root.children.map(mesh=>new THREE.Vector3().setFromMatrixPosition(mesh.matrix)),delta=new THREE.Vector3(.15,-.08,.11);
 const result=f.api.duplicate(['part-a','part-b'],delta.toArray());assert.equal(result.ok,true);assert.equal(f.counts().checkpoints,1);
 for(let i=0;i<2;i++){const copy=f.document().parts[i+2],actual=new THREE.Vector3().setFromMatrixPosition(f.root.children[i+2].matrix);assert(actual.distanceTo(before[i].clone().add(delta))<1e-10);same(copy.rotation,[a,b][i].rotation,'Native Euler representation remains exact');same(copy.scale,[a,b][i].scale);assert.equal(copy.group,'Animated assembly');}
 groups++;
}
{
 const f=fixture([part(),part('part-b')],{limit:3}),before=clone(f.document()),ids=[...f.ctx.atelierMeshIds];f.redo.push({keep:true});
 assert.equal(f.api.duplicate(['part-a','part-b']).ok,false);same(f.document(),before);same(f.ctx.atelierMeshIds,ids);assert.equal(f.redo.length,1);
 for(const selection of [[],['missing'],['part-a','part-a'],Array.from({length:33},(_,i)=>'part-'+i)])assert.equal(f.api.duplicate(selection).ok,false);
 for(const translation of [[NaN,0,0],[101,0,0],[0,0]])assert.equal(f.api.duplicate(['part-a'],{translation}).ok,false);
 assert.equal(f.api.duplicate(['part-a'],{documentToken:99}).ok,false);assert.equal(f.api.duplicate(['part-a'],{translation:[100,0,0]}).ok,false);assert.equal(f.counts().checkpoints,0);
 const full=fixture([part()],{limit:1});assert.equal(full.api.draft('box').ok,false);assert.equal(full.counts().checkpoints,0);groups++;
}
{
 const a=part();a.group='Broken';const f=fixture([a],{assemblies:{Broken:new THREE.Matrix4().makeScale(0,1,1)}}),before=clone(f.document());assert.equal(f.api.duplicate(['part-a']).ok,false);same(f.document(),before);assert.equal(f.counts().checkpoints,0);groups++;
}
{
 const f=fixture(),d=f.api.draft('box'),preview=f.api.previewGeometry(d);assert.equal(preview.ok,true);assert.equal(f.ctx.close(),'native-close');assert.equal(f.api.inspect().pending,null);assert.equal(f.api.commit(d).ok,false);assert.equal(f.api.draft('sphere').ok,false);assert.equal(f.api.previewGeometry(d).ok,false);assert.equal(f.counts().checkpoints,0);preview.geometry.dispose();groups++;
}
console.log('MODEL_VR_QUICK_CREATE_V11_390_PASS',JSON.stringify({groups,three:THREE.REVISION,primitiveKinds:4,nativeFactory:true,transactions:'one checkpoint',duplicate:'full native source/UV/material/group preserved'}));
