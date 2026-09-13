(()=>{"use strict";
if(window.__swrlzRecoveryIntegrityInstalled)return;
window.__swrlzRecoveryIntegrityInstalled=true;

const CARRIER='[[SWRLZ_RMCCA_TRANSPORT_V1:';
const STORE_KEY='swrlz.chat.pending-streams.v1';
const priorFetch=window.fetch.bind(window);

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}}
function isCarrierText(value){return String(value||'').startsWith(CARRIER)}
function compactCarrier(payload){
  const e=payload?.swrlzCognitiveContext,t=payload?.swrlzUserTimeContext;
  if(!e?.cognitiveClock&&!t)return '';
  const data={v:1};
  if(e?.cognitiveClock)data.e={envelopeId:String(e.envelopeId||''),directiveId:String(e.directiveId||''),cognitiveClock:e.cognitiveClock};
  if(t)data.t={localDate:String(t.localDate||''),localTime:String(t.localTime||''),daypart:String(t.daypart||''),timeZone:String(t.timeZone||''),utcOffset:String(t.utcOffset||'')};
  const encoded=JSON.stringify(data);
  return encoded.length<=1800?CARRIER+encoded+']]':'';
}
function withCarrier(payload){
  if(!payload||typeof payload!=='object')return payload;
  let prepared=payload;
  try{const fn=window.__swrlzCanonicalContext?.preparePayload;if(typeof fn==='function')prepared=fn(payload)||payload}catch(_){prepared=payload}
  const carrier=compactCarrier(prepared);if(!carrier)return prepared;
  const history=(Array.isArray(prepared.history)?prepared.history:[]).filter(item=>!isCarrierText(item?.text));
  history.push({role:'assistant',text:carrier});
  return {...prepared,history};
}
window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const next=withCarrier(payload);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};

function pendingStore(){try{const value=JSON.parse(localStorage.getItem(STORE_KEY)||'{}');return value&&typeof value==='object'?value:{}}catch(_){return {}}}
function dropPending(rid){if(!rid)return;try{const store=pendingStore();if(store[rid]){delete store[rid];localStorage.setItem(STORE_KEY,JSON.stringify(store))}}catch(_){}}
function pushLocalTrace(message,phase,reason){
  if(!message)return;message.meta=message.meta||{};message.meta.phase=phase;message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
  const last=message.meta.trail[message.meta.trail.length-1];
  if(last?.reason!==reason)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase,reason,at:Date.now()});
  if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);
}
function preservePartial(context,reason){
  const message=context?.message,reconcile=context?.__swrlzReconcile;if(!message||!reconcile)return false;
  const baseline=String(reconcile.baseline||message.text||'');
  if(!baseline)return false;
  message.text=baseline;message.state='complete';message.meta=message.meta||{};
  message.meta.backgroundResumeMode='partial-preserved';message.meta.recoveryStopped=true;message.meta.recoveryStoppedReason=reason;
  context.terminal=true;context.__swrlzPartialPreserved=true;dropPending(String(context.requestId||message.meta.requestId||''));
  pushLocalTrace(message,'PARTIAL_PRESERVED',reason);
  try{saveState()}catch(_){ }try{scheduleRender(false)}catch(_){ }
  return true;
}

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(baseConsume){
  consumeEvent=function(event,context){
    if(!context?.__swrlzReplay)return baseConsume(event,context);
    const message=context.message,reconcile=context.__swrlzReconcile,rid=String(context.requestId||message?.meta?.requestId||'');
    if(!message||!reconcile)return baseConsume(event,context);
    if(message?.meta?.backgroundInstanceChanged&&String(reconcile.baseline||message.text||'')){
      preservePartial(context,'Server instance changed; preserved the existing partial response instead of regenerating and replacing it.');
      return true;
    }
    const type=String(event?.type||'');
    if(type==='RESET'&&String(reconcile.baseline||message.text||'')){
      preservePartial(context,'Recovery requested a reset; preserved the existing partial response instead of clearing it.');
      return true;
    }
    if(type==='DELTA'){
      const seq=Number(event.seq||0);if(!Number.isInteger(seq)||seq<=Number(context.lastSeq||0))return false;
      if(event.identity&&String(event.identity.requestId||'')!==rid)throw new Error('Stream identity mismatch');
      const chunk=String(event.text??'');const nextGenerated=String(reconcile.generated||'')+chunk;const baseline=String(reconcile.baseline||'');
      reconcile.generated=nextGenerated;
      if(baseline.startsWith(nextGenerated)){
        message.text=baseline;reconcile.mode='compare';message.meta=message.meta||{};message.meta.backgroundResumeMode='compare';
      }else if(nextGenerated.startsWith(baseline)){
        message.text=nextGenerated;reconcile.mode='continue';message.meta=message.meta||{};message.meta.backgroundResumeMode='continue';
      }else{
        preservePartial(context,'Recovered generation diverged from the saved response; automatic redo was stopped to protect the better existing answer.');
        return true;
      }
      context.lastSeq=seq;
      if(message.meta.firstDeltaLatencyMs==null&&event.firstDeltaLatencyMs!=null)message.meta.firstDeltaLatencyMs=event.firstDeltaLatencyMs;
      try{if(typeof pushTrace==='function')pushTrace(message,event)}catch(_){ }
      try{saveState()}catch(_){ }try{scheduleRender(true)}catch(_){ }
      return true;
    }
    return baseConsume(event,context);
  };
}

window.__swrlzRecoveryIntegrity={version:1,carrier:CARRIER,policy:'exact-replay-or-preserve-partial'};
})();
