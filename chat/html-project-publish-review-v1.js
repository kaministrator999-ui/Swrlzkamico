/* §C HTML deployment review: presentation only; server OAuth and one-use
   approval state remain authoritative. No browser-side GitHub or HF secrets. */
(function(root){
  "use strict";
  const MAX_AGE_MS=300000;
  const okSlug=s=>typeof s==="string"&&/^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$/.test(s);
  const okSha=s=>typeof s==="string"&&/^[a-f0-9]{40}$/.test(s);
  function render(container,data,opts={}){
    if(!container||!data||!okSlug(data.project)||!(data.mode==="create"?/^[a-f0-9]{64}$/.test(data.sourceSha):okSha(data.sourceSha))
      ||data.repo!=="kaministrator999-ui/Swrlzkamico"
      ||!Array.isArray(data.files)||typeof opts.confirm!=="function")return false;
    const creating=data.mode==="create";
    const doc=container.ownerDocument,thread=String(opts.threadId||""),created=Date.now();
    const surface=doc.createElement("section");
    surface.className="swrlz-github-change-review swrlz-html-publish-review";
    surface.dataset.reviewThread=thread;
    const heading=doc.createElement("h3");
    heading.textContent=creating?"HTML project · GitHub creation approval":"HTML project · deployment approval";
    surface.append(heading);
    const subtitle=doc.createElement("p");
    subtitle.textContent="Project "+data.project+(creating?" · create source in GitHub (no deployment)":" · existing §C Hugging Face Space");
    surface.append(subtitle);
    const facts=[
      ["Repository",data.repo],["Branch",data.branch||"main"],
      [creating?"Verified artifact source hash":"Immutable GitHub source",data.sourceSha],["Files",data.files.length],
      ["Total size",String(data.bytes)+" bytes"],
      [creating?"Proposed GitHub directory":"Published directory",data.destinationPrefix||""],
    ];
    for(const [label,value] of facts){
      const p=doc.createElement("p"),strong=doc.createElement("strong");
      strong.textContent=label+": ";p.append(strong,doc.createTextNode(String(value)));surface.append(p);
    }
    const files=doc.createElement("details");
    const summary=doc.createElement("summary");
    summary.textContent="Inspect "+data.files.length+(creating?" proposed source files":" committed project files");
    files.append(summary);
    const list=doc.createElement("ul");
    list.style.cssText="margin:6px 0;padding-left:18px;font:12px/1.6 monospace;overflow-wrap:anywhere";
    for(const entry of data.files.slice(0,48)){
      const li=doc.createElement("li");
      li.textContent=String(entry.path||"")+" · "+String(entry.bytes||0)+" bytes";
      list.append(li);
    }
    files.append(list);surface.append(files);
    const sourceLink=doc.createElement("a");
    sourceLink.href=creating?"https://github.com/"+data.repo+"/tree/main":
      "https://github.com/"+data.repo+"/tree/"+data.sourceSha+
      "/html-projects/"+encodeURIComponent(data.project);
    sourceLink.target="_blank";sourceLink.rel="noopener noreferrer";
    sourceLink.textContent=creating?"Open selected GitHub repository":"Review exact committed source on GitHub";
    surface.append(sourceLink);
    const note=doc.createElement("p");
    note.setAttribute("role","status");
    note.setAttribute("aria-live","polite");
    note.textContent=creating?"No GitHub files have been created. This approval authorizes only the listed commit; deploying requires a second approval within this thread.":"No deployment dispatched. Approval is valid only in this thread for five minutes.";
    surface.append(note);
    const actions=doc.createElement("div");
    actions.className="swrlz-github-change-actions";
    const decline=doc.createElement("button"),approve=doc.createElement("button");
    decline.type=approve.type="button";
    decline.textContent=creating?"Cancel creation":"Cancel deployment";
    approve.textContent=creating?"Approve GitHub commit":"Approve publish";
    actions.append(decline,approve);surface.append(actions);
    let decided=false,busy=false;
    async function decide(accepted){
      if(busy||decided)return;
      if(Date.now()-created>MAX_AGE_MS
        ||!(typeof opts.isLatest==="function"&&opts.isLatest(surface))
        ||!(typeof opts.currentThread==="function"&&String(opts.currentThread())===thread)){
        note.textContent="This review expired or is no longer current. Request a new approval proposal.";
        approve.disabled=decline.disabled=true;
        return;
      }
      busy=true;approve.disabled=decline.disabled=true;
      note.textContent=accepted?"Submitting your approval to §C…":"Submitting rejection to §C…";
      try{
        const sent=await opts.confirm(accepted);
        if(sent){
          decided=true;
          note.textContent=accepted
            ?"Decision submitted. The next server receipt confirms the operation and any following approval."
            :"Cancellation submitted; no GitHub write or publication was authorized.";
          approve.hidden=decline.hidden=true;
        }else{
          note.textContent="Decision was not accepted. No deployment assumed.";
          approve.disabled=decline.disabled=false;
        }
      }catch(_){
        note.textContent="Decision failed. No deployment assumed.";
        approve.disabled=decline.disabled=false;
      }finally{busy=false;}
    }
    approve.addEventListener("click",()=>decide(true));
    decline.addEventListener("click",()=>decide(false));
    container.append(surface);
    return surface;
  }
  root.SwrlzHtmlPublishReviewV1=Object.freeze({render});
})(typeof window!=="undefined"?window:globalThis);
