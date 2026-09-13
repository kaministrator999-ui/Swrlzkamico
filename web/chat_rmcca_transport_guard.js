(()=>{"use strict";
if(window.__swrlzRmccaTransportGuardInstalled)return;
window.__swrlzRmccaTransportGuardInstalled=true;

const traceByRequest=new Map();
function currentMessage(rid){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid))||null}catch(_){return null}}
function annotate(payload,trace){const rid=String(payload?.requestId||'');if(!rid)return;traceByRequest.set(rid,trace);const message=currentMessage(rid);if(!message)return;message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};Object.assign(message.meta.contextCamera,{rmccaTransportGuard:true,rmccaPreparationPath:trace.path,rmccaContextAvailable:trace.contextAvailable,rmccaPrepareAvailable:trace.prepareAvailable,rmccaEnvelopeAfterPrepare:trace.envelopeAfterPrepare,rmccaFallbackUsed:trace.fallbackUsed,rmccaGuardError:trace.error||''})}
function install(){
  const ctx=window.__swrlzCanonicalContext;if(!ctx||typeof ctx!=='object')return false;
  if(ctx.__transportGuardWrapped)return true;
  const original=typeof ctx.preparePayload==='function'?ctx.preparePayload.bind(ctx):null;
  ctx.preparePayload=function(payload){
    const trace={path:'none',contextAvailable:true,prepareAvailable:Boolean(original),envelopeAfterPrepare:false,fallbackUsed:false,error:''};let prepared=payload;
    try{if(original){prepared=original(payload);trace.path='canonical-prepare'}}catch(err){trace.error=String(err?.message||err);prepared=payload}
    try{
      const valid=Boolean(prepared?.swrlzCognitiveContext?.cognitiveClock&&prepared?.swrlzCognitiveContext?.envelopeId&&prepared?.swrlzCognitiveContext?.directiveId);
      if(!valid){trace.fallbackUsed=true;const envelope=typeof ctx.buildEnvelope==='function'?ctx.buildEnvelope(payload):null;const clock=envelope?.cognitiveClock||(typeof ctx.cognitiveClock==='function'?ctx.cognitiveClock(String(payload?.prompt||'')):null);if(clock){prepared={...payload,responseDirective:String(ctx.directive||payload?.responseDirective||''),swrlzCognitiveContext:{...(envelope||{}),envelopeId:String(envelope?.envelopeId||ctx.envelopeId||'swrlz-rmcca-context-v3'),directiveId:String(envelope?.directiveId||ctx.directiveId||'rmcca-cognitive-policy-v4-social-participation'),architecture:'RMCCA',architectureVersion:4,cognitiveClock:clock,prepareStatus:String(envelope?.prepareStatus||'guard-fallback')}};trace.path=envelope?'build-envelope-fallback':'clock-fallback'}}
      trace.envelopeAfterPrepare=Boolean(prepared?.swrlzCognitiveContext?.cognitiveClock&&prepared?.swrlzCognitiveContext?.envelopeId&&prepared?.swrlzCognitiveContext?.directiveId);
    }catch(err){trace.error=[trace.error,String(err?.message||err)].filter(Boolean).join(' | ')}
    annotate(prepared,trace);return prepared;
  };
  ctx.__transportGuardWrapped=true;return true;
}
const installed=install();
window.__swrlzRmccaTransportGuard={version:1,installed,traceByRequest,retryInstall:install};
})();
