#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const scene=JSON.parse(fs.readFileSync(path.join(root,'scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json'),'utf8'));
const part=scene.project.modelAtelier.parts[0],original=JSON.stringify(part);
const runtime=fs.readFileSync(path.join(root,'runtime/humanoid_uv_anatomy_view_v11_545.js'),'utf8');
new vm.Script(runtime);
const context={console,window:{},currentProject:scene.project,document:{getElementById:()=>null},
 se336SelectedMesh:()=>({part}),ensurePanel(){},refreshInspector(){},se336SaveCanvas(){},status(){}};
vm.createContext(context);vm.runInContext(runtime,context);
const api=context.window.SWYRL_E_UV_ANATOMY_545;
assert.equal(api.version,'v11.545');
const report=api.inspect();
assert.equal(report.triangles,13932);
assert.equal(Object.values(report.counts).reduce((a,b)=>a+b,0),13932);
for(const zone of ['head','chest','back','side','leftArm','rightArm','leftLeg','rightLeg'])
 assert.ok(report.counts[zone]>0,zone);
assert.equal(JSON.stringify(part),original,'inspection must not change UV, paint or geometry');
const before=part.id;part.id='different-mesh';
assert.equal(api.inspect(),null,'do not identify unrelated mesh as mannequin');
part.id=before;assert.equal(JSON.stringify(part),original);
console.log('SE545_UV_ANATOMY_VIEW_OK',JSON.stringify(report.counts));
