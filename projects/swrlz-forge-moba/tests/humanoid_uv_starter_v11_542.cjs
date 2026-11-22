#!/usr/bin/env node
'use strict';
// §E v11.542 regression: native UV-ready Starter Models loads the actual
// new asset and generic conical UV candidate cannot detach its painted PNG.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const scene=JSON.parse(fs.readFileSync(path.join(root,
 'scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json'),'utf8'));
const loader=fs.readFileSync(path.join(root,'runtime/humanoid_uv_starter_v11_542.js'),'utf8');
const guard=fs.readFileSync(path.join(root,'runtime/humanoid_uv_guard_v11_542.js'),'utf8');
new vm.Script(loader);new vm.Script(guard);
let saves=0,loads=0,syncs=0,history=0,views=0;
const context={
 console,URL,dirty:false,currentProject:null,confirm:()=>true,
 document:{baseURI:'https://example.com/',querySelector:()=>({}),
   getElementById:()=>({classList:{remove(){}}})},
 window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change:()=>{}},
   SWYRL_ENGINE_MODEL_ATELIER:{view:()=>{views++}}},
 toast(){},requestAnimationFrame:f=>f(),
 ModelAtelier:{close(){},syncProject(){syncs++}},
 loadProject:data=>{loads++;context.currentProject=data.project;},
 se232ActivateSelectedModelWorkspace(){},
 initializeHistory(){history++},markSaved(){saves++},
 se538ValidateHumanoid:data=>{
  assert.equal(data.project.modelAtelier.parts.length,1);
  const p=data.project.modelAtelier.parts[0],g=p.topologyMesh;
  assert.ok(g.uvs.length===g.positions.length/3*2);
  assert.ok(p.uvPaintPNG.length>100);
  return {vertices:g.positions.length/3,triangles:g.indices.length/3,parts:1,hasAtlas:true};
 },
 fetch:async url=>{
  assert.ok(url.includes('model-atelier-futuristic-humanoid-v11-542.swyrl.json'));
  return {ok:true,json:async()=>scene};
 }
};
vm.createContext(context);
vm.runInContext(loader,context,{timeout:2500});
assert.ok(context.window.SWYRL_ENGINE_HUMANOID_542.validate(scene).vertices<=9000);
(async()=>{
 assert.equal(await context.se537OpenMannequin(true),true);
 assert.equal(loads,1);assert.equal(saves,1);assert.equal(syncs,1);
 assert.equal(history,1);assert.equal(views,1);
 const part=context.currentProject.modelAtelier.parts[0];
 assert.equal(part.id,'humanoid-body-unified');
 assert.equal(part.uvPaintPNG,scene.project.modelAtelier.parts[0].uvPaintPNG);
 // Test guard in its actual lexical context; non-humanoid UVs must not
 // lose the existing experimental tool.
 let active=part;
 const button={disabled:false},label={textContent:''};
 const guardContext={
  se503Target:()=>({part:active}),
  se503Candidate:()=>({legacy:true}),
  se503Refresh:()=>{},
  se503Preview:null,
  document:{getElementById:()=>({querySelector:id=>id==='#se503AtlasStatus'?label:button})},
  window:{}
 };
 vm.createContext(guardContext);
 vm.runInContext(guard,guardContext,{timeout:2500});
 assert.equal(guardContext.window.SWYRL_ENGINE_HUMANOID_UV_GUARD_542.blocked(),true);
 assert.throws(()=>guardContext.se503Candidate(),/humanoid already has its own relaxed/);
 guardContext.se503Refresh();
 assert.equal(button.disabled,true);
 assert.ok(label.textContent.includes('UV atlas already applied'));
 active={id:'ordinary-cone',kind:'topologyMesh'};
 assert.equal(guardContext.se503Candidate().legacy,true);
 assert.equal(guardContext.window.SWYRL_ENGINE_HUMANOID_UV_GUARD_542.blocked(),false);
 console.log('SE542_NATIVE_UV_STARTER_AND_GUARD_OK',
  JSON.stringify({parts:1,uvVertices:part.topologyMesh.positions.length/3,
   triangles:part.topologyMesh.indices.length/3,painted:true,
   protectedHumanoid:true,otherUVModelsUntouched:true}));
})().catch(e=>{console.error(e);process.exitCode=1});
