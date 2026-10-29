// §E v11.168 — Quest Browser 2D panel comfort, without inventing an XR session.
// This module affects only editor presentation. Native pointer, camera, game,
// physics, and model edit handlers remain authoritative and unchanged.
(function se168QuestPanel(){
  if (window.SWYRL_ENGINE_DEVICE) return;
  const key='se.engine.questPanel.v1';
  const ua=String(navigator.userAgent||'');
  const questHint=/\bQuest(?:\s*(?:2|3|3S|Pro))?\b/i.test(ua) && /(?:OculusBrowser|VR)/i.test(ua);
  const xrApi=!!(navigator.xr && typeof navigator.xr.isSessionSupported==='function');
  let preference='auto',lastPointer='unknown',vrSupported=null;
  try {const saved=localStorage.getItem(key);if(['auto','on','off'].includes(saved))preference=saved;}catch(_e){}
  const isSmallTouch=()=>Boolean(window.matchMedia?.('(pointer: coarse)').matches) &&
    (window.innerWidth<=900 || window.innerHeight<=550);
  const profile=()=>questHint?'quest-browser':isSmallTouch()?'phone-tablet':'desktop';
  const enabled=()=>preference==='on'||(preference==='auto'&&questHint);
  let switchButton=null;
  function apply(){
    const active=enabled();
    document.documentElement.classList.toggle('se-quest-panel',active);
    document.documentElement.dataset.seDeviceProfile=profile();
    if(switchButton){
      switchButton.setAttribute('aria-pressed',String(active));
      switchButton.textContent=active?'🥽 Quest UI on':'🥽 Quest UI off';
      switchButton.title=(active?'Use standard-sized editor controls':'Use larger headset-friendly editor controls')+' · '+profile();
    }
  }
  function setComfortMode(mode){
    if(!['auto','on','off'].includes(mode))return false;
    preference=mode;
    try{localStorage.setItem(key,mode);}catch(_e){}
    apply();return true;
  }
  function mount(){
    const bar=document.querySelector('.topbar');
    if(!bar||document.getElementById('seQuestModeSwitch'))return;
    switchButton=document.createElement('button');
    switchButton.id='seQuestModeSwitch';
    switchButton.type='button';
    switchButton.className='se-quest-mode-toggle';
    switchButton.setAttribute('aria-label','Toggle Quest-friendly editor controls');
    switchButton.addEventListener('click',()=>setComfortMode(enabled()?'off':'on'));
    bar.appendChild(switchButton);
    apply();
  }
  const api={
    read:()=>({profile:profile(),questBrowserHint:questHint,questPanelActive:enabled(),
      preference,xrApi,immersiveVRSupported:vrSupported,lastPointerType:lastPointer,
      viewport:{width:innerWidth,height:innerHeight}}),
    setComfortMode
  };
  window.SWYRL_ENGINE_DEVICE=api;
  document.addEventListener('pointerdown',event=>{
    if(typeof event.pointerType==='string'&&event.pointerType)lastPointer=event.pointerType;
  },{passive:true,capture:true});
  window.addEventListener('resize',apply,{passive:true});
  apply();
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});
  else mount();
  // A missed dynamic toolbar load is retried once on window load, no poll loop.
  window.addEventListener('load',mount,{once:true});
  // WebXR capability is reported, NEVER auto-requested. A 2D panel is not VR.
  if(xrApi){
    Promise.resolve().then(()=>navigator.xr.isSessionSupported('immersive-vr'))
      .then(supported=>{vrSupported=Boolean(supported);})
      .catch(()=>{vrSupported=false;});
  }
})();