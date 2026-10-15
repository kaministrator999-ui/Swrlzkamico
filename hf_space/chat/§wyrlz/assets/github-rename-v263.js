/* v263 · Owner-confirmed GitHub rename; no implicit writes. */
(() => {
 "use strict";
 const seen=new Set();
 let active=null;
 function el(tag,props={},...children){
   const n=document.createElement(tag);
   for(const [key,value] of Object.entries(props)){
     if(key==="text")n.textContent=value;
     else if(key==="className")n.className=value;
     else n.setAttribute(key,value);
   }
   n.append(...children);return n;
 }
 function extract(prompt){
   const m=String(prompt||"").match(/\b(?:rename|move)\s+(?:the\s+file\s+|file\s+)?["'“]?([^\s"'“”<>?*|]{1,512})["'”]?\s+(?:to|as|into)\s+["'“]?([^\s"'“”<>?*|]{1,512})/i);
   const clean=x=>String(x||"").replace(/[.,!?;]+$/,"");
   return {source:m?clean(m[1]):"",destination:m?clean(m[2]):""};
 }
 async function post(route,value){
   const res=await fetch("/api/github/files/"+route,{
     method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json"},
     body:JSON.stringify(value),
   });
   const data=await res.json();
   if(!res.ok)throw Error(data.code||data.detail||"RENAME_ACTION_UNAVAILABLE");
   return data;
 }
 function open(detail){
   if(active)return;
   const dialog=el("dialog",{className:"github-general-dialog","aria-label":"Review GitHub file rename"});
   const heading=el("h2",{text:"Rename a GitHub file"});
   const explain=el("p",{text:"Move or rename an existing file in the selected repository in one atomic commit. Contents and Git file mode are preserved. Existing destinations cannot be overwritten."});
   const repo=el("div",{className:"github-general-repo",text:"Checking connected repository…"});
   const oldLabel=el("label",{text:"Existing file path"});
   const src=el("input",{type:"text",maxlength:"512",placeholder:"src/old-name.py"});
   const newLabel=el("label",{text:"New file path"});
   const dst=el("input",{type:"text",maxlength:"512",placeholder:"src/new-name.py"});
   const preview=el("pre",{className:"github-general-preview"});
   const status=el("p",{className:"github-general-status",role:"status","aria-live":"polite",text:"Checking authorization…"});
   const oauth=el("a",{href:"/api/github/start?access=public-write",text:"Authorize GitHub public-repository writing"});
   oauth.hidden=true;
   const prepare=el("button",{type:"button",text:"Prepare rename (no write)"});
   const confirm=el("button",{type:"button",text:"Confirm atomic rename"});
   const cancel=el("button",{type:"button",text:"Cancel"});
   const controls=el("div",{className:"github-general-buttons"},prepare,confirm,cancel);
   dialog.append(heading,explain,repo,oldLabel,src,newLabel,dst,preview,status,oauth,controls);
   document.body.append(dialog);dialog.showModal();active=dialog;
   const parsed=extract(detail.prompt);
   src.value=parsed.source;dst.value=parsed.destination;src.focus();
   let ticket=null,allowed=false;
   const reset=()=>{ticket=null;confirm.disabled=true;preview.textContent="";};
   [src,dst].forEach(x=>x.addEventListener("input",reset));
   prepare.disabled=true;confirm.disabled=true;
   cancel.addEventListener("click",()=>dialog.close());
   dialog.addEventListener("close",()=>{dialog.remove();if(active===dialog)active=null;});
   fetch("/api/github/files/rename-status",{credentials:"same-origin"})
     .then(async res=>{
       const data=await res.json();
       if(!res.ok)throw Error(data.detail||"STATUS_UNAVAILABLE");
       if(data.repo)repo.textContent="Repository: "+data.repo+(data.branch?" · "+data.branch:"");
       if(data.allowed){allowed=true;prepare.disabled=false;status.textContent="Review both paths. Nothing has changed on GitHub.";}
       else {
         status.textContent="GitHub rename unavailable: "+String(data.reason||"UNKNOWN");
         if(data.authorizeUrl==="/api/github/start?access=public-write")oauth.hidden=false;
       }
     }).catch(error=>{status.textContent="Cannot check GitHub permission: "+error.message;});
   prepare.addEventListener("click",async()=>{
     if(!allowed)return;
     reset();prepare.disabled=true;
     status.textContent="Verifying source blob, destination and current branch revision…";
     try{
       const ready=await post("prepare-rename",{sourcePath:src.value,destinationPath:dst.value});
       if(!dialog.open)return;
       ticket=ready.approvalToken;
       preview.textContent="Operation: ATOMIC RENAME_FILE\nRepository: "+ready.repo+
         "\nBranch: "+ready.branch+"\nFrom: "+ready.sourcePath+"\nTo: "+ready.destinationPath+
         "\nExisting blob: "+ready.sourceBlobSha+"\nGit mode: "+ready.sourceMode+
         "\nBytes: "+(ready.bytes==null?"Unavailable":ready.bytes)+
         "\nHEAD: "+ready.headSha+"\nOverwrite: NO"+
         "\n\nOne Git commit will move the same blob to the new path.";
       status.textContent="Prepared. No rename yet; confirm the exact change.";
       confirm.disabled=false;
     }catch(error){status.textContent="Cannot prepare rename: "+error.message;}
     finally{prepare.disabled=!allowed;}
   });
   confirm.addEventListener("click",async()=>{
     if(!ticket)return;
     const approvalToken=ticket;reset();prepare.disabled=true;
     status.textContent="Writing one rename commit and verifying the Git tree…";
     try{
       const receipt=await post("confirm-rename",{approvalToken,approved:true});
       if(!receipt.ok||!receipt.verified)throw Error("Rename not verified");
       status.textContent="Renamed and verified: "+receipt.sourcePath+" → "+receipt.destinationPath+
         " · commit "+receipt.commitSha;
       if(typeof receipt.url==="string"&&/^https:\/\/github\.com\/kaministrator999-ui\//.test(receipt.url)){
         status.append(el("a",{href:receipt.url,target:"_blank",rel:"noopener noreferrer",text:" Open renamed file"}));
       }
       if(receipt.widget&&window.SwrlzGithubRenameView?.render){
         const view=el("div",{className:"github-general-work-receipt"});
         if(window.SwrlzGithubRenameView.render(view,receipt.widget))dialog.insertBefore(view,controls);
       }
     }catch(error){status.textContent="Rename not verified: "+error.message+
       ". Check GitHub before retrying; no automatic retry.";}
     finally{prepare.disabled=!allowed;}
   });
 }
 window.addEventListener("swrlz:github-rename-proposal",event=>{
   const detail=event.detail||{},id=String(detail.requestId||"");
   if(!id||seen.has(id))return;
   seen.add(id);if(seen.size>100)seen.clear();
   open(detail);
 });
})();