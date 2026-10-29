/* ATELIER_BRIDGE_START */
// Runs inside the existing ModelAtelier closure. Every write uses its native
// checkpoint/render/dirty path; this is data-only and never executes model code.
function seChatAtelierApply(op){
  if(!model()||!panel||panel.hidden)throw Error('MODEL_EDITOR_NOT_OPEN');
  const describe=p=>p?{id:p.id,name:p.name,kind:p.kind,position:[...p.position],rotation:[...p.rotation],scale:[...p.scale],color:p.color,material:p.material}:null;
  if(op.op==='editor.undo'||op.op==='editor.redo'){
    const back=op.op==='editor.undo';if(!(back?undo:redo).length)throw Error('NO_HISTORY_STEP');
    historyStep(back);return {changed:true,selectedId:selection};
  }
  if(op.op==='mesh.add'){
    if(model().parts.length>=MODEL_ATELIER_LIMIT)throw Error('MESH_LIMIT');
    const p={id:'atelier-chat-'+crypto.randomUUID(),name:op.name||'New mesh',kind:op.kind,position:op.position||[0,2.6,.7],rotation:op.rotation||[0,0,0],scale:op.scale||[.3,.3,.3],color:op.color||'#88daff',material:op.material||'gloss',group:'Custom'};
    if(!checkPart(p))throw Error('INVALID_NATIVE_PART');
    checkpoint();model().parts.push(p);selection=p.id;signalEdited();return {changed:true,...describe(partById(p.id))};
  }
  const p=partById(op.id);if(!p)throw Error('MESH_NOT_FOUND');
  if(op.op==='mesh.select'){select(p.id);return {selectedId:selection,...describe(partById(selection))};}
  if(op.op==='mesh.duplicate'){select(p.id);const count=model().parts.length;addPart(true);if(model().parts.length!==count+1)throw Error('DUPLICATE_NOT_APPLIED');return {changed:true,...describe(partById(selection))};}
  if(op.op==='mesh.remove'){if(model().parts.length<=1)throw Error('KEEP_ONE_MESH');select(p.id);removePart();if(partById(p.id))throw Error('REMOVE_NOT_APPLIED');return {changed:true,id:p.id,removed:true};}
  if(op.op!=='mesh.set')throw Error('UNSUPPORTED_MESH_OPERATION');
  const keys=['name','position','rotation','scale','color','material'].filter(k=>Object.hasOwn(op,k));
  const changed=keys.some(k=>JSON.stringify(p[k])!==JSON.stringify(op[k]));
  if(changed){checkpoint();for(const k of keys)p[k]=Array.isArray(op[k])?[...op[k]]:op[k];selection=p.id;signalEdited();}
  const actual=partById(p.id);if(!actual||keys.some(k=>JSON.stringify(actual[k])!==JSON.stringify(op[k])))throw Error('EDIT_NOT_APPLIED');
  return {changed,...describe(actual)};
}
/* ATELIER_BRIDGE_END */

