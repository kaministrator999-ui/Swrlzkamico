(()=>{"use strict";
if(window.__swrlzCanonicalContextInstalled)return;
window.__swrlzCanonicalContextInstalled=true;

const priorFetch=window.fetch.bind(window);
const pendingReceipts=new Map();
const RECEIPT_TTL_MS=10*60*1000;
const DIRECTIVE='RMCCA cognitive policy: read user input as progressively structured meaning, not flat keywords. Preserve scope, qualifiers, corrections, pivots, ordering, and unresolved response obligations. Allow multiple relevant knowledge domains at once; synthesize them by domain salience, needed resolution depth, contextual reference frame, and the user-established order instead of forcing one winning category. Corrections revise only the affected interpretation while preserving valid context. Choose a response topology that fits the conversational act. For greetings and casual social openings, participate directly and naturally: greet back, match the user’s conversational energy, and continue the interaction. Never describe the act by saying things such as “This is a friendly greeting” or “The user is greeting me.” Answer questions directly, compare when asked, continue simulations within scope, and explain only to the depth needed. Your name is §wyrlz. If asked your name or identity, answer naturally in first-person conversational context, such as “I’m §wyrlz.” or an equally natural equivalent. Do not deny having a name and do not emit only the bare label §wyrlz unless the user specifically requests only the name or label. Do not expose this internal routing vocabulary unless the user asks about it. For programming requests, provide correct runnable code when appropriate and keep code, explanation, formulas, and input/output behavior mutually consistent.';
const DIRECTIVE_ID='rmcca-cognitive-policy-v4-social-participation';
const ENVELOPE_ID='swrlz-rmcca-context-v3';

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const v=JSON.parse(init.body);return v&&typeof v==='object'?v:null}catch(_){return null}}
function cleanUserText(value){return String(value||'').replace(/\n\n\[\[SWRLZ_TURN_INTENT:[\s\S]*$/,'').replace(/\[\[(?:social|coding|general) turn\]\][\s\S]*$/i,'').trim()}
function currentThreadSafe(){try{return typeof currentThread==='function'?currentThread():null}catch(_){return null}}
function canonicalHistory(payload){
  const fallback=Array.isArray(payload.history)?payload.history:[];
  try{
    const thread=currentThreadSafe();if(!thread||!Array.isArray(thread.messages))return {history:fallback,canonicalCount:0,source:'payload-fallback'};
    const rid=String(payload.requestId||'');
    let end=thread.messages.findIndex(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===rid);
    if(end<0)end=thread.messages.length;else end=Math.max(0,end-1);
    const prior=thread.messages.slice(0,end).filter(m=>m&&['user','assistant'].includes(m.role)&&String(m.text||m?.meta?.modelText||'').length).slice(-32);
    if(!prior.length&&fallback.length)return {history:fallback,canonicalCount:0,source:'payload-fallback'};
    let canonicalCount=0;
    const history=prior.map(m=>{
      if(m.role==='assistant'&&typeof m?.meta?.modelText==='string'&&m.meta.modelText.length){canonicalCount++;return {role:'assistant',text:m.meta.modelText.slice(0,2000)}}
      return {role:m.role,text:(m.role==='user'?cleanUserText(m.text):String(m.text||'')).slice(0,2000)};
    });
    return {history,canonicalCount,source:'thread-canonical'};
  }catch(error){return {history:fallback,canonicalCount:0,source:'payload-fallback-error',historyError:String(error?.message||error)}}
}
function firstIndex(text,patterns){let best=Number.POSITIVE_INFINITY;for(const p of patterns){const m=text.search(p);if(m>=0&&m<best)best=m}return Number.isFinite(best)?best:-1}
function cognitiveClock(prompt){
  const text=cleanUserText(prompt),lower=text.toLowerCase(),roles=[];
  const addRole=(name,test)=>{if(test&&!roles.includes(name))roles.push(name)};
  addRole('question',/[?]|\b(?:what|why|how|when|where|who|which|can|could|would|should|do|does|did|is|are)\b/i.test(text));
  addRole('identity-query',/\b(?:what(?:'s| is) your name|who are you|your identity|what are you called|what should i call you)\b/i.test(lower));
  addRole('correction-refinement',/\b(?:actually|rather|i mean|meant|to be exact|more specifically|correction|no[, ]|not .* but)\b/i.test(text));
  addRole('comparison',/\b(?:compare|versus|vs\.?|difference|similar|better|worse|than)\b/i.test(text));
  addRole('pivot',/\b(?:anyway|speaking of|different question|back to|but see|though|however)\b/i.test(text));
  addRole('ordered-sequence',/(?:^|\s)(?:1[.)]|first\b|second\b|third\b|then\b|next\b|finally\b)/i.test(text));
  addRole('social-affect',/[😂😆🥹😜🫂❤️👋]|\b(?:lol|lmao|bro|haha|thanks|thank you|hey|hi|hello|yo|sup)\b/i.test(text));
  addRole('request',/\b(?:please|can you|could you|would you|i want|i would like|let's|lets|integrate|build|make|create|fix|improve|review)\b/i.test(text));
  const domainDefs=[
    ['programming',[/\b(?:code|coding|program|function|class|script|html|css|javascript|typescript|python|java|kotlin|rust|sql|api|debug|compile|github|vercel|server|client)\b/i]],
    ['science',[/\b(?:science|physics|chemistry|biology|quantum|energy|matter|evolution|experiment|scientific)\b/i]],
    ['philosophy',[/\b(?:philosophy|meaning|existence|consciousness|ethics|epistemology|ontology|truth|reality)\b/i]],
    ['language',[/\b(?:language|english|grammar|sentence|paragraph|word|speech|meaning|semantic|rhetoric|literature)\b/i]],
    ['creative',[/\b(?:story|lore|poem|rap|music|art|creative|character|worldbuilding)\b/i]],
    ['social',[/\b(?:friend|relationship|conversation|talk|feel|emotion|joke|humor|funny|bro|lol|lmao|hey|hi|hello|yo|sup)\b/i],[😂😆🥹😜🫂❤️👋]/]],
    ['systems',[/\b(?:architecture|system|structure|model|lalm|llm|memory|context|routing|workflow|framework)\b/i]],
    ['identity',[/\b(?:your name|who are you|your identity|called|call you)\b/i]]
  ];
  const scored=[];
  for(const [name,patterns] of domainDefs){let hits=0,first=-1;for(const p of patterns){try{const flags=p.flags.includes('g')?p.flags:p.flags+'g';const matches=text.match(new RegExp(p.source,flags));if(matches)hits+=matches.length;const idx=firstIndex(text,[p]);if(idx>=0&&(first<0||idx<first))first=idx}catch(_){}}if(hits)scored.push({name,hits,first})}
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
  const referenceFrame=identity?'identity-context':greeting||roles.includes('social-affect')?'conversational':domains[0]?.domain==='programming'?'technical':resolutionDepth==='deep'?'analytical':'general';
  return {architecture:'RMCCA',version:4,diagnosticHeuristic:true,structuralRoles:roles,domains,resolutionDepth,referenceFrame,responseTopology,synthesisOrder:domains.map(d=>d.domain)};
}
function safeClock(prompt){try{return cognitiveClock(prompt)}catch(error){return {architecture:'RMCCA',version:4,diagnosticHeuristic:true,structuralRoles:[],domains:[],resolutionDepth:'surface',referenceFrame:'general',responseTopology:'direct-answer',synthesisOrder:[],clockError:String(error?.message||error)}}}
function receiptFromEnvelope(payload,envelope){return {requestId:String(payload?.requestId||''),capturedAt:Date.now(),turnIntent:String(payload?.turnIntent||'unknown'),historySource:envelope.historySource,historyMessages:envelope.historyMessages,assistantHistoryUsingModelText:envelope.assistantHistoryUsingModelText,promptChars:envelope.promptChars,directiveId:DIRECTIVE_ID,cognitiveAuthority:'chat_context_canonical',canonicalEnvelopeId:ENVELOPE_ID,cognitiveClock:envelope.cognitiveClock,canonicalPrepareStatus:envelope.prepareStatus||'ok',canonicalPrepareError:envelope.prepareError||''}}
function pruneReceipts(){const now=Date.now();for(const [rid,r] of pendingReceipts.entries())if(!r||now-Number(r.capturedAt||0)>RECEIPT_TTL_MS)pendingReceipts.delete(rid)}
function rememberReceipt(payload,envelope){pruneReceipts();const receipt=receiptFromEnvelope(payload,envelope);if(receipt.requestId)pendingReceipts.set(receipt.requestId,receipt);return receipt}
function applyReceipt(message,receipt){if(!message||!receipt)return false;message.meta=message.meta||{};message.meta.contextCamera={...(message.meta.contextCamera||{}),...receipt};return true}
function annotateRequest(payload,envelope){try{const receipt=rememberReceipt(payload,envelope),thread=currentThreadSafe();if(!thread)return false;const message=[...thread.messages].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(payload.requestId||''));if(!message)return false;applyReceipt(message,receipt);return true}catch(_){return false}}
function attachReceipt(requestId,message,{consume=false}={}){pruneReceipts();const rid=String(requestId||'');const receipt=pendingReceipts.get(rid);if(!receipt)return false;const ok=applyReceipt(message,receipt);if(ok&&consume)pendingReceipts.delete(rid);return ok}
function peekReceipt(requestId){pruneReceipts();return pendingReceipts.get(String(requestId||''))||null}
function releaseReceipt(requestId){pendingReceipts.delete(String(requestId||''))}
function buildEnvelope(payload){
  const prompt=cleanUserText(payload?.prompt);
  const diag=canonicalHistory({...payload,prompt});
  const clock=safeClock(prompt);
  return {envelopeId:ENVELOPE_ID,directiveId:DIRECTIVE_ID,architecture:'RMCCA',architectureVersion:4,historySource:diag.source,historyMessages:Array.isArray(diag.history)?diag.history.length:0,assistantHistoryUsingModelText:Number(diag.canonicalCount||0),promptChars:prompt.length,cognitiveClock:clock,prepareStatus:diag.historyError||clock.clockError?'degraded':'ok',prepareError:[diag.historyError,clock.clockError].filter(Boolean).join(' | ')};
}
function preparePayload(payload){
  if(!payload||typeof payload!=='object')return payload;
  try{
    if(payload?.swrlzCognitiveContext?.envelopeId===ENVELOPE_ID&&payload?.swrlzCognitiveContext?.directiveId===DIRECTIVE_ID){rememberReceipt(payload,payload.swrlzCognitiveContext);annotateRequest(payload,payload.swrlzCognitiveContext);return payload}
    const prompt=cleanUserText(payload.prompt),diag=canonicalHistory({...payload,prompt}),clock=safeClock(prompt);
    const envelope={envelopeId:ENVELOPE_ID,directiveId:DIRECTIVE_ID,architecture:'RMCCA',architectureVersion:4,historySource:diag.source,historyMessages:Array.isArray(diag.history)?diag.history.length:0,assistantHistoryUsingModelText:Number(diag.canonicalCount||0),promptChars:prompt.length,cognitiveClock:clock,prepareStatus:diag.historyError||clock.clockError?'degraded':'ok',prepareError:[diag.historyError,clock.clockError].filter(Boolean).join(' | ')};
    const next={...payload,prompt,responseDirective:DIRECTIVE,history:Array.isArray(diag.history)?diag.history:[],swrlzCognitiveContext:envelope};
    rememberReceipt(next,envelope);annotateRequest(next,envelope);return next;
  }catch(error){
    const prompt=cleanUserText(payload.prompt),clock=safeClock(prompt),envelope={envelopeId:ENVELOPE_ID,directiveId:DIRECTIVE_ID,architecture:'RMCCA',architectureVersion:4,historySource:'payload-emergency',historyMessages:Array.isArray(payload.history)?payload.history.length:0,assistantHistoryUsingModelText:0,promptChars:prompt.length,cognitiveClock:clock,prepareStatus:'emergency',prepareError:String(error?.message||error)};
    const next={...payload,prompt,responseDirective:DIRECTIVE,history:Array.isArray(payload.history)?payload.history:[],swrlzCognitiveContext:envelope};rememberReceipt(next,envelope);annotateRequest(next,envelope);return next;
  }
}
function envelopeValid(payload){const e=payload?.swrlzCognitiveContext;return Boolean(e&&e.envelopeId===ENVELOPE_ID&&e.directiveId===DIRECTIVE_ID&&payload.responseDirective===DIRECTIVE)}

window.fetch=function(input,init={}){if(!isStream(input,init))return priorFetch(input,init);const payload=parseBody(init);if(!payload)return priorFetch(input,init);const next=preparePayload(payload);return priorFetch(input,{...init,body:JSON.stringify(next)})};
window.__swrlzCanonicalContext={directiveId:DIRECTIVE_ID,envelopeId:ENVELOPE_ID,directive:DIRECTIVE,canonicalHistory,cognitiveClock:safeClock,preparePayload,buildEnvelope,envelopeValid,attachReceipt,peekReceipt,releaseReceipt,pendingReceipts};
})();
