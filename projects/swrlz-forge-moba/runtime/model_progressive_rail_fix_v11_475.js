/* SE475_PROGRESSIVE_RAIL_VISIBILITY_START */
/* Repair-only adapter for v11.474: keep native tool/context ownership intact.
 * The v11.320 rail is a scrolling grid column. A flyout placed inside it is
 * clipped by overflow-x:hidden!important; relocate the same DOM node so its
 * original handlers and model state survive. */
(function se475ProgressiveRailVisibility(){
 'use strict';
 let mounted=null,queued=false;
 const categories=new Set(['Meshes','Sculpt','Lasso','Topology','Face','Appearance','Motion','References']);
 const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
 const number=n=>Math.round(n)+'px';
 function rect(node){return node?.getBoundingClientRect?.()||null;}
 function sync(){
  const a=mounted;if(!a||!a.panel.isConnected)return;
  const progress=window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
  if(!progress)return;
  const {panel,rail,body,flyout,top}=a;
  const buttons=[...rail.querySelectorAll(':scope > button')];
  let selected=null;
  for(const button of buttons){
   const name=(button.textContent||'').trim();
   if(!categories.has(name))continue;
   const active=name===progress.family;
   if(active)selected=button;
   const want=active?'true':'false';
   if(button.getAttribute('aria-pressed')!==want)button.setAttribute('aria-pressed',want);
   const role=active?'selected':'idle';
   if(button.dataset.se475FamilyState!==role)button.dataset.se475FamilyState=role;
  }
  panel.dataset.se475Family=progress.family||'none';
  panel.dataset.se475Mounted='true';
  const area=rect(body),column=rect(rail),anchor=rect(selected),menu=rect(flyout);
  if(area&&column&&area.width>0&&area.height>0){
   const compact=panel.dataset.se251Layout==='compact'||column.width>column.height*2;
   const width=clamp(Math.min(212,area.width-12),120,238);
   let x,y;
   flyout.style.setProperty('--se475-flyout-width',number(width));
   const menuHeight=clamp(menu?.height||Math.min(350,area.height-12),42,Math.max(42,area.height-10));
   if(compact){
    x=clamp((anchor?.left??column.left)-area.left,5,Math.max(5,area.width-width-5));
    y=clamp(column.top-area.top-menuHeight-5,5,Math.max(5,area.height-menuHeight-5));
   }else{
    x=clamp(column.left-area.left-width-6,5,Math.max(5,area.width-width-5));
    y=clamp((anchor?.top??column.top)-area.top-4,5,Math.max(5,area.height-menuHeight-5));
   }
   flyout.style.setProperty('--se475-flyout-x',number(x));
   flyout.style.setProperty('--se475-flyout-y',number(y));
   flyout.dataset.se475Placement=compact?'compact':'vertical';
  }
  const scene=rect(panel.querySelector('.atelier-scene'));
  const trans=panel.querySelector('#se320ModelTransform');
  const toolbar=rect(trans);
  if(area&&scene&&scene.width>0&&scene.height>0){
   const x=clamp(scene.left-area.left+6,4,area.width-20);
   const width=Math.max(120,Math.min(scene.width-12,area.width-x-5));
   let y=scene.top-area.top+6;
   if(toolbar&&!trans.hidden&&toolbar.height>0&&toolbar.bottom>=scene.top&&toolbar.top<scene.bottom){
    y=Math.max(y,toolbar.bottom-area.top+7);
   }
   y=clamp(y,4,Math.max(4,area.height-53));
   top.style.setProperty('--se475-modes-x',number(x));
   top.style.setProperty('--se475-modes-y',number(y));
   top.style.setProperty('--se475-modes-width',number(width));
  }
 }
 function schedule(){
  if(queued)return;
  queued=true;
  queueMicrotask(()=>{queued=false;install();sync();});
 }
 function install(){
  const panel=document.getElementById('modelAtelierPanel');
  const body=panel?.querySelector('.atelier-body');
  const rail=panel?.querySelector('#modelAtelierToolRail');
  const flyout=panel?.querySelector('#se474ToolFlyout');
  const top=panel?.querySelector('#se474SpecificModes');
  if(!body||!rail||!flyout||!top||!window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.())return;
  if(mounted?.panel===panel&&mounted.flyout===flyout&&mounted.body===body)return;
  // Same node: inherited native events, selected mode and focus are retained.
  if(flyout.parentElement!==body)body.append(flyout);
  mounted={panel,body,rail,flyout,top};
  new MutationObserver(schedule).observe(panel,{
   attributes:true,attributeFilter:['data-se474-family','data-se474-settings-open',
    'data-se474-specific-type','data-se251-layout','hidden']
  });
  new MutationObserver(schedule).observe(flyout,{
   attributes:true,attributeFilter:['hidden'],
   childList:true
  });
  new MutationObserver(schedule).observe(top,{
   attributes:true,attributeFilter:['hidden'],
   childList:true
  });
  // Native context or older layout logic may update the underlying pressed state.
  new MutationObserver(schedule).observe(rail,{
   subtree:false,childList:true
  });
  for(const button of rail.querySelectorAll(':scope > button')){
   if(!categories.has(button.textContent.trim()))continue;
   new MutationObserver(schedule).observe(button,{
    attributes:true,attributeFilter:['aria-pressed']
   });
  }
  rail.addEventListener('scroll',schedule,{passive:true});
  window.addEventListener('resize',schedule,{passive:true});
  window.addEventListener('orientationchange',schedule,{passive:true});
  window.addEventListener('swrlz:model-workshop-change',schedule);
  sync();
 }
 function observe(){
  const root=document.body;
  if(!root)return;
  new MutationObserver(records=>{
   if(mounted?.panel?.isConnected&&mounted?.flyout?.isConnected)return;
   if(records.some(record=>record.addedNodes.length))schedule();
  }).observe(root,{subtree:true,childList:true});
 }
 if(document.readyState==='loading'){
  document.addEventListener('DOMContentLoaded',()=>{schedule();observe();},{once:true});
 }else{schedule();observe();}
 window.SWYRL_ENGINE_PROGRESSIVE_RAIL_475=Object.freeze({
  version:'v11.475',
  inspect:()=>({
   mounted:!!mounted?.panel?.isConnected,
   flyoutInBody:!!mounted&&mounted.flyout.parentElement===mounted.body,
   family:window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.()?.family||'',
   flyoutVisible:!!mounted&&!mounted.flyout.hidden,
   modesVisible:!!mounted&&!mounted.top.hidden,
   activeRailButtons:mounted?[...mounted.rail.querySelectorAll(':scope > button[aria-pressed="true"]')]
    .filter(b=>categories.has(b.textContent.trim())).map(b=>b.textContent.trim()):[]
  }),
  refresh:schedule
 });
})();
/* SE475_PROGRESSIVE_RAIL_VISIBILITY_END */