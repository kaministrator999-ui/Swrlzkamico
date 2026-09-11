(()=>{"use strict";
if(window.__swrlzIncrementalStreamRenderInstalled)return;
window.__swrlzIncrementalStreamRenderInstalled=true;

const baseRenderMessage=renderMessage;
const baseSaveState=saveState;
let pendingSave=false;
let saveTimer=0;
let lastRenderedHeight=null;
let pendingScroll=false;

function activeStreamMessage(){
  try{return typeof activeMessage==='function'?activeMessage():null}catch(_){return null}
}

function activeArticle(message){
  if(!message||!refs?.stack)return null;
  try{return refs.stack.querySelector(`[data-message-id="${CSS.escape(String(message.id||''))}"]`)}catch(_){return null}
}

function flushSave(){
  if(saveTimer){clearTimeout(saveTimer);saveTimer=0}
  if(!pendingSave)return;
  pendingSave=false;
  try{baseSaveState()}catch(_){}
}

saveState=function(){
  const message=activeStreamMessage();
  if(!message){
    flushSave();
    return baseSaveState();
  }
  pendingSave=true;
  if(!saveTimer)saveTimer=setTimeout(flushSave,700);
};

renderMessage=function(message){
  const article=baseRenderMessage(message);
  if(article)article.dataset.messageState=String(message?.state||'');
  return article;
};

function followEnabled(){
  return refs?.messages?.dataset?.streamFollow==='true';
}

function centerTailLine(article){
  if(!followEnabled()||!refs?.messages||!article)return;
  const bubble=article.querySelector('.bubble');
  if(!bubble)return;
  const viewport=refs.messages.getBoundingClientRect();
  const rect=bubble.getBoundingClientRect();
  const height=Math.ceil(rect.height);
  const style=getComputedStyle(bubble);
  const line=parseFloat(style.lineHeight);
  const font=parseFloat(style.fontSize)||16;
  const lineHeight=Number.isFinite(line)?line:font*1.5;
  const lineAdvanced=lastRenderedHeight==null||Math.abs(height-lastRenderedHeight)>=Math.max(4,lineHeight*.45);
  if(!lineAdvanced)return;
  lastRenderedHeight=height;
  const target=viewport.top+viewport.height*.52;
  const delta=rect.bottom-target;
  if(Math.abs(delta)>1)refs.messages.scrollTop+=delta;
}

function stableStreamText(article,message){
  if(!article||!message)return false;
  article.dataset.messageState=String(message.state||'streaming');
  const bubble=article.querySelector('.bubble');
  if(!bubble)return false;
  let live=bubble.querySelector(':scope > .swrlz-live-stream-text');
  if(!live){
    live=document.createElement('div');
    live.className='swrlz-live-stream-text';
    bubble.replaceChildren(live);
  }
  const next=String(message.text||'');
  if(live.textContent!==next)live.textContent=next;
  const summary=article.querySelector('.trace summary');
  if(summary){
    const label=typeof phaseLabel==='function'?phaseLabel(message.meta?.phase||'GENERATING'):'Generating response';
    const first=summary.childNodes?.[0];
    if(first&&first.nodeType===Node.TEXT_NODE)first.textContent=`Activity log · ${label}`;
  }
  return true;
}

function finalizeArticle(article,message){
  if(!article||!message)return false;
  const replacement=renderMessage(message);
  if(!replacement)return false;
  article.replaceWith(replacement);
  lastRenderedHeight=null;
  flushSave();
  return true;
}

function patchActiveArticle(scroll){
  const message=activeStreamMessage();
  const article=activeArticle(message);
  if(!message||!article)return false;
  const streaming=message.state==='streaming'||message.state==='cancelling';
  const patched=streaming?stableStreamText(article,message):finalizeArticle(article,message);
  if(patched&&scroll&&streaming)requestAnimationFrame(()=>centerTailLine(article));
  return patched;
}

scheduleRender=function(scroll=false){
  pendingScroll=pendingScroll||Boolean(scroll);
  if(renderQueued)return;
  renderQueued=true;
  requestAnimationFrame(()=>{
    renderQueued=false;
    const shouldScroll=pendingScroll;
    pendingScroll=false;
    const message=activeStreamMessage();
    const patched=message?patchActiveArticle(shouldScroll):false;
    if(!patched){
      lastRenderedHeight=null;
      render(false);
    }
  });
};

const style=document.createElement('style');
style.textContent=`
.swrlz-live-stream-text{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;min-height:1.4em;contain:content}
.message[data-message-state="streaming"] .bubble{will-change:auto;backface-visibility:hidden;transform:translateZ(0)}
`;
document.head.append(style);

window.addEventListener('pagehide',flushSave);
window.addEventListener('beforeunload',flushSave);
})();
