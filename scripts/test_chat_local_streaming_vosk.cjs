"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const code=fs.readFileSync("voice-streaming-source/chat/§wyrlz/assets/local_voice_vosk.js","utf8");

(async () => {
  const waitFor = async (ready, message) => {
    for (let i=0; i<100; i++) {
      if (ready()) return;
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.fail(message);
  };
  const recognized=[];
  const micStreams=[];
  const instances=[];
  const events=[];
  let modelLoads=0,workerTerminations=0,playedAudioFrames=0;
  const model = {
    KaldiRecognizer: class {
      constructor(){this.listeners=new Map();this.removed=false;instances.push(this);}
      on(event, fn){this.listeners.set(event,fn);}
      setWords(){}
      acceptWaveform(){playedAudioFrames++;}
      remove(){this.removed=true;}
      emit(name,result){this.listeners.get(name)?.({result});}
    },
    terminate(){workerTerminations++;}
  };
  const window={
    Vosk:{createModel:async url=>{assert.match(url,/vosk-model-small-en-us-0\.15\.tar\.gz$/);modelLoads++;return model;}},
    dispatchEvent:event=>events.push(event.type),
    AudioContext:class {
      constructor(){this.state="running";this.destination={};}
      createScriptProcessor(){return {connect(){},disconnect(){},onaudioprocess:null};}
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){this.closed=true;return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{getUserMedia:async constraints=>{
    assert.equal(constraints.audio.echoCancellation,true);
    const track={stopped:false,stop(){this.stopped=true;}};
    const stream={track,getTracks:()=>[track]};
    micStreams.push(stream);
    return stream;
  }}};
  // vm.runInNewContext does not provide browser timer APIs automatically.
  // The production mic watchdog requires them even when audio is mocked.
  const sandbox={window,navigator,document:{},
    setTimeout:()=>1,clearTimeout:()=>{},
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}},console};
  vm.runInNewContext(code,sandbox);
  assert.ok(window.SwrlzLocalVoice);
  assert.ok(window.SwrlzLocalSpeechRecognition);

  const Rec=window.SwrlzLocalSpeechRecognition;
  const first=new Rec();
  const transcripts=[];
  let final=0,ended=0;
  first.onresult=e=>{const value=e.results[0];transcripts.push([value.isFinal,value[0].transcript]);if(value.isFinal)final++;};
  first.onend=()=>ended++;
  first.start();
  await waitFor(() => window.SwrlzLocalVoice.active, "First local microphone never became ready");
  assert.equal(modelLoads,1,"model loads only on opt-in");
  assert.equal(micStreams.length,1,"captures microphone exactly once");
  assert.equal(window.SwrlzLocalVoice.active,true);
  instances[0].emit("partialresult",{partial:"hey how"});
  instances[0].emit("result",{text:"hey how are you"});
  assert.equal(transcripts.length,2);
  assert.deepEqual(transcripts.map(x=>x[1]),["hey how","hey how are you"]);
  assert.equal(final,1);
  first.stop();
  assert.equal(ended,1);
  assert.equal(micStreams[0].track.stopped,true,"microphone tracks stopped on utterance end");
  assert.equal(instances[0].removed,true,"recognizer disposed after utterance");
  assert.equal(workerTerminations,0,"keep model ready across conversation turns");

  const second=new Rec();
  second.start();
  await waitFor(() => window.SwrlzLocalVoice.active, "Second local microphone never became ready");
  assert.equal(modelLoads,1,"reuse local model for the next turn");
  assert.equal(micStreams.length,2);
  second.abort();
  assert.equal(micStreams[1].track.stopped,true);
  window.SwrlzLocalVoice.dispose();
  for(let i=0;i<10;i++)await Promise.resolve();
  assert.equal(workerTerminations,1,"free WASM model when Talk turns off");
  assert.equal(playedAudioFrames,0,"no fabricated audio frames");
  console.log("PASS: local-only ASR, per-turn microphone teardown, partial/final callbacks, model reuse and worker termination");
})().catch(error=>{console.error(error);process.exitCode=1;});