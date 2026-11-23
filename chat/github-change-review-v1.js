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
    const note=doc.createElement("p");
    note.textContent="No repository changes have been made. Review before approval.";
    wrapper.append(note);
    const reject=doc.createElement("button"),approve=doc.createElement("button");
    reject.type=approve.type="button";
    reject.textContent="Reject";approve.textContent="Approve change";
    const act=async accepted=>{
      const latest=typeof options.isLatest==="function"&&options.isLatest(wrapper);
      const current=typeof options.currentThread==="function"&&String(options.currentThread())===thread;
      if(!latest||!current||Date.now()-createdAt>MAX_AGE_MS||approve.disabled){
        approve.disabled=reject.disabled=true;
        note.textContent="Review expired or changed. Request a new proposal.";
        return;
      }
      approve.disabled=reject.disabled=true;
      try{
        const result=await options.confirm(accepted);
        note.textContent=result?"Decision submitted. Await server verification.":"Decision not confirmed. No change assumed.";
        if(!result)approve.disabled=reject.disabled=false;
      }catch(_){
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
