/* SE465_NARROW_INSPECTOR_START */
// Correct the mobile "one letter per line" collapse without altering the
// existing dock widths, draggable handles, tool events, or model viewport.
const se465InspectorNarrowLimit=236;
function se465InspectorInstall(host){
 if(!host)return;
 const inspector=host.querySelector('.atelier-inspector');
 const handle=inspector?.querySelector('.atelier-tool-handle');
 if(!inspector||!handle||host._se465InspectorObserved===inspector)return;
 host._se465InspectorObserver?.disconnect?.();
 if(host._se465InspectorWindowResize){
  window.removeEventListener('resize',host._se465InspectorWindowResize);
 }
 const note=document.createElement('div');
 note.id='se465InspectorNarrowHint';
 note.className='se465-inspector-narrow-hint';
 note.setAttribute('role','note');
 const heading=document.createElement('strong');
 heading.textContent='Tools are compact';
 const message=document.createElement('p');
 message.textContent='Tap Expand above, or drag this panel wider, to edit tool settings.';
 note.append(heading,message);
 handle.after(note);
 const update=()=>{
  if(host.hidden||!inspector.isConnected)return;
  const width=inspector.getBoundingClientRect?.().width||inspector.clientWidth||0;
  if(width>0){
   host.dataset.se465InspectorNarrow=String(width<se465InspectorNarrowLimit);
  }
 };
 host._se465InspectorObserved=inspector;
 host._se465InspectorWindowResize=update;
 window.addEventListener('resize',update);
 if(typeof ResizeObserver==='function'){
  const observer=new ResizeObserver(update);
  observer.observe(inspector);
  host._se465InspectorObserver=observer;
 }
 requestAnimationFrame(update);
}
const se465PreviousBeginnerInstall=se430BeginnerInstall;
se430BeginnerInstall=function(host){
 const result=se465PreviousBeginnerInstall.apply(this,arguments);
 se465InspectorInstall(host);
 return result;
};
window.SWYRL_ENGINE_INSPECTOR_READABILITY_465=Object.freeze({
 version:'v11.465',thresholdPx:se465InspectorNarrowLimit,
 inspect:()=>({
  compact:panel?.dataset?.se465InspectorNarrow==='true',
  expanded:panel?.dataset?.se464InspectorFocus==='true'
 })
});
 /* SE465_NARROW_INSPECTOR_END */