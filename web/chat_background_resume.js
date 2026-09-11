(()=>{"use strict";
if(window.__swrlzBackgroundResumeInstalled)return;
window.__swrlzBackgroundResumeInstalled=true;

const STORE_KEY='swrlz.chat.pending-streams.v1';
const MAX_AGE_MS=30*60*1000;
const live=new Set();
const retryTimers=new Map();
const nativeFetch=window.fetch.bind(window);
const CHAT_RESPONSE_DIRECTIVE='Answer naturally without printing, announcing, or signing with the assistant name unless the user explicitly asks about identity or the name. For programming requests, unless the user explicitly asks for code only, give a short natural lead-in, then complete runnable code, then a concise explanation or overview of what the code does, and finish with one short natural closing sentence after the explanation. Keep code, explanation, and claims mutually consistent and verify syntax, formulas, input/output behavior, and requested requirements before ending.';

function loadStore(){try{const value=JSON.parse(localStorage.getItem(STORE_KEY)||'{}');return value&&typeof value==='object'?value:{}}catch(_){return {}}}
function saveStore(store){try{localStorage.setItem(STORE_KEY,JSON.stringify(store))}catch(_){}}
function prune(store=loadStore()){
  const now=Date.now();let changed=false;
  for(const [rid,entry] of Object.entries(store))if(!entry||!entry.createdAt||now-Number(entry.createdAt)>MAX_AGE_MS){delete store[rid];changed=true}
  if(changed)saveStore(store);return store;
}
function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStreamRequest(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();if(method!=='POST')return false;return /(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function bodyPayload(init){if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}}
function normalizePayload(payload){if(!payload||typeof payload!=='object')return payload;const next={...payload};if(!String(next.responseDirective||'').trim())next.responseDirective=CHAT_RESPONSE_DIRECTIVE;return next}
function recoveryHeaders(){
  try{if(typeof authHeaders==='function')return {...authHeaders(),Accept:'application/x-ndjson'}}catch(_){ }
  return {'Accept':'application/x-ndjson','Content-Type':'application/json; charset=utf-8'};
}

async function serverInstanceId(){
  try{const response=await nativeFetch('/api/server/status',{cache:'no-store',credentials:'same-origin'});if(!response.ok)return '';const value=await response.json();return String(value?.instanceId||'')}catch(_){return ''}
}
async function captureOriginInstance(rid){
  const instanceId=await serverInstanceId();if(!instanceId)return;
  const store=loadStore();const entry=store[rid];if(!entry)return;
  if(!entry.originInstanceId)entry.originInstanceId=instanceId;entry.lastSeenInstanceId=instanceId;entry.updatedAt=Date.now();saveStore(store);
}
function remember(payload,url){
  if(!payload?.requestId)return;
  const store=prune(),rid=String(payload.requestId),old=store[rid]||{};
  store[rid]={...old,requestId:rid,threadId:String(payload.threadId||''),url:String(url||'/api/chat?action=stream'),body:payload,createdAt:Number(old.createdAt||Date.now()),updatedAt:Date.now()};
  saveStore(store);captureOriginInstance(rid);
}
function forget(rid){
  if(!rid)return;const store=loadStore();if(store[rid]){delete store[rid];saveStore(store)}
  live.delete(rid);const timer=retryTimers.get(rid);if(timer)clearTimeout(timer);retryTimers.delete(rid);
}

window.fetch=async function(input,init={}){
  if(!isStreamRequest(input,init))return nativeFetch(input,init);
  const raw=bodyPayload(init),payload=normalizePayload(raw),rid=String(payload?.requestId||'');
  const nextInit=payload?{...init,body:JSON.stringify(payload)}:init;
  if(rid)remember(payload,streamUrl(input));
  try{return await nativeFetch(input,nextInit)}catch(err){if(rid)setTimeout(()=>resumeOne(rid),80);throw err}
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
function phaseNote(message,text,phase='RECONNECTING'){
  if(!message)return;message.meta=message.meta||{};message.meta.phase=phase;message.meta.error='';message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
  const last=message.meta.trail[message.meta.trail.length-1];if(last?.reason!==text)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase,reason:text,at:Date.now()});
  if(message.meta.trail.length>40)message.meta.trail=message.meta.trail.slice(-40);
  if(message.state!=='complete')message.state='streaming';
  try{saveState()}catch(_){ }try{scheduleRender(false)}catch(_){ }
}
function persistEvent(rid,message,seq){
  const store=loadStore(),entry=store[rid];if(!entry)return;
  entry.updatedAt=Date.now();entry.lastSeq=Math.max(Number(entry.lastSeq||0),Number(seq||0));entry.partialText=String(message?.text||'');saveStore(store);
}
async function compareInstance(entry,message){
  const current=await serverInstanceId();if(!current)return;
  const store=loadStore(),saved=store[entry.requestId];if(saved){saved.lastSeenInstanceId=current;saved.updatedAt=Date.now();saveStore(store)}
  const previous=String(entry.lastSeenInstanceId||entry.originInstanceId||'');
  if(previous&&previous!==current){
    message.meta=message.meta||{};message.meta.backgroundInstanceChanged=true;
    phaseNote(message,'A new server instance was detected. The same pending request is being resumed or regenerated and reconciled against the partial response already on this device.');
  }
}

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
function replayDelta(event,context){
  const message=context.message,reconcile=context.__swrlzReconcile,seq=Number(event.seq||0);
  if(!Number.isInteger(seq)||seq<=context.lastSeq)return false;
  if(!event.identity||String(event.identity.requestId||'')!==String(context.requestId))throw new Error('Stream identity mismatch');
  const chunk=String(event.text??'');reconcile.generated+=chunk;
  const baseline=reconcile.baseline;
  let mode=reconcile.mode,target=message.text;
  if(baseline.startsWith(reconcile.generated)){
    mode='compare';target=baseline;
  }else if(reconcile.generated.startsWith(baseline)){
    mode='continue';target=reconcile.generated;
  }else{
    mode='redo';target=reconcile.generated;
    if(!reconcile.redoNoted){reconcile.redoNoted=true;phaseNote(message,'The replacement instance regenerated a different prefix, so Chat switched to a clean redo instead of stitching incompatible text onto the old partial response.','RESTARTING')}
  }
  reconcile.mode=mode;message.text=target;message.meta=message.meta||{};message.meta.backgroundResumeMode=mode;
  if(message.meta.firstDeltaLatencyMs==null&&event.firstDeltaLatencyMs!=null)message.meta.firstDeltaLatencyMs=event.firstDeltaLatencyMs;
  try{if(typeof pushTrace==='function')pushTrace(message,event)}catch(_){ }
  context.lastSeq=seq;
  try{const thread=state?.threads?.find?.(t=>t.id===context.threadId);if(thread)thread.updatedAt=Date.now()}catch(_){ }
  persistEvent(context.requestId,message,seq);try{saveState()}catch(_){ }try{scheduleRender(true)}catch(_){ }
  return true;
}

if(baseConsume){
  consumeEvent=function(event,context){
    const message=context?.message,rid=String(event?.identity?.requestId||message?.meta?.requestId||'');
    if(context?.__swrlzReplay&&event?.type==='DELTA')return replayDelta(event,context);
    if(context?.__swrlzReplay&&event?.type==='RESET'&&context.__swrlzReconcile){context.__swrlzReconcile.baseline='';context.__swrlzReconcile.generated='';context.__swrlzReconcile.mode='redo'}
    const result=baseConsume(event,context);
    if(rid)persistEvent(rid,message,event?.seq);
    if(rid&&['COMPLETED','CANCELLED','FAILED'].includes(String(event?.type||'')))forget(rid);
    return result;
  };
}

async function consumeNdjson(response,context,rid){
  if(!response.ok)throw new Error(`HTTP ${response.status}`);
  const reader=response.body?.getReader?.();if(!reader)throw new Error('STREAM_BODY_UNAVAILABLE');
  const decoder=new TextDecoder();let buffer='';
  while(true){
    const {value,done}=await reader.read();if(done)break;
    buffer+=decoder.decode(value,{stream:true});let nl;
    while((nl=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,nl).trim();buffer=buffer.slice(nl+1);if(!line)continue;let event;try{event=JSON.parse(line)}catch(_){continue}if(String(event?.identity?.requestId||event?.requestId||rid)!==String(rid))continue;consumeEvent(event,context);if(context.terminal)try{await reader.cancel()}catch(_){}}
    if(context.terminal)break;
  }
  const tail=(buffer+decoder.decode()).trim();if(tail&&!context.terminal){try{const event=JSON.parse(tail);consumeEvent(event,context)}catch(_){}}
  if(!context.terminal)throw new Error('STREAM_ENDED_WITHOUT_TERMINAL');
}
function scheduleRetry(rid,delay=1500){if(retryTimers.has(rid))return;retryTimers.set(rid,setTimeout(()=>{retryTimers.delete(rid);resumeOne(rid)},delay))}
async function resumeOne(rid){
  if(!rid||live.has(rid)||document.visibilityState==='hidden')return;
  try{if(typeof active!=='undefined'&&active?.requestId===rid)return}catch(_){ }
  const store=prune(),entry=store[rid];if(!entry)return;
  const found=currentContext(rid,entry.threadId);if(!found)return;
  const context={threadId:found.thread.id,requestId:rid,message:found.message,lastSeq:0,terminal:false,started:performance.now(),__swrlzReplay:true,__swrlzReconcile:{baseline:String(found.message.text||entry.partialText||''),generated:'',mode:'compare',redoNoted:false}};
  live.add(rid);phaseNote(found.message,'Checking the pending server generation now. Existing work will continue; if the worker moved, the same request will restart immediately and reconcile against the partial response already shown.');
  compareInstance(entry,found.message);
  try{
    const response=await nativeFetch(entry.url||'/api/chat?action=stream',{method:'POST',credentials:'same-origin',cache:'no-store',headers:recoveryHeaders(),body:JSON.stringify(entry.body)});
    if(response.status===401){
      phaseNote(found.message,'Generation recovery is waiting for the current Chat access token before it can reattach.','RECONNECTING');
      return;
    }
    await consumeNdjson(response,context,rid);
  }catch(err){
    phaseNote(found.message,`Generation recovery is retrying (${String(err?.message||err)}). The pending request remains saved on this device.`);
    if(document.visibilityState!=='hidden')scheduleRetry(rid);
  }finally{live.delete(rid)}
}
function resumeCurrent(){
  const store=prune();let thread=null;try{thread=typeof currentThread==='function'?currentThread():null}catch(_){thread=null}if(!thread)return;
  for(const entry of Object.values(store))if(String(entry?.threadId||'')===String(thread.id||''))resumeOne(String(entry.requestId||''));
}
function persistNow(){try{saveState()}catch(_){ }}

window.addEventListener('pageshow',()=>setTimeout(resumeCurrent,80));
window.addEventListener('focus',()=>setTimeout(resumeCurrent,60));
window.addEventListener('online',()=>setTimeout(resumeCurrent,60));
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(resumeCurrent,60);else persistNow()});
window.addEventListener('pagehide',persistNow);
setTimeout(resumeCurrent,300);
setInterval(()=>{if(document.visibilityState==='visible')resumeCurrent()},2500);

window.__swrlzBackgroundResume={resumeCurrent,pending:()=>prune(),live};
})();