/* SE474_PROGRESSIVE_MODEL_TOOLS_START */
// Presentation controller only. Existing Model Atelier context, topology,
// transactions and component-selection bridges remain authoritative.
(function se474ProgressiveTools(){
 'use strict';
 const families=['Meshes','Sculpt','Lasso','Topology','Face','Appearance','Motion','References'];
 const meshOps=[
  ['inset','Inset'],['extrude','Extrude'],['subdivide','Subdivide'],
  ['splitEdge','Split edge'],['deleteFaces','Delete faces'],
  ['solidify','Solidify'],['fillHole','Fill hole'],['repairNormals','Repair normals']
 ];
 let state=null,scheduled=false;
 const byId=(id,root=document)=>root.querySelector('#'+id);
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const current=()=>window.SWYRL_E_CONTEXT?.current?.()||{};
 const context=()=>window.SWYRL_E_UNIFIED_TOOLS;
 function inspected(){try{return workshop()?.inspect?.()||null;}catch{return null;}}
 function previewPending(){return !!inspected()?.preview?.active;}
 function feedback(message){
  if(!state)return;
  state.feedback.textContent=message||'';
 }
 function nativeMode(mode){
  const api=workshop();
  const result=api?.setComponentMode?.(mode);
  if(result?.ok===false)feedback(result.reason||result.error||'Cannot change component selection.');
  return result?.ok!==false;
 }
 function chooseContext(group,operation){
  const api=context();
  if(!api?.select)return false;
  api.select(group,operation);
  return true;
 }
 function setOpen(open){
  if(!state)return;
  const p=state.panel;
  state.settings=!!open;
  p.dataset.se474SettingsOpen=String(state.settings);
  p.dataset.se474SpecificType=state.toolType||'none';
  p.dataset.se474SpecificMode=state.mode||'none';
  if(state.settings&&p.dataset.se251RightCollapsed==='true'){
   const toggle=p.querySelector('.se251-external-collapse');
   toggle?.click();
  }
  const inspector=p.querySelector('.atelier-inspector');
  if(inspector)inspector.setAttribute('aria-label',state.settings?state.family+' '+state.tool+' settings':'Model tool settings (closed)');
 }
 function makeButton(label,kind,value,pressed,disabled=false){
  const b=document.createElement('button');
  b.type='button';b.textContent=label;b.dataset.se474Kind=kind;b.dataset.se474Value=value;
  b.setAttribute('aria-pressed',String(!!pressed));b.disabled=disabled;
  return b;
 }
 function toolList(family){
  const fromNative=window.SWYRL_E_CONTEXT?.groups?.()?.[family]||[];
  const items=[...new Set(fromNative.filter(x=>typeof x==='string'&&x.trim()))].map(name=>({name,kind:'native'}));
  if(family==='Sculpt'||family==='Topology'){
   items.unshift({name:'Vertex',kind:'vertex'});
   for(const [operation,name]of meshOps.slice(0,2))items.push({name,kind:operation});
  }
  if(family==='Topology')for(const [operation,name]of meshOps.slice(2))items.push({name,kind:operation});
  return items.filter((item,index,array)=>array.findIndex(x=>x.name===item.name)===index);
 }
 function renderFlyout(){
  if(!state)return;
  state.flyout.hidden=!state.family||!state.flyoutOpen;
  state.flyout.setAttribute('aria-label',state.family+' tools');
  state.flyout.replaceChildren();
  const title=document.createElement('div');title.className='se474-flyout-title';
  title.textContent=state.family+' tools';
  const close=document.createElement('button');close.type='button';close.textContent='×';
  close.setAttribute('aria-label','Collapse '+state.family+' tool list');
  close.addEventListener('click',()=>{state.flyoutOpen=false;renderFlyout();});
  title.append(close);state.flyout.append(title);
  for(const item of toolList(state.family)){
   const button=makeButton(item.name,'tool',item.name,state.tool===item.name);
   button.dataset.se474ToolType=item.kind;state.flyout.append(button);
  }
 }
 function specificModes(){
  if(state.toolType==='vertex')return [['single','Single vertex'],['ring','Vertex ring'],['fill','Ring fill']];
  if(state.toolType==='inset'||state.toolType==='extrude')return [['face','Face'],['region','Region']];
  if(state.toolType==='manual')return meshOps.map(x=>[x[0],x[1]]);
  if(meshOps.some(x=>x[0]===state.toolType))return [['settings','Settings']];
  return [['settings','Tool settings']];
 }
 function renderTop(){
  if(!state)return;
  state.top.hidden=!state.tool;
  state.top.replaceChildren();
  if(!state.tool)return;
  const name=document.createElement('strong');
  name.className='se474-top-label';name.textContent=state.tool;
  state.top.append(name);
  for(const [value,label]of specificModes()){
   state.top.append(makeButton(label,'mode',value,state.mode===value));
  }
  state.top.append(state.feedback);
 }
 function selectFamily(family){
  if(previewPending()){feedback('Apply or Cancel the current geometry preview before switching tool families.');return;}
  if(state.family===family){
   state.flyoutOpen=!state.flyoutOpen;
  }else{
   state.family=family;state.tool='';state.toolType='';state.mode='';
   state.flyoutOpen=true;
  }
  // Retire the old staged Face flyout if it was open before this selection.
  if(state.panel.dataset.se452FaceOpen==='true')window.SWYRL_ENGINE_FACE_FLYOUTS_452?.close?.();
  // Activate the existing context without firing the legacy Face flyout.
  const native=toolList(family).find(x=>x.kind==='native');
  if(native)chooseContext(family,native.name);
  setOpen(false);renderFlyout();renderTop();
  state.panel.dataset.se474Family=family;
  feedback('');
 }
 function chooseTool(name,kind){
  if(previewPending()){feedback('Apply or Cancel the preview before selecting another tool.');return;}
  if(kind==='native'){
   if(!chooseContext(state.family,name))return;
  }else if(kind==='vertex'){
   nativeMode('vertex');
  }else if(meshOps.some(x=>x[0]===kind)){
   if(!chooseContext('Topology','Manual mesh modeling'))return;
   const select=byId('modelAtelierWorkshopOperation',state.panel);
   if(select&&select.value!==kind){select.value=kind;select.dispatchEvent(new Event('change',{bubbles:true}));}
  }
  state.tool=name;state.toolType=kind==='native'&&/manual mesh modeling/i.test(name)?'manual':kind;
  state.mode='';setOpen(false);renderFlyout();renderTop();
  feedback('Choose a specific mode above; its settings will appear in the right inspector.');
 }
 function nativeOperation(op){
  const select=byId('modelAtelierWorkshopOperation',state.panel);
  if(!select||![...select.options].some(o=>o.value===op))return false;
  if(select.value!==op){select.value=op;select.dispatchEvent(new Event('change',{bubbles:true}));}
  return true;
 }
 function selectRing(mode){
  const p=state.panel,api=workshop(),input=byId('se466RingMode',p);
  nativeMode('vertex');
  if(input&&input.value!==mode){input.value=mode;input.dispatchEvent(new Event('change',{bubbles:true}));}
  const inspectedState=inspected();
  if(!inspectedState?.ring?.centered){
   const ids=inspectedState?.selection?.ids||[];
   if(ids.length!==1){feedback('Tap exactly one vertex, then press "Use selected vertex as center" in settings.');return;}
   const r=api?.setRingAnchor?.();
   if(r?.ok===false){feedback(r.reason||r.error);return;}
  }
  const value=id=>Number(byId(id,p)?.value);
  const result=api?.selectRing?.({
   steps:value('se466RingSteps')||2,mode,
   arcStart:value('se466ArcStart')||0,arcSweep:value('se466ArcSweep')||360,
   plane:byId('se466RingPlane',p)?.value||'xz'
  });
  feedback(result?.message||result?.reason||'Adjust the selected ring in the inspector.');
 }
 function selectSpecific(mode){
  if(!state?.tool)return;
  if(previewPending()){feedback('Apply or Cancel the preview before changing operation modes.');return;}
  state.mode=mode;
  state.panel.dataset.se474SpecificType=state.toolType||'none';
  state.panel.dataset.se474SpecificMode=mode;
  let show=true;
  if(state.toolType==='vertex'){
   nativeMode('vertex');
   show=mode!=='single';
   if(show)selectRing(mode==='fill'?'fill':'outline');
   else feedback('Tap a single vertex in the viewport.');
  }else if(state.toolType==='inset'||state.toolType==='extrude'){
   nativeMode('face');nativeOperation(state.toolType);
   if(mode==='region'){
    const s=inspected(),face=s?.selection?.faceIds?.[0],part=s?.selection?.partId;
    if(Number.isInteger(face)){
     const result=workshop()?.selectRegion?.(face,part);
     if(result?.ok===false)feedback(result.reason||result.error||'Could not select flat region.');
    }else feedback('Tap a face first, then choose Region to expand the selection.');
   }
  }else if(state.toolType==='manual'){
   nativeOperation(mode);
   if(['inset','extrude','deleteFaces','solidify'].includes(mode))nativeMode('face');
   else if(mode==='splitEdge')nativeMode('edge');
  }
  setOpen(show);renderTop();
 }
 function mount(){
  const p=byId('modelAtelierPanel'),rail=p?.querySelector('#modelAtelierToolRail');
  const body=p?.querySelector('.atelier-body'),inspector=p?.querySelector('.atelier-inspector');
  if(!p||!rail||!body||!inspector||!context()?.select||!workshop()?.inspect)return;
  if(state?.panel===p&&state.rail===rail)return;
  const flyout=document.createElement('nav');
  flyout.id='se474ToolFlyout';flyout.className='se474-tool-flyout';
  flyout.setAttribute('aria-label','Tools for selected family');flyout.hidden=true;
  rail.append(flyout);
  const top=document.createElement('nav');top.id='se474SpecificModes';
  top.className='se474-specific-modes';top.setAttribute('aria-label','Specific tool modes');
  top.hidden=true;body.append(top);
  const line=document.createElement('output');
  line.id='se474ToolFeedback';line.className='se474-tool-feedback';
  line.setAttribute('role','status');line.setAttribute('aria-live','polite');
  state={panel:p,rail,flyout,top,feedback:line,family:'',tool:'',toolType:'',mode:'',flyoutOpen:false,settings:false};
  p.dataset.se474Progressive='true';p.dataset.se474SettingsOpen='false';p.dataset.se474SpecificType='none';
  // Capture just category choices before legacy "always show settings" and
  // Face flyout handlers. Native tools are activated through the same context.
  rail.addEventListener('click',event=>{
   if(event.target.closest('#se474ToolFlyout')||event.target.closest('#se473RailFold'))return;
   const button=event.target.closest('button');if(!button)return;
   const category=button.textContent.trim();
   if(!families.includes(category))return;
   event.preventDefault();event.stopImmediatePropagation();
   selectFamily(category);
  },true);
  flyout.addEventListener('pointerdown',event=>event.stopPropagation());
  flyout.addEventListener('click',event=>{
   const button=event.target.closest('button[data-se474-kind="tool"]');
   if(button)chooseTool(button.dataset.se474Value,button.dataset.se474ToolType);
   event.stopPropagation();
  });
  top.addEventListener('pointerdown',event=>event.stopPropagation());
  top.addEventListener('click',event=>{
   const b=event.target.closest('button[data-se474-kind="mode"]');
   if(b)selectSpecific(b.dataset.se474Value);
   event.stopPropagation();
  });
  p.addEventListener('keydown',event=>{
   if(event.key==='Escape'&&event.target.closest('#se474ToolFlyout')){
    state.flyoutOpen=false;renderFlyout();state.rail.querySelector('button:not(#se473RailFold)')?.focus();
   }
  });
  p.addEventListener('click',event=>{
   if(event.target.closest('#modelAtelierClose')){state.flyoutOpen=false;renderFlyout();setOpen(false);}
  },true);
  window.addEventListener('swrlz:model-workshop-change',()=>{
   if(state?.settings&&state.toolType==='vertex'&&state.mode==='single')setOpen(false);
  });
 }
 function schedule(){
  if(scheduled)return;scheduled=true;
  queueMicrotask(()=>{scheduled=false;mount();});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{mount();watch();},{once:true});
 else{mount();watch();}
 function watch(){
  const host=document.body;if(!host)return;
  const observer=new MutationObserver(records=>{
   if(state?.panel?.isConnected&&state.rail?.isConnected)return;
   if(records.some(r=>r.addedNodes.length))schedule();
  });
  observer.observe(host,{subtree:true,childList:true});
 }
 window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474=Object.freeze({
  version:'v11.474',
  inspect:()=>state&&{family:state.family,tool:state.tool,mode:state.mode,
   flyout:state.flyoutOpen,settings:state.settings},
  chooseFamily:family=>{if(families.includes(family)&&state)selectFamily(family);},
  chooseTool:(tool,kind)=>{if(state)chooseTool(tool,kind);},
  chooseMode:mode=>{if(state)selectSpecific(mode);}
 });
})();
/* SE474_PROGRESSIVE_MODEL_TOOLS_END */