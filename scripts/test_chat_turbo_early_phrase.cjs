"use strict";
/* End-to-end fake streaming events: first Turbo audio must queue before the
 * first sentence or terminal response, without clipping words or duplicating
 * text. Existing Browser/Local timing and offline ASR are preserved.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync(
  "voice-turbo-source/chat/§wyrlz/assets/voice_conversation.js", "utf8");

function session(mode) {
  const events = new Map(), instances = [], spoken = [], traces = [];
  const synth = {
    live: null, busy: false,
    getVoices: () => [{lang:"en-US", default:true}],
    cancel() { this.live = null; this.busy = false; },
    speak(utterance) {
      assert.equal(this.busy, false, "speech output must never overlap");
      this.busy = true;
      this.live = utterance;
      spoken.push({text:utterance.text,rate:utterance.rate});
    }
  };
  function element(id) {
    return {
      id, value:"", hidden:true, disabled:false, dataset:{}, attrs:{},
      handlers:new Map(),
      setAttribute(name,v){this.attrs[name]=v;},
      getAttribute(name){return this.attrs[name]||"false";},
      addEventListener(name,fn){this.handlers.set(name,fn);},
      dispatchEvent(){},
      click(){this.handlers.get("click")?.();}
    };
  }
  class Recognition {
    constructor(){instances.push(this);}
    start(){this.started=true;}
    stop(){this.onend?.();}
    abort(){this.aborted=true;}
  }
  class Utterance { constructor(text){this.text=text;} }
  const elements = Object.fromEntries([
    "voiceConversationButton","voiceConversationStatus","prompt",
    "sendButton","micButton","imageAttachment","voiceProviderSelect"
  ].map(id=>[id,element(id)]));
  elements.voiceProviderSelect.value = mode;
  const fakeWindow = {
    SpeechRecognition: Recognition, SwrlzLocalSpeechRecognition: Recognition,
    SpeechSynthesisUtterance: Utterance, speechSynthesis: synth,
    SwrlzLocalVoice: {stop(){},dispose(){}},
    addEventListener(name,fn){
      (events.get(name)||events.set(name,[]).get(name)).push(fn);
    },
    dispatchEvent(e){for(const fn of events.get(e.type)||[])fn(e);}
  };
  const doc = {
    visibilityState:"visible",
    body:{classList:{toggle(){}}},
    getElementById:id=>elements[id]||null,
    addEventListener(){}
  };
  const context = {
    window:fakeWindow, document:doc,
    location:{pathname:"/chat/§wyrlz"},
    navigator:{language:"en-US"},
    fetch:()=>Promise.resolve(),
    Event:class{constructor(type,options){this.type=type;this.detail=options?.detail;}},
    CustomEvent:class{constructor(type,options){this.type=type;this.detail=options?.detail;}},
    SpeechSynthesisUtterance:Utterance,
    setTimeout(){return 1;},clearTimeout(){},
    Date, console
  };
  elements.sendButton.click = () => {
    fakeWindow.dispatchEvent({type:"swrlz-voice-turn",
      detail:{phase:"sent",requestId:"turn-1"}});
    elements.sendButton.disabled=true;
  };
  vm.runInNewContext(source,context,{filename:"voice_conversation.js"});
  elements.voiceConversationButton.click();
  const recognizer=instances.at(-1);
  assert.ok(recognizer.started);
  recognizer.onresult({results:[{isFinal:true,0:{transcript:"Hey, how are you?"}}]});
  assert.equal(elements.voiceConversationButton.dataset.voiceState,"waiting");
  function event(type,detail){fakeWindow.dispatchEvent({type,detail});}
  function delta(text,id="turn-1"){event("swrlz-voice-delta",{requestId:id,text});}
  function complete(text) {
    event("swrlz-voice-state",{requestId:"turn-1",terminalType:"COMPLETE",text});
  }
  function drain() {
    assert.ok(synth.live,"TTS must be active to drain");
    const prior=synth.live;
    synth.busy=false;
    synth.live=null;
    prior.onend();
  }
  function stop(){elements.voiceConversationButton.click();}
  return {spoken,synth,elements,delta,complete,drain,stop};
}
{
  const h=session("turbo");
  h.delta("I can explain how this works, ");
  assert.deepEqual(h.spoken.map(x=>x.text),["I can explain how this works,"],
    "Turbo speaks a natural clause at under 95 chars, before full sentence");
  assert.equal(h.elements.voiceConversationButton.dataset.voiceState,"speaking");
  assert.equal(h.spoken[0].rate,1.14);
  h.delta("because the answer is still generating and I can speak ");
  assert.equal(h.spoken.length,1,"do not speak two chunks simultaneously");
  h.drain();
  assert.equal(h.spoken.length,2,"second early phrase begins when first speech drains");
  const text="I can explain how this works, because the answer is still generating and I can speak ";
  h.complete(text+"while more words arrive.");
  h.drain();
  assert.equal(h.spoken.length,3,"terminal suffix is queued exactly once");
  h.drain();
  assert.equal(h.elements.voiceConversationButton.dataset.voiceState,"listening",
    "microphone reopens only after generation complete and speech drain");
  assert.equal(h.spoken.map(x=>x.text).join(" "),
    "I can explain how this works, because the answer is still generating and I can speak while more words arrive.",
    "no duplicated, missing or clipped words across chunk boundaries");
  h.complete(text+"while more words arrive.");
  assert.equal(h.spoken.length,3,"duplicate terminal must not replay");
  h.stop();
}
{
  const h=session("turbo");
  h.delta("Here is a straightforward explanation that begins with the incomp");
  assert.equal(h.spoken.length,1,"first phrase speaks without waiting for sentence");
  assert.ok(!h.spoken[0].text.includes("incomp"),"never speak unfinished token");
  h.delta("lete word and continues naturally.");
  h.complete("Here is a straightforward explanation that begins with the incomplete word and continues naturally.");
  h.drain();
  assert.equal(h.spoken.length,2);
  assert.equal(h.spoken.map(x=>x.text).join(" "),
    "Here is a straightforward explanation that begins with the incomplete word and continues naturally.");
  h.drain();
  h.stop();
}
for (const mode of ["browser","local","local-turbo"]) {
  const h=session(mode);
  h.delta("I can explain how this works, because the answer is still ");
  assert.equal(h.spoken.length,0,mode+" must keep the existing longer buffering");
  h.complete("I can explain how this works, because the answer is still generating.");
  assert.equal(h.spoken.length,1,mode+" sends after terminal");
  h.drain();
  h.stop();
}
{
  const h=session("turbo");
  h.delta("This first message is long enough to speak early with ");
  assert.equal(h.spoken.length,1);
  h.stop();
  h.delta("should never play again after stop");
  h.complete("stale");
  assert.equal(h.spoken.length,1,"cancelled voice turn discards stale events");
}
console.log("PASS: Browser Turbo speaks completed clauses before sentence/terminal, serializes speech, preserves words, and leaves offline modes unchanged");
