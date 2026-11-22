#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/futuristic_humanoid_five_digit_v11_540.js'),'utf8');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json'),'utf8'));
new vm.Script(source);
let loaded=0,synced=0,historied=0,saved=0,views=0;
const context={
  console,dirty:false,currentProject:null,URL,confirm:()=>true,
  document:{baseURI:'https://example.test/',getElementById:()=>({classList:{remove(){}}}),
    querySelector:()=>({})},
  window:{SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change:()=>{}},
          SWYRL_ENGINE_MODEL_ATELIER:{view:()=>{views++}}},
  ModelAtelier:{close(){},syncProject(){synced++}},
  se232ActivateSelectedModelWorkspace(){},
  toast(){},initializeHistory(){historied++},markSaved(){saved++},
  requestAnimationFrame:f=>f(),
  se537OpenMannequin:()=>{throw Error('Prior 178-part/featureless-hand scene still routed')},
  se538ValidateHumanoid:data=>{
    const parts=data?.project?.modelAtelier?.parts||[];
    assert.equal(parts.length,1);
    assert.equal(parts[0]?.id,'humanoid-body-unified');
    const mesh=parts[0].topologyMesh;
    assert.equal(mesh.uvs.length,mesh.positions.length/3*2);
    return {parts:1,vertices:mesh.positions.length/3,
      triangles:mesh.indices.length/3,hasAtlas:!!parts[0].uvPaintPNG};
  },
  loadProject:data=>{loaded++;context.currentProject=data.project;},
  fetch:async url=>{
    assert.ok(url.includes('model-atelier-futuristic-humanoid-v11-540.swyrl.json'));
    return {ok:true,json:async()=>scene};
  }
};
vm.createContext(context);vm.runInContext(source,context,{timeout:3000});
const stats=context.window.SWYRL_ENGINE_HUMANOID_540.validate(scene);
assert.ok(stats.vertices>6000&&stats.vertices<=9000);
assert.ok(stats.triangles>12000&&stats.triangles<=16000);
assert.equal(typeof context.se537OpenMannequin,'function');
(async()=>{
 assert.equal(await context.se537OpenMannequin(true),true);
 assert.equal(loaded,1);assert.equal(synced,1);
 assert.equal(historied,1);assert.equal(saved,1);assert.equal(views,1);
 assert.equal(context.currentProject.modelAtelier.parts.length,1);
 assert.equal(context.currentProject.modelAtelier.parts[0].id,'humanoid-body-unified');
 console.log('SE540_NATIVE_HANDS_STARTER_OK',JSON.stringify(stats));
})().catch(e=>{console.error(e);process.exitCode=1});
