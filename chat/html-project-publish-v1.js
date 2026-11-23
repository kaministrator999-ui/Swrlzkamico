/* §C HTML project publishing: one-use owner approval, isolated preview and verified receipts. */
(() => {
  "use strict";
  if (window.SwrlzHtmlProjectsV1) return;
  window.SwrlzHtmlProjectsV1 = true;

  const css = document.createElement("style");
  css.textContent = `
    .swrlz-html-publish-open{border:1px solid rgba(69,211,242,.42)!important;background:rgba(12,45,63,.94)!important;color:#e9f8ff!important}
    .swrlz-html-publish-overlay{position:fixed;inset:0;z-index:2147483000;background:rgba(1,7,16,.82);display:flex;align-items:center;justify-content:center;padding:12px;box-sizing:border-box}
    .swrlz-html-publish-panel{width:min(920px,100%);max-height:calc(100dvh - 24px);overflow:auto;box-sizing:border-box;background:#071a29;color:#eaf7ff;border:1px solid #366b80;border-radius:14px;padding:18px;box-shadow:0 20px 70px #000a;font:14px system-ui,sans-serif}
    .swrlz-html-publish-top{display:flex;align-items:center;justify-content:space-between;gap:12px}
    .swrlz-html-publish-panel h2{font:700 19px system-ui,sans-serif;margin:0}
    .swrlz-html-publish-panel p{line-height:1.5;color:#abc6d4}
    .swrlz-html-publish-panel label{display:block;font-size:13px;line-height:1.6;color:#d0e8f2}
    .swrlz-html-publish-panel input[type=text]{width:100%;max-width:450px;background:#0d2d3e;border:1px solid #39768e;color:white;padding:10px;border-radius:8px;box-sizing:border-box;font:inherit}
    .swrlz-html-publish-panel button{background:#17465f;border:1px solid #407d98;color:#e7faff;padding:9px 13px;min-height:38px;border-radius:8px;cursor:pointer;font:inherit}
    .swrlz-html-publish-panel button:disabled{opacity:.38;cursor:not-allowed}
    .swrlz-html-publish-panel a{color:#7fdefa;overflow-wrap:anywhere}
    .swrlz-html-publish-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
    .swrlz-html-publish-result{padding:10px 12px;white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #20485c;border-radius:8px;background:#0a2233;min-height:25px}
    .swrlz-html-publish-details{font:12px ui-monospace,monospace;max-height:120px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere}
    .swrlz-html-publish-preview{display:block;width:100%;height:300px;background:white;border:1px solid #46798b;border-radius:7px;margin:10px 0}
    .swrlz-html-publish-panel [hidden]{display:none!important}
    @media(max-width:600px){.swrlz-html-publish-panel{padding:12px}.swrlz-html-publish-preview{height:240px}}
  `;
  document.head.appendChild(css);

  function make(tag, attrs = {}, text) {
    const el = document.createElement(tag);
    for (const [key,value] of Object.entries(attrs)) {
      if (key === "class") el.className = value;
      else if (key === "type") el.type = value;
      else if (key === "href") el.href = value;
      else if (key === "target") el.target = value;
      else el.setAttribute(key, value);
    }
    if (text !== undefined) el.textContent = text;
    return el;
  }
  function api(path, method, payload) {
    return fetch(path, {
      method, credentials:"same-origin", cache:"no-store",
      headers: method === "POST"
        ? {"Content-Type":"application/json","X-Swrlz-Project-Action":"v1"}
        : {"Accept":"application/json"},
      ...(method === "POST" ? {body:JSON.stringify(payload)} : {}),
    }).then(async response => {
      const body = await response.json().catch(()=>({}));
      if (!response.ok) throw new Error(body.detail || body.code || "HTTP " + response.status);
      return body;
    });
  }

  function open() {
    const overlay = make("div", {"class":"swrlz-html-publish-overlay"});
    overlay.setAttribute("role","presentation");
    const panel = make("section", {"class":"swrlz-html-publish-panel",role:"dialog","aria-modal":"true","aria-label":"Publish HTML project"});
    const top = make("div", {"class":"swrlz-html-publish-top"});
    const title = make("h2", {}, "GitHub → Hugging Face · HTML project");
    const close = make("button", {type:"button","aria-label":"Close HTML publishing panel"}, "Close");
    top.append(title,close); panel.append(top);
    panel.append(make("p", {}, "First create or edit the files in GitHub under html-projects/<project>/, including index.html. Review the committed source before choosing to publish it to the existing §C Space."));
    const label = make("label", {}, "Project directory name (lowercase letters, digits, hyphens)");
    const slugInput = make("input",{type:"text",placeholder:"example-webpage",autocomplete:"off",spellcheck:"false"});
    label.append(slugInput); panel.append(label);
    const actions = make("div", {"class":"swrlz-html-publish-actions"});
    const reviewButton = make("button",{type:"button"},"Review committed project");
    actions.append(reviewButton); panel.append(actions);
    const output = make("div",{"class":"swrlz-html-publish-result",role:"status","aria-live":"polite"},"No files have been published.");
    panel.append(output);
    const info = make("pre",{"class":"swrlz-html-publish-details"});
    panel.append(info);
    const previewLabel = make("p",{},"Sandboxed index.html snapshot preview. Relative CSS/JS assets may not load until the project is published.");
    previewLabel.hidden=true;panel.append(previewLabel);
    const preview = make("iframe",{"class":"swrlz-html-publish-preview",sandbox:"allow-scripts",referrerpolicy:"no-referrer",title:"Sandboxed HTML project preview"});
    preview.hidden=true;panel.append(preview);
    const approvalLabel = make("label");
    const check = make("input",{type:"checkbox"});
    approvalLabel.append(check, document.createTextNode(" I reviewed the exact committed files and approve publishing this project to the public Hugging Face Space."));
    approvalLabel.hidden=true;panel.append(approvalLabel);
    const follow = make("div",{"class":"swrlz-html-publish-actions"});
    const approveButton = make("button",{type:"button"},"Approve and deploy");
    approveButton.disabled=true;follow.append(approveButton);
    const runLink = make("a",{target:"_blank",rel:"noopener noreferrer"},"Open GitHub Actions");
    runLink.hidden=true;follow.append(runLink);
    const liveLink = make("a",{target:"_blank",rel:"noopener noreferrer"},"Open verified webpage");
    liveLink.hidden=true;follow.append(liveLink);
    panel.append(follow);overlay.append(panel);document.body.append(overlay);

    let approval=null,nonce=null,timer=null,closed=false,busy=false;
    const write = text => {output.textContent = text};
    const stopPoll = () => {if(timer) clearInterval(timer);timer=null};
    function dismiss(){
      closed=true;stopPoll();preview.srcdoc="";overlay.remove();
    }
    close.addEventListener("click",dismiss);
    overlay.addEventListener("click",e=>{if(e.target===overlay)dismiss()});
    const esc=e=>{if(e.key==="Escape"){document.removeEventListener("keydown",esc);dismiss()}};
    document.addEventListener("keydown",esc);
    slugInput.addEventListener("input",()=>{
      approval=null;check.checked=false;check.disabled=true;approveButton.disabled=true;
      approvalLabel.hidden=true;preview.hidden=true;previewLabel.hidden=true;info.textContent="";
    });
    check.addEventListener("change",()=>{approveButton.disabled=!approval || !check.checked || busy});
    reviewButton.addEventListener("click",async()=>{
      const slug=slugInput.value.trim();
      if(!/^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$/.test(slug)){
        write("Enter a valid lowercase project directory name.");return;
      }
      approval=null;check.checked=false;approveButton.disabled=true;approvalLabel.hidden=true;
      reviewButton.disabled=true;write("Inspecting the exact committed GitHub revision…");
      try{
        const result=await api("/api/html-projects/prepare","POST",{project:slug});
        if(closed)return;
        approval=result;
        info.textContent=
          "GitHub commit: "+result.sourceSha+"\n"+
          "Destination: "+result.destination+"\n"+
          "Files: "+result.count+" ("+result.bytes+" bytes)\n"+
          result.files.map(f=>"  "+f.path+" · "+f.bytes+" bytes").join("\n");
        preview.srcdoc=result.previewHtml || "";
        preview.hidden=false;previewLabel.hidden=false;
        approvalLabel.hidden=false;check.disabled=false;
        write("Ready for review. Nothing has been deployed. Approval expires in "+result.expiresInSeconds+" seconds.");
      }catch(error){write("Review failed: "+String(error.message||error))}
      finally{reviewButton.disabled=false}
    });
    async function refresh(){
      if(!nonce||closed)return;
      try{
        const state=await api("/api/html-projects/status/"+encodeURIComponent(nonce),"GET");
        if(closed)return;
        if(state.actionsUrl){runLink.href=state.actionsUrl;runLink.hidden=false}
        switch(state.code){
          case "PUBLISHED_VERIFIED":
            stopPoll();write("Deployed and verified: GitHub Actions succeeded and the public HTML response has the required browser sandbox.");
            liveLink.href=state.url;liveLink.hidden=false;return;
          case "FAILED":
            stopPoll();write("Deployment failed. Inspect the Actions run to see why. No success claimed.");return;
          case "RUNTIME_SECURITY_NOT_VERIFIED":
            stopPoll();write("Source workflow finished but browser sandbox verification failed. Do not treat this project as live.");return;
          case "RUNNING":write("Publishing and verifying… GitHub Actions status: "+state.workflowStatus);return;
          default:write("GitHub Actions request accepted; awaiting a matching run.");
        }
      }catch(error){
        write("Status lookup unavailable: "+String(error.message||error)+". Check GitHub Actions.");
      }
    }
    approveButton.addEventListener("click",async()=>{
      if(!approval||!check.checked||busy)return;
      busy=true;approveButton.disabled=true;reviewButton.disabled=true;
      write("Submitting your single-use publishing approval…");
      try{
        const result=await api("/api/html-projects/confirm","POST",{
          approvalToken:approval.approvalToken,approved:true});
        approval=null;
        if(closed)return;
        if(result.code!=="DISPATCH_ACCEPTED")throw new Error("Dispatch was not acknowledged");
        nonce=result.requestNonce;
        runLink.href=result.actionsUrl;runLink.hidden=false;
        write("Owner approval accepted; deployment requested. Waiting for verified GitHub Actions results.");
        await refresh();
        if(!closed && timer===null)timer=setInterval(refresh,6500);
      }catch(error){write("Publishing not confirmed: "+String(error.message||error))}
      finally{busy=false;reviewButton.disabled=false}
    });
    slugInput.focus();
  }

  function addButton(){
    const target=document.querySelector(".github-connect-actions");
    if(!target || document.getElementById("swrlz-html-publish-button"))return false;
    const button=make("button",{
      id:"swrlz-html-publish-button",type:"button","class":"swrlz-html-publish-open"
    },"Publish HTML");
    button.title="Preview, approve and deploy a committed GitHub HTML project";
    button.addEventListener("click",open);
    target.append(button);
    return true;
  }
  if(!addButton()){
    const observer=new MutationObserver(()=>{if(addButton())observer.disconnect()});
    observer.observe(document.documentElement,{childList:true,subtree:true});
    document.addEventListener("DOMContentLoaded",addButton,{once:true});
  }
})();
