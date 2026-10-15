/* Experimental, explicitly approved GitHub TXT sandbox write UI. No chat/model text can execute it. */
(() => {
  'use strict';
  const endpoint = '/api/github/sandbox/';
  const el = (tag, props = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
      if (key === 'text') node.textContent = value;
      else if (key === 'className') node.className = value;
      else node.setAttribute(key, value);
    }
    for (const child of children) node.append(child);
    return node;
  };
  const button = el('button', {type:'button', text:'Test GitHub TXT creation', 'aria-haspopup':'dialog'});
  button.style.cssText = 'position:fixed;right:1rem;bottom:1rem;z-index:10000;padding:0.65rem 0.9rem;border-radius:0.65rem;border:1px solid #777;background:#171717;color:#fff;cursor:pointer';
  document.body.append(button);
  let dialog = null;
  button.addEventListener('click', () => {
    if (dialog) return;
    dialog = el('dialog', {'aria-label':'GitHub sandbox TXT creation test'});
    dialog.style.cssText = 'max-width:min(90vw,36rem);width:100%;padding:1.2rem;background:#171717;color:#fff;border:1px solid #aaa;border-radius:0.6rem';
    const heading = el('h2',{text:'Sandbox text file'});
    const explanation = el('p',{text:'Only kaministrator999-ui/Swrlzing-core • main • write-action-tests/*.txt. No overwrites. A second explicit confirmation is required.'});
    const nameLabel=el('label',{text:'New filename (example: test-one.txt)'});
    const filename=el('input',{type:'text',maxlength:'68',autocomplete:'off',required:'true',placeholder:'test-one.txt'});
    const bodyLabel=el('label',{text:'Text file contents'});
    const content=el('textarea',{rows:'6',maxlength:'4096',required:'true'});
    const status=el('p',{role:'status','aria-live':'polite',text:'Checking your existing GitHub connection…'});
    const oauth=el('a',{href:'/api/github/start?access=public-write',text:'Authorize GitHub sandbox write access'});
    oauth.style.cssText='display:none;color:#8feaff;text-decoration:underline;margin-top:0.7rem';
    const preview=el('pre');
    preview.style.cssText='white-space:pre-wrap;max-height:13rem;overflow:auto';
    const prepare=el('button',{type:'button',text:'Prepare (no write)'});
    const confirm=el('button',{type:'button',text:'Confirm GitHub creation'});
    confirm.disabled=true;
    prepare.disabled=true;
    const close=el('button',{type:'button',text:'Cancel / close'});
    const controls=el('div',{},prepare,confirm,close);
    controls.style.cssText='display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:1rem';
    [nameLabel,filename,bodyLabel,content].forEach(x=>{x.style.display='block';x.style.width='100%';x.style.marginTop='0.5rem'});
    dialog.append(heading,explanation,nameLabel,filename,bodyLabel,content,preview,status,oauth,controls);
    document.body.append(dialog);
    dialog.showModal();
    filename.focus();
    let approvalToken=null;
    const reset=()=>{approvalToken=null;confirm.disabled=true;preview.textContent=''};
    for(const inp of [filename,content])inp.addEventListener('input',reset);
    // No extra PAT: inspect the OAuth grant already linked to this Google account.
    fetch('/api/github/sandbox/write-status',{credentials:'same-origin'})
      .then(async response=>{
        const state=await response.json();
        if(!response.ok)throw Error(state.detail||'GITHUB_CONNECTION_UNAVAILABLE');
        if(state.allowed){
          status.textContent='Existing GitHub authorization verified for Swrlzing-core.';
          prepare.disabled=false;
        }else if(state.reason==='GITHUB_WRITE_SCOPE_REQUIRED'){
          status.textContent='GitHub is connected for reading. It has not granted repository writing. Approve the limited GitHub OAuth write scope once to enable this test.';
          if(state.authorizeUrl==='/api/github/start?access=public-write')oauth.style.display='block';
        }else if(state.reason==='SANDBOX_REPOSITORY_NOT_SELECTED'){
          status.textContent='Select kaministrator999-ui/Swrlzing-core in the existing GitHub repository chooser, then reopen this test.';
        }else{
          status.textContent='Write permission unavailable: '+String(state.reason||'UNKNOWN');
          if(state.reason==='GITHUB_NOT_CONNECTED'&&state.authorizeUrl==='/api/github/start?access=public-write')oauth.style.display='block';
        }
      })
      .catch(error=>{status.textContent='Could not verify connected GitHub authorization: '+error.message});

    async function post(resource, body) {
      const response=await fetch(endpoint+resource,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const result=await response.json();
      if(!response.ok)throw Error(result.code||'WRITE_ACTION_UNAVAILABLE');
      return result;
    }
    prepare.addEventListener('click',async()=>{
      reset();prepare.disabled=true;status.textContent='Checking filename and permissions…';
      try{
        const result=await post('prepare-create-txt',{filename:filename.value,content:content.value});
        approvalToken=result.approvalToken;
        preview.textContent='Operation: '+result.operation+'\nRepository: '+result.repo+'\nBranch: '+result.branch+'\nPath: '+result.path+'\n\nContent preview:\n'+result.preview;
        status.textContent='Review everything above. Confirm only if you authorize this one file creation.';
        confirm.disabled=false;
      }catch(error){status.textContent='Not prepared: '+error.message}
      finally{prepare.disabled=false}
    });
    confirm.addEventListener('click',async()=>{
      if(!approvalToken)return;
      const ticket=approvalToken;
      reset();confirm.disabled=true;prepare.disabled=true;status.textContent='Creating approved file and verifying GitHub read-back…';
      try{
        const result=await post('confirm-create-txt',{approvalToken:ticket,approved:true});
        status.textContent=result.ok&&result.verified?'Created and verified. Commit: '+result.commitSha:'Not verified; inspect GitHub before retry.';
        if(result.ok&&result.verified)status.append(el('a',{href:result.url,target:'_blank',rel:'noopener noreferrer',text:' Open verified file'}));
      }catch(error){status.textContent='Creation not confirmed: '+error.message+'; check repository before retrying.'}
      finally{prepare.disabled=false}
    });
    close.addEventListener('click',()=>dialog.close());
    dialog.addEventListener('close',()=>{dialog.remove();dialog=null});
  });
})();
