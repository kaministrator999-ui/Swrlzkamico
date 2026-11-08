#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const uv=fs.readFileSync(ROOT+'/runtime/model_atelier_multi_uv_atlas_v11_345.js','utf8');
const pages=fs.readFileSync(ROOT+'/runtime/model_multi_uv_sheets_v11_346.js','utf8');
const patch=fs.readFileSync(ROOT+'/patches/v11_346_model_multi_uv_sheets.py','utf8');
new vm.Script(uv.replace('const SE345_ATLAS_MAX=96;','const SE345_ATLAS_MAX=96;\n'+pages));
new vm.Script(pages);
assert(patch.includes('Previous sheet')&&patch.includes('Next sheet'));
assert(patch.includes('se346AtlasSuffix(plan)'));
const geometry=new THREE.BoxGeometry(.4,.5,.3),parts=[],scene=new THREE.Group();
for(let i=0;i<811;i++){
 const part={id:'character-'+i,name:'Character part '+i,kind:'box',group:i<313?'Character':'Companions'};
 parts.push(part);
 const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial());mesh.userData.atelierId=part.id;scene.add(mesh);
}
const current={name:'Large multi-object character',parts};
const c={THREE,model:()=>current,modelRoot:scene,partById:id=>parts.find(x=>x.id===id),
 selection:parts[0].id,ensurePanel(){},refreshInspector(){},window:{},
 currentProject:{name:current.name},document:{getElementById:()=>null},status(){}};
vm.createContext(c);
vm.runInContext(uv.replace('const SE345_ATLAS_MAX=96;','const SE345_ATLAS_MAX=96;\n'+pages)+
 '\nthis.test={init:se345AtlasCurrent,selected:se345AtlasSelectedParts,go:se346AtlasGo,info:se346AtlasPageInfo,suffix:se346AtlasSuffix,layout:se345AtlasLayout,api:window.SWYRL_ENGINE_UV_ATLAS};',c);
c.test.init();
assert.equal(c.test.api.selectAll(),811);
assert.equal(c.test.info().pages,9);
assert.equal(c.test.selected().length,96);
assert.equal(c.test.selected()[0].part.id,'character-0');
assert.equal(c.test.go(1),true);
assert.equal(c.test.info().page,1);
assert.equal(c.test.selected()[0].part.id,'character-96');
for(let i=0;i<7;i++)assert.equal(c.test.go(1),true);
assert.equal(c.test.info().page,8);
assert.equal(c.test.info().visible,43);
assert.equal(c.test.selected().length,43);
assert.equal(c.test.selected()[0].part.id,'character-768');
assert.equal(c.test.go(1),false);
assert.equal(c.test.go(-1),true);
assert.equal(c.test.selected().length,96);
assert.equal(c.test.suffix({sheetIndex:9,sheetCount:9}),'-SHEET-09-of-09');
assert.equal(c.test.layout(96,4096).rect(95).length,4);
assert.equal(c.test.api.inspect().sheet.total,811);
console.log('MODEL_UV_FULL_CHARACTER_811_PARTS_9_SHEETS_PASS');
