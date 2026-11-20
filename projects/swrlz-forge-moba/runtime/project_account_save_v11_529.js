/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START */
// §E v11.529: "Save project to account" must save the complete native §E
// project. The v11.488 model-asset naming wrapper intentionally routes the
// separate Model Studio *asset* save to ASSET_LIBRARY; it is not a project save.
// Reuse the v11.371 native snapshot -> cloud revision guard -> durable RPC.
let se529ProjectSaveBusy=false;
let se529ProjectSaveResult=null;
async function se529SaveNativeProjectToAccount(){
 if(se529ProjectSaveBusy||cloudBusy||se175Transition||se175LocalLoading||
    se371ActionBusy||playing||simulating){
  const detail='A project edit, save or loading operation is already active.';
  se371Display(detail,true);
  return {ok:false,error:'PROJECT_BUSY',detail};
 }
 if(!ready||!se176AccountConnected){
  if(!ready&&frame&&!frame.src)frame.src=CHAT_ORIGIN+'/?forgeEmbed=1';
  const detail='The Chat account is not connected. Open §Chat and sign in before saving to account.';
  se371Display(detail,true);
  return {ok:false,error:'ACCOUNT_NOT_CONNECTED',detail};
 }
 se529ProjectSaveBusy=true;se529ProjectSaveResult=null;
 const button=document.getElementById('se529SaveAccount');
 if(button){button.disabled=true;button.dataset.busy='true';}
 try{
  // Preserve v11.488 naming rules, including starter-safe cloning and model
  // names. The user can cancel without modifying a canonical starter.
  if(!(await se488EnsureProjectNameForAccount())){
   return {ok:false,error:'SAVE_CANCELLED',detail:'Account save cancelled; no remote write was attempted.'};
  }
  if(se175Saving)await se175Saving;
  if(!se371HasSavedIdentity())throw Error('Project needs an independent identity. Clone it first.');
  await se371SaveLocal();
  const idBefore=getProjectId();
  const linkedBefore=cloudRefs.get(idBefore)||se371CloudLinks.get(idBefore);
  se371Display('Saving the complete native project to your account…');
  // This is the original project save facade (not v11.488 ASSET_LIBRARY.save).
  // It enforces the existing remote revision preflight and durable=true RPC.
  const confirmed=await se371PreviousSaveCloud()===true;
  const linked=cloudRefs.get(idBefore);
  const valid=confirmed&&getProjectId()===idBefore&&
   !!linked?.id&&Number.isInteger(linked.revision)&&linked.revision>=1&&
   (!linkedBefore||linked.id===linkedBefore.id&&linked.revision>linkedBefore.revision);
  if(!valid){
   const raw=String(status?.textContent||'').trim();
   const detail=raw&&/error|fail|stopp|timed out|unavailable|revision|storage|quota|invalid/i.test(raw)
    ?raw:'The account service did not confirm a new project revision. No cloud success was recorded.';
   const result={ok:false,error:'ACCOUNT_SAVE_UNCONFIRMED',detail};
   se529ProjectSaveResult=result;
   se371Display('Saved on this device. Account save failed: '+detail,true);
   return result;
  }
  try{await se176RefreshProjects();}catch{}
  try{await se175RefreshLocal();}catch{}
  try{if(se170Active==='mine')await se170Refresh();}catch{}
  const result={ok:true,scope:'account',name:se371ProjectName(),
   projectId:linked.id,revision:linked.revision};
  se529ProjectSaveResult=result;
  se371Display('Saved to your account · '+result.name+' · revision '+result.revision+'.');
  return result;
 }catch(error){
  const detail=String(error?.message||error).slice(0,240);
  const result={ok:false,error:'ACCOUNT_SAVE_FAILED',detail};
  se529ProjectSaveResult=result;
  se371Display('Account save failed: '+detail,true);
  return result;
 }finally{
  se529ProjectSaveBusy=false;
  if(button){button.disabled=false;delete button.dataset.busy;}
  window.dispatchEvent(new CustomEvent('swrlz:account-save-result',
   {detail:{ok:se529ProjectSaveResult?.ok===true,revision:se529ProjectSaveResult?.revision??null}}));
 }
}
// Redirect old buttons and XR facade to this *one native project-save route*.
// The standalone asset-save workflow remains independently available in Model
// Studio. The existing account host closure retains all credentials and RPCs.
se528SaveAccount=se529SaveNativeProjectToAccount;
window.SWYRL_ENGINE_ACCOUNT_SAVE_528=Object.freeze({
 save:se529SaveNativeProjectToAccount,
 status:()=>({connected:!!(ready&&se176AccountConnected),
  busy:se529ProjectSaveBusy||cloudBusy,
  last:se529ProjectSaveResult?.ok===true?'confirmed':se529ProjectSaveResult?'failed':'idle'})
});
window.SWYRL_ENGINE_PROJECT_ACCOUNT_529=Object.freeze({
 save:se529SaveNativeProjectToAccount,
 status:()=>({connected:!!(ready&&se176AccountConnected),
  busy:se529ProjectSaveBusy||cloudBusy,
  result:se529ProjectSaveResult?
   {ok:se529ProjectSaveResult.ok,error:se529ProjectSaveResult.error||null,
    revision:se529ProjectSaveResult.revision||null}:null})
});
/* SE529_NATIVE_PROJECT_ACCOUNT_SAVE_END */