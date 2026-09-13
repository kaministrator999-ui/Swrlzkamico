(()=>{"use strict";
if(window.__swrlzTemporalPersonalityInstalled)return;
window.__swrlzTemporalPersonalityInstalled=true;

const priorFetch=window.fetch.bind(window);
const CLAIMS_KEY='swrlzGoogleLoginTestClaims';
const LEGACY_PREFS_KEY='swrlzAccountPrefsV1';
const ACCOUNT_PREFS_PREFIX='swrlzAccountPrefsV2.account.';
const DIRECT_TIME_RE=/^\s*(?:what(?:'s| is)(?: the)? time(?: for me| here| right now)?|what time is it(?: for me| here| right now)?|tell me(?: the)?(?: current| local)? time|current time(?: for me| here)?|my(?: current| local)? time)\s*[?.!]*\s*$/i;

function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}}
function safeJson(raw){try{const value=JSON.parse(raw||'null');return value&&typeof value==='object'?value:null}catch(_){return null}}
function preferredName(){
  const claims=safeJson(sessionStorage.getItem(CLAIMS_KEY));
  const subject=String(claims?.subject||'').trim();
  const key=subject?ACCOUNT_PREFS_PREFIX+encodeURIComponent(subject):LEGACY_PREFS_KEY;
  const prefs=safeJson(localStorage.getItem(key))||{};
  return String(prefs.preferredName||'').trim().slice(0,80);
}
function displayTime(ctx){
  const match=/^(\d{1,2}):(\d{2})/.exec(String(ctx?.localTime||''));
  if(!match)return String(ctx?.localTime||'').trim();
  const hour=Math.max(0,Math.min(23,Number(match[1]))),minute=match[2],suffix=hour>=12?'PM':'AM',h12=hour%12||12;
  return `${h12}:${minute} ${suffix}`;
}
function appendDirective(existing,extra){const base=String(existing||'').trim();return [base,extra].filter(Boolean).join(' ').trim()}
function currentMessage(requestId){try{const thread=typeof currentThread==='function'?currentThread():null;return [...(thread?.messages||[])].reverse().find(m=>m?.role==='assistant'&&String(m?.meta?.requestId||'')===String(requestId||''))||null}catch(_){return null}}
function annotate(payload,name,time,ctx){const message=currentMessage(payload?.requestId);if(!message)return;message.meta=message.meta||{};message.meta.temporalResponseContract={version:1,directCurrentTime:true,preferredNameAnchor:Boolean(name),timeAnchor:time,daypart:String(ctx?.daypart||''),personalityOutsideAnchors:true,timeAppropriateEmoji:true,at:Date.now()};try{typeof saveState==='function'&&saveState()}catch(_){ }}
function augment(payload){
  if(!payload||typeof payload!=='object')return payload;
  const ctx=payload.swrlzUserTimeContext;
  if(!DIRECT_TIME_RE.test(String(payload.prompt||''))||ctx?.available!==true||ctx?.timeSpecificClaimsAllowed!==true)return payload;
  const time=displayTime(ctx);if(!time)return payload;
  const name=preferredName();
  const nameRule=name?`The user's preferred-name anchor is ${JSON.stringify(name)}; include that exact name naturally once.`:'No preferred-name anchor is currently set; do not invent one.';
  const contract=(
    `Direct current-time response contract: the exact approved local-time anchor is ${JSON.stringify(time)}. ${nameRule} `+
    `These anchors are fixed facts; wording before, between, and after them may express §wyrlz personality. `+
    `Use a fitting time-of-day emoji rather than defaulting to a waving-hand emoji. `+
    `Do not redundantly say an AM time "in the morning" or a PM time "in the afternoon/evening"; if daypart adds value, make it separate natural context. `+
    `Keep the answer concise, warm, and conversational.`
  );
  const next={...payload,responseDirective:appendDirective(payload.responseDirective,contract)};
  annotate(next,name,time,ctx);
  return next;
}

window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const next=augment(payload);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};

window.__swrlzTemporalPersonality={version:1,preferredName,directTimePattern:DIRECT_TIME_RE,augment,policy:'fixed-preferred-name-and-approved-time-anchors-personality-outside'};
})();
