/* SE521_MODEL_VR_LABS_START
 * Native three-stage spatial menu stays the sole interaction dispatcher.
 * All editable project/rig/animation authority is routed through the
 * established Model Atelier document bridge, never a duplicate XR model.
 */
const se521ModelLabs=(()=>{
 'use strict';
 const choices=new Set(['model','rig','animate','texture']);
 const native=()=>window.SWYRL_ENGINE_MODEL_LAB_NATIVE_521;
 let pendingDelete=null;
 const status=(msg,bad=false)=>{se340Notice(msg,bad);se340SyncUI();se340Publish();};
 const lab=()=>choices.has(se340XR.se521Lab)?se340XR.se521Lab:'model';
 function switchLab(next){
  if(!choices.has(next))return false;
  if(se340XR.gesture)se340CancelGesture('Switched lab; unfinished edit canceled.');
  if(!native()?.setLab?.(next)){status('Model workspace is not ready for a lab switch.',true);return true;}
  se340XR.se521Lab=next;
  se340XR.mode='inspect';
  se340XR.page=next==='rig'?'rig':next==='animate'?'rig':next==='texture'?'views':'tools';
  se340XR.stateKey='';
  pendingDelete=null;
  status(({'model':'Modeling','rig':'Rigging','animate':'Animation','texture':'Texture & Materials'})[next]+
   ' Lab · only middle tools change; this project retains its own lab history.');
  return true;
 }
 function deleteSelected(){
  const bridge=native(),ids=bridge?.selected?.()||[];
  if(!ids.length){status('Select a mesh before Delete.',true);return true;}
  const key=String(bridge?.projectId?.()||'')+'|'+ids.join('|');
  if(pendingDelete?.key!==key){
   pendingDelete={key};
   status('Delete '+ids.length+' selected mesh(es)? Trigger Delete again to confirm; B cancels.',true);
   return true;
  }
  pendingDelete=null;
  const result=bridge?.deleteSelected?.();
  status(result?.ok?'Deleted '+result.deleted+' selected mesh(es) · Modeling Undo restores them.':
   result?.reason||'Delete not available.',!result?.ok);
  return true;
 }
 const prior=se340ModelXRAction;
 se340ModelXRAction=function(action,record=null){
  if(typeof action!=='string')return prior.apply(this,arguments);
  if(action==='labs'||action==='transform-menu')return true;
  if(action.startsWith('lab-'))return switchLab(action.slice(4));
  if(action==='delete-selected')return deleteSelected();
  if(action==='animation-play'||action==='animation-key'||action==='animation-loop'||
    action==='animation-prev'||action==='animation-next'||action==='animation-time-minus'||
    action==='animation-time-plus'){
   const result=native()?.animation?.(action);
   status(result?.ok?result.message||'Animation operation completed.':
    result?.reason||'Animation tool unavailable.',!result?.ok);
   return true;
  }
  if(action==='texture-uv'||action==='texture-paint'||action==='texture-placement'){
   status('Texture & Materials Lab · immersive '+action.slice(8)+
    ' controls will be refined in the next submenu pass. This action makes no changes.');
   return true;
  }
  if(action==='texture-material'){
   status('Materials controls are scheduled for the next lab submenu pass. No material changed.');
   return true;
  }
  if(action==='lab-history'){
   const info=native()?.journal?.();
   if(!info){status('Project history unavailable.',true);return true;}
   status('Project history: '+info.totalEvents+' recorded events · '+info.lab+
    ' lab: Undo '+info.undoDepth+', Redo '+info.redoDepth);
   return true;
  }
  const result=prior.apply(this,arguments);
  if(action==='undo'||action==='redo'){
   const error=native()?.journal?.()?.lastError;
   if(error)status(error,true);
  }
  return result;
 };
 const priorCleanup=se340Cleanup;
 se340Cleanup=function(...args){pendingDelete=null;return priorCleanup.apply(this,args);};
 return Object.freeze({switchLab,lab,inspect:()=>({lab:lab(),
  saved:native()?.savedLab?.()||null,history:native()?.journal?.()||null}),
  get pendingDelete(){return pendingDelete;}});
})();
window.SWYRL_ENGINE_MODEL_VR_LABS_521=se521ModelLabs;
/* SE521_MODEL_VR_LABS_END */
