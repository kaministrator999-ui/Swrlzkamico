(()=>{"use strict";
if(window.__swrlzImmediateActivityInstalled)return;
window.__swrlzImmediateActivityInstalled=true;
const priorFetch=window.fetch.bind(window);
function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{return JSON.parse(init.body)}catch(_){return null}}
function mark(payload){
  try{
    const rid=String(payload?.requestId||'');if(!rid||typeof currentThread!=='function')return;
    const thread=currentThread();if(!thread?.messages)return;
    const message=[...thread.messages].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);if(!message)return;
    message.meta=message.meta||{};message.meta.phase='ANALYZING_REQUEST';message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
    if(!message.meta.trail.some(x=>x?.phase==='ANALYZING_REQUEST'&&x?.reason==='Preparing the canonical request locally.')){
      message.meta.trail.push({seq:0,phase:'ANALYZING_REQUEST',reason:'Preparing the canonical request locally.',at:Date.now()});
    }
    if(typeof scheduleRender==='function')scheduleRender(true);
  }catch(_){ }
}
window.fetch=function(input,init={}){
  if(isStream(input,init)){const payload=parseBody(init);if(payload)mark(payload)}
  return priorFetch(input,init);
};
})();
