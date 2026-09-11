(()=>{"use strict";
if(window.__swrlzIncrementalStreamRenderInstalled)return;
window.__swrlzIncrementalStreamRenderInstalled=true;

const baseRenderMessage=renderMessage;
const baseSaveState=saveState;
let pendingSave=false;
let saveTimer=0;
let lastRenderedHeight=null;

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
  if(!saveTimer)saveTimer=setTimeout(flushSave,220);
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

function patchActiveArticle(scroll){
  const message=activeStreamMessage();
  const existing=activeArticle(message);
  if(!message||!existing)return false;
  const replacement=renderMessage(message);
  if(!replacement)return false;
  existing.replaceWith(replacement);
  if(scroll)requestAnimationFrame(()=>centerTailLine(replacement));
  return true;
}

scheduleRender=function(scroll=false){
  if(renderQueued)return;
  renderQueued=true;
  requestAnimationFrame(()=>{
    renderQueued=false;
    const message=activeStreamMessage();
    const patched=message?patchActiveArticle(scroll):false;
    if(!patched){
      lastRenderedHeight=null;
      render(false);
    }
  });
};

window.addEventListener('pagehide',flushSave);
window.addEventListener('beforeunload',flushSave);
})();
