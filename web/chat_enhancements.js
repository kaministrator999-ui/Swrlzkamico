(()=>{"use strict";
const GOOGLE_CLIENT_KEY='swrlzGoogleLoginTestClientId';
const GOOGLE_CLAIMS_KEY='swrlzGoogleLoginTestClaims';
const ACCOUNT_PREFS_KEY='swrlzAccountPrefsV1';
const ACCOUNT_PREFS_PREFIX='swrlzAccountPrefsV2.account.';
const PREFS_MIGRATION_KEY='swrlzAccountPrefsV2.migrated';
const CHAT_ACCOUNT_PREFIX='swrlz.vercel.chat.v2.account.';
const CHAT_MIGRATION_KEY='swrlz.vercel.chat.v2.migrated';
const GIS_SRC='https://accounts.google.com/gsi/client';

function make(tag,attrs={},html=''){
  const el=document.createElement(tag);
  Object.entries(attrs).forEach(([k,v])=>{if(k==='class')el.className=v;else if(k==='text')el.textContent=v;else if(v!==null&&v!==undefined)el.setAttribute(k,v)});
  if(html)el.innerHTML=html;
  return el;
}
function safeClaims(raw){try{const v=JSON.parse(raw||'null');return v&&v.authenticated?v:null}catch{return null}}
function currentClaims(){return safeClaims(sessionStorage.getItem(GOOGLE_CLAIMS_KEY))}
function accountSubject(){return String(currentClaims()?.subject||'').trim()}
function accountSuffix(){const subject=accountSubject();return subject?encodeURIComponent(subject):''}
function prefsKey(){const suffix=accountSuffix();return suffix?ACCOUNT_PREFS_PREFIX+suffix:ACCOUNT_PREFS_KEY}
function chatKey(){const suffix=accountSuffix();return suffix?CHAT_ACCOUNT_PREFIX+suffix:STORAGE_KEY}
function defaultPrefs(){return {displayName:'',preferredName:'',useGoogleName:true,responseDepth:'adaptive',retainLocalPrefs:true}}
function migratePrefsOnce(){
  const suffix=accountSuffix();if(!suffix)return;
  const target=ACCOUNT_PREFS_PREFIX+suffix;
  if(localStorage.getItem(target)!==null||localStorage.getItem(PREFS_MIGRATION_KEY))return;
  const legacy=localStorage.getItem(ACCOUNT_PREFS_KEY);
  if(legacy!==null)localStorage.setItem(target,legacy);
  localStorage.setItem(PREFS_MIGRATION_KEY,suffix);
}
function readPrefs(){migratePrefsOnce();try{return {...defaultPrefs(),...(JSON.parse(localStorage.getItem(prefsKey())||'{}')||{})}}catch{return defaultPrefs()}}
function savePrefs(next){localStorage.setItem(prefsKey(),JSON.stringify(next))}
function esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function decodeJwtPayload(token){
  const part=String(token||'').split('.')[1];if(!part)throw new Error('Google credential was not a JWT');
  const normalized=part.replace(/-/g,'+').replace(/_/g,'/');const padded=normalized+'='.repeat((4-normalized.length%4)%4);
  const json=decodeURIComponent(atob(padded).split('').map(c=>'%'+('00'+c.charCodeAt(0).toString(16)).slice(-2)).join(''));
  return JSON.parse(json);
}
function loadGoogleIdentity(){
  if(window.google?.accounts?.id)return Promise.resolve(window.google.accounts.id);
  if(window.__swrlzGoogleIdentityPromise)return window.__swrlzGoogleIdentityPromise;
  window.__swrlzGoogleIdentityPromise=new Promise((resolve,reject)=>{
    let script=document.querySelector(`script[src="${GIS_SRC}"]`);
    const done=()=>window.google?.accounts?.id?resolve(window.google.accounts.id):reject(new Error('Google Identity Services unavailable'));
    if(script){script.addEventListener('load',done,{once:true});script.addEventListener('error',()=>reject(new Error('Google Identity Services failed to load')),{once:true});setTimeout(()=>{if(window.google?.accounts?.id)resolve(window.google.accounts.id)},0);return}
    script=document.createElement('script');script.src=GIS_SRC;script.async=true;script.defer=true;script.onload=done;script.onerror=()=>reject(new Error('Google Identity Services failed to load'));document.head.appendChild(script);
  });
  return window.__swrlzGoogleIdentityPromise;
}

function parseChatState(raw){
  try{
    const parsed=JSON.parse(raw||'null');
    if(parsed&&parsed.version===1&&Array.isArray(parsed.threads)&&parsed.threads.length){
      parsed.threads=parsed.threads.filter(t=>t&&typeof t.id==='string'&&Array.isArray(t.messages)).slice(0,80);
      if(parsed.threads.length){parsed.currentId=parsed.threads.some(t=>t.id===parsed.currentId)?parsed.currentId:parsed.threads[0].id;return parsed}
    }
  }catch(_){ }
  const first=freshThread();return {version:1,currentId:first.id,threads:[first]};
}
function persistStateTo(key){try{localStorage.setItem(key,JSON.stringify(state));return true}catch(_){toast('Conversation storage is full; export before refreshing.');return false}}
function migrateChatOnce(){
  const suffix=accountSuffix();if(!suffix)return;
  const target=CHAT_ACCOUNT_PREFIX+suffix;
  if(localStorage.getItem(target)!==null||localStorage.getItem(CHAT_MIGRATION_KEY))return;
  const legacy=localStorage.getItem(STORAGE_KEY);
  if(legacy!==null)localStorage.setItem(target,legacy);
  localStorage.setItem(CHAT_MIGRATION_KEY,suffix);
}
function loadScopedChat(){migrateChatOnce();return parseChatState(localStorage.getItem(chatKey()))}
function switchScopedChat(){state=loadScopedChat();render(false)}
function installAccountScopedChat(){
  if(window.__swrlzAccountScopedChatInstalled)return;
  window.__swrlzAccountScopedChatInstalled=true;
  migrateChatOnce();if(accountSubject())state=loadScopedChat();
  loadState=function(){return loadScopedChat()};
  saveState=function(){persistStateTo(chatKey())};
  window.addEventListener('swrlz:account-change',switchScopedChat);
  window.addEventListener('storage',event=>{if(event.key===chatKey()){state=loadScopedChat();render(false)}});
  render(false);
}
function saveCurrentNamespace(){persistStateTo(chatKey())}
function emitAccountChange(){window.dispatchEvent(new CustomEvent('swrlz:account-change',{detail:{signedIn:Boolean(accountSubject())}}))}

function setupStreamFollow(){
  if(window.__swrlzStreamFollowInstalled)return;
  window.__swrlzStreamFollowInstalled=true;
  let eventType='',messageId='',followLocked=true,lastHeight=null,programmaticUntil=0,lifecycle=false,clearTimer=0;
  const baseRender=render,baseRenderMessage=renderMessage,baseConsume=consumeEvent;
  const article=()=>{
    const live=typeof activeMessage==='function'?activeMessage():null;
    const id=live?.id||messageId;if(!id||!refs?.stack)return null;
    return refs.stack.querySelector(`[data-message-id="${CSS.escape(id)}"]`)||null;
  };
  const bubble=()=>article()?.querySelector?.('.bubble')||null;
  const setLock=next=>{followLocked=Boolean(next);if(refs?.messages){if(followLocked)refs.messages.dataset.streamFollow='true';else delete refs.messages.dataset.streamFollow}};
  const tailAtFollowBand=()=>{
    const b=bubble();if(!b||!refs?.messages)return false;
    const v=refs.messages.getBoundingClientRect(),y=b.getBoundingClientRect().bottom;
    return y>=v.top+v.height*.34&&y<=v.top+v.height*.70;
  };
  const centerLine=()=>{
    if(!followLocked||!refs?.messages)return;
    const b=bubble();if(!b)return;
    const v=refs.messages.getBoundingClientRect(),r=b.getBoundingClientRect();
    const delta=r.bottom-(v.top+v.height*.52);if(Math.abs(delta)<=1)return;
    programmaticUntil=performance.now()+90;refs.messages.scrollTop+=delta;
  };
  const lineAdvanced=()=>{
    if(eventType==='RESET'){lastHeight=null;return false}
    if(eventType!=='DELTA')return false;
    const b=bubble();if(!b)return false;
    const h=Math.ceil(b.getBoundingClientRect().height);
    if(lastHeight==null){lastHeight=h;return false}
    const style=getComputedStyle(b),parsed=parseFloat(style.lineHeight),font=parseFloat(style.fontSize)||16,line=Number.isFinite(parsed)?parsed:font*1.5;
    const advanced=h-lastHeight>=Math.max(4,line*.45);if(advanced||h<lastHeight)lastHeight=h;return advanced;
  };
  const startFollow=()=>{lifecycle=true;lastHeight=null;setLock(true);clearTimeout(clearTimer)};
  const finishSoon=()=>{clearTimeout(clearTimer);clearTimer=setTimeout(()=>{lifecycle=false;eventType='';messageId='';lastHeight=null;if(refs?.messages)delete refs.messages.dataset.streamFollow},180)};
  if(refs?.messages&&!refs.messages.dataset.swrlzFollowBound){
    refs.messages.dataset.swrlzFollowBound='true';
    const manual=()=>{if(lifecycle&&performance.now()>=programmaticUntil)setLock(false)};
    const reevaluate=()=>{if(lifecycle&&performance.now()>=programmaticUntil&&tailAtFollowBand())setLock(true)};
    refs.messages.addEventListener('wheel',manual,{passive:true});refs.messages.addEventListener('touchstart',manual,{passive:true});refs.messages.addEventListener('pointerdown',manual,{passive:true});refs.messages.addEventListener('scroll',reevaluate,{passive:true});
  }
  render=function(scroll=false){return baseRender(scroll&&lifecycle&&!followLocked?false:scroll)};
  scheduleRender=function(scroll=false){
    if(renderQueued)return;renderQueued=true;
    requestAnimationFrame(()=>{renderQueued=false;render(false);if(scroll&&lineAdvanced())requestAnimationFrame(centerLine)});
  };
  renderMessage=function(message){
    const node=baseRenderMessage(message);if(message?.role!=='assistant')return node;
    message.meta=message.meta||{};const body=node.querySelector('.message-body'),b=node.querySelector('.bubble'),trace=node.querySelector('.trace');
    if(trace&&body&&b){trace.open=Boolean(message.meta.activityExpanded);const summary=trace.querySelector('summary');if(summary&&!String(summary.textContent||'').startsWith('Activity log'))summary.textContent=`Activity log · ${summary.textContent||'runtime'}`;trace.addEventListener('toggle',()=>{message.meta.activityExpanded=trace.open;saveState()});body.insertBefore(trace,b)}
    if(body&&b){const actions=body.querySelector('.message-actions'),evidence=body.querySelector('.swrlz-evidence');if(actions)body.insertBefore(actions,b);if(evidence)body.insertBefore(evidence,b)}
    return node;
  };
  consumeEvent=function(event,context){
    const nextType=String(event?.type||''),nextId=String(context?.message?.id||'');
    if(!lifecycle||messageId!==nextId)startFollow();eventType=nextType;messageId=nextId;
    const result=baseConsume(event,context);if(['COMPLETED','CANCELLED','FAILED'].includes(nextType))finishSoon();return result;
  };
  const style=document.createElement('style');style.textContent='.messages[data-stream-follow="true"]{scroll-behavior:auto!important}.message.assistant[data-stream-tail="true"] .bubble{scroll-margin-bottom:12px}';document.head.appendChild(style);
}

function setupAccountFooter(){
  const foot=document.querySelector('.sidebar-foot');if(!foot||document.querySelector('#swrlzAccountDock'))return;
  const dock=make('div',{id:'swrlzAccountDock',class:'swrlz-account-dock'}),loginHost=make('div',{class:'swrlz-google-host','aria-live':'polite'}),account=make('div',{class:'swrlz-account-card',hidden:'hidden'}),gear=make('button',{id:'swrlzAccountSettings',type:'button',class:'swrlz-account-gear','aria-label':'Account settings',title:'Account settings'},'⚙');
  dock.append(loginHost,account,gear);const versionLine=foot.querySelector('#swrlzChatVersion,.swrlz-version-line');foot.insertBefore(dock,versionLine||null);
  let claims=currentClaims();
  const renderAccount=()=>{
    claims=currentClaims();if(!claims){account.hidden=true;loginHost.hidden=false;return}
    loginHost.hidden=true;account.hidden=false;const prefs=readPrefs(),shown=(prefs.useGoogleName?claims.name:null)||prefs.displayName||prefs.preferredName||claims.email||'Google account';
    const pic=claims.picture?`<img src="${esc(claims.picture)}" alt="">`:'<span class="swrlz-account-avatar-fallback">G</span>';
    account.innerHTML=`${pic}<span class="swrlz-account-copy"><strong>${esc(shown)}</strong><span>${esc(claims.email||'')}</span></span>`;
  };
  const handleCredential=response=>{
    try{
      const c=decodeJwtPayload(response?.credential),safe={authenticated:true,name:c.name||null,given_name:c.given_name||null,family_name:c.family_name||null,email:c.email||null,email_verified:c.email_verified===true,picture:c.picture||null,issuer:c.iss||null,subject:c.sub||null,expires_at:c.exp?new Date(c.exp*1000).toISOString():null};
      saveCurrentNamespace();sessionStorage.setItem(GOOGLE_CLAIMS_KEY,JSON.stringify(safe));renderAccount();emitAccountChange();
    }catch(_){loginHost.innerHTML='<div class="swrlz-google-state error">Google sign-in could not be completed.</div>'}
  };
  const bootGoogle=async()=>{
    loginHost.hidden=false;loginHost.innerHTML='';const clientId=localStorage.getItem(GOOGLE_CLIENT_KEY);
    if(!clientId){loginHost.innerHTML='<div class="swrlz-google-state">Google sign-in is not configured on this device.</div>';return}
    try{const id=await loadGoogleIdentity();id.initialize({client_id:clientId,callback:handleCredential,auto_select:false,cancel_on_tap_outside:true});const target=make('div',{class:'swrlz-google-button'});loginHost.appendChild(target);id.renderButton(target,{type:'standard',theme:'outline',size:'large',text:'signin_with',shape:'pill',width:Math.max(230,Math.min(360,loginHost.clientWidth||320))})}
    catch(_){loginHost.innerHTML='<div class="swrlz-google-state error">Google sign-in is temporarily unavailable.</div>'}
  };
  const closeModal=modal=>modal?.remove();
  const signOut=modal=>{saveCurrentNamespace();sessionStorage.removeItem(GOOGLE_CLAIMS_KEY);try{window.google?.accounts?.id?.disableAutoSelect?.()}catch(_){ }claims=null;renderAccount();emitAccountChange();bootGoogle();closeModal(modal)};
  const renderSection=(panel,key)=>{
    const detail=panel.querySelector('[data-detail]'),prefs=readPrefs();claims=currentClaims();
    const identityName=claims?.name||'Not signed in',email=claims?.email||'—',verified=claims?.email_verified?'Verified':'Not verified';
    const storageScope=claims?'This browser keeps a separate Chat history and preference namespace for this signed-in Google account. Switching Google accounts switches the loaded namespace.':'You are using the signed-out browser namespace.';
    const sections={
      profile:`<h3>Profile</h3><div class="swrlz-setting-grid"><label>Google name<input value="${esc(identityName)}" disabled></label><label>Email<input value="${esc(email)}" disabled></label><label>Display name<input data-pref="displayName" value="${esc(prefs.displayName)}" placeholder="Optional display name"></label><label>Preferred name<input data-pref="preferredName" value="${esc(prefs.preferredName)}" placeholder="How §wyrlz should address you"></label></div><label class="swrlz-check"><input type="checkbox" data-pref-check="useGoogleName" ${prefs.useGoogleName?'checked':''}>Use Google account name when available</label><button type="button" data-save-prefs>Save profile preferences</button>`,
      data:`<h3>Data & privacy</h3><div class="swrlz-setting-row"><strong>Account-selected Chat storage</strong><span>${esc(storageScope)}</span></div><div class="swrlz-setting-row"><strong>Cross-device sync boundary</strong><span>Google identifies which namespace to load, but durable cross-device cloud sync is not enabled until the server has verified Google sessions plus persistent account storage. No credential token is stored in Chat history.</span></div><label class="swrlz-check"><input type="checkbox" data-pref-check="retainLocalPrefs" ${prefs.retainLocalPrefs?'checked':''}>Keep account preferences on this device</label><button type="button" data-clear-prefs>Clear this account's local preferences</button>`,
      personalization:`<h3>Personalization</h3><div class="swrlz-setting-grid"><label>Response depth<select data-pref="responseDepth"><option value="adaptive" ${prefs.responseDepth==='adaptive'?'selected':''}>Adaptive</option><option value="concise" ${prefs.responseDepth==='concise'?'selected':''}>Concise</option><option value="detailed" ${prefs.responseDepth==='detailed'?'selected':''}>Detailed</option></select></label><label>Preferred name<input data-pref="preferredName" value="${esc(prefs.preferredName)}" placeholder="Optional"></label></div><button type="button" data-save-prefs>Save personalization</button>`,
      security:`<h3>Security</h3><div class="swrlz-setting-row"><strong>Google sign-in</strong><span>${claims?'Signed in':'Not signed in'}</span></div><div class="swrlz-setting-row"><strong>Email status</strong><span>${esc(verified)}</span></div><div class="swrlz-setting-row"><strong>Session expires</strong><span>${esc(claims?.expires_at||'—')}</span></div><div class="swrlz-setting-row"><strong>Credential display</strong><span>OAuth client configuration and Google credential tokens stay hidden from the account UI and Chat storage.</span></div>${claims?'<button type="button" class="swrlz-signout" data-signout>Sign out</button>':''}`
    };
    detail.innerHTML=sections[key]||sections.profile;
    const collect=()=>{const next=readPrefs();detail.querySelectorAll('[data-pref]').forEach(el=>next[el.dataset.pref]=el.value);detail.querySelectorAll('[data-pref-check]').forEach(el=>next[el.dataset.prefCheck]=el.checked);return next};
    detail.querySelector('[data-save-prefs]')?.addEventListener('click',()=>{savePrefs(collect());renderAccount();renderSection(panel,key)});
    detail.querySelector('[data-clear-prefs]')?.addEventListener('click',()=>{localStorage.removeItem(prefsKey());renderAccount();renderSection(panel,key)});
    detail.querySelector('[data-signout]')?.addEventListener('click',()=>signOut(panel.closest('.swrlz-account-modal')));
  };
  const openSettings=()=>{
    const modal=make('div',{class:'swrlz-modal swrlz-account-modal','data-account-modal':'true'}),panel=make('div',{class:'swrlz-panel swrlz-account-panel'});claims=currentClaims();
    panel.innerHTML=`<div class="swrlz-panel-head"><div><strong>Account settings</strong><div class="swrlz-account-sub">${claims?`${esc(claims.name||'Google account')}<span>${esc(claims.email||'')}</span>`:'Not signed in'}</div></div><button type="button" data-close>Close</button></div><div class="swrlz-settings-shell"><nav class="swrlz-settings-list"><button type="button" data-setting="profile"><strong>Profile</strong><span>Identity and account details</span></button><button type="button" data-setting="data"><strong>Data & privacy</strong><span>Storage and account data controls</span></button><button type="button" data-setting="personalization"><strong>Personalization</strong><span>Account-linked Chat preferences</span></button><button type="button" data-setting="security"><strong>Security</strong><span>Sign-in and session controls</span></button></nav><section class="swrlz-settings-detail" data-detail></section></div>`;
    modal.appendChild(panel);document.body.appendChild(modal);modal.addEventListener('click',e=>{if(e.target===modal||e.target.closest('[data-close]'))closeModal(modal)});
    panel.querySelectorAll('[data-setting]').forEach(btn=>btn.addEventListener('click',()=>{panel.querySelectorAll('[data-setting]').forEach(x=>x.classList.toggle('active',x===btn));renderSection(panel,btn.dataset.setting)}));
    const first=panel.querySelector('[data-setting="profile"]');first?.classList.add('active');renderSection(panel,'profile');
  };
  gear.addEventListener('click',openSettings);renderAccount();if(!claims)bootGoogle();
}

function setupLalmStatus(){
  const title=document.querySelector('#nodeTitle'),detail=document.querySelector('#nodeDetail'),light=document.querySelector('#nodeLight');if(!title||!detail||!light)return;
  const refresh=async()=>{try{const r=await fetch('/api/lalm/status',{cache:'no-store'});if(!r.ok)throw new Error();const s=await r.json(),ready=Boolean(s?.readiness?.interactiveReady),error=s?.readiness?.ok===false;light.classList.remove('ready','error');if(ready){light.classList.add('ready');title.textContent='Local LALM ready';detail.textContent='R39 resident · native backend'}else if(error){light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent=String(s?.readiness?.detail||s?.readiness?.code||'Check LALM status')}else{title.textContent='Local LALM warming';detail.textContent='R39 is being prepared'}}catch(_){light.classList.remove('ready');light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent='LALM status unavailable'}};
  refresh();window.setInterval(refresh,60000);
}
const apply=()=>{installAccountScopedChat();setupStreamFollow();setupLalmStatus();setupAccountFooter()};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});else apply();
})();
