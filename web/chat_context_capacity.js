(()=>{"use strict";
if(window.__swrlzContextCapacityInstalled)return;
window.__swrlzContextCapacityInstalled=true;

const MODEL_CONTEXT_BUDGET=2048;
const HISTORY_MESSAGE_LIMIT=32;
const HISTORY_TEXT_LIMIT=2000;
const PRIMARY_KEY='swrlz.vercel.chat.v1';
const SHADOW_KEY='swrlz.vercel.chat.v1.thread-shadow.v1';
const CONTRACT='thread-history-integrity-v1';
const originalSave=typeof window.saveState==='function'?window.saveState:null;
let stableSnapshot=null;
let renderTimer=0;

function clone(value){try{return JSON.parse(JSON.stringify(value))}catch(_){return null}}
function threadMap(snapshot){const out=new Map();for(const t of snapshot?.threads||[])if(t?.id&&Array.isArray(t.messages))out.set(String(t.id),t);return out}
function mergeMissingTail(current,previous){if(!current||!previous||!Array.isArray(current.messages)||!Array.isArray(previous.messages))return false;if(current.messages.length>=previous.messages.length)return false;const currentIds=new Set(current.messages.map(m=>String(m?.id||'')));const missing=previous.messages.filter(m=>m?.id&&!currentIds.has(String(m.id)));if(!missing.length)return false;current.messages=[...current.messages,...clone(missing)].sort((a,b)=>Number(a?.createdAt||0)-Number(b?.createdAt||0));current.updatedAt=Math.max(Number(current.updatedAt||0),Number(previous.updatedAt||0));current.historyIntegrity={contract:CONTRACT,reconciledAt:Date.now(),restoredMessages:missing.length,reason:'silent-thread-shrink-detected'};return true}
function reconcileSnapshot(target,source){if(!target||!source)return false;const prior=threadMap(source);let changed=false;for(const t of target.threads||[]){const p=prior.get(String(t?.id||''));if(p)changed=mergeMissingTail(t,p)||changed}return changed}
function loadShadow(){try{return JSON.parse(localStorage.getItem(SHADOW_KEY)||'null')}catch(_){return null}}
function storeShadow(snapshot){try{localStorage.setItem(SHADOW_KEY,JSON.stringify(snapshot))}catch(_){}}
function reconcileBoot(){try{const shadow=loadShadow();if(shadow&&typeof state==='object'&&reconcileSnapshot(state,shadow)){originalSave?.();}stableSnapshot=clone(state);if(stableSnapshot)storeShadow(stableSnapshot)}catch(_){stableSnapshot=clone(typeof state==='object'?state:null)}}

if(originalSave){window.saveState=function(){try{if(stableSnapshot&&typeof state==='object')reconcileSnapshot(state,stableSnapshot)}catch(_){}const result=originalSave();stableSnapshot=clone(typeof state==='object'?state:null);if(stableSnapshot)storeShadow(stableSnapshot);queueRender();return result}}

function tokenEstimate(text){const s=String(text||'');if(!s)return 0;let weighted=0;for(const ch of s){const code=ch.codePointAt(0)||0;weighted+=code>0xffff||code>=0x2e80?1.5:1}return Math.max(1,Math.ceil(weighted/4))}
function activeHistory(thread){return (thread?.messages||[]).filter(m=>m?.text&&['user','assistant'].includes(String(m.role||''))).slice(-HISTORY_MESSAGE_LIMIT).map(m=>({role:m.role,text:String(m.text).slice(0,HISTORY_TEXT_LIMIT)}))}
function metrics(){let thread=null;try{thread=typeof currentThread==='function'?currentThread():null}catch(_){}const history=activeHistory(thread);const estimated=history.reduce((n,m)=>n+tokenEstimate(m.text)+4,0);const used=Math.min(MODEL_CONTEXT_BUDGET,estimated);const overflow=Math.max(0,estimated-MODEL_CONTEXT_BUDGET);return{thread,storedMessages:Array.isArray(thread?.messages)?thread.messages.length:0,historyMessages:history.length,estimatedTokens:estimated,usedTokens:used,overflowTokens:overflow,percent:Math.min(100,Math.round((estimated/MODEL_CONTEXT_BUDGET)*100))}}
function ensureStyle(){if(document.getElementById('swrlz-context-capacity-style'))return;const style=document.createElement('style');style.id='swrlz-context-capacity-style';style.textContent=`
.swrlz-context-capacity{display:grid;gap:5px;margin:7px 8px 0;color:var(--muted,#91a9c0);font-size:10px}.swrlz-context-capacity-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.swrlz-context-capacity-head strong{color:var(--secondary,#d7e7f5);font-weight:700}.swrlz-context-capacity-track{height:5px;overflow:hidden;border-radius:99px;background:rgba(145,169,192,.14);border:1px solid rgba(145,169,192,.12)}.swrlz-context-capacity-fill{height:100%;width:0;border-radius:inherit;background:linear-gradient(90deg,var(--cyan,#38e8ff),var(--violet,#9a55ff));transition:width .22s ease}.swrlz-context-capacity[data-full="true"] .swrlz-context-capacity-fill{background:var(--amber,#ffd45a)}.swrlz-context-capacity-note{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:rgba(145,169,192,.78)}
`;document.head.append(style)}
function ensureWidget(){ensureStyle();let root=document.getElementById('swrlzContextCapacity');if(root)return root;const composer=document.querySelector('.composer');if(!composer)return null;root=document.createElement('div');root.id='swrlzContextCapacity';root.className='swrlz-context-capacity';root.innerHTML='<div class="swrlz-context-capacity-head"><strong class="swrlz-context-capacity-label">Context</strong><span class="swrlz-context-capacity-value"></span></div><div class="swrlz-context-capacity-track" role="progressbar" aria-label="Conversation context usage" aria-valuemin="0" aria-valuemax="100"><div class="swrlz-context-capacity-fill"></div></div><div class="swrlz-context-capacity-note"></div>';const caption=composer.querySelector('.composer-caption');composer.insertBefore(root,caption||null);return root}
function renderMeter(){const root=ensureWidget();if(!root)return;const m=metrics();root.dataset.full=String(m.estimatedTokens>=MODEL_CONTEXT_BUDGET);const value=root.querySelector('.swrlz-context-capacity-value'),fill=root.querySelector('.swrlz-context-capacity-fill'),track=root.querySelector('.swrlz-context-capacity-track'),note=root.querySelector('.swrlz-context-capacity-note');if(value)value.textContent=`≈ ${m.usedTokens.toLocaleString()} / ${MODEL_CONTEXT_BUDGET.toLocaleString()} tokens · ${m.percent}%`;if(fill)fill.style.width=`${m.percent}%`;if(track)track.setAttribute('aria-valuenow',String(m.percent));if(note)note.textContent=m.overflowTokens>0?`${m.storedMessages} messages remain stored · active context is full; older text stays in the thread instead of being deleted.`:`${m.storedMessages} messages stored · ${m.historyMessages} recent messages currently eligible for active context.`;root.title=`Estimated model-active conversation context. Thread history is stored separately and is not deleted when this reaches 100%.`}
function queueRender(){clearTimeout(renderTimer);renderTimer=setTimeout(renderMeter,20)}

const observer=new MutationObserver(queueRender);function boot(){reconcileBoot();renderMeter();const stack=document.querySelector('#messageStack');if(stack)observer.observe(stack,{childList:true,subtree:true,characterData:true});window.addEventListener('storage',e=>{if(e.key===PRIMARY_KEY||e.key===SHADOW_KEY){setTimeout(()=>{try{const shadow=loadShadow();if(shadow&&typeof state==='object'&&reconcileSnapshot(state,shadow)){originalSave?.();stableSnapshot=clone(state)}renderMeter()}catch(_){}},0)}});document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')renderMeter()});window.addEventListener('pageshow',renderMeter)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();

window.__swrlzContextCapacity={version:1,contract:CONTRACT,modelContextBudget:MODEL_CONTEXT_BUDGET,historyMessageLimit:HISTORY_MESSAGE_LIMIT,historyTextLimit:HISTORY_TEXT_LIMIT,metrics,reconcile:()=>{const changed=stableSnapshot&&typeof state==='object'?reconcileSnapshot(state,stableSnapshot):false;if(changed)window.saveState?.();return changed},policy:'thread-history-persistent-active-model-context-bounded-and-visible'};
})();
