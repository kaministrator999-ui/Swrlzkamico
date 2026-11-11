"use strict";
/* Local Turbo only: 16kHz context, 1024 frame callbacks, fast silence,
 * safe 48kHz fallback; never alter cached model or browser Talk baseline. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const source=fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/local_voice_vosk.js","utf8");

(async()=>{
  const wait=async ready=>{
    for(let i=0;i<100;i++){if(ready())return;await new Promise(r=>setTimeout(r,10));}
    assert.fail("Turbo local microphone never became ready");
  };
  let tick=1000,downloads=0,created=0,ended=0;
  let unsupported=false;
  const contexts=[], processors=[],recognizers=[],streams=[];
  const model={
    KaldiRecognizer:class{
      constructor(rate){
        assert.equal(rate,unsupported?48000:16000,"Vosk must receive actual context rate");
        this.handlers=new Map();this.removed=false;recognizers.push(this);
      }
      on(name,fn){this.handlers.set(name,fn);}
      setWords(){}
      acceptWaveform(buffer){assert.ok(buffer.getChannelData);}
      emit(type,value){this.handlers.get(type)?.({result:value});}
      remove(){this.removed=true;}
    },
    terminate(){}
  };
  const window={
    Vosk:{async createModel(){downloads++;return model;}},
    dispatchEvent(){},
    AudioContext:class{
      constructor(options){
        if(unsupported&&options?.sampleRate)throw new Error("NotSupportedError");
        this.sampleRate=options?.sampleRate||48000;
        this.state="running";this.destination={};
        contexts.push(options);
      }
      createScriptProcessor(samples){processors.push(samples);return{
        connect(){},disconnect(){},
        set onaudioprocess(fn){this.fn=fn;processors[processors.length-1]={samples,process:fn};},
        get onaudioprocess(){return this.fn;}
      };}
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{async getUserMedia(){
    const track={stop(){this.stopped=true;}};const stream={track,getTracks(){return [track];}};
    streams.push(stream);return stream;
  }}};
  const fakeDate=class extends Date{static now(){return tick;}};
  vm.runInNewContext(source,{window,navigator,Date:fakeDate,console,
    setTimeout:()=>1,clearTimeout:()=>{},
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts.detail;}}
  });
  const Recognition=window.SwrlzLocalSpeechRecognition;
  const start=async()=>{
    const r=new Recognition();r.turbo=true;r.results=[];
    r.onresult=e=>{r.results.push(e.results[0]);if(e.results[0].isFinal){ended++;r.stop();}};
    r.start();await wait(()=>window.SwrlzLocalVoice.active);
    return r;
  };
  const a=await start();
  assert.equal(contexts[0].sampleRate,16000,"16 kHz explicit browser resampling requested");
  assert.equal(processors[0].samples,1024,"Turbo uses tighter audio blocks");
  const p=processors[0];
  for(let i=0;i<4;i++){tick+=100;p.process({inputBuffer:{getChannelData(){return new Float32Array(1024).fill(.06);}}});}
  recognizers[0].emit("partialresult",{partial:"hey how are you"});
  for(let i=0;i<8;i++){tick+=100;p.process({inputBuffer:{getChannelData(){return new Float32Array(1024);}}});}
  assert.equal(a.results.filter(x=>x.isFinal).length,1,"Turbo must submit after 650ms quiet");
  assert.equal(a.results.at(-1)[0].transcript,"hey how are you");
  assert.equal(streams[0].track.stopped,true,"stop releases microphone");
  assert.equal(downloads,1);
  unsupported=true;
  const b=await start();
  assert.equal(contexts.at(-1).sampleRate,undefined,"fallback uses normal interactive context");
  assert.equal(processors.at(-1).samples,1024,"fallback still uses fast audio blocks");
  recognizers.at(-1).emit("result",{text:"fallback working"});
  assert.equal(b.results.at(-1)[0].transcript,"fallback working");
  assert.equal(streams[1].track.stopped,true);
  assert.equal(downloads,1,"Turbo and device fallback reuse one Vosk model");
  assert.equal(ended,2);
  window.SwrlzLocalVoice.dispose();
  console.log("PASS: Turbo 16kHz/1024 samples, ~650ms post-speech submission, 48kHz fallback, one cached model");
})().catch(e=>{console.error(e);process.exitCode=1;});