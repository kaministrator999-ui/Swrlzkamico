/* §E v11.490 — per-project Model Studio workspace and cloth skin binding. */
const se490Workspace=(()=>{
 'use strict';
 const PREFIX='swrlz.engine.modeler.workspace.v2:';
 let restoring=false,opening=false,pending=0,lastKey='';
 const finite=v=>Number.isFinite(v)&&Math.abs(v)<1e5;
 const vector=v=>Array.isArray(v)&&v.length===3&&v.every(finite);
 const rigged=()=>se220RigAvailable()&&se220Rig()?.schema==='swyrl-cloth-skin-v1';
 function identity(){
  const m=model(),p=currentProject;
  if(!m||!Array.isArray(m.parts))return null;
  const id=m.se470DraftId||p?.instanceId||p?.id||p?.canonicalId;
  if(typeof id!=='string'||!id||id.length>160)return null;
  return PREFIX+encodeURIComponent(id);
 }
 function snapshot(){
  if(!panel||panel.hidden||!model())return null;
  const cam=se430ModelCamera?.inspect?.();
  if(!cam?.ready||!vector(cam.position)||!vector(cam.target))return null;
  const native=window.SWYRL_E_UNIFIED_TOOLS?.current?.();
  return {schema:'swyrl-model-workspace-v2',
   camera:{position:cam.position.slice(),target:cam.target.slice(),
    projection:cam.projection,view:cam.view},
   selectedPart:typeof selection==='string'?selection:null,
   tool:native?.category&&native?.mode?{category:native.category,mode:native.mode}:null,
   rig:rigged()?{clip:se220Rig().activeClip,time:se220Time}:null,
   railCollapsed:window.SWYRL_ENGINE_TOOL_RAIL_473?.state?.()?.collapsed===true,
   rightCollapsed:panel.dataset.se251RightCollapsed==='true',
   dock:window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251?.modelDock?.()||null,
   rigPanelOpen:!!se220R('Studio')?.open,
   inspectorScroll:panel.querySelector('.atelier-inspector')?.scrollTop||0};
 }
 function valid(s){return !!s&&s.schema==='swyrl-model-workspace-v2'&&
  vector(s.camera?.position)&&vector(s.camera?.target)&&
  ['perspective','orthographic'].includes(s.camera.projection)&&
  (s.selectedPart===null||typeof s.selectedPart==='string'&&s.selectedPart.length<160)&&
  (s.rig==null||typeof s.rig.clip==='string'&&finite(s.rig.time)&&s.rig.time>=0&&s.rig.time<=30);}
 function persist(){
  if(opening||restoring)return false;
  const key=identity(),state=snapshot();if(!key||!state)return false;
  try{localStorage.setItem(key,JSON.stringify(state));lastKey=key;
   model().editorWorkspace=structuredClone(state);return true;
  }catch{return false;}
 }
 function schedule(){
  if(opening||restoring||pending)return;
  pending=setTimeout(()=>{pending=0;persist();},300);
 }
 function restore(){
  const key=identity();if(!key||!panel||panel.hidden)return false;
  let saved=null;
  try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch{}
  if(!valid(saved)&&valid(model()?.editorWorkspace))saved=model().editorWorkspace;
  if(!valid(saved))return false;
  restoring=true;
  try{
   if(saved.tool)window.SWYRL_E_UNIFIED_TOOLS?.select?.(saved.tool.category,saved.tool.mode);
   if(saved.selectedPart&&partById(saved.selectedPart))select(saved.selectedPart);
   const rail=window.SWYRL_ENGINE_TOOL_RAIL_473;
   if(typeof saved.railCollapsed==='boolean'&&rail?.state?.()?.collapsed!==saved.railCollapsed)rail?.toggle?.();
   const docks=window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251;
   if(saved.dock&&docks?.setModelDock)docks.setModelDock(saved.dock);
   else if(typeof saved.rightCollapsed==='boolean'&&
    (panel.dataset.se251RightCollapsed==='true')!==saved.rightCollapsed)
    panel.querySelector('.se251-external-collapse')?.click();
   const bones=se220R('Studio');if(bones&&typeof saved.rigPanelOpen==='boolean')bones.open=saved.rigPanelOpen;
   if(rigged()&&saved.rig&&Object.hasOwn(se220Rig().clips,saved.rig.clip)){
    if(se220Rig().activeClip!==saved.rig.clip)se489SelectClip(saved.rig.clip);
    se220Playing=false;
    se220Time=Math.max(0,Math.min(se220Rig().duration,saved.rig.time));
    se220Rig().pose=se220RigInterpolate(se220Rig(),se220Time);
    se220RigPose(se220Rig().pose);
    se220RigRefresh();
   }
   if(typeof saved.camera.view==='string'&&saved.camera.view!=='orbit')
    se430ModelCamera?.setView?.(saved.camera.view);
   window.SWYRL_ENGINE_STARTUP_CAMERA_476?.restore?.(saved.camera);
   const inspector=panel.querySelector('.atelier-inspector');
   if(inspector&&finite(saved.inspectorScroll))inspector.scrollTop=Math.max(0,saved.inspectorScroll);
   return true;
  }finally{restoring=false;}
 }
 function ensureSkinBinding(){
  if(!rigged()||!modelRoot)return;
  const part=model()?.parts.find(p=>p.id===se220Rig().targetPartId);
  if(!part)return;
  const existing=modelRoot.children.find(o=>o.userData?.atelierId===part.id);
  if(!existing||existing.isSkinnedMesh)return;
  const skinned=se220RigMesh(part);
  if(!skinned?.isSkinnedMesh){status('Cloth geometry could not attach to the skeleton.',true);return;}
  skinned.name=existing.name;skinned.userData={...existing.userData};
  skinned.position.copy(existing.position);skinned.rotation.copy(existing.rotation);
  skinned.scale.copy(existing.scale);skinned.visible=existing.visible;
  skinned.castShadow=existing.castShadow;skinned.receiveShadow=existing.receiveShadow;
  modelRoot.remove(existing);modelRoot.add(skinned);
  existing.geometry?.dispose();existing.material?.dispose();
  se220RigBind();
 }
 const previousRender=renderParts;
 renderParts=function(...args){
  const result=previousRender.apply(this,args);
  ensureSkinBinding();return result;
 };
 const previousOpen=open;
 open=function(...args){
  opening=true;
  const result=previousOpen.apply(this,args);
  if(result===false){opening=false;return result;}
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   setTimeout(()=>{restore();opening=false;},100);
  }));
  return result;
 };
 const previousClose=close;
 close=function(...args){
  clearTimeout(pending);pending=0;
  opening=false;persist();
  return previousClose.apply(this,args);
 };
 const previousCameraUpdate=cameraUpdate;
 cameraUpdate=function(...args){
  const result=previousCameraUpdate.apply(this,args);schedule();return result;
 };
 window.addEventListener('pagehide',()=>{clearTimeout(pending);pending=0;opening=false;persist();});
 document.addEventListener('change',event=>{if(panel?.contains(event.target))schedule();},true);
 document.addEventListener('pointerup',event=>{if(panel?.contains(event.target))schedule();},true);
 return Object.freeze({capture:snapshot,restore,persist,identity,
  status:()=>({key:lastKey,restoring,skinned:!!modelRoot?.children.some(o=>o.isSkinnedMesh),
   rigAvailable:se220RigAvailable(),time:se220Time,clip:se220Rig()?.activeClip})});
})();
window.SWYRL_ENGINE_MODEL_WORKSPACE_490=se490Workspace;
