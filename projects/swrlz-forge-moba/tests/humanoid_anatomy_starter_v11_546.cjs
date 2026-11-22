#!/usr/bin/env node
'use strict';
// §E v11.546 new starter: correct source asset and anatomy-oriented UV mapping.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'),'utf8'));
const factory=fs.readFileSync(path.join(root,'runtime/humanoid_anatomical_robot_v11_546.js'),'utf8');
new vm.Script(factory);
let loaded=0,saveState=0,viewed=0;
const context={
 console,URL,dirty:false,currentProject:null,toast(){},confirm:()=>true,
 document:{baseURI:'https://example.test/',getElementById:()=>({classList:{remove(){}}})},
 window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change:()=>{}},
         SWYRL_ENGINE_MODEL_ATELIER:{view:()=>{viewed++}}},
 ModelAtelier:{close(){},syncProject(){}},
 loadProject:d=>{loaded++;context.currentProject=d.project},
 se232ActivateSelectedModelWorkspace(){},initializeHistory(){},
 markSaved(){saveState++},requestAnimationFrame:f=>f(),
 se538ValidateHumanoid:d=>{
  const p=d.project.modelAtelier.parts[0],m=p.topologyMesh;
  assert.ok(m.positions.length/3<=9000);
  assert.equal(m.indices.length,13932*3);
  assert.ok(p.uvPaintPNG.startsWith('data:image/png;base64,'));
  return {vertices:m.positions.length/3};
 },
 fetch:async url=>{
  assert.ok(url.toString().endsWith('v11-546.swyrl.json'));
  return {ok:true,json:async()=>scene};
 }
};
vm.createContext(context);vm.runInContext(factory,context);
assert.ok(context.window.SWYRL_ENGINE_HUMANOID_546.validate(scene).vertices<=9000);
(async()=>{
 assert.equal(await context.se537OpenMannequin(true),true);
 assert.equal(loaded,1);assert.equal(saveState,1);assert.equal(viewed,1);
 assert.equal(context.currentProject.canonicalId,'robotic-humanoid-mannequin');
 assert.equal(context.currentProject.modelAtelier.parts.length,1);
 assert.equal(context.currentProject.modelAtelier.parts[0].uvPaintPNG,
              scene.project.modelAtelier.parts[0].uvPaintPNG);
 assert.equal(context.window.SWYRL_ENGINE_HUMANOID_546.status().busy,false);
 console.log('SE546_NATIVE_ANATOMICAL_ROBOT_STARTER_OK');
})().catch(e=>{console.error(e);process.exitCode=1});
