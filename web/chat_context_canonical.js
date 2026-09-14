(()=>{"use strict";
if(window.__swrlzCanonicalContextInstalled)return;
window.__swrlzCanonicalContextInstalled=true;

const priorFetch=window.fetch.bind(window);
const pendingReceipts=new Map();
const RECEIPT_TTL_MS=10*60*1000;
const RELAY_ID='mask-factual-relay-v1';

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function cleanUserText(value){return String(value||'').replace(/\n\n\[\[SWRLZ_TURN_INTENT:[\s\S]*$/,'').replace(/\[\[(?:social|coding|general) turn\]\][\s\S]*$/i,'').trim()}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function canonicalHistory(payload){
  const fallback=Array.isArray(payload.history)?payload.history:[];
  try{
    const thread=currentThreadSafe();if(!thread||!Array.isArray(thread.messages))return{history:fallback,canonicalCount:0,source:'payload-fallback'};
    const rid=String(payload.requestId||'');let end=thread.messages.findIndex(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);
    if(end<0)end=thread.messages.length;else end=Math.max(0,end-1);
    const prior=thread.messages.slice(0,end).filter(m=>m&&['user','assistant'].includes(m.role)&&String(m.text||m?.meta?.modelText||'').length).slice(-32);
    if(!prior.length&&fallback.length)return{history:fallback,canonicalCount:0,source:'payload-fallback'};
    let canonicalCount=0;
    const history=prior.map(m=>{if(m.role==='assistant'&&typeof m?.meta?.modelText==='string'&&m.meta.modelText.length){canonicalCount++;return{role:'assistant',text:m.meta.modelText.slice(0,2000)}}return{role:m.role,text:(m.role==='user'?cleanUserText(m.text):String(m.text||'')).slice(0,2000)}});
    return{history,canonicalCount,source:'thread-canonical'};
  }catch(error){return{history:fallback,canonicalCount:0,source:'payload-fallback-error',historyError:String(error?.message||error)}}
}
function pruneReceipts(){const now=Date.now();for(const [rid,r] of pendingReceipts.entries())if(!r||now-Number(r.capturedAt||0)>RECEIPT_TTL_MS)pendingReceipts.delete(rid)}
function currentMessage(rid){try{return [...(currentThreadSafe()?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid||''))||null}catch(_){return null}}
function rememberReceipt(payload,diag){pruneReceipts();const receipt={requestId:String(payload?.requestId||''),capturedAt:Date.now(),relayId:RELAY_ID,historySource:diag.source,historyMessages:Array.isArray(diag.history)?diag.history.length:0,assistantHistoryUsingModelText:Number(diag.canonicalCount||0),promptChars:String(payload?.prompt||'').length,cognitiveAuthority:'lalm',clientInterpretation:false,prepareError:String(diag.historyError||'')};if(receipt.requestId)pendingReceipts.set(receipt.requestId,receipt);const message=currentMessage(receipt.requestId);if(message){message.meta=message.meta||{};message.meta.contextCamera={...(message.meta.contextCamera||{}),...receipt}}return receipt}
function preparePayload(payload){if(!payload||typeof payload!=='object')return payload;const prompt=cleanUserText(payload.prompt),diag=canonicalHistory({...payload,prompt});const next={...payload,prompt,history:Array.isArray(diag.history)?diag.history:[]};delete next.swrlzCognitiveContext;next.swrlzClientRelay={contract:RELAY_ID,historySource:diag.source,historyMessages:next.history.length,promptChars:prompt.length,interpretationOwner:'lalm'};rememberReceipt(next,diag);return next}
function buildEnvelope(payload){const prepared=preparePayload(payload);return prepared?.swrlzClientRelay||{contract:RELAY_ID,interpretationOwner:'lalm'}}
function envelopeValid(payload){return Boolean(payload?.swrlzClientRelay?.contract===RELAY_ID&&!payload?.swrlzCognitiveContext)}
function attachReceipt(requestId,message,{consume=false}={}){pruneReceipts();const rid=String(requestId||''),receipt=pendingReceipts.get(rid);if(!receipt||!message)return false;message.meta=message.meta||{};message.meta.contextCamera={...(message.meta.contextCamera||{}),...receipt};if(consume)pendingReceipts.delete(rid);return true}
function peekReceipt(requestId){pruneReceipts();return pendingReceipts.get(String(requestId||''))||null}
function releaseReceipt(requestId){pendingReceipts.delete(String(requestId||''))}

window.fetch=function(input,init={}){if(!isStream(input,init))return priorFetch(input,init);const payload=parseBody(init);if(!payload)return priorFetch(input,init);const next=preparePayload(payload);return priorFetch(input,{...init,body:JSON.stringify(next)})};
window.__swrlzCanonicalContext={version:5,relayId:RELAY_ID,canonicalHistory,preparePayload,buildEnvelope,envelopeValid,attachReceipt,peekReceipt,releaseReceipt,pendingReceipts,policy:'client-relays-facts-and-history-lalm-interprets'};
})();
