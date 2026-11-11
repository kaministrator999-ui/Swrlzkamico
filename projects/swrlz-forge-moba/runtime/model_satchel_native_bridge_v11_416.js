/* SE416_SATCHEL_NATIVE_BRIDGE_START
 * Lives in the native Model Atelier lexical scope and delegates only validated
 * edits. The tutorial cannot mutate meshes through cloned button previews.
 */
(function se415ExposeNativeSatchel(){
 'use strict';
 const lesson=()=>currentProject?.se412Tutorial==='satchel-001';
 function valid(parts){
  return Array.isArray(parts)&&parts.length>0&&parts.length<=MODEL_ATELIER_LIMIT&&
   new Set(parts.map(p=>p?.id)).size===parts.length&&parts.every(p=>checkPart(p));
 }
 function busy(){
  return !!(typeof se340XR!=='undefined'&&(se340XR.gesture||se340XR.se390Creation))||
   !!(typeof se350ModelTools!=='undefined'&&se350ModelTools.inspect().gesture);
 }
 function restore(next){
  if(!lesson()||!model()||!valid(next))return {ok:false,message:'Checkpoint model failed native validation.'};
  if(busy())return {ok:false,message:'Finish or cancel the active VR edit first.'};
  checkpoint();
  model().parts.splice(0,model().parts.length,...structuredClone(next));
  selection=null;atelierMeshIds=[];signalEdited();
  return {ok:true};
 }
 function paint(material,color){
  if(!lesson()||!model())return {ok:false,message:'Open the satchel model tutorial first.'};
  if(busy())return {ok:false,message:'Finish the active gesture before changing materials.'};
  if(!MODEL_ATELIER_MATERIALS.includes(material)||!/^#[0-9a-fA-F]{6}$/.test(color))
   return {ok:false,message:'Invalid material or color.'};
  const ids=se350ModelTools.selection().ids;
  if(!ids.length)return {ok:false,message:'Select a real satchel part with Trigger first.'};
  const targets=ids.map(partById);
  if(targets.some(p=>!p||!checkPart({...p,material,color})))return {ok:false,message:'Selected material change failed native validation.'};
  if(targets.every(p=>p.material===material&&p.color===color))
   return {ok:true,changed:false,message:'Selected parts already use that material.'};
  checkpoint();
  for(const part of targets){part.material=material;part.color=color;}
  signalEdited();
  return {ok:true,changed:true,message:'Applied '+material+' to '+targets.length+' selected part'+(targets.length>1?'s':'')+'. Undo remains available.'};
 }
 function shade(direction=1){
  if(!lesson()||!model()||busy())return {ok:false,message:'Select a satchel part and finish the active gesture first.'};
  const ids=se350ModelTools.selection().ids,targets=ids.map(partById);
  if(!targets.length)return {ok:false,message:'Select an editable satchel part first.'};
  const palette=['#916b48','#70452f','#b18a61','#453427','#c9a56c','#9dbaae','#ded6ce'];
  const base=palette.indexOf(targets[0].color?.toLowerCase()),color=palette[(base+direction+palette.length)%palette.length];
  if(targets.some(p=>!p||!checkPart({...p,color})))return {ok:false,message:'Color change rejected by native part validation.'};
  checkpoint();for(const p of targets)p.color=color;signalEdited();
  return {ok:true,changed:true,message:'Applied color '+color+' to '+targets.length+' selected part'+(targets.length>1?'s':'')+'.'};
 }
 const oldRender=renderParts;
 renderParts=function(...args){const result=oldRender.apply(this,args);
  window.SWYRL_E_SATCHEL_ACADEMY_416?.onNativeRender?.();return result;};
 window.SWYRL_E_SATCHEL_NATIVE_416=Object.freeze({
  root:()=>modelRoot,
  validate:valid,
  restore,
  paint,
  shade,
  busy,
  selected:()=>se350ModelTools.selection().ids,
  inspect:()=>({ready:!!model()&&lesson(),parts:model()?.parts.length||0,editorOpen:!!panel})
 });
})();
 /* SE416_SATCHEL_NATIVE_BRIDGE_END */