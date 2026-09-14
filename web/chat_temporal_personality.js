(()=>{"use strict";
if(window.__swrlzTemporalPersonalityInstalled)return;
window.__swrlzTemporalPersonalityInstalled=true;

const CLAIMS_KEY='swrlzGoogleLoginTestClaims';
const LEGACY_PREFS_KEY='swrlzAccountPrefsV1';
const ACCOUNT_PREFS_PREFIX='swrlzAccountPrefsV2.account.';
function safeJson(raw){try{const value=JSON.parse(raw||'null');return value&&typeof value==='object'?value:null}catch(_){return null}}
function preferredName(){const claims=safeJson(sessionStorage.getItem(CLAIMS_KEY));const subject=String(claims?.subject||'').trim();const key=subject?ACCOUNT_PREFS_PREFIX+encodeURIComponent(subject):LEGACY_PREFS_KEY;const prefs=safeJson(localStorage.getItem(key))||{};return String(prefs.preferredName||'').trim().slice(0,80)}
function augment(payload){return payload}
window.__swrlzTemporalPersonality={version:2,preferredName,augment,policy:'profile-facts-only-no-client-temporal-response-steering',interpretationOwner:'lalm'};
})();
