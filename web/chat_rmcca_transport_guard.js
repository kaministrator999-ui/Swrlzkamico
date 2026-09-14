(()=>{"use strict";
if(window.__swrlzRmccaTransportGuardInstalled)return;
window.__swrlzRmccaTransportGuardInstalled=true;

const traceByRequest=new Map();
function currentMessage(rid){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid))||null}catch(_){return null}}
function annotate(payload,trace){const rid=String(payload?.requestId||'');if(!rid)return;traceByRequest.set(rid,trace);const message=currentMessage(rid);if(!message)return;message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};Object.assign(message.meta.contextCamera,{rmccaTransportGuard:true,rmccaPreparationPath:trace.path,rmccaContextAvailable:false,rmccaPrepareAvailable:trace.prepareAvailable,rmccaEnvelopeAfterPrepare:false,rmccaFallbackUsed:false,rmccaGuardError:trace.error||'',cognitiveAuthority:'lalm'})}
function install(){const ctx=window.__swrlzCanonicalContext;if(!ctx||typeof ctx!=='object')return false;if(ctx.__transportGuardWrapped)return true;const original=typeof ctx.preparePayload==='function'?ctx.preparePayload.bind(ctx):null;ctx.preparePayload=function(payload){const trace={path:'factual-relay',prepareAvailable:Boolean(original),error:''};let prepared=payload;try{if(original)prepared=original(payload)}catch(err){trace.error=String(err?.message||err);prepared=payload}if(prepared&&typeof prepared==='object'&&prepared.swrlzCognitiveContext){prepared={...prepared};delete prepared.swrlzCognitiveContext}annotate(prepared,trace);return prepared};ctx.__transportGuardWrapped=true;return true}
const installed=install();
window.__swrlzRmccaTransportGuard={version:2,installed,traceByRequest,retryInstall:install,policy:'no-browser-cognitive-envelope-reconstruction'};
})();
