(()=>{"use strict";
const CHAT_TOKEN_KEY="swrlz.vercel.chat.token.v1";
const LEGACY_SESSION_KEY="swrlz.vercel.chat.admin-session.v1";
const SESSION_MARKER="__SERVER_MANAGED_CHAT_SESSION__";

/*
 * Server-managed Chat auth shim. This file must not own or repaint the Chat UI
 * version; the hot Chat enhancement asset is the single authoritative version
 * painter. Keep the base UI's historical token() guard satisfied with a
 * non-secret marker without exposing SWRLZ_WEB_CHAT_TOKEN to browser storage.
 */
sessionStorage.setItem(CHAT_TOKEN_KEY,SESSION_MARKER);
sessionStorage.removeItem(LEGACY_SESSION_KEY);

function paint(){
  const dialog=document.querySelector('#settingsDialog');
  const title=dialog?.querySelector('.dialog-head h2');
  if(title) title.textContent='Chat settings';

  const credential=document.querySelector('#accessToken')?.closest('.field');
  if(credential) credential.style.display='none';

  const panel=document.querySelector('#runtimePanel');
  if(panel){
    panel.innerHTML=panel.innerHTML
      .replace(/Credential:\s*configured\s*·\s*Admin session not active/gi,'Authorization: server managed')
      .replace(/Credential:\s*configured\s*·\s*Admin session active/gi,'Authorization: server managed');
    panel.dataset.authorization='server-managed-cookie';
  }

  const detail=document.querySelector('#nodeDetail');
  if(detail&&detail.textContent.includes('Open bridge settings')) detail.textContent='Open Chat settings';
}

paint();
setInterval(paint,500);
})();
