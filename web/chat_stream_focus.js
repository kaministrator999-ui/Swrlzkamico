(()=>{"use strict";
if(window.__swrlzStreamFollowInstalled)return;
window.__swrlzStreamFollowInstalled=true;
let viewportEventType='';
let viewportMessageId='';
let followLocked=true;
let lastTailHeight=null;
let programmaticUntil=0;
let lifecycleActive=false;
let lifecycleClearTimer=0;

function activeArticle(){
  const message=typeof activeMessage==='function'?activeMessage():null;
  if(!message)return null;
  return refs?.stack?.querySelector?.(`[data-message-id="${CSS.escape(message.id)}"]`)||null;
}

function tailArticle(){
  const activeNode=activeArticle();
  if(activeNode)return activeNode;
  if(!viewportMessageId||!refs?.stack)return null;
  return refs.stack.querySelector(`[data-message-id="${CSS.escape(viewportMessageId)}"]`)||null;
}

function setFollowLocked(next){
  followLocked=Boolean(next);
  if(refs?.messages){
    if(followLocked)refs.messages.dataset.streamFollow='true';
    else delete refs.messages.dataset.streamFollow;
  }
}

function newestLineInFollowBand(){
  const article=tailArticle();
  const bubble=article?.querySelector?.('.bubble');
  if(!bubble||!refs?.messages)return false;
  const viewport=refs.messages.getBoundingClientRect();
  const y=bubble.getBoundingClientRect().bottom;
  return y>=viewport.top+viewport.height*.34&&y<=viewport.top+viewport.height*.70;
}

function centerGeneratedLine(){
  if(!followLocked||!refs?.messages)return;
  const article=tailArticle();
  const bubble=article?.querySelector?.('.bubble');
  if(!bubble)return;
  const viewport=refs.messages.getBoundingClientRect();
  const rect=bubble.getBoundingClientRect();
  const target=viewport.top+(viewport.height*.52);
  const delta=rect.bottom-target;
  if(Math.abs(delta)<=1)return;
  programmaticUntil=performance.now()+90;
  refs.messages.scrollTop+=delta;
}

function renderedLineAdvanced(){
  if(viewportEventType==='RESET'){
    lastTailHeight=null;
    return false;
  }
  if(viewportEventType!=='DELTA')return false;
  const bubble=tailArticle()?.querySelector?.('.bubble');
  if(!bubble)return false;
  const height=Math.ceil(bubble.getBoundingClientRect().height);
  if(lastTailHeight==null){
    lastTailHeight=height;
    return false;
  }
  const style=getComputedStyle(bubble);
  const parsedLine=parseFloat(style.lineHeight);
  const fontSize=parseFloat(style.fontSize)||16;
  const lineHeight=Number.isFinite(parsedLine)?parsedLine:fontSize*1.5;
  const advanced=height-lastTailHeight>=Math.max(4,lineHeight*.45);
  if(advanced||height<lastTailHeight)lastTailHeight=height;
  return advanced;
}

function resetStreamFollow(){
  lastTailHeight=null;
  setFollowLocked(true);
  lifecycleActive=true;
  clearTimeout(lifecycleClearTimer);
}

function finishStreamFollowSoon(){
  clearTimeout(lifecycleClearTimer);
  lifecycleClearTimer=setTimeout(()=>{
    lifecycleActive=false;
    viewportEventType='';
    viewportMessageId='';
    lastTailHeight=null;
    if(refs?.messages)delete refs.messages.dataset.streamFollow;
  },180);
}

function installUserScrollIntent(){
  if(!refs?.messages||refs.messages.dataset.swrlzFollowBound==='true')return;
  refs.messages.dataset.swrlzFollowBound='true';
  const manual=()=>{if(lifecycleActive&&performance.now()>=programmaticUntil)setFollowLocked(false)};
  const reevaluate=()=>{
    if(!lifecycleActive||performance.now()<programmaticUntil||followLocked)return;
    if(newestLineInFollowBand())setFollowLocked(true);
  };
  refs.messages.addEventListener('scroll',reevaluate,{passive:true});
  refs.messages.addEventListener('wheel',manual,{passive:true});
  refs.messages.addEventListener('touchstart',manual,{passive:true});
  refs.messages.addEventListener('pointerdown',manual,{passive:true});
}

function clipText(text){
  const value=String(text??'');
  if(navigator.clipboard?.writeText)return navigator.clipboard.writeText(value);
  const box=document.createElement('textarea');box.value=value;box.style.position='fixed';box.style.opacity='0';document.body.appendChild(box);box.select();
  try{document.execCommand('copy')}finally{box.remove()}
  return Promise.resolve();
}

function cleanTraceText(trace){
  if(!trace)return '';
  const clone=trace.cloneNode(true);
  clone.querySelectorAll('.swrlz-log-tools').forEach(node=>node.remove());
  return String(clone.innerText||clone.textContent||'').trim();
}

function messageLogText(message,article){
  const bubble=article?.querySelector?.('.bubble');
  const trace=article?.querySelector?.('.trace');
  const lines=[
    '§wyrlz Message Activity Log',
    `captured=${new Date().toISOString()}`,
    `messageId=${message?.id||'—'}`,
    `role=${message?.role||'—'}`,
    '',
    '=== RESPONSE ===',
    String(bubble?.innerText||bubble?.textContent||message?.text||message?.content||'').trim(),
    '',
    '=== ACTIVITY / GENERATION TRACE ===',
    cleanTraceText(trace)||'No rendered activity trace.',
    '',
    '=== RAW MESSAGE STATE ===',
    JSON.stringify(message??{},null,2)
  ];
  return lines.join('\n');
}

function fullThreadLogText(){
  const t=currentThread?.();
  const receipt=typeof effectiveServerReceipt==='function'?effectiveServerReceipt():{};
  const messages=Array.isArray(t?.messages)?t.messages:[];
  const blocks=messages.map((message,index)=>{
    const article=refs?.stack?.querySelector?.(`[data-message-id="${CSS.escape(String(message?.id||''))}"]`)||null;
    return [`\n===== MESSAGE ${index+1}/${messages.length} =====`,messageLogText(message,article)].join('\n');
  });
  let streamCamera='';
  try{streamCamera=typeof cameraText==='function'?cameraText(true):''}catch(_){streamCamera=''}
  return [
    '§wyrlz Full Conversation + Generation Log',
    `exported=${new Date().toISOString()}`,
    `threadId=${t?.id||'—'}`,
    `threadTitle=${t?.title||'—'}`,
    `baseVersion=${receipt?.base||'—'}`,
    `hotServerVersion=${receipt?.effective||'—'}`,
    `hotRevision=${receipt?.hot||'—'}`,
    `messageCount=${messages.length}`,
    `cameraEventCount=${Array.isArray(window.camera)?window.camera.length:(typeof camera!=='undefined'&&Array.isArray(camera)?camera.length:'—')}`,
    ...blocks,
    '\n===== FULL STREAM CAMERA / RESPONSE-GENERATION EVENTS =====',
    streamCamera||'No camera events captured in this browser session.',
    '\n===== RAW THREAD STATE =====',
    JSON.stringify(t??{},null,2),
    ''
  ].join('\n');
}

function downloadText(filename,text){
  const blob=new Blob([String(text??'')],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
}

function openLogCamera(message,article){
  document.querySelector('#swrlzLogCameraModal')?.remove();
  const modal=document.createElement('div');modal.id='swrlzLogCameraModal';modal.className='swrlz-log-camera-modal';
  const panel=document.createElement('div');panel.className='swrlz-log-camera-panel';
  const head=document.createElement('div');head.className='swrlz-log-camera-head';
  const title=document.createElement('strong');title.textContent='📷 Activity Log Camera';
  const actions=document.createElement('div');actions.className='swrlz-log-camera-actions';
  const copy=document.createElement('button');copy.type='button';copy.textContent='Copy box';
  const exportAll=document.createElement('button');exportAll.type='button';exportAll.textContent='Export full log';
  const close=document.createElement('button');close.type='button';close.textContent='Close';
  const pre=document.createElement('pre');pre.textContent=messageLogText(message,article);
  copy.onclick=async()=>{await clipText(pre.textContent||'');toast?.('Copied activity log box')};
  exportAll.onclick=()=>{const t=currentThread?.(),stamp=new Date().toISOString().replace(/[:.]/g,'-');downloadText(`swrlz-full-log-${typeof safeFilePart==='function'?safeFilePart(t?.id):'thread'}-${stamp}.log.txt`,fullThreadLogText());toast?.('Exported full conversation + generation log')};
  close.onclick=()=>modal.remove();
  modal.addEventListener('click',event=>{if(event.target===modal)modal.remove()});
  actions.append(copy,exportAll,close);head.append(title,actions);panel.append(head,pre);modal.append(panel);document.body.append(modal);
}

function installLogTools(message,article,trace){
  if(!trace||trace.querySelector('.swrlz-log-tools'))return;
  const tools=document.createElement('span');tools.className='swrlz-log-tools';
  const cameraButton=document.createElement('button');cameraButton.type='button';cameraButton.className='swrlz-log-tool';cameraButton.title='Open full activity log camera';cameraButton.setAttribute('aria-label','Open full activity log camera');cameraButton.textContent='📷';
  const copyButton=document.createElement('button');copyButton.type='button';copyButton.className='swrlz-log-tool';copyButton.title='Copy this activity log box';copyButton.textContent='Copy';
  const exportButton=document.createElement('button');exportButton.type='button';exportButton.className='swrlz-log-tool';exportButton.title='Export full conversation and response-generation log';exportButton.textContent='Export full log';
  [cameraButton,copyButton,exportButton].forEach(button=>button.addEventListener('click',event=>{event.preventDefault();event.stopPropagation()}));
  cameraButton.addEventListener('click',()=>openLogCamera(message,article));
  copyButton.addEventListener('click',async()=>{await clipText(messageLogText(message,article));toast?.('Copied activity log box')});
  exportButton.addEventListener('click',()=>{const t=currentThread?.(),stamp=new Date().toISOString().replace(/[:.]/g,'-');downloadText(`swrlz-full-log-${typeof safeFilePart==='function'?safeFilePart(t?.id):'thread'}-${stamp}.log.txt`,fullThreadLogText());toast?.('Exported full conversation + generation log')});
  tools.append(cameraButton,copyButton,exportButton);
  const summary=trace.querySelector('summary');
  if(summary)summary.appendChild(tools);else trace.prepend(tools);
}

const focusBaseRender=render;
render=function(scroll=false){
  const suppressForcedScroll=Boolean(scroll&&lifecycleActive&&!followLocked);
  return focusBaseRender(suppressForcedScroll?false:scroll);
};

scheduleRender=function(scroll=false){
  if(renderQueued)return;
  renderQueued=true;
  requestAnimationFrame(()=>{
    renderQueued=false;
    render(false);
    if(scroll&&renderedLineAdvanced())requestAnimationFrame(centerGeneratedLine);
  });
};

const focusBaseRenderMessage=renderMessage;
renderMessage=function(message){
  const article=focusBaseRenderMessage(message);
  if(message?.role!=='assistant')return article;
  message.meta=message.meta||{};
  const body=article.querySelector('.message-body'),bubble=article.querySelector('.bubble'),trace=article.querySelector('.trace');
  if(trace&&body&&bubble){
    trace.open=Boolean(message.meta.activityExpanded);
    const summary=trace.querySelector('summary');
    if(summary&&!String(summary.childNodes?.[0]?.textContent||summary.textContent||'').startsWith('Activity log')){
      const first=summary.childNodes?.[0];
      if(first&&first.nodeType===Node.TEXT_NODE)first.textContent=`Activity log · ${first.textContent||'runtime'}`;
    }
    installLogTools(message,article,trace);
    trace.addEventListener('toggle',()=>{
      message.meta.activityExpanded=trace.open;
      saveState();
    });
    body.insertBefore(trace,bubble);
  }
  if(body&&bubble){
    const actions=body.querySelector('.message-actions');
    const evidence=body.querySelector('.swrlz-evidence');
    if(actions)body.insertBefore(actions,bubble);
    if(evidence)body.insertBefore(evidence,bubble);
  }
  return article;
};

const focusBaseConsume=consumeEvent;
consumeEvent=function(event,context){
  const nextType=String(event?.type||'');
  const nextMessageId=String(context?.message?.id||'');
  const starting=!lifecycleActive||viewportMessageId!==nextMessageId;
  viewportEventType=nextType;
  viewportMessageId=nextMessageId;
  if(starting)resetStreamFollow();
  const result=focusBaseConsume(event,context);
  if(['COMPLETED','CANCELLED','FAILED'].includes(nextType))finishStreamFollowSoon();
  return result;
};

exportCameraLog=function(){
  const t=currentThread(),receipt=effectiveServerReceipt(),stamp=new Date().toISOString().replace(/[:.]/g,'-');
  const header=[`§wyrlz Stream Camera Export`,`exported=${new Date().toISOString()}`,`threadId=${t?.id||'—'}`,`threadTitle=${t?.title||'—'}`,`baseVersion=${receipt.base}`,`hotServerVersion=${receipt.effective||'—'}`,`hotRevision=${receipt.hot||'—'}`,`eventCount=${camera.length}`,''].join('\n');
  const blob=new Blob([header+cameraText(true)+'\n'],{type:'text/plain;charset=utf-8'}),u=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=u;a.download=`swrlz-camera-${safeFilePart(t?.id)}-${stamp}.log.txt`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500);toast(`Exported ${camera.length} camera event${camera.length===1?'':'s'} to device`);
};

const style=document.createElement('style');
style.textContent=`
.message.assistant .trace{order:initial}
.message.assistant .trace summary{user-select:none;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.message.assistant .trace:not([open]) .trace-list{display:none}
.message.assistant[data-stream-tail="true"] .bubble{scroll-margin-bottom:12px}
.messages[data-stream-follow="true"]{scroll-behavior:auto!important;overflow-anchor:none!important}
.swrlz-log-tools{display:inline-flex;gap:5px;align-items:center;margin-left:auto}
.swrlz-log-tool{border:1px solid var(--line);background:rgba(13,23,42,.88);color:var(--secondary);border-radius:8px;padding:4px 7px;font-size:10px;line-height:1.2;cursor:pointer}
.swrlz-log-tool:hover{border-color:var(--line-strong);color:var(--text)}
.swrlz-log-camera-modal{position:fixed;inset:0;z-index:120;background:rgba(0,0,0,.72);display:grid;place-items:center;padding:14px}
.swrlz-log-camera-panel{width:min(900px,100%);max-height:90dvh;display:grid;grid-template-rows:auto minmax(0,1fr);border:1px solid var(--line-strong);border-radius:18px;background:#07101d;box-shadow:var(--shadow);overflow:hidden}
.swrlz-log-camera-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 14px;border-bottom:1px solid var(--line)}
.swrlz-log-camera-actions{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.swrlz-log-camera-actions button{border:1px solid var(--line);background:rgba(13,23,42,.92);color:var(--secondary);border-radius:9px;padding:7px 9px;cursor:pointer;font-size:11px}
.swrlz-log-camera-panel pre{margin:0;padding:14px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--secondary);font:11px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;background:#040914}
@media(max-width:600px){.swrlz-log-tools{width:100%;margin-left:0}.swrlz-log-tool{flex:1}.swrlz-log-camera-head{align-items:flex-start;flex-direction:column}.swrlz-log-camera-actions{width:100%}.swrlz-log-camera-actions button{flex:1}}
`;
document.head.append(style);
installUserScrollIntent();
render(false);
})();
