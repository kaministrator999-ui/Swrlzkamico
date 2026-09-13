(()=>{"use strict";
if(window.__swrlzTerminalIntegrityInstalled)return;
window.__swrlzTerminalIntegrityInstalled=true;

const downstreamConsume=typeof window.consumeEvent==='function'?window.consumeEvent:null;
const downstreamSave=typeof window.saveState==='function'?window.saveState:null;
const CONTRACT='terminal-response-integrity-v1';

function allAssistantMessages(){try{return (state?.threads||[]).flatMap(t=>Array.isArray(t?.messages)?t.messages:[]).filter(m=>m?.role==='assistant')}catch(_){return[]}}
function terminalSnapshot(message){return message?.meta?.terminalIntegrity?.terminalSnapshot||null}
function visibleSnapshot(message){return message?.meta?.terminalIntegrity?.lastVisibleSnapshot||null}
function networkish(value){return /network|fetch|connection|offline|resume|reconnect|transcript|generation session/i.test(String(value||''))}
function ensureMeta(message){message.meta=message.meta||{};message.meta.terminalIntegrity=message.meta.terminalIntegrity||{contract:CONTRACT,version:1};return message.meta.terminalIntegrity}
function captureVisible(message){if(!message)return;const text=String(message.text||'');if(!text)return;const ti=ensureMeta(message);ti.lastVisibleSnapshot={text,chars:text.length,state:String(message.state||''),phase:String(message.meta?.phase||''),rawPhase:String(message.meta?.rawPhase||''),at:Date.now()}}
function captureTerminal(message,event,context){if(!message||String(event?.type||'')!=='COMPLETED')return;const text=String(message.text||'');const ti=ensureMeta(message);ti.terminalSnapshot={text,chars:text.length,eventSeq:Number(event?.seq||0),requestId:String(context?.requestId||message.meta?.requestId||''),completedAt:Date.now()};ti.terminalConfirmed=true;ti.lastReconciliation='stream-terminal';ti.lastReconciliationAt=Date.now()}
function terminalEvidence(message){const snap=terminalSnapshot(message);return Boolean(snap&&snap.requestId&&message?.meta?.requestId&&snap.requestId===String(message.meta.requestId))}
function preserveOne(message){if(!message)return false;const ti=ensureMeta(message);const terminal=terminalSnapshot(message);if(terminalEvidence(message)){
    const damaged=message.state!=='complete'||String(message.meta?.phase||'').toUpperCase()==='ERROR'||networkish(message.meta?.error)||String(message.text||'')!==String(terminal.text||'');
    if(damaged){message.text=String(terminal.text||'');message.state='complete';message.meta.phase='COMPLETE';message.meta.rawPhase='COMPLETE';message.meta.error='';message.meta.workLabel='Response complete';ti.lastReconciliation='terminal-restored-after-late-network-state';ti.lastReconciliationAt=Date.now();ti.lateFailureIgnored=true;return true}
    return false;
  }
  const visible=visibleSnapshot(message);if(visible?.text&&!message.text&&networkish(message.meta?.error)){
    message.text=String(visible.text);ti.lastReconciliation='visible-committed-text-restored';ti.lastReconciliationAt=Date.now();ti.partialPreserved=true;return true;
  }
  return false;
}
function preserveAll(){let changed=false;for(const message of allAssistantMessages())changed=preserveOne(message)||changed;return changed}

if(downstreamConsume){window.consumeEvent=function(event,context){const result=downstreamConsume(event,context);const message=context?.message;captureVisible(message);captureTerminal(message,event,context);return result}}

if(downstreamSave){window.saveState=function(){preserveAll();return downstreamSave()}}

function reconcileSoon(reason){try{window.__swrlzTranscriptSync?.syncActive?.(`terminal-integrity-${reason}`)}catch(_){ }for(const delay of [0,180,650,1600,3600])setTimeout(()=>{if(preserveAll()){try{downstreamSave?.()}catch(_){ }try{typeof scheduleRender==='function'&&scheduleRender(false)}catch(_){ }}},delay)}
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'){for(const m of allAssistantMessages())captureVisible(m);try{downstreamSave?.()}catch(_){ }}else reconcileSoon('foreground')});
window.addEventListener('pageshow',()=>reconcileSoon('pageshow'));
window.addEventListener('online',()=>reconcileSoon('online'));

window.__swrlzTerminalIntegrity={version:1,contract:CONTRACT,preserveAll,terminalEvidence,policy:'terminal-stream-completion-is-monotonic-late-network-errors-cannot-downgrade-completed-text'};
})();
