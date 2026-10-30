import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto,randomBytes,createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const source=fs.readFileSync(fileURLToPath(new URL('../chat/§wyrlz/assets/forge-embed-v1.js',import.meta.url)),'utf8');
const CHAT='https://kamiloki-swyrlz.hf.space',FORGE='https://kamiloki-swrlz-forge-moba.static.hf.space';
const protocol='swrlz-forge-chat-v1',hostId='host_01234567890123456789',channelId='chan_01234567890123456789';
const pairId='a'.repeat(32),leaseId='b'.repeat(32),projectId='c'.repeat(32),uploadId='d'.repeat(32);
const bearer='sfe1_PRIVATE_FIXTURE_NOT_FOR_PARENT';
const hash=value=>createHash('sha256').update(new Uint8Array(value)).digest('hex');
const flush=async()=>{for(let i=0;i<12;i++)await new Promise(resolve=>setImmediate(resolve));};

function fixture({framed=true,query='?forgeEmbed=1',presenceErrors=[],onPresence=()=>{}}={}){
  const listeners=new Map(),timers=new Map(),requests=[],windowMessages=[],portMessages=[],events=[];
  let nextTimer=0,upload=null,parts=[],project=null,rawLoaded=new TextEncoder().encode('{"engine":"§E","version":1,"project":{},"editor":{},"scene":{}}');
  const parent={postMessage:(data,target)=>windowMessages.push({data,target})};
  const doc={visibilityState:'visible',documentElement:{classList:{add(){}}},addEventListener(){}};
  const win={parent,addEventListener:(name,fn)=>{const all=listeners.get(name)||[];all.push(fn);listeners.set(name,all);},dispatchEvent:event=>{events.push(event);for(const fn of listeners.get(event.type)||[])fn(event);}};
  if(!framed)win.parent=win;
  const nativeFetch=async(input,init={})=>{
    const url=new URL(input instanceof Request?input.url:input,CHAT),headers=new Headers(init.headers||{});
    requests.push({url:url.href,init:{...init,headers},body:init.body});
    const path=url.pathname,body=typeof init.body==='string'?JSON.parse(init.body):null;
    const response=(value,status=200)=>new Response(JSON.stringify(value),{status,headers:{'Content-Type':'application/json'}});
    if(path==='/api/forge/embed/pair')return response({pairId,loginUrl:'/forge/login?pairId='+pairId,expiresAt:Date.now()/1000+300,recoveryCode:'b'.repeat(12)});
    if(path==='/api/forge/embed/pair/'+pairId)return response({approved:true});
    if(path==='/api/forge/embed/pair/exchange')return response({token:bearer,expiresAt:Date.now()/1000+3600,parentOrigin:FORGE,hostId,channelId,user:{id:'google:private',displayName:'Fixture User'}});
    if(path==='/api/forge/embed/presence')return response({ticket:'sfp1_PRIVATE_PRESENCE',hostId,channelId,threadId:body.threadId,projectId:body.projectId});
    if(path==='/api/forge/projects/uploads'){
      upload=body;parts=[];return response({uploadId,projectId,partBytes:524288,parts:Math.ceil(body.encodedBytes/524288)});
    }
    if(path.startsWith('/api/forge/projects/uploads/'+uploadId+'/parts/')){
      const index=Number(path.split('/').at(-1));parts[index]=init.body;
      return response({index,confirmed:true});
    }
    if(path==='/api/forge/projects/uploads/'+uploadId+'/commit'){
      project={id:projectId,name:upload.name,revision:1,rawSha256:upload.rawSha256,rawBytes:upload.rawBytes};return response({project,durable:true});
    }
    if(path==='/api/forge/projects')return response({projects:project?[project]:[],limits:{}});
    if(path==='/api/forge/projects/'+projectId)return new Response(rawLoaded,{headers:{'X-SWRLZ-Project-Revision':'1','X-SWRLZ-Project-SHA256':hash(rawLoaded)}});
    return response({ok:true,user:{id:'google:private'}});
  };
  win.fetch=nativeFetch;
  const context=vm.createContext({window:win,document:doc,location:new URL('/'+query,CHAT),crypto:webcrypto,URL,URLSearchParams,Headers,Request,Response,TextEncoder,TextDecoder,ArrayBuffer,Uint8Array,Blob,CompressionStream,CustomEvent:class{constructor(type,{detail}){this.type=type;this.detail=detail;}},btoa:s=>Buffer.from(s,'binary').toString('base64'),setTimeout:(fn,ms)=>{const key=++nextTimer;timers.set(key,{fn,ms});return key;},clearTimeout:key=>timers.delete(key),console});
  vm.runInContext(source,context);
  const envelope=(type,payload={},requestId='request-1')=>({protocol,hostId,channelId,type,payload,requestId});
  const windowEvent=(data,origin=FORGE,eventSource=parent,ports=[])=>{for(const fn of listeners.get('message')||[])fn({data,origin,source:eventSource,ports});};
  const port={start(){},postMessage(data,transfer){
    portMessages.push({data,transfer});
    if(data.type==='host.context')queueMicrotask(()=>port.onmessage({data:envelope('rpc.result',{ok:true,result:{projectId:'native-project',context:{mode:'edit',epoch:'1',meshes:[]}}},data.requestId)}));
    if(data.type==='host.presence'){
      onPresence();const failure=presenceErrors.shift();
      queueMicrotask(()=>port.onmessage({data:envelope('rpc.result',failure?{ok:false,error:failure}:{ok:true,result:{leaseId}},data.requestId)}));
    }
  }};
  const connect=()=>{windowEvent(envelope('host.hello'));windowEvent(envelope('host.connect'),FORGE,parent,[port]);};
  const request=async(type,payload={},requestId='rpc-'+Math.random())=>{
    await port.onmessage({data:envelope(type,payload,requestId)});await flush();
    return portMessages.findLast(item=>item.data.type==='rpc.result'&&item.data.requestId===requestId)?.data.payload;
  };
  const pair=async()=>{
    const result=await request('account.signIn');assert.equal(result.ok,true);assert.equal(result.result.pairId,pairId);
    const timer=[...timers].find(([,item])=>item.ms===1200);assert.ok(timer);timers.delete(timer[0]);timer[1].fn();await flush();
    assert.ok(events.some(event=>event.type==='swrlz-forge-account-changed'&&event.detail.signedIn));
  };
  return {win,parent,doc,windowEvent,envelope,connect,request,pair,port,requests,windowMessages,portMessages,timers,events,get upload(){return upload;},get parts(){return parts;},setRaw:raw=>{rawLoaded=raw;}};
}

