/* SE451_GUIDED_FACE_WORKFLOW_START */
// Presentation-only guide for the existing native topology workshop.
// The real selection, source, preview, Undo and persistence stay with se430.
(function(){
 'use strict';
 let queued=false, pendingAmount=null;
 const panel=()=>se430BeginnerState.panel;
 const api=()=>se430BeginnerAPI();
 const operation=()=>panel()?.querySelector('#modelAtelierWorkshopOperation')?.value||'inset';
 const numberInput=()=>panel()?.querySelector('#modelAtelierWorkshopAmount');
 const guide=()=>panel()?.querySelector('#se451FaceWorkflow');
 const currentContext=()=>window.SWYRL_E_CONTEXT?.current?.()||{};
 const readAmount=()=>{
  const input=numberInput(),cfg=se430BeginnerAmount(operation());
  if(!input||!cfg)return null;
  const n=Number(input.value);
  return Number.isFinite(n)?Math.min(cfg.max,Math.max(cfg.min,n)):cfg.value;
 };
 const format=n=>Number(n.toFixed(3)).toString();
 function updateAmount(raw){
  const cfg=se430BeginnerAmount(operation()),input=numberInput();
  if(!cfg||!input||raw===''||!Number.isFinite(Number(raw)))return;
  const value=Math.min(cfg.max,Math.max(cfg.min,Number(raw)));
  input.value=format(value);
  pendingAmount=value;
  if(!queued){
   queued=true;
   requestAnimationFrame(()=>{
    queued=false;
    const n=pendingAmount;pendingAmount=null;
    const state=api()?.inspect?.(),op=operation();
    if(state?.preview.active&&state.preview.operation===op){
     // Rebuild the disposable preview in place. Never Apply from a slider.
     se430BeginnerResult(api().preview(op,{amount:n}));
    }else if(state?.selection?.faceIds?.length&&state.operations?.[op]?.available){
     se430BeginnerResult(api().preview(op,{amount:n}));
    }
    se451GuidedRefresh();
   });
  }
  se451GuidedRefresh();
 }
 function se451GuidedInstall(p){
  if(!p?.dataset?.se430Beginner||p.querySelector('#se451FaceWorkflow'))return;
  const quick=p.querySelector('#se445ShapeQuick');
  if(!quick)return;
  const section=document.createElement('section');
  section.id='se451FaceWorkflow';section.setAttribute('aria-label','Face modeling modifiers');
  section.innerHTML='<div class="se451-heading"><strong id="se451ToolName">Inset</strong><button type="button" id="se451Advanced" aria-expanded="false">Advanced tools</button></div>'+
   '<p id="se451Step" role="status" aria-live="polite">Select a face, then choose Inset or Extrude.</p>'+
   '<div id="se451AmountControls"><label for="se451AmountRange" id="se451AmountLabel">Inset amount</label>'+
   '<div class="se451-amount-row"><input id="se451AmountRange" type="range" aria-label="Live face modifier amount">'+
   '<input id="se451AmountNumber" type="number" inputmode="decimal" aria-label="Exact face modifier amount"></div></div>'+
   '<div class="se451-commit"><button type="button" id="se451Apply">Apply</button>'+
   '<button type="button" id="se451Cancel">Cancel</button></div>';
  quick.after(section);
  section.querySelector('#se451Advanced').addEventListener('click',()=>{
   const expanded=p.dataset.se451Advanced!=='true';
   p.dataset.se451Advanced=String(expanded);
   se451GuidedRefresh();
  });
  section.querySelector('#se451AmountRange').addEventListener('input',e=>updateAmount(e.target.value));
  const numeric=section.querySelector('#se451AmountNumber');
  numeric.addEventListener('input',e=>updateAmount(e.target.value));
  section.querySelector('#se451Apply').addEventListener('click',()=>{
   se430BeginnerResult(api()?.apply());se451GuidedRefresh();
  });
  section.querySelector('#se451Cancel').addEventListener('click',()=>{
   se430BeginnerResult(api()?.cancel());se451GuidedRefresh();
  });
  p.dataset.se451Advanced='false';
  se451GuidedRefresh();
 }
 function se451GuidedRefresh(){
  const p=panel(),section=guide();if(!p||!section)return;
  const context=currentContext();
  const onFaceTools=context.group==='Topology'&&/manual mesh modeling/i.test(context.operation||'');
  p.dataset.se451Guided=String(onFaceTools);
  section.hidden=!onFaceTools;
  if(!onFaceTools)return;
  const state=api()?.inspect?.();if(!state)return;
  const op=operation(),cfg=se430BeginnerAmount(op),preview=state.preview||{};
  const name=se430BeginnerTeaching()?.get(op)?.name||op;
  const step=section.querySelector('#se451Step');
  const summary=state.selection||{},allowed=state.operations?.[op];
  section.querySelector('#se451ToolName').textContent=name+' · Face tools';
  section.querySelector('#se451AmountControls').hidden=!cfg;
  if(cfg){
   const input=numberInput(),range=section.querySelector('#se451AmountRange'),numeric=section.querySelector('#se451AmountNumber');
   const amount=readAmount();
   for(const control of [range,numeric]){
    control.min=cfg.min;control.max=cfg.max;control.step=cfg.step;
    if(document.activeElement!==control&&Number(control.value)!==amount)control.value=format(amount);
    control.disabled=!!preview.active&&preview.operation!==op;
   }
   section.querySelector('#se451AmountLabel').textContent=cfg.label;
  }
  if(preview.active){
   const stats=preview.stats||{};
   step.textContent='Live preview · '+(stats.facesBefore??'?')+' → '+(stats.facesAfter??'?')+' triangles. Adjust amount, then Apply or Cancel.';
  }else if(!summary.partId){
   step.textContent='Select a mesh, choose a face tool, then tap a square face.';
  }else if(summary.objectCount>1){
   step.textContent='Select one mesh to edit its faces.';
  }else if(summary.mode!=='face'||!summary.faceIds?.length){
   step.textContent='Tool ready. Tap a square face; its connected triangles form one region.';
  }else if(!allowed?.available){
   step.textContent=allowed?.reason||'Choose a connected planar face to continue.';
  }else{
   step.textContent='Face selected. Tap '+name+' to preview; adjust amount before applying.';
  }
  section.querySelector('#se451Apply').disabled=!preview.active;
  section.querySelector('#se451Cancel').disabled=!preview.active;
  const toggle=section.querySelector('#se451Advanced'),expanded=p.dataset.se451Advanced==='true';
  toggle.textContent=expanded?'Hide advanced':'Advanced tools';
  toggle.setAttribute('aria-expanded',String(expanded));
 }
 window.se451GuidedShowAdvanced=()=>{
  const p=panel();if(!p)return;
  p.dataset.se451Advanced='true';se451GuidedRefresh();
 };
 const oldInstall=se430BeginnerInstall;
 se430BeginnerInstall=function(p){const result=oldInstall(p);se451GuidedInstall(p);return result;};
 const oldRefresh=se430BeginnerRefresh;
 se430BeginnerRefresh=function(...args){const result=oldRefresh.apply(this,args);se451GuidedRefresh();return result;};
 window.SWYRL_ENGINE_GUIDED_FACE_451=Object.freeze({version:'v11.451',refresh:se451GuidedRefresh});
})();
/* SE451_GUIDED_FACE_WORKFLOW_END */
