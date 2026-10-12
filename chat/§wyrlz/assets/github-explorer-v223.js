/* §wyrlz Stage-1 GitHub Explorer v223. Authenticated, read-only.
   Source metadata is rendered with textContent, never source-controlled HTML. */
(function(){
"use strict";
const historyCache = new Map();
const stateCache = new Map();
const MAX_CACHE=30;
const css=`
.repo-explorer{border:1px solid rgba(125,207,255,.27);border-radius:14px;padding:12px;margin:8px 0;background:rgba(2,16,30,.93);color:#e7f4ff;min-width:0;box-sizing:border-box}
.repo-explorer *{box-sizing:border-box}
.repo-explorer-header,.repo-explorer-controls,.repo-explorer-actions{display:flex;align-items:center;flex-wrap:wrap;gap:7px}
.repo-explorer-header{justify-content:space-between}
.repo-explorer-title{font-size:15px;font-weight:750;min-width:0;overflow-wrap:anywhere}
.repo-explorer-meta{font-size:11px;color:#a7c7da;overflow-wrap:anywhere;margin:7px 0}
.repo-explorer button,.repo-explorer select,.repo-explorer input{background:rgba(8,36,57,.93);border:1px solid rgba(126,214,255,.29);color:#e8f6ff;border-radius:9px;padding:7px 9px;min-height:35px;font-size:12px}
.repo-explorer button{cursor:pointer}
.repo-explorer button:focus-visible,.repo-explorer select:focus-visible,.repo-explorer input:focus-visible{outline:2px solid #76deff;outline-offset:1px}
.repo-explorer button:disabled{opacity:.6;cursor:default}
.repo-explorer .repo-crumbs{display:flex;flex-wrap:wrap;gap:3px;margin:5px 0}
.repo-explorer .repo-crumbs button{border:0;background:transparent;color:#93d9ff;min-height:25px;padding:3px 5px}
.repo-explorer .repo-summary{display:flex;gap:6px;flex-wrap:wrap;margin:9px 0}
.repo-explorer .repo-stat{padding:7px 10px;border-radius:9px;background:rgba(87,148,181,.12);font-size:12px;flex:1 1 76px;min-width:65px}
.repo-explorer .repo-stat strong{display:block;font-size:15px}
.repo-explorer .repo-explorer-controls select{flex:1 1 105px;min-width:90px}
.repo-explorer .repo-explorer-controls input{flex:2 1 125px;min-width:110px}
.repo-explorer .repo-explorer-list{max-height:210px;overflow:auto;overscroll-behavior:contain}
.repo-explorer.expanded .repo-explorer-list{max-height:min(67dvh,650px)}
.repo-explorer.fullscreen{position:fixed;inset:8px;max-height:calc(100dvh - 16px);overflow:auto;z-index:9999;box-shadow:0 0 0 100vmax rgba(0,0,0,.82)}
.repo-explorer.fullscreen .repo-explorer-list{max-height:calc(100dvh - 355px)}
.repo-explorer .repo-explorer-entry{display:flex;align-items:center;gap:8px;border-bottom:1px solid rgba(126,214,255,.11);padding:7px 2px;min-width:0}
.repo-explorer .repo-entry-name{flex:1;min-width:0;overflow-wrap:anywhere;font-size:13px}
.repo-explorer .repo-entry-detail{display:block;color:#97b8ca;font-size:11px;margin-top:2px}
.repo-explorer .repo-explorer-entry button{flex-shrink:0;padding:5px 7px;font-size:11px}
.repo-explorer .repo-alert{font-size:12px;margin:8px 0;color:#ffcc86}
.repo-explorer .repo-panel{margin-top:9px;border:1px solid rgba(109,192,240,.2);padding:9px;border-radius:10px;min-width:0}
.repo-explorer .repo-code{overflow:auto;white-space:pre;tab-size:2;max-height:54dvh;max-width:100%;font:12px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace}
.repo-explorer .repo-code .repo-keyword{color:#92bcff}.repo-explorer .repo-code .repo-string{color:#a4e0ac}
.repo-explorer .repo-code .repo-comment{color:#90a2ac}.repo-explorer .repo-code .repo-number{color:#ffbc83}
.repo-explorer .repo-panel-head{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}
.repo-explorer .repo-panel-head strong{overflow-wrap:anywhere}
@media(max-width:430px){.repo-explorer{padding:9px}.repo-explorer .repo-explorer-entry button{padding:5px}.repo-explorer .repo-stat{min-width:58px}.repo-explorer .repo-explorer-controls{gap:5px}}
`;
const style=document.createElement("style");
style.textContent=css;document.head.appendChild(style);
const el=(tag,cls="",content)=>{
  const node=document.createElement(tag);
  if(cls)node.className=cls;
  if(content!==undefined)node.textContent=String(content);
  return node;
};
const btn=(label,handler)=>{const x=el("button","",label);x.type="button";x.onclick=handler;return x;};
const safeCopy=async(raw,node)=>{
  try{await navigator.clipboard.writeText(String(raw));node.textContent="Copied";}catch(_){node.textContent="Copy unavailable";}
};
const bytes=n=>Number.isFinite(n)?(n>=1048576?(n/1048576).toFixed(1)+" MiB":n>=1024?(n/1024).toFixed(1)+" KiB":n+" B"):"Size unknown";
const when=date=>date?new Date(date).toLocaleString():"Date unavailable";
async function request(path,params){
  const query=new URLSearchParams(params||{});
  const reply=await fetch("/api/github/explorer/"+path+"?"+query.toString(),{credentials:"same-origin",cache:"no-store"});
  const data=await reply.json().catch(()=>({}));
  if(!reply.ok)throw new Error(String(data.detail||"GitHub source lookup failed").slice(0,200));
  return data;
}
const keyWords=/\b(?:def|class|return|import|from|for|while|if|else|elif|try|except|finally|with|async|await|lambda|True|False|None|const|let|var|function|export|default|new|throw|switch|case|break|continue|public|private|static|void|int|string|interface|type|extends|implements|package|fun|val|object)\b|\b\d+(?:\.\d+)?\b|#[^\n]*|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g;
function highlight(pre,text){
  const code=el("code");const input=String(text||"");let index=0,match;
  keyWords.lastIndex=0;
  while((match=keyWords.exec(input))){
    if(match.index>index)code.appendChild(document.createTextNode(input.slice(index,match.index)));
    const value=match[0],klass=value.startsWith("//")||value.startsWith("#")?"repo-comment":value.startsWith('"')||value.startsWith("'")?"repo-string":/^\d/.test(value)?"repo-number":"repo-keyword";
    code.appendChild(el("span",klass,value));index=keyWords.lastIndex;
  }
  if(index<input.length)code.appendChild(document.createTextNode(input.slice(index)));
  pre.replaceChildren(code);
}
function parseListing(source){
  const lines=String(source||"").trim().split(/\r?\n/);
  const heading=lines[0]?.match(/^(?:##\s*)?GitHub directory:\s*(\/[^\n]*)$/);
  if(!heading||lines.length>3000)return null;
  const items=[];
  for(const line of lines.slice(1)){
    if(!line.trim()||/^\(First \d+ entries\.\)$/.test(line.trim()))continue;
    const entry=line.match(/^\s*[-*•]\s*(dir|file)\s+(.+?)\s*$/i);
    if(!entry)return null;
    const path=entry[2].trim();
    if(!path||path.length>220||path.includes("<")||path.includes(">"))return null;
    items.push({path,type:entry[1].toLowerCase(),name:path.split("/").pop(),sizeBytes:null});
  }
  if(!items.length)return null;
  return {path:heading[1].replace(/^\/|\/$/g,""),entries:items,
    incomplete:/\(First \d+ entries\.\)/.test(source)};
}
function render(container,source,options={}){
  const listing=parseListing(source);
  if(!listing)return false;
  const identity=String(options.accountId?.()||"anonymous");
  const thread=String(options.threadId?.()||"");
  const key=identity+"|"+thread+"|"+String(options.messageId||"");
  let state=stateCache.get(key);
  if(!state){
    state={path:listing.path,items:listing.entries,info:null,search:false,query:"",
           opened:"",content:null,history:null,compare:null,sort:"name",filter:"all",expanded:false,
           fullscreen:false,dates:new Map(),sourcePath:listing.path,incomplete:listing.incomplete};
    if(stateCache.size>=MAX_CACHE)stateCache.delete(stateCache.keys().next().value);
    stateCache.set(key,state);
  }
  const card=el("section","repo-explorer");
  card.setAttribute("aria-label","GitHub repository explorer");
  if(state.expanded)card.classList.add("expanded");
  if(state.fullscreen)card.classList.add("fullscreen");
  const title=el("strong","repo-explorer-title","📁 GitHub · /"+state.path);
  const controlsHead=el("div","repo-explorer-header");
  const full=btn(state.fullscreen?"Close full screen":"⛶ Full screen",()=>{
    state.fullscreen=!state.fullscreen;card.classList.toggle("fullscreen",state.fullscreen);
    full.textContent=state.fullscreen?"Close full screen":"⛶ Full screen";
  });
  controlsHead.append(title,full);
  const meta=el("div","repo-explorer-meta","");
  const crumbs=el("div","repo-crumbs");
  const summary=el("div","repo-summary");
  const controls=el("div","repo-explorer-controls");
  const sort=el("select");sort.setAttribute("aria-label","Sort GitHub files");
  [["name","Name A–Z"],["name-desc","Name Z–A"],["type","Type"],["size","Size"],["files","File count"],["modified","Last changed"]]
    .forEach(([v,t])=>sort.add(new Option(t,v)));
  sort.value=state.sort;
  const filter=el("select");filter.setAttribute("aria-label","Filter GitHub files");
  [["all","All items"],["file","Files only"],["dir","Folders only"]].forEach(([v,t])=>filter.add(new Option(t,v)));
  filter.value=state.filter;
  const search=el("input");search.type="search";search.placeholder="Filter names";search.maxLength=100;
  search.value=state.query;search.setAttribute("aria-label","Filter repository entries");
  const deepSearch=btn("Find in repo",()=>runSearch(search.value));
  const expand=btn(state.expanded?"Collapse":"Expand",()=>{
    state.expanded=!state.expanded;card.classList.toggle("expanded",state.expanded);
    expand.textContent=state.expanded?"Collapse":"Expand";
  });
  controls.append(sort,filter,search,deepSearch,expand);
  const status=el("div","repo-alert");
  const list=el("div","repo-explorer-list");list.tabIndex=0;
  const detail=el("div","repo-panel");detail.hidden=true;
  const actions=el("div","repo-explorer-actions");
  const refresh=btn("↻ Refresh metadata",()=>loadDir(state.path));
  const copyList=btn("Copy listing",()=>safeCopy(state.items.map(x=>x.path).join("\n"),copyList));
  const compare=btn("Compare refs",()=>openCompare());
  actions.append(refresh,copyList,compare);
  card.append(controlsHead,meta,crumbs,summary,controls,list,actions,detail,status);
  container.appendChild(card);
  let pending=null;
  const notice=t=>{if(card.isConnected)status.textContent=String(t||"");};
  const currentBranch=()=>state.info?.branch||"";
  function prepare(text){
    if(typeof options.preparePrompt==="function")options.preparePrompt(text);
    else safeCopy(text,el("button"));
  }
  async function context(path,kind){
    const id=String(options.threadId?.()||"");
    if(!id||!state.info)return;
    try{
      const result=await fetch("/api/lalm_station/github-context",{
        method:"POST",credentials:"same-origin",cache:"no-store",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({threadId:id,path,kind,branch:currentBranch(),sourceSha:state.info.sourceSha})});
      if(!result.ok)notice("View updated; conversation context could not be saved. Use a Chat read command to establish it.");
      else options.contextUpdated?.(state.info.repository,currentBranch(),path);
    }catch(_){notice("View updated, but conversation context is not yet durable.");}
  }
  function breadcrumbs(){
    crumbs.replaceChildren();
    const parts=state.path?state.path.split("/"):[];
    const root=btn("⌂ root",()=>loadDir(""));
    crumbs.appendChild(root);
    for(let i=0;i<parts.length;i++){
      const piece=parts.slice(0,i+1).join("/");
      crumbs.appendChild(el("span",""," › "));
      crumbs.appendChild(btn(parts[i],()=>loadDir(piece)));
    }
  }
  function stats(){
    summary.replaceChildren();
    const info=state.info?.stats;
    const total=state.items.length;
    const fields=info?[
      ["Files",info.recursiveFiles],["Folders",info.recursiveDirectories],["Git blobs",bytes(info.gitBlobBytes)]
    ]:[
      ["Displayed",total],["Folders",state.items.filter(x=>x.type==="dir").length],["Files",state.items.filter(x=>x.type==="file").length]
    ];
    for(const [label,n] of fields){
      const b=el("div","repo-stat");b.append(el("strong","",n),el("span","",label));summary.appendChild(b);
    }
    title.textContent="📁 GitHub · /"+state.path;
    const inf=state.info;
    meta.textContent=inf?(inf.repository+" · "+inf.branch+" · "+inf.sourceSha.slice(0,12)+" · "+state.items.length+" direct entries"):
      ("Initial GitHub listing · "+total+" shown"+(state.incomplete?" · partial":"")+" · select Refresh metadata for exact recursive totals");
  }
  async function loadDir(path){
    if(pending)return;
    pending="directory";notice("Verifying repository tree…");
    try{
      const d=await request("directory",{path,branch:currentBranch()});
      if(state.info&&state.info.repository!==d.repository)throw Error("The selected GitHub repository changed. Reopen its listing.");
      state.info=d;state.path=d.path;state.items=d.entries;state.opened="";state.search=false;
      state.content=null;state.history=null;state.dates=new Map();state.query="";
      search.value="";detail.hidden=true;breadcrumbs();stats();renderRows();notice("");
      await context(d.path,"dir");
    }catch(e){notice(e.message||"Repository metadata unavailable");}
    finally{pending=null;}
  }
  async function runSearch(term){
    const value=String(term||"").trim();
    if(value.length<2){notice("Enter at least two characters to search filenames.");return;}
    if(!state.info){await loadDir(state.path);if(!state.info)return;}
    notice("Searching verified filenames…");
    try{
      const result=await request("search",{q:value,branch:currentBranch()});
      if(result.repository!==state.info.repository)throw Error("Selected repository changed");
      state.items=result.matches.map(x=>({...x,name:x.path.split("/").pop()}));
      state.search=true;state.query=value;search.value=value;
      renderRows();stats();
      notice(result.total+" verified matching paths"+(result.truncatedResults?" · first 50 shown":"")+" · Back to folder to clear search");
    }catch(e){notice(e.message);}
  }
  async function loadChangedDates(rows){
    if(rows.length>24){notice("Too many entries for complete date sorting. Open a smaller folder first.");sort.value="name";state.sort="name";return;}
    notice("Checking last path commits for "+rows.length+" entries…");
    for(const x of rows){
      if(state.dates.has(x.path))continue;
      try{
        const d=await request("modified",{path:x.path,branch:currentBranch()});
        if(d.sourceSha!==state.info.sourceSha)throw Error("Repository advanced; refresh before sorting");
        state.dates.set(x.path,d.lastChangedAt||"");
      }catch(_){state.dates.set(x.path,"");}
    }
    if(rows.some(x=>!state.dates.get(x.path))){
      notice("Some commit dates were unavailable; chronological sorting cannot be certified.");
      sort.value="name";state.sort="name";
    }else notice("Sorted by verified last path commits (not filesystem modification timestamps).");
    renderRows();
  }
  function rowFor(item){
    const row=el("div","repo-explorer-entry");
    const name=el("div","repo-entry-name",item.type==="dir"?"📁 "+item.name:"📄 "+item.name);
    const lines=[];
    if(Number.isFinite(item.sizeBytes))lines.push(bytes(item.sizeBytes));
    if(Number.isInteger(item.fileCount))lines.push(item.fileCount+" files");
    if(Number.isInteger(item.directoryCount))lines.push(item.directoryCount+" folders");
    const date=state.dates.get(item.path);
    if(date)lines.push("Changed "+when(date));
    if(lines.length)name.appendChild(el("small","repo-entry-detail",lines.join(" · ")));
    const open=btn(item.type==="dir"?"Browse":"Open",()=>item.type==="dir"?loadDir(item.path):openFile(item));
    const copy=btn("Copy",()=>safeCopy(item.path,copy));
    row.append(name,open,copy);return row;
  }
  function renderRows(){
    list.replaceChildren();
    const scope=state.items.filter(x=>filter.value==="all"||x.type===filter.value);
    const term=state.search?"":search.value.trim().toLowerCase();
    const rows=scope.filter(x=>!term||x.path.toLowerCase().includes(term));
    const type=sort.value;
    rows.sort((a,b)=>{
      if(type==="type")return a.type.localeCompare(b.type)||a.path.localeCompare(b.path);
      if(type==="size")return (b.sizeBytes??-1)-(a.sizeBytes??-1)||a.path.localeCompare(b.path);
      if(type==="files")return (b.fileCount??-1)-(a.fileCount??-1)||a.path.localeCompare(b.path);
      if(type==="modified")return (state.dates.get(b.path)||"").localeCompare(state.dates.get(a.path)||"")||a.path.localeCompare(b.path);
      return type==="name-desc"?b.name.localeCompare(a.name):a.name.localeCompare(b.name);
    });
    for(const item of rows)list.appendChild(rowFor(item));
    if(!rows.length)list.appendChild(el("div","repo-explorer-meta","No matching entries."));
  }
  async function openFile(item){
    detail.hidden=false;detail.replaceChildren(el("div","repo-explorer-meta","Loading bounded source…"));
    try{
      if(!state.info)await loadDir(state.path);
      const data=await request("file",{path:item.path,branch:currentBranch()});
      state.opened=item.path;state.content=data;
      detail.replaceChildren();
      const head=el("div","repo-panel-head");
      head.appendChild(el("strong","",item.path));
      const close=btn("Close",()=>{detail.hidden=true;state.opened="";});
      head.appendChild(close);detail.appendChild(head);
      detail.appendChild(el("div","repo-explorer-meta",bytes(data.sizeBytes)+" · revision "+String(data.sourceSha||"").slice(0,12)));
      const buttons=el("div","repo-explorer-actions");
      const inChat=btn("Ask about file",()=>prepare("Explain "+item.path+" in our GitHub repository"));
      const history=btn("Dates / history",()=>openHistory(item.path));
      buttons.append(inChat,history);
      if(data.readable){
        const copy=btn("Copy code",()=>safeCopy(data.content,copy));
        buttons.appendChild(copy);
      }
      detail.appendChild(buttons);
      if(data.readable){
        const pre=el("pre","repo-code");pre.tabIndex=0;
        highlight(pre,data.content);detail.appendChild(pre);
      }else detail.appendChild(el("div","repo-alert",data.message||"Source not available for text preview."));
      await context(item.path,"file");
    }catch(e){detail.replaceChildren(el("div","repo-alert",e.message||"File could not be read"));}
  }
  async function openHistory(path){
    if(!state.info)await loadDir(state.path);
    detail.hidden=false;
    detail.appendChild(el("div","repo-explorer-meta","Checking GitHub commits for this path…"));
    try{
      const data=await request("history",{path,branch:currentBranch()});
      const block=el("div","repo-panel");
      block.appendChild(el("strong","", "Git commit history: "+path));
      block.appendChild(el("div","repo-explorer-meta","Last path change: "+when(data.lastCommit?.date)));
      block.appendChild(el("div","repo-explorer-meta","First visible path commit: "+
         (data.firstSeenComplete?when(data.firstSeenPathCommit?.date):"Unverified (history scan incomplete)")));
      block.appendChild(el("div","repo-explorer-meta",data.caution));
      const close=btn("Close history",()=>block.remove());
      block.appendChild(close);detail.appendChild(block);
    }catch(e){detail.appendChild(el("div","repo-alert",e.message));}
  }
  async function openCompare(){
    detail.hidden=false;detail.replaceChildren();
    const head=el("div","repo-panel-head");head.appendChild(el("strong","","Compare GitHub refs"));
    head.appendChild(btn("Close",()=>{detail.hidden=true;}));detail.appendChild(head);
    const base=el("input");base.placeholder="Base branch";base.value=currentBranch()||"main";base.maxLength=120;
    const compareTo=el("input");compareTo.placeholder="Head branch";compareTo.maxLength=120;
    const results=el("div","repo-explorer-meta");
    const check=btn("Compare",async()=>{
      results.textContent="Reading branch comparison…";
      try{
        const data=await request("compare",{base:base.value.trim(),head:compareTo.value.trim()});
        results.replaceChildren(el("div","repo-explorer-meta",data.caution));
        for(const item of data.files){
          const sec=el("details");const sum=el("summary","",item.status+" · "+item.path+" (+"+item.additions+"/-"+item.deletions+")");
          sec.appendChild(sum);
          const pre=el("pre","repo-code");pre.textContent=item.patch||"Patch unavailable";sec.appendChild(pre);
          results.appendChild(sec);
        }
      }catch(e){results.textContent=e.message;}
    });
    const row=el("div","repo-explorer-controls");row.append(base,compareTo,check);
    detail.append(row,results);
  }
  breadcrumbs();stats();renderRows();
  sort.onchange=async()=>{
    state.sort=sort.value;
    if(sort.value==="modified"&&state.info){
      await loadChangedDates(state.items.filter(x=>filter.value==="all"||x.type===filter.value));
    }else if((sort.value==="size"||sort.value==="files")&&!state.info){
      await loadDir(state.path);renderRows();
    }else renderRows();
  };
  filter.onchange=()=>{state.filter=filter.value;renderRows();};
  search.oninput=()=>{state.query=search.value;if(!state.search)renderRows();};
  const footer=el("div","repo-explorer-meta","Read-only · Git blob sizes exclude history and LFS. GitHub dates refer to commits, not filesystem timestamps.");
  card.appendChild(footer);
  if(state.info){breadcrumbs();stats();renderRows();}
  return true;
}
window.SwrlzGitHubExplorerV223={render,version:"223",reset:()=>{historyCache.clear();stateCache.clear();}};
})();