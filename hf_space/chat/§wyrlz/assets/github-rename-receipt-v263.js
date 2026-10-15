/* v263 · Display an atomic, verified file-rename GitHub work receipt. */
(() => {
 "use strict";
 const el=(tag,cls,text)=>{
   const n=document.createElement(tag);if(cls)n.className=cls;
   if(text!==undefined&&text!==null)n.textContent=String(text);
   return n;
 };
 const repoOK=r=>/^(?:kaministrator999-ui)\/(?:Swrlzing-core|Swrlzkamico)$/.test(String(r||""));
 const pathOK=p=>typeof p==="string"&&p.length>0&&p.length<=512&&!p.startsWith("/")&&!p.endsWith("/")
   &&!p.includes("//")&&!p.includes("\\")&&p.split("/").every(x=>x&&x!=="."&&x!==".."&&x.toLowerCase()!==".git");
 const encodePath=p=>p.split("/").map(encodeURIComponent).join("/");
 function render(host,widget){
   if(!host||widget?.contract!=="swrlz-widget-v1"||widget.kind!=="github-rename")return false;
   const d=widget.data||{};
   if(d.operation!=="RENAME_FILE"||d.verification!=="IDENTICAL_BLOB_AND_MODE"
     ||d.atomic!==true||d.overwritten!==0||!repoOK(d.repo)
     ||!pathOK(d.sourcePath)||!pathOK(d.destinationPath)||d.sourcePath===d.destinationPath
     ||typeof d.branch!=="string"||!/^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$/.test(d.branch)
     ||d.branch.split("/").some(x=>!x||x==="."||x==="..")
     ||!(/^[0-9a-fA-F]{40}$/.test(String(d.commitSha||"")))
     ||!(/^[0-9a-fA-F]{40}$/.test(String(d.blobSha||""))))return false;
   const link="https://github.com/"+d.repo+"/blob/"+encodePath(d.branch)+"/"+encodePath(d.destinationPath);
   const commit="https://github.com/"+d.repo+"/commit/"+d.commitSha;
   if(d.fileUrl!==link||d.commitUrl!==commit)return false;
   const card=el("div","github-work-dashboard");
   card.setAttribute("aria-label","Verified GitHub file rename");
   const title=el("div","github-work-summary");
   const head=el("div","github-work-heading");
   head.append(el("span","github-work-eyebrow","GITHUB · WORK RECEIPT"),
               el("strong","github-work-title","File renamed"));
   title.append(head,el("span","github-work-verified","✓ Blob & mode preserved"));
   card.append(title,el("div","github-work-repo",d.repo.replace("/"," / ")+" · "+d.branch));
   const from=el("div","github-work-repo","From: "+d.sourcePath);
   const to=el("a","github-work-file","To: "+d.destinationPath);
   to.href=link;to.rel="noopener noreferrer";to.target="_blank";
   card.append(from,to);
   const grid=el("div","github-work-metrics");
   const metric=(label,value)=>{
     const box=el("div","github-work-metric");
     box.append(el("span","github-work-metric-label",label),el("strong","github-work-metric-value",value));
     grid.append(box);
   };
   metric("Files renamed",1);
   metric("Overwritten",0);
   if(Number.isSafeInteger(d.bytesPreserved)&&d.bytesPreserved>=0)metric("Bytes preserved",d.bytesPreserved);
   metric("Atomic commit","Yes");
   card.append(grid);
   const foot=el("div","github-work-footer");
   const commitRef=el("a","github-work-commit","Commit "+d.commitSha.slice(0,7));
   commitRef.href=commit;commitRef.target="_blank";commitRef.rel="noopener noreferrer";
   foot.append(commitRef,el("span","github-work-stat-note","Source removed · target holds identical Git blob SHA"));
   card.append(foot);host.append(card);return true;
 }
 window.SwrlzGithubRenameView=Object.freeze({render});
})();