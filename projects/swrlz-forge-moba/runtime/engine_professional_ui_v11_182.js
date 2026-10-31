// §E v11.182: live geometry audit of editor chrome; read-only diagnostics.
// No overlay is inserted. No buttons are moved, simulated, or obscured.
(function se182LayoutAuditInstall(){
 if(window.SWYRL_ENGINE_LAYOUT)return;
 const names={
  toolbar:'.app > .topbar',viewport:'.app > .workspace > .viewport-wrap',
  leftDock:'.app > .workspace > .panel.left',
  rightDock:'.app > .workspace > .panel.right',
  levelBar:'#st141LevelBar',mobileTabs:'.viewport-wrap > .mobile-tabs',
  mobileDrawer:'#mobileDrawer',projects:'#projectHub',
  projectWindow:'#projectHub .project-window',chat:'#seChatAccountPanel',
  chatToggle:'#seChatToggle',modelAtelier:'#modelAtelierPanel',
  vrStudio:'.se179-dialog',runtimeMenu:'#st141RuntimeMenu'
 };
 function geometry(name){
  const el=document.querySelector(names[name]);if(!el)return null;
  const c=getComputedStyle(el),r=el.getBoundingClientRect();
  const visible=!el.hidden&&c.display!=='none'&&c.visibility!=='hidden'&&
    r.width>0&&r.height>0&&c.opacity!=='0'&&
    (!name.includes('projects')||el.classList.contains('show'));
  return {id:el.id||name,visible,
   x:Number(r.left.toFixed(1)),y:Number(r.top.toFixed(1)),
   width:Number(r.width.toFixed(1)),height:Number(r.height.toFixed(1)),
   right:Number(r.right.toFixed(1)),bottom:Number(r.bottom.toFixed(1)),
   position:c.position,zIndex:c.zIndex,
   scrollable:el.scrollWidth>el.clientWidth+2||el.scrollHeight>el.clientHeight+2,
   overflowX:c.overflowX,overflowY:c.overflowY};
 }
 function intersection(a,b){
  if(!a?.visible||!b?.visible)return 0;
  return Math.max(0,Math.min(a.right,b.right)-Math.max(a.x,b.x))*
    Math.max(0,Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y));
 }
 function audit(){
  const rects={};
  for(const name of Object.keys(names))rects[name]=geometry(name);
  const viewport={width:innerWidth,height:innerHeight};
  const issues=[];
  const leave=(name,rect)=>{
   if(rect?.visible&&(rect.x<-3||rect.y<-3||rect.right>viewport.width+3||rect.bottom>viewport.height+3))
    issues.push({kind:'offscreen',name,rect});
  };
  // Scrollable toolbar overflow is intentional; content overlaid on native
  // viewport controls is not. Side docks and canvas form one grid.
  if(rects.toolbar?.visible)leave('toolbar',rects.toolbar);
  for(const name of ['projectWindow','vrStudio']){
   if(rects[name]?.visible)leave(name,rects[name]);
  }
  if(rects.levelBar?.visible&&rects.mobileTabs?.visible&&intersection(rects.levelBar,rects.mobileTabs)>9)
   issues.push({kind:'collision',pair:['levelBar','mobileTabs']});
  if(rects.toolbar?.visible&&rects.viewport?.visible&&intersection(rects.toolbar,rects.viewport)>9)
   issues.push({kind:'collision',pair:['toolbar','viewport']});
  if(rects.leftDock?.visible&&rects.viewport?.visible&&intersection(rects.leftDock,rects.viewport)>9&&innerWidth>720)
   issues.push({kind:'collision',pair:['leftDock','viewport']});
  if(rects.rightDock?.visible&&rects.viewport?.visible&&intersection(rects.rightDock,rects.viewport)>9&&innerWidth>720)
   issues.push({kind:'collision',pair:['rightDock','viewport']});
  return {version:'v11.182',viewport,rects,issues,ok:!issues.length,
   expectedOverlays:['projects','chat','vrStudio','runtimeMenu'],
   note:'Measured 2D editor chrome only; not a physical Quest headset acceptance test'};
 }
 window.SWYRL_ENGINE_LAYOUT=Object.freeze({audit});
})();
