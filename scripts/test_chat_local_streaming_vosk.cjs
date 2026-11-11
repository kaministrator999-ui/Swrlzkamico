"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const code = fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/local_voice_vosk.js", "utf8");
(async () => {
  let now=1000, nextTimer=1, loads=0, terminations=0, waveformChunks=0, flushes=0;
  const timers=new Map(), recognizers=[], processors=[], tracks=[];
  const schedule=(fn,ms=0)=>{const id=nextTimer++;timers.set(id,{due:now+ms,fn});return id;};
  const advance=ms=>{
    now+=ms;
    for(let guard=0;guard<40;guard++){
      const due=[...timers.entries()].filter(([,x])=>x.due<=now).sort((a,b)=>a[1].due-b[1].due);
      if(!due.length)return;
      for(const [id,x] of due){if(timers.delete(id))x.fn();}
    }
    assert.fail("Timer recursion");
  };
  const model={
    KaldiRecognizer:class{
      constructor(sampleRate){assert.equal(sampleRate,48000);this.listeners=new Map();recognizers.push(this);}
      on(type,fn){this.listeners.set(type,fn);}
      setWords(){}
      acceptWaveform(){waveformChunks++;}
      emit(type,result){this.listeners.get(type)?.({result});}
      retrieveFinalResult(){flushes++;schedule(()=>this.emit("result",{text:this.finalText||""}),400);}
      remove(){this.removed=true;}
    },
    terminate(){terminations++;}
  };
  const window={
    Vosk:{async createModel(){loads++;return model;}},
    dispatchEvent(){},
    AudioContext:class{
      constructor(){this.sampleRate=48000;this.state="running";this.destination={};}
      createScriptProcessor(size){
        assert.equal(size,4096);
        const processor={onaudioprocess:null,connect(){},disconnect(){}};
        processors.push(processor);return processor;
      }
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{async getUserMedia({audio}){
    assert.equal(audio.sampleRate,undefined);
    assert.equal(audio.autoGainControl,true);
    const track={stopped:false,stop(){this.stopped=true;}};
    tracks.push(track);return {getTracks:()=>[track]};
  }}};
  const ClockDate=class extends Date{static now(){return now;}};
  vm.runInNewContext(code,{window,navigator,Date:ClockDate,console,
    setTimeout:schedule,clearTimeout:id=>timers.delete(id),
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}}
  });
  async function waitForMic(){
    for(let i=0;i<100&&!window.SwrlzLocalVoice.active;i++)
      await new Promise(resolve=>setTimeout(resolve,5));
    assert.ok(window.SwrlzLocalVoice.active);
  }
  const rec=new window.SwrlzLocalSpeechRecognition();
  let ended=0;
  const text=[];
  rec.onresult=event=>{
    const result=event.results[0];
    text.push({final:result.isFinal,text:result[0].transcript});
    if(result.isFinal)rec.stop();
  };
  rec.onend=()=>ended++;
  rec.start();await waitForMic();
  assert.equal(loads,1);
  function frames(n,amplitude){
    for(let i=0;i<n;i++){
      now+=100;
      processors.at(-1).onaudioprocess({inputBuffer:{getChannelData(){
        return new Float32Array(4096).fill(amplitude);
      }}});
      advance(0);
    }
  }
  frames(5,.03);
  recognizers[0].emit("partialresult",{partial:"hey how"});
  recognizers[0].emit("result",{text:"hey how"});
  assert.equal(text.at(-1).text,"hey how","matching partial and result must retain words");
  assert.equal(text.filter(x=>x.final).length,0,"Vosk phrase end must not trigger send");
  recognizers[0].finalText="are you";
  frames(24,0);
  assert.equal(flushes,1,"silence flushes worker");
  assert.equal(text.filter(x=>x.final).length,0);
  advance(401);advance(551);
  assert.equal(text.at(-1).text,"hey how are you");
  assert.equal(text.at(-1).final,true);
  assert.equal(ended,1);
  assert.equal(tracks[0].stopped,true);
  assert.equal(recognizers[0].removed,true);
  const second=new window.SwrlzLocalSpeechRecognition();
  second.start();await waitForMic();
  assert.equal(loads,1,"cache ready model across turns");
  second.abort();
  assert.equal(tracks[1].stopped,true);
  window.SwrlzLocalVoice.dispose();
  for(let i=0;i<5;i++)await Promise.resolve();
  assert.equal(terminations,1);
  assert.ok(waveformChunks>=25);
  console.log("PASS: local speech retained until final flush, phrase preservation, mic teardown and model reuse");
})().catch(error=>{console.error(error);process.exitCode=1;});
