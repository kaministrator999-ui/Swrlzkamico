"use strict";
// No network, browser, or real mic. Tests the exact local ASR adapter and
// persists a fake ~41MB archive through CacheStorage across model disposal.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const js=fs.readFileSync("voice-streaming-source/chat/§wyrlz/assets/local_voice_vosk.js","utf8");
(async()=>{
  const waitFor = async (ready, message) => {
    for (let i=0; i<100; i++) {
      if (ready()) return;
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.fail(message);
  };
  let now=1000, downloads=0, saved=0, modelLoads=0, terminations=0;
  let audioBuffers=0, opened=0, closed=0;
  const recognizers=[],processors=[],voices=[],tracks=[],cacheMap=new Map();
  const downloadedResponse={
    ok:true,type:"cors",
    clone(){return this;},
    async blob(){return {size:41116628};}
  };
  const window={
    caches:{async open(key){assert.equal(key,"swrlz-vosk-en-015-v1");return {
      async match(url){return cacheMap.get(url)||null;},
      async put(url,response){cacheMap.set(url,response);saved++;}
    };}},
    URL:{createObjectURL(blob){assert.equal(blob.size,41116628);return "blob:vosk-test-"+opened++;},
      revokeObjectURL(url){assert.ok(url.startsWith("blob:vosk-test-"));}},
    Vosk:{async createModel(url){
      assert.ok(url.startsWith("blob:vosk-test-"));
      modelLoads++;
      return {
        KaldiRecognizer:class {
          constructor(){this.listeners=new Map();this.removed=false;recognizers.push(this);}
          setWords(){}
          on(type,fn){this.listeners.set(type,fn);}
          emit(type,value){this.listeners.get(type)?.({result:value});}
          acceptWaveform(buf){assert.ok(buf.getChannelData);audioBuffers++;}
          remove(){this.removed=true;}
        },
        terminate(){terminations++;}
      };
    }},
    dispatchEvent(){},
    AudioContext:class {
      constructor(){this.state="running";this.destination={};}
      createScriptProcessor(){const p={connect(){},disconnect(){},onaudioprocess:null};processors.push(p);return p;}
      createMediaStreamSource(){return {connect(){},disconnect(){}};}
      createGain(){return {gain:{value:1},connect(){},disconnect(){}};}
      close(){closed++;return Promise.resolve();}
      resume(){return Promise.resolve();}
    }
  };
  const navigator={mediaDevices:{getUserMedia:async()=>{let track={ended:false,stop(){this.ended=true;}};tracks.push(track);return {getTracks:()=>[track]};}}};
  const DateFake=class extends Date {static now(){return now;}};
  const scope={window,navigator,Date:DateFake,console,
    setTimeout:()=>1,clearTimeout:()=>{},
    fetch:async url=>{assert.ok(url.includes("vosk-model-small-en-us-0.15.tar.gz"));downloads++;return downloadedResponse;},
    CustomEvent:class{constructor(type,options){this.type=type;this.detail=options?.detail;}}
  };
  vm.runInNewContext(js,scope);
  const Rec=window.SwrlzLocalSpeechRecognition;
  async function openRec(){
    const r=new Rec();r.results=[];r.onresult=e=>{r.results.push(e.results[0]);if(e.results[0].isFinal)r.stop();};
    r.start();
    await waitFor(() => window.SwrlzLocalVoice.active,
                  "Local mic not active after async archive/cache and model initialization");
    assert.equal(window.SwrlzLocalVoice.active,true,"mic captures after model ready");
    return r;
  }
  const first=await openRec();
  assert.equal(downloads,1,"first explicit opt-in downloads exactly once");
  assert.equal(saved,1,"one cache entry persists model");
  assert.equal(modelLoads,1);
  const p=processors.at(-1);
  const sendFrame=(amplitude,step=100)=>{
    now+=step;
    p.onaudioprocess?.({inputBuffer:{getChannelData(){return new Float32Array(256).fill(amplitude);}}});
  };
  for(let i=0;i<5;i++)sendFrame(.065);
  recognizers.at(-1).emit("partialresult",{partial:"hey how are you"});
  assert.equal(first.results.at(-1).isFinal,false,"partial transcript visible before submission");
  for(let i=0;i<18;i++)sendFrame(0);
  assert.equal(first.results.filter(x=>x.isFinal).length,1,"silence submits best partial even if Vosk never emits result");
  assert.equal(first.results.at(-1)[0].transcript,"hey how are you");
  assert.equal(tracks[0].ended,true);
  assert.equal(recognizers[0].removed,true);
  assert.equal(terminations,0,"Talk stop must not kill model");

  const second=await openRec();
  assert.equal(downloads,1,"second activation must not download");
  assert.equal(modelLoads,1,"same ready WASM model reused");
  recognizers.at(-1).emit("result",{text:"thanks"});
  assert.equal(second.results.at(-1)[0].transcript,"thanks");
  assert.equal(tracks[1].ended,true);
  window.SwrlzLocalVoice.dispose();
  for(let i=0;i<6;i++)await Promise.resolve();
  assert.equal(terminations,1,"only explicit model disposal terminates worker");

  const third=await openRec();
  assert.equal(downloads,1,"cached archive persists across model disposal/reinit");
  assert.equal(modelLoads,2,"only reinitialize WASM, no re-download");
  third.abort();
  assert.equal(tracks[2].ended,true);
  window.SwrlzLocalVoice.dispose();
  for(let i=0;i<6;i++)await Promise.resolve();
  assert.equal(terminations,2);
  assert.ok(audioBuffers>=15,"audio chunks actually reached Vosk");
  assert.ok(closed>=3,"AudioContext cleanup per turn");
  console.log("PASS: model cached, no repeated download, real audio buffers, partial->silence final, per-turn mic cleanup and explicit disposal");
})().catch(e=>{console.error(e);process.exitCode=1;});