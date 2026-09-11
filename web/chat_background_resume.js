(()=>{"use strict";
if(window.__swrlzBackgroundResumeInstalled)return;
window.__swrlzBackgroundResumeInstalled=true;

const STORE_KEY='swrlz.chat.pending-streams.v1';
const MAX_AGE_MS=30*60*1000;
const live=new Set();
const retryTimers=new Map();
const nativeFetch=window.fetch.bind(window);

function loadStore(){
  try{const value=JSON.parse(localStorage.getItem(STORE_KEY)||'{}');return value&&typeof value==='object'?value:{}}catch(_){return {}}
}
function saveStore(store){
  try{localStorage.setItem(STORE_KEY,JSON.stringify(store))}catch(_){}}
function prune(store=loadStore()){
  const now=Date.now();let changed=false;
  for(const [rid,entry] of Object.entries(store)){
    if(!entry||!entry.createdAt||now-Number(entry.createdAt)>MAX_AGE_MS){delete store[rid];changed=true}
  }
  if(changed)saveStore(store);return store
}
function remember(payload,url){
  if(!payload?.requestId)return;
  const store=prune();const rid=String(payload.requestId);
  store[rid]={requestId:rid,threadId:String(payload.threadId||''),url:String(url||'/api/chat?action=stream'),body:payload,createdAt:Number(store[rid]?.createdAt||Date.now()),updatedAt:Date.now()};
  saveStore(store);
}
function forget(rid){
  if(!rid)return;const store=loadStore();if(store[rid]){delete store[rid];saveStore(store)}
  live.delete(rid);const timer=retryTimers.get(rid);if(timer)clearTimeout(timer);retryTimers.delete(rid);
}
function streamUrl(input){
  try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}
}
function isStreamRequest(input,init){
  const method=String(init?.method||input?.method||'GET').toUpperCase();if(method!=='POST')return false;
  const url=streamUrl(input);return /(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(url);
}
function bodyPayload(init){
  if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}
}

window.fetch=async function(input,init={}){
  if(isStreamRequest(input,init)){
    const payload=bodyPayload(init);if(payload?.requestId){remember(payload,streamUrl(input));live.add(String(payload.requestId))}
  }
  return nativeFetch(input,init);
};

function currentContext(rid,threadId){
  try{
    const thread=typeof currentThread==='function'?currentThread():null;if(!thread)return null;
    if(threadId&&String(thread.id||'')!==String(threadId))return null;
    const messages=Array.isArray(thread.messages)?thread.messages:[];
    const message=[...messages].reverse().find(item=>item?.role==='assistant'&&String(item?.meta?.requestId||'')===String(rid));
    return message?{thread,message}:null;
  }catch(_){return null}
}
function phaseNote(message,text){
  if(!message)return;message.meta=message.meta||{};message.meta.phase='RECONNECTING';message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
  const last=message.meta.trail[message.meta.trail.length-1];if(last?.reason!==text)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase:'RECONNECTING',reason:text,at:Date.now()});
  if(message.state!=='complete')message.state='streaming';
  try{saveState()}catch(_){ }try{scheduleRender(false)}catch(_){ }
}

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(baseConsume){
  consumeEvent=function(event,context){
    const message=context?.message;const rid=String(event?.identity?.requestId||message?.meta?.requestId||'');const seq=Number(event?.seq||0);
    if(message){message.meta=message.meta||{};const last=Number(message.meta.backgroundResumeLastSeq||0);if(context?.__swrlzReplay&&seq&&seq<=last)return false;if(seq>last)message.meta.backgroundResumeLastSeq=seq}
    const result=baseConsume(event,context);
    if(rid){const store=loadStore();if(store[rid]){store[rid].updatedAt=Date.now();store[rid].lastSeq=Math.max(Number(store[rid].lastSeq||0),seq||0);saveStore(store)}}
    if(rid&&['COMPLETED','CANCELLED','FAILED'].includes(String(event?.type||'')))forget(rid);
    return result;
  };
}

async function consumeNdjson(response,context,rid){
  if(!response.ok)throw new Error(`HTTP ${response.status}`);
  const reader=response.body?.getReader?.();if(!reader)throw new Error('STREAM_BODY_UNAVAILABLE');
  const decoder=new TextDecoder();let buffer='';
  while(true){const {value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});let nl;while((nl=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,nl).trim();buffer=buffer.slice(nl+1);if(!line)continue;let event;try{event=JSON.parse(line)}catch(_){continue}if(String(event?.identity?.requestId||event?.requestId||rid)!==String(rid))continue;consumeEvent(event,{...context,__swrlzReplay:true})}}
  const tail=(buffer+decoder.decode()).trim();if(tail){try{const event=JSON.parse(tail);consumeEvent(event,{...context,__swrlzReplay:true})}catch(_){}}
}
function scheduleRetry(rid,delay=3500){
  if(retryTimers.has(rid))return;retryTimers.set(rid,setTimeout(()=>{retryTimers.delete(rid);resumeOne(rid)},delay));
}
async function resumeOne(rid){
  if(!rid||live.has(rid)||document.visibilityState==='hidden')return;
  const store=prune();const entry=store[rid];if(!entry)return;
  const context=currentContext(rid,entry.threadId);if(!context)return;
  live.add(rid);phaseNote(context.message,'Reattaching to the server-side generation and catching this Chat view up to the current response state.');
  try{
    const response=await nativeFetch(entry.url||'/api/chat?action=stream',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Accept':'application/x-ndjson','Content-Type':'application/json; charset=utf-8'},body:JSON.stringify(entry.body)});
    await consumeNdjson(response,context,rid);
  }catch(err){
    phaseNote(context.message,`Generation reattach is waiting for the server (${String(err?.message||err)}). The pending request remains saved locally.`);
    if(document.visibilityState!=='hidden')scheduleRetry(rid);
  }finally{live.delete(rid)}
}
function resumeCurrent(){
  const store=prune();let thread=null;try{thread=typeof currentThread==='function'?currentThread():null}catch(_){thread=null}if(!thread)return;
  for(const entry of Object.values(store))if(String(entry?.threadId||'')===String(thread.id||''))resumeOne(String(entry.requestId||''));
}
function persistNow(){
  try{saveState()}catch(_){ }
}

window.addEventListener('pageshow',()=>setTimeout(resumeCurrent,150));
window.addEventListener('focus',()=>setTimeout(resumeCurrent,100));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(resumeCurrent,100);else persistNow()});
window.addEventListener('pagehide',persistNow);
setTimeout(resumeCurrent,500);
setInterval(()=>{if(document.visibilityState==='visible')resumeCurrent()},5000);

window.__swrlzBackgroundResume={resumeCurrent,pending:()=>prune(),live};
})();
