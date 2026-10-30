import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/chat_panel_account_project_v11_176.js',import.meta.url),'utf8');
new vm.Script(source);
class El {
  constructor(tag='div'){this.tag=tag;this.children=[];this.hidden=false;this.disabled=false;this.textContent='';this.attrs={};this._value='';}
  append(...n){this.children.push(...n)}
  insertBefore(n,ref){const i=this.children.indexOf(ref);this.children.splice(i>=0?i:0,0,n)}
  replaceChildren(...nodes){this.children=nodes}
  setAttribute(k,v){this.attrs[k]=v}
  addEventListener(k,fn){this['on'+k]=fn}
  get options(){return this.children.flatMap(c=>c.tag==='optgroup'?c.options:[c]).filter(x=>x.tag==='option')}
  get value(){if(this.tag!=='select')return this._value;return this.options.some(o=>o.value===this._value)?this._value:this.options[0]?.value??''}
  set value(v){this._value=v}
}
const names=['seChatSignIn','seChatRefresh','seChatLoad','seChatAccount','seChatProjects','se176GoogleIcon'];
const elements=Object.fromEntries(names.map(n=>[n,new El(n==='seChatProjects'?'select':'button')]));
const row=new El();row.children=[elements.seChatAccount,elements.seChatSignIn];
const document={
  getElementById:k=>elements[k]||null,
  querySelector:k=>k==='#seChatAccountPanel .se-chat-row'?row:null,
  createElement:tag=>new El(tag),
  head:{append:()=>{}}
};
let project={id:'native-open',name:'Sheep Tag',projectName:'Sheep Tag'};
let local=[{id:'local-one',name:'Independent scene',updatedAt:'2026-10-30'}];
let cloud=[{id:'cloud-one',name:'Saved account scene',revision:3}];
let cloudResolve=null,cloudCalls=0,loadCloudCalls=0;
const sandbox={
  document,
  get currentProject(){return project;},
  getProjectId:()=>project.id,
  accountText:elements.seChatAccount,
  cloudList:elements.seChatProjects,
  summaryName:v=>String(v||'').slice(0,100),
  setStatus:()=>{},
  get ready(){return true;},
  get cloudBusy(){return false;},
  se175Read:async()=>local,
  se175LocalList:new El('select'),
  se175RefreshLocal:async()=>{},
  se175LoadLocal:async()=>{project={id:'local-one',name:'Independent scene',projectName:'Independent scene'};},
  loadCloud:async()=>{loadCloudCalls++;project={id:'cloud-one',name:'Saved account scene'};return true;},
  rpc:async(type)=>{assert.equal(type,'cloud.list');cloudCalls++;return cloudResolve?await cloudResolve:{projects:cloud};}
};
const ctx=vm.createContext(sandbox);vm.runInContext(source,ctx);
const call=(exp)=>vm.runInContext(exp,ctx);
call('se176Install()');
assert.equal(elements.seChatProjects.options[0].textContent,'Editing now · Sheep Tag');
assert.equal(elements.seChatLoad.disabled,true);
call('se176AccountState({authenticated:true,user:{name:"Kami"}})');
assert.equal(elements.seChatSignIn.hidden,true);
assert.equal(elements.se176GoogleIcon.hidden,false);
assert.equal(elements.seChatAccount.textContent,'Kami');
await call('se176RefreshProjects()');
assert.deepEqual(elements.seChatProjects.options.map(x=>x.value),['active','local:local-one','cloud:cloud-one']);
elements.seChatProjects.value='local:local-one';call('se176UpdateLoadButton()');
assert.equal(elements.seChatLoad.disabled,false);
await call('se176LoadSelection()');
assert.equal(project.id,'local-one');
assert.equal(elements.seChatProjects.options[0].textContent,'Editing now · Independent scene');
elements.seChatProjects.value='cloud:cloud-one';await call('se176LoadSelection()');
assert.equal(loadCloudCalls,1);
assert.equal(project.id,'cloud-one');
const deferred={};cloudResolve=new Promise(resolve=>{deferred.resolve=resolve});
const pending=call('se176RefreshProjects()');
await Promise.resolve();await Promise.resolve();
call('se176AccountState({authenticated:false})');
deferred.resolve({projects:[{id:'other-user',name:'Private cloud',revision:99}]});
await pending;
assert.equal(elements.seChatSignIn.hidden,false);
assert.equal(elements.se176GoogleIcon.hidden,true);
assert(!elements.seChatProjects.options.some(x=>x.value.startsWith('cloud:')),'cloud projects must clear after logout and ignore late results');
assert(elements.seChatProjects.options.some(x=>x.value==='local:local-one'),'local projects remain available');
console.log(JSON.stringify({ok:true,suite:'forge-v11-176-account-project-picker',checks:16,cloudCalls}));
