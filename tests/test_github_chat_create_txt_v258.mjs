'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const file = path.join(__dirname,'../hf_space/chat/§wyrlz/assets/github-chat-create-txt-v258.js');
const source = fs.readFileSync(file,'utf8');
assert(!source.includes("const button = el('button', {type:'button', text:'Test GitHub TXT creation'"),
       'Old floating test button must not be the entry point');
assert(source.includes("'swrlz:github-txt-proposal'"),'Chat action event missing');

let elements = [];
let events = {};
let requests = [];
let authAllowed = true;
class Element {
  constructor(tag) {
    this.tag = tag; this.attrs={}; this.children=[];this.handlers={};
    this.style={};this.textContent='';this.value='';this.disabled=false;this.open=false;
    elements.push(this);
  }
  setAttribute(k,v) {this.attrs[k]=v;}
  append(...children) {this.children.push(...children);}
  addEventListener(type,fn) {this.handlers[type]=fn;}
  click() {this.handlers.click?.();}
  showModal() {this.open=true;}
  focus() {}
  close() {this.open=false;this.handlers.close?.();}
  remove() {this.removed=true;}
}
const document = {body:new Element('body'),createElement:tag=>new Element(tag)};
const window = {addEventListener:(type,fn)=>{events[type]=fn;}};
const fetch = async(url,args)=>{
  requests.push({url,args});
  if(url.endsWith('/write-status'))return {ok:true,json:async()=>({allowed:authAllowed})};
  if(url.endsWith('/prepare-create-txt'))return {ok:true,json:async()=>({approvalToken:'ticket',path:'write-action-tests/note.txt',repo:'kaministrator999-ui/Swrlzing-core',branch:'main',preview:'hello world',operation:'CREATE_FILE'})};
  if(url.endsWith('/confirm-create-txt'))return {ok:true,json:async()=>({ok:true,verified:true,commitSha:'commitSha',url:'https://github.com/kaministrator999-ui/Swrlzing-core/blob/main/write-action-tests/note.txt'})};
  throw Error('Unexpected endpoint '+url);
};
vm.runInNewContext(source,{window,document,fetch,console},{filename:file});
assert.equal(document.body.children.length,0,'Do not create any floating test button');
assert.equal(typeof events['swrlz:github-txt-proposal'],'function');
const emit=(requestId,prompt)=>events['swrlz:github-txt-proposal']({detail:{requestId,prompt}});
emit('req1','Create a file called note.txt in the repo containing "hello world"');
const dialog=elements.find(e=>e.tag==='dialog');
assert(dialog?.open,'Server proposal should open action review directly');
let filename=elements.find(e=>e.tag==='input');
let contentInput=elements.find(e=>e.tag==='textarea');
assert.equal(filename?.value,'note.txt');
assert.equal(contentInput?.value,'hello world');
assert.equal(requests.filter(x=>x.url.endsWith('confirm-create-txt')).length,0,'No automatic write');
emit('req1','Create a file called other.txt in the repo');
assert.equal(elements.filter(e=>e.tag==='dialog').length,1,'Duplicate stream events must not create duplicate prompts');
let prepare=elements.find(e=>e.textContent==='Prepare (no write)');
let confirm=elements.find(e=>e.textContent==='Confirm GitHub creation');
assert(prepare&&confirm);
assert.equal(confirm.disabled,true,'Only preparation enables final confirmation');
(async()=>{
  await new Promise(resolve=>setImmediate(resolve));
  prepare.click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(requests.filter(x=>x.url.endsWith('confirm-create-txt')).length,0,'Prepare is read only');
  assert.equal(confirm.disabled,false,'Prepare must allow explicit confirmation');
  confirm.click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(requests.filter(x=>x.url.endsWith('confirm-create-txt')).length,1,'Only explicit confirmation writes');
  dialog.close();
  emit('req2','Can you make a text file in the repo?');
  assert.equal(elements.filter(e=>e.tag==='dialog').length,2);
  assert.equal(elements.filter(e=>e.tag==='input').at(-1).value,'','No invented filename');
  assert.equal(elements.filter(e=>e.tag==='textarea').at(-1).value,'','No invented file bytes');
  console.log('v258 Chat natural TXT approval UI PASS');
})().catch(err=>{console.error(err);process.exitCode=1});
