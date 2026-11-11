"use strict";
/* Verify Browser Turbo routes to native browser STT without touching offline Vosk,
 * while Local and Local Turbo remain independent recognizers. Reproduce a
 * provisional "anyhow" revised to the correct phrase before canonical send.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const controller=fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/voice_conversation.js","utf8");
const html=fs.readFileSync("voice-turbo-source/chat/§wyrlz/index.html","utf8");
const selector=html.match(/<select id="voiceProviderSelect"[\s\S]*?<\/select>/)?.[0]||"";
for(const mode of ["browser","turbo","local","local-turbo"])
  assert.ok(selector.includes('value="'+mode+'"'),"missing selector option "+mode);
assert.ok(selector.includes('value="turbo" selected'),"browser Turbo must be the new default");
assert.ok(selector.includes("may use online speech recognition"),"browser service disclosure missing");
assert.ok(selector.includes("offline"),"offline Local modes must be identified");

function runMode(mode,shouldBeLocal,fastSpeech) {
  const eventMap=new Map(), browserInstances=[], localInstances=[], spoken=[], submitted=[], times=[];
  const synth={
    getVoices:()=>[{lang:"en-US",default:true}],
    cancel(){},
    speak(utterance){spoken.push({text:utterance.text,rate:utterance.rate});}
  };
  function el(id){
    return {id,value:"",hidden:true,disabled:false,attributes:{},handlers:new Map(),dataset:{},
      setAttribute(k,v){this.attributes[k]=v;},
      getAttribute(k){return this.attributes[k]||"false";},
      addEventListener(n,f){this.handlers.set(n,f);},
      dispatchEvent(){},
      click(){this.handlers.get("click")?.();}};
  }
  class BaseRecognition {
    start(){this.started=true;}
    stop(){this.onend?.();}
    abort(){this.aborted=true;}
  }
  class Browser extends BaseRecognition {constructor(){super();browserInstances.push(this);}}
  class Local extends BaseRecognition {constructor(){super();localInstances.push(this);}}
  class Speech {constructor(text){this.text=text;}}
  const elements=Object.fromEntries(["voiceConversationButton","voiceConversationStatus",
    "prompt","sendButton","micButton","imageAttachment","voiceProviderSelect"]
    .map(id=>[id,el(id)]));
  elements.voiceProviderSelect.value=mode;
  elements.imageAttachment.hidden=true;
  const fakeWindow={
    SpeechRecognition:Browser,SpeechSynthesisUtterance:Speech,speechSynthesis:synth,
    SwrlzLocalSpeechRecognition:Local,
    SwrlzLocalVoice:{stop(){},dispose(){}},
    addEventListener(n,f){(eventMap.get(n)||eventMap.set(n,[]).get(n)).push(f);},
    dispatchEvent(e){for(const f of eventMap.get(e.type)||[])f(e);}
  };
  const document={
    visibilityState:"visible",
    getElementById(id){return elements[id]||null;},
    body:{classList:{toggle(){}}},addEventListener(){}
  };
  const ctx={window:fakeWindow,document,navigator:{language:"en-US"},
    location:{pathname:"/chat/§wyrlz"},console,fetch:()=>Promise.resolve(),
    Event:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}},
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}},
    SpeechSynthesisUtterance:Speech,
    setTimeout(fn,ms){times.push({fn,ms});return times.length;},clearTimeout(){},Date};
  elements.sendButton.click=()=>{
    submitted.push(elements.prompt.value);
    fakeWindow.dispatchEvent({type:"swrlz-voice-turn",detail:{phase:"sent",requestId:"r1"}});
    elements.sendButton.disabled=true;
  };
  vm.runInNewContext(controller,ctx,{filename:"voice_conversation.js"});
  elements.voiceConversationButton.click();
  assert.equal(browserInstances.length,shouldBeLocal?0:1,mode+" browser engine selection");
  assert.equal(localInstances.length,shouldBeLocal?1:0,mode+" offline engine selection");
  const recognizer=(shouldBeLocal?localInstances:browserInstances)[0];
  assert.equal(recognizer.lang,"en-US",mode+" English recognizer locale");
  if(shouldBeLocal)assert.equal(Boolean(recognizer.turbo),mode==="local-turbo");
  assert.ok(recognizer.started,mode+" recognizer starts");
  recognizer.onresult({results:[{isFinal:false,0:{transcript:"anyhow"}}]});
  assert.equal(elements.prompt.value,"anyhow",mode+" provisional displayed");
  assert.equal(submitted.length,0,mode+" interim must never send");
  recognizer.onresult({results:[{isFinal:true,0:{transcript:"hey how are you"}}]});
  assert.equal(submitted.length,1,mode+" send only after final");
  assert.equal(submitted[0],"hey how are you",mode+" final replaces provisional");
  assert.equal(elements.voiceConversationButton.dataset.voiceState,"waiting");
  fakeWindow.dispatchEvent({type:"swrlz-voice-delta",detail:{
    requestId:"r1",text:"Hello there. This is a longer sentence for response playback."}});
  assert.equal(spoken.length,1,mode+" first completed sentence streams immediately");
  assert.equal(spoken[0].text,"Hello there.");
  assert.equal(spoken[0].rate,fastSpeech?1.14:1,mode+" expected playback rate");
  elements.voiceConversationButton.click();
  assert.equal(elements.voiceConversationButton.dataset.voiceState,"off");
}
runMode("browser",false,false);
runMode("turbo",false,true);
runMode("local",true,false);
runMode("local-turbo",true,true);
console.log("PASS: Turbo uses browser accuracy and fast reply speech; both optional offline Vosk modes stay separate");
