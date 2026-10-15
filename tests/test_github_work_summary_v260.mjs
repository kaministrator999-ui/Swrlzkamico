import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
import path from "node:path";
import {fileURLToPath} from "node:url";

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const js=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-work-summary-v260.js"),"utf8");
const chat=fs.readFileSync(path.join(root,"chat/§wyrlz/index.html"),"utf8");
const station=fs.readFileSync(path.join(root,"hf_space/station.py"),"utf8");
const manual=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-chat-create-txt-v258.js"),"utf8");
const css=fs.readFileSync(path.join(root,"hf_space/chat/§wyrlz/assets/github-work-summary-v260.css"),"utf8");
assert(chat.includes('widget.kind==="github-work"'));
assert(station.includes("github-work-summary-v260.js"));
assert(station.includes("github-work-summary-v260.css"));
assert(manual.includes("SwrlzGithubWorkView.render(visual,result.widget)"));
assert(css.includes(".github-work-dashboard"));
const created=[];
class Element{
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.className="";this.textContent="";created.push(this);}
  setAttribute(k,v){this.attributes[k]=v;}
  append(...nodes){this.children.push(...nodes);}
}
const window={};
const document={createElement:tag=>new Element(tag)};
vm.runInNewContext(js,{window,document,Date,Number,String,Object},{filename:"github-work-summary-v260.js"});
const PATH="write-action-tests/chat-test-6bbae6acc5289bb8.txt";
const SHA="d7d24c4629c62613744742e52ca9349716721e31";
const widget={contract:"swrlz-widget-v1",kind:"github-work",data:{
  repo:"kaministrator999-ui/Swrlzing-core",branch:"main",operation:"CREATE_FILE",
  path:PATH,verified:true,verification:"EXACT_BYTES_MATCHED",
  fileUrl:"https://github.com/kaministrator999-ui/Swrlzing-core/blob/main/"+PATH,
  commitUrl:"https://github.com/kaministrator999-ui/Swrlzing-core/commit/"+SHA,
  commitSha:SHA,filesCreated:1,bytesWritten:189,textLines:3,
  providerStatsAvailable:true,additions:3,deletions:0,filesChanged:1,
  commitAt:"2026-10-15T22:08:53Z"
}};
const host=new Element("div");
assert.equal(window.SwrlzGithubWorkView.render(host,widget),true);
assert.equal(host.children.length,1);
const nodes=[];
const walk=(n)=>{nodes.push(n);for(const x of n.children||[])walk(x)};
walk(host);
const strings=nodes.map(x=>x.textContent);
for(const part of ["Files created","Bytes written","Text lines","Added lines","Deleted lines","Commit d7d24c4","1","189","3","+3","−0"]){
  assert(strings.includes(part),"Missing rendered figure: "+part);
}
const links=nodes.filter(x=>x.tag==="a");
assert.equal(links.length,2);
assert(links.every(x=>x.target==="_blank"&&x.rel==="noopener noreferrer"));
const noStats={...widget,data:{...widget.data,providerStatsAvailable:false,additions:undefined,deletions:undefined}};
const host2=new Element("div");
assert(window.SwrlzGithubWorkView.render(host2,noStats));
const all2=[];const walk2=n=>{all2.push(n);(n.children||[]).forEach(walk2)};walk2(host2);
assert(!all2.map(n=>n.textContent).includes("Added lines"),"Never fake provider diff statistics");
assert(all2.map(n=>n.textContent).some(x=>String(x).includes("statistics unavailable")));
const malicious={...widget,data:{...widget.data,fileUrl:"https://attacker.example/phishing"}};
assert.equal(window.SwrlzGithubWorkView.render(new Element("div"),malicious),false);
assert(!js.includes("innerHTML"),"Work summary must not parse HTML from GitHub data");
console.log("v260 GitHub statistics UI PASS");
