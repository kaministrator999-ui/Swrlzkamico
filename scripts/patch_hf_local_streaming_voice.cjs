"use strict";
// Patch only the opt-in browser/local mic selector, never replace unrelated Chat.
const fs = require("node:fs");
const [source, destination] = process.argv.slice(2);
if (!source || !destination) throw Error("Usage: node patch_hf_local_streaming_voice.cjs INPUT OUTPUT");
let html = fs.readFileSync(source, "utf8");
for (const marker of ['id="voiceConversationButton"', 'swrlz-voice-delta',
  '/chat/§wyrlz/assets/voice_conversation.js', '/api/lalm_station/stream'])
  if (!html.includes(marker)) throw Error("STREAMING_TALK_BASELINE_MISSING " + marker);
if (html.includes('id="voiceProviderSelect"') || html.includes('/chat/§wyrlz/assets/local_voice_vosk.js'))
  throw Error("LOCAL_STREAMING_ALREADY_PRESENT");
const m=html.match(/<meta name="swrlz-chat-version" content="(\d+)\.(\d+)\.(\d+)">/);
if (!m || Number(m[1]) !== 1 || Number(m[2]) !== 1 || Number(m[3]) < 30)
  throw Error("LOCAL_STREAMING_UNSUPPORTED_VERSION");
const from=m.slice(1).join(".");
const to=m[1]+"."+m[2]+"."+(Number(m[3])+1);
function once(a,b,label) {
  const n=html.split(a).length-1;
  if (n!==1) throw Error("LOCAL_STREAMING_SOURCE_DRIFT "+label+" count="+n);
  html=html.replace(a,b);
}
once('<meta name="swrlz-chat-version" content="'+from+'">',
     '<meta name="swrlz-chat-version" content="'+to+'">', "meta");
once('const SWRLZ_CHAT_VERSION = "'+from+'";',
     'const SWRLZ_CHAT_VERSION = "'+to+'";', "javascript-version");
const css=[
'    /* Opt-in local microphone mode remains alongside the working browser recognizer. */',
'    .voice-provider-label{display:inline-flex;align-items:center;gap:5px;min-height:30px;padding:0 5px;border-radius:8px;border:1px solid rgba(128,169,203,.32);color:#c3ecff;font-size:11px}',
'    .voice-provider-label select{max-width:170px;min-width:0;padding:4px 6px;border:0;border-radius:6px;background:rgba(4,23,40,.95);color:#edf8ff;font:inherit}',
'    .voice-provider-label select:focus-visible{outline:2px solid #73d5ff;outline-offset:2px}',
'    .voice-provider-label select:disabled{opacity:.72}',
''].join("\n");
once('  </style>\n',css+'  </style>\n',"style");
const selector=[
'        <label class="voice-provider-label" for="voiceProviderSelect">Input',
'          <select id="voiceProviderSelect" aria-label="Talk speech recognition mode" title="Browser default, or opt into ~41 MB on-device streaming transcription">',
'            <option value="browser" selected>Browser</option>',
'            <option value="local">Local stream · 41 MB</option>',
'          </select>',
'        </label>',
''].join("\n");
once('        <input id="imagePicker" type="file" accept="image/jpeg,image/png,image/webp" hidden>',
selector+'        <input id="imagePicker" type="file" accept="image/jpeg,image/png,image/webp" hidden>',"select");
once('  <script src="/chat/§wyrlz/assets/voice_conversation.js" defer></script>',
'  <script src="/chat/§wyrlz/assets/local_voice_vosk.js" defer></script>\n'+
'  <script src="/chat/§wyrlz/assets/voice_conversation.js" defer></script>',"asset");
if (html.split('id="voiceProviderSelect"').length!==2 ||
    html.split('/chat/§wyrlz/assets/local_voice_vosk.js').length!==2)
  throw Error("LOCAL_STREAMING_POSTPATCH_DUPLICATE");
fs.writeFileSync(destination,html);
console.log(JSON.stringify({result:"LOCAL_MIC_PATCH_READY",sourceVersion:from,nextVersion:to,bytes:Buffer.byteLength(html)}));