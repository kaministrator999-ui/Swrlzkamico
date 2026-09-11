(()=>{"use strict";
const GOOGLE_PAGE='/live/pages/google-login-test.html';
const GOOGLE_CLIENT_KEY='swrlzGoogleLoginTestClientId';
const GOOGLE_CLAIMS_KEY='swrlzGoogleLoginTestClaims';

function safeClaims(raw){
  try{const v=JSON.parse(raw||'null');return v&&v.authenticated?v:null}catch{return null}
}

function make(tag,attrs={},html=''){
  const el=document.createElement(tag);
  Object.entries(attrs).forEach(([k,v])=>{if(k==='class')el.className=v;else if(k==='text')el.textContent=v;else el.setAttribute(k,v)});
  if(html)el.innerHTML=html;
  return el;
}

function setupAccountFooter(){
  const foot=document.querySelector('.sidebar-foot');
  if(!foot||document.querySelector('#swrlzAccountDock'))return;

  const dock=make('div',{id:'swrlzAccountDock',class:'swrlz-account-dock'});
  const loginHost=make('div',{class:'swrlz-google-host'});
  const account=make('button',{type:'button',class:'swrlz-account-card',hidden:'hidden'});
  const gear=make('button',{id:'swrlzAccountSettings',type:'button',class:'swrlz-account-gear','aria-label':'Account settings',title:'Account settings'},'⚙');
  const configure=make('button',{type:'button',class:'swrlz-google-config'},'Sign in with Google');

  dock.append(loginHost,account,gear);
  const versionLine=foot.querySelector('#swrlzChatVersion,.swrlz-version-line');
  foot.insertBefore(dock,versionLine||null);

  let frame=null;
  let claims=null;

  const renderAccount=(next)=>{
    claims=next;
    if(!claims){
      account.hidden=true;
      loginHost.hidden=false;
      return;
    }
    loginHost.hidden=true;
    account.hidden=false;
    const pic=claims.picture?`<img src="${String(claims.picture).replace(/"/g,'&quot;')}" alt="">`:'<span class="swrlz-account-avatar-fallback">G</span>';
    account.innerHTML=`${pic}<span class="swrlz-account-copy"><strong>${claims.name||claims.email||'Google account'}</strong><span>${claims.email||''}</span></span>`;
  };

  const readFrameClaims=()=>{
    if(!frame?.contentWindow)return null;
    try{return safeClaims(frame.contentWindow.sessionStorage.getItem(GOOGLE_CLAIMS_KEY))}catch{return null}
  };

  const cropGooglePage=()=>{
    if(!frame?.contentDocument)return;
    try{
      const d=frame.contentDocument;
      const style=d.createElement('style');
      style.textContent='html,body{margin:0!important;min-height:0!important;background:transparent!important;padding:0!important;overflow:hidden!important}.card{width:100%!important;background:transparent!important;border:0!important;box-shadow:none!important;padding:0!important}.card>:not(.google-wrap){display:none!important}.google-wrap{margin:0!important;min-height:44px!important;display:flex!important;justify-content:center!important}.google-wrap iframe{max-width:100%!important}';
      d.head.appendChild(style);
      const pull=()=>{const c=readFrameClaims();if(c)renderAccount(c)};
      pull();
      window.setInterval(pull,700);
    }catch(_){ }
  };

  const bootGoogle=()=>{
    const configured=Boolean(localStorage.getItem(GOOGLE_CLIENT_KEY));
    loginHost.innerHTML='';
    if(!configured){
      configure.onclick=()=>window.open(GOOGLE_PAGE,'swrlz-google-setup','popup,width=620,height=760');
      loginHost.appendChild(configure);
      return;
    }
    frame=make('iframe',{class:'swrlz-google-frame',src:GOOGLE_PAGE,title:'Google sign in'});
    frame.addEventListener('load',cropGooglePage);
    loginHost.appendChild(frame);
  };

  const closeModal=(modal)=>modal?.remove();
  const openSettings=()=>{
    const modal=make('div',{class:'swrlz-modal swrlz-account-modal','data-account-modal':'true'});
    const panel=make('div',{class:'swrlz-panel swrlz-account-panel'});
    const who=claims?`${claims.name||'Google account'}${claims.email?`<span>${claims.email}</span>`:''}`:'Not signed in';
    panel.innerHTML=`<div class="swrlz-panel-head"><div><strong>Account settings</strong><div class="swrlz-account-sub">${who}</div></div><button type="button" data-close>Close</button></div><div class="swrlz-settings-list"><button type="button" data-setting="profile"><strong>Profile</strong><span>Identity and account details</span></button><button type="button" data-setting="data"><strong>Data & privacy</strong><span>Chat data, export, and account-linked storage</span></button><button type="button" data-setting="personalization"><strong>Personalization</strong><span>Preferences and §wyrlz experience</span></button><button type="button" data-setting="security"><strong>Security</strong><span>Sign-in and active account controls</span></button></div><div class="swrlz-settings-detail" data-detail>${claims?'Signed in with Google. Account-specific settings can now be attached to this identity.':'Sign in with Google to attach settings and saved Chat data to an account.'}</div>${claims?'<button type="button" class="swrlz-signout" data-signout>Sign out</button>':''}`;
    modal.appendChild(panel);document.body.appendChild(modal);
    modal.addEventListener('click',e=>{if(e.target===modal||e.target.closest('[data-close]'))closeModal(modal)});
    panel.querySelectorAll('[data-setting]').forEach(btn=>btn.addEventListener('click',()=>{
      const map={profile:'Profile settings will hold display name and account-linked profile fields.',data:'Data & privacy is the home for chat export, deletion, and account-linked data controls.',personalization:'Personalization will hold user preferences used by §wyrlz.',security:'Security controls sign-in state and future account/session management.'};
      panel.querySelector('[data-detail]').textContent=map[btn.dataset.setting]||'';
    }));
    panel.querySelector('[data-signout]')?.addEventListener('click',()=>{
      try{frame?.contentWindow?.sessionStorage.removeItem(GOOGLE_CLAIMS_KEY);frame?.contentWindow?.google?.accounts?.id?.disableAutoSelect?.()}catch(_){ }
      renderAccount(null);bootGoogle();closeModal(modal);
    });
  };

  account.addEventListener('click',openSettings);
  gear.addEventListener('click',openSettings);
  bootGoogle();
  const initial=readFrameClaims();if(initial)renderAccount(initial);
}

function setupLalmStatus(){
  const title=document.querySelector('#nodeTitle');
  const detail=document.querySelector('#nodeDetail');
  const light=document.querySelector('#nodeLight');
  if(!title||!detail||!light)return;
  const refresh=async()=>{
    try{
      const r=await fetch('/api/lalm/status',{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);
      const s=await r.json(),ready=Boolean(s?.readiness?.interactiveReady),error=s?.readiness?.ok===false;
      light.classList.remove('ready','error');
      if(ready){light.classList.add('ready');title.textContent='Local LALM ready';detail.textContent='R39 resident · native backend'}
      else if(error){light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent=String(s?.readiness?.detail||s?.readiness?.code||'Check LALM status')}
      else{title.textContent='Local LALM warming';detail.textContent='R39 is being prepared'}
    }catch(_){light.classList.remove('ready');light.classList.add('error');title.textContent='Local LALM unavailable';detail.textContent='LALM status unavailable'}
  };
  refresh();window.setInterval(refresh,60000);
}

const apply=()=>{setupLalmStatus();setupAccountFooter()};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',apply,{once:true});else apply();
})();