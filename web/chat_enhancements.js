(()=>{"use strict";
const GOOGLE_CLIENT_KEY='swrlzGoogleLoginTestClientId';
const GOOGLE_CLAIMS_KEY='swrlzGoogleLoginTestClaims';
const ACCOUNT_PREFS_KEY='swrlzAccountPrefsV1';
const GIS_SRC='https://accounts.google.com/gsi/client';

function make(tag,attrs={},html=''){
  const el=document.createElement(tag);
  Object.entries(attrs).forEach(([k,v])=>{if(k==='class')el.className=v;else if(k==='text')el.textContent=v;else if(v!==null&&v!==undefined)el.setAttribute(k,v)});
  if(html)el.innerHTML=html;
  return el;
}
function safeClaims(raw){try{const v=JSON.parse(raw||'null');return v&&v.authenticated?v:null}catch{return null}}
function readPrefs(){try{return {...{displayName:'',preferredName:'',useGoogleName:true,responseDepth:'adaptive',retainLocalPrefs:true},...(JSON.parse(localStorage.getItem(ACCOUNT_PREFS_KEY)||'{}')||{})}}catch{return {displayName:'',preferredName:'',useGoogleName:true,responseDepth:'adaptive',retainLocalPrefs:true}}}
function savePrefs(next){localStorage.setItem(ACCOUNT_PREFS_KEY,JSON.stringify(next))}
function esc(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function decodeJwtPayload(token){
  const part=String(token||'').split('.')[1];if(!part)throw new Error('Google credential was not a JWT');
  const normalized=part.replace(/-/g,'+').replace(/_/g,'/');
  const padded=normalized+'='.repeat((4-normalized.length%4)%4);
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

function setupAccountFooter(){
  const foot=document.querySelector('.sidebar-foot');
  if(!foot||document.querySelector('#swrlzAccountDock'))return;
  const dock=make('div',{id:'swrlzAccountDock',class:'swrlz-account-dock'});
  const loginHost=make('div',{class:'swrlz-google-host','aria-live':'polite'});
  const account=make('div',{class:'swrlz-account-card',hidden:'hidden'});
  const gear=make('button',{id:'swrlzAccountSettings',type:'button',class:'swrlz-account-gear','aria-label':'Account settings',title:'Account settings'},'⚙');
  dock.append(loginHost,account,gear);
  const versionLine=foot.querySelector('#swrlzChatVersion,.swrlz-version-line');foot.insertBefore(dock,versionLine||null);
  let claims=safeClaims(sessionStorage.getItem(GOOGLE_CLAIMS_KEY));

  const renderAccount=()=>{
    claims=safeClaims(sessionStorage.getItem(GOOGLE_CLAIMS_KEY));
    if(!claims){account.hidden=true;loginHost.hidden=false;return}
    loginHost.hidden=true;account.hidden=false;
    const prefs=readPrefs();
    const shown=(prefs.useGoogleName?claims.name:null)||prefs.displayName||prefs.preferredName||claims.email||'Google account';
    const pic=claims.picture?`<img src="${esc(claims.picture)}" alt="">`:'<span class="swrlz-account-avatar-fallback">G</span>';
    account.innerHTML=`${pic}<span class="swrlz-account-copy"><strong>${esc(shown)}</strong><span>${esc(claims.email||'')}</span></span>`;
  };
  const handleCredential=(response)=>{
    try{
      const c=decodeJwtPayload(response?.credential);
      const safe={authenticated:true,name:c.name||null,given_name:c.given_name||null,family_name:c.family_name||null,email:c.email||null,email_verified:c.email_verified===true,picture:c.picture||null,issuer:c.iss||null,subject:c.sub||null,expires_at:c.exp?new Date(c.exp*1000).toISOString():null};
      sessionStorage.setItem(GOOGLE_CLAIMS_KEY,JSON.stringify(safe));renderAccount();
    }catch(_){loginHost.innerHTML='<div class="swrlz-google-state error">Google sign-in could not be completed.</div>'}
  };
  const bootGoogle=async()=>{
    loginHost.hidden=false;loginHost.innerHTML='';
    const clientId=localStorage.getItem(GOOGLE_CLIENT_KEY);
    if(!clientId){loginHost.innerHTML='<div class="swrlz-google-state">Google sign-in is not configured on this device.</div>';return}
    try{
      const id=await loadGoogleIdentity();
      id.initialize({client_id:clientId,callback:handleCredential,auto_select:false,cancel_on_tap_outside:true});
      const target=make('div',{class:'swrlz-google-button'});loginHost.appendChild(target);
      id.renderButton(target,{type:'standard',theme:'outline',size:'large',text:'signin_with',shape:'pill',width:Math.max(230,Math.min(360,loginHost.clientWidth||320))});
    }catch(_){loginHost.innerHTML='<div class="swrlz-google-state error">Google sign-in is temporarily unavailable.</div>'}
  };

  const closeModal=modal=>modal?.remove();
  const signOut=(modal)=>{
    sessionStorage.removeItem(GOOGLE_CLAIMS_KEY);try{window.google?.accounts?.id?.disableAutoSelect?.()}catch(_){ }
    claims=null;renderAccount();bootGoogle();closeModal(modal);
  };
  const renderSection=(panel,key)=>{
    const detail=panel.querySelector('[data-detail]');const prefs=readPrefs();claims=safeClaims(sessionStorage.getItem(GOOGLE_CLAIMS_KEY));
    const identityName=claims?.name||'Not signed in',email=claims?.email||'—',verified=claims?.email_verified?'Verified':'Not verified';
    const sections={
      profile:`<h3>Profile</h3><div class="swrlz-setting-grid"><label>Google name<input value="${esc(identityName)}" disabled></label><label>Email<input value="${esc(email)}" disabled></label><label>Display name<input data-pref="displayName" value="${esc(prefs.displayName)}" placeholder="Optional display name"></label><label>Preferred name<input data-pref="preferredName" value="${esc(prefs.preferredName)}" placeholder="How §wyrlz should address you"></label></div><label class="swrlz-check"><input type="checkbox" data-pref-check="useGoogleName" ${prefs.useGoogleName?'checked':''}>Use Google account name when available</label><button type="button" data-save-prefs>Save profile preferences</button>`,
      data:`<h3>Data & privacy</h3><div class="swrlz-setting-row"><strong>Chat storage</strong><span>Current Chat history remains private on this device unless a server account-storage feature explicitly moves it.</span></div><div class="swrlz-setting-row"><strong>Account preferences</strong><span>These settings are stored locally in this browser today. Google credential tokens and the hidden client configuration are not shown here.</span></div><label class="swrlz-check"><input type="checkbox" data-pref-check="retainLocalPrefs" ${prefs.retainLocalPrefs?'checked':''}>Keep local account preferences on this device</label><button type="button" data-clear-prefs>Clear local account preferences</button>`,
      personalization:`<h3>Personalization</h3><div class="swrlz-setting-grid"><label>Response depth<select data-pref="responseDepth"><option value="adaptive" ${prefs.responseDepth==='adaptive'?'selected':''}>Adaptive</option><option value="concise" ${prefs.responseDepth==='concise'?'selected':''}>Concise</option><option value="detailed" ${prefs.responseDepth==='detailed'?'selected':''}>Detailed</option></select></label><label>Preferred name<input data-pref="preferredName" value="${esc(prefs.preferredName)}" placeholder="Optional"></label></div><button type="button" data-save-prefs>Save personalization</button>`,
      security:`<h3>Security</h3><div class="swrlz-setting-row"><strong>Google sign-in</strong><span>${claims?'Signed in':'Not signed in'}</span></div><div class="swrlz-setting-row"><strong>Email status</strong><span>${esc(verified)}</span></div><div class="swrlz-setting-row"><strong>Session expires</strong><span>${esc(claims?.expires_at||'—')}</span></div><div class="swrlz-setting-row"><strong>Credential display</strong><span>OAuth client configuration and Google credential tokens stay hidden from the account UI.</span></div>${claims?'<button type="button" class="swrlz-signout" data-signout>Sign out</button>':''}`
    };
    detail.innerHTML=sections[key]||sections.profile;
    const collect=()=>{const next=readPrefs();detail.querySelectorAll('[data-pref]').forEach(el=>next[el.dataset.pref]=el.value);detail.querySelectorAll('[data-pref-check]').forEach(el=>next[el.dataset.prefCheck]=el.checked);return next};
    detail.querySelector('[data-save-prefs]')?.addEventListener('click',()=>{savePrefs(collect());renderAccount();renderSection(panel,key)});
    detail.querySelector('[data-clear-prefs]')?.addEventListener('click',()=>{localStorage.removeItem(ACCOUNT_PREFS_KEY);renderAccount();renderSection(panel,key)});
    detail.querySelector('[data-signout]')?.addEventListener('click',()=>signOut(panel.closest('.swrlz-account-modal')));
  };
  const openSettings=()=>{
    const modal=make('div',{class:'swrlz-modal swrlz-account-modal','data-account-modal':'true'});const panel=make('div',{class:'swrlz-panel swrlz-account-panel'});
    claims=safeClaims(sessionStorage.getItem(GOOGLE_CLAIMS_KEY));
    panel.innerHTML=`<div class="swrlz-panel-head"><div><strong>Account settings</strong><div class="swrlz-account-sub">${claims?`${esc(claims.name||'Google account')}<span>${esc(claims.email||'')}</span>`:'Not signed in'}</div></div><button type="button" data-close>Close</button></div><div class="swrlz-settings-shell"><nav class="swrlz-settings-list"><button type="button" data-setting="profile"><strong>Profile</strong><span>Identity and account details</span></button><button type="button" data-setting="data"><strong>Data & privacy</strong><span>Storage and local data controls</span></button><button type="button" data-setting="personalization"><strong>Personalization</strong><span>Account-linked Chat preferences</span></button><button type="button" data-setting="security"><strong>Security</strong><span>Sign-in and session controls</span></button></nav><section class="swrlz-settings-detail" data-detail></section></div>`;
    modal.appendChild(panel);document.body.appendChild(modal);
    modal.addEventListener('click',e=>{if(e.target===modal||e.target.closest('[data-close]'))closeModal(modal)});
    panel.querySelectorAll('[data-setting]').forEach(btn=>btn.addEventListener('click',()=>{panel.querySelectorAll('[data-setting]').forEach(x=>x.classList.toggle('active',x===btn));renderSection(panel,btn.dataset.setting)}));
    const first=panel.querySelector('[data-setting="profile"]');first?.classList.add('active');renderSection(panel,'profile');
  };
  gear.addEventListener('click',openSettings);
  renderAccount();if(!claims)bootGoogle();
}

function setupLalmStatus(){
  const title=document.querySelector('#nodeTitle'),detail=document.querySelector('#nodeDetail'),light=document.querySelector('#nodeLight');if(!title||!detail||!light)return;
  const refresh=async()=>{try{const r=await fetch('/api/lalm/status',{cache:'no-store'});if(!r.ok)throw new Error();const s=await r.json(),ready=Boolean(s?.readiness?.interactiveReady),error=s?.readiness?.ok===false;light.classList.remove('ready','error');if(ready){light.classList.add('ready');title.textContent='Local LALM ready';detail.textContent='R39 resident · native backend'}else if(error){light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent=String(s?.readiness?.detail||s?.readiness?.code||'Check LALM status')}else{title.textContent='Local LALM warming';detail.textContent='R39 is being prepared'}}catch(_){light.classList.remove('ready');light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent='LALM status unavailable'}};
  refresh();window.setInterval(refresh,60000);
}
const apply=()=>{setupLalmStatus();setupAccountFooter()};if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});else apply();
})();