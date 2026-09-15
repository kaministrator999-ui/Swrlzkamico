(()=>{'use strict';

if(window.__swrlzChatAccountStateSyncV1)return;

const API='/api/chat_state';
const DEBUG_ENDPOINT='/api/chat/client-debug';
const STORAGE_KEY='swrlz.vercel.chat.v1';
const APPLIED_KEY='swrlz.chat.account-state.applied.v1';
const MUTATION_CONTRACT='swrlz-chat-account-mutation-v1';
const CAMERA_CONTRACT='swrlz-whole-conversation-camera-v1';
const ctl={contract:'swrlz-chat-account-state-sync-v3',revision:0,ready:false,lastError:'',syncing:false,mode:'unknown',pendingMutations:0};
window.__swrlzChatAccountStateSyncV1=ctl;

const dbg=(m,d)=>{try{window.__swrlzDebug?.log('account-state',m,d)}catch(_){}};
function parse(v){try{const x=JSON.parse(v||'null');return x&&x.version===1&&Array.isArray(x.threads)?x:null}catch{return null}}
function local(){return parse(localStorage.getItem(STORAGE_KEY))}
function newest(a,b){return Number(a?.updatedAt||0)>=Number(b?.updatedAt||0)?a:b}
function mergeMessage(a,b){const n=newest(a,b)||a||b;return {...(a||{}),...(b||{}),...n,meta:{...(a?.meta||{}),...(b?.meta||{}),...(n?.meta||{})}}}
function mergeThread(a,b){if(!a)return b;if(!b)return a;const n=newest(a,b);const map=new Map();for(const m of [...(a.messages||[]),...(b.messages||[])]){if(!m?.id)continue;map.set(m.id,map.has(m.id)?mergeMessage(map.get(m.id),m):m)}const messages=[...map.values()].sort((x,y)=>Number(x.createdAt||0)-Number(y.createdAt||0));return {...a,...b,...n,messages}}
function mergeState(a,b){if(!a)return b;if(!b)return a;const map=new Map();for(const t of [...(a.threads||[]),...(b.threads||[])]){if(!t?.id)continue;map.set(t.id,map.has(t.id)?mergeThread(map.get(t.id),t):t)}const threads=[...map.values()].sort((x,y)=>Number(y.pinned)-Number(x.pinned)||Number(y.updatedAt||0)-Number(x.updatedAt||0)).slice(0,80);const ids=new Set(threads.map(t=>t.id));const currentId=ids.has(a.currentId)?a.currentId:(ids.has(b.currentId)?b.currentId:(threads[0]?.id||''));return {version:1,currentId,threads}}
function sameThreadMeta(a,b){return String(a?.title||'')===String(b?.title||'')&&!!a?.pinned===!!b?.pinned}
function threadMap(state){return new Map((state?.threads||[]).filter(t=>t?.id).map(t=>[String(t.id),t]))}
function messageMap(thread){return new Map((thread?.messages||[]).filter(m=>m?.id).map(m=>[String(m.id),m]))}
function requestIdOf(message){return String(message?.meta?.requestId||'')}
function isLocalInflight(message){const s=String(message?.state||'').toLowerCase();return message?.role==='assistant'&&(s==='streaming'||s==='cancelling')}
function isTerminalAssistant(message){if(message?.role!=='assistant')return false;const s=String(message?.state||'').toLowerCase();if(['complete','cancelled','failed'].includes(s))return true;const meta=message?.meta||{};if(String(meta.commitPhase||'').toUpperCase()==='TERMINAL')return true;return ['COMPLETED','CANCELLED','FAILED'].includes(String(meta.terminalType||'').toUpperCase())}
function assistantForLocal(remoteThread,localMessage){
  if(!remoteThread)return null;
  const rid=requestIdOf(localMessage);
  if(rid){const byRequest=(remoteThread.messages||[]).find(m=>m?.role==='assistant'&&requestIdOf(m)===rid);if(byRequest)return byRequest}
  return messageMap(remoteThread).get(String(localMessage?.id||''))||null;
}
function unresolvedInflight(localState,remoteState){
  if(!localState)return [];
  const unresolved=[],remoteThreads=threadMap(remoteState);
  for(const thread of localState.threads||[]){
    const remoteThread=remoteThreads.get(String(thread?.id||''));
    for(const message of thread?.messages||[]){
      if(!isLocalInflight(message))continue;
      const remoteMessage=assistantForLocal(remoteThread,message);
      if(!remoteMessage||!isTerminalAssistant(remoteMessage))unresolved.push({threadId:String(thread?.id||''),localMessageId:String(message?.id||''),requestId:requestIdOf(message),remoteMessageId:String(remoteMessage?.id||''),remoteState:String(remoteMessage?.state||''),matchedBy:remoteMessage&&(requestIdOf(message)&&requestIdOf(remoteMessage)===requestIdOf(message))?'requestId':remoteMessage?'messageId':'none'});
    }
  }
  return unresolved;
}
function hasUnresolvedInflight(localState,remoteState){return unresolvedInflight(localState,remoteState).length>0}

const DIAGNOSTIC_META_KEYS=['phase','trail','firstDeltaLatencyMs','totalLatencyMs','error','terminalIntegrity','workLabel','responsePresence','contextCamera','temporalContext','activityExpanded','networkContinuity','committedOutputV4','outputVisibilityPolicy','committedChars','stagedChars','semanticValidationOwner','rawPhase','transcriptSync','committedContractBridge','committedContractBridgePolicy','turnIntegrity','categories','modelText','generationBranchId'];
function diagnosticMeta(meta){const out={};for(const key of DIAGNOSTIC_META_KEYS)if(meta&&Object.prototype.hasOwnProperty.call(meta,key))out[key]=meta[key];return out}
function localAssistantForRemote(localThread,remoteMessage){
  if(!localThread||remoteMessage?.role!=='assistant')return null;
  const rid=requestIdOf(remoteMessage);
  if(rid){const byRequest=(localThread.messages||[]).find(m=>m?.role==='assistant'&&requestIdOf(m)===rid);if(byRequest)return byRequest}
  return messageMap(localThread).get(String(remoteMessage?.id||''))||null;
}
function preserveLocalDiagnostics(remoteState,localState){
  if(!remoteState||!localState)return remoteState;
  const locals=threadMap(localState);
  return {...remoteState,threads:(remoteState.threads||[]).map(remoteThread=>{
    const localThread=locals.get(String(remoteThread?.id||''));
    if(!localThread)return remoteThread;
    return {...remoteThread,messages:(remoteThread.messages||[]).map(remoteMessage=>{
      const localMessage=localAssistantForRemote(localThread,remoteMessage);
      if(!localMessage)return remoteMessage;
      const diagnostics=diagnosticMeta(localMessage.meta||{});
      if(!Object.keys(diagnostics).length)return remoteMessage;
      return {...remoteMessage,meta:{...(remoteMessage.meta||{}),...diagnostics,requestId:requestIdOf(remoteMessage)||requestIdOf(localMessage),clientCacheMessageId:String(localMessage.id||'')}};
    })};
  })};
}
function deriveMutations(before,after){
  if(!before||!after)return [];
  const ops=[],a=threadMap(before),b=threadMap(after);
  for(const [id,thread] of b){const prior=a.get(id);if(!prior||!sameThreadMeta(prior,thread)){ops.push({type:'UPSERT_THREAD',threadId:id,title:String(thread.title||'New conversation').slice(0,120),pinned:!!thread.pinned,createdAt:Number(thread.createdAt||0)})}}
  for(const [id] of a){if(!b.has(id))ops.push({type:'DELETE_THREAD',threadId:id})}
  if(String(before.currentId||'')!==String(after.currentId||'')){const nextId=String(after.currentId||'');if(!nextId||b.has(nextId))ops.push({type:'SET_CURRENT_THREAD',threadId:nextId})}
  for(const [threadId,nextThread] of b){const priorThread=a.get(threadId);if(!priorThread)continue;const priorMessages=messageMap(priorThread);for(const [messageId,nextMessage] of messageMap(nextThread)){const priorMessage=priorMessages.get(messageId);if(priorMessage&&!!priorMessage.pinned!==!!nextMessage.pinned){ops.push({type:'SET_MESSAGE_PINNED',threadId,messageId,pinned:!!nextMessage.pinned,_retry:0})}}}
  return ops.slice(0,32);
}
function terminalTransition(before,after){
  if(!after)return null;
  const oldThreads=threadMap(before);
  for(const thread of after.threads||[]){
    const oldThread=oldThreads.get(String(thread?.id||''));
    const oldMessages=messageMap(oldThread);
    for(const message of thread?.messages||[]){
      if(message?.role!=='assistant'||!isTerminalAssistant(message))continue;
      let prior=oldMessages.get(String(message.id||''));
      if(!prior&&requestIdOf(message)&&oldThread)prior=(oldThread.messages||[]).find(m=>m?.role==='assistant'&&requestIdOf(m)===requestIdOf(message));
      if(!prior||!isTerminalAssistant(prior))return {threadId:String(thread.id||''),messageId:String(message.id||''),requestId:requestIdOf(message),state:String(message.state||'')};
    }
  }
  return null;
}

const SENSITIVE_KEY=/(?:^|_)(?:token|secret|password|credential|authorization|cookie|access.?token|id.?token)(?:$|_)/i;
function redact(value,depth=0){
  if(depth>7)return '[depth-limit]';
  if(value==null||typeof value==='boolean'||typeof value==='number')return value;
  if(typeof value==='string')return value.slice(0,5000);
  if(Array.isArray(value))return value.slice(0,80).map(v=>redact(v,depth+1));
  if(typeof value==='object'){const out={};for(const [key,val] of Object.entries(value).slice(0,80)){if(SENSITIVE_KEY.test(String(key)))continue;out[key]=redact(val,depth+1)}return out}
  return String(value).slice(0,5000);
}
function addChunks(target,prefix,value,maxChunks=8){
  let text='';try{text=JSON.stringify(redact(value))}catch(_){text=String(value||'')}
  const size=1700,count=Math.min(maxChunks,Math.ceil(text.length/size));target[`${prefix}Chars`]=text.length;target[`${prefix}Chunks`]=count;target[`${prefix}Truncated`]=text.length>size*maxChunks;
  for(let i=0;i<count;i++)target[`${prefix}${String(i+1).padStart(2,'0')}`]=text.slice(i*size,(i+1)*size);
}
function cameraState(){try{if(typeof state!=='undefined'&&state?.version===1&&Array.isArray(state.threads))return state}catch(_){ }return local()}

const nativeFetch=window.fetch.bind(window);
function cameraSend(message,data){
  try{
    const debug=window.__swrlzDebug,event={at:new Date().toISOString(),ms:Math.round(performance.now()),type:'conversation-camera',message:String(message||''),data};
    const payload=JSON.stringify({runId:String(debug?.runId||'conversation-camera'),url:location.pathname,ua:navigator.userAgent,event});
    nativeFetch(DEBUG_ENDPOINT,{method:'POST',headers:{'content-type':'application/json'},body:payload,keepalive:true,cache:'no-store',credentials:'same-origin'}).catch(()=>{});
  }catch(_){ }
}
function relayConversationCamera(reason,stateValue=cameraState(),extra={}){
  try{
    if(!stateValue?.threads?.length)return false;
    const thread=stateValue.threads.find(t=>String(t?.id||'')===String(extra.threadId||stateValue.currentId||''))||stateValue.threads[0];if(!thread)return false;
    const all=Array.isArray(thread.messages)?thread.messages:[],included=all.slice(-8),captureId=`camera:${Date.now().toString(36)}:${Math.random().toString(36).slice(2,9)}`;
    const header={contract:CAMERA_CONTRACT,captureId,reason:String(reason||'manual'),capturedAt:new Date().toISOString(),mode:ctl.mode,revision:ctl.revision,threadId:String(thread.id||''),threadTitle:String(thread.title||'').slice(0,160),messageCount:all.length,includedMessages:included.length,truncatedMessages:all.length>included.length,...redact(extra)};
    addChunks(header,'rawThreadState',{...thread,messages:included},10);cameraSend('whole-thread',header);
    included.forEach((message,index)=>{
      const meta=message?.meta||{},data={contract:CAMERA_CONTRACT,captureId,reason:String(reason||'manual'),threadId:String(thread.id||''),threadTitle:String(thread.title||'').slice(0,160),messageIndex:all.length-included.length+index+1,messageCount:all.length,messageId:String(message?.id||''),role:String(message?.role||''),state:String(message?.state||''),createdAt:Number(message?.createdAt||0),pinned:!!message?.pinned,text:String(message?.text||'').slice(0,2000),requestId:requestIdOf(message),phase:String(meta.phase||''),firstDeltaLatencyMs:meta.firstDeltaLatencyMs??null,totalLatencyMs:meta.totalLatencyMs??null,error:String(meta.error||'').slice(0,1000),activity:(Array.isArray(meta.trail)?meta.trail:[]).map(step=>`${String(step?.phase||'')} — ${String(step?.reason||'')}`).join('\n').slice(0,2000)};
      for(const key of ['terminalIntegrity','responsePresence','contextCamera','temporalContext','networkContinuity','transcriptSync','turnIntegrity'])if(meta[key]!=null)addChunks(data,key,meta[key],2);
      addChunks(data,'rawMessageState',message,6);cameraSend('message',data);
    });
    return true;
  }catch(_){return false}
}
window.__swrlzWholeConversationCamera={version:1,contract:CAMERA_CONTRACT,capture:(reason='manual')=>relayConversationCamera(reason,cameraState(),{})};

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
function enqueue(ops){if(!ops.length)return;pendingOps.push(...ops);ctl.pendingMutations=pendingOps.length;dbg('mutation-enqueued',{operations:ops.map(op=>op.type),queued:pendingOps.length});clearTimeout(mutationTimer);mutationTimer=setTimeout(flushMutations,350)}
function scheduleLegacyPush(delay=1400){clearTimeout(legacyTimer);legacyTimer=setTimeout(legacyPush,delay)}
function scheduleMutationFlush(delay=250){if(!pendingOps.length)return;clearTimeout(mutationTimer);mutationTimer=setTimeout(flushMutations,delay)}

localStorage.setItem=function(key,value){
  if(key!==STORAGE_KEY){nativeSet(key,value);return}
  const before=parse(localStorage.getItem(STORAGE_KEY));nativeSet(key,value);if(applyingRemote)return;
  const after=parse(value);if(!after)return;
  const terminal=terminalTransition(before,after);if(terminal)setTimeout(()=>relayConversationCamera('assistant-terminal-local',after,terminal),0);
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
  mutationTimer=0;
  if(!pendingOps.length)return;
  if(ctl.syncing){dbg('mutation-deferred',{reason:'sync-busy',queued:pendingOps.length});scheduleMutationFlush(250);return}
  ctl.syncing=true;
  const batch=pendingOps.splice(0,32);ctl.pendingMutations=pendingOps.length;
  try{
    let remote=await readRemote();if(remote.signedOut)return;
    if(!isServerMutationMode(remote)){ctl.mode='compatibility';pendingOps=[];ctl.pendingMutations=0;scheduleLegacyPush(50);return}
    ctl.mode='server';let base=Number(remote.revision||0);let result=await mutateRemote(batch,base);if(result.conflict){base=Number(result.revision||0);result=await mutateRemote(batch,base)}
    if(result.signedOut)return;if(result.conflict)throw new Error('account state changed during mutation retry');rememberRevision(result.revision||base);ctl.ready=true;ctl.lastError='';dbg('mutation-complete',{revision:ctl.revision,operations:batch.map(op=>op.type),queued:pendingOps.length});
    const l=local();if(result.state&&!hasUnresolvedInflight(l,result.state)){const hydrated=preserveLocalDiagnostics(result.state,l),before=l?JSON.stringify(l):'',after=JSON.stringify(hydrated);if(before!==after)setLocal(hydrated)}
    relayConversationCamera('mutation-complete',cameraState(),{revision:ctl.revision,operations:batch.map(op=>op.type)});
  }catch(e){
    const retryable=String(e?.message||'').includes('CHAT_STATE_MESSAGE_NOT_FOUND')||String(e?.message||'').includes('CHAT_STATE_THREAD_NOT_FOUND');
    if(retryable){const again=batch.map(op=>({...op,_retry:Number(op._retry||0)+1})).filter(op=>op._retry<=6);if(again.length){pendingOps.unshift(...again);ctl.pendingMutations=pendingOps.length;scheduleMutationFlush(1800)}}
    ctl.lastError=String(e?.message||e);dbg('mutation-failed',{error:ctl.lastError,retryable,queued:pendingOps.length});
  }finally{ctl.syncing=false;if(pendingOps.length&&!mutationTimer)scheduleMutationFlush(450)}
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
    if(pendingOps.length){dbg('hydrate-deferred',{reason:'pending-mutations',queued:pendingOps.length,revision:ctl.revision});scheduleMutationFlush(60);return}
    const l=local(),unresolved=unresolvedInflight(l,remote.state);if(unresolved.length){dbg('hydrate-deferred',{reason:'local-stream-unresolved',revision:ctl.revision,unresolved});relayConversationCamera('hydrate-unresolved',l,{revision:ctl.revision,unresolved});return}
    if(remote.state){const hydrated=preserveLocalDiagnostics(remote.state,l),before=l?JSON.stringify(l):'',after=JSON.stringify(hydrated);if(before!==after){setLocal(hydrated);rememberRevision(remote.revision);dbg('server-hydrate-applied',{revision:ctl.revision,threads:hydrated.threads?.length||0,diagnosticsPreserved:true});relayConversationCamera('server-hydrate-applied',hydrated,{revision:ctl.revision});if(appliedBefore!==ctl.revision){location.reload();return}}}
    dbg('server-authority-ready',{revision:ctl.revision,snapshotWrites:false,terminalCorrelation:'requestId-first',diagnosticOverlay:'local-presentation-only'});
  }catch(e){ctl.lastError=String(e?.message||e);dbg('hydrate-failed',{error:ctl.lastError})}finally{ctl.syncing=false}
}

function boot(){hydrate();document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')hydrate()});window.addEventListener('online',hydrate);document.addEventListener('click',e=>{if(e.target.closest?.('#saveToken,[data-google-login],#swrlzGoogleSignIn'))setTimeout(hydrate,900)},true);window.addEventListener('swrlz:account-change',()=>setTimeout(hydrate,100));setInterval(()=>{if(document.visibilityState==='visible')hydrate()},30000)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
