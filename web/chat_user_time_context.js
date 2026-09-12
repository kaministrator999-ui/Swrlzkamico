(()=>{"use strict";
if(window.__swrlzUserTimeContextInstalled)return;
window.__swrlzUserTimeContextInstalled=true;

const priorFetch=window.fetch.bind(window);
const PREFIX='[[SWRLZ_USER_LOCAL_TIME:';

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
  return {epochMs:date.getTime(),localDate:`${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}`,localTime:`${pad(hour)}:${pad(date.getMinutes())}`,hour,daypart,timeZone:zoneName(),utcOffset:offsetLabel(date)};
}
function marker(ctx){return `${PREFIX}${ctx.localDate} ${ctx.localTime} ${ctx.timeZone} UTC${ctx.utcOffset}; daypart=${ctx.daypart}]]`}
function decorate(text,ctx){const value=String(text||'').replace(/^\[\[SWRLZ_USER_LOCAL_TIME:[^\]]+\]\]\n?/,'');return `${marker(ctx)}\n${value}`}
function threadMessagesBeforeRequest(payload){
  const thread=currentThreadSafe();if(!thread||!Array.isArray(thread.messages))return [];
  const rid=String(payload?.requestId||'');
  let end=thread.messages.findIndex(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);
  if(end<0)end=thread.messages.length;else end=Math.max(0,end-1);
  return thread.messages.slice(0,end).filter(m=>m&&['user','assistant'].includes(m.role)&&String(m.text||m?.meta?.modelText||'').length).slice(-32);
}
function augment(payload){
  const next={...payload};
  const prior=threadMessagesBeforeRequest(payload);
  let userIndex=0;
  const priorUsers=prior.filter(m=>m.role==='user');
  next.history=(Array.isArray(payload.history)?payload.history:[]).map(item=>{
    if(item?.role!=='user')return item;
    const source=priorUsers[userIndex++];
    return {...item,text:decorate(item.text,timeContext(source?.createdAt||Date.now()))};
  });
  const thread=currentThreadSafe();
  const rid=String(payload?.requestId||'');
  const assistantIndex=thread?.messages?.findIndex?.(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid)??-1;
  const currentUser=assistantIndex>0?thread.messages[assistantIndex-1]:null;
  const ctx=timeContext(currentUser?.createdAt||Date.now());
  next.prompt=decorate(payload.prompt,ctx);
  next.swrlzUserTimeContext=ctx;
  return next;
}

window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const next=augment(payload);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};
window.__swrlzUserTimeContext={timeContext,decorate,augment};
})();
