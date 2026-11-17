'use strict';
/* §E v11.495: restore complete textured historical revisions after compaction. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),crypto=require('node:crypto');
const code=fs.readFileSync(path.join(__dirname,'../runtime/model_revision_shared_texture_v11_495.js'),'utf8');
const old={
 SCHEMA:'se-project-revisions-v1',LIMIT:8,
 history:d=>d?.se486History?.entries||[],
 pack:async doc=>{
  const snapshot=structuredClone(doc);delete snapshot.se486History;
  return {codec:'gzip+base64',bytes:zlib.gzipSync(Buffer.from(JSON.stringify(snapshot))).toString('base64')};
 },
 unpack:async entry=>JSON.parse(zlib.gunzipSync(Buffer.from(entry.bytes,'base64')).toString())
};
const context=vm.createContext({window:{SWYRL_ENGINE_REVISIONS_486:old},structuredClone,TextEncoder,Date,Set,Map,Error,Object,Array,Number,Math});
vm.runInContext(code,context);
const codec=context.window.SWYRL_ENGINE_REVISIONS_495;
const paint='data:image/png;base64,'+crypto.randomBytes(140000).toString('base64');
function scene(png=paint){
 return {project:{instanceId:'hat',modelAtelier:{parts:[{id:'hat',uvPaintPNG:png,vertices:[0,1,2]}]},
  levelPack:{levels:[{data:{project:{modelAtelier:{parts:[{id:'hat',uvPaintPNG:png}]}}}}]}},
  scene:{actors:[]},editor:{}};
}
(async()=>{
 const before=scene();
 before.se486History={schema:old.SCHEMA,limit:8,entries:[]};
 for(let i=1;i<=5;i++){
  const snap=scene();snap.project.modelAtelier.parts[0].vertices=[i,1,2];
  before.se486History.entries.push({number:i,savedAt:'2026-11-17',...await old.pack(snap)});
 }
 const after=scene();
 const {payload}=await codec.prepare(before,after,6,96*1024*1024);
 assert.equal(payload.se486History.entries.length,6);
 assert.equal(payload.se486History.se495TexturePool.length,1);
 assert(payload.se486History.entries.every(e=>e.se495SharedTextures));
 assert(JSON.stringify(payload).length<JSON.stringify(before).length*.6);
 const restored=[];
 for(const e of codec.history(payload))restored.push(await codec.unpack(e));
 assert(restored.every(s=>s.project.modelAtelier.parts[0].uvPaintPNG===paint));
 assert(restored.every(s=>s.project.levelPack.levels[0].data.project.modelAtelier.parts[0].uvPaintPNG===paint));
 assert.equal(restored[0].project.modelAtelier.parts[0].vertices[0],1);
 assert.equal(restored[5].project.modelAtelier.parts[0].vertices[0],0);
 const newer=scene('data:image/png;base64,'+crypto.randomBytes(140000).toString('base64'));
 const result=await codec.prepare(payload,newer,7,96*1024*1024);
 assert.equal(result.payload.se486History.se495TexturePool.length,1);
 assert.equal((await codec.unpack(codec.history(result.payload)[0])).project.modelAtelier.parts[0].uvPaintPNG,paint);
 await assert.rejects(()=>codec.unpack({...codec.history(payload)[0],_se495Pool:[]}),/texture pool missing|missing texture/);
 console.log('SE495_COMPACT_SHARED_TEXTURE_HISTORY_PASS',JSON.stringify({
  oldBytes:JSON.stringify(before).length,newBytes:JSON.stringify(payload).length,
  revisions:restored.length,reducedPercent:Math.round((1-JSON.stringify(payload).length/JSON.stringify(before).length)*100)
 }));
})().catch(e=>{console.error(e);process.exitCode=1});
