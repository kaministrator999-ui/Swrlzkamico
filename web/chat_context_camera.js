(()=>{"use strict";
if(window.__swrlzContextCameraInstalled)return;
window.__swrlzContextCameraInstalled=true;

const rawByRequest=new Map();
const priorConsume=typeof window.consumeEvent==='function'?window.consumeEvent:null;
if(!priorConsume)return;

function ridOf(event,context){return String(event?.identity?.requestId||context?.requestId||context?.message?.meta?.requestId||'')}
function ensureMeta(message){message.meta=message.meta||{};message.meta.contextCamera=message.meta.contextCamera||{};return message.meta.contextCamera}
function hydrateCognitiveReceipt(message,rid){
  if(!message||!rid)return false;
  try{
    const camera=ensureMeta(message);if(camera.cognitiveAuthority&&camera.canonicalEnvelopeId&&camera.cognitiveClock)return true;
    const attach=window.__swrlzCanonicalContext?.attachReceipt;
    if(typeof attach==='function'&&attach(rid,message,{consume:true})){const next=ensureMeta(message);next.firstSendReceiptAttachedAt=Date.now();next.firstSendReceiptAttached=true;return true}
  }catch(_){ }
  return false;
}
function addCameraTrail(message,reason){
  try{message.meta=message.meta||{};message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];const last=message.meta.trail[message.meta.trail.length-1];message.meta.trail.push({seq:Number(last?.seq||0)+1,phase:'CONTEXT_CAMERA',reason,at:Date.now()});if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80)}catch(_){ }
}
function clockSummary(camera){
  const c=camera?.cognitiveClock;if(!c||typeof c!=='object')return 'RMCCA=not-captured';
  const domains=Array.isArray(c.domains)&&c.domains.length?c.domains.map(d=>`${d.domain}:${d.salience}`).join('>'):'none';
  const roles=Array.isArray(c.structuralRoles)&&c.structuralRoles.length?c.structuralRoles.join('+'):'none';
  return `RMCCA topology=${c.responseTopology||'unknown'} · depth=${c.resolutionDepth||'unknown'} · frame=${c.referenceFrame||'unknown'} · domains=${domains} · structure=${roles}`;
}
function continuitySummary(camera){
  const authority=camera?.cognitiveAuthority||'unknown';
  const envelope=camera?.canonicalEnvelopeId||'none';
  const attempts=Number(camera?.recoveryAttempts||0);
  const preserved=camera?.canonicalEnvelopePreserved===true?'yes':camera?.canonicalEnvelopePreserved===false?'no':'n/a';
  const firstSend=camera?.firstSendReceiptAttached===true?'yes':camera?.firstSendReceiptAttached===false?'no':'n/a';
  return `authority=${authority} · envelope=${envelope} · first-send receipt=${firstSend} · recovery attempts=${attempts} · canonical recovery preserved=${preserved}`;
}

window.consumeEvent=function(event,context){
  const message=context?.message,rid=ridOf(event,context);
  if(message&&rid){
    hydrateCognitiveReceipt(message,rid);
    const camera=ensureMeta(message);
    if(event?.type==='RESET')rawByRequest.set(rid,'');
    if(event?.type==='DELTA'&&typeof event.text==='string')rawByRequest.set(rid,(rawByRequest.get(rid)||'')+event.text);
    camera.lastRawEventSeq=Number(event?.seq||camera.lastRawEventSeq||0);
    camera.captureMode='raw-before-display-filter';
  }
  const result=priorConsume(event,context);
  if(message&&rid&&['COMPLETED','CANCELLED','FAILED'].includes(String(event?.type||''))){
    hydrateCognitiveReceipt(message,rid);
    const raw=rawByRequest.get(rid),camera=ensureMeta(message);
    if(typeof raw==='string'&&raw.length){message.meta.modelText=raw;camera.rawAssistantChars=raw.length}
    camera.displayAssistantChars=String(message.text||'').length;
    camera.canonicalDiffersFromDisplay=typeof raw==='string'?raw!==String(message.text||''):false;
    camera.completedAt=Date.now();
    addCameraTrail(message,`Context camera · history=${camera.historySource||'unknown'} · canonical assistant history=${Number(camera.assistantHistoryUsingModelText||0)} · raw/display differ=${camera.canonicalDiffersFromDisplay?'yes':'no'} · ${continuitySummary(camera)} · ${clockSummary(camera)}.`);
    rawByRequest.delete(rid);
    try{if(typeof saveState==='function')saveState()}catch(_){ }
  }
  return result;
};

window.__swrlzContextCamera={rawByRequest,clockSummary,continuitySummary,hydrateCognitiveReceipt};
})();
