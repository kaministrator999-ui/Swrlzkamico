#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const path=require('node:path'),root=path.resolve(__dirname,'..');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json'),'utf8'));
const repair=fs.readFileSync(path.join(root,'runtime/humanoid_semantic_repair_v11_544.js'),'utf8');
const loader=fs.readFileSync(path.join(root,'runtime/humanoid_semantic_starter_v11_544.js'),'utf8');
new vm.Script(repair);new vm.Script(loader);
let checkpoints=0,updates=0,selects=0,downloads=0,load=0,opens=0;
let currentPart=JSON.parse(JSON.stringify(scene.project.modelAtelier.parts[0]));
currentPart.uvPaintPNG='data:image/png;base64,OLDERPAINT';
currentPart.uvPaintOffset=[.2,-.1];
const old=JSON.parse(JSON.stringify(currentPart.topologyMesh));
let consent=true;
const ctx={
 console,URL,document:{
  baseURI:'https://example.org/',
  getElementById:()=>null,querySelector:()=>null
 },
 window:{},
 currentProject:{canonicalId:'robotic-humanoid-mannequin'},
 selection:'humanoid-body-unified',
 partById:id=>id==='humanoid-body-unified'?currentPart:null,
 se336SelectedMesh:()=>({part:currentPart}),
 ensurePanel(){},refreshInspector(){},
 panel:null,status(){},
 checkpoint(){checkpoints++},signalEdited(){updates++},select(){selects++},
 checkPart:part=>part.uvPaintPNG.length<=360000&&part.topologyMesh.indices.length===13932*3,
 confirm:()=>consent,
 fetch:async url=>{downloads++;assert.ok(String(url).includes('v11-544'));return{ok:true,json:async()=>scene}},
 MutationObserver:class{}
};
vm.createContext(ctx);
vm.runInContext(repair,ctx,{timeout:1500});
const api=ctx.window.SWYRL_E_MANNEQUIN_PAINT_REPAIR_544;
assert.equal(api.compatible(),true);
(async()=>{
 consent=false;
 assert.equal(await api.restore(),false);
 assert.equal(downloads,0);
 assert.equal(checkpoints,0);
 consent=true;
 assert.equal(await api.restore(),true);
 assert.equal(downloads,1);
 assert.equal(checkpoints,1);
 assert.equal(updates,1);assert.equal(selects,1);
 assert.equal(currentPart.uvPaintPNG,scene.project.modelAtelier.parts[0].uvPaintPNG);
 assert.deepEqual(currentPart.topologyMesh,old);
 assert.equal(currentPart.uvPaintOffset,undefined);
 // Do not apply a new painting to altered UV coordinates.
 currentPart.topologyMesh.uvs[0]+=.1;
 assert.equal(api.compatible(),false);
 assert.equal(await api.restore(),false);
 assert.equal(downloads,1);assert.equal(checkpoints,1);
 console.log('SE544_NATIVE_PAINT_RECOVERY_OK',JSON.stringify({
  mappedBodyOnly:true,confirmBeforeReplace:true,
  undoCheckpoint:checkpoints,geometryAndUVPreserved:true,
  offAtlasPaintBlocked:true,projectOwnershipPreserved:true}));
})().catch(err=>{console.error(err);process.exitCode=1});
