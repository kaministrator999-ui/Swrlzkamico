import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {webcrypto} from 'node:crypto';

const source=fs.readFileSync(new URL('../runtime/chat_account_panel_v1.js',import.meta.url),'utf8');
const bridge=source.slice(source.indexOf('/* ATELIER_BRIDGE_START */'),source.indexOf('/* ATELIER_BRIDGE_END */'));
const initial=()=>({id:'mesh-one',name:'Original exact name',kind:'sphere',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color:'#ffffff',material:'matte',group:'Custom'});
let data={parts:[initial()]},selection='mesh-one',undo=[],redo=[],dirtyCount=0;
const describe=()=>JSON.parse(JSON.stringify(data));
const native={crypto:webcrypto,model:()=>data,panel:{hidden:false},MODEL_ATELIER_LIMIT:10,checkPart:()=>true,
 partById:id=>data.parts.find(p=>p.id===id),checkpoint:()=>{undo.push(describe());redo=[];},
 signalEdited:()=>dirtyCount++,select:id=>{selection=id;},
 addPart:()=>{undo.push(describe());const p=structuredClone(data.parts.find(p=>p.id===selection));p.id='copied';p.name+=' copy';data.parts.push(p);selection=p.id;dirtyCount++;},
 removePart:()=>{undo.push(describe());data.parts=data.parts.filter(p=>p.id!==selection);selection=null;dirtyCount++;},
 historyStep:back=>{const from=back?undo:redo,to=back?redo:undo;to.push(describe());data=from.pop();selection=null;dirtyCount++;},
 get selection(){return selection;},set selection(v){selection=v;},get undo(){return undo;},get redo(){return redo;}
};
const nativeVM=vm.createContext(native);vm.runInContext(bridge,nativeVM);
const nativeAction=op=>JSON.parse(JSON.stringify(nativeVM.seChatAtelierApply(op)));
const edited=nativeAction({op:'mesh.set',id:'mesh-one',name:'Use This EXACT Text §§',color:'#ff00aa',position:[2,3,4]});
assert.equal(edited.name,'Use This EXACT Text §§');assert.equal(undo.length,1,'one atomic native checkpoint for multi-field edit');
assert.equal(edited.color,'#ff00aa');assert.deepEqual(edited.position,[2,3,4]);
nativeAction({op:'editor.undo'});assert.equal(data.parts[0].name,'Original exact name');
nativeAction({op:'editor.redo'});assert.equal(data.parts[0].name,'Use This EXACT Text §§');
const added=nativeAction({op:'mesh.add',kind:'box',name:'Independent box',scale:[.5,.5,.5]});
assert.equal(data.parts.length,2);assert.equal(added.kind,'box');
nativeAction({op:'mesh.remove',id:added.id});assert.equal(data.parts.length,1);
assert.throws(()=>nativeAction({op:'mesh.remove',id:'mesh-one'}),/KEEP_ONE_MESH/);
assert.throws(()=>nativeAction({op:'mesh.set',id:'nonexistent',name:'bad'}),/MESH_NOT_FOUND/);
assert(dirtyCount>=5);

const elements=new Map();
for(const key of ['modelAtelierUndo','modelAtelierRedo','undoBtn','redoBtn','seChatToggle','seChatClose'])elements.set(key,{disabled:false,focus(){},setAttribute(){}});
const frameWindow={posted:[],postMessage(...args){this.posted.push(args);}};
const fakeFrame={contentWindow:frameWindow};
const requests=[],messages=[];
let responseForRequest=()=>({});
const ctx={console,crypto:webcrypto,TextEncoder,TextDecoder,URL,URLSearchParams,ArrayBuffer,Uint8Array,structuredClone,WeakMap,Map,Set,
 setTimeout:()=>99,clearTimeout(){},queueMicrotask(){},
 document:{hidden:false,getElementById:key=>elements.get(key),addEventListener(){},head:{append(){}},body:{append(){}}},
 location:{origin:'https://kamiloki-swrlz-forge-moba.static.hf.space'},window:{addEventListener(){},SWYRL_ENGINE_AGENT:{}},
 currentProject:{name:'Test project',kind:'model-atelier',modelAtelier:data},actors:[],selected:null,playing:false,simulating:false,historyIndex:0,
 ModelAtelier:{status:()=>({open:true,selected:selection}),chatAction:op=>nativeAction(op)},
 markDirty(){dirtyCount++;},loadProject(p){ctx.currentProject=p.project;return true;},
 fetch:async(url,options)=>{const body=JSON.parse(options.body);requests.push({url,body,headers:options.headers});return {ok:true,json:async()=>responseForRequest(url,body)};},
 MessageChannel:class{constructor(){this.port1={postMessage:m=>messages.push(m),start(){},close(){}};this.port2={};}},
};
ctx.window.window=ctx.window;
const host=source.slice(source.indexOf('/* ATELIER_BRIDGE_END */')+'/* ATELIER_BRIDGE_END */'.length);
const anchor='if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(mount);';
assert.equal(host.split(anchor).length,2);
const hooks=`globalThis.__test={context,validateOperation,execute,applyBatch,handshake,receive,revoke,heartbeat,
 seed(options){if(options.lease!==undefined)lease=options.lease;if(options.panel!==undefined)panel=options.panel;if(options.frame!==undefined)frame=options.frame;if(options.port!==undefined)port=options.port;if(options.open!==undefined)open=options.open;if(options.lastContext!==undefined)lastContext=options.lastContext;status={dataset:{}};accountText={};},
 state:()=>({lease,port,ready,lastContext}),ids:()=>({hostId,channelId})};`;
