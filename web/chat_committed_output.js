(()=>{"use strict";
if(window.__swrlzCommittedOutputInstalled)return;
window.__swrlzCommittedOutputInstalled=true;

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(!baseConsume)return;

const CONTROL_LINE_RE=/^(?:Output Budget|Coding Mode|Response Budget|Debugging|Priority)\s*:\s*(?:Preserve architecture|Finished syntactically|Retrieve the most relevant|Identify causal fault|Completion headroom|Prioritize the runnable|.*requested response.*)$/i;
const FENCE_RE=/```/g;

function stateFor(context){
  if(!context.__swrlzCommitState)context.__swrlzCommitState={staged:'',discarded:0,blocked:false,committedEvents:0,clientClosedFence:false};
  return context.__swrlzCommitState;
}
function fenceCount(text){return (String(text||'').match(FENCE_RE)||[]).length}
function insideFence(text){return fenceCount(text)%2===1}
function stripControlLeak(text){
  const lines=String(text||'').split('\n');
  const kept=[];
  for(const line of lines){
    const t=line.trim();
    if(CONTROL_LINE_RE.test(t))continue;
    if(/^Coding Mode:\s*Preserve architecture and constraints/i.test(t))continue;
    if(/^Debugging:\s*Identify causal fault/i.test(t))continue;
    if(/^Output Budget:\s*/i.test(t)&&/retrieved messages|syntactically coherent|requested response/i.test(t))continue;
    kept.push(line);
  }
  return kept.join('\n');
}
function degenerate(text){
  const s=String(text||'');
  const tail=s.slice(-900).toLowerCase();
  if(/(?:\balt\b|alt){8,}/i.test(tail))return true;
  if(/(?:```\s*){4,}/.test(tail))return true;
  if(/\b(?:delta|deltda|kitt|story|mee)\b(?:[\s.!`]*\b(?:delta|deltda|kitt|story|mee)\b){3,}/i.test(tail))return true;
  const words=(tail.match(/[a-z]{2,20}/g)||[]).slice(-48);
  return words.length>=28&&new Set(words).size/words.length<0.24;
}
function lastSentenceBoundary(text){
  const s=String(text||'');
  let best=-1;
  const re=/[.!?](?:["'\)\]]?)(?=\s|$)/g;
  let m;while((m=re.exec(s)))best=re.lastIndex;
  return best;
}
function splitSafe(committed,staged){
  const s=stripControlLeak(staged);
  if(!s)return {commit:'',rest:''};
  const combined=String(committed||'')+s;
  const code=insideFence(String(committed||''))||(/```[^\n]*\n/.test(s)&&insideFence(combined));
  if(code){
    const nl=s.lastIndexOf('\n');
    if(nl>=0)return {commit:s.slice(0,nl+1),rest:s.slice(nl+1)};
    return {commit:'',rest:s};
  }
  const para=s.lastIndexOf('\n\n');
  if(para>=0)return {commit:s.slice(0,para+2),rest:s.slice(para+2)};
  const sentence=lastSentenceBoundary(s);
  if(sentence>0)return {commit:s.slice(0,sentence),rest:s.slice(sentence)};
  const nl=s.lastIndexOf('\n');
  if(nl>=0)return {commit:s.slice(0,nl+1),rest:s.slice(nl+1)};
  return {commit:'',rest:s};
}
function annotate(message,st){
  if(!message)return;
  message.meta=message.meta||{};
  message.meta.committedOutputV1=true;
  message.meta.outputVisibilityPolicy='append-only-final-copy';
  message.meta.committedChars=String(message.text||'').length;
  message.meta.stagedChars=String(st.staged||'').length;
  message.meta.discardedStagedChars=Number(st.discarded||0);
  if(st.clientClosedFence)message.meta.clientClosedFence=true;
}
function addLocalTrace(message,phase,reason){
  if(!message)return;message.meta=message.meta||{};message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
  const last=message.meta.trail[message.meta.trail.length-1];
  if(last?.reason!==reason)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase,reason,at:Date.now()});
  if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);
}
function terminalFlush(context){
  const st=stateFor(context),message=context?.message;
  if(!message||st.blocked){st.staged='';annotate(message,st);return}
  let tail=stripControlLeak(st.staged);
  st.staged='';
  if(!tail){annotate(message,st);return}
  if(degenerate(String(message.text||'')+tail)){
    st.discarded+=tail.length;st.blocked=true;
    addLocalTrace(message,'COMMIT_GUARD','A rough generated tail was rejected before visibility because it became repetitive or malformed.');
    annotate(message,st);return;
  }
  message.text=String(message.text||'')+tail;
  if(insideFence(message.text)){
    message.text=message.text.replace(/\s*$/,'')+'\n```';
    st.clientClosedFence=true;
    addLocalTrace(message,'COMMIT_FINALIZE','The final visible code artifact was closed at the presentation boundary so the committed copy remains structurally complete.');
  }
  annotate(message,st);
}

consumeEvent=function(event,context){
  if(!event||typeof event!=='object')return baseConsume(event,context);
  const st=stateFor(context),message=context?.message;
  if(event.type==='DELTA'){
    const chunk=String(event.text??'');
    if(!st.blocked)st.staged+=chunk;
    if(!st.blocked&&degenerate(String(message?.text||'')+st.staged)){
      st.discarded+=st.staged.length;st.staged='';st.blocked=true;
      addLocalTrace(message,'COMMIT_GUARD','Generation entered a malformed/repetitive tail. The uncommitted rough tail was discarded before it could become visible.');
    }
    let visible='';
    if(!st.blocked){
      const split=splitSafe(message?.text||'',st.staged);visible=split.commit;st.staged=split.rest;
      if(visible)st.committedEvents++;
    }
    const next={...event,text:visible};
    const result=baseConsume(next,context);
    annotate(message,st);
    return result;
  }
  if(['COMPLETED','CANCELLED','FAILED'].includes(String(event.type||'')))terminalFlush(context);
  const result=baseConsume(event,context);
  annotate(message,st);
  return result;
};

window.__swrlzCommittedOutput={
  version:1,
  policy:'append-only-final-copy',
  description:'Raw deltas stage privately; only coherent committed chunks enter message.text and become user-visible.'
};
})();
