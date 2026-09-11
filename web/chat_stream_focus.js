(()=>{"use strict";
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

function newestLineVisible(){
  const article=tailArticle();
  const bubble=article?.querySelector?.('.bubble');
  if(!bubble||!refs?.messages)return false;
  const viewport=refs.messages.getBoundingClientRect();
  const rect=bubble.getBoundingClientRect();
  const y=rect.bottom;
  return y>=viewport.top+12&&y<=viewport.bottom-12;
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
  const reevaluate=()=>{
    if(!lifecycleActive||performance.now()<programmaticUntil)return;
    setFollowLocked(newestLineVisible());
  };
  refs.messages.addEventListener('scroll',reevaluate,{passive:true});
  refs.messages.addEventListener('wheel',()=>{if(lifecycleActive&&performance.now()>=programmaticUntil)setFollowLocked(false)},{passive:true});
  refs.messages.addEventListener('touchstart',()=>{if(lifecycleActive&&performance.now()>=programmaticUntil)setFollowLocked(false)},{passive:true});
  refs.messages.addEventListener('pointerdown',()=>{if(lifecycleActive&&performance.now()>=programmaticUntil)setFollowLocked(false)},{passive:true});
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
    if(summary&&!String(summary.textContent||'').startsWith('Activity log'))summary.textContent=`Activity log · ${summary.textContent||'runtime'}`;
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
.message.assistant .trace summary{user-select:none}
.message.assistant .trace:not([open]) .trace-list{display:none}
.message.assistant[data-stream-tail="true"] .bubble{scroll-margin-bottom:12px}
.messages[data-stream-follow="true"]{scroll-behavior:auto!important}
`;
document.head.append(style);
installUserScrollIntent();
render(false);
})();
