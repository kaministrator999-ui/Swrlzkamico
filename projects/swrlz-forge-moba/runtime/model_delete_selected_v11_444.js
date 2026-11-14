/* SE444_DELETE_SELECTED_VR_ACTION_START */
// The permanent dock routes through the existing controller action dispatcher.
// First trigger arms only the exact current selection; second trigger commits.
(function(){
 'use strict';
 const previousAction=se340ModelXRAction;
 let pending=null;
 se340ModelXRAction=function(action,record=null){
  if(action!=='delete-selected')return previousAction(action,record);
  const s=se340XR;
  if(!s.session||!s.scene||!se340VisibleSession())return false;
  if(s.gesture||se340Bridge().inspect().gesture||se350Tools().inspect().gesture){
   pending=null;se340Notice('Finish or cancel the current transform before deleting.',true);se340SyncUI();return true;
  }
  const native=se340Bridge().inspect();
  const ids=se350Tools().selection().ids.filter(id=>se340PartEntries().some(entry=>entry.id===id));
  if(!ids.length){
   pending=null;se340Notice('Select one or more meshes first.');se340SyncUI();return true;
  }
  if(ids.length>=native.partCount){
   pending=null;se340Notice('Keep at least one mesh in the model.',true);se340SyncUI();return true;
  }
  const signature=[native.documentToken,native.revision,...ids.slice().sort()].join('|');
  const now=performance.now();
  if(!pending||pending.signature!==signature||now>pending.until){
   pending={signature,until:now+5500};
   se340Notice('Delete '+ids.length+' selected mesh'+(ids.length===1?'':'es')+'? Trigger DELETE again to confirm.');se340SyncUI();return true;
  }
  pending=null;
  const result=ModelAtelier.deleteSelected();
  if(!result?.ok){se340Notice(result?.reason||'Delete unavailable.',true);se340SyncUI();return true;}
  s.frameEntries=null;s.cachedEntries=null;s.projectionRevision=-1;s.boxCache=new WeakMap();
  se343DropHoverSurfaces();se350Invalidate();
  se340Notice('Deleted '+result.deletedCount+' mesh'+(result.deletedCount===1?'':'es')+'. Undo restores the deletion.');
  se340SyncUI();se340Publish();
  return true;
 };
 window.SWYRL_ENGINE_MODEL_DELETE_SELECTED_444=Object.freeze({version:'v11.444',confirmation:'double trigger',surface:'permanent VR dock'});
})();
/* SE444_DELETE_SELECTED_VR_ACTION_END */
