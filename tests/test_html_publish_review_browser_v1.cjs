/* Browser-free DOM acceptance for both HTML approval gates and live blob identity. */
const fs=require("node:fs");
const assert=require("node:assert/strict");
const vm=require("node:vm");
const crypto=require("node:crypto");
const path=require("node:path");

const code=fs.readFileSync(path.join(__dirname,"../chat/html-project-publish-review-v1.js"),"utf8");
class Element {
  constructor(tag,document){
    this.tagName=tag;this.ownerDocument=document;this.children=[];
    this.listeners={};this.dataset={};this.style={};
    this.isConnected=true;this.textContent="";this.hidden=false;
  }
  append(...nodes){this.children.push(...nodes);}
  appendChild(node){this.append(node);return node;}
  addEventListener(name,callback){this.listeners[name]=callback;}
  setAttribute(key,value){this[key]=value;}
}
function harness(){
  const blob=Buffer.from("<!doctype html><title>Verified project</title>");
  const sha=crypto.createHash("sha1").update("blob "+blob.length+"\0").update(blob).digest("hex");
  let fetched=0;
  const document={
    createElement(tag){return new Element(tag,document);},
    createTextNode(text){return {textContent:text};},
    getElementById(){return null;},
    defaultView:{
      location:{origin:"https://kamiloki-swyrlz.hf.space"},
      crypto:crypto.webcrypto,
      fetch:async()=>{fetched++;return {
        ok:true,
        headers:{get(key){return ({
          "content-security-policy":"sandbox allow-scripts; connect-src 'none'; default-src 'self'",
          "x-content-type-options":"nosniff",
        })[key]||"";}},
        async arrayBuffer(){return blob.buffer.slice(blob.byteOffset,blob.byteOffset+blob.length);}
      };},
      setTimeout(fn){fn();}
    }
  };
  const window={};
  vm.runInNewContext(code,{window,crypto:crypto.webcrypto,TextEncoder,URL,Date,Promise,console},{timeout:3000});
  return {render:window.SwrlzHtmlPublishReviewV1.render,document,sha,fetched:()=>fetched};
}
function find(el,predicate){
  if(predicate(el))return el;
  for(const child of el.children||[]){const found=find(child,predicate);if(found)return found;}
  return null;
}
async function verifyPublish(){
  const h=harness(),container=new Element("div",h.document);
  const data={
    repo:"kaministrator999-ui/Swrlzkamico",project:"sample",branch:"main",
    sourceSha:"a".repeat(40),indexGitBlobSha:h.sha,
    url:"https://kamiloki-swyrlz.hf.space/api/html-projects/sample/index.html",
    files:[{path:"index.html",bytes:45}],bytes:45,
    destinationPrefix:"published-html-projects/sample/"
  };
  const surface=h.render(container,data,{
    threadId:"thread-1",currentThread:()=>"thread-1",
    isLatest:()=>true,confirm:async()=>true
  });
  assert.ok(surface);
  const approve=find(surface,e=>e.textContent==="Approve publish");
  assert.ok(approve);
  await approve.listeners.click();
  for(let i=0;i<30;i++){
    if(find(surface,e=>e.textContent==="Open verified website"))break;
    await new Promise(resolve=>setTimeout(resolve,15));
  }
  assert.ok(find(surface,e=>e.textContent==="Open verified website"),"Expected verified live website link");
  assert.ok(find(surface,e=>String(e.textContent).includes("Exact committed HTML source")),"Expected integrity receipt");
  assert.equal(h.fetched(),1);
}
async function verifyCreate(){
  const h=harness(),container=new Element("div",h.document);
  const data={
    mode:"create",repo:"kaministrator999-ui/Swrlzkamico",project:"sample",branch:"main",
    sourceSha:"b".repeat(64),files:[{path:"index.html",bytes:42}],bytes:42,
    destinationPrefix:"html-projects/sample/"
  };
  const surface=h.render(container,data,{
    threadId:"thread-1",currentThread:()=>"thread-1",
    isLatest:()=>true,confirm:async()=>true
  });
  assert.ok(surface);
  assert.ok(find(surface,e=>e.textContent==="Approve GitHub commit"));
  const approve=find(surface,e=>e.textContent==="Approve GitHub commit");
  await approve.listeners.click();
  assert.equal(h.fetched(),0,"GitHub approval must not poll live deployment before second consent");
}
(async()=>{
  await verifyPublish();
  await verifyCreate();
  console.log("HTML_PROJECT_APPROVAL_BROWSER_CONTRACT_PASS");
})().catch(e=>{console.error(e);process.exitCode=1;});
