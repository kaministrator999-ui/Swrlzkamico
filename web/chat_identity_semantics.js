(()=>{"use strict";
if(window.__swrlzIdentitySemanticsInstalled)return;
window.__swrlzIdentitySemanticsInstalled=true;

const BRAND='§wyrlz';
const ALIAS_RE=/\b(?:swurlz|swrlz|swyrlz)\b/gi;
const priorFetch=window.fetch.bind(window);

function canonicalizeIdentity(value){return String(value??'').replace(ALIAS_RE,BRAND)}
function streamUrl(input){try{return typeof input==='string'?input:(input?.url||'')}catch(_){return ''}}
function isStream(input,init){const method=String(init?.method||input?.method||'GET').toUpperCase();return method==='POST'&&/(?:[?&]action=stream(?:&|$)|\/stream(?:[?#]|$))/i.test(streamUrl(input))}
function parseBody(init){if(typeof init?.body!=='string')return null;try{const value=JSON.parse(init.body);return value&&typeof value==='object'?value:null}catch(_){return null}}
function normalizeHistory(history){return Array.isArray(history)?history.map(item=>{if(!item||typeof item!=='object')return item;if(String(item.role||'').toLowerCase()!=='user')return item;return {...item,text:canonicalizeIdentity(item.text)}}):history}
function normalizePayload(payload){if(!payload||typeof payload!=='object')return payload;return {...payload,prompt:canonicalizeIdentity(payload.prompt),history:normalizeHistory(payload.history)}}

window.fetch=function(input,init={}){
  if(!isStream(input,init))return priorFetch(input,init);
  const payload=parseBody(init);if(!payload)return priorFetch(input,init);
  const next=normalizePayload(payload);
  return priorFetch(input,{...init,body:JSON.stringify(next)});
};

window.__swrlzIdentitySemantics={version:1,brand:BRAND,aliases:['swurlz','swrlz','swyrlz'],canonicalizeIdentity,normalizePayload,policy:'semantic-aliases-canonicalize-to-section-sign-brand-raw-thread-preserved'};
})();
