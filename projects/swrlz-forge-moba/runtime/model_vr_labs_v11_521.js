/* SE521_MODEL_VR_LABS_START
 * The existing three-stage native XR menu owns hit testing and placement.
 * This router owns only lab intent and hands operations to native editors.
 */
const se521ModelLabs=(()=>{
 'use strict';
 const choices=new Set(['model','rig','animate','texture']);
 const status=(msg,bad=false)=>{se340Notice(msg,bad);se340SyncUI();se340Publish();};
 const lab=()=>choices.has(se340XR.se521Lab)?se340XR.se521Lab:'model';
 function switchLab(next){
  if(!choices.has(next))return false;
  if(se340XR.gesture)se340CancelGesture('Switched lab; unfinished edit canceled.');
  se220Playing=false;
  se340XR.se521Lab=next;
  se340XR.mode='inspect';se340XR.page=next==='rig'?'rig':next==='animate'?'rig':next==='texture'?'views':'tools';
  const m=model();
  if(m){m.editorWorkspace=m.editorWorkspace||{};m.editorWorkspace.vrLab=next;}
  se340XR.stateKey='';
  status(({'model':'Modeling','rig':'Rigging','animate':'Animation','texture':'Texture & Materials'})[next]+
   ' Lab · top navigation and lab Undo/Redo remain available.');
  return true;
 }
 function ensureRig(){
  if(se220RigAvailable?.())return se220Rig();
  status('This lab operation requires a valid editable skeleton.',true);return null;
 }
 function animation(action){
  const r=ensureRig();if(!r)return true;
  if(action==='animation-play'){
   if(se220Playing){se220Playing=false;se220RigPose(r.pose);status('Animation playback stopped.');}
   else if(r.timeline?.length>=2){
    se220Playing=true;se220PlayBegin=performance.now()-se220Time*1000;
    status('Playing '+(r.activeClip||'active')+' animation.');
   }else status('Add two keyframes before playback.',true);
   return true;
  }
  if(action==='animation-key'){
   const t=+se220Time.toFixed(2),idx=r.timeline?.findIndex(x=>Math.abs(x.time-t)<.02)??-1;
   if(idx<0&&r.timeline?.length>=32){status('Maximum 32 keyframes in this clip.',true);return true;}
   se521Journal.setLabel('Animation · saved pose at '+t.toFixed(2)+'s');
   if(idx>=0)r.timeline[idx]={time:t,pose:structuredClone(r.pose)};
   else{r.timeline.push({time:t,pose:structuredClone(r.pose)});r.timeline.sort((a,b)=>a.time-b.time);}
   se220RigTouched('Animation key saved at '+t.toFixed(2)+'s.');return true;
  }
  if(action==='animation-loop'){
   r.loop=!r.loop;se521Journal.setLabel('Animation · loop '+(r.loop?'enabled':'disabled'));
   se220RigTouched('Loop '+(r.loop?'on':'off'));return true;
  }
  const timeline=r.timeline||[];
  if(action==='animation-prev'||action==='animation-next'){
   const times=timeline.map(x=>x.time).sort((a,b)=>a-b);
   const t=action==='animation-prev'?times.filter(v=>v<se220Time-.005).at(-1):times.find(v=>v>se220Time+.005);
   if(t===undefined){status('No '+(action==='animation-prev'?'earlier':'later')+' animation key.');return true;}
   se220Time=t;se220Playing=false;se220RigPose(se220RigInterpolate(r,t));
   status('Animation playhead '+t.toFixed(2)+'s · pose preview only.');return true;
  }
  if(action==='animation-time-minus'||action==='animation-time-plus'){
   se220Time=Math.max(0,Math.min(Number(r.duration)||2,se220Time+(action.endsWith('plus')?.1:-.1)));
   se220Playing=false;se220RigPose(se220RigInterpolate(r,se220Time));
   status('Playhead '+se220Time.toFixed(2)+'s · no authored key changed.');return true;
  }
  return false;
 }
 function deleteSelected(){
  const m=model(),ids=se350Tools()?.selection?.()?.ids||[];
  if(!m||!ids.length){status('Select a mesh before Delete.',true);return true;}
  if(m.parts.length<=ids.length){status('Keep at least one editable mesh in the project.',true);return true;}
  const key=String(currentProject?.instanceId||'')+'|'+ids.join('|');
  if(se521ModelLabs.pendingDelete?.key!==key){
   se521ModelLabs.pendingDelete={key};
   status('Delete '+ids.length+' selected mesh(es)? Trigger Delete again to confirm; B cancels.',true);
   return true;
  }
  se521ModelLabs.pendingDelete=null;
  se521Journal.setLabel('Modeling · deleted '+ids.length+' selected mesh(es)');
  checkpoint();
  const chosen=new Set(ids);
  m.parts=m.parts.filter(part=>!chosen.has(part.id));
  selection=null;
  atelierMeshIds=[];
  signalEdited();
  status('Deleted '+ids.length+' selected mesh(es). Undo in Modeling Lab restores them.');
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
    action==='animation-time-plus')return animation(action);
  if(action==='texture-uv'||action==='texture-paint'||action==='texture-placement'){
   status('Texture & Materials Lab selected · precise immersive '+action.slice(8)+
    ' submenu controls are reserved for the next menu pass. No texture was changed.');return true;
  }
  if(action==='texture-material'){
   status('Materials Lab · use native Texture/Display inspection now; material authoring controls are in the next submenu pass.');
   return true;
  }
  if(action==='lab-history'){
   const info=se521Journal.inspect();status('Project edit journal: '+info.totalEvents+
    ' preserved events · '+info.lab+' lab Undo '+info.undoDepth+' / Redo '+info.redoDepth);return true;
  }
  const result=prior.apply(this,arguments);
  if(action==='undo'||action==='redo'){
   const error=se521Journal.inspect().lastError;
   if(error)status(error,true);
  }
  return result;
 };
 const priorCleanup=se340Cleanup;
 se340Cleanup=function(...args){se521ModelLabs.pendingDelete=null;return priorCleanup.apply(this,args);};
 return Object.freeze({switchLab,lab,inspect:()=>({lab:lab(),
  saved:model()?.editorWorkspace?.vrLab||null,history:se521Journal.inspect()}),
  pendingDelete:null});
})();
window.SWYRL_ENGINE_MODEL_VR_LABS_521=se521ModelLabs;
/* SE521_MODEL_VR_LABS_END */