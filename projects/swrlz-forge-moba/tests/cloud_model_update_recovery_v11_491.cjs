'use strict';
// §E v11.491: no replay of cloud saves; only trusted, identical selected-document reads.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.resolve(__dirname,'../runtime/model_account_update_recovery_v11_491.js'),'utf8');
const ctx={
 window:{},
 NAME:{selectedDocument:async()=>({id:'project-a',doc:{project:{}},metadata:{revision:4}})},
 ready:true,se176AccountConnected:true,
 setTimeout:fn=>{fn();return 1},Promise,Error
};
const api=()=>vm.runInNewContext('(()=>{'+source+';return window.SWYRL_ENGINE_UPDATE_READ_491})()',ctx);
(async()=>{
 let count=0;
 ctx.NAME.selectedDocument=async()=>{count++;if(count<3)throw Error('Failed to fetch');return {id:'p',metadata:{revision:4}};};
 let progress=[];
 let result=await api().read({id:'p'},'cloud',x=>progress.push(x));
 assert.equal(result.metadata.revision,4);assert.equal(count,3);assert.equal(progress.length,2);
 count=0;
 ctx.NAME.selectedDocument=async()=>{count++;throw Error('Failed to fetch')};
 let error;try{await api().read({id:'p'},'cloud')}catch(e){error=e}
 assert.equal(count,3);assert.equal(error?.se491Recoverable,true);
 assert.match(error.message,/No model changes were sent/);
 count=0;
 ctx.NAME.selectedDocument=async()=>{count++;throw Error('Invalid project selection')};
 await assert.rejects(async()=>api().read({id:'p'},'cloud'),/Invalid project selection/);
 assert.equal(count,1,'not retrying validation/identity failures');
 count=0;
 ctx.NAME.selectedDocument=async()=>{count++;throw Error('Failed to fetch')};
 await assert.rejects(async()=>api().read({id:'p'},'local'),/Failed to fetch/);
 assert.equal(count,1,'local read is never retried as network read');
 assert.equal(api().isTransient(Error('Failed to fetch')),true);
 assert.equal(api().isTransient(Error('Wrong project identity')),false);
 console.log('SE491_CLOUD_READ_RETRY_PASS');
})().catch(e=>{console.error(e);process.exit(1)});
