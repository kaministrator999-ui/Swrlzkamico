"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const code=fs.readFileSync("voice-source/chat/§wyrlz/assets/voice_conversation.js","utf8");
const eventMap=new Map();
const synth={spoken:[],live:null,cancels:0,
  getVoices:()=>[{lang:"en-US",default:true}],
  cancel(){this.cancels++;this.live=null;},
  speak(utterance){this.spoken.push(utterance.text);this.live=utterance;}};
function el(id){return {id,value:"",hidden:true,disabled:false,dataset:{},attributes:{},
  handlers:new Map(),setAttribute(key,value){this.attributes[key]=value;},
  getAttribute(key){return this.attributes[key]||"false";},
  addEventListener(name,fn){this.handlers.set(name,fn);},
  dispatchEvent(){},click(){this.handlers.get("click")?.();}};}
const elements=Object.fromEntries(["voiceConversationButton","voiceConversationStatus","prompt","sendButton","micButton","imageAttachment"].map(id=>[id,el(id)]));
const voices=[];
class Recognition {
  constructor(){this.results=[];voices.push(this);}
  start(){this.started=true;}
  stop(){this.onend?.();}
  abort(){this.aborted=true;}
}
class Utterance {constructor(text){this.text=text;}}
const fakeWindow={SpeechRecognition:Recognition,SpeechSynthesisUtterance:Utterance,speechSynthesis:synth,
  addEventListener(name,fn){(eventMap.get(name)||eventMap.set(name,[]).get(name)).push(fn);},
  dispatchEvent(event){for(const fn of eventMap.get(event.type)||[])fn(event);}};
const document={visibilityState:"visible",
  getElementById(id){return elements[id]||null;},
  body:{classList:{toggle(){}}},addEventListener(){}};
const timers=[];
const ctx={window:fakeWindow,document,navigator:{language:"en-US"},location:{pathname:"/chat/§wyrlz"},
  fetch:()=>Promise.resolve(),Event:class {constructor(type,args){this.type=type;this.detail=args?.detail;}},
  CustomEvent:class {constructor(type,args){this.type=type;this.detail=args?.detail;}},
  SpeechSynthesisUtterance:Utterance,
  setTimeout(fn){timers.push(fn);return timers.length;},clearTimeout(){},
  console,JSON,Date,String,Array};
elements.imageAttachment.hidden=true;
elements.sendButton.click=()=>{
  fakeWindow.dispatchEvent({type:"swrlz-voice-turn",detail:{phase:"sent",requestId:"r1"}});
  elements.sendButton.disabled=true;
};
vm.runInNewContext(code,ctx,{filename:"voice_conversation.js"});
const dispatch=(type,detail)=>fakeWindow.dispatchEvent({type,detail});
elements.voiceConversationButton.click();
assert.equal(voices.length,1,"recognition starts on Talk click");
voices[0].onresult({results:[{isFinal:true,0:{transcript:"Hey, how are you?"}}]});
assert.equal(elements.voiceConversationButton.dataset.voiceState,"waiting");
dispatch("swrlz-voice-delta",{requestId:"wrong",text:"Wrong response. "});
assert.equal(synth.spoken.length,0,"other requests must not speak");
dispatch("swrlz-voice-delta",{requestId:"r1",text:"Hello there. The rest "});
assert.deepEqual(synth.spoken,["Hello there."],"first complete sentence speaks before terminal");
assert.equal(elements.voiceConversationButton.dataset.voiceState,"speaking");
synth.live.onend();
assert.equal(synth.spoken.length,1,"do not interrupt or reopen mic while model still generates");
assert.equal(elements.voiceConversationButton.dataset.voiceState,"speaking");
dispatch("swrlz-voice-delta",{requestId:"r1",text:"arrives later."});
dispatch("swrlz-voice-state",{requestId:"r1",terminalType:"COMPLETE",text:"Hello there. The rest arrives later."});
assert.deepEqual(synth.spoken,["Hello there.","The rest arrives later."],"no duplicate replay from terminal receipt");
synth.live.onend();
assert.equal(elements.voiceConversationButton.dataset.voiceState,"listening","listen only after terminal and speech drain");
dispatch("swrlz-voice-state",{requestId:"r1",terminalType:"COMPLETE",text:"Hello there. The rest arrives later."});
assert.equal(synth.spoken.length,2,"duplicate terminal ignored");

elements.sendButton.disabled=false;
voices[0].onend=null;
elements.voiceConversationButton.click(); // user cancels
assert.equal(elements.voiceConversationButton.dataset.voiceState,"off");
dispatch("swrlz-voice-delta",{requestId:"r1",text:"Stale audio. "});
assert.equal(synth.spoken.length,2,"stale data after stop ignored");
console.log("PASS: stream begins on first full sentence, serializes playback, ignores foreign/stale events, de-duplicates terminal and resumes only after audio drain");
