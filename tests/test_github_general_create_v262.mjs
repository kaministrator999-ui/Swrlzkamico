import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import path from "node:path";
import {fileURLToPath} from "node:url";

const base=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const script=fs.readFileSync(path.join(base,"hf_space/chat/§wyrlz/assets/github-general-create-v262.js"),"utf8");
const css=fs.readFileSync(path.join(base,"hf_space/chat/§wyrlz/assets/github-general-create-v262.css"),"utf8");
const station=fs.readFileSync(path.join(base,"hf_space/station.py"),"utf8");
const chat=fs.readFileSync(path.join(base,"chat/§wyrlz/index.html"),"utf8");
assert(station.includes("githubGeneralFileProposal"));
assert(station.includes("github-general-create-v262.js"));
assert(station.includes("github-general-create-v262.css"));
assert(chat.includes("GITHUB_GENERAL_CREATE_FILE_APPROVAL_REQUIRED"));
assert(chat.includes("swrlz:github-general-create-proposal"));
assert(css.includes("github-general-dialog"));

const created=[], events={}, requests=[];
class El {
  constructor(tag) {this.tag=tag;this.children=[];this.handlers={};this.style={};this.textContent="";this.value="";this.hidden=false;this.open=false;this.disabled=false;created.push(this);}
  setAttribute(k,v){this[k]=v;}
  append(...nodes){this.children.push(...nodes);}
  addEventListener(name,fn){this.handlers[name]=fn;}
  focus(){}
  click(){return this.handlers.click?.();}
  showModal(){this.open=true;}
  close(){this.open=false;this.handlers.close?.();}
  remove(){this.removed=true;}
}
const document={body:new El("body"),createElement:tag=>new El(tag)};
const window={addEventListener:(name,fn)=>{events[name]=fn;}};
const btoa=x=>Buffer.from(x,"binary").toString("base64");
const fetch=async(url,options)=>{
  requests.push({url,options});
  if(url.endsWith("create-status"))return {ok:true,json:async()=>({allowed:true,repo:"kaministrator999-ui/Swrlzing-core",branch:"main"})};
  if(url.endsWith("prepare-create")){
    const args=JSON.parse(options.body);
    return {ok:true,json:async()=>({
      approvalToken:"ticket"+requests.length,
      repo:"kaministrator999-ui/Swrlzing-core",branch:"main",
      path:args.path,bytes:Buffer.from(args.contentBase64,"base64").length,
      sha256:"a".repeat(64),mediaType:args.mediaType,
    })};
  }
  if(url.endsWith("confirm-create")){
    return {ok:true,json:async()=>({ok:true,verified:true,
      path:"src/app.py",commitSha:"a".repeat(40),
      url:"https://github.com/kaministrator999-ui/Swrlzing-core/blob/main/src/app.py"})};
  }
  throw Error("Unexpected endpoint "+url);
};
vm.runInNewContext(script,{window,document,fetch,btoa,TextEncoder,Uint8Array,String,Object,console});
const emit=(requestId,prompt)=>events["swrlz:github-general-create-proposal"]({detail:{requestId,prompt}});
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const count=suffix=>requests.filter(r=>r.url.endsWith(suffix)).length;
assert.equal(document.body.children.length,0,"No unrelated modal on initial page load");
emit("req1",'Create a Python file named src/app.py in the GitHub repo containing "print(1)"');
const form=created.find(x=>x.tag==="dialog");
assert(form?.open,"Server proposal should open review");
const filename=created.find(x=>x.tag==="input"&&x.type==="text");
const contents=created.find(x=>x.tag==="textarea");
const prepare=created.find(x=>x.textContent==="Prepare preview");
const confirm=created.find(x=>x.textContent==="Confirm this GitHub file");
assert.equal(filename.value,"src/app.py");
assert.equal(contents.value,"print(1)");
assert.equal(confirm.disabled,true);
assert.equal(count("confirm-create"),0);
emit("req1","Create another file named skip.py in GitHub");
assert.equal(created.filter(x=>x.tag==="dialog").length,1,"Duplicate status cannot repeat approval");
await tick();
assert.equal(prepare.disabled,false);
prepare.click();await tick();await tick();
assert.equal(count("prepare-create"),1);
assert.equal(count("confirm-create"),0,"Preparing must not mutate GitHub");
assert.equal(confirm.disabled,false);
const proposed=JSON.parse(requests.find(x=>x.url.endsWith("prepare-create")).options.body);
assert.equal(proposed.path,"src/app.py");
assert.equal(Buffer.from(proposed.contentBase64,"base64").toString(),"print(1)");
confirm.click();await tick();await tick();
assert.equal(count("confirm-create"),1,"Only real user confirm sends mutation");
form.close();
emit("req2","Upload a picture to the GitHub repo");
const forms=created.filter(x=>x.tag==="dialog");
assert.equal(forms.length,2);
const mode=created.filter(x=>x.tag==="select").at(-1);
mode.value="binary";mode.handlers.change();
const binaryInput=created.filter(x=>x.tag==="input"&&x.type==="file").at(-1);
binaryInput.files=[{name:"dragon.png",size:6,type:"image/png",arrayBuffer:async()=>Uint8Array.from([0,255,137,80,78,71]).buffer}];
binaryInput.handlers.change();
assert.equal(created.filter(x=>x.tag==="input"&&x.type==="text").at(-1).value,"dragon.png");
await tick();
created.filter(x=>x.textContent==="Prepare preview").at(-1).click();
await tick();await tick();
assert.equal(count("prepare-create"),2);
const bytes=JSON.parse(requests.filter(x=>x.url.endsWith("prepare-create")).at(-1).options.body);
assert.equal(bytes.mediaType,"image/png");
assert.deepEqual([...Buffer.from(bytes.contentBase64,"base64")],[0,255,137,80,78,71]);
assert.equal(count("confirm-create"),1,"Binary upload must also await confirmation");
console.log("v262 general file review UI: source+binary/no-auto-write PASS");
