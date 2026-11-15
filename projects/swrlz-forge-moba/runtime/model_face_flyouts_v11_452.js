/* SE452_NATIVE_FACE_FLYOUTS_START */
// Move, don't recreate, the existing Face quick controls and guided modifiers.
// se430/se448/se450/se451 remain the only geometry, preview and Undo owners.
(function(){
 'use strict';
 const previousInstall=se430BeginnerInstall;
 let current=null;
 function mount(panel){
  if(!panel||panel.dataset.se452NativeFace==='1')return;
  const body=panel.querySelector('.atelier-body'),inspector=panel.querySelector('.atelier-inspector');
  const rail=panel.querySelector('#modelAtelierToolRail');
  const quick=panel.querySelector('#se445ShapeQuick');
  const guided=panel.querySelector('#se451FaceWorkflow');
  if(!body||!inspector||!rail||!quick||!guided)return;
  panel.dataset.se452NativeFace='1';
  panel.dataset.se452FaceOpen='false';
  panel.dataset.se452Stage='closed';
  // Anchors restore original DOM ordering and original event listeners.
  const quickAnchor=document.createComment('se452-original-face-tools');
  const guidedAnchor=document.createComment('se452-original-guided-modifiers');
  quick.before(quickAnchor);guided.before(guidedAnchor);

  const operations=document.createElement('aside');
  operations.id='se452FaceOperations';
  operations.setAttribute('aria-label','Face operations');
  operations.hidden=true;
  operations.innerHTML='<header class="se452-face-header">'+
   '<strong>Face tools</strong><button type="button" data-se452-close aria-label="Close face tools">×</button></header>'+
   '<div id="se452FaceOperationsContent"></div>';
  const modifiers=document.createElement('aside');
  modifiers.id='se452FaceModifiers';
  modifiers.setAttribute('aria-label','Face tool modifiers');
  modifiers.hidden=true;
  modifiers.innerHTML='<header class="se452-face-header">'+
   '<button type="button" data-se452-back aria-label="Back to face tools">‹</button>'+
   '<strong>Tool settings</strong><button type="button" data-se452-close aria-label="Close face tools">×</button></header>'+
   '<div id="se452FaceModifiersContent"></div>';
  body.append(operations,modifiers);
  const opsHolder=operations.querySelector('#se452FaceOperationsContent');
  const modHolder=modifiers.querySelector('#se452FaceModifiersContent');
  const api=()=>se430BeginnerAPI();
  const inspect=()=>{try{return api()?.inspect?.()||null;}catch{return null;}};
  const isPreview=()=>!!inspect()?.preview?.active;
  const active=()=>panel.dataset.se452FaceOpen==='true';
  let previousContext=null,transit=false;

  function restore(){
   if(quick.parentNode!==quickAnchor.parentNode||quick.previousSibling!==quickAnchor)
    quickAnchor.after(quick);
   if(guided.parentNode!==guidedAnchor.parentNode||guided.previousSibling!==guidedAnchor)
    guidedAnchor.after(guided);
  }
  function status(msg){
   const line=guided.querySelector('#se451Step')||quick.querySelector('.se445-shape-hint');
   if(line)line.textContent=msg;
  }
  function stage(value){
   panel.dataset.se452Stage=value;
   operations.hidden=value==='closed'||value==='advanced';
   modifiers.hidden=value!=='modifiers';
  }
  function open(){
   if(!active())previousContext=window.SWYRL_E_CONTEXT?.current?.()||null;
   // Use the native context and operation codepaths; no project mutations.
   const context=window.SWYRL_E_CONTEXT?.current?.()||{};
   if(context.group!=='Topology'||!/manual mesh modeling/i.test(context.operation||'')){
    window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
   }
   opsHolder.append(quick);modHolder.append(guided);
   panel.dataset.se452FaceOpen='true';
   panel.dataset.se451Advanced='false';
   stage('operations');
   window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
  }
  function revealModifiers(){
   if(!active())open();
   if(panel.dataset.se452FaceOpen!=='true')return;
   stage('modifiers');
   window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
   // Native guided code decides visibility based on actual tool context.
   if(guided.hidden){
    const context=window.SWYRL_E_CONTEXT?.current?.()||{};
    if(context.group!=='Topology')window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
    window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
   }
  }
  function close(){
   if(isPreview()){
    revealModifiers();
    status('Preview pending. Apply commits one Undo step; Cancel discards the preview.');
    return false;
   }
   restore();panel.dataset.se452FaceOpen='false';
   stage('closed');window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
   se430BeginnerQueue();return true;
  }
  function showAdvanced(){
   // The original inspector and its native controls are always recoverable.
   restore();panel.dataset.se452FaceOpen='false';stage('advanced');
   panel.dataset.se451Advanced='true';
   const button=panel.querySelector('.se251-external-collapse');
   if(panel.dataset.se251RightCollapsed==='true')button?.click();
   window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
   se430BeginnerQueue();
  }
  function back(){
   if(isPreview()){
    status('Apply or Cancel the preview before changing tools.');
    return false;
   }
   stage('operations');return true;
  }
  function ifFaceRail(event){
   const button=event.target.closest('button');
   if(!button||!rail.contains(button))return;
   const label=(button.dataset.se320Category||button.textContent||'').trim().toLowerCase();
   // Other categories retain the existing inspector and tool behaviors.
   if(/^(?:face|face tools|topology)$/.test(label)){
    queueMicrotask(open);
   }else if(active()&&!transit){
    queueMicrotask(close);
   }
  }
  rail.addEventListener('click',ifFaceRail);
  operations.addEventListener('click',event=>{
   const b=event.target.closest('button');if(!b)return;
   if(b.hasAttribute('data-se452-close')){close();return;}
   const op=b.closest('#se445ShapeQuick [data-se445-op]');
   if(!op)return;
   const action=op.dataset.se445Op;
   // The existing faceQuick listener executes first, then reveal modifiers
   // only for an actual Face operation. 'All' exposes the native inspector.
   queueMicrotask(()=>action==='more'?showAdvanced():revealModifiers());
  });
  modifiers.addEventListener('click',event=>{
   const b=event.target.closest('button');if(!b)return;
   if(b.hasAttribute('data-se452-close')){close();return;}
   if(b.hasAttribute('data-se452-back')){back();return;}
   if(b.id==='se451Advanced')queueMicrotask(showAdvanced);
  });
  panel.addEventListener('keydown',event=>{
   if(event.key!=='Escape'||!event.target.closest('#se452FaceOperations,#se452FaceModifiers'))return;
   event.preventDefault();if(panel.dataset.se452Stage==='modifiers')back();else close();
  });
  panel.addEventListener('click',event=>{
   if(event.target.closest('#modelAtelierClose')&&!isPreview())close();
  },true);
  window.addEventListener('swrlz:model-workshop-change',()=>{
   if(!active())return;
   // Observe native preview state, but never force a redraw or write geometry.
   queueMicrotask(()=>{if(!isPreview()&&panel.dataset.se452Stage==='modifiers'){
    window.SWYRL_ENGINE_GUIDED_FACE_451?.refresh?.();
   }});
  });
  current=Object.freeze({
   open,revealModifiers,back,close,showAdvanced,
   inspect:()=>({opened:active(),stage:panel.dataset.se452Stage,
     preview:isPreview(),originalQuickControls:quick===opsHolder.firstElementChild,
     originalModifierControls:guided===modHolder.firstElementChild,
     geometryWrites:0})
  });
 }
 se430BeginnerInstall=function(panel){
  const result=previousInstall(panel);
  mount(panel);
  return result;
 };
 window.SWYRL_ENGINE_FACE_FLYOUTS_452=Object.freeze({
  version:'v11.452',
  inspect:()=>current?.inspect()||{opened:false,stage:'closed'},
  open:()=>current?.open(),close:()=>current?.close()
 });
})();
/* SE452_NATIVE_FACE_FLYOUTS_END */