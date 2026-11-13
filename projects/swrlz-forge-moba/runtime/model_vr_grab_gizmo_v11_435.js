/* SE435_MODEL_VR_GRAB_GIZMO_START */
// The default post-selection tool is Grab. Its free-form behavior is kept,
// but the selected pivot now displays the native Move handles as an anchor.
// A Grip started on a handle becomes a constrained native Move transaction;
// Grip elsewhere keeps the established move/turn/size Grab transaction.
const se435PreviousGizmoFrame=se372GizmoFrame;
se372GizmoFrame=function(s){
 if(s.mode!=='grab')return se435PreviousGizmoFrame(s);
 const original=s.mode;
 s.mode='move';
 try{return se435PreviousGizmoFrame(s);}
 finally{s.mode=original;}
};
const se435PreviousContact=se374GizmoContact;
se374GizmoContact=function(record,cast=null){
 const s=se340XR;
 if(s.mode!=='grab')return se435PreviousContact(record,cast);
 const original=s.mode;
 s.mode='move';
 try{return se435PreviousContact(record,cast);}
 finally{s.mode=original;}
};
const se435PreviousBeginGrab=se390BeginGrab;
se390BeginGrab=function(record,purpose,pose){
 const s=se340XR;
 if(purpose!=='grab'||s.mode!=='grab')return se435PreviousBeginGrab(record,purpose,pose);
 const contact=se374GizmoContact(record);
 const axis=contact?.axis;
 // Only the actual visible X/Y/Z Move handles constrain Grab. Hidden modes,
 // nonhandle rays, and real menus retain the original behavior/priority.
 if(!['x','y','z'].includes(axis))return se435PreviousBeginGrab(record,purpose,pose);
 const selected=se350Tools().selection();
 if(!selected?.ids?.length)return se435PreviousBeginGrab(record,purpose,pose);
 const result=se350Tools().beginGroup(undefined,'move');
 if(result?.ok===false)return se390NoticeError(result);
 const root=se350Root();root.updateWorldMatrix(true,false);
 const g={kind:'group',record,id:selected.primaryId||selected.ids[0],
  mode:'move',axis,hand:pose,rootInverse:root.matrixWorld.clone().invert(),
  rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion())};
 s.gesture=g;se390BeginPose(g,pose);se372GuideStart(g);
 se340Notice('Move '+axis.toUpperCase()+' · Grip constrains this axis · release applies · B cancels.');
 se340Pulse(record,.2,20);
 return true;
};
window.SWYRL_ENGINE_MODEL_VR_GRAB_GIZMO=Object.freeze({inspect:()=>{
 const s=se340XR,g=s.se372Gizmo;
 return {version:'v11.435',mode:s.mode,selected:se350Tools().selection().ids.length,
  visible:!!g?.root?.visible,
  activeAxis:s.gesture?.axis||null,
  visualRoles:(g?.handles||[]).filter(h=>h.visible).map(h=>h.userData.se431Role)};
}});
/* SE435_MODEL_VR_GRAB_GIZMO_END */
