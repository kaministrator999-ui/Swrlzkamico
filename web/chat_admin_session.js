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

function copyText(text){
  const value=String(text??'');
  if(navigator.clipboard?.writeText)return navigator.clipboard.writeText(value);
  const box=document.createElement('textarea');box.value=value;box.style.position='fixed';box.style.opacity='0';document.body.appendChild(box);box.select();
  try{document.execCommand('copy')}finally{box.remove()}
  return Promise.resolve();
}

function traceTextFor(message){
  if(!message?.id)return '';
  try{
    const article=document.querySelector(`[data-message-id="${CSS.escape(String(message.id))}"]`);
    const trace=article?.querySelector?.('.trace');
    if(!trace)return '';
    const clone=trace.cloneNode(true);
    clone.querySelectorAll('.swrlz-log-tools').forEach(node=>node.remove());
    return String(clone.innerText||clone.textContent||'').trim();
  }catch(_){return ''}
}

function conversationCameraText(){
  const thread=typeof currentThread==='function'?currentThread():null;
  const messages=Array.isArray(thread?.messages)?thread.messages:[];
  const blocks=messages.map((message,index)=>{
    const text=String(message?.text||message?.content||'').trim();
    const trace=message?.role==='assistant'?traceTextFor(message):'';
    const trail=Array.isArray(message?.meta?.trail)?message.meta.trail:[];
    return [
      `===== MESSAGE ${index+1}/${messages.length} =====`,
      `messageId=${message?.id||'—'}`,
      `role=${message?.role||'—'}`,
      `state=${message?.state||'—'}`,
      `createdAt=${message?.createdAt?new Date(message.createdAt).toISOString():'—'}`,
      '',
      '=== MESSAGE TEXT ===',
      text||'(empty)',
      ...(message?.role==='assistant'?['','=== RESPONSE GENERATION / ACTIVITY ===',trace||trail.map(step=>step?.reason?`${step.phase||'STATE'} — ${step.reason}`:(step?.phase||'STATE')).join('\n')||'No activity trace stored.']:[]),
      '',
      '=== RAW MESSAGE STATE ===',
      JSON.stringify(message??{},null,2),
      ''
    ].join('\n');
  });
  return [
    '§wyrlz Whole Conversation Camera Log',
    `captured=${new Date().toISOString()}`,
    `threadId=${thread?.id||'—'}`,
    `threadTitle=${thread?.title||'—'}`,
    `messageCount=${messages.length}`,
    '',
    ...blocks,
    '===== RAW THREAD STATE =====',
    JSON.stringify(thread??{},null,2),
    ''
  ].join('\n');
}

function downloadConversationLog(){
  const thread=typeof currentThread==='function'?currentThread():null;
  const safe=String(thread?.title||'conversation').replace(/[^a-z0-9._-]+/gi,'-').replace(/^-|-$/g,'').slice(0,70)||'conversation';
  const stamp=new Date().toISOString().replace(/[:.]/g,'-');
  const blob=new Blob([conversationCameraText()],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=`${safe}-camera-${stamp}.log.txt`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
}

function openConversationCamera(){
  document.querySelector('#swrlzConversationCameraModal')?.remove();
  const modal=document.createElement('div');modal.id='swrlzConversationCameraModal';modal.className='swrlz-whole-camera-modal';
  const panel=document.createElement('div');panel.className='swrlz-whole-camera-panel';
  const head=document.createElement('div');head.className='swrlz-whole-camera-head';
  const title=document.createElement('strong');title.textContent='📷 Whole Conversation Camera';
  const actions=document.createElement('div');actions.className='swrlz-whole-camera-actions';
  const copy=document.createElement('button');copy.type='button';copy.textContent='Copy whole log';
  const refresh=document.createElement('button');refresh.type='button';refresh.textContent='Refresh';
  const exportAll=document.createElement('button');exportAll.type='button';exportAll.textContent='Export full log';
  const close=document.createElement('button');close.type='button';close.textContent='Close';
  const pre=document.createElement('pre');
  const update=()=>{pre.textContent=conversationCameraText()};update();
  copy.onclick=async()=>{await copyText(pre.textContent||'');if(typeof toast==='function')toast('Copied whole conversation camera log')};
  refresh.onclick=()=>{update();if(typeof toast==='function')toast('Conversation camera refreshed')};
  exportAll.onclick=()=>{downloadConversationLog();if(typeof toast==='function')toast('Exported whole conversation camera log')};
  close.onclick=()=>modal.remove();
  modal.addEventListener('click',event=>{if(event.target===modal)modal.remove()});
  actions.append(copy,refresh,exportAll,close);head.append(title,actions);panel.append(head,pre);modal.append(panel);document.body.append(modal);
}

function installConversationCamera(){
  if(document.querySelector('#swrlzConversationCamera'))return;
  const host=document.querySelector('.topbar-right');if(!host)return;
  const button=document.createElement('button');button.id='swrlzConversationCamera';button.type='button';button.className='icon-button swrlz-conversation-camera';button.title='Open whole conversation camera log';button.setAttribute('aria-label','Open whole conversation camera log');button.textContent='📷';
  button.addEventListener('click',openConversationCamera);
  const exportButton=host.querySelector('#exportChat');host.insertBefore(button,exportButton||host.querySelector('#settingsButton')||null);
  if(!document.querySelector('#swrlzWholeCameraStyle')){
    const style=document.createElement('style');style.id='swrlzWholeCameraStyle';style.textContent=`
.swrlz-conversation-camera{font-size:17px;line-height:1}
.swrlz-whole-camera-modal{position:fixed;inset:0;z-index:130;background:rgba(0,0,0,.74);display:grid;place-items:center;padding:14px}
.swrlz-whole-camera-panel{width:min(940px,100%);max-height:90dvh;display:grid;grid-template-rows:auto minmax(0,1fr);border:1px solid var(--line-strong);border-radius:18px;background:#07101d;box-shadow:var(--shadow);overflow:hidden}
.swrlz-whole-camera-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line)}
.swrlz-whole-camera-actions{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.swrlz-whole-camera-actions button{border:1px solid var(--line);background:rgba(13,23,42,.92);color:var(--secondary);border-radius:9px;padding:7px 9px;cursor:pointer;font-size:11px}
.swrlz-whole-camera-panel pre{margin:0;padding:14px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--secondary);font:11px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;background:#040914}
@media(max-width:600px){.swrlz-whole-camera-head{align-items:flex-start;flex-direction:column}.swrlz-whole-camera-actions{width:100%}.swrlz-whole-camera-actions button{flex:1}}
`;
    document.head.appendChild(style);
  }
}

window.swrlzOpenConversationCamera=openConversationCamera;
paint();
installConversationCamera();
setInterval(()=>{paint();installConversationCamera()},500);
})();
