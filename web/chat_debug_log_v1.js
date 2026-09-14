(()=>{"use strict";
if(window.__swrlzDebug)return;
const KEY='swrlz.chat.debug.v1',MAX=240;
let entries=[];
try{const v=JSON.parse(localStorage.getItem(KEY)||'[]');if(Array.isArray(v))entries=v.slice(-MAX)}catch(_){ }
const clean=v=>{try{if(v instanceof Error)return {name:v.name,message:v.message,stack:v.stack};if(typeof v==='string'||typeof v==='number'||typeof v==='boolean'||v==null)return v;return JSON.parse(JSON.stringify(v))}catch(_){return String(v)}};
function persist(){try{localStorage.setItem(KEY,JSON.stringify(entries.slice(-MAX)))}catch(_){ }}
function log(type,message,data){const e={at:new Date().toISOString(),ms:Math.round(performance.now()),type:String(type||'info'),message:String(message||''),data:clean(data)};entries.push(e);if(entries.length>MAX)entries=entries.slice(-MAX);persist();return e}
function text(){return [`SWRLZ Chat Debug Log`, `URL: ${location.href}`, `UA: ${navigator.userAgent}`, `Generated: ${new Date().toISOString()}`, '',...entries.map(e=>`[${e.at}] +${e.ms}ms ${e.type.toUpperCase()} ${e.message}${e.data===undefined?'':' '+JSON.stringify(e.data)}`)].join('\n')}
async function copy(){const value=text();try{await navigator.clipboard.writeText(value);return true}catch(_){const ta=document.createElement('textarea');ta.value=value;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();let ok=false;try{ok=document.execCommand('copy')}catch(__){ }ta.remove();return ok}}
function download(){const blob=new Blob([text()],{type:'text/plain;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`swrlz-chat-debug-${new Date().toISOString().replace(/[:.]/g,'-')}.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
function clear(){entries=[];persist();log('debug','log-cleared')}
window.__swrlzDebug={version:1,log,text,copy,download,clear,get entries(){return entries.slice()}};
window.__swrlzDebugLog=entries;
window.addEventListener('error',e=>log('error','window-error',{message:e.message,source:e.filename,line:e.lineno,column:e.colno,error:clean(e.error)}));
window.addEventListener('unhandledrejection',e=>log('error','unhandled-rejection',clean(e.reason)));
document.addEventListener('visibilitychange',()=>log('lifecycle','visibility',{state:document.visibilityState}));
window.addEventListener('pageshow',e=>log('lifecycle','pageshow',{persisted:e.persisted}));
window.addEventListener('pagehide',e=>log('lifecycle','pagehide',{persisted:e.persisted}));
log('boot','debug-logger-ready',{readyState:document.readyState});
})();