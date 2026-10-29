// §E v11.120: predictable tool locations without native model changes.
function seAtelierQuickstripSafeTop(stage){
 const toolbar=stage?.closest?.('.atelier-scene')?.querySelector?.('#modelAtelierViewportModes');
 if(!toolbar||!stage?.getBoundingClientRect)return 50;
 const distance=toolbar.getBoundingClientRect().bottom-stage.getBoundingClientRect().top;
 return Number.isFinite(distance)?Math.max(50,Math.ceil(distance+8)):50;
}
function seAtelierBottomRailCenter(panel){
 const rail=panel?.querySelector?.('#modelAtelierToolRail');
 if(!rail||rail.dataset.centerInstalled==='1')return;
 rail.dataset.centerInstalled='1';
 const center=button=>{
  if(!button||!rail.contains(button)||typeof rail.scrollBy!=='function')return;
  const outer=rail.getBoundingClientRect(),inner=button.getBoundingClientRect();
  const delta=inner.left+inner.width/2-outer.left-outer.width/2;
  if(Number.isFinite(delta)&&Math.abs(delta)>3)
   rail.scrollBy({left:delta,behavior:window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches?'instant':'smooth'});
 };
 rail.addEventListener('click',event=>{
  const b=event.target?.closest?.('button');
  if(b&&rail.contains(b))requestAnimationFrame(()=>center(b));
 });
 requestAnimationFrame(()=>{
  const all=[...rail.querySelectorAll('button')];
  center(all.find(b=>b.getAttribute('aria-pressed')==='true')
   ||all.find(b=>b.textContent.trim()==='Meshes'));
 });
}
function seAtelierTopMenuExclusivity(panel){
 const a=panel?.querySelector?.('#seAtelierExportMenu'),b=panel?.querySelector?.('#seAtelierViewMenu');
 if(!a||!b||a.dataset.exclusiveMenu==='1')return;
 a.dataset.exclusiveMenu='1';
 a.addEventListener('toggle',()=>{if(a.open)b.open=false;});
 b.addEventListener('toggle',()=>{if(b.open)a.open=false;});
}
