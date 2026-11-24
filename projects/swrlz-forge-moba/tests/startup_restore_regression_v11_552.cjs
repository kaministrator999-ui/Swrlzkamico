'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'../runtime');
const start=fs.readFileSync(path.join(root,'engine_account_start_v11_476.js'),'utf8');
const bridge=fs.readFileSync(path.join(root,'engine_account_bridge_v11_476.js'),'utf8');
const boot=fs.readFileSync(path.join(root,'user_project_default_boot_v11_184.js'),'utf8');
for(const [name,js] of [['startup',start],['bridge',bridge],['default',boot]])
 new vm.Script(js,{filename:name});
function fixture(defaultState,api){
 const events=new Map(),nodes=new Map(),timers=[];
 const add=(map,type,listener)=>{if(!map.has(type))map.set(type,[]);map.get(type).push(listener);};
 function element(id){
  if(!nodes.has(id)){
   const el={id,hidden:false,value:'',textContent:'',dataset:{},checked:false,options:[],listeners:new Map(),
    addEventListener(type,fn){add(this.listeners,type,fn)},
    replaceChildren(...items){this.options=[...items];this.value=''},
    append(child){this.options.push(child)},
    focus(){},setAttribute(){},querySelector(){return null}};
   nodes.set(id,el);
  }
  return nodes.get(id);
 }
 const document={readyState:'complete',hidden:false,body:element('body'),
  documentElement:{dataset:{}},getElementById:id=>element(id),
  createElement:tag=>element('created-'+tag+'-'+nodes.size),
  addEventListener(type,fn){add(events,'doc:'+type,fn)},
  dispatchEvent(e){for(const fn of events.get('doc:'+e.type)||[])fn(e)}};
 // Startup defaults and last sessions must remain read-only during recovery.
 const store=new Map();
 const window={SWYRL_ENGINE_SAVED_DEFAULT:defaultState,SWYRL_ENGINE_STARTUP_ACCOUNT_476:api,
  addEventListener(type,fn){add(events,type,fn)},
  dispatchEvent(e){for(const fn of events.get(e.type)||[])fn(e)},
  SWYRL_ENGINE_STUDIOS:{active:()=> 'modeler',change:()=>{}},
  SWYRL_ENGINE_WORKSPACES:{active:()=> 'game'}};
 const context=vm.createContext({window,document,
  localStorage:{getItem:key=>store.get(key)||null,setItem:(key,v)=>store.set(key,v)},
  MutationObserver:class{observe(){}disconnect(){}},
  CustomEvent:class{constructor(type,opts){this.type=type;this.detail=opts?.detail}},
  queueMicrotask,setTimeout:(fn,ms)=>{timers.push({fn,ms});return timers.length},
  clearTimeout:()=>{},Date,JSON,Object,Array,String,Promise,console});
 vm.runInContext(start,context,{timeout:1000});
 return {window,document,element,store,timers,
  event:(type,detail)=>window.dispatchEvent({type,detail}),
  click:id=>{const node=element(id);for(const fn of node.listeners.get('click')||[])fn({target:node})}};
}
const flush=async()=>{for(let i=0;i<15;i++)await Promise.resolve()};
(async()=>{
 const receipt={attempted:true,source:'cloud',pending:true,success:null};
 const pref={read:()=>({source:'cloud',id:'cloud-A'}),pending:()=>receipt.pending?{source:'cloud',id:'cloud-A'}:null,
  report:()=>receipt};
 let loads=0;
 const api={list:async()=>({local:[],cloud:[{id:'cloud-A',name:'Saved A'}]}),
  ready:()=>true,loadCloud:async()=>{loads++;return true}};
 const f=fixture(pref,api);await flush();
 f.event('swrlz:account-assets',{authenticated:true});await flush();
 assert.equal(loads,0,'Do not launch a concurrent native cloud load');
 assert.equal(f.element('se476StartupGate').hidden,false,'Gate remains while native default is pending');
 receipt.pending=false;receipt.success=true;
 f.event('swrlz:saved-default-complete',{source:'cloud',id:'cloud-A',success:true});
 assert.equal(f.element('se476StartupGate').hidden,true,'Successful native default releases gate');
 assert.equal(loads,0,'No duplicate cloud request after default completes');
 assert.equal(f.window.SWYRL_ENGINE_STARTUP_476.inspect().finished,true);
 const failed={attempted:true,source:'cloud',pending:false,success:false,reason:'Account temporarily unavailable'};
 const f2=fixture({read:()=>({source:'cloud',id:'cloud-B'}),pending:()=>null,report:()=>failed},{
  ready:()=>true,list:async()=>({local:[],cloud:[{id:'cloud-B',name:'Saved B'}]}),
  loadCloud:async()=>{throw Error('Should not auto-retry failed default')}
 });
 await flush();f2.event('swrlz:account-assets',{authenticated:true});await flush();
 assert.equal(f2.element('se476StartupGate').hidden,false);
 assert.match(f2.element('se476StartupStatus').textContent,/temporarily unavailable/);
 f2.click('se476ContinueLocal');
 assert.equal(f2.element('se476StartupGate').hidden,true,'Recovery button enters editor');
 assert.equal(f2.window.SWYRL_ENGINE_STARTUP_476.inspect().account,'connected','Do not forge account-offline state');
 const f3=fixture({read:()=>null,pending:()=>null,report:()=>({attempted:false})},{
  ready:()=>true,list:async()=>({local:[],cloud:[]})
 });
 await flush();f3.event('swrlz:account-assets',{authenticated:true});await flush();
 f3.click('se476Open');await flush();
 assert.equal(f3.element('se476StartupGate').hidden,true,'Current workspace can open without saved project');
 assert(bridge.includes('const loaded=await se175LoadLocal()'),'Local loader requires explicit receipt');
 assert(bridge.includes('loaded===true'),'A stale session cannot be counted as local load success');
 assert(boot.includes('swrlz:saved-default-complete'),'Native boot emits verified terminal outcome');
 console.log('SE552_STARTUP_RESTORE_REGRESSION_PASS duplicate-cloud=0 confirmed-default=true failed-default-recovery=true local-receipt=true');
})().catch(error=>{console.error('SE552_STARTUP_RESTORE_REGRESSION_FAIL',error.stack||error);process.exitCode=1});
