import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../runtime/chat_workspace_analysis_v11_178.js',import.meta.url),'utf8');
new vm.Script(source);
const ui={},sent=[],statuses=[];
const element=(tag)=>({tagName:tag,attrs:{},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,f){this[k]=f},after(child){ui[child.id]=child}});
ui.seChatRefresh=element('button');
let account=true,visible=true,ready=true;
const ctx={
  projectId:'p123',project:{name:'Sheep Tag'},workspace:'scene',selectedId:'sel',
  actors:[
    {id:'sel',name:'Menu house',type:'building',position:[0,0,0]},
    {id:'a2',name:'Menu house',type:'building',position:[0,0,0]},
    {id:'a3',name:'Menu sheep',type:'character',position:[2,0,1]},
    {id:'a4',name:'Menu wolf',type:'character',position:[3,0,1]},
  ],totalActors:40
};
const sandbox={document:{createElement:element,getElementById:k=>ui[k]||null},
  get se176AccountConnected(){return account},get ready(){return ready},
  isVisible:()=>visible,context:()=>ctx,send:(type,payload)=>sent.push({type,payload}),setStatus:(s,error=false)=>statuses.push({s,error}),
  summaryName:String,TextEncoder,Number,Map,Array,JSON,String,Error};
const vmctx=vm.createContext(sandbox);vm.runInContext(source,vmctx);
vm.runInContext('se178Install()',vmctx);
const button=ui.se178Analyze;assert(button);
vm.runInContext('se178EnrichContext',vmctx)(ctx);
assert.equal(ctx.workspaceAudit.sampled,4);
assert.equal(ctx.workspaceAudit.types.find(x=>x.name==='building').count,2);
assert.equal(ctx.workspaceAudit.findings.some(x=>x.code==='duplicate-name'),true);
assert.equal(ctx.workspaceAudit.findings.some(x=>x.code==='shared-position'),true);
assert(!('operations' in ctx.workspaceAudit));
button.click();
assert.equal(sent.length,1);
assert.equal(sent[0].type,'host.analyze');
assert.equal(Object.keys(sent[0].payload).length,0,'no untrusted scene prompt to Chat');
account=false;button.click();assert.equal(sent.length,1,'not signed in');
account=true;visible=false;button.click();assert.equal(sent.length,1,'hidden editor blocked');
visible=true;ready=false;button.click();assert.equal(sent.length,1,'disconnected Chat blocked');
const huge={...ctx,actors:Array.from({length:48},(_,i)=>({name:'a'.repeat(100),type:'mesh',position:[i,0,1]})),project:{name:'X'.repeat(30000)}};
delete huge.workspaceAudit;vm.runInContext('se178EnrichContext',vmctx)(huge);assert.equal(huge.workspaceAudit,undefined,'large source snapshot does not overflow lease');
console.log(JSON.stringify({ok:true,suite:'forge-v11-178-workspace-analysis',checks:13}));