// §E account/Chat host. Private closure holds the host-only credential. Chat
// identity, Google credentials, histories and preferences remain on Chat origin.
(()=>{
'use strict';
const PROTOCOL='swrlz-forge-chat-v1',CHAT_ORIGIN='https://kamiloki-swyrlz.hf.space';
const ALLOWED_PARENTS=new Set(['https://kamiloki-swrlz-forge-moba.static.hf.space','https://kamiloki-swrlz-forge-moba.hf.space']);
const MAX_RAW=96*1024*1024,MAX_META=48,MAX_BATCH=16;
const MATERIALS=new Set(['matte','silk','gloss','metal','emissive']),KINDS=new Set(['sphere','box','cone','cylinder']),PREFABS=new Set(['wall','rock','bush','crystal','pedestal']);
const id=()=>crypto.randomUUID().replaceAll('-','');
const hostId=id(),channelId=id(),projectIds=new WeakMap(),cloudRefs=new Map(),pending=new Map(),seenBatches=new Set();
let panel,frame,status,accountText,cloudList,port=null,ready=false,open=false,epoch=0,lease=null,lastContext=null,heartbeatTimer=null,popup=null,popupPair=null,cloudBusy=false,disposed=false;
const vector=v=>Array.isArray(v)&&v.length===3&&v.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=100);
const bounded=(value,max=100)=>typeof value==='string'&&value.length>0&&value.length<=max&&!/[\u0000-\u001f]/.test(value);
const summaryName=v=>String(v??'').slice(0,100);
function getProjectId(){if(!currentProject||typeof currentProject!=='object')throw Error('PROJECT_NOT_READY');if(!projectIds.has(currentProject))projectIds.set(currentProject,id());return projectIds.get(currentProject);}
function atelierOpen(){return !!ModelAtelier.status().open;}
function isVisible(){return open&&!document.hidden&&panel&&!panel.hidden;}
function prioritized(items,selectedId){const selectedItem=items.find(p=>p.id===selectedId);return [...(selectedItem?[selectedItem]:[]),...items.filter(p=>p.id!==selectedId)].slice(0,MAX_META);}
function context(){
  const workspace=atelierOpen()?'model-atelier':'scene',ms=ModelAtelier.status(),parts=currentProject?.modelAtelier?.parts||[];
  const selectedId=workspace==='model-atelier'?ms.selected:selected?.userData?.id||null;
  const meshes=workspace==='model-atelier'?prioritized(parts.map(p=>({id:p.id,name:summaryName(p.name),kind:p.kind,position:[...p.position],rotation:[...p.rotation],scale:[...p.scale],color:p.color,material:p.material})),selectedId):[];
  const actorRows=workspace==='scene'?prioritized(actors.map(a=>({id:a.userData.id,name:summaryName(a.name),type:a.userData.actorType||'object',position:a.position.toArray(),rotation:[a.rotation.x,a.rotation.y,a.rotation.z],scale:a.scale.toArray()})),selectedId):[];
  const undoButton=document.getElementById(workspace==='model-atelier'?'modelAtelierUndo':'undoBtn'),redoButton=document.getElementById(workspace==='model-atelier'?'modelAtelierRedo':'redoBtn');
  const value={projectId:getProjectId(),project:{name:summaryName(currentProject.name),kind:summaryName(currentProject.kind)},workspace,mode:playing||simulating?'play':'edit',epoch,selectedId,meshes,actors:actorRows,totalMeshes:parts.length,totalActors:actors.length,canUndo:!!undoButton&&!undoButton.disabled,canRedo:!!redoButton&&!redoButton.disabled};
  if(new TextEncoder().encode(JSON.stringify(value)).length>32768)throw Error('EDITOR_CONTEXT_TOO_LARGE');return value;
}
function setStatus(message,error=false){if(status){status.textContent=message;status.dataset.error=String(error);}}
function send(type,payload={},requestId=id(),transfer=[]){if(!port)throw Error('CHAT_NOT_CONNECTED');port.postMessage({protocol:PROTOCOL,hostId,channelId,type,requestId,payload},transfer);return requestId;}
function rpc(type,payload={},transfer=[]){if(!ready)return Promise.reject(Error('Chat is still connecting.'));const requestId=id();return new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(requestId);reject(Error('Chat connection timed out.'));},type==='cloud.save'||type==='cloud.load'?180000:30000);pending.set(requestId,{resolve,reject,timer});try{send(type,payload,requestId,transfer);}catch(error){clearTimeout(timer);pending.delete(requestId);reject(error);}});}
function validEnvelope(value){return value&&typeof value==='object'&&value.protocol===PROTOCOL&&value.hostId===hostId&&value.channelId===channelId&&bounded(value.type,64)&&bounded(value.requestId,128)&&value.payload&&typeof value.payload==='object';}
async function hostRequest(path,body,capability=lease){
  const headers={'Content-Type':'application/json'};if(capability)headers['X-Swrlz-Forge-Host']=capability.hostToken;
  const response=await fetch(CHAT_ORIGIN+'/api/forge/embed/host/'+path,{method:'POST',headers,body:JSON.stringify(body),mode:'cors',credentials:'omit',cache:'no-store'});
  const data=await response.json().catch(()=>({}));if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'EDITOR_CONNECTION_FAILED');return data;
}
function revoke(reason='Editor access paused.',notify=true){const previous=lease;lease=null;lastContext=null;clearTimeout(heartbeatTimer);heartbeatTimer=null;if(previous)hostRequest('close',{leaseId:previous.leaseId},previous).catch(()=>{});if(port&&notify)try{send('host.inactive',{reason});}catch{};}
async function heartbeat(){
  if(!lease||!isVisible()){revoke();return;}
  const active=lease;
  try{const ctx=context();if(ctx.projectId!==active.projectId||ctx.workspace!==active.workspace){revoke('Project or editor changed.');return;}
    await hostRequest('heartbeat',{leaseId:active.leaseId,visible:true,hostId,channelId,threadId:active.threadId,projectId:active.projectId,context:ctx},active);
    if(lease===active)heartbeatTimer=setTimeout(heartbeat,5000);
  }catch(error){if(lease===active){revoke();setStatus('Editor access paused. Send a new message to reconnect.',true);}}
}
function validateOperation(op,ctx){
  if(!op||typeof op!=='object'||Array.isArray(op))throw Error('INVALID_OPERATION');
  const spec={
    'mesh.add':[['op','kind'],['name','position','rotation','scale','color','material']],
    'mesh.set':[['op','id'],['name','position','rotation','scale','color','material']],
    'mesh.select':[['op','id'],[]],'mesh.duplicate':[['op','id'],[]],'mesh.remove':[['op','id'],[]],
    'sceneactor.add':[['op','prefab'],['name','position']],
    'sceneactor.transform':[['op','id'],['position','rotation','scale']],
    'sceneactor.select':[['op','id'],[]],'sceneactor.rename':[['op','id','name'],[]],
    'editor.undo':[['op'],[]],'editor.redo':[['op'],[]]
  }[op.op];
  if(!spec||spec[0].some(k=>!Object.hasOwn(op,k))||Object.keys(op).some(k=>!spec.flat().includes(k)))throw Error('UNSUPPORTED_OPERATION');
  if(ctx.mode!=='edit')throw Error('STOP_PLAY_BEFORE_EDITING');
  if(op.op==='editor.undo'&&ctx.canUndo!==true||op.op==='editor.redo'&&ctx.canRedo!==true)throw Error('NO_HISTORY_STEP');
  if(op.op.startsWith('mesh.')&&ctx.workspace!=='model-atelier'||op.op.startsWith('sceneactor.')&&ctx.workspace!=='scene')throw Error('WRONG_EDITOR_WORKSPACE');
  for(const key of ['position','rotation','scale'])if(Object.hasOwn(op,key)&&(!vector(op[key])||key==='scale'&&op[key].some(n=>n<=.005||n>20)))throw Error('INVALID_TRANSFORM');
  if(Object.hasOwn(op,'name')&&!bounded(op.name))throw Error('INVALID_NAME');
  if(Object.hasOwn(op,'color')&&(typeof op.color!=='string'||!/^#[0-9a-fA-F]{6}$/.test(op.color)))throw Error('INVALID_COLOR');
  if(Object.hasOwn(op,'material')&&!MATERIALS.has(op.material))throw Error('INVALID_MATERIAL');
  if(op.op==='mesh.add'&&!KINDS.has(op.kind)||op.op==='sceneactor.add'&&!PREFABS.has(op.prefab))throw Error('INVALID_PRIMITIVE');
  if((op.op==='mesh.set'||op.op==='sceneactor.transform')&&!spec[1].some(k=>Object.hasOwn(op,k)))throw Error('EMPTY_EDIT');
  if(Object.hasOwn(op,'id')){
    const rows=op.op.startsWith('mesh.')?ctx.meshes:ctx.actors;if(!bounded(op.id,160)||!rows.some(p=>p.id===op.id))throw Error('TARGET_NOT_IN_SNAPSHOT');
  }
}
function execute(op){
  if(op.op.startsWith('mesh.')||op.op.startsWith('editor.')&&atelierOpen())return ModelAtelier.chatAction(op);
  const agent=window.SWYRL_ENGINE_AGENT;
  if(op.op==='sceneactor.add'){
    const newId=agent.spawn(op.prefab,{...(op.name?{name:op.name}:{}),...(op.position?{position:op.position}:{})});
    const actual=actors.find(a=>a.userData.id===newId);if(!actual)throw Error('SPAWN_NOT_APPLIED');return {id:newId,name:actual.name,position:actual.position.toArray(),changed:true};
  }
  const a=op.id?actors.find(item=>item.userData.id===op.id):null;
  if(op.op==='sceneactor.transform'){
    if(!a||!agent.setTransform(op.id,Object.fromEntries(['position','rotation','scale'].filter(k=>Object.hasOwn(op,k)).map(k=>[k,op[k]]))))throw Error('TRANSFORM_NOT_APPLIED');
    const result={id:a.userData.id,position:a.position.toArray(),rotation:[a.rotation.x,a.rotation.y,a.rotation.z],scale:a.scale.toArray()};
    if(['position','rotation','scale'].some(k=>op[k]&&result[k].some((n,i)=>Math.abs(n-op[k][i])>1e-8)))throw Error('TRANSFORM_NOT_APPLIED');return {changed:true,...result};
  }
  if(op.op==='sceneactor.select'){if(!a)throw Error('ACTOR_NOT_FOUND');selectActor(a);if(selected?.userData.id!==op.id)throw Error('SELECTION_NOT_APPLIED');return {id:op.id,selectedId:op.id};}
  if(op.op==='sceneactor.rename'){if(!a)throw Error('ACTOR_NOT_FOUND');beginTransaction('Chat rename '+a.name);a.name=op.name;rebuildHierarchy();syncInspector();commitTransaction('Chat rename');if(a.name!==op.name)throw Error('RENAME_NOT_APPLIED');return {id:op.id,name:a.name,changed:true};}
  if(op.op==='editor.undo'||op.op==='editor.redo'){
    const back=op.op==='editor.undo',button=document.getElementById(back?'undoBtn':'redoBtn');if(!button||button.disabled)throw Error('NO_HISTORY_STEP');const before=historyIndex;button.click();if(historyIndex===before)throw Error('HISTORY_NOT_APPLIED');return {changed:true,historyIndex};
  }
  throw Error('UNSUPPORTED_OPERATION');
}
async function applyBatch(payload){
  if(!lease||!isVisible()||payload.leaseId!==lease.leaseId||seenBatches.has(payload.batchId))return;
  const active=lease;seenBatches.add(payload.batchId);if(seenBatches.size>256)seenBatches.delete(seenBatches.values().next().value);
  clearTimeout(heartbeatTimer);heartbeatTimer=null;
  let taken;
  try{
    taken=await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/take',{leaseId:active.leaseId},active);
    const before=context(),binding=taken.preconditions;
    if(!isVisible()||lease!==active||!binding||binding.leaseId!==active.leaseId||binding.threadId!==active.threadId||binding.projectId!==before.projectId||binding.generationId!==payload.generationId||JSON.stringify(binding.context)!==JSON.stringify(before))throw Error('STALE_NATIVE_PRECONDITIONS');
    if(!Array.isArray(taken.operations)||!taken.operations.length||taken.operations.length>MAX_BATCH)throw Error('INVALID_BATCH');
    if(taken.operations.length>1&&taken.operations.some(op=>op?.op==='editor.undo'||op?.op==='editor.redo'))throw Error('HISTORY_REQUIRES_SEPARATE_BATCH');
    for(const op of taken.operations)validateOperation(op,before);
    const results=[];let failed=false;
    for(const op of taken.operations){
      if(failed){results.push({op:op.op,ok:false,code:'PREVIOUS_OPERATION_FAILED'});continue;}
      try{const now=context();if(!isVisible()||lease!==active||now.projectId!==before.projectId||now.workspace!==before.workspace||now.mode!=='edit')throw Error('EDITOR_DETACHED');
        results.push({op:op.op,ok:true,...execute(op)});
      }catch(error){failed=true;results.push({op:op.op,ok:false,code:summaryName(error.message)});}
    }
    await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/finish',{leaseId:active.leaseId,receiptNonce:taken.receiptNonce,results,context:context()},active);
    setStatus(failed?'Some editor actions could not finish. See Chat for the receipts.':'Native editor changes applied. Undo is available.',failed);
  }catch(error){
    if(taken?.receiptNonce&&Array.isArray(taken.operations))try{await hostRequest('batches/'+encodeURIComponent(payload.batchId)+'/finish',{leaseId:active.leaseId,receiptNonce:taken.receiptNonce,results:taken.operations.map(op=>({op:op.op,ok:false,code:summaryName(error.message)})),context:context()},active);}catch{}
    setStatus('Editor actions paused: '+summaryName(error.message),true);
  }finally{if(lease===active&&isVisible())heartbeatTimer=setTimeout(heartbeat,5000);}
}
async function receive(message){
  if(!validEnvelope(message))return;
  const {type,payload,requestId}=message;
  if(type==='rpc.result'){
    const item=pending.get(requestId);if(!item)return;pending.delete(requestId);clearTimeout(item.timer);
    if(payload.ok===false)item.reject(Error(typeof payload.error==='string'?payload.error:'Chat request failed.'));else item.resolve(payload.result??payload);
    return;
  }
  if(type==='account.status'){
    revoke('Account changed.');const user=payload.user;accountText.textContent=payload.authenticated&&user?'Connected · '+summaryName(user.name||user.email||'Google account'):'Google account not connected';
    setStatus(payload.authenticated?'Your Chat account is connected.':'Sign in to load your Chat history and save projects to your account.');return;
  }
  if(type==='account.signInRequested'){document.getElementById('seChatSignIn').focus();setStatus('Choose “Sign in with Google” above to connect your account.');return;}
  if(type==='host.context'){
    try{if(!isVisible())throw Error('EDITOR_PANEL_NOT_VISIBLE');const ctx=context();lastContext=ctx;send('rpc.result',{ok:true,result:{projectId:ctx.projectId,context:ctx}},requestId);}catch(error){send('rpc.result',{ok:false,error:error.message},requestId);}return;
  }
  if(type==='host.presence'){
    const expectedContext=lastContext;revoke('Reconnecting editor.',false);
    try{
      if(!isVisible())throw Error('EDITOR_PANEL_NOT_VISIBLE');const ctx=context();
      if(!expectedContext||JSON.stringify(ctx)!==JSON.stringify(expectedContext)||payload.projectId!==ctx.projectId||payload.hostId!==hostId||payload.channelId!==channelId||!bounded(payload.threadId,160))throw Error('EDITOR_CONTEXT_CHANGED');
      const result=await hostRequest('activate',{ticket:payload.ticket,visible:true,hostId,channelId,threadId:payload.threadId,projectId:ctx.projectId,context:ctx},null);
      if(!isVisible()||context().projectId!==ctx.projectId){if(result.hostToken)hostRequest('close',{leaseId:result.leaseId},result).catch(()=>{});throw Error('EDITOR_PANEL_CLOSED');}
      lease={...result,threadId:payload.threadId,projectId:ctx.projectId,workspace:ctx.workspace};
      heartbeatTimer=setTimeout(heartbeat,5000);send('rpc.result',{ok:true,result:{leaseId:result.leaseId}},requestId);setStatus('Chat can edit this active workspace. Close the panel to pause access.');
    }catch(error){send('rpc.result',{ok:false,error:error.message},requestId);}return;
  }
  if(type==='host.batch'){await applyBatch(payload);return;}
  if(type==='host.revoke'||type==='account.logout')revoke('Chat session changed.');
}
function handshake(event){
  if(event.origin===CHAT_ORIGIN&&event.source===popup&&popupPair&&event.data?.protocol===PROTOCOL&&event.data.type==='popup.ready'&&event.data.hostId===hostId&&event.data.channelId===channelId&&bounded(event.data.requestId,128)&&event.data.payload?.pairId===popupPair){
    popup.postMessage({protocol:PROTOCOL,hostId,channelId,type:'popup.bind',requestId:event.data.requestId,payload:{pairId:popupPair}},CHAT_ORIGIN);return;
  }
  if(!frame||event.origin!==CHAT_ORIGIN||event.source!==frame.contentWindow||!validEnvelope(event.data)||event.data.type!=='iframe.ready'||port)return;
  const channel=new MessageChannel();port=channel.port1;port.onmessage=e=>{receive(e.data).catch(error=>setStatus('Chat connection error: '+summaryName(error.message),true));};port.start();
  frame.contentWindow.postMessage({protocol:PROTOCOL,hostId,channelId,type:'host.connect',requestId:id(),payload:{}},CHAT_ORIGIN,[channel.port2]);
  ready=true;setStatus('Chat connected. Sign in to use your account.');send('host.visibility',{visible:isVisible()});
}
function openPanel(){open=true;panel.hidden=false;document.getElementById('seChatToggle').setAttribute('aria-expanded','true');document.getElementById('seChatClose').focus();if(!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';if(port)send('host.visibility',{visible:true});}
function closePanel(){revoke();open=false;panel.hidden=true;document.getElementById('seChatToggle').setAttribute('aria-expanded','false');document.getElementById('seChatToggle').focus();}
async function signIn(){
  if(!ready){setStatus('Chat is still connecting. Try sign-in when it is ready.',true);return;}
  popup=window.open('about:blank','seChatAccountConnect','popup,width=520,height=700');if(!popup){setStatus('Allow the account sign-in popup, then try again.',true);return;}
  try{const result=await rpc('account.signIn');const url=new URL(result.loginUrl,CHAT_ORIGIN);if(url.origin!==CHAT_ORIGIN||url.pathname!=='/forge/login'||!bounded(result.pairId,128)||url.searchParams.get('pairId')!==result.pairId)throw Error('INVALID_LOGIN_URL');popupPair=result.pairId;popup.location.href=url.href;setStatus('Complete Google sign-in and Connect in the account window.');}
  catch(error){popup.close();popup=null;popupPair=null;setStatus(error.message,true);}
}
async function saveCloud(){
  if(cloudBusy)return;cloudBusy=true;
  try{revoke('Saving project.');const projectId=getProjectId(),native=window.SWYRL_ENGINE_AGENT.inspectScene(),text=JSON.stringify(native),bytes=new TextEncoder().encode(text);
    if(bytes.byteLength>MAX_RAW)throw Error('This project exceeds the 96 MiB account limit. Use local Save Project to keep the complete file.');
    const previous=cloudRefs.get(projectId);setStatus('Saving complete native project to your account…');
    const result=await rpc('cloud.save',{bytes:bytes.buffer,name:summaryName(currentProject.name)||'§E project',...(previous?{projectId:previous.id,expectedRevision:previous.revision}:{expectedRevision:0})},[bytes.buffer]);
    const stored=result.project;if(!stored?.id||!Number.isInteger(stored.revision)||result.durable!==true)throw Error('Cloud save was not confirmed. Keep your local project.');
    cloudRefs.set(projectId,stored);setStatus('Saved to your account · revision '+stored.revision+'.');
  }catch(error){setStatus('Account save failed: '+error.message,true);}finally{cloudBusy=false;}
}
async function listCloud(){
  try{setStatus('Loading account project list…');const result=await rpc('cloud.list');if(!Array.isArray(result.projects))throw Error('Invalid project list.');cloudList.replaceChildren();
    const blank=document.createElement('option');blank.value='';blank.textContent=result.projects.length?'Choose an account project':'No account projects saved';cloudList.append(blank);
    for(const p of result.projects){const option=document.createElement('option');option.value=p.id;option.textContent=summaryName(p.name)+' · revision '+p.revision;cloudList.append(option);}setStatus('Choose a project, then Load.');
  }catch(error){setStatus(error.message,true);}
}
async function loadCloud(){
  if(cloudBusy)return;const projectId=cloudList.value;if(!projectId){setStatus('Choose an account project first.',true);return;}
  if(dirty&&!window.confirm('Load this account project and replace unsaved local changes? Save the current project first if you want to keep them.'))return;
  cloudBusy=true;
  try{revoke('Loading project.');setStatus('Loading complete native project…');const result=await rpc('cloud.load',{projectId});
    if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX_RAW||!result.project?.id)throw Error('Invalid account project download.');
    const native=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result.bytes));if(!native?.project||!native?.editor||!Array.isArray(native.scene?.actors))throw Error('Invalid native project.');
    // Validate before replacing the editor and retain a recovery snapshot if a
    // native importer fails after starting its transaction.
    const recovery=window.SWYRL_ENGINE_AGENT.inspectScene();
    try{window.SWYRL_ENGINE_AGENT.loadScene(native);ModelAtelier.syncProject();if(currentProject.kind==='model-atelier')ModelAtelier.open();}
    catch(error){try{window.SWYRL_ENGINE_AGENT.loadScene(recovery);ModelAtelier.syncProject();}catch{}throw error;}
    cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');
  }catch(error){setStatus('Account load failed: '+error.message,true);}finally{cloudBusy=false;}
}
function mount(){
  if(document.getElementById('seChatAccountPanel')||disposed)return;
  const css=document.createElement('style');css.textContent=`
#seChatToggle{position:fixed;right:14px;bottom:calc(18px + env(safe-area-inset-bottom));z-index:2147482200;background:#a58cff;color:#100d1e;border:1px solid #d4c7ff;border-radius:28px;padding:13px 18px;font:700 14px system-ui;box-shadow:0 8px 28px #0008;cursor:pointer}
#seChatAccountPanel{position:fixed;inset:8px 8px 8px auto;width:min(480px,calc(100vw - 16px));z-index:2147482300;background:#141326;color:#f3efff;border:1px solid #776496;border-radius:16px;box-shadow:-12px 0 60px #0009;display:flex;flex-direction:column;overflow:hidden;font:13px system-ui;max-height:calc(100dvh - 16px)}
#seChatAccountPanel[hidden]{display:none!important}#seChatAccountPanel header{display:flex;align-items:center;gap:8px;padding:12px 14px;background:#211d36}#seChatAccountPanel header strong{flex:1;font-size:16px}#seChatAccountPanel button,#seChatAccountPanel select{min-height:36px;border:1px solid #655680;border-radius:8px;background:#30283f;color:#fff;padding:7px 10px;cursor:pointer}#seChatAccountPanel button:focus-visible,#seChatToggle:focus-visible,#seChatAccountPanel select:focus-visible{outline:3px solid #aadaff;outline-offset:2px}#seChatAccountPanel .se-chat-account{padding:8px 12px;border-bottom:1px solid #443953;display:grid;gap:7px}#seChatAccountPanel .se-chat-row{display:flex;flex-wrap:wrap;gap:7px;align-items:center}#seChatAccountPanel select{flex:1;min-width:140px;max-width:100%}#seChatStatus{color:#cec7de;max-height:64px;overflow:auto;font-size:12px;line-height:1.4}#seChatStatus[data-error=true]{color:#ffb8b8}#seChatFrame{display:block;flex:1;min-height:160px;width:100%;border:0;background:#121018}#seChatAccountPanel a{color:#c5b1ff}@media(max-width:620px){#seChatAccountPanel{inset:0;width:100vw;height:100dvh;max-height:100dvh;border-radius:0}#seChatToggle{padding:10px 14px;bottom:calc(72px + env(safe-area-inset-bottom))}}
`;
  document.head.append(css);
  const toggle=document.createElement('button');toggle.id='seChatToggle';toggle.type='button';toggle.textContent='§ Chat';toggle.setAttribute('aria-controls','seChatAccountPanel');toggle.setAttribute('aria-expanded','false');toggle.title='Open your §wyrlz Chat and account projects';toggle.onclick=()=>open?closePanel():openPanel();
  panel=document.createElement('aside');panel.id='seChatAccountPanel';panel.hidden=true;panel.setAttribute('aria-label','§wyrlz Chat and account projects');
  panel.innerHTML='<header><strong>§wyrlz Chat</strong><a href="https://kamiloki-swyrlz.hf.space" target="_blank" rel="noopener">Open Chat</a><button type="button" id="seChatClose" aria-label="Close Chat panel">×</button></header><section class="se-chat-account" aria-label="Google account and cloud projects"><div class="se-chat-row"><span id="seChatAccount">Google account not connected</span><button type="button" id="seChatSignIn">Sign in with Google</button></div><div class="se-chat-row"><button type="button" id="seChatSave">Save to account</button><button type="button" id="seChatRefresh">My projects</button></div><div class="se-chat-row"><select id="seChatProjects" aria-label="Saved account projects"><option value="">Choose My projects to browse</option></select><button type="button" id="seChatLoad">Load</button></div><div id="seChatStatus" role="status" aria-live="polite">Your local editor works without signing in.</div></section>';
  frame=document.createElement('iframe');frame.id='seChatFrame';frame.title='Your §wyrlz Chat';frame.setAttribute('referrerpolicy','strict-origin');frame.setAttribute('allow','clipboard-write');frame.setAttribute('sandbox','allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox allow-downloads');
  panel.append(frame);document.body.append(toggle,panel);status=document.getElementById('seChatStatus');accountText=document.getElementById('seChatAccount');cloudList=document.getElementById('seChatProjects');
  document.getElementById('seChatClose').onclick=closePanel;document.getElementById('seChatSignIn').onclick=signIn;document.getElementById('seChatSave').onclick=saveCloud;document.getElementById('seChatRefresh').onclick=listCloud;document.getElementById('seChatLoad').onclick=loadCloud;
  panel.addEventListener('keydown',event=>{if(event.key==='Escape'&&event.target!==frame){event.preventDefault();event.stopPropagation();closePanel();}});
  frame.addEventListener('load',()=>{if(port){revoke('Chat reloaded.');port.close();port=null;ready=false;}frame.contentWindow.postMessage({protocol:PROTOCOL,hostId,channelId,type:'host.hello',requestId:id(),payload:{parentOrigin:location.origin}},CHAT_ORIGIN);});
  window.addEventListener('message',handshake);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)revoke('Editor hidden.');if(port)send('host.visibility',{visible:isVisible()});});
  window.addEventListener('pagehide',()=>{disposed=true;revoke('Editor closed.');});
}
const nativeMarkDirty=markDirty;markDirty=function(...args){epoch++;return nativeMarkDirty.apply(this,args);};
const nativeLoadProject=loadProject;loadProject=function(...args){
  const preserve=args[1]?.preserveHistory===true,previousId=preserve?getProjectId():null;epoch++;if(!preserve)revoke('Project changed.');
  const result=nativeLoadProject.apply(this,args);if(preserve&&currentProject&&typeof currentProject==='object')projectIds.set(currentProject,previousId);return result;
};
// A deployment on a different origin can still edit locally, but cannot mount a
// credentialed Chat host. Tests use explicit harness origins, never URL flags.
if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(mount);
})();
