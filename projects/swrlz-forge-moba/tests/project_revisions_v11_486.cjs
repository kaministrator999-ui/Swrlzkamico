/* §E v11.486 — executable revision-codec regression checks (Node 20). */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const content=fs.readFileSync(path.join(root,'runtime/project_revisions_v11_486.js'),'utf8');
const context={window:{},TextEncoder,TextDecoder,Blob,Response,CompressionStream,DecompressionStream,
 Uint8Array,btoa,atob,Date,JSON,structuredClone,console};
vm.runInNewContext(content,context,{filename:'project_revisions_v11_486.js'});
const lib=context.window.SWYRL_ENGINE_REVISIONS_486;
assert.equal(lib.LIMIT,8);
async function main(){
 const make=(i)=>({project:{instanceId:'stable-project',name:'Hat',modelAtelier:{parts:[{id:'single-mesh',uvPaintPNG:'abc'.repeat(2048),position:[0,1,0],stamp:i}]}},
  editor:{currentStudio:'modeler'},scene:{actors:[]},se486History:{schema:'se-project-revisions-v1',entries:[]}});
 let saved=make(1);
 for(let i=1;i<=12;i++){
  const update=await lib.prepare(saved,make(i+1),i,96*1024*1024);
  saved=update.payload;
  assert.ok(JSON.stringify(saved).includes('stable-project'));
  assert.equal(lib.history(saved).length,Math.min(i,7));
  assert.equal(saved.project.modelAtelier.parts[0].stamp,i+1);
 }
 const entries=lib.history(saved);
 assert.deepEqual(Array.from(entries,x=>x.number),[6,7,8,9,10,11,12]);
 const restored=await lib.unpack(entries[0]);
 assert.equal(restored.project.modelAtelier.parts[0].stamp,6);
 assert.equal(restored.se486History,undefined,'archived revisions must not recursively contain history');
 const payload=await lib.pack(make(15)),decoded=await lib.unpack(payload);
 assert.equal(decoded.project.modelAtelier.parts[0].stamp,15);
 assert.equal(decoded.se486History,undefined);
 const cap=Buffer.byteLength(JSON.stringify(lib.withoutHistory(make(50))))+350;\n const tiny=await lib.prepare(saved,make(50),12,cap);
 assert.ok(tiny.dropped>=1,'quota pressure must prune oldest revisions');
 assert.ok(Buffer.byteLength(JSON.stringify(tiny.payload))<=cap,'bound revision payload under supplied quota');
 const asset={project:{kind:'model-atelier',modelAtelier:{schema:'swyrl-model-atelier-v1',parts:[{id:'hat'}]}},
  scene:{actors:[]},editor:{studioWorkspace:'modeler'},assetRecord:{id:'asset-one',type:'modeler'}};
 const assetFuture={...asset,project:{...asset.project,modelAtelier:{...asset.project.modelAtelier,parts:[{id:'hat',rig:{bones:[1,2,3]}}]}}};
 const assetVersion=await lib.prepare(asset,assetFuture,5,8*1024*1024);
 assert.equal(lib.history(assetVersion.payload).length,1);
 assert.equal((await lib.unpack(lib.history(assetVersion.payload)[0])).assetRecord.id,'asset-one');
 await assert.rejects(()=>lib.prepare(asset,assetFuture,0,999),/expected project revision/);
 await assert.rejects(()=>lib.unpack({codec:'evil',bytes:''}),/Unsupported revision format/);
 console.log('SE486_REVISION_CODEC_PASS: 12 saves, 8 retained, original identity, restore, size pruning, asset round-trip');
}
main().catch(error=>{console.error(error);process.exitCode=1});
