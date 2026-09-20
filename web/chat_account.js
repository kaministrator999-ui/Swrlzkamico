(()=>{"use strict";
const ACCOUNT_UI_VERSION='1.4.0';
const STORAGE_KEY='swrlz.vercel.chat.v1';
const MIGRATION_KEY='swrlz.account.local-import.v1';
const nativeFetch=window.fetch.bind(window);
let status=null,me=null,accountMode=false,dialog=null,activeJobs=new Map(),pollTimer=0;

function readLocal(){try{return JSON.parse(localStorage.getItem(STORAGE_KEY)||'null')}catch(_){return null}}
function writeLocal(value){localStorage.setItem(STORAGE_KEY,JSON.stringify(value));window.dispatchEvent(new StorageEvent('storage',{key:STORAGE_KEY,newValue:JSON.stringify(value)}))}
function meaningfulLocal(state){return !!state?.threads?.some(t=>Array.isArray(t.messages)&&t.messages.some(m=>String(m?.text||'').trim()))}
function toastText(text){const el=document.querySelector('#toast');if(!el)return;el.textContent=text;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2600)}
function safeJson(response){return response.json().catch(()=>({}))}

function accountButton(){
  let host=document.querySelector('.topbar-right');if(!host)return null;
  let button=document.querySelector('#swrlzAccountButton');if(button)return button;
  button=document.createElement('button');button.id='swrlzAccountButton';button.type='button';button.className='icon-button';button.title='§wyrlz account';button.setAttribute('aria-label','§wyrlz account');button.textContent='◎';button.style.fontWeight='900';button.style.fontSize='19px';button.onclick=()=>openAccount();host.append(button);return button;
}
function paintAccount(){
  const button=accountButton();if(!button)return;
  button.style.color=accountMode?'var(--trust,#4dffb4)':'inherit';
  button.title=accountMode?`Signed in${me?.user?.displayName?' as '+me.user.displayName:''}`:'Sign in to sync §wyrlz';
  const meta=document.querySelector('#currentMeta');
  if(meta&&accountMode)meta.textContent='Synced to your §wyrlz account';
}

function ensureDialog(){
  if(dialog)return dialog;
  dialog=document.createElement('dialog');dialog.id='swrlzAccountDialog';dialog.innerHTML=`
    <div style="min-width:min(560px,88vw);max-width:620px;padding:4px">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><h2 style="margin:0">§wyrlz account</h2><button type="button" data-close class="secondary-button">Close</button></div>
      <p data-summary style="color:var(--muted,#91a9c0)">Checking account…</p>
      <div data-google style="min-height:44px;margin:14px 0"></div>
      <div data-profile hidden>
        <label style="display:block;margin:10px 0">Display name<input data-display style="width:100%;margin-top:6px"></label>
        <label style="display:block;margin:10px 0">What should §wyrlz call you?<input data-preferred style="width:100%;margin-top:6px"></label>
        <label style="display:block;margin:10px 0">About you<textarea data-about rows="4" style="width:100%;margin-top:6px"></textarea></label>
        <label style="display:block;margin:10px 0">How you prefer §wyrlz to respond<textarea data-response rows="4" style="width:100%;margin-top:6px"></textarea></label>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px"><button data-save type="button" class="primary-button">Save profile</button><button data-import type="button" class="secondary-button">Import device threads</button><button data-logout type="button" class="secondary-button">Sign out</button></div>
      </div>
      <small style="display:block;margin-top:14px;color:var(--muted,#91a9c0)">Google proves identity; §wyrlz stores its own user ID, profile, threads, messages and generation journal. Closing this page does not cancel queued generation.</small>
    </div>`;
  document.body.append(dialog);
  dialog.querySelector('[data-close]').onclick=()=>dialog.close();
  dialog.querySelector('[data-save]').onclick=saveProfile;
  dialog.querySelector('[data-import]').onclick=()=>importDevice(true);
  dialog.querySelector('[data-logout]').onclick=logout;
  return dialog;
}
async function openAccount(){ensureDialog();await refreshIdentity();renderAccountDialog();dialog.showModal()}
function renderAccountDialog(){
  const d=ensureDialog(),summary=d.querySelector('[data-summary]'),profile=d.querySelector('[data-profile]'),google=d.querySelector('[data-google]');
  if(accountMode&&me){
    summary.textContent=`Signed in${me.user?.displayName?' as '+me.user.displayName:''}. Server state is authoritative.`;profile.hidden=false;google.replaceChildren();
    const p=me.profile||{},prefs=p.preferences||{},model=p.model_preferences||p.modelPreferences||{};
    d.querySelector('[data-display]').value=p.display_name||p.displayName||'';
    d.querySelector('[data-preferred]').value=prefs.preferredName||'';
    d.querySelector('[data-about]').value=prefs.about||'';
    d.querySelector('[data-response]').value=model.responsePreferences||'';
  }else{
    profile.hidden=true;summary.textContent=status?.authConfigured&&status?.storeConfigured?'Sign in with Google to restore your §wyrlz profile and conversations on this device.':'Account backend is not configured on this deployment.';
    if(status?.authConfigured&&status?.storeConfigured)renderGoogleButton(google);else google.replaceChildren();
  }
}
async function loadGoogle(){
  if(window.google?.accounts?.id)return;
  await new Promise((resolve,reject)=>{let existing=document.querySelector('script[data-swrlz-google]');if(existing){existing.addEventListener('load',resolve,{once:true});existing.addEventListener('error',reject,{once:true});return}let s=document.createElement('script');s.src='https://accounts.google.com/gsi/client';s.async=true;s.defer=true;s.dataset.swrlzGoogle='1';s.onload=resolve;s.onerror=reject;document.head.append(s)})
}
async function renderGoogleButton(host){
  if(!status?.googleClientId)return;
  try{await loadGoogle();host.replaceChildren();google.accounts.id.initialize({client_id:status.googleClientId,callback:handleGoogle,auto_select:false,cancel_on_tap_outside:true});google.accounts.id.renderButton(host,{type:'standard',theme:'outline',size:'large',text:'signin_with',shape:'pill',width:Math.min(420,Math.max(260,window.innerWidth-100))})}catch(_){host.textContent='Google Identity Services failed to load.'}
}
async function handleGoogle(response){
  const r=await nativeFetch('/api/account/google',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({credential:response.credential})}),j=await safeJson(r);if(!r.ok){toastText(j.detail||'Google sign-in failed');return}me=j;accountMode=true;await importDevice(false);await hydrateFromServer();paintAccount();renderAccountDialog();toastText('§wyrlz account connected')
}
async function refreshIdentity(){
  try{status=await (await nativeFetch('/api/account/status',{cache:'no-store'})).json();if(!status.authConfigured||!status.storeConfigured){accountMode=false;me=null;paintAccount();return}let r=await nativeFetch('/api/account/me',{cache:'no-store',credentials:'same-origin'});if(r.ok){me=await r.json();accountMode=true}else{me=null;accountMode=false}}catch(_){accountMode=false;me=null}paintAccount()
}
async function saveProfile(){
  if(!accountMode||!me)return;
  const d=ensureDialog(),p=me.profile||{},body={version:p.version,displayName:d.querySelector('[data-display]').value.trim(),preferences:{...(p.preferences||{}),preferredName:d.querySelector('[data-preferred]').value.trim(),about:d.querySelector('[data-about]').value.trim()},modelPreferences:{...(p.model_preferences||p.modelPreferences||{}),responsePreferences:d.querySelector('[data-response]').value.trim()},uiPreferences:p.ui_preferences||p.uiPreferences||{}};
  const r=await nativeFetch('/api/account/profile',{method:'PUT',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(body)}),j=await safeJson(r);if(!r.ok){toastText(j.detail||'Profile save failed');return}me.profile=j.profile;me.user.displayName=j.profile.display_name||j.profile.displayName||null;paintAccount();toastText('Profile saved')
}
async function logout(){await nativeFetch('/api/account/logout',{method:'POST',credentials:'same-origin'});accountMode=false;me=null;activeJobs.clear();paintAccount();renderAccountDialog();toastText('Signed out; device cache remains available')}
async function importDevice(force){
  if(!accountMode)return false;const local=readLocal();if(!meaningfulLocal(local))return false;if(!force&&localStorage.getItem(MIGRATION_KEY))return false;
  const r=await nativeFetch('/api/account/import-local',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify({threads:local.threads})}),j=await safeJson(r);if(!r.ok){if(force)toastText(j.detail||'Import failed');return false}localStorage.setItem(MIGRATION_KEY,new Date().toISOString());if(force)toastText(`Imported ${j.importedThreads||0} thread(s), ${j.importedMessages||0} message(s)`);return true
}

