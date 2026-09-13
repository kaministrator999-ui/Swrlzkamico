(()=>{"use strict";
if(window.__swrlzTurnIntegrityInstalled)return;
window.__swrlzTurnIntegrityInstalled=true;

const priorFetch=window.fetch.bind(window);
const downstreamSave=typeof window.saveState==='function'?window.saveState:null;
const CONTRACT='turn-integrity-v1';
const SOCIAL_RE=/^\s*(?:hey|hi|hello|yo|sup)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$/i;
const timers=new Map();

function isStream(input,init){try{const method=String(init?.method||input?.method||'GET').toUpperCase(),url=typeof input==='string'?input:(input?.url||'');return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(url)}catch(_){return false}}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function appendDirective(existing,extra){return [String(existing||'').trim(),String(extra||'').trim()].filter(Boolean).join(' ').trim()}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function messageForRequest(rid){try{return [...(currentThreadSafe()?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid||''))||null}catch(_){return null}}
function approvedTime(){try{return window.__swrlzUserTimeContext?.approvedTimeContext?.()||null}catch(_){return null}}
function receiptFromContext(rid,ctx){if(!ctx||ctx.available!==true)return null;return{requestId:String(rid||''),capturedAt:Date.now(),available:true,timeSpecificClaimsAllowed:ctx.timeSpecificClaimsAllowed===true,permission:String(ctx.permission||'granted'),source:String(ctx.source||'device-timezone'),timeZone:String(ctx.timeZone||''),localTime:String(ctx.localTime||''),localDate:String(ctx.localDate||''),daypart:String(ctx.daypart||''),utcOffset:String(ctx.utcOffset||'')}}
function anchorRequest(rid){const m=messageForRequest(rid);if(!m)return; m.meta=m.meta||{};if(m.meta.temporalRequestAnchor)return;const ctx=approvedTime(),receipt=receiptFromContext(rid,ctx);if(receipt)m.meta.temporalRequestAnchor={contract:'request-time-anchor-v1',...receipt};}
function socialDirective(prompt){if(!SOCIAL_RE.test(String(prompt||'')))return '';return 'Social opener contract: this user turn is a greeting, not a completed-help follow-up. Reply naturally to the greeting. If approved local-time context is available, a brief fitting time-of-day greeting is appropriate. Do not say “anything else I can help with”, “let me know if there is anything else”, or otherwise imply that assistance already occurred. Do not end with a generic customer-support closure. Keep the reply warm, natural, and short.'}

window.fetch=function(input,init={}){if(!isStream(input,init))return priorFetch(input,init);const payload=parseBody(init);if(!payload)return priorFetch(input,init);const rid=String(payload.requestId||'');if(rid)anchorRequest(rid);const directive=socialDirective(payload.prompt);const next=directive?{...payload,responseDirective:appendDirective(payload.responseDirective,directive)}:payload;return priorFetch(input,{...init,body:JSON.stringify(next)})};

function terminalSynced(m){return Boolean(m?.meta?.transcriptSync?.strict===true&&m?.meta?.transcriptSync?.verified===true&&String(m?.meta?.transcriptSync?.state||'')==='terminal-synced')}
function restoreTemporalAnchor(m){const a=m?.meta?.temporalRequestAnchor;if(!a)return false;const current=m.meta.temporalContext||{};if(Number(current.capturedAt||0)===Number(a.capturedAt||0))return false;m.meta.temporalContext={requestId:String(a.requestId||m.meta?.requestId||''),capturedAt:Number(a.capturedAt||0),available:a.available===true,timeSpecificClaimsAllowed:a.timeSpecificClaimsAllowed===true,permission:String(a.permission||''),source:String(a.source||''),timeZone:String(a.timeZone||''),localTime:String(a.localTime||''),localDate:String(a.localDate||''),daypart:String(a.daypart||''),utcOffset:String(a.utcOffset||'')};return true}
function terminalize(m){if(!m||!terminalSynced(m))return false;let changed=false;m.meta=m.meta||{};if(m.state!=='complete'){m.state='complete';changed=true}if(String(m.meta.phase||'')!=='COMPLETE'){m.meta.phase='COMPLETE';changed=true}if(String(m.meta.rawPhase||'')!=='COMPLETE'){m.meta.rawPhase='COMPLETE';changed=true}if(m.meta.error){m.meta.error='';changed=true}if(m.meta.workLabel!=='✅ Response complete'){m.meta.workLabel='✅ Response complete';changed=true}m.meta.responsePresence={...(m.meta.responsePresence||{}),version:4,stage:'complete',label:'✅ Response complete',at:Number(m.meta.responsePresence?.at||Date.now())};m.meta.networkContinuity={...(m.meta.networkContinuity||{}),state:'complete',lastError:'',nudgeReason:'',terminalAuthority:'generation-transcript-v1'};m.meta.turnIntegrity={contract:CONTRACT,version:1,terminalUiRetired:true,activityLogSettled:true,at:Date.now()};changed=restoreTemporalAnchor(m)||changed;return changed}
function retireActiveIfTerminal(){try{if(typeof active==='undefined'||!active)return false;const m=activeMessage?.()||messageForRequest(active.requestId);if(!terminalSynced(m))return false;const ctl=active.controller;active=null;terminalize(m);try{ctl?.abort?.('terminal-transcript-synced')}catch(_){ }return true}catch(_){return false}}
function reconcileState(){let changed=false;try{for(const t of state?.threads||[])for(const m of t?.messages||[])if(m?.role==='assistant')changed=terminalize(m)||changed}catch(_){ }changed=retireActiveIfTerminal()||changed;return changed}

if(downstreamSave){window.saveState=function(){reconcileState();return downstreamSave()}}

function settleDom(){try{const thread=currentThreadSafe();for(const m of thread?.messages||[]){if(m?.role!=='assistant')continue;const article=document.querySelector(`.message[data-message-id="${CSS.escape(String(m.id))}"]`),details=article?.querySelector('details.trace'),summary=details?.querySelector('summary');if(!details)continue;if(['streaming','cancelling'].includes(String(m.state||''))&&!String(m.text||'')){details.style.display='none';details.open=false}else{details.style.display='';if(m.state==='complete'){details.open=false;if(summary)summary.textContent='Activity log · Response complete'}else if(summary&&m.meta?.workLabel)summary.textContent=`Activity log · ${String(m.meta.workLabel).replace(/^[^A-Za-z§]+\s*/,'')}`}}}if(typeof active!=='undefined'&&!active&&typeof refs!=='undefined'&&refs?.send){refs.send.classList.remove('stop');refs.send.setAttribute('aria-label','Send message')}}catch(_){}}
function reconcileSoon(){reconcileState();try{downstreamSave?.()}catch(_){ }try{typeof scheduleRender==='function'&&scheduleRender(false)}catch(_){ }for(const delay of [0,40,160,500,1200]){const id=setTimeout(()=>{if(reconcileState()){try{downstreamSave?.()}catch(_){ }try{typeof scheduleRender==='function'&&scheduleRender(false)}catch(_){ }}settleDom()},delay);timers.set(delay,id)}}

document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')reconcileSoon()});window.addEventListener('pageshow',reconcileSoon);window.addEventListener('online',reconcileSoon);
let queued=false;const observer=new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;reconcileState();settleDom()})});
function boot(){reconcileSoon();observer.observe(document.body,{subtree:true,childList:true,characterData:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();

window.__swrlzTurnIntegrity={version:1,contract:CONTRACT,reconcileState,terminalSynced,policy:'terminal-transcript-retires-active-ui-request-time-evidence-stays-anchored-social-openers-do-not-use-followup-closures'};
})();
