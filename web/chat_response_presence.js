(()=>{"use strict";
if(window.__swrlzResponsePresenceInstalled)return;
window.__swrlzResponsePresenceInstalled=true;

const BRAND='§wyrlz';
const ALIAS_RE=/\b(?:swurlz|swrlz|swyrlz)\b/gi;
const priorFetch=window.fetch.bind(window);
const downstreamConsume=typeof window.consumeEvent==='function'?window.consumeEvent:null;
const timers=new Map();

function normalizeBrandText(value){return String(value??'').replace(ALIAS_RE,BRAND)}
function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function currentMessage(rid){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid))||null}catch(_){return null}}
function renderNow(message){try{if(typeof saveState==='function')saveState()}catch(_){ }try{if(typeof scheduleRender==='function')scheduleRender(false)}catch(_){ }try{if(typeof refs!=='undefined'&&refs?.composerHint&&message?.meta?.workLabel)refs.composerHint.textContent=message.meta.workLabel}catch(_){ }}
function setPresence(message,label,phase='ANALYZING_REQUEST',stage='waiting'){if(!message||!['streaming','cancelling'].includes(String(message.state||'')))return;message.meta=message.meta||{};message.meta.phase=phase;message.meta.workLabel=normalizeBrandText(label);message.meta.responsePresence={...(message.meta.responsePresence||{}),version:2,stage,label:message.meta.workLabel,at:Date.now()};renderNow(message)}
function clearTimers(rid){const list=timers.get(String(rid));if(list){for(const timer of list)clearTimeout(timer);timers.delete(String(rid))}}
function armInitial(rid){
  const message=currentMessage(rid);if(!message)return;clearTimers(rid);
  setPresence(message,`📥 ${BRAND} is receiving your message…`,'ANALYZING_REQUEST','receiving');
  const list=[];
  list.push(setTimeout(()=>{const m=currentMessage(rid);if(m?.meta?.responsePresence?.stage==='receiving')setPresence(m,`👁️ ${BRAND} is reading your message…`,'ANALYZING_REQUEST','reading')},320));
  list.push(setTimeout(()=>{const m=currentMessage(rid);if(['receiving','reading'].includes(String(m?.meta?.responsePresence?.stage||'')))setPresence(m,`🧩 ${BRAND} is connecting the context…`,'ANALYZING_REQUEST','understanding')},1100));
  timers.set(String(rid),list);
}
function labelFor(event,message){const p=String(event?.phase||'').toUpperCase(),t=String(event?.type||'').toUpperCase();
  if(t==='COMPLETED'||p==='COMPLETE')return ['✅ Response complete','COMPLETE','complete'];
  if(t==='FAILED'||p==='ERROR')return ['⚠️ Request failed','ERROR','failed'];
  if(t==='CANCELLED'||p==='CANCELLED')return ['⏹️ Request cancelled','CANCELLED','cancelled'];
  if(p==='RECONNECTING')return [`🔄 ${BRAND} is reconnecting to the same response…`,'RECONNECTING','reconnecting'];
  if(p==='CATCHING_UP')return [`⚡ ${BRAND} is catching you up to the live response…`,'CATCHING_UP','catching-up'];
  if(['STATE_VALIDATION','QUEUED','MODEL_READY'].includes(p))return [`🧩 ${BRAND} is getting the response ready…`,'ANALYZING_REQUEST','preparing'];
  if(p==='PREFILL')return [`🧩 ${BRAND} is gathering the conversation context…`,'PREFILL','context'];
  if(p==='COMPUTE_HEARTBEAT'){
    const prior=String(message?.meta?.responsePresence?.stage||'');
    return [prior==='context'?`🧠 ${BRAND} is thinking through the context…`:`🧠 ${BRAND} is thinking it through…`,'ANALYZING_REQUEST','thinking'];
  }
  if(['COGNITIVE_ROUTE','ROUTE_RESOLVED','RESPONSE_PLAN','ANALYZING_REQUEST','CAPABILITY_DISCOVERY','PERMISSION_PREFLIGHT'].includes(p)||t==='STARTED'||t==='ROUTE')return [`🧠 ${BRAND} is thinking it through…`,'ANALYZING_REQUEST','thinking'];
  if(['FIRST_TOKEN','GENERATING','DECODE_PROGRESS','ANSWER_STREAMING'].includes(p))return [`✨ ${BRAND} is shaping your response…`,'GENERATING','composing'];
  if(t==='DELTA')return [`✍️ ${BRAND} is writing back…`,'GENERATING','writing'];
  if(['VERIFYING_RESULT','REQUIREMENT_GUARD','REQUIREMENT_REPAIR','FINALIZING','IMPLEMENTATION_CONTRACT'].includes(p))return [`🔎 ${BRAND} is checking the response…`,'VERIFYING_RESULT','checking'];
  return null;
}

if(downstreamConsume){window.consumeEvent=function(event,context){const result=downstreamConsume(event,context);const message=context?.message,rid=String(context?.requestId||message?.meta?.requestId||'');const mapped=labelFor(event,message);if(mapped&&message){clearTimers(rid);const [label,phase,stage]=mapped;if(['complete','failed','cancelled'].includes(stage)){message.meta=message.meta||{};message.meta.workLabel=label;message.meta.responsePresence={...(message.meta.responsePresence||{}),version:2,stage,label,at:Date.now()};renderNow(message)}else setPresence(message,label,phase,stage)}return result}}

window.fetch=function(input,init={}){if(isStream(input,init)){const payload=parseBody(init);if(payload?.requestId)armInitial(String(payload.requestId))}return priorFetch(input,init)};

function skipNode(node){const p=node?.parentElement;if(!p)return true;return Boolean(p.closest('code,pre,textarea,input,script,style,[contenteditable="true"]'))}
function normalizeTextNode(node){if(!node||node.nodeType!==Node.TEXT_NODE||skipNode(node))return;const value=node.nodeValue||'',next=normalizeBrandText(value);if(next!==value)node.nodeValue=next}
function normalizeAttributes(element){if(!(element instanceof Element))return;if(element.matches('input,textarea,[contenteditable="true"]'))return;for(const name of ['aria-label','title','placeholder']){if(!element.hasAttribute(name))continue;const value=element.getAttribute(name)||'',next=normalizeBrandText(value);if(next!==value)element.setAttribute(name,next)}}
function normalizeTree(root){if(root?.nodeType===Node.TEXT_NODE){normalizeTextNode(root);return}if(!(root instanceof Element||root instanceof Document||root instanceof DocumentFragment))return;if(root instanceof Element)normalizeAttributes(root);const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while((node=walker.nextNode()))normalizeTextNode(node);if(root.querySelectorAll)for(const el of root.querySelectorAll('[aria-label],[title],[placeholder]'))normalizeAttributes(el)}
let normalizationQueued=false;function queueNormalization(){if(normalizationQueued)return;normalizationQueued=true;queueMicrotask(()=>{normalizationQueued=false;normalizeTree(document.body)})}
const observer=new MutationObserver(records=>{for(const record of records){if(record.type==='characterData'){normalizeTextNode(record.target);continue}for(const node of record.addedNodes)normalizeTree(node)}queueNormalization()});
function boot(){normalizeTree(document.body);observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['aria-label','title','placeholder']})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();

window.__swrlzResponsePresence={version:2,brand:BRAND,aliases:['swurlz','swrlz','swyrlz'],normalizeBrandText,labelFor,policy:'stage-aware-expressive-response-presence-display-brand-normalization'};
})();
