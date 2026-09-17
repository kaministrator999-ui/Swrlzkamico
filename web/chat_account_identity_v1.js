(()=>{'use strict';
if(window.__swrlzAccountIdentityV1Installed)return;
window.__swrlzAccountIdentityV1Installed=true;
const GOOGLE_CLAIMS_KEY='swrlzGoogleLoginTestClaims';
const ACCOUNT_PREFS_KEY='swrlzAccountPrefsV1';
const ACCOUNT_PREFS_PREFIX='swrlzAccountPrefsV2.account.';
function safeClaims(){try{const v=JSON.parse(sessionStorage.getItem(GOOGLE_CLAIMS_KEY)||'null');return v&&v.authenticated?v:null}catch{return null}}
function prefsKey(){const c=safeClaims(),subject=String(c?.subject||'').trim();return subject?ACCOUNT_PREFS_PREFIX+encodeURIComponent(subject):ACCOUNT_PREFS_KEY}
function prefs(){try{return JSON.parse(localStorage.getItem(prefsKey())||'{}')||{}}catch{return {}}}
function identity(){const c=safeClaims(),p=prefs();const useGoogle=p.useGoogleName!==false;const name=String(p.displayName||((useGoogle&&c?.name)?c.name:'')||c?.given_name||c?.email||'You').trim()||'You';return{name,picture:String(c?.picture||''),email:String(c?.email||''),googleName:String(c?.name||'')}}
function decorateUser(node,message){if(!node||message?.role!=='user')return node;const id=identity(),avatar=node.querySelector('.avatar'),who=node.querySelector('.message-label strong');if(who)who.textContent=id.name;if(avatar){avatar.classList.toggle('swrlz-user-photo',Boolean(id.picture));if(id.picture){avatar.textContent='';const img=document.createElement('img');img.src=id.picture;img.alt='';img.referrerPolicy='no-referrer';avatar.appendChild(img)}else avatar.textContent=(id.name||'You').slice(0,2).toUpperCase()}return node}
function installRenderer(){if(typeof window.renderMessage!=='function'||window.__swrlzAccountIdentityRenderWrapped)return;window.__swrlzAccountIdentityRenderWrapped=true;const base=window.renderMessage;window.renderMessage=function(message){return decorateUser(base(message),message)};try{window.render?.(false)}catch(_){}}
function makeIdentityCard(){const id=identity(),wrap=document.createElement('div');wrap.className='swrlz-account-identity';const avatar=id.picture?`<img src="${id.picture.replace(/"/g,'&quot;')}" alt="">`:'<span class="swrlz-account-avatar-fallback">'+((id.name||'U').slice(0,1).toUpperCase())+'</span>';wrap.innerHTML=`${avatar}<div><strong>${escapeHtml(id.googleName||id.name)}</strong><span>${escapeHtml(id.email||'Signed-out browser profile')}</span></div>`;return wrap}
function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function installChatFrame(){if(document.getElementById('swrlz-chat-frame-v1'))return;const style=document.createElement('style');style.id='swrlz-chat-frame-v1';style.textContent=`
@media(max-width:820px){
 html.swrlz-android-device .app{left:var(--swrlz-vv-left,0px)!important;width:var(--swrlz-vvw,100vw)!important;max-width:var(--swrlz-vvw,100vw)!important}
 html.swrlz-android-device .workspace{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important}
 html.swrlz-android-device .topbar{padding-left:max(14px,env(safe-area-inset-left))!important;padding-right:max(14px,env(safe-area-inset-right))!important}
 html.swrlz-android-device .message-stack{width:calc(100% - 28px)!important;max-width:calc(100% - 28px)!important;margin-left:14px!important;margin-right:14px!important}
 html.swrlz-android-device .composer-shell{width:100%!important;max-width:100%!important;padding-left:max(14px,env(safe-area-inset-left))!important;padding-right:max(14px,env(safe-area-inset-right))!important}
 html.swrlz-android-device .composer{width:100%!important;max-width:100%!important;margin-inline:0!important}
 html.swrlz-android-device .messages{width:100%!important;max-width:100%!important;margin:0!important}
 html.swrlz-android-device .bubble,html.swrlz-android-device .message-body{min-width:0!important;max-width:100%!important}
}
.swrlz-top-account{display:inline-grid;place-items:center;width:36px;height:36px;flex:0 0 36px;padding:0;border:1px solid rgba(145,169,192,.18);border-radius:50%;overflow:hidden;background:rgba(7,16,28,.78);color:var(--secondary);cursor:pointer;box-shadow:0 4px 18px rgba(0,0,0,.22)}
.swrlz-top-account:hover{border-color:rgba(56,232,255,.42)}
.swrlz-top-account img{display:block;width:100%;height:100%;object-fit:cover;border-radius:50%}
.swrlz-top-account span{display:grid;place-items:center;width:100%;height:100%;font-size:13px;font-weight:800;color:var(--cyan)}
@media(max-width:540px){.swrlz-top-account{width:34px;height:34px;flex-basis:34px}.topbar-right{gap:5px!important}}
`;document.head.appendChild(style)}
function renderTopAccount(){const host=document.querySelector('.topbar-right');if(!host)return;let button=document.getElementById('swrlzTopAccount');if(!button){button=document.createElement('button');button.id='swrlzTopAccount';button.type='button';button.className='swrlz-top-account';button.setAttribute('aria-label','Google account');button.title='Account';host.appendChild(button);button.addEventListener('click',()=>{const settings=document.getElementById('swrlzAccountSettings');if(settings)settings.click();else document.getElementById('settingsButton')?.click()})}const id=identity();button.replaceChildren();if(id.picture){const img=document.createElement('img');img.src=id.picture;img.alt='';img.referrerPolicy='no-referrer';img.addEventListener('error',()=>{img.remove();const fallback=document.createElement('span');fallback.textContent=(id.name||'U').slice(0,1).toUpperCase();button.appendChild(fallback)},{once:true});button.appendChild(img)}else{const fallback=document.createElement('span');fallback.textContent=(id.name||'U').slice(0,1).toUpperCase();button.appendChild(fallback)}button.title=id.email||id.name||'Account'}
function patchSettings(root=document){const modal=root.querySelector?.('.swrlz-account-modal')||(root.matches?.('.swrlz-account-modal')?root:null);if(!modal)return;const detail=modal.querySelector('[data-detail]');if(!detail)return;if(!detail.querySelector('.swrlz-account-identity'))detail.prepend(makeIdentityCard());
  const display=detail.querySelector('[data-pref="displayName"]');if(display){const label=display.closest('label');if(label){for(const n of [...label.childNodes])if(n.nodeType===Node.TEXT_NODE&&n.textContent.trim())n.textContent='Chat name';display.placeholder='Name shown beside your messages'}}
  detail.querySelector('[data-pref="preferredName"]')?.closest('label')?.remove();
  const disabled=[...detail.querySelectorAll('input:disabled')];if(disabled.length>1){const googleNameField=disabled.find(x=>String(x.value||'')!==identity().email);googleNameField?.closest('label')?.remove()}
  const h3=detail.querySelector('h3');if(h3?.textContent==='Personalization'&&!detail.querySelector('[data-pref="displayName"]')){const existing=detail.querySelector('.swrlz-setting-grid');if(existing){const label=document.createElement('label');label.textContent='Chat name';const input=document.createElement('input');input.dataset.pref='displayName';input.value=prefs().displayName||'';input.placeholder='Name shown beside your messages';label.appendChild(input);existing.appendChild(label)}}
}
function observeSettings(){const obs=new MutationObserver(records=>{for(const r of records){for(const n of r.addedNodes){if(n.nodeType===1){if(n.matches?.('.swrlz-account-modal'))setTimeout(()=>patchSettings(n),0);else if(n.querySelector?.('.swrlz-account-modal'))setTimeout(()=>patchSettings(n),0)}}}const modal=document.querySelector('.swrlz-account-modal');if(modal)setTimeout(()=>patchSettings(modal),0)});obs.observe(document.documentElement,{childList:true,subtree:true})}
function refresh(){installRenderer();renderTopAccount();try{window.render?.(false)}catch(_){}const modal=document.querySelector('.swrlz-account-modal');if(modal)patchSettings(modal)}
function boot(){installChatFrame();installRenderer();renderTopAccount();observeSettings();window.addEventListener('swrlz:account-change',refresh);window.addEventListener('storage',e=>{if(String(e.key||'').startsWith('swrlzAccountPrefs'))refresh()});document.addEventListener('click',e=>{if(e.target.closest?.('#swrlzAccountSettings,[data-setting]'))setTimeout(()=>patchSettings(document),0)});setTimeout(refresh,0)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
