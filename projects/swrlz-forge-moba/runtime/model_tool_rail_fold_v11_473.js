/* SE473_MODEL_TOOL_RAIL_FOLD_START */
// Compact, persistent tool-category rail. Never duplicate tool handlers or
// hide viewport transforms; only the vertical category buttons are folded.
(function se473ModelToolRailFold(){
 'use strict';
 const key='swyrl.engine.modeler.tool-rail-fold.v1';
 let collapsed=false,scheduled=false;
 try{collapsed=localStorage.getItem(key)==='collapsed';}catch{}
 function install(){
  const panel=document.getElementById('modelAtelierPanel');
  const rail=panel?.querySelector('#modelAtelierToolRail');
  if(!rail)return;
  let toggle=rail.querySelector('#se473RailFold');
  if(!toggle){
   toggle=document.createElement('button');
   toggle.id='se473RailFold';
   toggle.type='button';
   toggle.className='se473-rail-fold';
   toggle.setAttribute('aria-controls','modelAtelierToolRail');
   rail.prepend(toggle);
   toggle.addEventListener('click',()=>{
    collapsed=!collapsed;
    try{localStorage.setItem(key,collapsed?'collapsed':'expanded');}catch{}
    reflect();
    window.dispatchEvent(new Event('resize'));
   });
  }
  function reflect(){
   panel.dataset.se473RailCollapsed=String(collapsed);
   toggle.textContent=collapsed?'▾':'▴ Tools';
   toggle.title=collapsed?'Expand vertical tool rail':'Collapse vertical tool rail upward';
   toggle.setAttribute('aria-label',toggle.title);
   toggle.setAttribute('aria-expanded',String(!collapsed));
  }
  reflect();
 }
 function schedule(){
  if(scheduled)return;
  scheduled=true;
  queueMicrotask(()=>{scheduled=false;install();});
 }
 if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',()=>{install();observe();},{once:true});
 else{install();observe();}
 function observe(){
  new MutationObserver(records=>{
   if(records.some(record=>[...record.addedNodes].some(node=>node.nodeType===1)))
    schedule();
  }).observe(document.body,{subtree:true,childList:true});
 }
 window.SWYRL_ENGINE_TOOL_RAIL_473=Object.freeze({
  version:'v11.473',
  state:()=>({collapsed}),
  toggle:()=>{
   const toggle=document.getElementById('se473RailFold');
   toggle?.click();return collapsed;
  }
 });
})();
/* SE473_MODEL_TOOL_RAIL_FOLD_END */
