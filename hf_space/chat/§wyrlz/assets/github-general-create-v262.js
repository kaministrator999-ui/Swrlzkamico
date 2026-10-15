/* v262 · Owner-reviewed GitHub CREATE_FILE for text/source and binary. */
(() => {
 "use strict";
 const MAX=1000000, handled=new Set();
 let dialog=null;
 const node=(tag,props={},...children)=>{
   const x=document.createElement(tag);
   for(const [k,v] of Object.entries(props)){
     if(k==="text")x.textContent=v;
     else if(k==="value")x.value=v;
     else if(k==="className")x.className=v;
     else x.setAttribute(k,v);
   }
   x.append(...children);return x;
 };
 const extract=prompt=>{
   const s=String(prompt||"");
   const named=s.match(/\b(?:named|called|path|filename)\s*[:=]?\s*["'“]?([^\s"'“”<>?*|]{1,512})/i);
   const file=s.match(/\b((?:[\w.-]+\/)*[\w.-]+\.[A-Za-z0-9_-]{1,15})\b/);
   const path=(named?.[1]||file?.[1]||"").replace(/[.,;!?]+$/,"");
   const labeled=s.match(/(?:^|\n)\s*(?:file\s+)?contents?\s*:\s*([\s\S]*)$/i);
   const quoted=s.match(/\b(?:containing|saying|with\s+the\s+text)\s+["'“]([^"'”]+)["'”]\s*[.!]?\s*$/i);
   return {path,text:labeled?.[1]||quoted?.[1]||""};
 };
 function toBase64(bytes){
   let output="";
   for(let i=0;i<bytes.length;i+=16384)output+=String.fromCharCode.apply(null,bytes.subarray(i,i+16384));
   return btoa(output);
 }
 async function post(action,payload){
   const response=await fetch("/api/github/files/"+action,{
     method:"POST",credentials:"same-origin",
     headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)
   });
   const result=await response.json();
   if(!response.ok)throw Error(result.code||result.detail||"GITHUB_ACTION_UNAVAILABLE");
   return result;
 }
 function open(detail){
   if(dialog)return;
   const form=node("dialog",{className:"github-general-dialog","aria-label":"Review GitHub file creation"});
   const heading=node("h2",{text:"Create a GitHub file"});
   const desc=node("p",{text:"One new file in your selected public owner repository. Source files, dotfiles, nested paths, images, PDFs and binary files are supported. No overwrites."});
   const location=node("div",{className:"github-general-repo",text:"Checking connected GitHub repository…"});
   const pathLabel=node("label",{text:"New repository path (example: src/app.py)"});
   const path=node("input",{type:"text",maxlength:"512",placeholder:"src/app.py"});
   const modeLabel=node("label",{text:"File contents"});
   const mode=node("select");
   mode.append(node("option",{value:"text",text:"Text / source / JSON / Markdown"}),
               node("option",{value:"binary",text:"Upload local file (binary / image / PDF)"}));
   const content=node("textarea",{rows:"7",placeholder:"Enter or paste exact file content"});
   const upload=node("input",{type:"file"});upload.hidden=true;
   const note=node("p",{className:"github-general-note",text:"Binary upload: 1,000,000 bytes maximum; exact bytes preserved."});note.hidden=true;
   const preview=node("pre",{className:"github-general-preview"});
   const status=node("p",{role:"status","aria-live":"polite",className:"github-general-status",text:"Checking authorization…"});
   const grant=node("a",{href:"/api/github/start?access=public-write",text:"Approve GitHub public-repository writing"});grant.hidden=true;
   const prepare=node("button",{type:"button",text:"Prepare preview"});
   const confirm=node("button",{type:"button",text:"Confirm this GitHub file"});
   const cancel=node("button",{type:"button",text:"Cancel"});
   const buttons=node("div",{className:"github-general-buttons"},prepare,confirm,cancel);
   const parsed=extract(detail.prompt);
   path.value=parsed.path;content.value=parsed.text;
   prepare.disabled=true;confirm.disabled=true;
   form.append(heading,desc,location,pathLabel,path,modeLabel,mode,content,upload,note,
               preview,status,grant,buttons);
   document.body.append(form);form.showModal();dialog=form;path.focus();
   let ticket=null,allowed=false;
   const reset=()=>{ticket=null;confirm.disabled=true;preview.textContent="";};
   [path,content,upload,mode].forEach(x=>x.addEventListener("input",reset));
   mode.addEventListener("change",()=>{
     const binary=mode.value==="binary";
     content.hidden=binary;upload.hidden=!binary;note.hidden=!binary;reset();
   });
   upload.addEventListener("change",()=>{
     if(upload.files?.length&&!path.value)path.value=upload.files[0].name;
     reset();
   });
   cancel.addEventListener("click",()=>form.close());
   form.addEventListener("close",()=>{form.remove();if(dialog===form)dialog=null;});
   fetch("/api/github/files/create-status",{credentials:"same-origin"})
    .then(async response=>{
      const info=await response.json();
      if(!response.ok)throw Error(info.detail||"STATUS_UNAVAILABLE");
      if(info.repo)location.textContent="Repository: "+info.repo+(info.branch?" · "+info.branch:"");
      if(info.allowed){allowed=true;prepare.disabled=false;status.textContent="Ready for review. No GitHub changes yet.";}
      else {
        status.textContent="Creation unavailable: "+String(info.reason||"UNKNOWN");
        if(info.authorizeUrl==="/api/github/start?access=public-write")grant.hidden=false;
      }
    }).catch(error=>{status.textContent="GitHub permission check failed: "+error.message;});
   prepare.addEventListener("click",async()=>{
     if(!allowed)return;
     reset();prepare.disabled=true;status.textContent="Preparing without writing…";
     try{
       let bytes,type;
       if(mode.value==="binary"){
         const file=upload.files?.[0];
         if(!file)throw Error("Choose a file to upload.");
         if(file.size>MAX)throw Error("File exceeds 1,000,000 bytes.");
         bytes=new Uint8Array(await file.arrayBuffer());
         type=file.type||"application/octet-stream";
       }else{
         bytes=new TextEncoder().encode(content.value);
         type="text/plain; charset=utf-8";
       }
       if(bytes.length>MAX)throw Error("File exceeds 1,000,000 bytes.");
       const result=await post("prepare-create",{path:path.value,contentBase64:toBase64(bytes),mediaType:type});
       if(!form.open)return;
       ticket=result.approvalToken;
       preview.textContent="Operation: CREATE_FILE\nRepository: "+result.repo+
         "\nBranch: "+result.branch+"\nPath: "+result.path+
         "\nBytes: "+result.bytes+"\nSHA-256: "+result.sha256+
         "\nType: "+result.mediaType+"\nOverwrite: NO"+
         "\n\nConfirm only if this exact file is authorized.";
       status.textContent="Proposal prepared. No file has been written.";
       confirm.disabled=false;
     }catch(error){status.textContent="Cannot prepare: "+error.message;}
     finally{prepare.disabled=!allowed;}
   });
   confirm.addEventListener("click",async()=>{
     if(!ticket)return;
     const approvalToken=ticket;reset();prepare.disabled=true;
     status.textContent="Creating file and verifying exact bytes on GitHub…";
     try{
       const receipt=await post("confirm-create",{approvalToken,approved:true});
       if(!receipt.ok||!receipt.verified)throw Error("Write not verified.");
       status.textContent="Created and verified: "+receipt.path+" · Commit: "+receipt.commitSha;
       if(typeof receipt.url==="string"&&/^https:\/\/github\.com\/kaministrator999-ui\//.test(receipt.url)){
         status.append(node("a",{href:receipt.url,target:"_blank",rel:"noopener noreferrer",text:" View file"}));
       }
     }catch(error){status.textContent="Not verified: "+error.message+". Inspect GitHub before retrying.";}
     finally{prepare.disabled=!allowed;}
   });
 }
 window.addEventListener("swrlz:github-general-create-proposal",event=>{
   const detail=event.detail||{};
   const id=String(detail.requestId||"");
   if(!id||handled.has(id))return;
   handled.add(id);if(handled.size>100)handled.clear();
   open(detail);
 });
})();