/* SE468_STANDALONE_STUDIO_ASSETS_START */
(function se468StudioAssets(){
 'use strict';
 const PREFIX='swrlz.engine.assets.v1.';
 const KEY={modeler:PREFIX+'modeler',particles:PREFIX+'particles'};
 const LABEL={modeler:'Model',particles:'Particle'};
 const MAX=8*1024*1024;
 const cloudRefs=new Map(),localCache=new Map();
 let busy=false,connected=false,cloudRows=[],userKey='',lastAutoKey='',autoRestoredKey='';
 const api=()=>window.SWYRL_ENGINE_ACCOUNT_ASSETS;
 const mode=()=>window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles'?'particles':
  window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()?'modeler':null;
 function clean(name){return String(name||'Untitled').trim().slice(0,80)||'Untitled';}
 function read(type){
  if(localCache.has(type))return localCache.get(type);
  let rows=[];
  try{
   const parsed=JSON.parse(localStorage.getItem(KEY[type])||'[]');
   if(Array.isArray(parsed))rows=parsed.filter(r=>r?.schema==='swrlz-asset-record-v1'&&r.type===type&&typeof r.id==='string'&&r.data&&typeof r.data==='object').slice(0,30);
  }catch(error){console.warn('§E asset library read',error);}
  localCache.set(type,rows);return rows;
 }
 function persist(type,rows){
  const raw=JSON.stringify(rows);
  if(raw.length>MAX)throw Error('Local asset library is full. Export older assets before saving.');
  localStorage.setItem(KEY[type],raw);
  localCache.set(type,rows);
 }
 function modelData(){
  const ws=window.SWYRL_ENGINE_WORKSPACES;
  const value=ws?.usingScratch?.()?ws.scratchModel():currentProject?.kind==='model-atelier'?currentProject.modelAtelier:null;
  if(!value||value.schema!=='swyrl-model-atelier-v1'||!Array.isArray(value.parts))throw Error('Open a valid model first.');
  return structuredClone(value);
 }
 function particleData(){
  const value=window.SWYRL_ENGINE_PARTICLES?.export?.();
  if(!value||value.schema!=='swyrl-particle-studio-v1'||!Array.isArray(value.emitters))throw Error('Open Particle Studio first.');
  return structuredClone(value);
 }
 function snapshot(type){
  const data=type==='modeler'?modelData():particleData();
  const name=clean(data.name||data.title||LABEL[type]+' asset');
  return {schema:'swrlz-asset-record-v1',type,id:crypto.randomUUID(),name,updatedAt:new Date().toISOString(),data};
 }
 function envelope(record){
  // Existing authenticated cloud storage accepts native scene documents.
  // The envelope is an asset, not a game project, and is NEVER passed to loadProject.
  return {project:{kind:record.type==='modeler'?'model-atelier':'particle-studio',
   name:record.name,assetLibrarySchema:'swrlz-asset-record-v1',
   ...(record.type==='modeler'?{modelAtelier:record.data}:{particleStudio:record.data})},
   editor:{studioWorkspace:record.type},scene:{actors:[]},assetRecord:{
    schema:record.schema,id:record.id,type:record.type,name:record.name,updatedAt:record.updatedAt}};
 }
 function decode(doc,type){
  const meta=doc?.assetRecord,p=doc?.project;
  if(meta?.schema!=='swrlz-asset-record-v1'||meta.type!==type||!p||!Array.isArray(doc.scene?.actors))throw Error('This is not a standalone '+LABEL[type]+' asset.');
  const data=type==='modeler'?p.modelAtelier:p.particleStudio;
  if(!data||data.schema!==(type==='modeler'?'swyrl-model-atelier-v1':'swyrl-particle-studio-v1'))throw Error('Asset schema mismatch.');
  return {schema:'swrlz-asset-record-v1',type,id:meta.id,name:clean(meta.name),updatedAt:meta.updatedAt,data};
 }
 function load(type,record){
  if(type==='modeler'){
   if(!window.SWYRL_ENGINE_WORKSPACES?.loadStandaloneModel?.(structuredClone(record.data)))throw Error('Model Studio rejected this model.');
  }else{
   if(!window.SWYRL_ENGINE_PARTICLES?.import?.(structuredClone(record.data)))throw Error('Particle Studio rejected this effect.');
  }
  status('Loaded '+record.name+' into '+LABEL[type]+' Studio. Game project unchanged.');
 }
 function status(text,error=false){
  const el=document.getElementById('se468AssetStatus');
  if(el){el.textContent=text;el.dataset.error=String(error);}
 }
 function refresh(){
  const type=mode(),bar=document.getElementById('se468AssetBar');
  if(!bar)return;
  bar.hidden=!type;
  if(!type)return;
  const dock=type==='modeler'?document.querySelector('#modelAtelierPanel .atelier-inspector'):document.getElementById('se223Panel');
  if(dock&&bar.parentElement!==dock)dock.prepend(bar);
  const sel=bar.querySelector('select');
  const previous=sel.value;
  sel.replaceChildren();
  const placeholder=document.createElement('option');placeholder.value='';placeholder.textContent='Select saved '+LABEL[type].toLowerCase()+' asset';sel.append(placeholder);
  const local=document.createElement('optgroup');local.label='Saved on this device';
  for(const item of read(type)){
   const opt=document.createElement('option');opt.value='local:'+item.id;opt.textContent=item.name;local.append(opt);
  }
  if(local.children.length)sel.append(local);
  if(connected){
   const group=document.createElement('optgroup');group.label='Saved to Google-connected account';
   for(const item of cloudRows.filter(r=>r.type===type)){
    const opt=document.createElement('option');opt.value='cloud:'+item.id;opt.textContent=item.name;group.append(opt);
   }
   if(group.children.length)sel.append(group);
  }
  if([...sel.options].some(x=>x.value===previous))sel.value=previous;
  bar.querySelector('#se468CloudSave').disabled=!connected||busy;
  bar.querySelector('#se468CloudRefresh').disabled=!connected||busy;
  bar.querySelector('#se468Load').disabled=busy;
 }
 async function listCloud(){
  if(!connected||!api()?.list)return;
  const result=await api().list();
  const projects=Array.isArray(result.projects)?result.projects:[];
  cloudRows=projects.filter(x=>typeof x.name==='string'&&x.name.startsWith('§E Asset · '))
   .map(x=>({id:x.id,name:x.name.slice('§E Asset · '.length),revision:x.revision,
    type:x.name.includes('[Model]')?'modeler':x.name.includes('[Particle]')?'particles':null}))
   .filter(x=>x.type);
  refresh();
  // Restore only into an empty standalone draft, never overwrite edits or
  // load a game project. Account metadata does not carry editable geometry.
  const type=mode(),autoKey=userKey+':'+type;
  if(type&&autoRestoredKey!==autoKey&&!busy){
   autoRestoredKey=autoKey;
   const blank=type==='modeler'
    ?window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()&&
      window.SWYRL_ENGINE_WORKSPACES.scratchModel()?.parts?.length===0
    :window.SWYRL_ENGINE_PARTICLES?.export?.()?.emitters?.length===0;
   const latest=cloudRows.find(x=>x.type===type);
   if(blank&&latest){
    try{
     const result=await api().load(latest.id);
     if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX)throw Error('Invalid asset download.');
     const record=decode(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result.bytes)),type);
     // Recheck: never overwrite work created while the download was pending.
     const stillBlank=type==='modeler'
      ?window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()&&window.SWYRL_ENGINE_WORKSPACES.scratchModel()?.parts?.length===0
      :window.SWYRL_ENGINE_PARTICLES?.export?.()?.emitters?.length===0;
     if(stillBlank)load(type,record);
    }catch(error){status('Account auto-restore unavailable: '+error.message,true);}
   }
  }
 }
 async function save(type,cloud){
  if(busy)return;
  busy=true;refresh();
  try{
   const record=snapshot(type);
   const existing=read(type);
   persist(type,[record,...existing].slice(0,30));
   status('Saved '+record.name+' on this device.');
   if(cloud){
    if(!connected||!api()?.save)throw Error('Connect your Google account in the Chat panel first.');
    const payload=new TextEncoder().encode(JSON.stringify(envelope(record)));
    if(payload.byteLength>MAX)throw Error('Asset exceeds the 8 MiB account limit.');
    const result=await api().save(payload.buffer,'§E Asset · ['+(type==='modeler'?'Model':'Particle')+'] '+record.name);
    if(result.durable!==true||!result.project?.id)throw Error('Account did not confirm durable storage.');
    cloudRefs.set(record.id,result.project);
    status('Saved '+record.name+' to your Google-connected account.');
    await listCloud();
   }
  }catch(error){status('Save failed: '+error.message,true);}
  finally{busy=false;refresh();}
 }
 async function loadSelection(){
  const type=mode(),value=document.querySelector('#se468AssetBar select')?.value;
  if(!type||!value||busy)return;
  busy=true;refresh();
  try{
   if(value.startsWith('local:')){
    const record=read(type).find(x=>x.id===value.slice(6));
    if(!record)throw Error('Local asset not found.');
    load(type,record);
   }else if(value.startsWith('cloud:')){
    if(!connected||!api()?.load)throw Error('Account not connected.');
    const result=await api().load(value.slice(6));
    if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX)throw Error('Invalid asset download.');
    const doc=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result.bytes));
    const record=decode(doc,type);
    load(type,record);
    persist(type,[record,...read(type).filter(x=>x.id!==record.id)].slice(0,30));
   }
  }catch(error){status('Load failed: '+error.message,true);}
  finally{busy=false;refresh();}
 }
 function install(){
  if(document.getElementById('se468AssetBar'))return;
  const bar=document.createElement('section');
  bar.id='se468AssetBar';bar.hidden=true;bar.setAttribute('aria-label','Standalone studio asset library');
  bar.innerHTML='<strong>Studio assets</strong><select aria-label="Saved studio assets"></select><button id="se468LocalSave" type="button">Save locally</button><button id="se468CloudSave" type="button">Save to account</button><button id="se468CloudRefresh" type="button">Refresh account</button><button id="se468Load" type="button">Load selected</button><span id="se468AssetStatus" role="status">Assets stay separate from Game Studio until explicitly imported.</span>';
  const style=document.createElement('style');style.textContent=
   '#se468AssetBar{position:relative;z-index:1;background:#152238;color:#f0f7ff;border:1px solid #64839d;border-radius:12px;padding:8px;display:flex;align-items:center;flex-wrap:wrap;gap:6px;width:100%;max-width:100%;max-height:none;overflow:auto;box-shadow:0 6px 25px #0009;font:12px system-ui}#se468AssetBar[hidden]{display:none!important}#se468AssetBar button,#se468AssetBar select{min-height:34px;background:#243650;color:white;border:1px solid #7891a9;border-radius:6px;padding:5px}#se468AssetBar select{flex:1;min-width:130px}#se468AssetStatus{flex-basis:100%}#se468AssetStatus[data-error=true]{color:#ffb2a5}';
  document.head.append(style);document.body.append(bar);
  bar.querySelector('#se468LocalSave').onclick=()=>void save(mode(),false);
  bar.querySelector('#se468CloudSave').onclick=()=>void save(mode(),true);
  bar.querySelector('#se468CloudRefresh').onclick=()=>void listCloud().catch(e=>status(e.message,true));
  bar.querySelector('#se468Load').onclick=()=>void loadSelection();
  // The existing account bridge owns Google auth; no duplicate token or cookie handling.
  window.addEventListener('swrlz:account-assets',event=>{
   const detail=event.detail||{};
   const identity=String(detail.user?.id||detail.user?.email||'');
   const changed=identity!==userKey;
   connected=detail.authenticated===true&&!!identity;
   if(changed){cloudRows=[];userKey=identity;cloudRefs.clear();}
   refresh();
   if(connected&&changed&&lastAutoKey!==identity){
    lastAutoKey=identity;void listCloud().catch(e=>status('Account library: '+e.message,true));
   }
  });
  window.addEventListener('swrlz:project-loaded',refresh);
  document.addEventListener('click',e=>{if(e.target.closest('.se187-workspace-tabs,.se223-studio-tab,[data-se225-tab]'))queueMicrotask(refresh);},true);
  setInterval(refresh,1500);
  refresh();
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else queueMicrotask(install);
 window.SWYRL_ENGINE_ASSET_LIBRARY=Object.freeze({refresh,save,loadSelection,read,inspect:()=>({connected,cloudCount:cloudRows.length,modelCount:read('modeler').length,particleCount:read('particles').length})});
})();
/* SE468_STANDALONE_STUDIO_ASSETS_END */