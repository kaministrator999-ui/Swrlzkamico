/* SE533_PROJECT_ACCOUNT_OPEN_START */
function se533AccountOpenFailure(message){
 const diagnostics=window.SWYRL_ENGINE_PROJECT_LOAD_493;
 const detail=diagnostics.failure(Error(message));
 setStatus('Account load failed: '+detail,true);
 return false;
}
loadCloud=async function(projectKey){
 // Native account cards, startup and VR pass an ID. The §Chat picker may
 // supply a cloud-prefixed selection. Leave that picker untouched while opening.
 const explicit=typeof projectKey==='string';
 const selection=explicit?projectKey:cloudList?.value||'';
 const projectId=selection.replace(/^cloud:/,'');
 if((!explicit&&!selection.startsWith('cloud:'))||!bounded(projectId,160))
  return se533AccountOpenFailure('Choose a Google-saved project first.');
 if(!ready||!se176AccountConnected)
  return se533AccountOpenFailure('Connect §Chat and sign in with Google before opening an account project.');
 if(cloudBusy)
  return se533AccountOpenFailure('Another account operation is in progress. Try Open again when it finishes.');
 const opened=await se528PriorLoadCloud.call(this,projectId);
 if(opened!==true){
  const diagnostics=window.SWYRL_ENGINE_PROJECT_LOAD_493;
  const detail=diagnostics?.getError?.()||status?.textContent||
   'Native account project download was not confirmed.';
  return se533AccountOpenFailure(detail);
 }
 const receipt=cloudRefs.get(getProjectId());
 if(receipt?.id!==projectId||!Number.isSafeInteger(receipt.revision)||receipt.revision<1)
  return se533AccountOpenFailure('The editor did not confirm the requested account project revision.');
 return true;
};
/* SE533_PROJECT_ACCOUNT_OPEN_END */
