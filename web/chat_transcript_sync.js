(()=>{"use strict";
if(window.__swrlzTranscriptSyncInstalled)return;
window.__swrlzTranscriptSyncInstalled=true;

const TRANSCRIPT_CONTRACT='generation-transcript-v1';
const STREAM_CONTRACT_ID='swrlz_llm_stream_v2';
const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(!baseConsume)return;

const sessions=new Map();

function sessionFor(context){
  const rid=String(context?.requestId||'');
  if(!rid)return null;
  let s=sessions.get(rid);
  if(!s){s={requestId:rid,context,raw:'',networkSeq:0,identity:null,syncing:false,pending:[],syncCount:0,lastSyncAt:0};sessions.set(rid,s)}
  s.context=context;
  return s;
}
function messageFor(s){return s?.context?.message||null}
function saveAndRender(){try{if(typeof saveState==='function')saveState()}catch(_){ }try{if(typeof scheduleRender==='function')scheduleRender(true)}catch(_){ }}
function setStatus(s,phase,label,state){const m=messageFor(s);if(!m)return;m.meta=m.meta||{};m.meta.phase=phase;m.meta.workLabel=label;m.meta.transcriptSync={...(m.meta.transcriptSync||{}),contract:TRANSCRIPT_CONTRACT,state,networkSeq:s.networkSeq,rawChars:s.raw.length,syncCount:s.syncCount,lastSyncAt:s.lastSyncAt};try{if(typeof refs!=='undefined'&&refs?.composerHint&&typeof active!=='undefined'&&active?.requestId===s.requestId)refs.composerHint.textContent=label}catch(_){ }saveAndRender()}
function sleep(ms){return new Promise(resolve=>setTimeout(resolve,ms))}
function auth(){try{return typeof authHeaders==='function'?authHeaders():{'Content-Type':'application/json'}}catch(_){return {'Content-Type':'application/json'}}}
function transcriptUrl(){try{const base=String(API||'/api/chat').replace(/\/$/,'');return base+'/transcript'}catch(_){return '/api/chat/transcript'}}
function fallbackIdentity(rid){return{streamId:'vercel:'+rid,requestId:rid,route:'LOCAL_R39',access:'CLIENT',runtimeId:'swrlz_vercel_chat_bridge_v1',engineId:'',modelId:'',modelSha256:''}}
function terminalEvent(s,snapshot){const type=['COMPLETED','CANCELLED','FAILED'].includes(String(snapshot.terminalType||''))?String(snapshot.terminalType):'COMPLETED';return{protocolVersion:2,schemaVersion:2,contractId:STREAM_CONTRACT_ID,seq:Number(snapshot.lastSeq||0),type,identity:(snapshot.identity&&typeof snapshot.identity==='object'?snapshot.identity:s.identity)||fallbackIdentity(s.requestId),text:'',reason:type==='COMPLETED'?'Generation transcript reached its terminal response state.':'Generation transcript ended before normal completion.',categories:[],phase:String(snapshot.phase|| (type==='COMPLETED'?'COMPLETE':'ERROR')),ingress:'VERCEL_CHAT',answerState:type==='COMPLETED'?'COMMITTED':'PARTIAL_OR_EMPTY',terminal:true}}
function recordNetwork(s,event){if(!event||typeof event!=='object')return;if(event.identity&&typeof event.identity==='object')s.identity={...event.identity};const seq=Number(event.seq||0);if(Number.isInteger(seq)&&seq>s.networkSeq){if(event.type==='DELTA')s.raw+=String(event.text||'');s.networkSeq=seq}}
function forwardNetwork(event,context,s){const seq=Number(event?.seq||0);if(Number.isInteger(seq)&&seq<=s.networkSeq)return;recordNetwork(s,event);return baseConsume(event,context)}

consumeEvent=function(event,context){
  const s=sessionFor(context);if(!s)return baseConsume(event,context);
  if(s.syncing&&!event?.__swrlzTranscriptSync){s.pending.push(event);return}
  return forwardNetwork(event,context,s);
};

function splitCatchup(text){const value=String(text||'');if(!value)return[];const target=44,count=Math.max(1,Math.ceil(value.length/target)),size=Math.ceil(value.length/count),out=[];for(let i=0;i<value.length;i+=size)out.push(value.slice(i,i+size));return out}
async function animateRawSuffix(s,missing){
  const chunks=splitCatchup(missing);if(!chunks.length)return;
  setStatus(s,'CATCHING_UP','Catching up to §wyrlz…','animating');
  for(const chunk of chunks){baseConsume({type:'DELTA',text:chunk,__swrlzTranscriptSync:true},s.context);await sleep(18)}
}
async function flushPending(s){const pending=s.pending.splice(0).sort((a,b)=>Number(a?.seq||0)-Number(b?.seq||0));for(const event of pending){forwardNetwork(event,s.context,s);await Promise.resolve()}}

async function syncSession(s,reason){
  if(!s||s.syncing||s.context?.terminal)return;
  s.syncing=true;s.syncCount++;s.lastSyncAt=Date.now();
  setStatus(s,'RECONNECTING','Synchronizing with §wyrlz…','requesting-snapshot');
  try{
    const response=await fetch(transcriptUrl(),{method:'POST',headers:auth(),body:JSON.stringify({requestId:s.requestId,reason:String(reason||'foreground')})});
    if(!response.ok)throw new Error(`Transcript sync HTTP ${response.status}`);
    const snapshot=await response.json();
    if(snapshot?.contract!==TRANSCRIPT_CONTRACT||String(snapshot?.requestId||'')!==s.requestId)throw new Error('Transcript sync contract mismatch');
    const serverText=String(snapshot.text||'');
    if(!serverText.startsWith(s.raw)){
      const m=messageFor(s);if(m){m.meta=m.meta||{};m.meta.transcriptSync={...(m.meta.transcriptSync||{}),state:'prefix-mismatch',localRawChars:s.raw.length,serverRawChars:serverText.length,lastSyncAt:s.lastSyncAt}}
      throw new Error('Transcript prefix mismatch; falling back to normal event replay');
    }
    const missing=serverText.slice(s.raw.length);
    if(missing)await animateRawSuffix(s,missing);
    s.raw=serverText;
    s.networkSeq=Math.max(s.networkSeq,Number(snapshot.lastSeq||0));
    const m=messageFor(s);if(m){m.meta=m.meta||{};m.meta.transcriptSync={contract:TRANSCRIPT_CONTRACT,state:snapshot.terminal?'terminal-synced':'live-synced',networkSeq:s.networkSeq,rawChars:s.raw.length,textRevision:Number(snapshot.textRevision||0),phase:String(snapshot.phase||''),syncCount:s.syncCount,lastSyncAt:s.lastSyncAt,reason:String(reason||'foreground')}}
    if(snapshot.terminal&&!s.context?.terminal&&Number(snapshot.lastSeq||0)>Number(s.context?.lastSeq||0)){baseConsume(terminalEvent(s,snapshot),s.context)}
    else if(!snapshot.terminal)setStatus(s,'GENERATING','Writing response…','live-synced');
  }catch(err){const m=messageFor(s);if(m){m.meta=m.meta||{};m.meta.transcriptSync={...(m.meta.transcriptSync||{}),state:'fallback-event-replay',error:String(err?.message||err),lastSyncAt:s.lastSyncAt}}}
  finally{s.syncing=false;await flushPending(s);saveAndRender()}
}

function syncActive(reason){for(const s of sessions.values()){const m=messageFor(s);if(m&&['streaming','cancelling'].includes(String(m.state||'')))syncSession(s,reason)}}
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')syncActive('foreground')});
window.addEventListener('pageshow',()=>syncActive('pageshow'));
window.addEventListener('online',()=>syncActive('online'));

window.__swrlzTranscriptSync={version:1,contract:TRANSCRIPT_CONTRACT,policy:'server-transcript-authoritative-browser-final-copy',syncActive};
})();
