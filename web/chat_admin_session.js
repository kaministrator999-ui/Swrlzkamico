(()=>{"use strict";
const CHAT_TOKEN_KEY="swrlz.vercel.chat.token.v1";
const LEGACY_SESSION_KEY="swrlz.vercel.chat.admin-session.v1";
const SESSION_MARKER="__SERVER_MANAGED_CHAT_SESSION__";

/*
 * Server 2.1.15+ issues an HttpOnly, SameSite=Strict cookie when /api/chat loads.
 * Keep the base UI's historical token() guard satisfied with a non-secret marker,
 * but never copy SWRLZ_WEB_CHAT_TOKEN into browser storage or request headers.
 *
 * Version ownership deliberately stays with the hot Chat enhancement asset.
 * This auth shim must never repaint or downgrade the visible Chat version receipt.
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

  const legacy=document.querySelector('#swrlzVersionLine');
  if(legacy) legacy.style.display='none';
  const hot=document.querySelector('#swrlzHotVersionLine');
  if(hot) hot.dataset.auth='server-managed-cookie';

  const detail=document.querySelector('#nodeDetail');
  if(detail&&detail.textContent.includes('Open bridge settings')) detail.textContent='Open Chat settings';
}

paint();
setInterval(paint,500);
})();
