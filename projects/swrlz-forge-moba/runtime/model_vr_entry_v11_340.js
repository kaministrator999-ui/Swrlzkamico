/* SE340_MODEL_VR_ENTRY_START */
(function se340ModelEntry(){
 'use strict';
 let button=null,status=null,checking=false,pending=false;
 function refresh(){
  if(!button)return;
  const api=window.SWYRL_ENGINE_MODEL_VR,state=api?.read?.()||{};
  button.disabled=!!state.busy||state.supported===false;
  button.textContent=state.active?'Exit model VR':state.busy?'Opening model VR…':'Enter model VR';
  button.setAttribute('aria-pressed',String(!!state.active));
  button.title=state.supported===false?'Immersive WebXR requires a headset browser, such as Meta Quest Browser.':'Open this native model in an immersive controller workspace';
  if(state.error){status.textContent=state.error;status.dataset.error='true';}
  else if(state.supported===false){status.textContent='Headset browser required';status.dataset.error='false';}
  else if(!state.active&&!state.busy){status.textContent='';status.dataset.error='false';}
  se181XRLabel();
 }
 function mount(){
  pending=false;
  const head=document.querySelector('#modelAtelierPanel .atelier-head');
  if(!head||!window.SWYRL_ENGINE_MODEL_VR)return;
  if(!button){
   const host=document.createElement('div');host.className='se340-model-vr-entry';
   button=document.createElement('button');button.id='se340EnterModelVR';button.type='button';
   button.setAttribute('aria-label','Enter or exit immersive Model Studio');
   button.addEventListener('click',()=>{const api=window.SWYRL_ENGINE_MODEL_VR;if(api.read().active)void api.exit();else void api.enter();});
   status=document.createElement('span');status.id='se340ModelVRStatus';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
   host.append(button,status);
   const title=head.querySelector('strong');if(title)title.after(host);else head.prepend(host);
  }
  refresh();
  if(!checking){checking=true;void window.SWYRL_ENGINE_MODEL_VR.checkSupport().finally(refresh);}
 }
 function schedule(){if(!pending){pending=true;queueMicrotask(mount);}}
 function boot(){
  mount();
  new MutationObserver(()=>{if(!button?.isConnected)schedule();}).observe(document.body,{childList:true,subtree:true});
  window.addEventListener('swrlz:model-vr-state',refresh);
  window.addEventListener('swrlz:project-loaded',schedule);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
/* SE340_MODEL_VR_ENTRY_END */
