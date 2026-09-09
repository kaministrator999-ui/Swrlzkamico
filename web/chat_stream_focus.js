(()=>{"use strict";
const STREAM_UI_VERSION='1.3.31';
let viewportEventType='',viewportMessageId='',viewportDeltaText='';
let streamFollow=true,lastBubbleHeight=0,lastFollowMessageId='',programmaticUntil=0;

function activeArticle(){
  const message=typeof activeMessage==='function'?activeMessage():null;
  if(!message)return null;
  return refs?.stack?.querySelector?.(`[data-message-id="${CSS.escape(message.id)}"]`)||null;
}

function nearRecentTail(){
  if(!refs?.messages)return true;
  const remaining=refs.messages.scrollHeight-refs.messages.clientHeight-refs.messages.scrollTop;
  const threshold=Math.max(96,Math.min(220,refs.messages.clientHeight*0.18));
  return remaining<=threshold;
}

function setProgrammaticScroll(value){
  if(!refs?.messages)return;
  programmaticUntil=performance.now()+120;
  refs.messages.scrollTop=value;
}

function focusGeneratedTail(force=false){
  const article=activeArticle();
  if(!article||!refs?.messages)return;
  const trace=article.querySelector('.trace');
  if(trace?.open){
    if(streamFollow||force)setProgrammaticScroll(refs.messages.scrollHeight);
    return;
  }
  if(!force&&viewportEventType!=='DELTA'&&viewportEventType!=='RESET')return;
  const bubble=article.querySelector('.bubble');
  if(!bubble)return;
  const currentId=String(article.dataset?.messageId||viewportMessageId||'');
  if(currentId!==lastFollowMessageId){
    lastFollowMessageId=currentId;
    lastBubbleHeight=0;
    streamFollow=nearRecentTail();
  }
  const style=getComputedStyle(bubble);
  const lineHeight=Math.max(16,parseFloat(style.lineHeight)||20);
  const bubbleHeight=Math.max(bubble.scrollHeight,bubble.getBoundingClientRect().height);
  const explicitLine=viewportDeltaText.includes('\n');
  const visualLine=lastBubbleHeight>0&&bubbleHeight-lastBubbleHeight>=lineHeight*0.55;
  lastBubbleHeight=bubbleHeight;
  if(!streamFollow&&!force)return;
  if(!force&&!explicitLine&&!visualLine&&viewportEventType!=='RESET')return;
  const viewport=refs.messages.getBoundingClientRect();
  const rect=bubble.getBoundingClientRect();
  const targetBottom=viewport.bottom-12;
  const delta=rect.bottom-targetBottom;
  // Never oscillate upward during streaming. Advance only when a new rendered/explicit line
  // crosses the viewport, so token-by-token width changes cannot make the conversation wobble.
  if(delta>1)setProgrammaticScroll(refs.messages.scrollTop+delta);
}

if(refs?.messages&&!refs.messages.dataset.swrlzLineFollowBound){
  refs.messages.dataset.swrlzLineFollowBound='1';
  refs.messages.addEventListener('scroll',()=>{
    if(performance.now()<programmaticUntil)return;
    // Manual movement away from the live tail pauses auto-follow without pausing generation.
    // Returning near the newest streamed region automatically rearms line-follow scrolling.
    streamFollow=nearRecentTail();
  },{passive:true});
}

scheduleRender=function(scroll=false){
  if(renderQueued)return;
  renderQueued=true;
  requestAnimationFrame(()=>{
    renderQueued=false;
    render(false);
    if(scroll)requestAnimationFrame(()=>focusGeneratedTail(false));
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
      if(trace.open)requestAnimationFrame(()=>{if(streamFollow)setProgrammaticScroll(refs.messages.scrollHeight);});
      else requestAnimationFrame(()=>focusGeneratedTail(true));
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
  viewportEventType=String(event?.type||'');
  viewportMessageId=String(context?.message?.id||'');
  viewportDeltaText=viewportEventType==='DELTA'?String(event?.text||''):'';
  if(viewportEventType==='RESET'){
    lastBubbleHeight=0;
    lastFollowMessageId=viewportMessageId;
    streamFollow=nearRecentTail();
  }
  return focusBaseConsume(event,context);
};

const focusBasePaintMode=paintMode;
paintMode=function(){
  const result=focusBasePaintMode();
  const line=document.querySelector('#swrlzHotVersionLine');
  if(line)line.textContent=String(line.textContent||'').replace(/CHAT v\d+\.\d+\.\d+/i,`CHAT v${STREAM_UI_VERSION}`);
  const detail=document.querySelector('#nodeDetail');
  if(detail)detail.textContent=String(detail.textContent||'').replace(/Chat v\d+\.\d+\.\d+/i,`Chat v${STREAM_UI_VERSION}`);
  return result;
};

const focusBaseExportCameraLog=exportCameraLog;
exportCameraLog=function(){
  const t=currentThread(),receipt=effectiveServerReceipt(),stamp=new Date().toISOString().replace(/[:.]/g,'-');
  const header=[`§wyrlz Stream Camera Export`,`exported=${new Date().toISOString()}`,`chatVersion=${STREAM_UI_VERSION}`,`threadId=${t?.id||'—'}`,`threadTitle=${t?.title||'—'}`,`baseVersion=${receipt.base}`,`hotServerVersion=${receipt.effective||'—'}`,`hotRevision=${receipt.hot||'—'}`,`eventCount=${camera.length}`,''].join('\n');
  const blob=new Blob([header+cameraText(true)+'\n'],{type:'text/plain;charset=utf-8'}),u=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=u;a.download=`swrlz-camera-${safeFilePart(t?.id)}-${stamp}.log.txt`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1500);toast(`Exported ${camera.length} camera event${camera.length===1?'':'s'} to device`);
};

const style=document.createElement('style');
style.textContent=`
.message.assistant .trace{order:initial}
.message.assistant .trace summary{user-select:none}
.message.assistant .trace:not([open]) .trace-list{display:none}
.message.assistant[data-stream-tail="true"] .bubble{scroll-margin-bottom:12px}
`;
document.head.append(style);

render(false);
paintMode();
})();