{
  const f=fixture();
  assert.equal((await f.win.fetch('/api/lalm_station/sync')).status,401,'an embedded frame cannot silently use an ambient cookie owner');
  assert.equal(f.requests.length,0);
  f.windowEvent(f.envelope('host.hello'),'https://evil.example');
  f.windowEvent(f.envelope('host.hello'),FORGE,{});
  assert.equal(f.windowMessages.length,0,'origin and exact parent window are required');
  f.windowEvent(f.envelope('host.hello'));
  assert.equal(f.windowMessages[0].data.type,'iframe.ready');
  f.windowEvent({...f.envelope('host.connect'),channelId:'wrong_01234567890123456789'},FORGE,f.parent,[f.port]);
  assert.equal(f.portMessages.length,0,'an incorrect channel cannot attach a port');
  f.windowEvent(f.envelope('host.connect'),FORGE,f.parent,[f.port]);
  await f.pair();
  await f.win.fetch('/api/lalm_station/stream?requestId=test');
  await f.win.fetch(new Request(CHAT+'/api/account/profile'));
  await f.win.fetch('/api/github/status');
  await f.win.fetch('/api/chatgpt_archive/list');
  for(const request of f.requests.filter(item=>/\/api\/(lalm_station|account\/profile|github\/status|chatgpt_archive)/.test(item.url))){
    assert.equal(request.init.headers.get('Authorization'),'Bearer '+bearer);assert.equal(request.init.credentials,'omit');
  }
  await f.win.fetch('https://github.com/api/account/profile');
  await f.win.fetch('/chat/§wyrlz/assets/kompanion.png');
  await f.win.fetch('/api/account/status');
  for(const request of f.requests.slice(-3))assert.equal(request.init.headers.get('Authorization'),null,'credentials attach only to exact protected Chat APIs');
  assert.ok(!JSON.stringify([...f.windowMessages,...f.portMessages]).includes(bearer),'the parent never receives the account credential');
  const before=await f.win.SwrlzForgeEmbedV1.beforeSend('thread-1');assert.equal(before.forgeLeaseId,leaseId);
  const event={type:'FORGE_BATCH_READY',batchId:'e'.repeat(32),leaseId,threadId:'thread-1',generationId:'gen-1',projectId:'native-project'};
  f.win.SwrlzForgeEmbedV1.forwardBatch({...event,leaseId:'0'.repeat(32)});
  f.win.SwrlzForgeEmbedV1.forwardBatch(event);f.win.SwrlzForgeEmbedV1.forwardBatch(event);
  assert.equal(f.portMessages.filter(item=>item.data.type==='host.batch').length,1,'only a matching live batch is forwarded once');
  await f.port.onmessage({data:f.envelope('host.inactive',{reason:'closed'})});
  f.win.SwrlzForgeEmbedV1.forwardBatch({...event,batchId:'f'.repeat(32)});
  assert.equal(f.portMessages.filter(item=>item.data.type==='host.batch').length,1,'closing the host revokes forwarding');
  const raw=new TextEncoder().encode(JSON.stringify({engine:'§E',version:'native',project:{geometry:randomBytes(1200000).toString('base64')},editor:{},scene:{}}));
  const saved=await f.request('cloud.save',{bytes:raw.buffer,name:'Native geometry',expectedRevision:0});
  assert.equal(saved.ok,true);assert.equal(saved.result.durable,true);assert.equal(f.upload.rawSha256,hash(raw));assert.ok(f.parts.length>1,'native data is uploaded in bounded parts');
  assert.ok(f.parts.every(part=>part.byteLength<=524288));
  f.setRaw(raw);
  const loaded=await f.request('cloud.load',{projectId});assert.equal(loaded.ok,true);assert.deepEqual(new Uint8Array(loaded.result.bytes),raw,'load preserves every native UTF8 byte');
  assert.equal(loaded.result.project.name,'Native geometry');
  await f.win.fetch('/api/account/logout',{method:'POST'});
  assert.equal(f.requests.at(-1).url,CHAT+'/api/forge/embed/logout','embedded logout does not sign out the standalone account');
  assert.equal((await f.win.fetch('/api/lalm_station/sync')).status,401);
}

