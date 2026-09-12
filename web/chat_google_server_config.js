(()=>{"use strict";
if(window.__swrlzGoogleServerConfigBridgeInstalled)return;
window.__swrlzGoogleServerConfigBridgeInstalled=true;

const CLIENT_KEY='swrlzGoogleLoginTestClientId';
const RELOAD_KEY='swrlz.google.server-config-reload.v1';
const GIS_SRC='https://accounts.google.com/gsi/client';

async function accountStatus(){
  const urls=['/api/account/status','/live/api/account/status'];
  let lastError=null;
  for(const url of urls){
    try{
      const response=await fetch(url,{cache:'no-store',credentials:'same-origin'});
      if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const body=await response.json();
      if(body&&body.ok)return body;
    }catch(error){lastError=error}
  }
  throw lastError||new Error('Account status unavailable');
}

function setStatusText(text,isError=false){
  const host=document.querySelector('.swrlz-google-host');
  if(!host)return;
  let state=host.querySelector('.swrlz-google-state');
  if(!state){state=document.createElement('div');state.className='swrlz-google-state';host.replaceChildren(state)}
  state.textContent=text;if(isError)state.classList.add('error');else state.classList.remove('error');
}

async function verifyCredential(credential){
  const response=await fetch('/api/account/google',{
    method:'POST',
    credentials:'same-origin',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({credential:String(credential||'')})
  });
  const body=await response.json().catch(()=>({}));
  if(!response.ok||!body?.ok)throw new Error(body?.detail||`Google verification failed (HTTP ${response.status})`);
  return body;
}

function patchGoogleIdentity(){
  const id=window.google?.accounts?.id;
  if(!id||id.__swrlzServerVerifiedInitialize)return false;
  const original=id.initialize?.bind(id);
  if(typeof original!=='function')return false;
  const wrapped=function(options){
    const callback=options?.callback;
    if(typeof callback!=='function')return original(options);
    return original({...options,callback:async response=>{
      try{
        const verified=await verifyCredential(response?.credential);
        window.__swrlzGoogleServerSession=verified;
        window.dispatchEvent(new CustomEvent('swrlz:google-server-session',{detail:{ok:true,durable:Boolean(verified?.durable)}}));
        callback(response);
      }catch(error){
        setStatusText('Google sign-in was rejected by the server.',true);
        window.dispatchEvent(new CustomEvent('swrlz:google-server-session',{detail:{ok:false,error:String(error?.message||error)}}));
      }
    }});
  };
  wrapped.__swrlzServerVerifiedInitialize=true;
  id.initialize=wrapped;
  id.__swrlzServerVerifiedInitialize=true;
  return true;
}

function watchGoogleIdentity(){
  if(patchGoogleIdentity())return;
  const script=[...document.scripts].find(s=>String(s.src||'').startsWith(GIS_SRC));
  if(script)script.addEventListener('load',()=>queueMicrotask(patchGoogleIdentity),{once:true});
  const observer=new MutationObserver(()=>{if(patchGoogleIdentity())observer.disconnect()});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  setTimeout(()=>observer.disconnect(),15000);
}

async function syncGoogleClient(){
  try{
    const status=await accountStatus();
    const serverClientId=String(status.googleClientId||'').trim();
    const browserClientId=String(localStorage.getItem(CLIENT_KEY)||'').trim();

    // Browser-proven OAuth configuration outranks the server fallback. The fallback
    // exists only to seed fresh browsers; it must never overwrite a client ID that
    // has already been configured and proven on this origin.
    if(browserClientId){
      sessionStorage.removeItem(RELOAD_KEY);
      window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{
        configured:true,
        source:'browser',
        serverFallbackAvailable:Boolean(serverClientId),
        authConfigured:Boolean(status.authConfigured),
        storeConfigured:Boolean(status.storeConfigured)
      }}));
      return;
    }

    if(!serverClientId){
      setStatusText('Google sign-in is not configured on the server.',true);
      window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:false,source:'server'}}));
      return;
    }

    localStorage.setItem(CLIENT_KEY,serverClientId);
    if(!sessionStorage.getItem(RELOAD_KEY)){
      sessionStorage.setItem(RELOAD_KEY,'1');
      location.reload();
      return;
    }
    sessionStorage.removeItem(RELOAD_KEY);
    window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:true,source:'server-seed',authConfigured:Boolean(status.authConfigured),storeConfigured:Boolean(status.storeConfigured)}}));
  }catch(error){
    if(!localStorage.getItem(CLIENT_KEY))setStatusText('Google sign-in configuration could not be loaded from the server.',true);
    window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:Boolean(localStorage.getItem(CLIENT_KEY)),source:localStorage.getItem(CLIENT_KEY)?'browser':'server',error:String(error?.message||error)}}));
  }
}

window.addEventListener('swrlz:account-change',event=>{
  if(event?.detail?.signedIn===false)fetch('/api/account/logout',{method:'POST',credentials:'same-origin'}).catch(()=>{});
});
window.__swrlzGoogleServerAuth={accountStatus,verifyCredential,patchGoogleIdentity};
watchGoogleIdentity();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',syncGoogleClient,{once:true});
else syncGoogleClient();
})();
