(()=>{"use strict";
if(window.__swrlzBackgroundResumeInstalled)return;
window.__swrlzBackgroundResumeInstalled=true;

const STORE_KEY='swrlz.chat.pending-streams.v1';
const MAX_AGE_MS=30*60*1000;
const live=new Set();
const retryTimers=new Map();
const nativeFetch=window.fetch.bind(window);
const INTENT_MARK='[[SWRLZ_TURN_INTENT:';

function cleanTurnText(value){
  let text=String(value||'');
  const markers=['\n\n'+INTENT_MARK,INTENT_MARK,'[[social turn]]','[[coding turn]]','[[general turn]]'];
  for(const marker of markers){const at=text.indexOf(marker);if(at>=0)text=text.slice(0,at)}
  return text.trim();
}
function classifyIntent(value){
  const text=cleanTurnText(value),words=text.split(/\s+/).filter(Boolean).length;
  const code=/\b(code|coding|program|programming|function|class|method|script|html|css|javascript|typescript|python|c\+\+|cpp|java|kotlin|rust|sql|api|json|implement|debug|refactor|snippet|compile|compiler)\b|\.(?:cpp|h|hpp|py|js|ts|html|css)\b/i.test(text);
  if(code)return 'coding';
  const social=/^(?:hey|hi|hello|yo|sup|thanks|thank you|lol|lmao|😂|😆|👋|🙂|😊|❤️|🫂)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$/i.test(text);
  if(words<=10&&social)return 'social';
  return 'general';
}
function normalizeHistory(history){
  return Array.isArray(history)?history.map(item=>{
    if(!item||typeof item!=='object')return item;
    const next={...item};
    if(String(next.role||'').toLowerCase()==='user')next.text=cleanTurnText(next.text);
    return next;
  }):history;
}
function fallbackNormalizePayload(payload){
  if(!payload||typeof payload!=='object')return payload;
  const next={...payload};
  const prompt=cleanTurnText(next.prompt);
  next.prompt=prompt;
  next.history=normalizeHistory(next.history);
  if(!next.turnIntent)next.turnIntent=classifyIntent(prompt);
  return next;
}
function canonicalizePayload(payload){
  const normalized=fallbackNormalizePayload(payload);
  try{
    const prepare=window.__swrlzCanonicalContext?.preparePayload;
    if(typeof prepare==='function')return prepare(normalized);
  }catch(_){ }
  return normalized;
}

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
function chatAuthHeaders(){
  try{if(typeof window.authHeaders==='function')return {...window.authHeaders()}}catch(_){ }
  let value='';try{value=sessionStorage.getItem('swrlzChatToken')||sessionStorage.getItem('swrlz.chat.token')||''}catch(_){ }
  return {'Content-Type':'application/json','X-SWRLZ-Chat-Token':value};
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
  const store=prune(),rid=String(payload.requestId),old=store[rid]||{},stamp=Date.now();
  store[rid]={...old,requestId:rid,threadId:String(payload.threadId||''),url:String(url||'/api/chat?action=stream'),body:payload,createdAt:Number(old.createdAt||stamp),requestStartedAt:Number(old.requestStartedAt||stamp),updatedAt:stamp,recoveryAttempts:Number(old.recoveryAttempts||0)};
  saveStore(store);captureOriginInstance(rid);
}
function forget(rid){
  if(!rid)return;const store=loadStore();if(store[rid]){delete store[rid];saveStore(store)}
  live.delete(rid);const timer=retryTimers.get(rid);if(timer)clearTimeout(timer);retryTimers.delete(rid);
}

window.fetch=async function(input,init={}){
  if(!isStreamRequest(input,init))return nativeFetch(input,init);
  const raw=bodyPayload(init),payload=canonicalizePayload(raw),rid=String(payload?.requestId||'');
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
  if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);
  if(message.state!=='complete')message.state='streaming';
  try{saveState()}catch(_){ }try{scheduleRender(false)}catch(_){ }
}
function persistEvent(rid,message,seq){
  const store=loadStore(),entry=store[rid];if(!entry)return;
  entry.updatedAt=Date.now();entry.lastSeq=Math.max(Number(entry.lastSeq||0),Number(seq||0));entry.partialText=String(message?.text||'');saveStore(store);
}
function markRecoveryCamera(message,entry,body){
  if(!message)return;message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};
  const camera=message.meta.contextCamera,envelope=body?.swrlzCognitiveContext;
  camera.recoveryAttempts=Number(entry?.recoveryAttempts||0);
  camera.requestStartedAt=Number(entry?.requestStartedAt||entry?.createdAt||0);
  camera.recoveryElapsedMs=camera.requestStartedAt?Math.max(0,Date.now()-camera.requestStartedAt):null;
  camera.canonicalEnvelopePreserved=Boolean(envelope?.envelopeId&&envelope?.directiveId);
  if(envelope){camera.directiveId=envelope.directiveId;camera.canonicalEnvelopeId=envelope.envelopeId;camera.cognitiveAuthority='chat_context_canonical';camera.cognitiveClock=envelope.cognitiveClock;camera.historySource=envelope.historySource;camera.historyMessages=envelope.historyMessages;camera.assistantHistoryUsingModelText=envelope.assistantHistoryUsingModelText;}
}
async function compareInstance(entry,message){
  const current=await serverInstanceId();if(!current)return;
  const store=loadStore(),saved=store[entry.requestId];if(saved){saved.lastSeenInstanceId=current;saved.updatedAt=Date.now();saveStore(store)}
  const previous=String(entry.lastSeenInstanceId||entry.originInstanceId||'');
  if(previous&&previous!==current){message.meta=message.meta||{};message.meta.backgroundInstanceChanged=true;phaseNote(message,'Server instance changed. The same canonical request is being resumed or regenerated and reconciled against the partial response already on this device.')}
}

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
function replayDelta(event,context){
  const message=context.message,reconcile=context.__swrlzReconcile,seq=Number(event.seq||0);
  if(!Number.isInteger(seq)||seq<=context.lastSeq)return false;
  if(!event.identity||String(event.identity.requestId||'')!==String(context.requestId))throw new Error('Stream identity mismatch');
  const chunk=String(event.text??'');reconcile.generated+=chunk;
  const baseline=reconcile.baseline;
  let mode=reconcile.mode,target=message.text;
  if(baseline.startsWith(reconcile.generated)){mode='compare';target=baseline}
  else if(reconcile.generated.startsWith(baseline)){mode='continue';target=reconcile.generated}
  else{mode='redo';target=reconcile.generated;if(!reconcile.redoNoted){reconcile.redoNoted=true;phaseNote(message,'The regenerated response diverged from the saved partial, so Chat switched to a clean redo instead of stitching incompatible text together.','RESTARTING')}}
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
  try{if(typeof active!=='undefined'&&active?.requestId===rid&&active?.controller&&!active.controller.signal.aborted)return}catch(_){ }
  const store=prune(),entry=store[rid];if(!entry)return;
  const found=currentContext(rid,entry.threadId);if(!found)return;
  entry.recoveryAttempts=Number(entry.recoveryAttempts||0)+1;entry.updatedAt=Date.now();saveStore(store);
  const body=canonicalizePayload(entry.body);entry.body=body;saveStore(store);markRecoveryCamera(found.message,entry,body);
  const context={threadId:found.thread.id,requestId:rid,message:found.message,lastSeq:0,terminal:false,started:performance.now(),requestStartedAt:Number(entry.requestStartedAt||entry.createdAt||Date.now()),__swrlzReplay:true,__swrlzReconcile:{baseline:String(found.message.text||entry.partialText||''),generated:'',mode:'compare',redoNoted:false}};
  live.add(rid);phaseNote(found.message,'Checking the pending canonical server generation now. Existing work will continue if available; otherwise the exact same cognitive request will restart and reconcile against the saved partial.');
  await compareInstance(entry,found.message);
  try{
    const allHeaders={...chatAuthHeaders(),'Accept':'application/x-ndjson'};
    const response=await nativeFetch(entry.url||'/api/chat?action=stream',{method:'POST',credentials:'same-origin',cache:'no-store',headers:allHeaders,body:JSON.stringify(body)});
    if(response.status===401){phaseNote(found.message,'Generation recovery needs a valid Chat access token before it can reconnect.','AUTH_REQUIRED');return}
    await consumeNdjson(response,context,rid);
  }catch(err){
    const text=String(err?.message||err);phaseNote(found.message,`Generation recovery is retrying (${text}). The pending canonical request remains saved on this device.`);
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
setInterval(()=>{if(document.visibilityState==='visible')resumeCurrent()},1800);

window.__swrlzBackgroundResume={resumeCurrent,pending:()=>prune(),live,classifyIntent,cleanTurnText,canonicalizePayload};
})();