vm.createContext(ctx);vm.runInContext(host.replace(anchor,hooks),ctx);
const api=ctx.__test, first=api.context();
assert.equal(first.meshes[0].id,'mesh-one');assert.equal(first.mode,'edit');assert.equal(first.workspace,'model-atelier');
api.validateOperation({op:'mesh.set',id:'mesh-one',name:'Exact §§'},first);
for(const op of [
 {op:'eval',code:'alert(1)'},{op:'mesh.set',id:'mesh-one',code:'alert(1)'},
 {op:'mesh.add',kind:'script'},{op:'mesh.set',id:'mesh-one',position:[NaN,0,0]},
 {op:'mesh.set',id:'mesh-one',scale:[0,1,1]},{op:'mesh.set',id:'forged',name:'x'},
 {op:'sceneactor.add',prefab:'wall'},{op:'mesh.set',id:'mesh-one'},
 {op:'mesh.add',kind:'box',name:'x',url:'https://attacker.invalid'},
 {op:'mesh.set',id:'mesh-one',material:'untrusted'}
])assert.throws(()=>api.validateOperation(op,first));
assert.throws(()=>api.validateOperation({op:'mesh.set',id:'mesh-one',name:'x'},{...first,mode:'play'}),/STOP_PLAY/);
const epochBefore=api.context().epoch;ctx.markDirty();assert.equal(api.context().epoch,epochBefore+1);

const bind=api.ids(), envelope=(type,payload,requestId='requestid123456789')=>({protocol:'swrlz-forge-chat-v1',...bind,type,requestId,payload});
api.seed({frame:fakeFrame,panel:{hidden:false},open:true});
api.handshake({origin:'https://attacker.invalid',source:frameWindow,data:envelope('iframe.ready',{})});
api.handshake({origin:'https://kamiloki-swyrlz.hf.space',source:{},data:envelope('iframe.ready',{})});
api.handshake({origin:'https://kamiloki-swyrlz.hf.space',source:frameWindow,data:{...envelope('iframe.ready',{}),hostId:'wrong'}});
assert.equal(api.state().port,null,'wrong origin/source/binding must not create a port');
api.handshake({origin:'https://kamiloki-swyrlz.hf.space',source:frameWindow,data:envelope('iframe.ready',{})});
assert.equal(api.state().ready,true);assert.equal(frameWindow.posted.length,1);

let publicContext=JSON.parse(JSON.stringify(api.context()));
responseForRequest=(url)=>url.endsWith('/activate')?{leaseId:'lease111',hostToken:'sfh1_PRIVATE',heartbeatSeconds:5}:{};
api.seed({lastContext:publicContext});
await api.receive(envelope('host.presence',{ticket:'sfp1_ticket',...bind,threadId:'thread-one',projectId:publicContext.projectId}));
assert.equal(api.state().lease?.leaseId,'lease111','fresh context must survive retiring an old lease');
assert(!JSON.stringify(messages).includes('sfh1_PRIVATE'),'host capability must never cross to the Chat iframe');
assert.equal(requests.at(-1).headers['X-Swrlz-Forge-Host'],undefined,'activation sends only one-use presence ticket');

publicContext=JSON.parse(JSON.stringify(api.context()));
const operation={op:'mesh.set',id:'mesh-one',name:'Successfully applied exact text'};
responseForRequest=(url)=>url.endsWith('/take')?{batchId:'batch1',operations:[operation],receiptNonce:'sfr1_private',preconditions:{leaseId:'lease111',threadId:'thread-one',projectId:publicContext.projectId,generationId:'gen-one',context:publicContext}}:{};
await api.applyBatch({batchId:'batch1',leaseId:'lease111',generationId:'gen-one'});
assert.equal(data.parts[0].name,'Successfully applied exact text');
assert.equal(requests.at(-1).body.results[0].ok,true);
const count=requests.length;await api.applyBatch({batchId:'batch1',leaseId:'lease111',generationId:'gen-one'});assert.equal(requests.length,count,'batch replay is not executed');

publicContext=JSON.parse(JSON.stringify(api.context()));
responseForRequest=(url)=>url.endsWith('/take')?{batchId:'batch-stale',operations:[{...operation,name:'Must not apply'}],receiptNonce:'sfr1_private',preconditions:{leaseId:'lease111',threadId:'thread-one',projectId:publicContext.projectId,generationId:'gen-two',context:{...publicContext,epoch:publicContext.epoch-1}}}:{};
await api.applyBatch({batchId:'batch-stale',leaseId:'lease111',generationId:'gen-two'});
assert.equal(data.parts[0].name,'Successfully applied exact text');
assert.equal(requests.at(-1).body.results[0].ok,false,'stale snapshot must return truthful failure');
api.revoke('test closure');assert.equal(api.state().lease,null);
const n=requests.length;await api.applyBatch({batchId:'outside',leaseId:'lease111',generationId:'gen-three'});assert.equal(requests.length,n);
assert(!JSON.stringify(messages).includes('sfr1_private'));
console.log(JSON.stringify({ok:true,suite:'chat-account-panel-cpu-v1',checks:['native mesh exact text + atomic checkpoint + undo/redo + add/remove','typed operation bounds and injected-code denial','origin/source/channel handshake','host-private credential','presence activation fresh context','native receipts and replay denial','stale/closed host denial']}));
