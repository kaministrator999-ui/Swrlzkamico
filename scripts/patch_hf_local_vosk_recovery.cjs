"use strict";
// HF Chat 1.1.31+ additive local-Vosk recovery; preserve all unrelated HTML.
const fs=require("node:fs");
const [source,destination]=process.argv.slice(2);
if(!source||!destination)throw Error("Usage: node patch_hf_local_vosk_recovery.cjs INPUT OUTPUT");
let html=fs.readFileSync(source,"utf8");
const required=['id="voiceConversationButton"','id="voiceProviderSelect"','swrlz-voice-delta','/api/lalm_station/stream',
'/chat/§wyrlz/assets/local_voice_vosk.js','/chat/§wyrlz/assets/voice_conversation.js'];
for(const key of required)if(!html.includes(key))throw Error("VOSK_RECOVERY_BASELINE_MISSING "+key);
if(html.includes("local_voice_vosk.js?v=")||html.includes("voice_conversation.js?v="))
 throw Error("VOSK_RECOVERY_ALREADY_PATCHED_OR_DIFFERENT_SCRIPT");
const v=html.match(/<meta name="swrlz-chat-version" content="(\d+)\.(\d+)\.(\d+)">/);
if(!v||Number(v[1])!==1||Number(v[2])!==1||Number(v[3])<31)
 throw Error("VOSK_RECOVERY_UNSUPPORTED_VERSION");
const old=v.slice(1).join(".");
const next="1.1."+(Number(v[3])+1);
const once=(a,b,label)=>{
 const count=html.split(a).length-1;
 if(count!==1)throw Error("VOSK_RECOVERY_SOURCE_DRIFT "+label+" count="+count);
 html=html.replace(a,b);
};
once('<meta name="swrlz-chat-version" content="'+old+'">','<meta name="swrlz-chat-version" content="'+next+'">',"meta");
once('const SWRLZ_CHAT_VERSION = "'+old+'";','const SWRLZ_CHAT_VERSION = "'+next+'";',"js-version");
for(const file of ["local_voice_vosk.js","voice_conversation.js"])
 once('<script src="/chat/§wyrlz/assets/'+file+'" defer></script>',
      '<script src="/chat/§wyrlz/assets/'+file+'?v='+next+'" defer></script>',
      file);
if(html.split("?v="+next).length!==3)throw Error("VOSK_RECOVERY_POSTPATCH_DUPLICATE");
fs.writeFileSync(destination,html);
console.log(JSON.stringify({result:"VOSK_RECOVERY_PATCH_READY",from:old,to:next,bytes:Buffer.byteLength(html)}));