{
  const retry=fixture({presenceErrors:['EDITOR_CONTEXT_CHANGED']});retry.connect();await retry.pair();
  assert.equal((await retry.win.SwrlzForgeEmbedV1.beforeSend('new-project-thread')).forgeLeaseId,leaseId);
  assert.equal(retry.portMessages.filter(item=>item.data.type==='host.context').length,2,'stale activation uses a fresh native snapshot');
  assert.equal(retry.requests.filter(item=>item.url.endsWith('/embed/presence')).length,2,'every retry obtains a fresh one-use presence ticket');
  const repeated=fixture({presenceErrors:Array(3).fill('EDITOR_CONTEXT_CHANGED')});repeated.connect();await repeated.pair();
  await assert.rejects(repeated.win.SwrlzForgeEmbedV1.beforeSend('thread'),/EDITOR_CONTEXT_CHANGED/);
  assert.equal(repeated.portMessages.filter(item=>item.data.type==='host.context').length,3,'retries are bounded');
  const detached=fixture({presenceErrors:['EDITOR_PANEL_CLOSED']});detached.connect();await detached.pair();
  await assert.rejects(detached.win.SwrlzForgeEmbedV1.beforeSend('thread'),/EDITOR_PANEL_CLOSED/);
  assert.equal(detached.portMessages.filter(item=>item.data.type==='host.context').length,1,'other errors never retry');
  const hidden=fixture({onPresence:()=>{hidden.doc.visibilityState='hidden';}});hidden.connect();await hidden.pair();
  await assert.rejects(hidden.win.SwrlzForgeEmbedV1.beforeSend('thread'),/connection changed/,'a hidden editor cannot finish activation');
}

{
  const standalone=fixture({framed:false});
  await standalone.win.fetch('/api/lalm_station/sync');
  assert.equal(standalone.requests.length,1);assert.equal(standalone.requests[0].init.headers.get('Authorization'),null);
  assert.deepEqual(Object.keys(await standalone.win.SwrlzForgeEmbedV1.beforeSend('thread')),[],'a standalone URL flag grants no editor tools');
  const unrelatedFrame=fixture({query:''});
  unrelatedFrame.connect();assert.equal(unrelatedFrame.windowMessages.length,0,'ordinary framed Chat does not accept editor connections');
}

const html=fs.readFileSync(fileURLToPath(new URL('../chat/§wyrlz/index.html',import.meta.url)),'utf8');
for(const match of html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
const popup=fs.readFileSync(fileURLToPath(new URL('../chat/§wyrlz/forge-connect.html',import.meta.url)),'utf8');
for(const match of popup.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
assert.match(html,/defaultModel:settingsState\.model\.defaultModel/,'explicit settings save includes selected inference model');
assert.match(html,/settingsSave\.disabled=!chatAccountUser\|\|!accountProfileAvailable/,'an available version0 profile can be saved explicitly');
console.log('PASS: strict frame identity, private account transport, scoped actions/revocation, multipart native project roundtrip, settings bootstrap and script syntax');
