#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const uvSource=fs.readFileSync(ROOT+'/runtime/model_atelier_multi_uv_atlas_v11_345.js','utf8');
const displaySource=fs.readFileSync(ROOT+'/runtime/model_vr_display_modes_v11_345.js','utf8');
const uiSource=fs.readFileSync(ROOT+'/runtime/model_studio_vr_ui_v11_345.js','utf8');
new vm.Script(uvSource);new vm.Script(displaySource);new vm.Script(uiSource);
const root=new THREE.Group(),parts=[];
for(let i=0;i<17;i++){
 const part={id:'mage-'+i,name:'Mage part '+i,group:i<15?'Character':'Staff',kind:'topologyMesh'};
 const mesh=new THREE.Mesh(i%2?new THREE.BoxGeometry(1,1,1):new THREE.SphereGeometry(.5,16,12),new THREE.MeshStandardMaterial());
 mesh.userData.atelierId=part.id;
 root.add(mesh);parts.push(part);
}
const native={name:'Mage · UV source',parts},byId=id=>parts.find(p=>p.id===id);
const ctx={THREE,model:()=>native,modelRoot:root,partById:byId,
 selection:parts[0].id,ensurePanel(){},refreshInspector(){},window:{},
 status(){},document:{},currentProject:{name:'Mage'}};
vm.createContext(ctx);
vm.runInContext(uvSource+'\nthis.uvTest={parts:se345AtlasParts,layout:se345AtlasLayout,metrics:se345AtlasMetrics,fingerprint:se345AtlasFingerprint,verify:se345AtlasVerify,inspect:window.SWYRL_ENGINE_UV_ATLAS.inspect,selectAll:window.SWYRL_ENGINE_UV_ATLAS.selectAll};',ctx);
const uv=ctx.uvTest;
assert.equal(uv.parts().length,17);
const a=uv.layout(17,2048),b=uv.layout(17,4096);
assert.equal(a.columns,5);assert.equal(a.rows,4);
assert.equal(b.width,4096);assert(b.size>a.size);
const cells=Array.from({length:17},(_,i)=>a.rect(i));
for(let i=0;i<17;i++){
 const [x,y,w,h]=cells[i];assert(x>=0&&y>=0&&x+w<=2048&&y+h<=2048);
 for(let j=i+1;j<17;j++){
  const [xx,yy,ww,hh]=cells[j];
  assert(x+w<=xx||xx+ww<=x||y+h<=yy||yy+hh<=y,'each part must have non-overlapping atlas region');
 }
}
assert.equal(uv.selectAll(),17,'one click selects entire mage');
const targets=uv.parts(),fp=uv.fingerprint(targets[0]);
assert.equal(uv.fingerprint(targets[0]),fp);
assert.equal(uv.metrics(targets[0].mesh).uvBounds.length,4);
const manifest={schema:'swyrl-model-uv-atlas-v1',width:2048,height:2048,
 parts:targets.map((t,i)=>({id:t.part.id,name:t.part.name,fingerprint:uv.fingerprint(t),uvRectPx:cells[i]}))};
assert.equal(uv.verify(manifest).size,17,'all 17 mesh-to-tile links are valid');
const wrong=JSON.parse(JSON.stringify(manifest));wrong.parts[3].fingerprint='deadbeef';
assert.throws(()=>uv.verify(wrong),/geometry\/UVs changed/,'stale UV atlas must fail closed');
const bad=new THREE.BufferGeometry();
bad.setAttribute('position',new THREE.Float32BufferAttribute([0,0,0,1,0,0,0,1,0],3));
const invalidTarget={part:{id:'bad'},mesh:new THREE.Mesh(bad,new THREE.MeshBasicMaterial())};
assert.equal(uv.fingerprint(invalidTarget),null);
assert.throws(()=>uv.metrics(invalidTarget.mesh),/Missing or incomplete mesh UV/);
let output=[];
const state={scene:new THREE.Scene(),displayMode:'textured',cachedEntries:targets.map(t=>({mesh:t.mesh})),
 displayOriginals:new Map(),displayMaterials:new Map(),owned:new Set()};
const dc={THREE,se340XR:state,se340Own:m=>{state.owned.add(m);return m;},
 se340Notice:message=>output.push(message)};
vm.createContext(dc);vm.runInContext(displaySource+'\nthis.displayTest={set:se345SetDisplay,restore:se345RestoreDisplay,sync:se345SyncDisplay};',dc);
const ops=dc.displayTest,original=targets[0].mesh.material;
for(const mode of ['solid','wireframe','xray','normals']){
 assert(ops.set(mode));
 assert.notEqual(targets[0].mesh.material,original,'display mode should be temporary');
 assert.equal(state.displayOriginals.get(targets[0].mesh),original);
}
assert(ops.set('textured'));assert.equal(targets[0].mesh.material,original);
assert(ops.set('wireframe'));ops.restore();
assert.equal(targets[0].mesh.material,original,'VR exit restores original materials');
assert.equal(state.displayOriginals.size,0);
assert(uiSource.includes("['display-wireframe','Wireframe']"));
assert(uiSource.includes("['display-xray','X-ray']"));
assert(uiSource.includes("['cameras','Angles']"));
assert(uiSource.includes("['view-front','Front']"));
assert(uiSource.includes("const slots=[];let currentPage=''"),'palette is reused, not duplicated');
console.log('MODEL_VR_DISPLAY_AND_MULTI_UV_ATLAS_V11_345_PASS',{parts:17,regions:cells.length,modeCount:5});
