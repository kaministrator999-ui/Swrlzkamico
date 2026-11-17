/* §E v11.494 — visible model update stages, in-memory verified reopen.
 * All code executes inside the existing authenticated §E account host closure.
 * The verified transfer cache lasts only until the immediate native loader call.
 * It never stores credentials, creates a project or retries cloud writes. */
const se494TrustedLoadCache=new Map();
function se494UpdateSteps(card,status,button){
 const names=['Read model file','Read saved project','Validate model','Prepare revision','Save to account','Open updated project'];
 let step=-1,start=performance.now(),timer=null,closed=false;
 const panel=document.createElement('div');
 panel.className='se494-model-progress';
 panel.setAttribute('role','status');
 panel.setAttribute('aria-live','polite');
 const title=document.createElement('strong');
 title.textContent='Updating '+String(card.querySelector('.se184-card-info strong')?.textContent||'saved model');
 const sub=document.createElement('div');sub.className='se494-current-step';
 const meter=document.createElement('div');meter.className='se494-indeterminate';
 const moving=document.createElement('span');meter.append(moving);
 const list=document.createElement('ol');
 const labels=names.map(text=>{
  const item=document.createElement('li');item.textContent=text;list.append(item);return item;
 });
 const caption=document.createElement('small');caption.textContent='Actual stages · transfer time depends on account connection';
 panel.append(title,sub,meter,list,caption);
 card.append(panel);
 card.classList.add('se494-busy');
 function message(value){
  const elapsed=((performance.now()-start)/1000).toFixed(1);
  sub.textContent=value+' · '+elapsed+' s';
  status.textContent=value;
 }
 function stage(n,detail=''){
  step=Math.max(step,n);
  labels.forEach((el,i)=>{
   el.classList.toggle('se494-active',i===step);
   el.classList.toggle('se494-complete',i<step);
  });
  message(names[Math.max(0,Math.min(step,names.length-1))]+(detail?' · '+detail:''));
 }
 function note(value){message(value)}
 function done(value,ok=true){
  if(closed)return;
  clearInterval(timer);timer=null;
  panel.classList.toggle('se494-failed',!ok);
  meter.classList.toggle('se494-meter-done',ok);
  if(ok)labels.forEach(el=>{el.classList.remove('se494-active');el.classList.add('se494-complete')});
  message(value);
  card.classList.remove('se494-busy');
  // Keep meaningful completion visible even when the project hub closes.
  if(ok)setTimeout(()=>{if(panel.isConnected)panel.remove()},2800);
  else {
   const close=document.createElement('button');
   close.type='button';close.textContent='Dismiss';close.onclick=()=>{panel.remove();closed=true};
   panel.append(close);
  }
 }
 timer=setInterval(()=>{
  if(step>=0&&!closed){
   const current=sub.textContent.split(' · ')[0];
   if(current)sub.textContent=current+' · '+((performance.now()-start)/1000).toFixed(1)+' s';
  }
 },350);
 return Object.freeze({stage,note,done});
}
function se494NextPaint(){
 return new Promise(resolve=>
  typeof requestAnimationFrame==='function'?requestAnimationFrame(()=>resolve()):setTimeout(resolve,0));
}
function se494AfterCloudSave(card,record,reply){
 if(!reply?.project||reply.project.id!==record.id)return;
 const revision=reply.project.revision;
 record.revision=revision;
 const item=card.querySelector('.se184-card-info small');
 if(item)item.textContent='Saved to account · Revision '+revision;
 if(typeof se183CloudCacheClear==='function')se183CloudCacheClear();
}
function se494AfterLocalSave(card){
 if(typeof se184SyncDefaultBoxes==='function')se184SyncDefaultBoxes();
}
// A project was confirmed durable by §C. Reuse the exact bytes for one normal
// native load instead of downloading an identical copy from the same account.
// Canonical loadCloud still validates the object, restores a prior scene on error,
// handles dirty scene prompts, preserves cloudRefs and the v11.371 link workflow.
async function se494OpenConfirmedCloud(id,project,snapshot,onProgress){
 const bytes=snapshot instanceof Uint8Array?snapshot.buffer:snapshot;
 if(!(bytes instanceof ArrayBuffer)||project?.id!==id||!Number.isInteger(project.revision))
  throw Error('Confirmed account project cannot be opened safely');
 if(se494TrustedLoadCache.size)se494TrustedLoadCache.clear();
 se494TrustedLoadCache.set(id,{project,bytes});
 try{
  onProgress('Opening verified revision '+project.revision+' without downloading it again…');
  await se494NextPaint();
  const opened=await loadCloud(id);
  if(opened!==true)
   throw Error('Update saved, but editor open was cancelled or failed. '+(
    window.SWYRL_ENGINE_PROJECT_LOAD_493?.getError?.()||'Use Open project to retry.'));
  document.getElementById('projectHub')?.classList.remove('show');
  return true;
 }finally{
  se494TrustedLoadCache.delete(id);
 }
}
async function se494OpenConfirmedLocal(id,scene,onProgress){
 if(dirty&&!window.confirm('Update was saved. Open the updated model and replace unsaved active scene edits?'))
  return false;
 onProgress('Opening updated model on this device…');
 await se494NextPaint();
 const backup=window.SWYRL_ENGINE_AGENT.inspectScene();
 try{
  window.SWYRL_ENGINE_AGENT.loadScene(structuredClone(scene));
  ModelAtelier.syncProject();
  if(currentProject?.kind==='model-atelier')ModelAtelier.open();
  else ModelAtelier.close();
  if(typeof markSaved==='function')markSaved();
  if(typeof se175UpdateLabel==='function')se175UpdateLabel();
  document.getElementById('projectHub')?.classList.remove('show');
  return true;
 }catch(error){
  try{window.SWYRL_ENGINE_AGENT.loadScene(backup);ModelAtelier.syncProject()}catch{}
  throw Error('Update saved locally, but editor open failed: '+String(error.message||error));
 }
}
