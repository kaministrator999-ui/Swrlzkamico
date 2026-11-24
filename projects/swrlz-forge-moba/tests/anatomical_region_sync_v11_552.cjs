#!/usr/bin/env node
'use strict';
/* Runtime contract: actual source triangles determine six matching UV/3D groups. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),read=x=>fs.readFileSync(path.join(root,x),'utf8');
const native=JSON.parse(read('scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json'));
const part=native.project.modelAtelier.parts[0],raw=part.topologyMesh;
const attr=(data,size)=>({count:data.length/size,getX:i=>data[size*i],getY:i=>data[size*i+1],getZ:i=>data[size*i+2]});
const target={part,mesh:{geometry:{
 getAttribute:name=>name==='position'?attr(raw.positions,3):name==='uv'?attr(raw.uvs,2):null,
 getIndex:()=>({count:raw.indices.length,getX:i=>raw.indices[i]})
}}};
const ctx={console,Math,Set,Map,
 se356EditTarget:()=>target,
 se356EditInstall(){},se356UVRender(){},se356UVPreviewSchedule(){},
 se356UVPreviewRoot:()=>null,
 se336SelectedMesh:()=>target,
 se356UVMode:'paint',
};
vm.createContext(ctx);
vm.runInContext(read('runtime/uv_island_workspace_v11_551.js'),ctx);
vm.runInContext(read('runtime/uv_texture_alignment_v11_552.js'),ctx);
const r=vm.runInContext('se552Regions(se551Target())',ctx);
assert.equal(r.anatomical,true);
assert.deepEqual(r.groups.map(g=>g.id),[0,1,2,3,4,5]);
assert.equal(r.groups.reduce((n,g)=>n+g.faces.length,0),13932);
for(const g of r.groups)assert.ok(g.faces.length>900);
const palette=Array.from(vm.runInContext('se552Palette',ctx));
assert.deepEqual(palette,['#ef4444','#3b82f6','#22c55e','#eab308','#a855f7','#f97316']);
const before=part.uvPaintPNG;
assert.equal(vm.runInContext('se552SyncSelection(se551Target(),0)',ctx),true);
assert.ok(vm.runInContext('se551Selection.ids.length',ctx)>200);
assert.equal(before,part.uvPaintPNG,'selecting a UV region must never alter the actual painted skin');
new vm.Script(read('runtime/uv_texture_alignment_v11_552.js'));
console.log('SE552_ANATOMICAL_REGION_SYNC_PASS',JSON.stringify({regions:r.groups.length,triangles:13932,colors:palette}));