function eventApply(message,event){
  message.meta=message.meta||{trail:[]};message.meta.requestId=event.identity?.requestId||message.meta.requestId;message.meta.phase=event.phase||message.meta.phase;
  if(event.type==='DELTA')message.text=(message.text||'')+String(event.text||'');
  if(event.type==='RESET')message.text='';
  if(event.type==='ROUTE'){message.meta.route=event.identity?.route||'';message.meta.engineId=event.identity?.engineId||'';message.meta.modelId=event.identity?.modelId||''}
  if(event.firstDeltaLatencyMs!=null)message.meta.firstDeltaLatencyMs=event.firstDeltaLatencyMs;if(event.totalLatencyMs!=null)message.meta.totalLatencyMs=event.totalLatencyMs;
  if(['COMPLETED','FAILED','CANCELLED'].includes(event.type))message.state=event.type==='COMPLETED'?'complete':event.type==='FAILED'?'failed':'cancelled';else message.state='streaming';
}
async function hydrateFromServer(){
  if(!accountMode)return;let r=await nativeFetch('/api/account/state',{cache:'no-store',credentials:'same-origin'});if(!r.ok)return;let s=await r.json();
  if(!Array.isArray(s.threads)||!s.threads.length){paintAccount();return}
  const local={version:1,currentId:s.threads[0].id,threads:s.threads.map(t=>({id:t.id,title:t.title||'Conversation',createdAt:t.createdAt,updatedAt:t.updatedAt,pinned:false,messages:(t.messages||[]).map(m=>({id:m.id,role:m.role,text:m.text||'',createdAt:m.createdAt,state:m.state==='complete'?'complete':m.state==='failed'?'failed':m.state==='cancelled'?'cancelled':'streaming',pinned:false,meta:{requestId:m.requestId||'',phase:m.state==='complete'?'COMPLETE':'GENERATING',trail:[],route:'LOCAL_R39_DURABLE'}}))}))};
  activeJobs.clear();for(const job of s.activeGenerations||[]){activeJobs.set(job.requestId,{...job,lastApplied:0});let t=local.threads.find(x=>x.id===job.threadId),m=t?.messages.find(x=>x.id===job.assistantMessageId);if(m){m.text='';let er=await nativeFetch(`/api/account/generation/${encodeURIComponent(job.requestId)}/events?after=0`,{cache:'no-store',credentials:'same-origin'});if(er.ok){let ej=await er.json();for(const e of ej.events||[]){eventApply(m,e);job.lastApplied=Math.max(job.lastApplied||0,e.seq||0)}}}}
  writeLocal(local);paintAccount();scheduleActivePolling()
}
function scheduleActivePolling(){clearTimeout(pollTimer);if(!accountMode||!activeJobs.size)return;pollTimer=setTimeout(pollActive,900)}
async function pollActive(){
  if(!accountMode)return;let local=readLocal(),changed=false;
  for(const [rid,job] of [...activeJobs]){try{let r=await nativeFetch(`/api/account/generation/${encodeURIComponent(rid)}/events?after=${job.lastApplied||0}`,{cache:'no-store',credentials:'same-origin'});if(!r.ok)continue;let j=await r.json(),t=local?.threads?.find(x=>x.id===job.threadId),m=t?.messages?.find(x=>x.id===job.assistantMessageId);for(const e of j.events||[]){if(m)eventApply(m,e);job.lastApplied=Math.max(job.lastApplied||0,e.seq||0);changed=true}if(['COMPLETE','FAILED','CANCELLED'].includes(j.job?.state)){activeJobs.delete(rid)}}catch(_){}}
  if(changed&&local)writeLocal(local);scheduleActivePolling()
}

