(()=>{"use strict";
if(window.__swrlzCanonicalContextInstalled)return;
window.__swrlzCanonicalContextInstalled=true;

const priorFetch=window.fetch.bind(window);
const DIRECTIVE='Assistant identity: your name is §wyrlz. A name the user gives for themself belongs to the user unless they explicitly rename the assistant. If the user asks your name or identity, answer §wyrlz accurately; otherwise do not announce, introduce, or sign with the assistant name. For casual conversation, participate naturally instead of describing the conversational act. Answer only the current user request directly, naturally, and completely. Do not introduce unrelated programming or examples. For programming requests, provide complete runnable code when appropriate and keep code, explanation, formulas, and input/output behavior mutually consistent.';

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function cleanUserText(value){return String(value||'').replace(/\n\n\[\[SWRLZ_TURN_INTENT:[\s\S]*$/,'').replace(/\[\[(?:social|coding|general) turn\]\][\s\S]*$/i,'').trim()}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function canonicalHistory(payload){
  const fallback=Array.isArray(payload.history)?payload.history:[];
  const thread=currentThreadSafe();if(!thread||!Array.isArray(thread.messages))return {history:fallback,canonicalCount:0,source:'payload-fallback'};
  const rid=String(payload.requestId||'');
  let end=thread.messages.findIndex(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);
  if(end<0)end=thread.messages.length;
  else end=Math.max(0,end-1);
  const prior=thread.messages.slice(0,end).filter(m=>m&&['user','assistant'].includes(m.role)&&String(m.text||m?.meta?.modelText||'').length).slice(-32);
  if(!prior.length&&fallback.length)return {history:fallback,canonicalCount:0,source:'payload-fallback'};
  let canonicalCount=0;
  const history=prior.map(m=>{
    if(m.role==='assistant'&&typeof m?.meta?.modelText==='string'&&m.meta.modelText.length){canonicalCount++;return {role:'assistant',text:m.meta.modelText.slice(0,2000)}}
    return {role:m.role,text:(m.role==='user'?cleanUserText(m.text):String(m.text||'')).slice(0,2000)};
  });
  return {history,canonicalCount,source:'thread-canonical'};
}
function annotateRequest(payload,diag){
  try{
    const thread=currentThreadSafe();if(!thread)return;
    const message=[...thread.messages].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(payload.requestId||''));
    if(!message)return;message.meta=message.meta||{};
    message.meta.contextCamera={...(message.meta.contextCamera||{}),turnIntent:String(payload.turnIntent||'unknown'),historySource:diag.source,historyMessages:diag.history.length,assistantHistoryUsingModelText:diag.canonicalCount,promptChars:String(payload.prompt||'').length,directiveId:'identity-social-canonical-v1'};
  }catch(_){ }
}

window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const diag=canonicalHistory(payload);
  const next={...payload,responseDirective:DIRECTIVE,history:diag.history};
  annotateRequest(next,diag);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};

window.__swrlzCanonicalContext={directiveId:'identity-social-canonical-v1',canonicalHistory};
})();
