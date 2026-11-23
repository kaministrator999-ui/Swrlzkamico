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
    wrapper.dataset.reviewPath=proposal.path;
    wrapper.dataset.reviewOperation=proposal.operation;
    wrapper.dataset.reviewThread=thread;
    const title=doc.createElement("h3");
    title.textContent=proposal.operation==="CREATE_FILE"?"Review new GitHub file":"Review GitHub file edit";
    wrapper.append(title);
    const summary=doc.createElement("p");
    summary.className="swrlz-github-change-summary";
    summary.textContent=(proposal.operation==="CREATE_FILE"?"Create ":"Update ")+proposal.path+" · "+proposal.branch;
    wrapper.append(summary);
    for(const [label,value] of [["Repository",proposal.repo],["Branch",proposal.branch],["File",proposal.path],["Action",proposal.operation],["SHA-256",proposal.sha256||""]]){
      const row=doc.createElement("p"),strong=doc.createElement("strong");
      strong.textContent=label+": ";row.append(strong,doc.createTextNode(String(value).slice(0,400)));wrapper.append(row);
    }
    const reviewDetails=doc.createElement("details");
    reviewDetails.className="swrlz-github-change-details";
    const reviewHeading=doc.createElement("summary");
    reviewHeading.textContent="Inspect proposed file contents";
    reviewDetails.append(reviewHeading);
    const preview=doc.createElement("pre");
    preview.className="swrlz-github-change-source";
    preview.textContent=proposal.content;
    reviewDetails.append(preview);
    wrapper.append(reviewDetails);
    if(proposal.operation==="UPDATE_FILE"){
      const diff=doc.createElement("pre");
      diff.className="swrlz-github-change-diff";
      diff.textContent=String(proposal.diff||"No textual differences");
      const old=doc.createElement("details"),oldTitle=doc.createElement("summary"),oldSource=doc.createElement("pre");
      oldTitle.textContent="View original file";oldSource.textContent=String(proposal.before||"");
      old.append(oldTitle,oldSource);
      const diffDetails=doc.createElement("details"),diffHeading=doc.createElement("summary");
      diffDetails.className="swrlz-github-change-diff-details";
      diffHeading.textContent="View exact changes (diff)";
      diffDetails.append(diffHeading,diff);
      wrapper.append(diffDetails,old);
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
      receiptPanel.hidden=false;
      const verifiedTitle=doc.createElement("strong");
      verifiedTitle.textContent=receipt.operation==="CREATE_FILE"?"File created · verified":"File updated · verified";
      receiptPanel.append(verifiedTitle);
      const verifiedInfo=doc.createElement("p");
      verifiedInfo.textContent=proposal.path+" · "+proposal.branch+" · exact bytes verified";
      receiptPanel.append(verifiedInfo);
      if(typeof receipt.commitSha==="string"&&/^[0-9a-f]{40}$/i.test(receipt.commitSha)
         &&/^[a-z0-9_.-]+\/[a-z0-9_.-]+$/i.test(proposal.repo)){
        const link=doc.createElement("a");
        link.href="https://github.com/"+proposal.repo+"/commit/"+receipt.commitSha;
        link.target="_blank";link.rel="noopener noreferrer";
        link.textContent="View verified commit";
        receiptPanel.append(link);
      }
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
      pending=accepted;
      wrapper.setAttribute("data-review-state",accepted?"submitted":"rejecting");
      note.textContent=accepted?"Submitting approval to §C…":"Submitting rejection to §C…";
      try{
        const result=await options.confirm(accepted);
        if(result){
          if(!settled)note.textContent=accepted
            ?"Approval sent. Checking GitHub verification receipt below…"
            :"Rejection submitted. No file change was approved.";
          if(!settled)wrapper.setAttribute("data-review-state",accepted?"submitted":"rejected");
          if(!accepted)approve.hidden=reject.hidden=true;
        }else{
          pending=false;
          wrapper.setAttribute("data-review-state","ready");
          note.textContent="Decision not confirmed. No change assumed.";
          approve.disabled=reject.disabled=false;
        }
      }catch(_){
        pending=false;
        wrapper.setAttribute("data-review-state","ready");
        note.textContent="Decision failed. No change assumed.";
        approve.disabled=reject.disabled=false;
      }
    };
    approve.addEventListener("click",()=>act(true));
    reject.addEventListener("click",()=>act(false));
    const actions=doc.createElement("div");
    actions.className="swrlz-github-change-actions";
    actions.append(reject,approve);
    wrapper.insertBefore(actions,reviewDetails);
    wrapper.insertBefore(note,actions);
    const receiptPanel=doc.createElement("section");
    receiptPanel.className="swrlz-github-change-receipt";
    receiptPanel.hidden=true;
    receiptPanel.setAttribute("role","status");
    wrapper.append(receiptPanel);
    container.append(wrapper);
    return wrapper;
  }
  function reconcileReceipt(card,threadId){
    if(!card||typeof card.textContent!=="string")return false;
    const receiptText=card.textContent;
    if(!/Exact bytes verified/i.test(receiptText))return false;
    const operation=/File created/i.test(receiptText)?"CREATE_FILE":
      /File updated/i.test(receiptText)?"UPDATE_FILE":null;
    if(!operation)return false;
    const doc=card.ownerDocument;
    const candidates=doc.querySelectorAll(".swrlz-github-change-review[data-review-state='submitted']");
    for(const wrapper of candidates){
      if(wrapper.dataset.reviewThread!==String(threadId||"")
        ||wrapper.dataset.reviewOperation!==operation
        ||!receiptText.includes(wrapper.dataset.reviewPath))continue;
      const path=wrapper.dataset.reviewPath;
      const details=wrapper.querySelectorAll("p");
      const repo=details[0]?.textContent?.replace(/^Repository:\s*/,"")||"";
      const branch=details[1]?.textContent?.replace(/^Branch:\s*/,"")||"";
      if(!repo||!branch||!receiptText.includes(repo.split("/").at(-1)))continue;
      const links=card.querySelectorAll?Array.from(card.querySelectorAll("a[href]")):[];
      const commitLink=links.map(link=>String(link.href||""))
        .find(url=>url.startsWith("https://github.com/"+repo+"/commit/") &&
          /^[0-9a-f]{40}$/i.test(url.split("/").at(-1)))||"";
      const commitSha=commitLink?commitLink.split("/").at(-1):"";
      if(typeof root.dispatchEvent==="function"&&typeof root.CustomEvent==="function"){
        root.dispatchEvent(new root.CustomEvent("swrlz-github-write-receipt",{
          detail:{threadId:String(threadId||""),operation,path,repo,branch,commitSha,verified:true}
        }));
        return true;
      }
    }
    return false;
  }
  root.SwrlzGithubChangeReviewV1=Object.freeze({render,reconcileReceipt});
})(typeof window!=="undefined"?window:globalThis);