function durableStream(payload,init){
  const signal=init?.signal,encoder=new TextEncoder();let last=0,done=false;
  const body=new ReadableStream({start(controller){(async()=>{try{
    const start=await nativeFetch('/api/account/generate',{method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',body:JSON.stringify(payload)}),created=await safeJson(start);if(!start.ok)throw new Error(created.detail||`HTTP ${start.status}`);
    const rid=created.job.requestId;
    while(!done){if(signal?.aborted)throw new DOMException('Aborted','AbortError');let r=await nativeFetch(`/api/account/generation/${encodeURIComponent(rid)}/events?after=${last}`,{cache:'no-store',credentials:'same-origin'});if(!r.ok)throw new Error(`Replay HTTP ${r.status}`);let j=await r.json();for(const e of j.events||[]){if((e.seq||0)<=last)continue;last=e.seq||last;controller.enqueue(encoder.encode(JSON.stringify(e)+'\n'));if(e.terminal){done=true;break}}if(!done)await new Promise((resolve,reject)=>{let id=setTimeout(resolve,700);if(signal)signal.addEventListener('abort',()=>{clearTimeout(id);reject(new DOMException('Aborted','AbortError'))},{once:true})})}controller.close()
  }catch(err){controller.error(err)}})()}});return new Response(body,{status:200,headers:{'Content-Type':'application/x-ndjson','Cache-Control':'no-store'}})
}
const previousFetch=window.fetch.bind(window);
window.fetch=async function(input,init={}){
  const u=new URL(typeof input==='string'?input:input.url,location.href),action=u.searchParams.get('action'),method=String(init.method||'GET').toUpperCase();
  if(accountMode&&u.origin===location.origin&&u.pathname==='/api/chat'&&action==='stream'&&method==='POST'){
    let payload={};try{payload=JSON.parse(init.body||'{}')}catch(_){return previousFetch(input,init)}return durableStream(payload,init)
  }
  if(accountMode&&u.origin===location.origin&&u.pathname==='/api/chat'&&action==='cancel'&&method==='POST'){
    let body={};try{body=JSON.parse(init.body||'{}')}catch(_){};if(body.requestId)return nativeFetch(`/api/account/generation/${encodeURIComponent(body.requestId)}/cancel`,{method:'POST',credentials:'same-origin'});
  }
  return previousFetch(input,init)
};

function enhanceCodeBlocks(root=document){for(const pre of root.querySelectorAll('.bubble pre:not([data-swrlz-copy-ready])')){pre.dataset.swrlzCopyReady='1';pre.style.position='relative';let b=document.createElement('button');b.type='button';b.className='swrlz-block-copy';b.textContent='COPY';b.title='Copy this block';b.onclick=async()=>{let code=pre.querySelector('code');try{await navigator.clipboard.writeText(code?.textContent||pre.textContent||'');b.textContent='COPIED';setTimeout(()=>b.textContent='COPY',1200)}catch(_){toastText('Clipboard unavailable')}};pre.append(b)}}
const observer=new MutationObserver(records=>{for(const r of records)for(const n of r.addedNodes)if(n.nodeType===1)enhanceCodeBlocks(n)});observer.observe(document.body,{childList:true,subtree:true});enhanceCodeBlocks();
const style=document.createElement('style');style.textContent=`.swrlz-block-copy{position:absolute;top:8px;right:8px;z-index:2;border:1px solid rgba(56,232,255,.35);border-radius:8px;background:#091423;color:#cdefff;padding:5px 8px;font-size:10px;font-weight:800;letter-spacing:.06em}.swrlz-block-copy:hover{background:#10233a}#swrlzAccountDialog{background:#07111e;color:#f7fbff;border:1px solid rgba(56,232,255,.25);border-radius:20px;box-shadow:0 24px 80px #0008}#swrlzAccountDialog::backdrop{background:#000a}#swrlzAccountDialog input,#swrlzAccountDialog textarea{background:#050c17;color:#fff;border:1px solid #294866;border-radius:10px;padding:10px}`;document.head.append(style);

(async()=>{accountButton();await refreshIdentity();if(accountMode){await importDevice(false);await hydrateFromServer()}paintAccount();setInterval(()=>{if(accountMode)paintAccount()},2500)})();
})();
