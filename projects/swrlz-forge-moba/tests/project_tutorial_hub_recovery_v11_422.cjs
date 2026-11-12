'use strict';
/* Self-contained DOM harness for the actual v11.422 Projects tab installer.
   Tests cold mount, native switching, lost tab/pane and project preservation
   without depending on a browser runtime or cloud services. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'runtime/project_tutorial_hub_recovery_v11_422.js'),'utf8');
const style=fs.readFileSync(path.join(root,'runtime/project_tutorial_hub_recovery_v11_422.css'),'utf8');
const patch=fs.readFileSync(path.join(root,'patches/v11_422_project_tutorial_hub_recovery.py'),'utf8');
const listeners=new Map(),observers=[],deferred=[];
let actions={start:0,resume:0,attach:0,nativeInstall:0,nativeSwitch:[]};
const allChildren=n=>n.children.flatMap(child=>[child,...allChildren(child)]);
class Elem{
 constructor(tag='div'){
  this.tagName=tag.toUpperCase();this.children=[];this.parentElement=null;
  this.id='';this.className='';this.hidden=false;this.attributes={};this.listeners={};this.tabIndex=-1;
  this.textContent='';this.style={};this._html='';
  this.classList={
   contains:name=>this.className.split(/\s+/).includes(name),
   add:name=>{if(!this.classList.contains(name))this.className=(this.className+' '+name).trim();},
   remove:name=>{this.className=this.className.split(/\s+/).filter(v=>v!==name).join(' ');}
  };
 }
 get isConnected(){let p=this;while(p){if(p===body)return true;p=p.parentElement;}return false;}
 get innerHTML(){return this._html;}
 set innerHTML(value){
  this._html=String(value);
  this.children=[];
  for(const [,id] of this._html.matchAll(/id="([^"]+)"/g)){
   const sub=new Elem(id==='se412LibraryActions'?'div':'p');sub.id=id;this.append(sub);
  }
 }
 setAttribute(name,value){this.attributes[name]=String(value);}
 getAttribute(name){return this.attributes[name]??null;}
 append(...items){
  for(const item of items){
   if(item.parentElement)item.remove();
   this.children.push(item);item.parentElement=this;
  }
 }
 after(item){
  const parent=this.parentElement;
  if(!parent)throw Error('Cannot insert after detached node');
  if(item.parentElement)item.remove();
  const i=parent.children.indexOf(this);
  parent.children.splice(i+1,0,item);item.parentElement=parent;
 }
 remove(){
  if(this.parentElement)this.parentElement.children=this.parentElement.children.filter(x=>x!==this);
  this.parentElement=null;
 }
 matches(selector){
  selector=selector.trim();
  let a=selector.match(/^([a-z]+)\[role="([^"]+)"\]$/i);
  if(a)return this.tagName===a[1].toUpperCase()&&this.getAttribute('role')===a[2];
  if(selector.startsWith('#'))return this.id===selector.slice(1);
  if(selector.startsWith('.'))return this.classList.contains(selector.slice(1));
  return this.tagName.toLowerCase()===selector.toLowerCase();
 }
 querySelector(selector){
  const parts=selector.split(/\s+/),targets=allChildren(this);
  if(parts.length===1)return targets.find(n=>n.matches(parts[0]))||null;
  return targets.find(n=>n.matches(parts.at(-1))&&(()=>{
   let p=n.parentElement;
   for(let i=parts.length-2;i>=0;i--){while(p&&!p.matches(parts[i]))p=p.parentElement;if(!p)return false;p=p.parentElement;}
   return true;
  })())||null;
 }
 querySelectorAll(selector){return allChildren(this).filter(n=>n.matches(selector));}
 addEventListener(type,handler){(this.listeners[type]??=[]).push(handler);}
 click(){this.onclick?.();for(const f of this.listeners.click||[])f({target:this});}
 focus(){this.focused=true;}
}
const body=new Elem('body');
const hub=new Elem('div');hub.id='projectHub';hub.classList.add('show');
const windowEl=new Elem('section');windowEl.className='project-window';
const head=new Elem('header');head.className='project-head';windowEl.append(head);
const starterCard=new Elem('button');starterCard.id='original-starter';windowEl.append(starterCard);
hub.append(windowEl);body.append(hub);
const doc={
 readyState:'complete',documentElement:body,
 createElement:tag=>new Elem(tag),
 getElementById:id=>[body,...allChildren(body)].find(n=>n.id===id)||null,
 addEventListener:(name,fn)=>listeners.set(name,fn)
};
function nativeSelect(name){
 actions.nativeSwitch.push(name);
 for(const n of ['starter','mine']){
  const btn=hub.querySelector('#se170-tab-'+n),pane=hub.querySelector('#se170-pane-'+n);
  btn?.setAttribute('aria-selected',String(name===n));
  if(pane)pane.hidden=name!==n;
 }
}
function nativeInstall(){
 actions.nativeInstall++;
 if(hub.querySelector('.se170-hub-tabs'))return;
 const tabs=new Elem('div');tabs.className='se170-hub-tabs';
 const starter=new Elem('div');starter.id='se170-pane-starter';starter.className='se170-hub-pane';
 const mine=new Elem('div');mine.id='se170-pane-mine';mine.className='se170-hub-pane';
 for(const [n,label] of [['starter','Starter Projects'],['mine','My Projects']]){
  const tab=new Elem('button');tab.id='se170-tab-'+n;tab.textContent=label;
  tab.setAttribute('role','tab');tab.onclick=()=>context.se170Select(n);tabs.append(tab);
 }
 starter.append(starterCard);windowEl.append(tabs,starter,mine);
 context.se170Select('starter');
}
class MockMutationObserver{
 constructor(fn){this.fn=fn;observers.push(this);this.active=false;}
 observe(el,options){this.el=el;this.options=options;this.active=true;}
 disconnect(){this.active=false;}
 emit(records){if(this.active)this.fn(records);}
}
const context={
 document:doc,window:{addEventListener(){}},MutationObserver:MockMutationObserver,
 queueMicrotask:f=>deferred.push(f),requestAnimationFrame:f=>deferred.push(f),
 se170Install:nativeInstall,se170Select:nativeSelect,
 belongs:()=>false,attachPanel:()=>{actions.attach++},
 button:(label,fn)=>{const e=new Elem('button');e.textContent=label;e.onclick=fn;return e;},
 newLesson:()=>{actions.start++},resume:()=>{actions.resume++}
};
vm.createContext(context);
vm.runInContext(source,context,{filename:'project_tutorial_hub_recovery_v11_422.js'});
function flush(){
 let cycles=0;while(deferred.length){if(++cycles>30)throw Error('Unbounded library repair loop');
  deferred.shift()();}
}
flush();
let tab=hub.querySelector('#se412Tab'),pane=hub.querySelector('#se412Tutorials');
assert(tab&&pane,'Tutorial tab and pane must mount after native hub initialization');
assert.equal(actions.nativeInstall,1,'Native project tabs initialized once');
assert.equal(hub.querySelector('#original-starter'),starterCard,'Original starter card preserved');
assert.equal(hub.querySelectorAll('button[role="tab"]').length,3,'All three tabs are present');
tab.click();
assert.equal(pane.hidden,false,'Tutorial pane shown');
assert.equal(hub.querySelector('#se170-pane-starter').hidden,true);
assert.equal(hub.querySelector('#se170-pane-mine').hidden,true);
assert.equal(tab.getAttribute('aria-selected'),'true');
hub.querySelector('#se170-tab-mine').click();
assert.equal(pane.hidden,true,'Switching to My Projects hides Tutorials');
assert.equal(hub.querySelector('#se170-pane-mine').hidden,false);
hub.querySelector('#se170-tab-starter').click();
assert.equal(hub.querySelector('#se170-pane-starter').hidden,false);
assert.equal(pane.hidden,true,'Returning to Starter hides Tutorials');
const actionsRow=pane.querySelector('#se412LibraryActions');
assert.equal(actionsRow.children.length,2);
actionsRow.children[0].click();actionsRow.children[1].click();
assert.equal(actions.start,1);assert.equal(actions.resume,1);
const observer=observers.find(o=>o.el===hub);
assert(observer?.active,'Hub has a scoped recovery observer');
tab.remove();pane.remove();
observer.emit([{type:'childList',target:hub}]);flush();
tab=hub.querySelector('#se412Tab');pane=hub.querySelector('#se412Tutorials');
assert(tab&&pane,'Missing tab and pane restored after native DOM rebuild');
assert.equal(hub.querySelectorAll('button[role="tab"]').length,3,'No duplicated tab after rebuild');
assert.equal(hub.querySelector('#original-starter'),starterCard,'Original starter still preserved');
pane.remove();observer.emit([{type:'childList',target:hub}]);flush();
assert(hub.querySelector('#se412Tutorials'),'Partially missing pane is recovered');
assert.equal(hub.querySelectorAll('button[role="tab"]').length,3);
const diagnostics=context.window.SWYRL_ENGINE_PROJECT_TUTORIAL_HUB_422.inspect();
assert.equal(diagnostics.tutorialTab,true);
assert.equal(diagnostics.tutorialPane,true);
assert.equal(diagnostics.mine,true);
assert(diagnostics.repairs>=3);
assert.match(style,/grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/);
assert.match(patch,/SE422_PROJECT_TUTORIAL_HUB_RECOVERY_START/);
assert.match(patch,/se170Install\(\)/);
console.log('PROJECT_TUTORIAL_HUB_422_PASS: deferred native install, all 3 tabs, correct selected panes, starter preservation, action buttons, DOM rebuild and partial-pane recovery.');
