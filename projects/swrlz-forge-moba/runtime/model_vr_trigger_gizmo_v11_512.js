/* SE512_MODEL_VR_TRIGGER_GIZMO_START */
// Controller Trigger capture for existing native XYZ/uniform transform gizmos.
// No changes to profile bindings or Grip-in-empty-space behavior.
const se512GizmoInput=(()=>{
 'use strict';
 const active=new Map(),previous=new Map();
 const keyOf=record=>record?.input?.handedness==='left'?'LT':'RT';
 const held=(sample,key)=>!!sample?.buttons?.[key]?.physical;
 const valid=record=>record?.targetTracked&&record?.gripTracked&&se340VisibleSession();
 function begin(record){
  const s=se340XR;
  if(!valid(record)||s.gesture||s.se390Creation||s.se372Sweep)return false;
  if(!['grab','move','rotate','scale'].includes(s.mode))return false;
  // Immediate contact test, not a cached hover hit. The native picker already
  // suppresses contacts behind floating UI and validates visible handle roles.
  const hit=se374GizmoContact(record);
  if(!hit?.gizmo)return false;
  const selection=se350Tools()?.selection?.();
  if(!selection?.ids?.length)return false;
  const mode=s.mode==='grab'?'move':s.mode;
  if(hit.axis==='uniform'&&mode!=='scale')return false;
  const pose=se340GripPose(record);
  if(!pose)return false;
  const result=se350Tools().beginGroup(undefined,mode);
  if(result?.ok===false){se390NoticeError(result);return false;}
  const root=se350Root();root.updateWorldMatrix(true,false);
  const gesture={kind:'group',record,id:selection.primaryId||selection.ids[0],
   mode,axis:hit.axis,hand:pose,
   rootInverse:root.matrixWorld.clone().invert(),
   rootQuaternion:root.getWorldQuaternion(new THREE.Quaternion()),
   se512Trigger:true};
  try{se390BeginPose(gesture,pose);se372GuideStart(gesture);}
  catch(error){se350Tools().cancel?.();se340Notice('Gizmo capture failed: '+String(error?.message||error),true);return false;}
  s.gesture=gesture;
  active.set(record,{key:keyOf(record),gesture});
  se340Notice('Trigger drag · '+mode+' '+hit.axis.toUpperCase()+' · release applies · B cancels.');
  se340Pulse(record,.18,18);return true;
 }
 function dispatch(sample,original){
  const suppressed=new Set();
  // Release first, so the same physical trigger cannot click the model after
  // completing a captured drag. Do not confuse a cancelled stroke with commit.
  for(const [record,session] of active){
   const down=held(sample,session.key);
   if(!down||!valid(record)||sample?.resetRequired||sample?.cancel){
    if(se340XR.gesture===session.gesture&&down===false&&valid(record)&&!sample?.resetRequired&&!sample?.cancel)
     se340FinishGesture(record);
    else if(se340XR.gesture===session.gesture)se340CancelGesture('Trigger gizmo edit canceled.');
    suppressed.add(session.key);active.delete(record);
   }
  }
  if(!sample?.resetRequired&&!sample?.cancel){
   for(const record of se340XR.controllers||[]){
    const key=keyOf(record),down=held(sample,key),was=previous.get(record)||false;
    if(down&&!was&&!active.size&&begin(record))suppressed.add(key);
   }
  }
  for(const record of se340XR.controllers||[])previous.set(record,held(sample,keyOf(record)));
  const events=sample.events?.filter(event=>{
   if(!['select','multiselect','stroke','sample'].includes(event.action))return true;
   const keys=event.keys||[];
   return !keys.some(key=>suppressed.has(key));
  })||[];
  return original({...sample,events});
 }
 function reset(){active.clear();previous.clear();}
 return Object.freeze({dispatch,reset,inspect:()=>({active:active.size,
  captured:[...active.values()].map(x=>({key:x.key,mode:x.gesture.mode,axis:x.gesture.axis}))})});
})();
const se512PriorDispatch=se350Dispatch;
se350Dispatch=function(sample){return se512GizmoInput.dispatch(sample,se512PriorDispatch);};
const se512PriorCleanup=se340Cleanup;
se340Cleanup=function(...args){se512GizmoInput.reset();return se512PriorCleanup.apply(this,args);};
// A panel remains at its placed world-space anchor but always presents its
// FRONT (+Z) to the headset. The existing orbit adapter owns position only.
const se512PriorMenuOrbit=se372MenuOrbit;
se372MenuOrbit=function(...args){
 const result=se512PriorMenuOrbit.apply(this,args);
 const s=se340XR,ui=s.ui,viewer=s.lastViewer;
 if(ui?.root?.visible&&viewer?.position?.isVector3&&s.se372MenuBase&&
    viewer.position.distanceToSquared(ui.root.position)>.02){
  ui.root.lookAt(viewer.position);
  ui.root.updateWorldMatrix(true,true);
 }
 return result;
};
window.SWYRL_ENGINE_MODEL_VR_TRIGGER_GIZMO_512=se512GizmoInput;
/* SE512_MODEL_VR_TRIGGER_GIZMO_END */
