"use strict";
/* Reproduce late Vosk worker output on short/fast and slow multi-phrase speech.
 * Workers process audio asynchronously; local STT must not send a partial
 * before retrieveFinalResult() flushes queued audio.
 */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const source=fs.readFileSync("voice-turbo-source/chat/§wyrlz/assets/local_voice_vosk.js","utf8");

(async()=>{
  const waitFor=async ready=>{for(let i=0;i<100;i++){if(ready())return;await new Promise(done=>setTimeout(done,10));}assert.fail("Microphone never ready");};
  let now=1000, nextTimer=1, sampleRate=48000, loads=0, framesDecoded=0, workerFinalizations=0;
  let fallbackNative=false;
  const timers=new Map(),contexts=[],processors=[],recognizers=[],tracks=[],constraintsSeen=[];
  const setClockTimeout=(fn,ms)=>{
    const id=nextTimer++;timers.set(id,{fn,due:now+ms});return id;
  };
  const advance=ms=>{
    now+=ms;
    for(let guard=0;guard<30;guard++){
      const ready=[...timers.entries()].filter(([,t])=>t.due<=now).sort((a,b)=>a[1].due-b[1].due);
      if(!ready.length)return;
      for(const [id,t] of ready){if(!timers.has(id))continue;timers.delete(id);t.fn();}
    }
    assert.fail("recursive timer loop");
  };
  const model={
    KaldiRecognizer:class{
      constructor(rate){assert.equal(rate,sampleRate);this.handlers=new Map();this.removed=false;this.queuedFinal="";recognizers.push(this);}
      on(type,fn){this.handlers.set(type,fn);}
      setWords(){}
      acceptWaveform(input){assert.ok(input.getChannelData);framesDecoded++;}
      emit(type,result){this.handlers.get(type)?.({result});}
      retrieveFinalResult(){
        workerFinalizations++;
        // Simulate worker backlog. The first partial was incomplete, but the
        // queued audio has the remaining words. Return the actual complete
        // trailing result only after worker processing.
        setClockTimeout(()=>this.emit("result",{text:this.queuedFinal}),400);
      }
      remove(){this.removed=true;}
    },
    terminate(){}
  };
  const window={
    Vosk:{async createModel(){loads++;return model;}},
    dispatchEvent(){},
    AudioContext:class{
      constructor(opts){
        if(fallbackNative&&opts?.latencyHint)throw Error("No interactive context");
        this.sampleRate=sampleRate;this.destination={};this.state="running";
        contexts.push(opts||{});
      }
      createScriptProcessor(n){
        const p={size:n,onaudioprocess:null,connect(){},disconnect(){}};
        processors.push(p);return p;
      }
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{async getUserMedia(constraints){
    constraintsSeen.push(constraints);
    const track={stopped:false,stop(){this.stopped=true;}};
    tracks.push(track);return {getTracks(){return [track];}};
  }}};
  const FakeDate=class extends Date{static now(){return now;}};
  vm.runInNewContext(source,{window,navigator,Date:FakeDate,console,
    setTimeout:setClockTimeout,clearTimeout:id=>timers.delete(id),
    CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail;}}
  });
  const Recognition=window.SwrlzLocalSpeechRecognition;
  async function begin(){
    const recognizer=new Recognition();recognizer.turbo=true;recognizer.messages=[];
    recognizer.onresult=event=>{
      const result=event.results[0];
      recognizer.messages.push({final:result.isFinal,text:result[0].transcript});
      if(result.isFinal)recognizer.stop();
    };
    recognizer.start();await waitFor(()=>window.SwrlzLocalVoice.active);
    return recognizer;
  }
  const speak=(n,amplitude=.009,ms=100)=>{
    for(let i=0;i<n;i++){
      now+=ms;
      processors.at(-1).onaudioprocess?.({
        inputBuffer:{getChannelData(){return new Float32Array(2048).fill(amplitude);}}
      });
      advance(0);
    }
  };
  const finals=rec=>rec.messages.filter(x=>x.final);

  const first=await begin();
  assert.equal(contexts[0].latencyHint,"interactive");
  assert.equal(contexts[0].sampleRate,undefined,"native device sample rate");
  assert.equal(constraintsSeen[0].audio.sampleRate,undefined,"Turbo must not force 16kHz mic capture");
  assert.equal(processors[0].size,2048);
  speak(8);
  recognizers.at(-1).emit("partialresult",{partial:"hello"});
  speak(7,0);
  assert.equal(finals(first).length,0,"fast speaker's brief pause is not send");
  speak(11,0);
  assert.equal(workerFinalizations,1,"sustained quiet requests final worker decode");
  assert.equal(finals(first).length,0,"latest partial cannot submit immediately");
  recognizers.at(-1).queuedFinal="hello how are you";
  advance(400);
  assert.equal(finals(first).length,0,"late final must settle before delivery");
  advance(551);
  assert.equal(finals(first).length,1);
  assert.equal(finals(first)[0].text,"hello how are you","short phrase must include trailing words");
  assert.equal(tracks[0].stopped,true);

  sampleRate=44100;fallbackNative=true;
  const second=await begin();
  assert.equal(contexts.at(-1).sampleRate,undefined);
  assert.equal(constraintsSeen.at(-1).audio.sampleRate,undefined,"fallback remains native mic capture");
  speak(5,.009);
  recognizers.at(-1).emit("result",{text:"well"});
  speak(10,0);
  assert.equal(finals(second).length,0,"normal speaking pause must not send");
  speak(5,.009);
  recognizers.at(-1).emit("partialresult",{partial:"i think"});
  speak(18,0);
  assert.equal(finals(second).length,0);
  assert.equal(workerFinalizations,2);
  recognizers.at(-1).queuedFinal="we should test that";
  advance(401);
  advance(551);
  assert.equal(finals(second).length,1);
  assert.equal(finals(second)[0].text,"well we should test that","worker final replaces provisional incomplete partial");
  assert.equal(tracks[1].stopped,true);
  // If a worker does not answer its explicit final-flush request, its old
  // provisional partial must NOT be silently sent as an incomplete message.
  const third=await begin();
  speak(6,.009);
  recognizers.at(-1).emit("partialresult",{partial:"hello how"});
  // Suppress the worker response: simulated decoding timeout.
  recognizers.at(-1).retrieveFinalResult=function(){workerFinalizations++;};
  speak(18,0);
  assert.equal(finals(third).length,0);
  advance(2601);
  assert.equal(finals(third).length,0,"never commit incomplete partial on worker timeout");
  third.abort();
  assert.equal(tracks[2].stopped,true);
  assert.equal(loads,1,"cached Vosk model reused");
  assert.ok(framesDecoded>20);
  window.SwrlzLocalVoice.dispose();
  console.log("PASS: Turbo retains short and slow utterances until the asynchronous Vosk final-result flush, without early sends");
})().catch(err=>{console.error(err);process.exitCode=1;});