(()=>{"use strict";
if(window.__swrlzChatTransportBoundaryV1)return;
const CONTRACT='mask-chat-transport-boundary-v1';
const CHAT_UI='/chat';
const CHAT_API='/api/chat';
const TOKEN_KEY='swrlz.vercel.chat.token.v1';
const SESSION_MARKER='__SERVER_MANAGED_CHAT_SESSION__';
const CHAT_ACTIONS=new Set(['status','stream','cancel','verify']);
const priorFetch=window.fetch.bind(window);

function ensureSessionMarker(){
  try{if(!sessionStorage.getItem(TOKEN_KEY))sessionStorage.setItem(TOKEN_KEY,SESSION_MARKER)}catch(_){ }
}

function rewriteTarget(input){
  try{
    const raw=input instanceof Request?input.url:String(input);
    const url=new URL(raw,location.href);
    if(url.origin!==location.origin)return input;
    const action=url.searchParams.get('action');
    if(url.pathname==='/'&&CHAT_ACTIONS.has(String(action||''))){
      url.pathname=CHAT_API;
      if(input instanceof Request)return new Request(url.toString(),input);
      return `${url.pathname}${url.search}${url.hash}`;
    }
    return input;
  }catch(_){return input}
}

window.fetch=function(input,init){
  return priorFetch(rewriteTarget(input),init);
};

function canonicalizeChatNavigation(event){
  const anchor=event.target?.closest?.('a[href]');
  if(!anchor)return;
  try{
    const url=new URL(anchor.href,location.href);
    if(url.origin!==location.origin||url.pathname!==CHAT_API||url.search||url.hash)return;
    event.preventDefault();
    location.assign(CHAT_UI);
  }catch(_){ }
}

document.addEventListener('click',canonicalizeChatNavigation,true);
ensureSessionMarker();

window.__swrlzChatTransportBoundaryV1={
  contract:CONTRACT,
  version:1,
  chatUi:CHAT_UI,
  chatApi:CHAT_API,
  policy:'mask-ui-never-owns-server-routing; chat UI is /chat; all chat control and stream actions terminate at /api/chat; browser auth remains server-managed'
};
})();
