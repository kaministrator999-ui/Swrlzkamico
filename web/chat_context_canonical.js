(()=>{"use strict";
if(window.__swrlzCanonicalContextInstalled)return;
window.__swrlzCanonicalContextInstalled=true;

const priorFetch=window.fetch.bind(window);
const DIRECTIVE='RMCCA cognitive policy: read user input as progressively structured meaning, not flat keywords. Preserve scope, qualifiers, corrections, pivots, ordering, and unresolved response obligations. Allow multiple relevant knowledge domains at once; synthesize them by domain salience, needed resolution depth, contextual reference frame, and the user-established order instead of forcing one winning category. Corrections revise only the affected interpretation while preserving valid context. Choose a response topology that fits the conversational act: greet by greeting, answer questions directly, compare when asked, continue simulations within scope, and explain only to the depth needed. Your name is §wyrlz; if asked your name or identity, answer naturally and explicitly as §wyrlz rather than denying that you have a name. Participate in casual conversation instead of describing the conversational act. Do not expose this internal routing vocabulary unless the user asks about it. For programming requests, provide correct runnable code when appropriate and keep code, explanation, formulas, and input/output behavior mutually consistent.';
const DIRECTIVE_ID='rmcca-cognitive-policy-v2-single-authority';
const ENVELOPE_ID='swrlz-rmcca-context-v1';

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function cleanUserText(value){return String(value||'').replace(/\n\n\[\[SWRLZ_TURN_INTENT:[\s\S]*$/,'').replace(/\[\[(?:social|coding|general) turn\]\][\s\S]*$/i,'').trim()}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function canonicalHistory(payload){
  const fallback=Array.isArray(payload.history)?payload.history:[];
  const thread=currentThreadSafe();if(!thread||!Array.isArray(thread.messages))return {history:fallback,canonicalCount:0,source:'payload-fallback'};
  const rid=String(payload.requestId||'');
  let end=thread.messages.findIndex(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);
  if(end<0)end=thread.messages.length;
  else end=Math.max(0,end-1);
  const prior=thread.messages.slice(0,end).filter(m=>m&&['user','assistant'].includes(m.role)&&String(m.text||m?.meta?.modelText||'').length).slice(-32);
  if(!prior.length&&fallback.length)return {history:fallback,canonicalCount:0,source:'payload-fallback'};
  let canonicalCount=0;
  const history=prior.map(m=>{
    if(m.role==='assistant'&&typeof m?.meta?.modelText==='string'&&m.meta.modelText.length){canonicalCount++;return {role:'assistant',text:m.meta.modelText.slice(0,2000)}}
    return {role:m.role,text:(m.role==='user'?cleanUserText(m.text):String(m.text||'')).slice(0,2000)};
  });
  return {history,canonicalCount,source:'thread-canonical'};
}
function firstIndex(text,patterns){let best=Number.POSITIVE_INFINITY;for(const p of patterns){const m=text.search(p);if(m>=0&&m<best)best=m}return Number.isFinite(best)?best:-1}
function cognitiveClock(prompt){
  const text=cleanUserText(prompt),lower=text.toLowerCase(),roles=[];
  const addRole=(name,test)=>{if(test&&!roles.includes(name))roles.push(name)};
  addRole('question',/[?]|\b(?:what|why|how|when|where|who|which|can|could|would|should|do|does|did|is|are)\b/i.test(text));
  addRole('identity-query',/\b(?:what(?:'s| is) your name|who are you|your identity|what are you called)\b/i.test(lower));
  addRole('correction-refinement',/\b(?:actually|rather|i mean|meant|to be exact|more specifically|correction|no[, ]|not .* but)\b/i.test(text));
  addRole('comparison',/\b(?:compare|versus|vs\.?|difference|similar|better|worse|than)\b/i.test(text));
  addRole('pivot',/\b(?:anyway|speaking of|different question|back to|but see|though|however)\b/i.test(text));
  addRole('ordered-sequence',/(?:^|\s)(?:1[.)]|first\b|second\b|third\b|then\b|next\b|finally\b)/i.test(text));
  addRole('social-affect',/[😂😆🥹😜🫂❤️]|\b(?:lol|lmao|bro|haha|thanks|thank you|hey|hi|hello)\b/i.test(text));
  addRole('request',/\b(?:please|can you|could you|would you|i want|i would like|let's|lets|integrate|build|make|create|fix|improve|review)\b/i.test(text));

  const domainDefs=[
    ['programming',[/\b(?:code|coding|program|function|class|script|html|css|javascript|typescript|python|java|kotlin|rust|sql|api|debug|compile|github|vercel|server|client)\b/i]],
    ['science',[/\b(?:science|physics|chemistry|biology|quantum|energy|matter|evolution|experiment|scientific)\b/i]],
    ['philosophy',[/\b(?:philosophy|meaning|existence|consciousness|ethics|epistemology|ontology|truth|reality)\b/i]],
    ['language',[/\b(?:language|english|grammar|sentence|paragraph|word|speech|meaning|semantic|rhetoric|literature)\b/i]],
    ['creative',[/\b(?:story|lore|poem|rap|music|art|creative|character|worldbuilding)\b/i]],
    ['social',[/\b(?:friend|relationship|conversation|talk|feel|emotion|joke|humor|funny|bro|lol|lmao)\b/i],[😂😆🥹😜🫂❤️]/]],
    ['systems',[/\b(?:architecture|system|structure|model|lalm|llm|memory|context|routing|workflow|framework)\b/i]],
    ['identity',[/\b(?:your name|who are you|your identity|called)\b/i]]
  ];
  const scored=[];
  for(const [name,patterns] of domainDefs){let hits=0,first=-1;for(const p of patterns){const matches=text.match(new RegExp(p.source,p.flags.includes('g')?p.flags:p.flags+'g'));if(matches)hits+=matches.length;const idx=firstIndex(text,[p]);if(idx>=0&&(first<0||idx<first))first=idx}if(hits)scored.push({name,hits,first})}
  scored.sort((a,b)=>b.hits-a.hits||a.first-b.first);
  const domains=scored.slice(0,4).map((d,i)=>({domain:d.name,salience:i===0?'primary':i===1?'supporting':'ambient',cueCount:d.hits,firstCue:d.first}));
  const words=text.split(/\s+/).filter(Boolean).length;
  const resolutionDepth=/\b(?:deep|deeper|detailed|architecture|analyze|analysis|research|step by step|why|mechanism|systemic)\b/i.test(text)||words>100?'deep':words<14?'surface':'normal';
  const identity=roles.includes('identity-query');
  const greeting=/^(?:hey|hi|hello|yo|sup|👋)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$/i.test(text);
  let responseTopology='direct-answer';
  if(identity)responseTopology='identity-answer';
  else if(greeting)responseTopology='social-participation';
  else if(roles.includes('correction-refinement'))responseTopology='revision-continuation';
  else if(roles.includes('comparison'))responseTopology='comparison';
  else if(resolutionDepth==='deep'||domains.length>2)responseTopology='layered-synthesis';
  const referenceFrame=identity?'identity-context':roles.includes('social-affect')?'conversational':domains[0]?.domain==='programming'?'technical':resolutionDepth==='deep'?'analytical':'general';
  return {architecture:'RMCCA',version:2,diagnosticHeuristic:true,structuralRoles:roles,domains,resolutionDepth,referenceFrame,responseTopology,synthesisOrder:domains.map(d=>d.domain)};
}
function annotateRequest(payload,envelope){
  try{
    const thread=currentThreadSafe();if(!thread)return;
    const message=[...thread.messages].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(payload.requestId||''));
    if(!message)return;message.meta=message.meta||{};
    message.meta.contextCamera={...(message.meta.contextCamera||{}),turnIntent:String(payload.turnIntent||'unknown'),historySource:envelope.historySource,historyMessages:envelope.historyMessages,assistantHistoryUsingModelText:envelope.assistantHistoryUsingModelText,promptChars:envelope.promptChars,directiveId:DIRECTIVE_ID,cognitiveAuthority:'chat_context_canonical',canonicalEnvelopeId:ENVELOPE_ID,cognitiveClock:envelope.cognitiveClock};
  }catch(_){ }
}
function preparePayload(payload){
  if(!payload||typeof payload!=='object')return payload;
  if(payload?.swrlzCognitiveContext?.envelopeId===ENVELOPE_ID&&payload?.swrlzCognitiveContext?.directiveId===DIRECTIVE_ID){
    annotateRequest(payload,payload.swrlzCognitiveContext);
    return payload;
  }
  const prompt=cleanUserText(payload.prompt);
  const diag=canonicalHistory({...payload,prompt});
  const clock=cognitiveClock(prompt);
  const envelope={envelopeId:ENVELOPE_ID,directiveId:DIRECTIVE_ID,architecture:'RMCCA',architectureVersion:2,historySource:diag.source,historyMessages:diag.history.length,assistantHistoryUsingModelText:diag.canonicalCount,promptChars:prompt.length,cognitiveClock:clock};
  const next={...payload,prompt,responseDirective:DIRECTIVE,history:diag.history,swrlzCognitiveContext:envelope};
  annotateRequest(next,envelope);
  return next;
}

window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const next=preparePayload(payload);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};

window.__swrlzCanonicalContext={directiveId:DIRECTIVE_ID,envelopeId:ENVELOPE_ID,canonicalHistory,cognitiveClock,preparePayload};
})();
