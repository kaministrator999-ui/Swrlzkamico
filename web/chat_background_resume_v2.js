(()=>{"use strict";
if(window.__swrlzBackgroundResumeInstalled)return;
window.__swrlzBackgroundResumeInstalled=true;

const nativeFetch=window.fetch.bind(window);
const INTENT_MARK='[[SWRLZ_TURN_INTENT:';
const CARRIER='[[SWRLZ_RMCCA_TRANSPORT_V1:';
const RESUME_CONTRACT='resumable-v1';
const encoder=new TextEncoder();

function cleanTurnText(value){let text=String(value||'');const markers=['\n\n'+INTENT_MARK,INTENT_MARK,'[[social turn]]','[[coding turn]]','[[general turn]]'];for(const marker of markers){const at=text.indexOf(marker);if(at>=0)text=text.slice(0,at)}return text.trim()}
function classifyIntent(value){const text=cleanTurnText(value),words=text.split(/\s+/).filter(Boolean).length;const code=/\b(code|coding|program|programming|function|class|method|script|html|css|javascript|typescript|python|c\+\+|cpp|java|kotlin|rust|sql|api|json|implement|debug|refactor|snippet|compile|compiler)\b|\.(?:cpp|h|hpp|py|js|ts|html|css)\b/i.test(text);if(code)return 'coding';const social=/^(?:hey|hi|hello|yo|sup|thanks|thank you|lol|lmao|😂|😆|👋|🙂|😊|❤️|🫂)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$/i.test(text);if(words<=10&&social)return 'social';return 'general'}
function normalizeHistory(history){return Array.isArray(history)?history.map(item=>{if(!item||typeof item!=='object')return item;const next={...item};if(String(next.role||'').toLowerCase()==='user')next.text=cleanTurnText(next.text);return next}):history}
function fallbackNormalizePayload(payload){if(!payload||typeof payload!=='object')return payload;const next={...payload};const prompt=cleanTurnText(next.prompt);next.prompt=prompt;next.history=normalizeHistory(next.history);if(!next.turnIntent)next.turnIntent=classifyIntent(prompt);return next}
function compactCarrier(payload){const e=payload?.swrlzCognitiveContext,t=payload?.swrlzUserTimeContext;if(!e?.cognitiveClock&&!t)return '';const data={v:1};if(e?.cognitiveClock)data.e={envelopeId:String(e.envelopeId||''),directiveId:String(e.directiveId||''),cognitiveClock:e.cognitiveClock};if(t)data.t={localDate:String(t.localDate||''),localTime:String(t.localTime||''),daypart:String(t.daypart||''),timeZone:String(t.timeZone||''),utcOffset:String(t.utcOffset||'')};const encoded=JSON.stringify(data);return encoded.length<=1800?CARRIER+encoded+']]':''}
function withCarrier(payload){if(!payload||typeof payload!=='object')return payload;const carrier=compactCarrier(payload);if(!carrier)return payload;const history=(Array.isArray(payload.history)?payload.history:[]).filter(item=>!String(item?.text||'').startsWith(CARRIER));history.push({role:'assistant',text:carrier});return {...payload,history,_swrlzCarrierAttached:true}}
function canonicalizePayload(payload){const normalized=fallbackNormalizePayload(payload);let prepared=normalized,error='';try{const prepare=window.__swrlzCanonicalContext?.preparePayload;if(typeof prepare==='function')prepared=prepare(normalized)}catch(err){error=String(err?.message||err)}try{const ctx=window.__swrlzCanonicalContext;if(ctx&&typeof ctx.envelopeValid==='function'&&!ctx.envelopeValid(prepared)&&typeof ctx.preparePayload==='function')prepared=ctx.preparePayload({...normalized,swrlzCognitiveContext:null})}catch(err){error=[error,String(err?.message||err)].filter(Boolean).join(' | ')}if(prepared&&typeof prepared==='object'&&error)prepared={...prepared,swrlzCanonicalTransportError:error};return withCarrier(prepared)}
function isStreamRequest(input,init){try{const method=String(init?.method||input?.method||'GET').toUpperCase();const url=typeof input==='string'?input:(input?.url||'');return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(url)}catch(_){return false}}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}}
function currentMessage(rid){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(rid))||null}catch(_){return null}}
function trace(message,phase,reason){if(!message)return;message.meta=message.meta||{};message.meta.phase=phase;message.meta.trail=Array.isArray(message.meta.trail)?message.meta.trail:[];const last=message.meta.trail.at(-1);if(last?.reason!==reason)message.meta.trail.push({seq:Number(last?.seq||0)+1,phase,reason,at:Date.now()});if(message.meta.trail.length>80)message.meta.trail.splice(0,message.meta.trail.length-80);try{saveState()}catch(_){ }try{scheduleRender(false)}catch(_){ }}
function annotate(message,patch){if(!message)return;message.meta=message.meta||{};message.meta.networkContinuity={...(message.meta.networkContinuity||{}),...patch}}
function abortError(){try{return new DOMException('Aborted','AbortError')}catch(_){const e=new Error('Aborted');e.name='AbortError';return e}}
function sleep(ms,signal){return new Promise((resolve,reject)=>{if(signal?.aborted)return reject(abortError());const timer=setTimeout(done,ms);function done(){signal?.removeEventListener?.('abort',stop);resolve()}function stop(){clearTimeout(timer);reject(abortError())}signal?.addEventListener?.('abort',stop,{once:true})})}
async function waitForOnline(signal){while(!navigator.onLine){await new Promise((resolve,reject)=>{if(signal?.aborted)return reject(abortError());const online=()=>{cleanup();resolve()},abort=()=>{cleanup();reject(abortError())};function cleanup(){window.removeEventListener('online',online);signal?.removeEventListener?.('abort',abort)}window.addEventListener('online',online,{once:true});signal?.addEventListener?.('abort',abort,{once:true})})}}
function copyHeaders(source){const headers=new Headers();source.headers.forEach((v,k)=>headers.set(k,v));return headers}

