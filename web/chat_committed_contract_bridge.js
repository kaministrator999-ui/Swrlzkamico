(()=>{"use strict";
if(window.__swrlzCommittedContractBridgeInstalled)return;
window.__swrlzCommittedContractBridgeInstalled=true;

const strictConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(!strictConsume)return;

function isPrivateCommit(event){
  return Boolean(event&&typeof event==='object'&&event.type==='DELTA'&&event.protocolVersion==null&&event.schemaVersion==null&&event.contractId==null&&event.seq==null&&event.identity==null);
}

function commitLocally(event,context){
  const message=context?.message;
  if(!message)return;
  const text=String(event?.text??'');
  if(!text)return;
  message.text=String(message.text||'')+text;
  message.meta=message.meta||{};
  if(message.meta.firstDeltaLatencyMs==null&&Number.isFinite(context?.started)){
    message.meta.firstDeltaLatencyMs=Math.max(0,Math.round(performance.now()-context.started));
  }
  message.meta.committedContractBridge=true;
  message.meta.committedContractBridgePolicy='network-events-strict-local-commits-direct';
  try{
    const thread=typeof state!=='undefined'&&Array.isArray(state?.threads)?state.threads.find(t=>t.id===context?.threadId):null;
    if(thread)thread.updatedAt=Date.now();
  }catch(_){ }
  try{if(typeof saveState==='function')saveState()}catch(_){ }
  try{if(typeof scheduleRender==='function')scheduleRender(true)}catch(_){ }
}

consumeEvent=function(event,context){
  if(isPrivateCommit(event)){
    commitLocally(event,context);
    return;
  }
  return strictConsume(event,context);
};

window.__swrlzCommittedContractBridge={
  version:1,
  policy:'network-events-strict-local-commits-direct',
  detail:'Strict stream-contract validation applies only to real transport events. Semantically staged text that has already passed transport validation commits directly to the append-only final-copy buffer.'
};
})();
