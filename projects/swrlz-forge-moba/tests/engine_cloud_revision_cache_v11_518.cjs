#!/usr/bin/env node
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const assert=require('node:assert/strict');
const code=fs.readFileSync(path.resolve(__dirname,'../runtime/engine_cloud_revision_cache_v11_518.js'),'utf8');
let auth=true,ready=true,cloudBusy=false,download=0,localLoads=0,refresh=0;
let current='initial',revision=4,meta=[{id:'local-model',cloudRef:{id:'remote-1',revision:4}}],
 rows=new Map([['local-model',{id:'local-model',cloudRef:{id:'remote-1',revision:4},
 data:{project:{name:'Hat',kind:'model-atelier'},scene:{actors:[]}}}]]);
const sel={value:''},startup=[];
const sandbox=vm.createContext({window:{SWYRL_ENGINE_STARTUP_476:{markLoaded:(...args)=>startup.push(args)}},
 ready:true,se176AccountConnected:true,cloudBusy:false,se175Transition:false,se175LocalLoading:false,
 se176CloudRows:[],
 se176RefreshProjects:async()=>{refresh++;sandbox.se176CloudRows=[{id:'remote-1',revision}];},
 se175Read:async id=>id?rows.get(id):meta,
 se175RefreshLocal:async()=>{},
 se175LocalList:sel,
 se175LoadLocal:async()=>{localLoads++;if(sel.value==='local-model')current='local-model';},
 getProjectId:()=>current,
 loadCloud:async id=>{download++;current='remote-loaded-'+download;return id==='remote-1';},
});
const go=async()=>{
 vm.runInContext(code,sandbox);
 const api=sandbox.window.SWYRL_ENGINE_CLOUD_CACHE_518;
 assert.equal(await api.load('remote-1'),true);
 assert.equal(download,0,'cached same-revision project must not download');
 assert.equal(localLoads,1);
 assert.equal(api.inspect().status,'cache-hit');
 assert.equal(startup.at(-1)[0],'cloud');
 current='other';
 revision=5;
 assert.equal(await api.load('remote-1'),true);
 assert.equal(download,1,'changed remote revision must download newer project');
 assert.equal(api.inspect().status,'network-loaded');
 sandbox.se176AccountConnected=false;
 assert.equal(await api.load('remote-1'),false,'signed-out user cannot use previous account cache');
 assert.equal(download,1);
 sandbox.se176AccountConnected=true;
 meta=[{id:'local-model',cloudRef:{id:'remote-1',revision:5}}];sandbox.se175Read=async id=>id?rows.get(id):meta;
 current='other';revision=5;
 assert.equal(await api.load('remote-1'),true);
 assert.equal(download,2,'metadata matching without matching stored revision must download');
 sandbox.cloudBusy=true;
 assert.equal(await api.load('remote-1'),false);
 assert.equal(download,2,'in-progress cloud work cannot be bypassed');
 assert(refresh>=4);
 console.log('SE518_CLOUD_CACHE_PASS',JSON.stringify({sameRevisionCacheHit:true,
  changedRevisionFetched:true,missingSnapshotFetched:true,logoutBlocked:true,
  cloudBusyBlocked:true,metadataLookups:refresh}));
};
go().catch(e=>{console.error(e);process.exitCode=1;});
