(()=>{"use strict";
if(window.__swrlzTerminalIntegrityInstalled)return;
window.__swrlzTerminalIntegrityInstalled=true;

const downstreamConsume=typeof window.consumeEvent==='function'?window.consumeEvent:null;
const downstreamSave=typeof window.saveState==='function'?window.saveState:null;
const CONTRACT='terminal-response-integrity-v2';

function allAssistantMessages(){try{return (state?.threads||[]).flatMap(t=>Array.isArray(t?.messages)?t.messages:[]).filter(m=>m?.role==='assistant')}catch(_){return[]}}
function terminalSnapshot(message){return message?.meta?.terminalIntegrity?.terminalSnapshot||null}
function visibleSnapshot(message){return message?.meta?.terminalIntegrity?.lastVisibleSnapshot||null}
function networkish(value){return /network|fetch|connection|offline|resume|reconnect|transcript|generation session/i.test(String(value||''))}
function ensureMeta(message){message.meta=message.meta||{};message.meta.terminalIntegrity=message.meta.terminalIntegrity||{contract:CONTRACT,version:2};message.meta.terminalIntegrity.contract=CONTRACT;message.meta.terminalIntegrity.version=2;return message.meta.terminalIntegrity}
function emit(message,reason,data={}){try{window.__swrlzClientDebug?.('terminal-integrity',reason,{requestId:String(message?.meta?.requestId||''),messageId:String(message?.id||''),...data})}catch(_){}}
function strongestText(message){const direct=String(message?.text||'');if(direct)return direct;const visible=String(visibleSnapshot(message)?.text||'');if(visible)return visible;const terminal=String(terminalSnapshot(message)?.text||'');return terminal}
function captureVisible(message){if(!message)return;const text=String(message.text||'');if(!text)return;const ti=ensureMeta(message);ti.lastVisibleSnapshot={text,chars:text.length,state:String(message.state||''),phase:String(message.meta?.phase||''),rawPhase:String(message.meta?.rawPhase||''),at:Date.now()};const snap=terminalSnapshot(message);if(ti.terminalConfirmed&&(!snap||!String(snap.text||''))){ti.terminalSnapshot={...(snap||{}),text,chars:text.length,requestId:String(snap?.requestId||message.meta?.requestId||''),completedAt:Number(snap?.completedAt||Date.now()),promotedAt:Date.now(),source:'visible-after-terminal'};ti.lastReconciliation='empty-terminal-promoted-from-visible';ti.lastReconciliationAt=Date.now();emit(message,'empty-terminal-promoted',{chars:text.length})}}
function captureTerminal(message,event,context){if(!message||String(event?.type||'')!=='COMPLETED')return;const ti=ensureMeta(message);const text=strongestText(message);const previous=terminalSnapshot(message);const requestId=String(context?.requestId||message.meta?.requestId||previous?.requestId||'');if(text){ti.terminalSnapshot={text,chars:text.length,eventSeq:Number(event?.seq||previous?.eventSeq||0),requestId,completedAt:Date.now(),source:'completed-nonempty'};ti.lastReconciliation='stream-terminal-nonempty'}else{ti.terminalSnapshot={...(previous||{}),text:String(previous?.text||''),chars:String(previous?.text||'').length,eventSeq:Number(event?.seq||previous?.eventSeq||0),requestId,completedAt:Number(previous?.completedAt||Date.now()),source:String(previous?.text||'')?'prior-nonempty-preserved':'completed-awaiting-text'};ti.lastReconciliation=String(previous?.text||'')?'stream-terminal-prior-preserved':'stream-terminal-awaiting-text'}ti.terminalConfirmed=true;ti.lastReconciliationAt=Date.now()}
function terminalEvidence(message){const snap=terminalSnapshot(message);return Boolean(snap&&String(snap.text||'')&&snap.requestId&&message?.meta?.requestId&&snap.requestId===String(message.meta.requestId))}
function promoteCanonicalText(message){if(!message)return false;const ti=ensureMeta(message);const current=String(message.text||'');const snap=terminalSnapshot(message);const completed=message.state==='complete'||String(message.meta?.phase||'').toUpperCase()==='COMPLETE'||String(message.meta?.terminalType||'').toUpperCase()==='COMPLETED'||ti.terminalConfirmed;if(!completed||!current||String(snap?.text||''))return false;ti.terminalSnapshot={...(snap||{}),text:current,chars:current.length,requestId:String(snap?.requestId||message.meta?.requestId||''),completedAt:Number(snap?.completedAt||Date.now()),promotedAt:Date.now(),source:'canonical-completed-message'};ti.terminalConfirmed=true;ti.lastReconciliation='empty-terminal-promoted-from-canonical';ti.lastReconciliationAt=Date.now();emit(message,'canonical-text-promoted',{chars:current.length});return true}
function preserveOne(message){if(!message)return false;const ti=ensureMeta(message);let changed=promoteCanonicalText(message);const terminal=terminalSnapshot(message);const current=String(message.text||'');const terminalText=String(terminal?.text||'');if(terminalEvidence(message)){
    const damaged=message.state!=='complete'||String(message.meta?.phase||'').toUpperCase()==='ERROR'||networkish(message.meta?.error)||(!current&&terminalText);
    if(damaged){message.text=terminalText;message.state='complete';message.meta.phase='COMPLETE';message.meta.rawPhase='COMPLETE';message.meta.error='';message.meta.workLabel='Response complete';ti.lastReconciliation='terminal-restored-after-late-network-state';ti.lastReconciliationAt=Date.now();ti.lateFailureIgnored=true;emit(message,'completed-assistant-text-preserved',{chars:terminalText.length});return true}
    if(current&&terminalText&&current!==terminalText){const winner=current.length>=terminalText.length?current:terminalText;message.text=winner;ti.terminalSnapshot={...terminal,text:winner,chars:winner.length,source:'nonempty-monotonic-merge',promotedAt:Date.now()};ti.lastReconciliation='nonempty-terminal-monotonic-merge';ti.lastReconciliationAt=Date.now();emit(message,'nonempty-monotonic-merge',{chars:winner.length});return true}
    return changed;
  }
  const visible=visibleSnapshot(message);if(visible?.text&&!current&&networkish(message.meta?.error)){
    message.text=String(visible.text);ti.lastReconciliation='visible-committed-text-restored';ti.lastReconciliationAt=Date.now();ti.partialPreserved=true;emit(message,'visible-text-restored',{chars:String(visible.text).length});return true;
  }
  return changed;
}
function preserveAll(){let changed=false;for(const message of allAssistantMessages())changed=preserveOne(message)||changed;return changed}

if(downstreamConsume){window.consumeEvent=function(event,context){const result=downstreamConsume(event,context);const message=context?.message;captureVisible(message);captureTerminal(message,event,context);captureVisible(message);return result}}

if(downstreamSave){window.saveState=function(){preserveAll();return downstreamSave()}}

function reconcileSoon(reason){try{window.__swrlzTranscriptSync?.syncActive?.(`terminal-integrity-${reason}`)}catch(_){ }for(const delay of [0,180,650,1600,3600])setTimeout(()=>{if(preserveAll()){try{downstreamSave?.()}catch(_){ }try{typeof scheduleRender==='function'&&scheduleRender(false)}catch(_){ }}},delay)}
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'){for(const m of allAssistantMessages())captureVisible(m);try{downstreamSave?.()}catch(_){ }}else reconcileSoon('foreground')});
window.addEventListener('pageshow',()=>reconcileSoon('pageshow'));
window.addEventListener('online',()=>reconcileSoon('online'));

window.__swrlzTerminalIntegrity={version:2,contract:CONTRACT,preserveAll,terminalEvidence,policy:'completed-assistant-text-is-monotonic-empty-terminal-snapshots-are-never-authoritative-and-canonical-nonempty-text-promotes-terminal-evidence'};
})();
