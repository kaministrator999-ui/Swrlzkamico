"use strict";
// Patch only the live Station DELTA bridge. All other active Chat work survives.
const fs=require("node:fs");
const [source,destination]=process.argv.slice(2);
if(!source||!destination)throw Error("Usage: node patch_hf_streaming_voice.cjs INPUT OUTPUT");
let html=fs.readFileSync(source,"utf8");
if(html.includes("swrlz-voice-delta"))throw Error("STREAMING_VOICE_ALREADY_INSTALLED");
for(const marker of ['id="voiceConversationButton"','swrlz-voice-state','/chat/§wyrlz/assets/voice_conversation.js','/api/lalm_station/stream'])
 if(!html.includes(marker))throw Error("LIVE_VOICE_BASELINE_MISSING "+marker);
const version=html.match(/<meta name="swrlz-chat-version" content="(\d+)\.(\d+)\.(\d+)">/);
if(!version||Number(version[1])!==1||Number(version[2])!==1||Number(version[3])<29)
 throw Error("LIVE_VOICE_UNSUPPORTED_VERSION");
const v0=version.slice(1).join(".");
const v1="1.1."+(Number(version[3])+1);
function once(a,b,label){const n=html.split(a).length-1;if(n!==1)throw Error("STATION_BRIDGE_DRIFT "+label+" count="+n);html=html.replace(a,b);}
once('<meta name="swrlz-chat-version" content="'+v0+'">','<meta name="swrlz-chat-version" content="'+v1+'">',"version-meta");
once('const SWRLZ_CHAT_VERSION = "'+v0+'";','const SWRLZ_CHAT_VERSION = "'+v1+'";',"version-js");
const original='            if(event.type==="DELTA")stationGeneration.text=(stationGeneration.text||"")+String(event.text||"");';
const streaming=[
'            if(event.type==="DELTA"){',
'              const deltaText=String(event.text||"");',
'              stationGeneration.text=(stationGeneration.text||"")+deltaText;',
'              if(deltaText)window.dispatchEvent(new CustomEvent("swrlz-voice-delta",{detail:{requestId,threadId,text:deltaText}}));',
'            }'
].join("\n");
once(original,streaming,"stream-delta");
if(html.split("swrlz-voice-delta").length!==2||html.split("swrlz-voice-state").length<2)
 throw Error("STREAMING_VOICE_POSTPATCH_GUARD");
fs.writeFileSync(destination,html);
console.log(JSON.stringify({status:"STREAMING_VOICE_PATCH_READY",sourceVersion:v0,nextVersion:v1,bytes:Buffer.byteLength(html)}));