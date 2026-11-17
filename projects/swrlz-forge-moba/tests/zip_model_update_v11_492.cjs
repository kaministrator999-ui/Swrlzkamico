'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib');
const src=fs.readFileSync(path.join(__dirname,'../runtime/model_zip_update_v11_492.js'),'utf8');
const ctx={window:{},TextDecoder,Blob,DecompressionStream,DataView,Uint8Array,Uint32Array,Error,JSON,Promise};
vm.createContext(ctx);
vm.runInContext(src,ctx);
const api=ctx.window.SWYRL_ENGINE_ZIP_UPDATES_492;
function buildZip(rows){
 const locals=[],centrals=[];let offset=0;
 for(const {name,json,method=8,crcOverride,claimSize} of rows){
  const raw=Buffer.from(json,'utf8'),deflated=method===8?zlib.deflateRawSync(raw):raw;
  const nameBytes=Buffer.from(name,'utf8'),crc=crcOverride??api.crc32(raw);
  const local=Buffer.alloc(30);local.writeUInt32LE(0x04034b50,0);
  local.writeUInt16LE(0x800,6);local.writeUInt16LE(method,8);
  local.writeUInt32LE(crc,14);local.writeUInt32LE(deflated.length,18);
  local.writeUInt32LE(raw.length,22);local.writeUInt16LE(nameBytes.length,26);
  locals.push(local,nameBytes,deflated);
  const central=Buffer.alloc(46);central.writeUInt32LE(0x02014b50,0);
  central.writeUInt16LE(20,4);central.writeUInt16LE(20,6);
  central.writeUInt16LE(0x800,8);central.writeUInt16LE(method,10);
  central.writeUInt32LE(crc,16);central.writeUInt32LE(deflated.length,20);
  central.writeUInt32LE(claimSize??raw.length,24);
  central.writeUInt16LE(nameBytes.length,28);central.writeUInt32LE(offset,42);
  centrals.push(central,nameBytes);
  offset+=local.length+nameBytes.length+deflated.length;
 }
 const cd=Buffer.concat(centrals),eocd=Buffer.alloc(22);
 eocd.writeUInt32LE(0x06054b50,0);eocd.writeUInt16LE(rows.length,8);
 eocd.writeUInt16LE(rows.length,10);eocd.writeUInt32LE(cd.length,12);
 eocd.writeUInt32LE(offset,16);
 return Buffer.concat([...locals,cd,eocd]);
}
function upload(name,raw){return {name,size:raw.length,arrayBuffer:async()=>Uint8Array.from(raw).buffer,
 text:async()=>raw.toString('utf8')}}
async function run(){
 const model={engine:'§E',project:{modelAtelier:{parts:[{id:'hat'}]}}};
 const payload=JSON.stringify(model);
 const archive=buildZip([{name:'The-Sorting-Hat-Mesh-Fix-v2.swyrl.json',json:payload}]);
 let progress=[];const got=await api.parse(upload('The-Sorting-Hat-Mesh-Fix-v2.zip',archive),t=>progress.push(t));
 assert.equal(JSON.stringify(got),payload);
 assert(progress.some(t=>t.includes('Extracting')));
 assert.equal(JSON.stringify(await api.parse(upload('hat.swyrl.json',Buffer.from(payload)))),payload);
 const stored=buildZip([{name:'hat.swyrl.json',json:payload,method:0}]);
 assert.equal(JSON.stringify(await api.parse(upload('hat.zip',stored))),payload);
 const extra=buildZip([{name:'metadata.txt',json:'hi'}, {name:'models/hat.swyrl.json',json:payload}]);
 assert.equal(JSON.stringify(await api.parse(upload('hat.zip',extra))),payload);
 for(const archive of [
  buildZip([{name:'a.swyrl.json',json:payload},{name:'b.swyrl.json',json:payload}]),
  buildZip([{name:'../a.swyrl.json',json:payload}]),
  buildZip([{name:'hat.swyrl.json',json:payload,claimSize:40*1024*1024}]),
  buildZip([{name:'hat.swyrl.json',json:payload,crcOverride:0}])
 ]){
  await assert.rejects(async()=>api.parse(upload('invalid.zip',archive)),/ZIP update:/);
 }
 await assert.rejects(async()=>api.parse(upload('hat.zip',Buffer.from('not a zip'))),/ZIP update:/);
 console.log('SE492_ZIP_MODEL_UPLOAD_PASS');
}
run().catch(e=>{console.error(e);process.exitCode=1});
