(()=>{"use strict";
if(window.__swrlzCommittedOutputV2Installed)return;
window.__swrlzCommittedOutputV2Installed=true;

const baseConsume=typeof consumeEvent==='function'?consumeEvent:null;
if(!baseConsume)return;

const FENCE_RE=/```/g;
const INTERNAL_LABEL_RE=/^(?:Output Budget|Coding Mode|Response Budget|Debugging|Priority|DELTA)\s*:??\s*$/i;
const MAX_RETRIEVED_RE=/\bat\s+most\s+(\d{1,2})\s+(?:retrieved\s+)?(?:older\s+)?messages\b/i;
const RECENT_WINDOW_RE=/\b(?:keep\s+the\s+)?(?:most\s+)?recent\s+(\d{1,3})\s+messages\b/i;
const CODE_REQUEST_RE=/\b(?:complete\s+)?runnable\s+(?:python\s+)?code\b|\bprovide\s+(?:complete\s+)?(?:runnable\s+)?(?:python\s+)?code\b/i;
const EXAMPLE_RE=/\binclude\s+(?:one\s+)?example\b|\bexample\s+conversation\b/i;
const PREFILL_RE=/\bprompt[- ]prefill\b/i;

function priorUserPrompt(context){
  try{
    const thread=typeof currentThread==='function'?currentThread():null;
    if(!thread||!Array.isArray(thread.messages))return '';
    const index=thread.messages.findIndex(m=>m===context?.message||String(m?.id||'')===String(context?.message?.id||''));
    for(let i=(index>=0?index-1:thread.messages.length-1);i>=0;i--)if(thread.messages[i]?.role==='user')return String(thread.messages[i].text||'');
  }catch(_){ }
  return '';
}
function buildLedger(prompt){
  const text=String(prompt||''),max=MAX_RETRIEVED_RE.exec(text),recent=RECENT_WINDOW_RE.exec(text);
  return {
    maxRetrievedOlder:max?Number(max[1]):null,
    recentWindow:recent?Number(recent[1]):null,
    requireRunnableCode:CODE_REQUEST_RE.test(text),
    requirePython:/\bpython\b/i.test(text)&&CODE_REQUEST_RE.test(text),
    requireExample:EXAMPLE_RE.test(text),
    requirePrefillExplanation:PREFILL_RE.test(text),
    userSuppliedPercent:/\b\d+(?:\.\d+)?\s*%/.test(text),
    asksForLexicalScore:/\blexical\s+relevance\s+score\b/i.test(text)
  };
}
function stateFor(context){
  if(!context.__swrlzCommitStateV2){
    const ledger=buildLedger(priorUserPrompt(context));
    context.__swrlzCommitStateV2={staged:'',discarded:0,blocked:false,committedEvents:0,clientClosedFence:false,ledger,section:'',retrievedOlderCount:0,seenHeadings:new Set(),semanticRejects:[]};
  }
  return context.__swrlzCommitStateV2;
}
function fenceCount(text){return (String(text||'').match(FENCE_RE)||[]).length}
function insideFence(text){return fenceCount(text)%2===1}
function addLocalTrace(message,phase,reason){
  if(!message)return;message.meta=message.meta||{};message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];
  const last=message.meta.trail[message.meta.trail.length-1];if(last?.reason!==reason)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase,reason,at:Date.now()});
  if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);
}
function recordReject(st,message,reason,text){
  const entry={reason,text:String(text||'').slice(0,180)};st.semanticRejects.push(entry);if(st.semanticRejects.length>20)st.semanticRejects.shift();st.discarded+=String(text||'').length;
  addLocalTrace(message,'SEMANTIC_COMMIT_GUARD',reason);
}
function cleanControlLines(text){
  const lines=String(text||'').split('\n'),kept=[];
  for(const line of lines){const t=line.trim();if(INTERNAL_LABEL_RE.test(t))continue;if(/^Coding Mode:\s*/i.test(t)||/^Debugging:\s*/i.test(t)||/^Response Budget:\s*/i.test(t)||/^Priority:\s*/i.test(t))continue;kept.push(line)}
  return kept.join('\n');
}
function degenerate(text){
  const tail=String(text||'').slice(-900).toLowerCase();
  if(/(?:\balt\b|alt){8,}/i.test(tail))return true;
  if(/(?:```\s*){4,}/.test(tail))return true;
  if(/\b(?:delta|deltda|kitt|story|mee)\b(?:[\s.!`]*\b(?:delta|deltda|kitt|story|mee)\b){3,}/i.test(tail))return true;
  const words=(tail.match(/[a-z]{2,20}/g)||[]).slice(-48);return words.length>=28&&new Set(words).size/words.length<0.24;
}
function lastSentenceBoundary(text){let best=-1,m;const re=/[.!?](?:["'\)\]]?)(?=\s|$)/g,s=String(text||'');while((m=re.exec(s)))best=re.lastIndex;return best}
function splitSafe(committed,staged){
  const s=cleanControlLines(staged);if(!s)return {commit:'',rest:''};
  const combined=String(committed||'')+s,code=insideFence(String(committed||''))||(/```[^\n]*\n/.test(s)&&insideFence(combined));
  if(code){const nl=s.lastIndexOf('\n');return nl>=0?{commit:s.slice(0,nl+1),rest:s.slice(nl+1)}:{commit:'',rest:s}}
  const para=s.lastIndexOf('\n\n');if(para>=0)return {commit:s.slice(0,para+2),rest:s.slice(para+2)};
  const sentence=lastSentenceBoundary(s);if(sentence>0)return {commit:s.slice(0,sentence),rest:s.slice(sentence)};
  const nl=s.lastIndexOf('\n');return nl>=0?{commit:s.slice(0,nl+1),rest:s.slice(nl+1)}:{commit:'',rest:s};
}
function normalizeHeading(line){return String(line||'').trim().replace(/:$/,'').trim().toLowerCase()}
function isHeading(line){const t=String(line||'').trim();return /^(?:Architecture(?: Overview)?|Example(?: Conversation)?|Retrieved Older Messages|Retrieved Recent Messages(?: \(most relevant\))?|Output|Explanation|Implementation|Code|How it works|Prefill(?: Cost)?)(?::)?$/i.test(t)}
function sanitizeSemantic(context,chunk){
  const st=stateFor(context),message=context?.message,ledger=st.ledger;
  if(!chunk)return '';
  if(insideFence(String(message?.text||'')))return chunk;
  const lines=String(chunk).split('\n'),kept=[];
  for(let line of lines){const trimmed=line.trim();
    if(!trimmed){kept.push(line);continue}
    if(isHeading(trimmed)){
      const key=normalizeHeading(trimmed);
      if(st.seenHeadings.has(key)){recordReject(st,message,`Duplicate structural heading “${trimmed}” was rejected before visibility.`,line);continue}
      st.seenHeadings.add(key);
      if(/^retrieved older messages/i.test(trimmed))st.section='retrieved-older';else if(/^retrieved recent/i.test(trimmed))st.section='retrieved-recent';else st.section=key;
      kept.push(line);continue;
    }
    if(st.section==='retrieved-older'&&/^\s*(?:\d+[.)]|[-*+])\s+\S/.test(line)){
      if(ledger.maxRetrievedOlder!=null&&st.retrievedOlderCount>=ledger.maxRetrievedOlder){recordReject(st,message,`Retrieved-older limit=${ledger.maxRetrievedOlder}; an extra list item was rejected before visibility.`,line);continue}
      st.retrievedOlderCount++;
    }
    if(!ledger.userSuppliedPercent&&/\b(?:reduce[sd]?|reduction|improv(?:e[sd]?|ement))\b[^.!?\n]{0,100}\b\d+(?:\.\d+)?\s*%/i.test(line)){
      const cleaned=line.replace(/\s+by\s+\d+(?:\.\d+)?\s*%/ig,'').replace(/\b\d+(?:\.\d+)?\s*%\s+(?:reduction|improvement)\b/ig,'');
      if(cleaned!==line){recordReject(st,message,'An unsupported percentage was removed before visibility.',line);line=cleaned}
    }
    if(ledger.asksForLexicalScore&&!/\bexample\b/i.test(line)){
      const cleaned=line.replace(/\blexical\s+relevance\s+score\s+of\s+\d+(?:\.\d+)?\b/ig,'lexical relevance score');
      if(cleaned!==line){recordReject(st,message,'A fabricated fixed lexical-score value was removed before visibility.',line);line=cleaned}
    }
    kept.push(line);
  }
  return kept.join('\n');
}
function hasRunnableCode(text,requirePython){
  const blocks=[...String(text||'').matchAll(/```\s*([A-Za-z0-9_+.-]*)\s*\n([\s\S]*?)```/g)];
  return blocks.some(m=>{const lang=(m[1]||'').toLowerCase(),code=m[2]||'';if(requirePython&&!['python','py',''].includes(lang))return false;if(requirePython)return /\b(?:def|class|import|from)\b/.test(code)&&code.trim().length>=60;return code.trim().length>=40});
}
function evaluateLedger(text,ledger,st){
  const value=String(text||''),lower=value.toLowerCase(),gaps=[];
  if(ledger.maxRetrievedOlder!=null&&st.retrievedOlderCount>ledger.maxRetrievedOlder)gaps.push(`retrieved-older<=${ledger.maxRetrievedOlder}`);
  if(ledger.requireRunnableCode&&!hasRunnableCode(value,ledger.requirePython))gaps.push('runnable-code');
  if(ledger.requireExample&&!lower.includes('example'))gaps.push('example');
  if(ledger.requirePrefillExplanation&&!(lower.includes('prefill')&&(lower.includes('prompt')||lower.includes('context'))))gaps.push('prefill-explanation');
  if(ledger.recentWindow!=null){const rx=new RegExp(`(?:recent|window|latest)[^\\n.]{0,80}\\b${ledger.recentWindow}\\b|\\b${ledger.recentWindow}\\b[^\\n.]{0,80}(?:recent|window|latest)`,'i');if(!rx.test(value))gaps.push(`recent-window=${ledger.recentWindow}`)}
  return gaps;
}
function annotate(message,st){
  if(!message)return;message.meta=message.meta||{};message.meta.committedOutputV2=true;message.meta.outputVisibilityPolicy='append-only-final-copy-semantic';message.meta.committedChars=String(message.text||'').length;message.meta.stagedChars=String(st.staged||'').length;message.meta.discardedStagedChars=Number(st.discarded||0);message.meta.requirementLedger=st.ledger;message.meta.semanticCommitRejects=st.semanticRejects.slice(-10);message.meta.retrievedOlderCommitted=st.retrievedOlderCount;if(st.clientClosedFence)message.meta.clientClosedFence=true;
}
function terminalFlush(context){
  const st=stateFor(context),message=context?.message;if(!message||st.blocked){st.staged='';annotate(message,st);return}
  let tail=cleanControlLines(st.staged);st.staged='';if(!tail){annotate(message,st);return}
  if(degenerate(String(message.text||'')+tail)){recordReject(st,message,'A malformed/repetitive terminal tail was rejected before visibility.',tail);st.blocked=true;annotate(message,st);return}
  tail=sanitizeSemantic(context,tail);message.text=String(message.text||'')+tail;
  if(insideFence(message.text)){message.text=message.text.replace(/\s*$/,'')+'\n```';st.clientClosedFence=true;addLocalTrace(message,'COMMIT_FINALIZE','The final visible code artifact was closed at the presentation boundary so the committed copy remains structurally complete.')}
  annotate(message,st);
}

