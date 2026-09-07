(()=>{"use strict";
const UI_VERSION="1.3.12";
const CHAT_TOKEN_KEY="swrlz.vercel.chat.token.v1";
const LEGACY_SESSION_KEY="swrlz.vercel.chat.admin-session.v1";
const SESSION_MARKER="__SERVER_MANAGED_CHAT_SESSION__";

/*
 * Server 2.1.15 issues an HttpOnly, SameSite=Strict cookie when /api/chat loads.
 * Keep the base UI's historical token() guard satisfied with a non-secret marker,
 * but never copy SWRLZ_WEB_CHAT_TOKEN into browser storage or request headers.
 */
sessionStorage.setItem(CHAT_TOKEN_KEY,SESSION_MARKER);
sessionStorage.removeItem(LEGACY_SESSION_KEY);

function paint(){
  const dialog=document.querySelector('#settingsDialog');
  const title=dialog?.querySelector('.dialog-head h2');
  if(title) title.textContent='Chat settings';

  const credential=document.querySelector('#accessToken')?.closest('.field');
  if(credential) credential.style.display='none';

  const legacy=document.querySelector('#swrlzVersionLine');
  if(legacy) legacy.style.display='none';
  const hot=document.querySelector('#swrlzHotVersionLine');
  if(hot){
    const current=hot.textContent||'';
    const server=(current.match(/SERVER v([^·\s]+)/)||[])[1]||'…';
    hot.textContent=`CHAT v${UI_VERSION} · SERVER v${server}`;
    hot.dataset.auth='server-managed-cookie';
  }

  const detail=document.querySelector('#nodeDetail');
  if(detail&&detail.textContent.includes('Open bridge settings')) detail.textContent='Open Chat settings';
}

paint();
setInterval(paint,500);
})();
