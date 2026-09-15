(()=>{'use strict';

if(window.__swrlzChatAccountStateSyncV1)return;

const API='/api/chat_state';
const STORAGE_KEY='swrlz.vercel.chat.v1';
const APPLIED_KEY='swrlz.chat.account-state.applied.v1';
const MUTATION_CONTRACT='swrlz-chat-account-mutation-v1';
const ctl={contract:'swrlz-chat-account-state-sync-v2',revision:0,ready:false,lastError:'',syncing:false,mode:'unknown',pendingMutations:0};
window.__swrlzChatAccountStateSyncV1=ctl;

const dbg=(m,d)=>{try{window.__swrlzDebug?.log('account-state',m,d)}catch(_){}};
function parse(v){try{const x=JSON.parse(v||'null');return x&&x.version===1&&Array.isArray(x.threads)?x:null}catch{return null}}
function local(){return parse(localStorage.getItem(STORAGE_KEY))}
function newest(a,b){return Number(a?.updatedAt||0)>=Number(b?.updatedAt||0)?a:b}
function mergeMessage(a,b){const n=newest(a,b)||a||b;return {...(a||{}),...(b||{}),...n,meta:{...(a?.meta||{}),...(b?.meta||{}),...(n?.meta||{})}}}
function mergeThread(a,b){if(!a)return b;if(!b)return a;const n=newest(a,b);const map=new Map();for(const m of [...(a.messages||[]),...(b.messages||[])]){if(!m?.id)continue;map.set(m.id,map.has(m.id)?mergeMessage(map.get(m.id),m):m)}const messages=[...map.values()].sort((x,y)=>Number(x.createdAt||0)-Number(y.createdAt||0));return {...a,...b,...n,messages}}
function mergeState(a,b){if(!a)return b;if(!b)return a;const map=new Map();for(const t of [...(a.threads||[]),...(b.threads||[])]){if(!t?.id)continue;map.set(t.id,map.has(t.id)?mergeThread(map.get(t.id),t):t)}const threads=[...map.values()].sort((x,y)=>Number(y.pinned)-Number(x.pinned)||Number(y.updatedAt||0)-Number(x.updatedAt||0)).slice(0,80);const ids=new Set(threads.map(t=>t.id));const currentId=ids.has(a.currentId)?a.currentId:(ids.has(b.currentId)?b.currentId:(threads[0]?.id||''));return {version:1,currentId,threads}}
function hasInflight(state){return !!state?.threads?.some(t=>t?.messages?.some(m=>String(m?.state||'').toLowerCase()==='streaming'))}
function sameThreadMeta(a,b){return String(a?.title||'')===String(b?.title||'')&&!!a?.pinned===!!b?.pinned}
function threadMap(state){return new Map((state?.threads||[]).filter(t=>t?.id).map(t=>[String(t.id),t]))}
function messageMap(thread){return new Map((thread?.messages||[]).filter(m=>m?.id).map(m=>[String(m.id),m]))}
function deriveMutations(before,after){
  if(!before||!after)return [];
  const ops=[],a=threadMap(before),b=threadMap(after);
  for(const [id,thread] of b){const prior=a.get(id);if(!prior||!sameThreadMeta(prior,thread)){ops.push({type:'UPSERT_THREAD',threadId:id,title:String(thread.title||'New conversation').slice(0,120),pinned:!!thread.pinned,createdAt:Number(thread.createdAt||0)})}}
  for(const [id] of a){if(!b.has(id))ops.push({type:'DELETE_THREAD',threadId:id})}
  if(String(before.currentId||'')!==String(after.currentId||'')){const nextId=String(after.currentId||'');if(!nextId||b.has(nextId))ops.push({type:'SET_CURRENT_THREAD',threadId:nextId})}
  for(const [threadId,nextThread] of b){const priorThread=a.get(threadId);if(!priorThread)continue;const priorMessages=messageMap(priorThread);for(const [messageId,nextMessage] of messageMap(nextThread)){const priorMessage=priorMessages.get(messageId);if(priorMessage&&!!priorMessage.pinned!==!!nextMessage.pinned){ops.push({type:'SET_MESSAGE_PINNED',threadId,messageId,pinned:!!nextMessage.pinned,_retry:0})}}}
  return ops.slice(0,32);
}

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

async function readRemote(){const r=await nativeFetch(API,{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});if(r.status===401)return {signedOut:true};const v=await r.json().catch(()=>({}));if(!r.ok)throw new Error(v.detail||`state read HTTP ${r.status}`);return v}
async function writeRemoteCompatibility(state,baseRevision){const r=await nativeFetch(API,{method:'PUT',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({baseRevision,state})});const v=await r.json().catch(()=>({}));if(r.status===401)return {signedOut:true};if(r.status===409)return {...v,conflict:true};if(!r.ok)throw new Error(v.detail||`state write HTTP ${r.status}`);return v}
async function mutateRemote(operations,baseRevision){const wireOps=operations.map(({_retry,...op})=>op);const r=await nativeFetch(API,{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({contract:MUTATION_CONTRACT,baseRevision,operations:wireOps})});const v=await r.json().catch(()=>({}));if(r.status===401)return {signedOut:true};if(r.status===409)return {...v,conflict:true};if(!r.ok){const error=new Error(v.detail||`state mutation HTTP ${r.status}`);error.code=v.code||'';throw error}return v}
function isServerMutationMode(remote){return remote?.mutationContract===MUTATION_CONTRACT&&remote?.snapshotWriteAuthority==='retired'&&remote?.stateAuthority==='server'}

let nativeSet=localStorage.setItem.bind(localStorage),applyingRemote=false,legacyTimer=0,mutationTimer=0,pendingOps=[];
function setLocal(state){applyingRemote=true;try{nativeSet(STORAGE_KEY,JSON.stringify(state))}finally{applyingRemote=false}}
function rememberRevision(revision){ctl.revision=Number(revision||0);sessionStorage.setItem(APPLIED_KEY,String(ctl.revision))}
function enqueue(ops){if(!ops.length)return;pendingOps.push(...ops);ctl.pendingMutations=pendingOps.length;clearTimeout(mutationTimer);mutationTimer=setTimeout(flushMutations,350)}
function scheduleLegacyPush(delay=1400){clearTimeout(legacyTimer);legacyTimer=setTimeout(legacyPush,delay)}

localStorage.setItem=function(key,value){
  if(key!==STORAGE_KEY){nativeSet(key,value);return}
  const before=parse(localStorage.getItem(STORAGE_KEY));nativeSet(key,value);if(applyingRemote)return;
  const after=parse(value);if(!after)return;
  if(ctl.mode==='server')enqueue(deriveMutations(before,after));else scheduleLegacyPush();
};

async function legacyPush(){
  if(ctl.syncing)return;const l=local();if(!l)return;ctl.syncing=true;
  try{
    let remote=await readRemote();if(remote.signedOut)return;
    if(isServerMutationMode(remote)){ctl.mode='server';rememberRevision(remote.revision);ctl.ready=true;dbg('server-authority-enabled',{revision:ctl.revision});return}
    ctl.mode='compatibility';let merged=mergeState(l,remote.state);let result=await writeRemoteCompatibility(merged,Number(remote.revision||0));
    if(result.conflict){merged=mergeState(merged,result.state);result=await writeRemoteCompatibility(merged,Number(result.revision||0))}
    if(result.signedOut)return;if(result.conflict)throw new Error('account state changed during retry');rememberRevision(result.revision||remote.revision||0);ctl.ready=true;ctl.lastError='';dbg('compat-push-complete',{revision:ctl.revision,threads:merged.threads.length});
  }catch(e){ctl.lastError=String(e?.message||e);dbg('compat-push-failed',{error:ctl.lastError})}finally{ctl.syncing=false}
}

async function flushMutations(){
  mutationTimer=0;if(ctl.syncing||!pendingOps.length)return;ctl.syncing=true;
  const batch=pendingOps.splice(0,32);ctl.pendingMutations=pendingOps.length;
  try{
    let remote=await readRemote();if(remote.signedOut)return;
    if(!isServerMutationMode(remote)){ctl.mode='compatibility';pendingOps=[];ctl.pendingMutations=0;scheduleLegacyPush(50);return}
    ctl.mode='server';let base=Number(remote.revision||0);let result=await mutateRemote(batch,base);if(result.conflict){base=Number(result.revision||0);result=await mutateRemote(batch,base)}
    if(result.signedOut)return;if(result.conflict)throw new Error('account state changed during mutation retry');rememberRevision(result.revision||base);ctl.ready=true;ctl.lastError='';dbg('mutation-complete',{revision:ctl.revision,operations:batch.map(op=>op.type),queued:pendingOps.length});
    if(result.state&&!hasInflight(local())){const before=local(),after=JSON.stringify(result.state);if(JSON.stringify(before)!==after)setLocal(result.state)}
  }catch(e){
    const retryable=String(e?.message||'').includes('CHAT_STATE_MESSAGE_NOT_FOUND')||String(e?.message||'').includes('CHAT_STATE_THREAD_NOT_FOUND');
    if(retryable){const again=batch.map(op=>({...op,_retry:Number(op._retry||0)+1})).filter(op=>op._retry<=6);if(again.length){pendingOps.unshift(...again);ctl.pendingMutations=pendingOps.length;clearTimeout(mutationTimer);mutationTimer=setTimeout(flushMutations,1800)}}
    ctl.lastError=String(e?.message||e);dbg('mutation-failed',{error:ctl.lastError,retryable,queued:pendingOps.length});
  }finally{ctl.syncing=false;if(pendingOps.length&&!mutationTimer)mutationTimer=setTimeout(flushMutations,450)}
}

async function hydrate(){
  if(ctl.syncing)return;const appliedBefore=Number(sessionStorage.getItem(APPLIED_KEY)||0);ctl.syncing=true;
  try{
    const remote=await readRemote();if(remote.signedOut){ctl.ready=false;ctl.mode='signed-out';return}
    if(!isServerMutationMode(remote)){
      ctl.mode='compatibility';const l=local();if(!remote.state){ctl.syncing=false;await legacyPush();return}
      const merged=mergeState(l,remote.state);rememberRevision(remote.revision);ctl.ready=true;ctl.lastError='';const before=l?JSON.stringify(l):'',after=JSON.stringify(merged);
      if(before!==after){setLocal(merged);rememberRevision(remote.revision);dbg('compat-hydrate-applied',{revision:ctl.revision,threads:merged.threads.length});if(appliedBefore!==ctl.revision){location.reload();return}}
      if(after!==JSON.stringify(remote.state))scheduleLegacyPush(150);return;
    }
    ctl.mode='server';rememberRevision(remote.revision);ctl.ready=true;ctl.lastError='';
    if(pendingOps.length){dbg('hydrate-deferred',{reason:'pending-mutations',queued:pendingOps.length,revision:ctl.revision});return}
    const l=local();if(hasInflight(l)){dbg('hydrate-deferred',{reason:'local-stream-active',revision:ctl.revision});return}
    if(remote.state){const before=l?JSON.stringify(l):'',after=JSON.stringify(remote.state);if(before!==after){setLocal(remote.state);rememberRevision(remote.revision);dbg('server-hydrate-applied',{revision:ctl.revision,threads:remote.state.threads?.length||0});if(appliedBefore!==ctl.revision){location.reload();return}}}
    dbg('server-authority-ready',{revision:ctl.revision,snapshotWrites:false});
  }catch(e){ctl.lastError=String(e?.message||e);dbg('hydrate-failed',{error:ctl.lastError})}finally{ctl.syncing=false}
}

function boot(){hydrate();document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')hydrate()});window.addEventListener('online',hydrate);document.addEventListener('click',e=>{if(e.target.closest?.('#saveToken,[data-google-login],#swrlzGoogleSignIn'))setTimeout(hydrate,900)},true);window.addEventListener('swrlz:account-change',()=>setTimeout(hydrate,100));setInterval(()=>{if(document.visibilityState==='visible')hydrate()},30000)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
