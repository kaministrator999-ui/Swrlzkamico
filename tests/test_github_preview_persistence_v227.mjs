/* v227: reproduce the Station githubContext-triggered full message redraw. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

class Element {
  constructor(tag){
    this.tagName=tag;
    this.children=[];
    this.parentNode=null;
    this.rootConnected=false;
    this._text="";
    this.hidden=false;
    this.className="";
    this.attributes={};
    this.classes=new Set();
    this.classList={
      add:(v)=>this.classes.add(v),
      toggle:(v,on)=>{
        const enabled=on===undefined?!this.classes.has(v):!!on;
        enabled?this.classes.add(v):this.classes.delete(v);
        return enabled;
      }
    };
  }
  set textContent(value){
    this._text=String(value??"");
    this.replaceChildren();
  }
  get textContent(){
    return this._text+this.children.map(x=>x.textContent||"").join("");
  }
  append(...items){items.forEach(x=>this.appendChild(x));}
  appendChild(node){
    assert.ok(node instanceof Element);
    if(node.parentNode)node.parentNode.children.splice(node.parentNode.children.indexOf(node),1);
    this.children.push(node);
    node.parentNode=this;
    return node;
  }
  replaceChildren(...items){
    this.children.forEach(x=>x.parentNode=null);
    this.children=[];
    this._text="";
    this.append(...items);
  }
  setAttribute(k,v){this.attributes[k]=String(v);}
  add(node){this.appendChild(node);}
  remove(){
    if(this.parentNode){
      this.parentNode.children.splice(this.parentNode.children.indexOf(this),1);
      this.parentNode=null;
    }
  }
  get isConnected(){return this.parentNode?this.parentNode.isConnected:this.rootConnected;}
}
const doc={
  head:new Element("head"),
  createElement:tag=>new Element(tag),
  createTextNode:text=>{const n=new Element("#text");n.textContent=text;return n;}
};
doc.head.rootConnected=true;
const urls=[];
const sourceSha="b".repeat(40);
const blobSha="c".repeat(40);
const source="## GitHub directory: /\n- dir src\n- file README.md";
const replies={
  directory:{repository:"owner/repo",branch:"main",sourceSha,complete:true,path:"",
    stats:{recursiveFiles:1,recursiveDirectories:1,gitBlobBytes:24},
    entries:[
      {type:"dir",name:"src",path:"src",sizeBytes:0,fileCount:0,directoryCount:0},
      {type:"file",name:"README.md",path:"README.md",sizeBytes:24,fileCount:null,directoryCount:null}
    ]},
  file:{repository:"owner/repo",branch:"main",sourceSha,path:"README.md",
    blobSha,sizeBytes:24,readable:true,content:"# README\nAn open file remains visible.\n"}
};
const window={};
const contextEvents=[];
const sandbox={
  window,document:doc,console,Date,URLSearchParams,
  navigator:{clipboard:{writeText:async()=>{}}},
  Option:function(label,value){const option=new Element("option");option.label=label;option.value=value;return option;},
  fetch:async(path,args)=>{
    const target=new URL(path,"https://chat.example");
    urls.push(target.pathname);
    if(target.pathname==="/api/lalm_station/github-context"){
      contextEvents.push(JSON.parse(args.body));
      return {ok:true,json:async()=>({ok:true})};
    }
    const endpoint=target.pathname.split("/").at(-1);
    if(!(endpoint in replies))throw Error("Unexpected endpoint "+path);
    return {ok:true,json:async()=>replies[endpoint]};
  }
};
const sourceCode=fs.readFileSync("chat/§wyrlz/assets/github-explorer-v223.js","utf8");
vm.runInNewContext(sourceCode,sandbox,{timeout:5000});
const explorer=window.SwrlzGitHubExplorerV223;
assert.equal(explorer.version,"227");
const makeContainer=()=>{const n=new Element("assistant-body");n.rootConnected=true;return n;};
const nodes=(root)=>[root,...root.children.flatMap(nodes)];
const find=(root,matcher)=>nodes(root).find(matcher);
const button=(root,label)=>find(root,x=>x.tagName==="button"&&x.textContent===label);
const preview=(root)=>find(root,x=>x.className==="repo-panel");
const opts={
  accountId:()=>"google:ownerA",threadId:()=>"threadA",messageId:"message-1",
  contextUpdated:()=>{
    // Real station sync changes thread.githubContext, so the whole message
    // is rebuilt. This callback mimics that replacement synchronously.
    last=makeContainer();
    assert.ok(explorer.render(last,source,opts));
  }
};
let last=makeContainer();
assert.ok(explorer.render(last,source,opts));
const initialCard=find(last,x=>x.className==="repo-explorer");
assert.ok(initialCard);
assert.equal(preview(last).hidden,true);
assert.ok(button(last,"Open"),"Initial file row should have Open control");
await button(last,"Open").onclick();
assert.equal(contextEvents.length,2,"Browsing root and opening file each persist GitHub context");
assert.ok(contextEvents.every(x=>x.threadId==="threadA"),"Thread-scoped context retained");
assert.ok(contextEvents.some(x=>x.kind==="file"&&x.path==="README.md"));
assert.equal(find(last,x=>x.className==="repo-explorer"),initialCard,
  "Station redraw must reattach the SAME DOM card and its event listeners");
assert.equal(preview(last).hidden,false,"Open file panel must remain visible after redraw");
assert.ok(preview(last).textContent.includes("An open file remains visible."),
  "Source preview contents must survive the redraw");
assert.equal(urls.filter(x=>x.endsWith("/file")).length,1,
  "A redraw must not refetch file contents");
assert.equal(urls.filter(x=>x.endsWith("/directory")).length,1,
  "A redraw must not refetch the directory tree");

const copy=button(last,"Copy code");
assert.ok(copy,"File controls must survive redraw");
assert.ok(button(last,"Dates / history"));
last=makeContainer();
explorer.render(last,source,opts);
assert.equal(find(last,x=>x.className==="repo-explorer"),initialCard);
assert.equal(preview(last).hidden,false);
assert.ok(button(last,"Close"));
button(last,"Close").onclick();
assert.equal(preview(last).hidden,true,"Explicit Close remains authoritative");
last=makeContainer();
explorer.render(last,source,opts);
assert.equal(preview(last).hidden,true,"Closed previews must not spontaneously reopen");

const otherAccount=makeContainer();
const differentAccount={...opts,accountId:()=>"google:ownerB"};
explorer.render(otherAccount,source,differentAccount);
assert.notEqual(find(otherAccount,x=>x.className==="repo-explorer"),initialCard,
  "Other Google account cannot inherit cached DOM or open file");
assert.equal(preview(otherAccount).hidden,true);
const otherThread=makeContainer();
explorer.render(otherThread,source,{...opts,threadId:()=>"threadB"});
assert.notEqual(find(otherThread,x=>x.className==="repo-explorer"),initialCard,
  "Other thread cannot inherit cached DOM");

const changed=makeContainer();
const updatedSource="## GitHub directory: /\n- dir src\n- file changed.md";
explorer.render(changed,updatedSource,opts);
assert.notEqual(find(changed,x=>x.className==="repo-explorer"),initialCard,
  "Updated listing evidence must invalidate cached DOM");
assert.equal(preview(changed).hidden,true,"Never display an old file from superseded source evidence");

console.log("v227 GitHub explorer: file preview, controls, close, context sync redraw, source isolation and no redundant fetch PASS");
