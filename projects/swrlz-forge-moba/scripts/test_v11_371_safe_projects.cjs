const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(require('node:path').join(__dirname,'../runtime/project_safe_save_v11_371.js'),'utf8');
const db=new Map(),refs=new Map();let current={name:'Original Starter',template:'model-atelier',kind:'model-atelier',modelAtelier:{parts:[{id:'mesh-1',uvPaintOffset:[.25,0]}]},particleStudio:{emitters:[{id:'spark'}]}},seq=0,cloudSaves=0;
const snapshot=()=>({id:current.instanceId||'starter-draft',name:current.projectName||current.name,updatedAt:'2026-11-09',data:{project:structuredClone(current),editor:{studioWorkspace:'modeler'},scene:{actors:[{id:'actor-1'}]}}});
const doc={readyState:'loading',addEventListener(){},getElementById(){return null},querySelector(){return null},querySelectorAll(){return[]}};
const ctx={console,structuredClone,Map,setTimeout,clearTimeout,Date,window:{addEventListener(){}},document:doc,requestAnimationFrame(fn){fn()},
 summaryName:s=>String(s||''),bounded:(v,max)=>typeof v==='string'&&v.length>0&&v.length<=max,
 getProjectId:()=>current.instanceId||'starter-draft',cloudRefs:refs,id:()=>('copy-'+(++seq)),currentProject:current,
 se175Snapshot:snapshot,se175Store:async rows=>{for(const row of rows)db.set(row.id,structuredClone(row))},
 se175Read:async key=>key?db.get(key):[...db.values()],se175Saving:null,se175Transition:false,se175LocalLoading:false,
 se175RefreshLocal:async()=>{},se175LocalMessage(){},se175UpdateLabel(){},
 se175StampProject:(id,name,starter)=>{current.instanceId=id;current.projectName=name;current.name=name;current.sourceStarterId=starter},
 se175Restore:row=>{current=structuredClone(row.data.project);ctx.currentProject=current},
 saveCloud:async()=>{cloudSaves++;refs.set(ctx.getProjectId(),{id:'remote-'+seq,revision:1})},
 loadCloud:async()=>true,rpc:async()=>({projects:[]}),se176AccountConnected:false,ready:false,cloudBusy:false,
 playing:false,simulating:false,dirty:false,history:[],historyIndex:0,revision:0,workspaceLocalAllowed:false,
 loadProject:row=>{current=structuredClone(row.project);ctx.currentProject=current},
 ModelAtelier:{syncProject(){},open(){}},initializeHistory(){},markSaved(){},toast(){},setStatus(){}
};
vm.createContext(ctx);vm.runInContext(code,ctx,{filename:'safe-project-runtime.js'});
(async()=>{
 assert.equal(ctx.se371HasSavedIdentity(),false);
 const original=structuredClone(current);
 await ctx.se371Clone('Crystal Mage Copy');
 assert.equal(seq,1);assert.deepEqual(original.modelAtelier.parts[0].uvPaintOffset,[.25,0]);
 assert.equal(db.get('copy-1').name,'Crystal Mage Copy');
 assert.equal(ctx.se371HasSavedIdentity(),true);
 assert.deepEqual(db.get('copy-1').data.project.particleStudio.emitters,[{id:'spark'}]);
 current.modelAtelier.parts[0].uvPaintOffset=[.5,.1];
 await ctx.se371SaveLocal();
 assert.deepEqual(db.get('copy-1').data.project.modelAtelier.parts[0].uvPaintOffset,[.5,.1]);
 assert.equal(db.size,1,'Save must update the same project ID');
 await ctx.se371Clone('Mage Branch B');
 assert.equal(db.size,2);
 assert.deepEqual(db.get('copy-1').data.project.modelAtelier.parts[0].uvPaintOffset,[.5,.1]);
 assert.equal(db.get('copy-2').name,'Mage Branch B');
 assert.equal(cloudSaves,0,'Offline clone never triggers account save');
 ctx.currentProject={name:'Particle Starter',template:'particle-studio',kind:'vfx',particleStudio:{emitters:[{id:'smoke'}]}};
 current=ctx.currentProject;
 await ctx.se371Save();
 assert.equal(db.size,3);
 assert.equal(db.get('copy-3').name,'Particle Starter Copy');
 assert.equal(ctx.se371HasSavedIdentity(),true);
 console.log('SE371_SAVE_CLONE_PASS',JSON.stringify({copies:db.size,starterImmutable:true,modelUVPreserved:true,particlePreserved:true,saveUpdatesById:true}));
})().catch(e=>{console.error(e);process.exitCode=1});
