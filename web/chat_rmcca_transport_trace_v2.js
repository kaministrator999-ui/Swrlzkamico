(()=>{"use strict";
if(window.__swrlzRmccaTransportTraceV2Installed)return;
window.__swrlzRmccaTransportTraceV2Installed=true;
const priorFetch=window.fetch.bind(window);
const CARRIER='[[SWRLZ_RMCCA_TRANSPORT_V1:';
function isStream(input,init){try{const method=String(init?.method||input?.method||'GET').toUpperCase();const url=typeof input==='string'?input:(input?.url||'');return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(url)}catch(_){return false}}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function currentMessage(rid){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid))||null}catch(_){return null}}
function carrierPresent(payload){return Array.isArray(payload?.history)&&payload.history.some(item=>String(item?.text||'').startsWith(CARRIER))}
function stamp(message,patch){if(!message)return;message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};Object.assign(message.meta.contextCamera,patch)}
function canonicalize(payload){const bg=window.__swrlzBackgroundResume;if(bg&&typeof bg.canonicalizePayload==='function')return bg.canonicalizePayload(payload);const ctx=window.__swrlzCanonicalContext;if(ctx&&typeof ctx.preparePayload==='function')return ctx.preparePayload(payload);return payload}
window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const raw=parseBody(init);if(!raw)return priorFetch(input,init);
  const rid=String(raw.requestId||''),message=currentMessage(rid);
  const beforeEnvelope=Boolean(raw?.swrlzCognitiveContext?.cognitiveClock),beforeCarrier=carrierPresent(raw);
  let prepared=raw,error='';try{prepared=canonicalize(raw)||raw}catch(err){error=String(err?.message||err);prepared=raw}
  const guardTrace=window.__swrlzRmccaTransportGuard?.traceByRequest?.get?.(rid)||null;
  const afterEnvelope=Boolean(prepared?.swrlzCognitiveContext?.cognitiveClock);
  const afterCarrier=Boolean(prepared?._swrlzCarrierAttached)||carrierPresent(prepared);
  stamp(message,{rmccaTraceV2:true,rmccaOuterWrapperReached:true,rmccaBeforeOuterEnvelope:beforeEnvelope,rmccaBeforeOuterCarrier:beforeCarrier,rmccaAfterOuterEnvelope:afterEnvelope,rmccaAfterOuterCarrier:afterCarrier,rmccaPreparationPath:String(guardTrace?.path||message?.meta?.contextCamera?.rmccaPreparationPath||'unknown'),rmccaGuardFallbackUsed:Boolean(guardTrace?.fallbackUsed),rmccaOuterError:error,rmccaSerializedBodyChars:JSON.stringify(prepared).length,canonicalRequestPrepared:afterEnvelope,canonicalEnvelopePreserved:afterEnvelope&&afterCarrier,rmccaCarrierAttached:afterCarrier,firstSendReceiptAttached:afterEnvelope});
  return priorFetch(input,{...init,body:JSON.stringify(prepared)});
};
window.__swrlzRmccaTransportTraceV2={version:2,carrier:CARRIER};
})();
