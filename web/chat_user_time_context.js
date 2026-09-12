(()=>{"use strict";
if(window.__swrlzUserTimeContextInstalled)return;
window.__swrlzUserTimeContextInstalled=true;

const priorFetch=window.fetch.bind(window);
function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function pad(value){return String(value).padStart(2,'0')}
function offsetLabel(date){const mins=-date.getTimezoneOffset(),sign=mins>=0?'+':'-',abs=Math.abs(mins);return `${sign}${pad(Math.floor(abs/60))}:${pad(abs%60)}`}
function zoneName(){try{return Intl.DateTimeFormat().resolvedOptions().timeZone||'local'}catch(_){return 'local'}}
function timeContext(createdAt){
  const date=new Date(Number(createdAt)||Date.now());
  const hour=date.getHours();
  const daypart=hour<5?'overnight':hour<12?'morning':hour<17?'afternoon':hour<21?'evening':'night';
  return {epochMs:date.getTime(),localDate:`${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`,localTime:`${pad(hour)}:${pad(date.getMinutes())}`,hour,daypart,timeZone:zoneName(),utcOffset:offsetLabel(date),source:'browser-message-createdAt'};
}
function augment(payload){
  const next={...payload};
  const thread=currentThreadSafe(),rid=String(payload?.requestId||'');
  const assistantIndex=thread?.messages?.findIndex?.(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid)??-1;
  const currentUser=assistantIndex>0?thread.messages[assistantIndex-1]:null;
  next.swrlzUserTimeContext=timeContext(currentUser?.createdAt||Date.now());
  return next;
}
window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  return priorFetch(input,{...init,body:JSON.stringify(augment(payload))});
};
window.__swrlzUserTimeContext={timeContext,augment};
})();
