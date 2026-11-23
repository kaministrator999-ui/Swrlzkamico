/* §C GitHub change review: presentation only; authorization stays server-side. */
(function(root){
  "use strict";
  const MAX_AGE_MS=300000;
  function render(container,proposal,options={}){
    if(!container||!proposal||!["CREATE_FILE","UPDATE_FILE"].includes(proposal.operation)
      ||typeof proposal.repo!=="string"||typeof proposal.branch!=="string"
      ||typeof proposal.path!=="string"||typeof proposal.content!=="string"
      ||typeof options.confirm!=="function")return false;
    const doc=container.ownerDocument;
    const createdAt=Date.now(), thread=String(options.threadId||"");
    const wrapper=doc.createElement("section");
    wrapper.className="swrlz-github-change-review";
    const title=doc.createElement("h3");
    title.textContent=proposal.operation==="CREATE_FILE"?"Review new GitHub file":"Review GitHub file edit";
    wrapper.append(title);
    for(const [label,value] of [["Repository",proposal.repo],["Branch",proposal.branch],["File",proposal.path],["Action",proposal.operation],["SHA-256",proposal.sha256||""]]){
      const row=doc.createElement("p"),strong=doc.createElement("strong");
      strong.textContent=label+": ";row.append(strong,doc.createTextNode(String(value).slice(0,400)));wrapper.append(row);
    }
    const preview=doc.createElement("pre");
    preview.className="swrlz-github-change-source";
    preview.textContent=proposal.content;
    wrapper.append(preview);
    if(proposal.operation==="UPDATE_FILE"){
      const diff=doc.createElement("pre");
      diff.className="swrlz-github-change-diff";
      diff.textContent=String(proposal.diff||"No textual differences");
      const old=doc.createElement("details"),oldTitle=doc.createElement("summary"),oldSource=doc.createElement("pre");
      oldTitle.textContent="View original file";oldSource.textContent=String(proposal.before||"");
      old.append(oldTitle,oldSource);
      wrapper.append(diff,old);
    }
    const note=doc.createElement("p");
    note.setAttribute("role","status");
    note.setAttribute("aria-live","polite");
    note.textContent="No repository changes have been made. Review before approval.";
    wrapper.append(note);
    const reject=doc.createElement("button"),approve=doc.createElement("button");
    reject.type=approve.type="button";
    reject.textContent="Reject";approve.textContent="Approve change";
    let pending=false, settled=false;
    const onReceipt=event=>{
      const receipt=event&&event.detail||{};
      if(!pending||settled||String(receipt.threadId||"")!==thread
        ||String(receipt.path||"")!==proposal.path
        ||String(receipt.repo||"")!==proposal.repo
        ||String(receipt.branch||"")!==proposal.branch)return;
      if(receipt.verified!==true||receipt.operation!==proposal.operation)return;
      settled=true;pending=false;
      note.textContent=receipt.operation==="CREATE_FILE"
        ?"File created and exact bytes verified by GitHub."
        :"File updated and exact bytes verified by GitHub.";
      wrapper.setAttribute("data-review-state","verified");
      approve.hidden=reject.hidden=true;
      if(typeof root.removeEventListener==="function")
        root.removeEventListener("swrlz-github-write-receipt",onReceipt);
    };
    if(typeof root.addEventListener==="function")
      root.addEventListener("swrlz-github-write-receipt",onReceipt);
    const act=async accepted=>{
      const latest=typeof options.isLatest==="function"&&options.isLatest(wrapper);
      const current=typeof options.currentThread==="function"&&String(options.currentThread())===thread;
      if(!latest||!current||Date.now()-createdAt>MAX_AGE_MS||approve.disabled){
        approve.disabled=reject.disabled=true;
        note.textContent="Review expired or changed. Request a new proposal.";
        return;
      }
      approve.disabled=reject.disabled=true;
      note.textContent=accepted?"Submitting approval to §C…":"Submitting rejection to §C…";
      try{
        const result=await options.confirm(accepted);
        if(result){
          pending=accepted;
          note.textContent=accepted
            ?"Approval sent. Checking GitHub verification receipt below…"
            :"Rejection submitted. No file change was approved.";
          wrapper.setAttribute("data-review-state",accepted?"submitted":"rejected");
          if(!accepted)approve.hidden=reject.hidden=true;
        }else{
          note.textContent="Decision not confirmed. No change assumed.";
          approve.disabled=reject.disabled=false;
        }
      }catch(_){
        pending=false;
        note.textContent="Decision failed. No change assumed.";
        approve.disabled=reject.disabled=false;
      }
    };
    approve.addEventListener("click",()=>act(true));
    reject.addEventListener("click",()=>act(false));
    wrapper.append(reject,approve);
    container.append(wrapper);
    return wrapper;
  }
  root.SwrlzGithubChangeReviewV1=Object.freeze({render});
})(typeof window!=="undefined"?window:globalThis);
