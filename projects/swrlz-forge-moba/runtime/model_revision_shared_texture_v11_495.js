/* §E v11.495 — portable, texture-deduplicated revision snapshots.
   Legacy gzip+base64 entries remain readable. No server/identity changes. */
const se495RevisionCodec=(()=>{
 'use strict';
 const base=window.SWYRL_ENGINE_REVISIONS_486;
 const PREFIX='@se495:shared-paint:',MAX=96*1024*1024,LIMIT=base.LIMIT||8;
 const isPaint=v=>typeof v==='string'&&v.length>65536&&/^data:image\/(png|jpe?g|webp);base64,/i.test(v);
 const validPool=p=>Array.isArray(p)&&p.length<=32&&p.every(v=>typeof v==='string'&&v.length<24*1024*1024);
 const token=n=>PREFIX+n+':end';
 function thin(doc,pool,index){
  const copy=structuredClone(doc);delete copy.se486History;
  const used=new Set(),stack=[copy];
  while(stack.length){
   const node=stack.pop();if(!node||typeof node!=='object')continue;
   if(Array.isArray(node)){for(const item of node)if(item&&typeof item==='object')stack.push(item);continue}
   for(const [key,item] of Object.entries(node)){
    if(key==='uvPaintPNG'&&isPaint(item)){
     let id=index.get(item);
     if(id===undefined){id=pool.length;if(id>=32)throw Error('Too many distinct revision textures');pool.push(item);index.set(item,id)}
     used.add(id);node[key]=token(id);
    }else if(item&&typeof item==='object')stack.push(item);
   }
  }
  return {copy,used:[...used]};
 }
 function hydrate(doc,pool){
  if(!validPool(pool))throw Error('Saved revision texture pool missing');
  const stack=[doc];
  while(stack.length){
   const node=stack.pop();if(!node||typeof node!=='object')continue;
   if(Array.isArray(node)){for(const item of node)if(item&&typeof item==='object')stack.push(item);continue}
   for(const [key,item] of Object.entries(node)){
    if(key==='uvPaintPNG'&&typeof item==='string'&&item.startsWith(PREFIX)){
     const match=/^@se495:shared-paint:(\d+):end$/.exec(item),i=match?Number(match[1]):-1;
     if(!Number.isSafeInteger(i)||i<0||i>=pool.length||!isPaint(pool[i]))
      throw Error('Archived revision references a missing texture');
     node[key]=pool[i];
    }else if(item&&typeof item==='object')stack.push(item);
   }
  }
  return doc;
 }
 async function compact(doc,pool,index,metadata){
  const {copy,used}=thin(doc,pool,index),saved=await base.pack(copy);
  return {...metadata,codec:saved.codec,bytes:saved.bytes,se495SharedTextures:true,se495Refs:used};
 }
 function history(doc){
  const pool=doc?.se486History?.se495TexturePool;
  return base.history(doc).map(entry=>{
   if(!entry.se495SharedTextures)return entry;
   const out={...entry};Object.defineProperty(out,'_se495Pool',{value:pool,enumerable:false});
   return out;
  });
 }
 async function unpack(entry){
  const value=await base.unpack(entry);
  return entry?.se495SharedTextures?hydrate(value,entry._se495Pool):value;
 }
 async function prepare(previous,next,revision,maxBytes,progress=()=>{}){
  if(!Number.isInteger(revision)||revision<1)throw Error('Missing expected project revision');
  const sourcePool=previous?.se486History?.se495TexturePool;
  if(sourcePool!==undefined&&!validPool(sourcePool))throw Error('Prior revision texture pool invalid');
  const pool=sourcePool?sourcePool.slice():[],index=new Map(pool.map((v,i)=>[v,i]));
  const entries=[];
  for(const entry of base.history(previous)){
   if(entry.se495SharedTextures){
    if(!Array.isArray(entry.se495Refs)||entry.se495Refs.some(i=>!Number.isInteger(i)||i<0||i>=pool.length))
     throw Error('Prior revision texture references invalid');
    entries.push({...entry});continue;
   }
   progress('Compacting saved revision '+entry.number+'…');
   const old=await base.unpack(entry);
   entries.push(await compact(old,pool,index,{number:entry.number,savedAt:entry.savedAt}));
  }
  progress('Archiving revision '+revision+' without repeating its texture…');
  entries.push(await compact(previous,pool,index,{number:revision,savedAt:new Date().toISOString()}));
  while(entries.length>=LIMIT)entries.shift();
  const payload=structuredClone(next);delete payload.se486History;
  const cap=Math.max(1024,Math.min(Number(maxBytes)||MAX,MAX));let dropped=0;
  const utf8=new TextEncoder();
  while(true){
   payload.se486History={schema:base.SCHEMA,limit:LIMIT,entries,se495TexturePool:pool};
   if(utf8.encode(JSON.stringify(payload)).byteLength<=cap)
    return {payload,dropped,compact:true,entryCount:entries.length,assetCount:pool.length};
   if(!entries.length)throw Error('Updated project exceeds account storage limit even after history compaction');
   entries.shift();dropped++;
  }
 }
 return Object.freeze({...base,history,unpack,prepare});
})();
window.SWYRL_ENGINE_REVISIONS_495=se495RevisionCodec;
window.SWYRL_ENGINE_REVISIONS_486=se495RevisionCodec;
