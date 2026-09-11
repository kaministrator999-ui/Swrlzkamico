(()=>{"use strict";
if(window.__swrlzContextCameraInstalled)return;
window.__swrlzContextCameraInstalled=true;

const rawByRequest=new Map();
const priorConsume=typeof window.consumeEvent==='function'?window.consumeEvent:null;
if(!priorConsume)return;

function ridOf(event,context){return String(event?.identity?.requestId||context?.requestId||context?.message?.meta?.requestId||'')}
function ensureMeta(message){message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};return message.meta.contextCamera}
function addCameraTrail(message,reason){
  try{
    message.meta=message.meta||{};message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
    const last=message.meta.trail[message.meta.trail.length-1];
    message.meta.trail.push({seq:Number(last?.seq||0)+1,phase:'CONTEXT_CAMERA',reason,at:Date.now()});
    if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);
  }catch(_){ }
}

window.consumeEvent=function(event,context){
  const message=context?.message,rid=ridOf(event,context);
  if(message&&rid){
    const camera=ensureMeta(message);
    if(event?.type==='RESET')rawByRequest.set(rid,'');
    if(event?.type==='DELTA'&&typeof event.text==='string')rawByRequest.set(rid,(rawByRequest.get(rid)||'')+event.text);
    camera.lastRawEventSeq=Number(event?.seq||camera.lastRawEventSeq||0);
    camera.captureMode='raw-before-display-filter';
  }
  const result=priorConsume(event,context);
  if(message&&rid&&['COMPLETED','CANCELLED','FAILED'].includes(String(event?.type||''))){
    const raw=rawByRequest.get(rid);
    const camera=ensureMeta(message);
    if(typeof raw==='string'&&raw.length){message.meta.modelText=raw;camera.rawAssistantChars=raw.length}
    camera.displayAssistantChars=String(message.text||'').length;
    camera.canonicalDiffersFromDisplay=typeof raw==='string'?raw!==String(message.text||''):false;
    camera.leadingIdentityFiltered=typeof raw==='string'&&/^\s*§wyrlz\s*(?:\r?\n)+/iu.test(raw)&&!/^\s*§wyrlz\s*(?:\r?\n)+/iu.test(String(message.text||''));
    camera.completedAt=Date.now();
    addCameraTrail(message,`Context camera · history=${camera.historySource||'unknown'} · canonical assistant history=${Number(camera.assistantHistoryUsingModelText||0)} · raw/display differ=${camera.canonicalDiffersFromDisplay?'yes':'no'} · leading identity filtered=${camera.leadingIdentityFiltered?'yes':'no'}.`);
    rawByRequest.delete(rid);
    try{if(typeof saveState==='function')saveState()}catch(_){ }
  }
  return result;
};

window.__swrlzContextCamera={rawByRequest};
})();
