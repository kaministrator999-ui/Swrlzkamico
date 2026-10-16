import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const source=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-rename-v263.js"),"utf8");
const widget=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-rename-receipt-v263.js"),"utf8");
const station=fs.readFileSync(path.join(root,"hf_space/station.py"),"utf8");
const chat=fs.readFileSync(path.join(root,"chat/§wyrlz/index.html"),"utf8");
assert(station.includes("githubChatFileAction"));
assert(!chat.includes("swrlz:github-rename-proposal"),"Chat no longer emits legacy popup triggers");
assert(!station.includes("github-rename-v263.js"),"Legacy rename popup must not load in Chat");
assert(station.includes("github-rename-receipt-v263.js"));
const made=[],callbacks={},network=[];
class Element {
 constructor(tag){this.tag=tag;this.props={};this.children=[];this.handlers={};this.value="";this.textContent="";this.hidden=false;this.open=false;this.disabled=false;this.style={};made.push(this);}
 setAttribute(k,v){this[k]=v;}
 append(...children){this.children.push(...children);}
 insertBefore(child,reference){let i=this.children.indexOf(reference);this.children.splice(i<0?this.children.length:i,0,child);}
 addEventListener(name,fn){this.handlers[name]=fn;}
 click(){return this.handlers.click?.();}
 focus(){}
 showModal(){this.open=true;}
 close(){this.open=false;this.handlers.close?.();}
 remove(){this.removed=true;}
}
const document={body:new Element("body"),createElement:tag=>new Element(tag)};
const window={addEventListener:(event,callback)=>callbacks[event]=callback};
const fake=async(uri,options)=>{
 network.push({uri,options});
 if(uri.endsWith("rename-status"))return {ok:true,json:async()=>({
    linked:true,allowed:true,repo:"kaministrator999-ui/Swrlzing-core",branch:"main"})};
 if(uri.endsWith("prepare-rename"))return {ok:true,json:async()=>({
   approvalToken:"approved-ticket",repo:"kaministrator999-ui/Swrlzing-core",
   branch:"main",sourcePath:"src/old.py",destinationPath:"src/new.py",
   sourceBlobSha:"a".repeat(40),sourceMode:"100755",bytes:428,headSha:"b".repeat(40)})};
 if(uri.endsWith("confirm-rename"))return {ok:true,json:async()=>({
   ok:true,verified:true,sourcePath:"src/old.py",destinationPath:"src/new.py",
   commitSha:"c".repeat(40),
   url:"https://github.com/kaministrator999-ui/Swrlzing-core/blob/main/src/new.py"})};
 throw Error("Unknown URL "+uri);
};
vm.runInNewContext(source,{document,window,fetch:fake,console});
const emit=(requestId,prompt)=>callbacks["swrlz:github-rename-proposal"]({detail:{requestId,prompt}});
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const count=kind=>network.filter(x=>x.uri.endsWith(kind)).length;
assert.equal(document.body.children.length,0);
emit("req1","Rename src/old.py to src/new.py in my GitHub repo");
const dlg=made.find(x=>x.tag==="dialog");
assert(dlg?.open);
const fields=made.filter(x=>x.tag==="input");
assert.equal(fields[0].value,"src/old.py");
assert.equal(fields[1].value,"src/new.py");
assert.equal(count("confirm-rename"),0);
emit("req1","Rename x.py to y.py in repo");
assert.equal(made.filter(x=>x.tag==="dialog").length,1);
await tick();
const prepare=made.find(x=>x.textContent==="Prepare rename (no write)");
const confirm=made.find(x=>x.textContent==="Confirm atomic rename");
assert.equal(confirm.disabled,true);
prepare.click();await tick();await tick();
assert.equal(count("prepare-rename"),1);
assert.equal(count("confirm-rename"),0);
assert.equal(confirm.disabled,false);
const sent=JSON.parse(network.find(x=>x.uri.endsWith("prepare-rename")).options.body);
assert.equal(sent.sourcePath,"src/old.py");
assert.equal(sent.destinationPath,"src/new.py");
confirm.click();await tick();await tick();
assert.equal(count("confirm-rename"),1);
dlg.close();
emit("req2","Move file LICENSE to docs/LICENSE in repository");
assert.equal(made.filter(x=>x.tag==="dialog").length,2);
console.log("v263 chat rename review never writes before explicit confirm PASS");

// Work display must reject external URLs and show source/destination.
const created=[],viewWindow={};
const document2={createElement:tag=>{const e=new Element(tag);created.push(e);return e;}};
vm.runInNewContext(widget,{window:viewWindow,document:document2,Date,Number,String,Object});
const src="src/old.py",dest="src/new.py",repo="kaministrator999-ui/Swrlzing-core",sha="d".repeat(40);
const view={kind:"github-rename",contract:"swrlz-widget-v1",data:{
 operation:"RENAME_FILE",repo,branch:"main",sourcePath:src,destinationPath:dest,
 fileUrl:"https://github.com/"+repo+"/blob/main/"+dest,
 commitUrl:"https://github.com/"+repo+"/commit/"+sha,commitSha:sha,blobSha:"e".repeat(40),
 verification:"IDENTICAL_BLOB_AND_MODE",atomic:true,overwritten:0,filesRenamed:1,
 bytesPreserved:428
}};
const host=new Element("div");
assert(viewWindow.SwrlzGithubRenameView.render(host,view));
const all=[];const walk=n=>{all.push(n);for(const c of n.children||[])walk(c);};walk(host);
assert(all.some(n=>n.textContent==="File renamed"));
assert(all.some(n=>n.textContent==="From: src/old.py"));
assert(all.some(n=>n.textContent==="To: src/new.py"));
assert(all.some(n=>n.textContent==="428"));
assert.equal(all.filter(n=>n.tag==="a").length,2);
assert.equal(viewWindow.SwrlzGithubRenameView.render(new Element("div"),{
 ...view,data:{...view.data,fileUrl:"https://evil.example/redirect"}}),false);
assert(!widget.includes("innerHTML"));
console.log("v263 rename work receipt PASS");
