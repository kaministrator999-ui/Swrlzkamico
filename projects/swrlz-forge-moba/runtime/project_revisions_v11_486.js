/* §E v11.486 — bounded, portable revision snapshots for native user projects.
   No credential, database schema, starter or renderer changes. */
const SWYRL_ENGINE_REVISIONS_486=(()=>{
 'use strict';
 const SCHEMA='se-project-revisions-v1',LIMIT=8,DB='swyrl-engine-revisions-v1';
 const stamp=()=>new Date().toISOString();
 const validId=id=>typeof id==='string'&&id.length>0&&id.length<=160&&!/[\x00-\x1f\x7f]/.test(id);
 const utf8=new TextEncoder(),decoder=new TextDecoder('utf-8',{fatal:true});
 function clearHistory(doc){
  const clean=structuredClone(doc);
  if(!clean||typeof clean!=='object')throw Error('Invalid project snapshot');
  delete clean.se486History;
  return clean;
 }
 function b64(bytes){
  let result='';
  for(let i=0;i<bytes.length;i+=8192)
   result+=String.fromCharCode(...bytes.subarray(i,i+8192));
  return btoa(result);
 }
 function un64(value){
  if(typeof value!=='string'||value.length>128*1024*1024)throw Error('Revision data is invalid or too large');
  const s=atob(value),out=new Uint8Array(s.length);
  for(let i=0;i<s.length;i++)out[i]=s.charCodeAt(i);
  return out;
 }
 async function pack(doc){
  const bytes=utf8.encode(JSON.stringify(clearHistory(doc)));
  if(bytes.length>96*1024*1024)throw Error('Snapshot exceeds the native project limit');
  if(typeof CompressionStream!=='function')return {codec:'json+base64',bytes:b64(bytes)};
  const stream=new Blob([bytes]).stream().pipeThrough(new CompressionStream('gzip'));
  return {codec:'gzip+base64',bytes:b64(new Uint8Array(await new Response(stream).arrayBuffer()))};
 }
 async function unpack(entry){
  if(!entry||!['gzip+base64','json+base64'].includes(entry.codec))throw Error('Unsupported revision format');
  const bytes=un64(entry.bytes);let raw=bytes;
  if(entry.codec==='gzip+base64'){
   if(typeof DecompressionStream!=='function')throw Error('This browser cannot decompress saved revisions');
   const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
   raw=new Uint8Array(await new Response(stream).arrayBuffer());
  }
  if(raw.byteLength>96*1024*1024)throw Error('Recovered project exceeds size limits');
  return JSON.parse(decoder.decode(raw));
 }
 function history(doc){
  const h=doc?.se486History;
  if(h?.schema!==SCHEMA||!Array.isArray(h.entries))return [];
  return h.entries.filter(e=>e&&Number.isInteger(e.number)&&e.number>=1&&
   typeof e.savedAt==='string'&&['gzip+base64','json+base64'].includes(e.codec)&&
   typeof e.bytes==='string').slice(-LIMIT+1);
 }
 function withoutHistory(doc){return clearHistory(doc)}
 async function prepare(previous,next,previousNumber,maxBytes){
  if(!Number.isInteger(previousNumber)||previousNumber<1)throw Error('Missing expected project revision');
  const entries=history(previous);
  const saved=await pack(previous);
  entries.push({number:previousNumber,savedAt:stamp(),...saved});
  while(entries.length>=LIMIT)entries.shift();
  const payload=clearHistory(next);
  const max=Math.max(1024,Math.min(Number(maxBytes)||96*1024*1024,96*1024*1024));
  let dropped=0;
  while(true){
   payload.se486History={schema:SCHEMA,limit:LIMIT,entries};
   if(utf8.encode(JSON.stringify(payload)).byteLength<=max)return {payload,dropped};
   if(!entries.length)throw Error('Updated project exceeds account storage limit');
   entries.shift();dropped++;
  }
 }
 function db(){
  return new Promise((resolve,reject)=>{
   if(!indexedDB)return reject(Error('Local revision storage unavailable'));
   const req=indexedDB.open(DB,1);
   req.onupgradeneeded=()=>{if(!req.result.objectStoreNames.contains('projects'))req.result.createObjectStore('projects',{keyPath:'id'})};
   req.onsuccess=()=>resolve(req.result);
   req.onerror=()=>reject(Error('Revision history storage unavailable'));
   req.onblocked=()=>reject(Error('Revision history storage is busy'));
  });
 }
 async function readLocal(id){
  if(!validId(id))throw Error('Invalid project ID');
  const database=await db();
  try{return await new Promise((resolve,reject)=>{
   const req=database.transaction('projects','readonly').objectStore('projects').get(id);
   req.onsuccess=()=>resolve(req.result||null);
   req.onerror=()=>reject(Error('Revision history could not be read'));
  })}finally{database.close()}
 }
 async function recordLocal(id,doc){
  if(!validId(id))throw Error('Invalid project ID');
  const prior=await readLocal(id),newPacked=await pack(doc);
  const seq=(prior?.latest?.number||0)+1;
  const entries=Array.isArray(prior?.entries)?prior.entries.slice(-LIMIT+1):[];
  if(prior?.latest)entries.push(prior.latest);
  while(entries.length>=LIMIT)entries.shift();
  const record={id,latest:{number:seq,savedAt:stamp(),...newPacked},entries};
  const database=await db();
  try{await new Promise((resolve,reject)=>{
   const tx=database.transaction('projects','readwrite');
   tx.objectStore('projects').put(record);
   tx.oncomplete=resolve;tx.onerror=tx.onabort=()=>reject(Error('Could not save revision history'));
  })}finally{database.close()}
  return record;
 }
 function download(name,content){
  const filename=String(name||'project').replace(/[^a-z0-9_.-]+/gi,'-').slice(0,75)||'project';
  const url=URL.createObjectURL(new Blob([JSON.stringify(content,null,2)],{type:'application/json'}));
  const link=document.createElement('a');link.href=url;link.download=filename+'.swyrl-update.json';
  document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }
 async function choose(){
  return new Promise(resolve=>{
   const file=document.createElement('input');file.type='file';file.accept='.json,.swyrl';
   file.style.display='none';document.body.append(file);
   file.addEventListener('change',()=>{const selected=file.files?.[0];file.remove();resolve(selected||null)},{once:true});
   file.addEventListener('cancel',()=>{file.remove();resolve(null)},{once:true});
   file.click();
  });
 }
 function present(title,items,onRestore){
  document.getElementById('se486HistoryDialog')?.remove();
  const el=document.createElement('dialog');el.id='se486HistoryDialog';el.setAttribute('aria-label','Project revision history');
  el.style.cssText='background:#172236;color:#f4f6ff;border:1px solid #8495b9;border-radius:14px;max-width:min(92vw,510px);width:100%;max-height:80dvh;overflow:auto;padding:16px;box-shadow:0 20px 80px #000b;z-index:2147483000';
  const heading=document.createElement('h2');heading.textContent=title;heading.style.margin='0 0 8px';
  const summary=document.createElement('p');summary.textContent='Last '+LIMIT+' explicitly saved revisions, including the current one. Restoring creates a new revision.';summary.style.fontSize='13px';
  const close=document.createElement('button');close.textContent='Close';close.type='button';close.onclick=()=>el.close();
  const list=document.createElement('div');list.style.cssText='display:grid;gap:9px;margin:12px 0';
  const status=document.createElement('p');status.setAttribute('role','status');status.style.fontSize='13px';
  for(const item of items){
   const row=document.createElement('div');row.style.cssText='border:1px solid #506282;border-radius:10px;padding:10px;display:flex;align-items:center;gap:12px;flex-wrap:wrap';
   const label=document.createElement('div');label.style.flex='1';label.textContent='Revision '+item.number+' · '+(item.savedAt||'Saved');
   row.append(label);
   if(item.current){const mark=document.createElement('strong');mark.textContent='Current';row.append(mark);}
   else{
    const button=document.createElement('button');button.type='button';button.textContent='Restore';
    button.onclick=async()=>{
     if(!confirm('Restore revision '+item.number+' to this same project? Your current saved revision will remain in history.'))return;
     button.disabled=true;status.textContent='Restoring revision '+item.number+'…';
     try{await onRestore(item);status.textContent='Revision restored and saved. Reopen History to inspect the newest revision.';el.close();}
     catch(error){status.textContent='Restore failed: '+String(error?.message||error).slice(0,170);button.disabled=false;}
    };row.append(button);
   }
   list.append(row);
  }
  el.append(heading,summary,list,status,close);document.body.append(el);
  el.addEventListener('close',()=>el.remove(),{once:true});
  if(typeof el.showModal==='function')el.showModal();else el.setAttribute('open','');
  return el;
 }
 return Object.freeze({SCHEMA,LIMIT,history,withoutHistory,pack,unpack,prepare,readLocal,recordLocal,download,choose,present});
})();
window.SWYRL_ENGINE_REVISIONS_486=SWYRL_ENGINE_REVISIONS_486;