consumeEvent=function(event,context){
  if(!event||typeof event!=='object')return baseConsume(event,context);
  const st=stateFor(context),message=context?.message;
  if(event.type==='DELTA'){
    if(!st.blocked)st.staged+=String(event.text??'');
    if(!st.blocked&&degenerate(String(message?.text||'')+st.staged)){recordReject(st,message,'Generation entered a malformed/repetitive tail; the rough tail was discarded before visibility.',st.staged);st.staged='';st.blocked=true}
    let visible='';if(!st.blocked){const split=splitSafe(message?.text||'',st.staged);visible=sanitizeSemantic(context,split.commit);st.staged=split.rest;if(visible)st.committedEvents++}
    const result=baseConsume({...event,text:visible},context);annotate(message,st);return result;
  }
  if(['COMPLETED','CANCELLED','FAILED'].includes(String(event.type||'')))terminalFlush(context);
  let next=event;
  if(event.type==='COMPLETED'){
    const gaps=evaluateLedger(message?.text||'',st.ledger,st);message.meta=message.meta||{};message.meta.requirementGaps=gaps;message.meta.requirementLedgerPassed=gaps.length===0;
    if(gaps.length){next={...event,type:'FAILED',phase:'ERROR',terminal:true,reason:`Final-copy validation found unmet user requirements: ${gaps.join(', ')}. Visible committed text was preserved.`};addLocalTrace(message,'REQUIREMENT_GUARD',next.reason)}
  }
  const result=baseConsume(next,context);annotate(message,st);return result;
};

window.__swrlzCommittedOutput={version:2,policy:'append-only-final-copy-semantic',description:'Raw deltas stage privately; semantic constraints are checked before coherent chunks enter the final visible buffer.'};
})();
