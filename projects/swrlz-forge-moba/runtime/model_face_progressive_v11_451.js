/* SE451_FACE_PROGRESSIVE_DOCK_START */
// Visible UI only: native workshop remains the sole model/undo authority.
// Stage 1 = existing tool rail; stage 2 = face operations; stage 3 = modifiers.
(function(){
 'use strict';
 const oldInstall=se430BeginnerInstall;
 let installed=null;
 function mount(panel){
  if(!panel||panel.dataset.se451Progressive==='1')return;
  const body=panel.querySelector('.atelier-body'),rail=panel.querySelector('#modelAtelierToolRail');
  const inspector=panel.querySelector('.atelier-inspector'),workshop=panel.querySelector('#modelAtelierTopologyWorkshop');
  if(!body||!rail||!inspector||!workshop)return;
  panel.dataset.se451Progressive='1';
  const home=workshop.parentNode,next=workshop.nextSibling;
  const ops=document.createElement('section');ops.id='se451FaceOperations';ops.hidden=true;
  ops.setAttribute('aria-label','Face modeling tools');
  ops.innerHTML='<header><strong>Face tools</strong><button type="button" data-se451-close aria-label="Close face tools">×</button></header>'+
   '<div class="se451-tool-list" role="group" aria-label="Face operations">'+
   '<button type="button" data-se451-op="inset" aria-pressed="false">▣ Inset</button>'+
   '<button type="button" data-se451-op="extrude" aria-pressed="false">↑ Extrude</button>'+
   '<button type="button" data-se451-op="solidify" aria-pressed="false">▤ Solidify</button>'+
   '<button type="button" data-se451-op="subdivide" aria-pressed="false">◇ Subdivide</button>'+
   '<button type="button" data-se451-more>All face tools</button></div>'+
   '<p class="se451-menu-help">Choose a tool, tap a square face, inspect the preview, then Apply.</p>';
  const settings=document.createElement('section');settings.id='se451FaceSettings';settings.hidden=true;
  settings.setAttribute('aria-label','Face operation modifiers');
  settings.innerHTML='<header><button type="button" data-se451-back aria-label="Back to face operations">‹</button>'+
   '<strong id="se451SettingsTitle">Inset settings</strong><button type="button" data-se451-close aria-label="Close face tools">×</button></header>'+
   '<p id="se451FaceMessage" role="status" aria-live="polite"></p>'+
   '<label class="se451-range-label" for="se451FaceRange">Amount</label>'+
   '<input type="range" id="se451FaceRange" min=".03" max=".8" step=".05" value=".2" aria-label="Operation amount slider">'+
   '<div id="se451NativeHolder"></div>';
  body.append(ops,settings);
  const holder=settings.querySelector('#se451NativeHolder'),range=settings.querySelector('#se451FaceRange');
  const message=settings.querySelector('#se451FaceMessage'),title=settings.querySelector('#se451SettingsTitle');
  let op=null,amountTimer=0;
  const api=()=>se430BeginnerAPI();
  const state=()=>{try{return api()?.inspect?.()||null;}catch{return null;}};
  const preview=()=>!!state()?.preview?.active;
  const note=text=>{message.textContent=String(text||'');};
  function restoreNative(){
   if(workshop.parentNode===home)return;
   if(next?.parentNode===home)home.insertBefore(workshop,next);
   else home.append(workshop);
  }
  function sync(){
   if(panel.dataset.se451FaceOpen!=='true')return;
   const current=state();if(!current)return;
   ops.querySelectorAll('[data-se451-op]').forEach(b=>
    b.setAttribute('aria-pressed',String(b.dataset.se451Op===op)));
   if(!op)return;
   const amount=workshop.querySelector('#modelAtelierWorkshopAmount');
   if(amount){
    for(const attr of ['min','max','step'])if(amount.hasAttribute(attr))range.setAttribute(attr,amount.getAttribute(attr));
    if(document.activeElement!==range&&range.value!==amount.value)range.value=amount.value;
    range.disabled=amount.disabled;
   }
   title.textContent=op.charAt(0).toUpperCase()+op.slice(1)+' settings';
   settings.querySelector('.se451-range-label').textContent=
    workshop.querySelector('#se430AmountLabel')?.textContent||'Amount';
   const selection=current.selection||{};
   if(current.preview?.active)note('Preview visible. Apply commits one Undo step; Cancel keeps the original.');
   else if(!selection.partId)note('Choose one mesh first, then tap a square face.');
   else if(!selection.faceIds?.length)note('Tool armed. Tap a whole square face to preview.');
   else note('Face selected. Preview geometry, then Apply or Cancel.');
  }
  function open(){
   panel.dataset.se451FaceOpen='true';panel.dataset.se451Stage='operations';
   ops.hidden=false;settings.hidden=true;sync();
  }
  function close(){
   if(preview()){
    settings.hidden=false;panel.dataset.se451Stage='settings';
    note('Apply or Cancel this preview before closing face tools.');return false;
   }
   clearTimeout(amountTimer);op=null;restoreNative();
   settings.hidden=true;ops.hidden=true;
   panel.dataset.se451FaceOpen='false';panel.dataset.se451Stage='closed';
   se430BeginnerQueue();return true;
  }
  function select(operation){
   if(!['inset','extrude','solidify','subdivide'].includes(operation))return false;
   if(preview()&&op!==operation){note('Apply or Cancel before changing tools.');return false;}
   open();op=operation;holder.append(workshop);
   settings.hidden=false;panel.dataset.se451Stage='settings';
   se430BeginnerSetOperation(operation);
   const quick=panel.querySelector('#se445ShapeQuick');
   if(quick&&typeof se448ShapeQuickActivate==='function'){
    se448ShapeQuickActivate(quick,operation);
   }else{
    const s=state();
    if(s?.selection?.partId&&s.selection.mode!=='face')api()?.setComponentMode?.('face');
    note('Choose a flat face to preview '+operation+'.');
   }
   se430BeginnerQueue();sync();return true;
  }
  function allTools(){
   if(!close())return;
   window.SWYRL_E_UNIFIED_TOOLS?.select?.('Topology','Manual mesh modeling');
   const button=panel.querySelector('.se251-external-collapse');
   if(panel.dataset.se251RightCollapsed==='true')button?.click();
  }
  ops.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b)return;
   if(b.hasAttribute('data-se451-close'))close();
   else if(b.hasAttribute('data-se451-more'))allTools();
   else if(b.dataset.se451Op)select(b.dataset.se451Op);
  });
  settings.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b)return;
   if(b.hasAttribute('data-se451-close'))close();
   else if(b.hasAttribute('data-se451-back')){
    if(preview())note('Apply or Cancel the preview first.');
    else{settings.hidden=true;restoreNative();panel.dataset.se451Stage='operations';}
   }
  });
  range.addEventListener('input',()=>{
   const amount=workshop.querySelector('#modelAtelierWorkshopAmount');
   if(!amount||!op)return;
   amount.value=range.value;
   // Native amount-change listener safely discards the old preview.
   amount.dispatchEvent(new Event('change',{bubbles:true}));
   clearTimeout(amountTimer);
   amountTimer=setTimeout(()=>{
    const s=state(),value=Number(amount.value);
    if(!s?.selection?.faceIds?.length||s.preview?.active||!Number.isFinite(value))return;
    const outcome=api()?.preview?.(op,{amount:value});
    if(outcome?.ok===false)note(outcome.reason||'Preview unavailable.');
    se430BeginnerQueue();sync();
   },110);
  });
  // The primary tools are the EXISTING far-right rail, not a duplicate.
  rail.addEventListener('click',e=>{
   const b=e.target.closest('button');if(!b)return;
   const name=(b.dataset.se320Category||b.textContent||'').trim().toLowerCase();
   if(['face','face tools','topology'].includes(name))queueMicrotask(open);
   else if(panel.dataset.se451FaceOpen==='true')queueMicrotask(close);
  });
  // Legacy Shape shortcuts keep their native preview and now reveal settings.
  panel.addEventListener('click',e=>{
   const b=e.target.closest('#se445ShapeQuick [data-se445-op]');if(!b)return;
   queueMicrotask(()=>{
    if(b.dataset.se445Op==='more')allTools();
    else if(['inset','extrude','solidify'].includes(b.dataset.se445Op)){
     open();op=b.dataset.se445Op;holder.append(workshop);
     settings.hidden=false;panel.dataset.se451Stage='settings';sync();
    }
   });
  });
  panel.addEventListener('keydown',e=>{
   if(e.key!=='Escape'||!e.target.closest('#se451FaceOperations,#se451FaceSettings'))return;
   e.preventDefault();
   if(!preview()&&!settings.hidden){settings.hidden=true;restoreNative();panel.dataset.se451Stage='operations';}
   else close();
  });
  window.addEventListener('swrlz:model-workshop-change',()=>queueMicrotask(sync));
  installed=Object.freeze({open,select,close,inspect:()=>({
   active:panel.dataset.se451FaceOpen==='true',stage:panel.dataset.se451Stage,
   operation:op,preview:preview(),nativeOwner:workshop.parentNode===holder?'settings':'inspector'
  })});
 }
 se430BeginnerInstall=function(panel){
  const result=oldInstall(panel);mount(panel);return result;
 };
 window.SWYRL_ENGINE_FACE_PROGRESSIVE_451=Object.freeze({
  version:'v11.451',layout:'rail > face tools > native settings',
  inspect:()=>installed?.inspect()||{active:false},
  open:()=>installed?.open(),choose:id=>installed?.select(id),close:()=>installed?.close()
 });
})();
/* SE451_FACE_PROGRESSIVE_DOCK_END */