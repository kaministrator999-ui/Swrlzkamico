'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../runtime/project_load_diagnostics_v11_493.js'),'utf8');
let fetched=0,parseName=null,parseCount=0,progress=[];
const context={
 window:{},
 ready:true,se176AccountConnected:true,
 setTimeout(fn){fn();},
 rpc:async()=>{fetched++;if(fetched===1)throw Error('Failed to fetch');return {project:{id:'hat-project'},bytes:new ArrayBuffer(5)}},
 se492ModelUpload:{parse:async file=>{parseName=file.name;parseCount++;return {ok:true}}},
 Promise,ArrayBuffer,Uint8Array,Error,String,Number
};
vm.createContext(context);vm.runInContext(source,context);
const api=context.window.SWYRL_ENGINE_PROJECT_LOAD_493;
const file=(name,bytes)=>{
 const blob=new Blob([Uint8Array.from(bytes)]);
 return {name,size:blob.size,slice:blob.slice.bind(blob),arrayBuffer:blob.arrayBuffer.bind(blob)};
};
(async()=>{
 const zip=file('android-model.json',[0x50,0x4b,3,4,1,2]);
 const result=await api.parseModel(zip,x=>progress.push(x));
 assert.equal(result.ok,true);
 assert(parseName.endsWith('.zip'),'ZIP signature must override Android file name');
 assert(progress.some(x=>x.includes('ZIP detected')));
 await api.parseModel(file('raw.swyrl.json',[0x7b,0x7d]));
 assert.equal(parseName,'raw.swyrl.json');
 await assert.rejects(async()=>api.parseModel(file('invalid.zip',[0x7b,0x7d])),/valid ZIP header/);
 const loaded=await api.fetchProject('hat-project',x=>progress.push(x));
 assert.equal(loaded.project.id,'hat-project');
 assert.equal(fetched,2,'retry only read once after one failed fetch');
 assert(progress.some(x=>x.includes('retry 2')));
 fetched=0;
 context.rpc=async()=>{fetched++;return {project:{id:'another-project'},bytes:new ArrayBuffer(0)}};
 await assert.rejects(async()=>api.fetchProject('hat-project'),/different project ID/);
 assert.equal(fetched,1,'never retry identity failures');
 api.failure(Error('Native import failed'));
 assert.equal(api.getError(),'Native import failed');
 api.reset();assert.equal(api.getError(),'');
 console.log('SE493_PROJECT_LOAD_DIAGNOSTICS_PASS');
})().catch(e=>{console.error(e);process.exit(1)});
