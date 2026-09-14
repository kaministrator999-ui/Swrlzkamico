(()=>{"use strict";
if(window.__swrlzDebug)return;
const KEY='swrlz.chat.debug.v1',MAX=240,RUN=(crypto.randomUUID?.()||`${Date.now()}-${Math.random()}`),ENDPOINT='/api/chat/client-debug';
let entries=[];try{const v=JSON.parse(localStorage.getItem(KEY)||'[]');if(Array.isArray(v))entries=v.slice(-MAX)}catch(_){ }
const clean=v=>{try{if(v instanceof Error)return{name:v.name,message:v.message,stack:v.stack};if(typeof v==='string'||typeof v==='number'||typeof v==='boolean'||v==null)return v;return JSON.parse(JSON.stringify(v))}catch(_){return String(v)}};
function persist(){try{localStorage.setItem(KEY,JSON.stringify(entries.slice(-MAX)))}catch(_){ }}
function send(e){const payload=JSON.stringify({runId:RUN,url:location.pathname,ua:navigator.userAgent,event:e});try{if(navigator.sendBeacon){const ok=navigator.sendBeacon(ENDPOINT,new Blob([payload],{type:'application/json'}));if(ok)return}}catch(_){ }try{fetch(ENDPOINT,{method:'POST',headers:{'content-type':'application/json'},body:payload,keepalive:true,cache:'no-store'}).catch(()=>{})}catch(_){ }}
function log(type,message,data){const e={at:new Date().toISOString(),ms:Math.round(performance.now()),type:String(type||'info'),message:String(message||''),data:clean(data)};entries.push(e);if(entries.length>MAX)entries=entries.slice(-MAX);persist();send(e);return e}
function text(){return[`SWRLZ Chat Debug Log`,`Run: ${RUN}`,`URL: ${location.href}`,`UA: ${navigator.userAgent}`,`Generated: ${new Date().toISOString()}`,'',...entries.map(e=>`[${e.at}] +${e.ms}ms ${e.type.toUpperCase()} ${e.message}${e.data===undefined?'':' '+JSON.stringify(e.data)}`)].join('\n')}
async function copy(){const value=text();try{await navigator.clipboard.writeText(value);return true}catch(_){return false}}
function download(){const blob=new Blob([text()],{type:'text/plain;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`swrlz-chat-debug-${RUN}.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
function clear(){entries=[];persist();log('debug','log-cleared')}
window.__swrlzDebug={version:2,runId:RUN,log,text,copy,download,clear,get entries(){return entries.slice()}};window.__swrlzDebugLog=entries;
window.addEventListener('error',e=>log('error','window-error',{message:e.message,source:e.filename,line:e.lineno,column:e.colno,error:clean(e.error)}));window.addEventListener('unhandledrejection',e=>log('error','unhandled-rejection',clean(e.reason)));document.addEventListener('visibilitychange',()=>log('lifecycle','visibility',{state:document.visibilityState}));window.addEventListener('pageshow',e=>log('lifecycle','pageshow',{persisted:e.persisted}));window.addEventListener('pagehide',e=>log('lifecycle','pagehide',{persisted:e.persisted}));
log('boot','debug-logger-ready',{readyState:document.readyState,runId:RUN});
})();