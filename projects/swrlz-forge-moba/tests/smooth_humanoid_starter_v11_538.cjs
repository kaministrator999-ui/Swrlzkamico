#!/usr/bin/env node
'use strict';
// §E v11.538: execute actual baked-scene loader in a minimal native context.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/smooth_humanoid_starter_v11_538.js'),'utf8');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json'),'utf8'));
new vm.Script(source);
const calls={load:0,close:0,sync:0,view:0,history:0,save:0};
let currentProject=null;
const context={
 URL, console,confirm:()=>true, dirty:false, currentProject,
 document:{baseURI:'https://example.test/',querySelector:()=>({}),
  getElementById:()=>({classList:{remove(){}}})},
 window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change(){throw Error('Unexpected workspace switch')}},
  SWYRL_ENGINE_MODEL_ATELIER:{view:()=>calls.view++}},
 ModelAtelier:{close:()=>calls.close++,syncProject:()=>calls.sync++},
 loadProject:project=>{calls.load++;currentProject=project.project;context.currentProject=currentProject;},
 se232ActivateSelectedModelWorkspace:()=>{},
 initializeHistory:()=>calls.history++,
 markSaved:()=>calls.save++,
 toast:()=>{},
 requestAnimationFrame:f=>f(),
 fetch:async url=>{
  assert.ok(url.includes('model-atelier-futuristic-humanoid-v11-538.swyrl.json'));
  return {ok:true,json:async()=>scene};
 },
 se537OpenMannequin:()=>{throw Error('Legacy 178-piece mesh was not replaced');}
};
vm.createContext(context);
vm.runInContext(source,context,{timeout:3000});
const api=context.window.SWYRL_ENGINE_HUMANOID_538;
const stats=api.validate(scene);
assert.equal(stats.parts,1);
assert.equal(stats.hasAtlas,true);
assert.equal(typeof context.se537OpenMannequin,'function');
(async()=>{
 assert.equal(await context.se537OpenMannequin(true),true);
 assert.equal(calls.load,1);assert.equal(calls.close,1);
 assert.equal(calls.sync,1);assert.equal(calls.history,1);assert.equal(calls.save,1);
 assert.equal(calls.view,1);
 assert.equal(context.currentProject.modelAtelier.parts.length,1);
 assert.equal(context.currentProject.modelAtelier.parts[0].id,'humanoid-body-unified');
 console.log('SE538_NATIVE_LOADER_OK',JSON.stringify(stats));
})().catch(error=>{console.error(error);process.exitCode=1});
