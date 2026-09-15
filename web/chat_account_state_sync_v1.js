(()=>{'use strict';
if(window.__swrlzChatAccountStateSyncV1)return;
const API='/api/chat_state',STORAGE_KEY='swrlz.vercel.chat.v1',APPLIED_KEY='swrlz.chat.account-state.applied.v1';
const ctl={contract:'swrlz-chat-account-state-sync-v1',revision:0,ready:false,lastError:'',syncing:false};window.__swrlzChatAccountStateSyncV1=ctl;
const dbg=(m,d)=>{try{window.__swrlzDebug?.log('account-state',m,d)}catch(_){}};
function parse(v){try{const x=JSON.parse(v||'null');return x&&x.version===1&&Array.isArray(x.threads)?x:null}catch{return null}}
function local(){return parse(localStorage.getItem(STORAGE_KEY))}
function newest(a,b){return Number(a?.updatedAt||0)>=Number(b?.updatedAt||0)?a:b}
function mergeMessage(a,b){const n=newest(a,b)||a||b;return {...(a||{}),...(b||{}),...n,meta:{...(a?.meta||{}),...(b?.meta||{}),...(n?.meta||{})}}}
function mergeThread(a,b){if(!a)return b;if(!b)return a;const n=newest(a,b);const map=new Map();for(const m of [...(a.messages||[]),...(b.messages||[])]){if(!m?.id)continue;map.set(m.id,map.has(m.id)?mergeMessage(map.get(m.id),m):m)}const messages=[...map.values()].sort((x,y)=>Number(x.createdAt||0)-Number(y.createdAt||0));return {...a,...b,...n,messages}}
function mergeState(a,b){if(!a)return b;if(!b)return a;const map=new Map();for(const t of [...(a.threads||[]),...(b.threads||[])]){if(!t?.id)continue;map.set(t.id,map.has(t.id)?mergeThread(map.get(t.id),t):t)}const threads=[...map.values()].sort((x,y)=>Number(y.pinned)-Number(x.pinned)||Number(y.updatedAt||0)-Number(x.updatedAt||0)).slice(0,80);const ids=new Set(threads.map(t=>t.id));const currentId=ids.has(a.currentId)?a.currentId:(ids.has(b.currentId)?b.currentId:(threads[0]?.id||''));return {version:1,currentId,threads}}

const nativeFetch=window.fetch.bind(window);
function enrichTurnRequest(input,init){
  try{
    if(!init||String(init.method||'GET').toUpperCase()!=='POST'||typeof init.body!=='string')return init;
    const payload=JSON.parse(init.body);if(!payload||payload.protocolVersion!==2||!payload.requestId||!payload.prompt||!payload.threadId)return init;
    const state=local(),thread=state?.threads?.find(t=>t?.id===payload.threadId);if(!thread)return init;
    const messages=Array.isArray(thread.messages)?thread.messages:[];
    let assistantIndex=messages.findIndex(m=>m?.role==='assistant'&&m?.meta?.requestId===payload.requestId);
    let assistant=assistantIndex>=0?messages[assistantIndex]:null,user=assistantIndex>0?messages[assistantIndex-1]:null;
    if(!user||user.role!=='user'||String(user.text||'')!==String(payload.prompt||''))user=[...messages].reverse().find(m=>m?.role==='user'&&String(m.text||'')===String(payload.prompt||''))||null;
    if(!assistant||!assistant.id||!user||!user.id)return init;
    const enriched={...payload,messageId:String(user.id).slice(0,160),assistantMessageId:String(assistant.id).slice(0,160),userCreatedAt:Number(user.createdAt||0),assistantCreatedAt:Number(assistant.createdAt||0)};
    dbg('turn-identity-attached',{threadId:payload.threadId,requestId:payload.requestId,messageId:enriched.messageId,assistantMessageId:enriched.assistantMessageId});
    return {...init,body:JSON.stringify(enriched)};
  }catch(_){return init}
}
window.fetch=function(input,init){return nativeFetch(input,enrichTurnRequest(input,init))};

async function readRemote(){const r=await fetch(API,{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});if(r.status===401)return {signedOut:true};const v=await r.json().catch(()=>({}));if(!r.ok)throw new Error(v.detail||`state read HTTP ${r.status}`);return v}
async function writeRemote(state,baseRevision){const r=await fetch(API,{method:'PUT',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({baseRevision,state})});const v=await r.json().catch(()=>({}));if(r.status===401)return {signedOut:true};if(r.status===409)return {...v,conflict:true};if(!r.ok)throw new Error(v.detail||`state write HTTP ${r.status}`);return v}
let pushTimer=0,nativeSet=localStorage.setItem.bind(localStorage);
function setLocal(state){nativeSet(STORAGE_KEY,JSON.stringify(state))}
async function push(){if(ctl.syncing)return;const l=local();if(!l)return;ctl.syncing=true;try{let remote=await readRemote();if(remote.signedOut)return;let merged=mergeState(l,remote.state);let result=await writeRemote(merged,Number(remote.revision||0));if(result.conflict){merged=mergeState(merged,result.state);result=await writeRemote(merged,Number(result.revision||0))}if(result.signedOut)return;if(result.conflict)throw new Error('account state changed during retry');ctl.revision=Number(result.revision||remote.revision||0);sessionStorage.setItem(APPLIED_KEY,String(ctl.revision));ctl.ready=true;ctl.lastError='';dbg('push-complete',{revision:ctl.revision,threads:merged.threads.length})}catch(e){ctl.lastError=String(e?.message||e);dbg('push-failed',{error:ctl.lastError})}finally{ctl.syncing=false}}
function schedulePush(delay=1400){clearTimeout(pushTimer);pushTimer=setTimeout(push,delay)}
localStorage.setItem=function(key,value){nativeSet(key,value);if(key===STORAGE_KEY)schedulePush()};
async function hydrate(){if(ctl.syncing)return;ctl.syncing=true;try{const remote=await readRemote();if(remote.signedOut){ctl.ready=false;return}const l=local();if(!remote.state){ctl.syncing=false;await push();return}const merged=mergeState(l,remote.state);const revision=Number(remote.revision||0);ctl.revision=revision;ctl.ready=true;ctl.lastError='';const before=l?JSON.stringify(l):'';const after=JSON.stringify(merged);if(before!==after){setLocal(merged);const applied=Number(sessionStorage.getItem(APPLIED_KEY)||0);sessionStorage.setItem(APPLIED_KEY,String(revision));dbg('hydrate-applied',{revision,threads:merged.threads.length});if(applied!==revision){location.reload();return}}sessionStorage.setItem(APPLIED_KEY,String(revision));if(after!==JSON.stringify(remote.state))schedulePush(150)}catch(e){ctl.lastError=String(e?.message||e);dbg('hydrate-failed',{error:ctl.lastError})}finally{ctl.syncing=false}}
function boot(){hydrate();document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')hydrate()});window.addEventListener('online',hydrate);document.addEventListener('click',e=>{if(e.target.closest?.('#saveToken,[data-google-login],#swrlzGoogleSignIn'))setTimeout(hydrate,900)},true);window.addEventListener('swrlz:account-change',()=>setTimeout(hydrate,100));setInterval(()=>{if(document.visibilityState==='visible')hydrate()},30000)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
