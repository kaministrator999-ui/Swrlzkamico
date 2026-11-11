"use strict";
/* Turbo input regression: recognize soft speech; preserve Vosk phrase result
 * segments through brief pauses; submit only after true end-of-turn silence.
 * Browser mode and original Local mode are independently regression-tested.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/local_voice_vosk.js", "utf8");

(async () => {
  const waitFor = async test => {
    for (let i=0; i<100; i++) {
      if (test()) return;
      await new Promise(done => setTimeout(done,10));
    }
    assert.fail("Turbo mic did not initialize");
  };
  let timestamp=1000, modelLoads=0, sampleRate=48000, rejectInteractive=false, totalAudioFrames=0;
  const contexts=[], processors=[], recognizers=[], tracks=[];
  const model = {
    KaldiRecognizer: class {
      constructor(rate){
        assert.equal(rate,sampleRate,"Recognizer gets the native AudioContext sample rate");
        this.handlers=new Map();
        recognizers.push(this);
      }
      on(type,callback){this.handlers.set(type,callback);}
      setWords(){}
      acceptWaveform(audio){assert.ok(audio.getChannelData);totalAudioFrames++;}
      remove(){this.removed=true;}
      emit(type,result){this.handlers.get(type)?.({result});}
    },
    terminate(){}
  };
  const window = {
    Vosk:{async createModel(){modelLoads++;return model;}},
    dispatchEvent(){},
    AudioContext:class {
      constructor(options) {
        if (rejectInteractive && options?.latencyHint)
          throw Error("Unsupported interactive context");
        this.sampleRate=sampleRate;
        this.state="running";
        this.destination={};
        contexts.push(options||{});
      }
      createScriptProcessor(samples){
        const p={size:samples,connect(){},disconnect(){},onaudioprocess:null};
        processors.push(p);return p;
      }
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{async getUserMedia(){
    const track={stopped:false,stop(){this.stopped=true;}};
    tracks.push(track);
    return {getTracks(){return [track];}};
  }}};
  const FakeDate=class extends Date { static now(){return timestamp;} };
  vm.runInNewContext(source, {
    window,navigator,Date:FakeDate,console,
    setTimeout:()=>1,clearTimeout:()=>{},
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}}
  });
  const Recognition=window.SwrlzLocalSpeechRecognition;
  async function begin(){
    const rec=new Recognition();
    rec.turbo=true;
    rec.messages=[];
    rec.onresult=event=>{
      const result=event.results[0];
      rec.messages.push({final:result.isFinal,text:result[0].transcript});
      if(result.isFinal)rec.stop();
    };
    rec.start();
    await waitFor(()=>window.SwrlzLocalVoice.active);
    return rec;
  }
  function frames(n,amplitude,step=100) {
    const processor=processors.at(-1);
    for(let i=0;i<n;i++){
      timestamp+=step;
      processor.onaudioprocess?.({
        inputBuffer:{getChannelData(){return new Float32Array(2048).fill(amplitude);}}
      });
    }
  }

  const first=await begin();
  assert.equal(contexts[0].latencyHint,"interactive");
  assert.equal(contexts[0].sampleRate,undefined,"do not force lossy 16kHz browser resampling");
  assert.equal(processors[0].size,2048,"reduce callback overhead relative to 1024");
  frames(4,.009); // soft speech below original 0.012 threshold
  recognizers.at(-1).emit("partialresult",{partial:"hello there"});
  recognizers.at(-1).emit("result",{text:"hello there"});
  assert.equal(first.messages.filter(m=>m.final).length,0,
    "Vosk phrase result must not auto-send the conversation");
  frames(8,0);
  assert.equal(first.messages.filter(m=>m.final).length,0,
    "800ms natural pause must not end turn");
  frames(4,.009);
  recognizers.at(-1).emit("partialresult",{partial:"how are you"});
  assert.equal(first.messages.at(-1).text,"hello there how are you",
    "on-screen transcript should combine earlier finalized phrase with new words");
  recognizers.at(-1).emit("result",{text:"how are you"});
  assert.equal(first.messages.filter(m=>m.final).length,0,"second phrase not auto-sent");
  frames(11,0);
  assert.equal(first.messages.filter(m=>m.final).length,0,"1100ms thinking pause not end of turn");
  frames(7,0);
  assert.equal(first.messages.filter(m=>m.final).length,1,"true prolonged quiet closes once");
  assert.equal(first.messages.at(-1).text,"hello there how are you");
  assert.equal(tracks[0].stopped,true);

  sampleRate=44100;
  rejectInteractive=true;
  const second=await begin();
  assert.equal(contexts.at(-1).sampleRate,undefined,"fallback uses native rate");
  assert.equal(processors.at(-1).size,2048);
  frames(5,.009);
  recognizers.at(-1).emit("partialresult",{partial:"one more thing"});
  frames(18,0);
  assert.equal(second.messages.filter(m=>m.final).length,1,
    "partial-only speech is still sent after sustained silence");
  assert.equal(second.messages.at(-1).text,"one more thing");
  assert.equal(modelLoads,1,"normal and Turbo reuse existing Vosk model");
  assert.equal(tracks[1].stopped,true);
  window.SwrlzLocalVoice.dispose();
  assert.ok(totalAudioFrames>20);
  console.log("PASS: native 48/44.1kHz Turbo, 2048 buffers, soft speech, multi-phrase results, pause safety, final silence, model reuse");
})().catch(e=>{console.error(e);process.exitCode=1;});