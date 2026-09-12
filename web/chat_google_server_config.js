(()=>{"use strict";
if(window.__swrlzGoogleServerConfigBridgeInstalled)return;
window.__swrlzGoogleServerConfigBridgeInstalled=true;

const CLIENT_KEY='swrlzGoogleLoginTestClientId';
const RELOAD_KEY='swrlz.google.server-config-reload.v1';

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
  const state=host.querySelector('.swrlz-google-state');
  if(state){state.textContent=text;if(isError)state.classList.add('error');else state.classList.remove('error')}
}

async function syncGoogleClient(){
  try{
    const status=await accountStatus();
    const serverClientId=String(status.googleClientId||'').trim();
    if(!serverClientId){
      if(!localStorage.getItem(CLIENT_KEY))setStatusText('Google sign-in is not configured on the server.',true);
      window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:false,source:'server'}}));
      return;
    }
    const previous=String(localStorage.getItem(CLIENT_KEY)||'').trim();
    if(previous!==serverClientId){
      localStorage.setItem(CLIENT_KEY,serverClientId);
      if(!sessionStorage.getItem(RELOAD_KEY)){
        sessionStorage.setItem(RELOAD_KEY,'1');
        location.reload();
        return;
      }
    }
    sessionStorage.removeItem(RELOAD_KEY);
    window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:true,source:'server'}}));
  }catch(error){
    if(!localStorage.getItem(CLIENT_KEY))setStatusText('Google sign-in configuration could not be loaded from the server.',true);
    window.dispatchEvent(new CustomEvent('swrlz:google-config',{detail:{configured:false,source:'server',error:String(error?.message||error)}}));
  }
}

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',syncGoogleClient,{once:true});
else syncGoogleClient();
})();
