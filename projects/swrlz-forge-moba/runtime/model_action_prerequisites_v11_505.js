/* SE505_ACTION_PREREQUISITES_START
   Centralized, consent-driven prerequisites for native Model Studio actions.
   Never guess a component selection or mutate on Cancel. */
const se505ActionRequirements=(()=>{
 'use strict';
 let inFlight=false,lastResult=null,hookedPanel=null;
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const progress=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474;
 const copies=()=>window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481;
 const failure=reason=>({ok:false,reason});
 const selected=()=>partById(selection);
 function inspect(){
  const part=selected(),project=model(),api=workshop(),native=api?.inspect?.();
  if(!project)return {kind:'blocked',reason:'Open a Model Studio project first.'};
  if(!part){
   const visible=project.parts.filter(p=>!p.se481SourceHidden&&!p.se481WorkHidden);
   if(visible.length===1)return {kind:'auto-select',project,part:visible[0],partId:visible[0].id,
    explanation:'The project has one visible mesh. Select it and continue the requested tool.'};
   return {kind:'blocked',reason:'Select which mesh to edit; this project has '+visible.length+' visible objects.'};
  }
  const multiple=(atelierMeshIds||[]).filter(id=>partById(id)).length>1;
  if(multiple)return {kind:'blocked',reason:'Select one mesh at a time. Choose which object you want to edit.'};
  if(native?.preview?.active)return {kind:'blocked',reason:'Apply or Cancel the current modeling preview first.'};
  if(part.kind==='topologyMesh')return {kind:'ready',partId:part.id,project,part};
  if(part.se481WorkId){
   const linked=partById(part.se481WorkId);
   if(linked?.kind==='topologyMesh')return {kind:'reuse',partId:part.id,project,part,copyId:linked.id,
    explanation:'An editable working copy already exists. Switch to it and continue. Original source is retained.'};
  }
  const state=copies()?.inspect?.();
  if(state?.available)return {kind:'textured-copy',partId:part.id,project,part,
    explanation:'Make a UV-preserving editable working copy of '+(part.name||'this mesh')+
     '? The original stays in this project, hidden and recoverable. The painted texture and UV coordinates are preserved. This creates one Undo step.'};
  if(native?.convert?.available)return {kind:'native',partId:part.id,project,part,
    explanation:'Make '+(part.name||'this mesh')+' editable? Its primitive geometry will become indexed topology with regenerated plain UVs. One Undo step restores the original.'};
  return {kind:'blocked',partId:part.id,project,part,
   reason:state?.reason&&part.uvPaintPNG?state.reason:
     native?.convert?.reason||state?.reason||'This model cannot be safely converted with the available editing tools.'};
 }
 function report(message,error=false){
  if(typeof status==='function')status(message,error);
  const line=document.getElementById('se503AtlasStatus');
  if(line&&error)line.textContent=message;
  const progressive=document.getElementById('se474ToolFeedback');
  if(progressive)progressive.textContent=message;
 }
 function perform(plan){
  if(plan.kind==='native')return workshop()?.convert?.()||failure('Native conversion is not available.');
  if(plan.kind==='textured-copy')return copies()?.prepare?.()||failure('UV-preserving copy is not available.');
  if(plan.kind==='reuse')return copies()?.switchSource?.()||failure('Existing editable copy cannot be selected.');
  return failure('This prerequisite has no approved conversion.');
 }
 function requireEditable(action,continueAction,mode=null){
  if(inFlight)return failure('Another mesh conversion is already running.');
  if(typeof continueAction!=='function')return failure('Missing requested operation to resume.');
  const original=inspect();const intent=String(action||'this action');
  if(original.kind==='blocked'){report(original.reason,true);return lastResult=failure(original.reason);}
  if(original.kind==='ready'){
   const r=continueAction();lastResult={ok:true,kind:'ready',result:r};return lastResult;
  }
  if(original.kind==='auto-select'){
   select(original.partId);
   if(model()!==original.project||selected()!==original.part)
    return lastResult=failure('Could not select the only visible mesh.');
   // Selection is only the first prerequisite: recheck topology and ask for
   // conversion if the newly selected mesh still needs one.
   const resumed=requireEditable(action,continueAction,mode);
   return lastResult=resumed.ok?{...resumed,autoSelected:true}:resumed;
  }
  if(typeof window.confirm!=='function')return lastResult=failure('Confirmation is unavailable. No conversion performed.');
  const accepted=window.confirm('Before '+intent+':\n\n'+original.explanation+'\n\nContinue with '+intent+' after preparing the mesh?');
  if(!accepted)return lastResult={ok:false,cancelled:true,reason:'Cancelled; original mesh unchanged.'};
  // Synchronous modal returns without authorizing a different selected part.
  if(model()!==original.project||selected()!==original.part||selection!==original.partId)
   return lastResult=failure('The selected mesh changed. Repeat your requested action.');
  inFlight=true;
  try{
   const result=perform(original);
   if(!result?.ok){report(result?.reason||result?.error||'Editable conversion failed.',true);
    return lastResult=failure(result?.reason||'Conversion failed.');}
   if(model()!==original.project||selected()?.kind!=='topologyMesh')
    return lastResult=failure('Mesh conversion did not produce the expected editable selection.');
   if(mode&&workshop()?.inspect?.()?.selection?.mode!==mode){
    const switched=workshop()?.setComponentMode?.(mode);
    if(switched?.ok===false){report(switched.reason,true);return lastResult=failure(switched.reason);}
   }
   const prepared=selected();
   // An explicit continuation is called only after conversion success.
   queueMicrotask(()=>{
    if(model()!==original.project||selected()!==prepared){
     report('The selection changed after conversion. The original action was not resumed.',true);return;
    }
    try{continueAction();}catch(e){report('Converted, but could not resume '+intent+': '+String(e?.message||e),true);}
   });
   report('Editable mesh ready. Continuing '+intent+'.');
   return lastResult={ok:true,kind:original.kind,resuming:true,partId:prepared.id};
  }finally{inFlight=false;}
 }
 const priorUVInstall=se503Install;
 se503Install=function(...args){
  const result=priorUVInstall.apply(this,args);
  const root=document.getElementById('se503AtlasTool');
  const button=root?.querySelector('#se503AtlasPrepare');
  if(button&&!button.dataset.se505Requirements){
   button.dataset.se505Requirements='true';
   button.addEventListener('click',event=>{
    const plan=inspect();
    if(plan.kind==='ready')return;
    event.preventDefault();event.stopImmediatePropagation();
    requireEditable('Preview UV atlas',()=>se503Prepare());
   },true);
  }
  se503Refresh();
  return result;
 };
 const priorUVRefresh=se503Refresh;
 se503Refresh=function(...args){
  const r=priorUVRefresh.apply(this,args);
  const root=document.getElementById('se503AtlasTool');
  const button=root?.querySelector('#se503AtlasPrepare');
  if(button){
   const plan=inspect();
   if(['native','textured-copy','reuse','auto-select'].includes(plan.kind)){
    button.disabled=false;
    button.title=plan.kind==='auto-select'?'Select only visible mesh, then preview.':'Offer editable conversion, then preview UV islands.';
    button.textContent=plan.kind==='auto-select'?'Select mesh & Preview UV atlas':'Make editable & Preview UV atlas';
    if(!se503Preview)root.querySelector('#se503AtlasStatus').textContent=
      plan.kind==='auto-select'?'The only visible mesh will be selected automatically.':
       'This action can prepare the mesh for editing, then immediately preview the UV atlas.';
   }else {
    button.textContent='Preview UV atlas';
    if(plan.kind==='blocked'&&!se503Preview){
     button.disabled=true;
     root.querySelector('#se503AtlasStatus').textContent=plan.reason;
    }
   }
  }
  return r;
 };
 const topologyTypes=new Set(['vertex','inset','extrude','deleteFaces','solidify',
   'splitEdge','subdivide','fillHole','repairNormals']);
 function requiresTopology(kind,name){
  return topologyTypes.has(kind)||(kind==='native'&&/manual mesh modeling/i.test(name||''));
 }
 function intercept(event){
  const button=event.target.closest?.('button');
  if(!button||button.disabled)return;
  const plan=inspect();if(plan.kind==='ready')return;
  const tool=button.closest('#se474ToolFlyout');
  const mode=button.closest('#se474SpecificModes');
  if(tool&&button.dataset.se474Kind==='tool'){
   const kind=button.dataset.se474ToolType,name=button.dataset.se474Value;
   if(!requiresTopology(kind,name))return;
   event.preventDefault();event.stopImmediatePropagation();
   if(plan.kind==='blocked'){report(plan.reason,true);return;}
   requireEditable('use '+name,()=>progress()?.chooseTool(name,kind),
    kind==='vertex'?'vertex':null);
   return;
  }
  if(mode&&button.dataset.se474Kind==='mode'){
   const state=progress()?.inspect?.(),kind=state?.toolType;
   if(!requiresTopology(kind,state?.tool))return;
   const value=button.dataset.se474Value;
   event.preventDefault();event.stopImmediatePropagation();
   if(plan.kind==='blocked'){report(plan.reason,true);return;}
   requireEditable('choose '+value+' mode',()=>progress()?.chooseMode(value),
    kind==='vertex'?'vertex':null);
  }
 }
 function install(){
  const panel=document.getElementById('modelAtelierPanel');
  if(!panel||hookedPanel===panel)return;
  hookedPanel=panel;
  panel.addEventListener('click',intercept,true);
 }
 const priorEnsurePanel=ensurePanel;
 ensurePanel=function(...args){
  const result=priorEnsurePanel.apply(this,args);install();return result;
 };
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else install();
 window.SWYRLZ_E_REQUIREMENTS_505=Object.freeze({
  inspect:()=>{const x=inspect();return {kind:x.kind,partId:x.partId||null,
   reason:x.reason||null,explanation:x.explanation||null};},
  requireEditable,refresh:()=>{install();se503Refresh();},
  last:()=>lastResult
 });
 return Object.freeze({inspect,requireEditable});
})();
/* SE505_ACTION_PREREQUISITES_END */