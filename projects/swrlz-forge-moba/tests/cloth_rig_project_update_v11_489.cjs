/* §E v11.489: cloth rig mathematics + version-bound selected-card updates. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const load=name=>fs.readFileSync(path.join(root,'runtime',name),'utf8');
const zero=id=>Object.fromEntries(id.map(k=>[k,[0,0,0]]));
const ids=['root','crown','brow','mouth'],bones=[
 {id:'root',label:'Root',parent:null,rest:[0,0,0]},
 {id:'crown',label:'Crown',parent:'root',rest:[0,1,0]},
 {id:'brow',label:'Brow',parent:'crown',rest:[0,1.8,.5]},
 {id:'mouth',label:'Mouth',parent:'crown',rest:[0,1.1,.7]}
],envelopes=[
 {bone:'crown',center:[0,1,0],radii:[1,2,1],strength:.75},
 {bone:'brow',center:[0,1.8,.5],radii:[.4,.3,.3],strength:.95},
 {bone:'mouth',center:[0,1.1,.7],radii:[.4,.3,.3],strength:.95}
];
const clip=(label,mouth=0)=>({label,duration:1.5,loop:true,timeline:[
 {time:0,pose:zero(ids)},{time:.75,pose:{...zero(ids),mouth:[mouth,0,0]}},
 {time:1.5,pose:zero(ids)}]});
const rig={schema:'swyrl-cloth-skin-v1',algorithm:'linear-blend-4',
 targetPartId:'sorting-hat-one-sculpt',bones,envelopes,
 duration:1.5,loop:true,pose:zero(ids),
 timeline:clip('Idle').timeline,clips:{idle:clip('Idle'),talk:clip('Talk',.3)},
 activeClip:'idle'};
let edited=0;
const ctx={window:{},se220RigValidate:r=>r?.schema==='swyrl-hand-skin-v1',
 se220RigWeights:()=>({indices:[0,0,0,0],weights:[1,0,0,0]}),
 se220RigTouched:()=>edited++,se220RigControlsInstall:()=>{},
 se220RigRefresh:()=>{},se220RigPose:()=>{},
 se220Rig:()=>rig,se220RigAvailable:()=>true,
 se220Time:0,se220Playing:false,se220R:()=>null,
 model:()=>({rigging:rig}),status:()=>{},
 Object,Array,Math,Date,JSON,structuredClone,console};
vm.createContext(ctx);vm.runInContext(load('model_atelier_cloth_rig_v11_489.js'),ctx);
const api=ctx.window.SWYRL_ENGINE_CLOTH_RIG_489;
assert.equal(api.validate(rig),true,'valid authored rig');
assert.equal(ctx.se220RigValidate({schema:'swyrl-hand-skin-v1'}),true,'legacy hand preserved');
const center=ctx.se220RigWeights([0,1.8,.5],rig);
assert.equal(center.indices.length,4);
assert.ok(Math.abs(Array.from(center.weights).reduce((a,b)=>a+b,0)-1)<1e-9);
assert.ok(center.weights[0]>.8,'brow bone should dominate at brow center');
const outside=ctx.se220RigWeights([10,10,10],rig);
assert.equal(outside.indices[0],0);
assert.ok(outside.weights[0]===1);
const authored=ctx.se489AuthoredSkinWeights({
  topologyMesh:{positions:[0,0,0,0,1,0]},
  skinning:{schema:'swyrl-explicit-skin-v1',indices:[0,2,0,0,0,3,0,0],
    weights:[.15,.85,0,0,.2,.8,0,0]}
},0,rig,[0,1.8,.5]);
assert.equal(authored.indices[1],2,'author-supplied brow influence survives skin bind');
assert.ok(authored.weights[1]>.84);
ctx.se489SelectClip('talk');
assert.equal(rig.activeClip,'talk');
assert.equal(rig.timeline[1].pose.mouth[0],.3);
assert.equal(edited,1);
const broken=structuredClone(rig);
broken.bones[2].parent='nonexistent';
assert.equal(api.validate(broken),false,'missing parent must be rejected');
const scene={project:{name:'The Sorting Hat',instanceId:'saved-id',
 canonicalId:'sorting-hat',kind:'model-atelier',modelAtelier:{
 schema:'swyrl-model-atelier-v1',parts:[{id:'sorting-hat-one-sculpt',kind:'topologyMesh',
 topologyMesh:{positions:[0,0,0,1,0,0,0,1,0],uvs:[0,0,1,0,0,1],indices:[0,1,2]}}]}},
 editor:{},scene:{actors:[]}};
let committed=null,requested=null,confirmCalls=0;
const uctx={window:{
 SWYRL_ENGINE_CLOTH_RIG_489:{validate:r=>r?.schema==='swyrl-cloth-skin-v1'},
 SWYRL_ENGINE_MY_PROJECTS_EXPORT_487:{selectedDocument:async(rec,source)=>({
 id:rec.id,doc:structuredClone(scene),metadata:{id:rec.id,name:'The Sorting Hat',revision:3}})},
 SWYRL_ENGINE_REVISIONS_486:{prepare:async(old,next,revision)=>({payload:{...next,se486History:{schema:'se-project-revisions-v1',entries:[{number:revision}]}}})}
 },
 se184ProjectCard:()=>({querySelector:()=>null}),
 ready:true,se176AccountConnected:true,MAX_RAW:96*1024*1024,
 rpc:async(method,body)=>{assert.equal(method,'cloud.save');requested=body;
  const data=JSON.parse(new TextDecoder().decode(body.bytes));
  assert.equal(data.project.instanceId,'saved-id');
  assert.equal(data.scene.actors.length,0);
  committed=data;return {durable:true,project:{id:'cloud-id',revision:4}};},
 se170Refresh:async()=>{},se175Read:async()=>{},
 se175Store:async()=>{},se175RefreshLocal:async()=>{},
 confirm:()=>{confirmCalls++;return true},
 windowsetTimeout:()=>{},
 document:{createElement:()=>({}),body:{append:()=>{}}},
 TextEncoder,TextDecoder,ArrayBuffer,Date,JSON,Number,Math,structuredClone,console};
vm.createContext(uctx);vm.runInContext(load('my_projects_update_model_v11_489.js'),uctx);
const update=uctx.window.SWYRL_ENGINE_MY_PROJECTS_UPDATE_489;
const imported=structuredClone(scene);
imported.project.instanceId=undefined; // old starter export has no account ID
imported.project.modelAtelier.rigging=structuredClone(rig);
(async()=>{
 const rec={id:'cloud-id',revision:3,name:'The Sorting Hat'};
 const chosen={size:6000,text:async()=>JSON.stringify(imported)};
 const result=await update.updateSelectedModel(rec,'cloud',chosen);
 assert.match(result,/revision 4/);
 assert.equal(requested.projectId,'cloud-id');
 assert.equal(requested.expectedRevision,3);
 assert.equal(requested.name,'The Sorting Hat');
 assert.equal(committed.project.modelAtelier.rigging.bones.length,4);
 assert.equal(committed.se486History.entries[0].number,3);
 const portable={schema:'swyrl-model-atelier-v1',model:imported.project.modelAtelier};
 const portableResult=await update.updateSelectedModel(rec,'cloud',
  {size:100,text:async()=>JSON.stringify(portable)});
 assert.match(portableResult,/revision 4/,'selected card can use model-only rig export');
 assert.equal(confirmCalls,1);
 const wrong=structuredClone(imported);wrong.project.canonicalId='not-sorting-hat';
 await assert.rejects(()=>update.updateSelectedModel(rec,'cloud',
  {size:100,text:async()=>JSON.stringify(wrong)}),/starter identity differs/);
 const stale={schema:'se-model-project-update-v1',target:{
  projectId:'saved-id',accountId:'cloud-id',baseRevision:2},
  model:imported.project.modelAtelier};
 await assert.rejects(()=>update.updateSelectedModel(rec,'cloud',
  {size:100,text:async()=>JSON.stringify(stale)}),/another project or revision/);
 console.log('SE489_CLOTH_RIG_AND_PROJECT_CARD_UPDATE_PASS: 4-weight skin, animated clips, original identity, CAS, revision archive, wrong-project refusal');
})().catch(e=>{console.error(e);process.exitCode=1});
