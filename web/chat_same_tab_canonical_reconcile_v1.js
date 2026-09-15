(()=>{'use strict';

if(window.__swrlzSameTabCanonicalReconcileV1)return;
const STORAGE_KEY='swrlz.vercel.chat.v1';
const ctl={contract:'swrlz-same-tab-canonical-reconcile-v2',lastSnapshot:'',applied:0,lastError:''};
window.__swrlzSameTabCanonicalReconcileV1=ctl;

const dbg=(m,d)=>{try{window.__swrlzDebug?.log('same-tab-reconcile',m,d)}catch(_){}};
function parse(v){try{const x=JSON.parse(v||'null');return x&&x.version===1&&Array.isArray(x.threads)?x:null}catch{return null}}
function requestIdOf(message){return String(message?.meta?.requestId||'')}
function terminal(message){if(message?.role!=='assistant')return false;const s=String(message?.state||'').toLowerCase();if(['complete','cancelled','failed'].includes(s))return true;const meta=message?.meta||{};if(String(meta.commitPhase||'').toUpperCase()==='TERMINAL')return true;return ['COMPLETED','CANCELLED','FAILED'].includes(String(meta.terminalType||'').toUpperCase())}
function terminalForRequest(snapshot,requestId){if(!snapshot||!requestId)return null;for(const thread of snapshot.threads||[])for(const message of thread.messages||[])if(message?.role==='assistant'&&requestIdOf(message)===requestId&&terminal(message))return {thread,message};return null}
function activeRequest(){try{return typeof active!=='undefined'&&active?.requestId?String(active.requestId):''}catch(_){return ''}}
function settleActiveFromServer(snapshot){
  const requestId=activeRequest();if(!requestId)return false;
  const match=terminalForRequest(snapshot,requestId);if(!match)return false;
  try{if(typeof active!=='undefined'&&active?.controller)active.controller.abort()}catch(_){ }
  try{if(typeof active!=='undefined')active=null}catch(_){ }
  dbg('active-terminal-adopted',{requestId,threadId:String(match.thread?.id||''),messageId:String(match.message?.id||''),state:String(match.message?.state||'')});
  return true;
}
function adoptIntoLiveMask(snapshot){
  try{
    if(typeof state==='undefined'||typeof render!=='function')return false;
    state=snapshot;
    render(false);
    window.dispatchEvent(new CustomEvent('swrlz:canonical-state-adopted',{detail:{currentId:String(snapshot.currentId||''),threads:snapshot.threads.length}}));
    return true;
  }catch(e){ctl.lastError=String(e?.message||e);dbg('direct-adopt-failed',{error:ctl.lastError});return false}
}
function adopt(reason){
  try{
    const raw=localStorage.getItem(STORAGE_KEY)||'';if(!raw||raw===ctl.lastSnapshot)return;
    const snapshot=parse(raw);if(!snapshot)return;
    ctl.lastSnapshot=raw;
    const settled=settleActiveFromServer(snapshot);
    const direct=adoptIntoLiveMask(snapshot);
    ctl.applied++;
    dbg('same-tab-cache-adopted',{reason,settledActive:settled,direct,currentId:String(snapshot.currentId||''),threads:snapshot.threads.length,applied:ctl.applied});
  }catch(e){ctl.lastError=String(e?.message||e);dbg('same-tab-cache-adopt-failed',{reason,error:ctl.lastError})}
}
function boot(){ctl.lastSnapshot=localStorage.getItem(STORAGE_KEY)||'';setInterval(()=>adopt('cache-change'),250);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(()=>adopt('visible'),0)});window.addEventListener('online',()=>setTimeout(()=>adopt('online'),0))}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
