// §E v11.247 — opt-in editor previews, not a new scene, renderer or game loop.
(function se247EditorLivePreview(){
 'use strict';
 const state={project:null,particles:false,cinematic:false,open:false,button:null,panel:null,ready:false};
 const game=()=>window.SWYRL_ENGINE_STUDIOS?.active?.()==='game' &&
  window.SWYRL_ENGINE_WORKSPACES?.active?.()!=='modeler';
 const editor=()=>!playing&&!simulating&&!stSession&&!seLevels.playingMenu&&
  !renderer?.xr?.isPresenting;
 const authoredCinematic=()=>currentProject?.canonicalId==='ghosts-different-forms-ep01' &&
  typeof storyPreview==='function'&&typeof storyExitPreview==='function';
 const hasParticles=()=>!!se223Data()?.emitters?.length;
 function stopParticles(){
  if(!state.particles)return;
  state.particles=false;se223State.preview=false;se223State.playingLast=false;
  for(const record of se223State.live.values()){
   record.particles.length=0;record.geometry.setDrawRange(0,0);
   record.cloud.visible=false;
  }
 }
 function stopCinematic(){
  if(!state.cinematic)return;
  state.cinematic=false;
  if(typeof storyExitPreview==='function')storyExitPreview();
 }
 function leave(){
  stopCinematic();stopParticles();state.open=false;
  if(state.panel)state.panel.hidden=true;
  if(state.button){state.button.setAttribute('aria-expanded','false');state.button.classList.remove('active');}
 }
 function toggleParticles(value){
  if(!editor()||!game()||(value&&!hasParticles()))return false;
  if(value){state.particles=true;se223State.preview=true;se223State.playingLast=false;}
  else stopParticles();
  if(se223State.panel&&typeof se223UIRefresh==='function')se223UIRefresh();
  paint();return true;
 }
 function toggleCinematic(value){
  if(!editor()||!game()||(value&&!authoredCinematic()))return false;
  if(value){
   // Reuse the native storyboard camera and objects; never enter Play mode.
   state.cinematic=storyPreview(0)===true;
  }else stopCinematic();
  paint();return state.cinematic===value;
 }
 function makeInput(kind,label,description){
  const row=document.createElement('label');row.className='se247-row';
  const checkbox=document.createElement('input');checkbox.type='checkbox';
  checkbox.dataset.se247Toggle=kind;
  const contents=document.createElement('span');
  const title=document.createElement('strong');title.textContent=label;
  const note=document.createElement('small');note.textContent=description;
  contents.append(title,note);row.append(checkbox,contents);return row;
 }
 function mount(){
  if(state.button?.isConnected&&state.panel?.isConnected)return;
  const bar=document.querySelector('.app>.topbar>.se187-game-tabs .segui-mini');
  const host=typeof se143ViewportHost==='function'?se143ViewportHost():null;
  if(!bar||!host)return;
  const existing=bar.querySelector('[data-se247-preview-button]');
  if(existing)existing.remove();
  const old=host.querySelector('#se247PreviewPanel');if(old)old.remove();
  const button=document.createElement('button');button.type='button';button.textContent='✦ Preview';
  button.dataset.se247PreviewButton='';button.setAttribute('aria-controls','se247PreviewPanel');
  button.setAttribute('aria-expanded','false');button.title='Edit-mode particle and cinematic previews';
  button.addEventListener('click',()=>{
   if(!editor()||!game())return;
   if(!state.open)window.SWYRL_ENGINE_GUI_STUDIO?.scene?.();
   state.open=!state.open;paint();
  });
  bar.append(button);
  const panel=document.createElement('section');panel.id='se247PreviewPanel';
  panel.className='se247-panel';panel.hidden=true;
  panel.setAttribute('aria-label','Edit-mode live previews');
  const heading=document.createElement('div');heading.className='se247-header';
  const title=document.createElement('strong');title.textContent='Live preview · Edit mode';
  const close=document.createElement('button');close.type='button';close.textContent='Close';
  close.addEventListener('click',()=>{state.open=false;paint();button.focus();});
  heading.append(title,close);
  const help=document.createElement('p');help.textContent='Run selected visuals without starting the game. These switches do not change your saved project or Play mode.';
  const particles=makeInput('particles','Particles','Run authored emitters in the scene editor.');
  const cinematic=makeInput('cinematic','Cinematic animation','Loop the authored episode timeline; restores your editor camera when off.');
  const note=document.createElement('small');note.id='se247Availability';
  panel.append(heading,help,particles,cinematic,note);
  panel.addEventListener('change',event=>{
   if(event.target?.dataset?.se247Toggle==='particles')toggleParticles(event.target.checked);
   if(event.target?.dataset?.se247Toggle==='cinematic')toggleCinematic(event.target.checked);
  });
  host.append(panel);state.button=button;state.panel=panel;
  paint();
 }
 function paint(){
  if(!state.button||!state.panel)return;
  const visible=game()&&editor();
  state.button.hidden=!visible;
  state.panel.hidden=!visible||!state.open;
  state.button.classList.toggle('active',visible&&state.open);
  state.button.setAttribute('aria-expanded',String(visible&&state.open));
  const a=state.panel.querySelector('[data-se247-toggle=particles]');
  const b=state.panel.querySelector('[data-se247-toggle=cinematic]');
  a.checked=state.particles;a.disabled=!hasParticles();
  b.checked=state.cinematic;b.disabled=!authoredCinematic();
  state.panel.querySelector('#se247Availability').textContent=
   !hasParticles()?'Add an emitter in Particle Studio to enable scene particles.':
   !authoredCinematic()?'Cinematic playback is available in the authored Storyboard episode project.':
   'Each preview is independent. Stop either at any time.';
 }
 function sync(){
  if(currentProject!==state.project){leave();state.project=currentProject;state.ready=false;}
  const ready=game()&&editor();
  if(!ready){
   if(state.ready||state.particles||state.cinematic||state.open){leave();paint();}
   state.ready=false;return;
  }
  if(!state.button?.isConnected||!state.panel?.isConnected)mount();
  if(!state.ready){state.ready=true;paint();}
 }
 // Extend the native cinematic update only when the owner enables preview.
 // The existing animeUpdateCinematic -> storyRender path still owns all drawing.
 const originalAnimeUpdate=animeUpdateCinematic;
 animeUpdateCinematic=function(dt){
  if(state.cinematic&&editor()&&authoredCinematic()&&storyPreviewActive&&animeCine){
   const duration=storyTimeline().duration;
   if(duration>0)animeCine.elapsed=(animeCine.elapsed+Math.max(0,Math.min(Number(dt)||0,.06)))%duration;
  }
  return originalAnimeUpdate(dt);
 };
 document.addEventListener('pointerdown',event=>{
  if(!state.open||!state.panel||!state.button)return;
  if(!state.panel.contains(event.target)&&!state.button.contains(event.target)){
   state.open=false;paint();
  }
 },{passive:true});
 window.SWYRL_ENGINE_EDITOR_PREVIEW_247=Object.freeze({
  sync,leave,particles:toggleParticles,cinematic:toggleCinematic,
  inspect:()=>({game:game(),edit:editor(),particles:state.particles,
   cinematic:state.cinematic,panelOpen:state.open,project:currentProject?.canonicalId||null})
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(sync,0),{once:true});
 else setTimeout(sync,0);
})();