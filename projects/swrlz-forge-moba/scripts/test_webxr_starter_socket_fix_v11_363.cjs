#!/usr/bin/env node
// Focused four-starter native project opening test. No browser/network dependencies.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const native=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-prism-jester.swyrl.json'),'utf8'));
// Earlier engine patches extend the canonical model with old named-socket references.
native.project.modelAtelier.assemblies={sockets:[{partId:'deleted-prism-part',name:'wrist'}]};
const status={open:false,workspace:'game',messages:[],loaded:null};
const host={
 console,URL,Object,Map,structuredClone,requestAnimationFrame:()=>0,
 dirty:false,confirm:()=>true,currentProject:{kind:'sandbox'},
 MODEL_ATELIER_CANONICAL_PROJECT:native,
 window:{
  SWYRL_ENGINE_MODEL_ATELIER:{view:()=>{}},
  SWYRL_ENGINE_WORKSPACES:{active:()=>status.workspace},
  SWYRL_ENGINE_STUDIOS:{active:()=>status.workspace,change:(mode)=>{status.workspace=mode;return true;}}
 },
 document:{
  readyState:'loading',baseURI:'https://kamiloki-swrlz-forge-moba.static.hf.space/modeler.html',
  addEventListener:()=>{},querySelector:()=>null,
  getElementById:()=>({classList:{remove:()=>{}}})
 },
 ModelAtelier:{
  close(){status.open=false;},syncProject(){},
  status(){return {open:status.open,count:host.currentProject?.modelAtelier?.parts?.length||0};}
 },
 createProjectFromTemplate:()=>false,
 se232ActivateSelectedModelWorkspace(){status.open=true;status.workspace='modeler';},
 loadProject(scene){
  assert(Array.isArray(scene.scene.actors));
  assert.equal(scene.project.kind,'model-atelier');
  assert.equal(scene.project.modelAtelier.assemblies,null,'Inherited named sockets must be cleared before native load');
  host.currentProject=structuredClone(scene.project);
  status.loaded=scene;
 },
 initializeHistory:()=>{},markSaved:()=>{},toast:m=>status.messages.push(m),
 requestAnimationFrame:()=>0,
 async fetch(url){
  const pathname=typeof url==='string'?url:new URL(url).pathname;
  const relative=pathname.replace(/^.*?(assets\/models\/)/,'$1');
  const full=path.resolve(root,relative);
  if(!full.startsWith(path.join(root,'assets','models')+path.sep)||!fs.existsSync(full))
   return {ok:false,status:404};
  return {ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(full,'utf8'))};
 }
};
vm.createContext(host);
// The v11.363 append-only patch changes the assembled HTML, not historical
// v11.358/v11.361 runtime files. Apply its exact scoped replacements to these
// two isolated runtime fragments so this pure Node test exercises the shipped logic.
const transforms={
 'webxr_reference_hand_starters_v11_358.js':[
  [" m.meshGroups=[];m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';",
   " m.meshGroups=[];m.assemblies=null;m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';"]
 ],
 'webxr_model_starters_v11_361.js':[
  [" model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';",
   " model.assemblies=null;model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';"],
  ["  const parts=source?.project?.modelAtelier?.parts;",
   "  if(source?.project?.modelAtelier)source.project.modelAtelier.assemblies=null;\\n  const parts=source?.project?.modelAtelier?.parts;"]
 ]
};
for(const name of ['webxr_reference_hand_starters_v11_358.js','webxr_model_starters_v11_361.js']){
 let script=fs.readFileSync(path.join(root,'runtime',name),'utf8');
 for(const [before,after] of transforms[name]){
  assert.equal(script.split(before).length,2,'missing expected v11.363 transform anchor in '+name);
  script=script.replace(before,after);
 }
 vm.runInContext(script,host,{filename:name});
}
(async()=>{
  const api=host.window.SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361;
  for(const id of ['webxr-hand-left','webxr-hand-right','webxr-touch-left','webxr-touch-right']){
   const ok=await api.open(id,true);
   assert.equal(ok,true,id+' failed: '+status.messages.at(-1));
   assert.equal(status.workspace,'modeler');
   assert.equal(status.open,true);
   const m=status.loaded.project.modelAtelier;
   assert.equal(status.loaded.project.template,id);
   assert.equal(status.loaded.project.kind,'model-atelier');
   assert.equal(m.parts.length,id.includes('hand')?1:7);
   for(const part of m.parts){
    assert.equal(part.kind,'topologyMesh');
    assert(part.topologyMesh.positions.length>9);
    assert.equal(part.topologyMesh.uvs.length,part.topologyMesh.positions.length/3*2);
    assert.equal(part.topologyMesh.indices.length%3,0);
    assert(part.topologyMesh.positions.length/3<=9000);
    assert(part.topologyMesh.indices.length/3<=16000);
    assert(Math.max(...part.topologyMesh.indices)<part.topologyMesh.positions.length/3);
    if(id.includes('touch'))assert(part.uvPaintPNG.length<360000);
   }
   if(id.includes('touch')){
    assert.equal(m.meshGroups.length,1);
    assert.equal(m.meshGroups[0].members.length,7);
   }else assert.equal(m.referenceJoints.length,25);
   assert(!api.status().busy);
   process.stdout.write(id+': '+m.parts.length+' editable native mesh part(s); route '+status.workspace+' OK\n');
  }
  assert.equal(await api.open('unknown',true),false);
  process.stdout.write('4/4 starter load and validation workflows PASS\n');
})().catch(err=>{console.error(err);process.exitCode=1;});
