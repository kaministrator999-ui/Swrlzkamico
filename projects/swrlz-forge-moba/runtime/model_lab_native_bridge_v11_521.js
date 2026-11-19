/* SE521_MODEL_LAB_NATIVE_BRIDGE_START
 * Narrow native Model Atelier authority for outer immersive XR menu.
 * No project data copied into the XR script, no parallel model or undo store.
 */
const se521NativeLab=(()=>{
 'use strict';
 const LABS=['model','rig','animate','texture'];
 const name=()=>String(currentProject?.instanceId||'');
 const active=()=>model();
 const lab=()=>{
  const xr=window.SWYRL_ENGINE_MODEL_VR_LABS_521;
  const vr=window.SWYRL_ENGINE_MODEL_VR?.inspect?.();
  if(vr?.active&&LABS.includes(xr?.lab?.()))return xr.lab();
  return LABS.includes(model()?.editorWorkspace?.vrLab)?model().editorWorkspace.vrLab:'model';
 };
 function setLab(next){
  if(!LABS.includes(next)||!model())return false;
  const m=model();m.editorWorkspace=m.editorWorkspace||{};
  m.editorWorkspace.vrLab=next;se220Playing=false;
  return true;
 }
 function deleteSelected(){
  const m=model(),ids=se350ModelTools.selection()?.ids||[];
  if(!m||!ids.length)return {ok:false,reason:'Select a mesh before Delete'};
  if(m.parts.length<=ids.length)return {ok:false,reason:'Keep at least one mesh in the model'};
  se521Journal.setLabel('Modeling · deleted '+ids.length+' selected mesh(es)');
  checkpoint();
  const selected=new Set(ids);
  m.parts=m.parts.filter(part=>!selected.has(part.id));
  selection=null;atelierMeshIds=[];
  signalEdited();
  return {ok:true,deleted:ids.length};
 }
 function animation(command){
  const r=se220RigAvailable()?se220Rig():null;
  if(!r)return {ok:false,reason:'A valid rig is required'};
  if(command==='animation-play'){
   if(se220Playing){se220Playing=false;se220RigPose(r.pose);}
   else if(r.timeline?.length>=2){
    se220Playing=true;se220PlayBegin=performance.now()-se220Time*1000;
   }else return {ok:false,reason:'At least two keyframes required'};
   return {ok:true,message:se220Playing?'Animation playing':'Animation stopped'};
  }
  if(command==='animation-key'){
   const t=+se220Time.toFixed(2),timeline=r.timeline||[];
   const index=timeline.findIndex(x=>Math.abs(x.time-t)<.02);
   if(index<0&&timeline.length>=32)return {ok:false,reason:'Maximum 32 keys'};
   se521Journal.setLabel('Animation · key pose at '+t.toFixed(2)+'s');
   const key={time:t,pose:structuredClone(r.pose)};
   if(index>=0)timeline[index]=key;
   else{timeline.push(key);timeline.sort((a,b)=>a.time-b.time);}
   se220RigTouched('Key saved at '+t.toFixed(2)+'s');
   return {ok:true,message:'Saved key at '+t.toFixed(2)+'s'};
  }
  if(command==='animation-loop'){
   r.loop=!r.loop;se521Journal.setLabel('Animation · loop '+(r.loop?'enabled':'disabled'));
   se220RigTouched('Animation loop '+(r.loop?'enabled':'disabled'));
   return {ok:true,message:'Loop '+(r.loop?'on':'off')};
  }
  if(['animation-prev','animation-next','animation-time-minus','animation-time-plus'].includes(command)){
   const times=(r.timeline||[]).map(x=>x.time).sort((a,b)=>a-b);
   let t=se220Time;
   if(command==='animation-prev')t=times.filter(v=>v<se220Time-.005).at(-1);
   else if(command==='animation-next')t=times.find(v=>v>se220Time+.005);
   else t=Math.max(0,Math.min(Number(r.duration)||2,se220Time+
      (command==='animation-time-plus'?.1:-.1)));
   if(t===undefined)return {ok:false,reason:'No further keyframe'};
   se220Time=t;se220Playing=false;
   se220RigPose(se220RigInterpolate(r,t));
   return {ok:true,message:'Playhead '+t.toFixed(2)+'s · preview only'};
  }
  return {ok:false,reason:'Unsupported animation operation'};
 }
 return Object.freeze({lab,setLab,projectId:name,deleteSelected,animation,
  journal:()=>se521Journal.inspect(),
  savedLab:()=>model()?.editorWorkspace?.vrLab||'model',
  selected:()=>se350ModelTools.selection()?.ids||[]});
})();
window.SWYRL_ENGINE_MODEL_LAB_NATIVE_521=se521NativeLab;
/* SE521_MODEL_LAB_NATIVE_BRIDGE_END */