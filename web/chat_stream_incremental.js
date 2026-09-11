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
  if(!message){flushSave();return baseSaveState()}
  pendingSave=true;
  if(!saveTimer)saveTimer=setTimeout(flushSave,700);
};
renderMessage=function(message){
  const article=baseRenderMessage(message);
  if(article)article.dataset.messageState=String(message?.state||'');
  return article;
};
function followEnabled(){return refs?.messages?.dataset?.streamFollow==='true'}
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
function phaseText(message){
  try{return typeof phaseLabel==='function'?phaseLabel(message?.meta?.phase||'CONNECTING'):'Preparing response'}catch(_){return 'Preparing response'}
}
function updateLiveActivity(article,message){
  const body=article?.querySelector('.message-body');
  if(!body)return;
  const trail=Array.isArray(message?.meta?.trail)?message.meta.trail:[];
  if(!trail.length)return;
  let details=body.querySelector(':scope > details.trace');
  if(!details){
    details=document.createElement('details');
    details.className='trace swrlz-live-trace';
    details.open=true;
    const summary=document.createElement('summary');
    const list=document.createElement('div');list.className='trace-list';
    details.append(summary,list);
    const actions=body.querySelector(':scope > .message-actions');
    if(actions)body.insertBefore(details,actions);else body.append(details);
  }
  details.open=true;
  const summary=details.querySelector('summary');
  if(summary)summary.textContent=`Activity log · ${phaseText(message)}`;
  const list=details.querySelector('.trace-list');
  if(list){
    const recent=trail.slice(-12);
    const signature=recent.map(x=>`${x.phase||''}\u0000${x.reason||''}`).join('\u0001');
    if(list.dataset.signature!==signature){
      list.dataset.signature=signature;
      const frag=document.createDocumentFragment();
      for(const step of recent){
        const item=document.createElement('div');item.className='trace-item';
        const label=typeof phaseLabel==='function'?phaseLabel(step.phase):String(step.phase||'Activity');
        item.textContent=step.reason?`${label} — ${step.reason}`:label;
        frag.append(item);
      }
      list.replaceChildren(frag);
    }
  }
}
function stableStreamText(article,message){
  if(!article||!message)return false;
  article.dataset.messageState=String(message.state||'streaming');
  const bubble=article.querySelector('.bubble');
  if(!bubble)return false;
  const next=String(message.text||'');
  if(next){
    let live=bubble.querySelector(':scope > .swrlz-live-stream-text');
    if(!live){live=document.createElement('div');live.className='swrlz-live-stream-text';bubble.replaceChildren(live)}
    if(live.textContent!==next)live.textContent=next;
  }else{
    let waiting=bubble.querySelector(':scope > .swrlz-live-status');
    if(!waiting){
      waiting=document.createElement('div');waiting.className='empty-response swrlz-live-status';
      const mark=document.createElement('span');mark.className='thinking-mark';
      const text=document.createElement('span');text.className='swrlz-live-status-text';
      waiting.append(mark,text);bubble.replaceChildren(waiting);
    }
    const text=waiting.querySelector('.swrlz-live-status-text');
    if(text)text.textContent=phaseText(message);
  }
  updateLiveActivity(article,message);
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
    const shouldScroll=pendingScroll;pendingScroll=false;
    const message=activeStreamMessage();
    const patched=message?patchActiveArticle(shouldScroll):false;
    if(!patched){lastRenderedHeight=null;render(false)}
  });
};
const style=document.createElement('style');
style.textContent=`
.swrlz-live-stream-text{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;min-height:1.4em;contain:content}
.swrlz-live-status{min-height:1.4em;color:var(--muted);display:flex;align-items:center;gap:9px}
.swrlz-live-trace{margin-top:8px}
.message[data-message-state="streaming"] .bubble{will-change:auto;backface-visibility:hidden;transform:translateZ(0)}
`;
document.head.append(style);
window.addEventListener('pagehide',flushSave);
window.addEventListener('beforeunload',flushSave);
})();