async function openConnection(input,init,payload,resumeAfterSeq,signal){await waitForOnline(signal);const body={...payload,resumeAfterSeq:Math.max(0,Number(resumeAfterSeq||0))};return nativeFetch(input,{...init,signal,body:JSON.stringify(body)})}

function resilientBody(input,init,payload,firstResponse){
  const rid=String(payload.requestId||''),message=currentMessage(rid),signal=init.signal;
  let lastSeq=0,terminal=false,currentResponse=firstResponse,reconnects=0;
  annotate(message,{contract:RESUME_CONTRACT,reconnects:0,lastSeq:0,state:'live'});
  return new ReadableStream({
    async start(controller){
      try{
        while(!terminal){
          if(!currentResponse){
            reconnects++;
            annotate(message,{state:'reconnecting',reconnects,lastSeq});
            trace(message,'RECONNECTING','Network connection changed or dropped. §wyrlz is still generating on the server; reconnecting to the same generation session.');
            let delay=250;
            while(!currentResponse){
              if(signal?.aborted)throw abortError();
              try{
                await waitForOnline(signal);
                const response=await openConnection(input,init,payload,lastSeq,signal);
                if(response.status===404||response.status===409||response.status===410)throw new Error(`Generation session unavailable (HTTP ${response.status}).`);
                if(!response.ok)throw new Error(`Resume HTTP ${response.status}`);
                if(response.headers.get('x-swrlz-generation-session')!==RESUME_CONTRACT)throw new Error('The server does not expose resumable generation sessions.');
                currentResponse=response;
              }catch(err){if(signal?.aborted)throw abortError();annotate(message,{state:'waiting-network',lastError:String(err?.message||err)});await sleep(delay,signal);delay=Math.min(3000,Math.round(delay*1.6))}
            }
          }
          const replayThrough=Math.max(lastSeq,Number(currentResponse.headers.get('x-swrlz-replay-through-seq')||0));
          const reader=currentResponse.body?.getReader?.();
          if(!reader)throw new Error('Streaming response body is unavailable.');
          const decoder=new TextDecoder();let buffer='';
          try{
            while(true){
              const {value,done}=await reader.read();if(done)break;
              buffer+=decoder.decode(value,{stream:true});let nl;
              while((nl=buffer.indexOf('\n'))>=0){
                const line=buffer.slice(0,nl).trim();buffer=buffer.slice(nl+1);if(!line)continue;
                let event;try{event=JSON.parse(line)}catch(_){continue}
                const seq=Number(event?.seq||0);if(!Number.isInteger(seq)||seq<=lastSeq)continue;
                const backlog=seq<=replayThrough;
                if(backlog){annotate(message,{state:'catching-up',lastSeq,replayThrough});message&&(message.meta.phase='CATCHING_UP');if(event.type==='DELTA')await sleep(24,signal);else await sleep(4,signal)}
                controller.enqueue(encoder.encode(JSON.stringify(event)+'\n'));
                lastSeq=seq;annotate(message,{state:backlog?'catching-up':'live',lastSeq,replayThrough,reconnects});
                if(['COMPLETED','CANCELLED','FAILED'].includes(String(event.type||''))){terminal=true;break}
              }
              if(terminal)break;
            }
            buffer+=decoder.decode();
            if(buffer.trim()&&!terminal){try{const event=JSON.parse(buffer.trim()),seq=Number(event?.seq||0);if(Number.isInteger(seq)&&seq>lastSeq){controller.enqueue(encoder.encode(JSON.stringify(event)+'\n'));lastSeq=seq;if(['COMPLETED','CANCELLED','FAILED'].includes(String(event.type||'')))terminal=true}}catch(_){}}
          }catch(err){if(signal?.aborted)throw abortError();annotate(message,{state:'reconnecting',lastError:String(err?.message||err),lastSeq})}
          finally{try{reader.releaseLock()}catch(_){}}
          if(!terminal){currentResponse=null;continue}
        }
        annotate(message,{state:'complete',lastSeq,reconnects});controller.close();
      }catch(err){annotate(message,{state:'failed',lastError:String(err?.message||err),lastSeq,reconnects});controller.error(err)}
    },
    cancel(){try{if(!signal?.aborted&&typeof active!=='undefined'&&active?.controller)active.controller.abort()}catch(_){}}
  });
}

window.fetch=async function(input,init={}){
  if(!isStreamRequest(input,init))return nativeFetch(input,init);
  const raw=parseBody(init);if(!raw)return nativeFetch(input,init);
  const payload=canonicalizePayload(raw),rid=String(payload?.requestId||''),message=currentMessage(rid);
  const nextInit={...init,body:JSON.stringify(payload)};
  let response;
  try{response=await nativeFetch(input,nextInit)}catch(err){annotate(message,{state:'initial-network-error',lastError:String(err?.message||err)});throw err}
  if(response.headers.get('x-swrlz-generation-session')!==RESUME_CONTRACT)return response;
  const headers=copyHeaders(response);headers.set('x-swrlz-browser-continuity','same-generation-v1');
  trace(message,'GENERATING','Resumable generation session established. Network handoffs will reconnect to this same response without regenerating it.');
  return new Response(resilientBody(input,nextInit,payload,response),{status:response.status,statusText:response.statusText,headers});
};

window.__swrlzBackgroundResume={version:3,classifyIntent,cleanTurnText,canonicalizePayload,continuityPolicy:'same-generation-resume',resumeContract:RESUME_CONTRACT,catchupDeltaDelayMs:24,carrier:CARRIER};
})();
