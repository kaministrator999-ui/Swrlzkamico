// §E v11.142 — mobile playback toolbar, menu entry and authored character gait.
// A corrective additive patch: no map-data migrations, no wolf/gameplay changes.
const se142={rigs:new Map(),lastPositions:new Map(),distance:new Map(),stopParent:null};
function se142CurrentMatches(){
 const rec=seLevelsCurrent(),project=currentProject;
 if(!rec||!project||!seLevels.records.size)return false;
 const p=rec.data?.project||{};
 return project.kind===p.kind && (
  project.levelProjectRoot===seLevels.root ||
  !!(project.canonicalId&&p.canonicalId===project.canonicalId) ||
  !!(project.name&&project.name===p.name)
 );
}
// Native applyProjectMeta may reconstitute only whitelisted project fields.
// Restore level metadata after the native loader has committed the scene.
function se142RestoreLevelMeta(){
 if(!se142CurrentMatches())return false;
 const p=seLevelsCurrent()?.data?.project;
 currentProject.levelProjectRoot=seLevels.root;
 currentProject.sheepTagLevel=p?.sheepTagLevel||seLevelsCurrent().role;
 if(p?.sheepTagMenu&&!currentProject.sheepTagMenu)
  currentProject.sheepTagMenu=structuredClone(p.sheepTagMenu);
 return true;
}
const se142OwnsBase=seLevelsOwns;
seLevelsOwns=function(){
 return se142OwnsBase()||se142CurrentMatches();
};
const se142OpenBase=seLevelsSwitch;
seLevelsSwitch=function(...args){
 const result=se142OpenBase(...args);
 if(result){se142RestoreLevelMeta();seLevelsRefresh();}
 return result;
};
const se142StarterBase=stLoadStarter;
stLoadStarter=function(...args){
 const result=se142StarterBase(...args);
 se142RestoreLevelMeta();
 seLevelsEnsureUI();seLevelsRefresh();
 return result;
};
const se142LoadBase=loadProject;
loadProject=function(...args){
 const result=se142LoadBase(...args);
 se142RestoreLevelMeta();
 seLevelsRefresh();
 return result;
};
// The old level browser was inside the same mobile toolbar as Play/Pause/
// Stop, pushing Stop out of reach. Mount it over the EDIT viewport instead.
function se142MoveLevelBar(){
 const viewport=$('viewport'),bar=seLevels.bar;
 if(viewport&&bar&&bar.parentElement!==viewport)viewport.appendChild(bar);
}
function se142PlaceStop(){
 const play=$('playBtn'),pause=$('pauseBtn'),stop=$('stopBtn');
 if(!stop||!play)return;
 if(pause?.parentElement===play.parentElement)pause.after(stop);
 else play.after(stop);
}
function se142EnsureGameEntry(){
 if(!seLevels.bar||seLevels.bar.querySelector('#se142PlayGame'))return;
 const button=document.createElement('button');
 button.id='se142PlayGame';button.type='button';button.textContent='▶ Play Game';
 button.title='Launch the project at its Main Menu level';
 button.addEventListener('click',()=>{
  if(playing||simulating||stSession||seLevels.playingMenu)return;
  const menu=[...seLevels.records.values()].find(l=>l.role==='menu');
  if(menu){
   if(seLevels.active!==menu.id&&!seLevelsSwitch(menu.id))return;
   beginPlay();
  }else beginPlay();
 });
 seLevels.bar.insertBefore(button,seLevels.bar.querySelector('#st141NewLevel'));
}
function se142SyncStop(){
 const stop=$('stopBtn');
 if(!stop)return;
 se142PlaceStop();
 // Preserve native gameplay's state machine; menu is an independent mode.
 const active=seLevels.playingMenu||playing||simulating||!!stSession;
 stop.classList.remove('hidden');
 stop.hidden=false;
 stop.disabled=!active;
 stop.setAttribute('aria-label',active?'Stop playback':'Stop (no active playback)');
 if(seLevels.playingMenu){
  stop.onclick=()=>stopSession();
 }
}
const se142EnsureBase=seLevelsEnsureUI;
seLevelsEnsureUI=function(...args){
 const result=se142EnsureBase(...args);
 se142MoveLevelBar();se142EnsureGameEntry();se142SyncStop();
 return result;
};
const se142RefreshBase=seLevelsRefresh;
seLevelsRefresh=function(...args){
 const result=se142RefreshBase(...args);
 se142MoveLevelBar();se142SyncStop();
 return result;
};
function se142CapturePivots(actor){
 const entries=[];
 actor.traverse(node=>{
  if(/^stLeg[0-3]$/.test(node.name)||node.name==='stHead'||node.name==='stTail')
   entries.push({node,rotation:node.rotation.clone(),name:node.name});
 });
 return entries;
}
function se142ResetRig(){
 for(const [actor,joints] of se142.rigs){
  for(const joint of joints)joint.node.rotation.copy(joint.rotation);
 }
 se142.rigs.clear();se142.lastPositions.clear();se142.distance.clear();
}
function se142Gait(dt){
 const step=Math.max(0,Math.min(.05,Number(dt)||0)),menuSheep=seLevelsMenuActors('st-sheep'),
 menuWolves=seLevelsMenuActors('st-wolf');
 for(const actor of [...menuSheep,...menuWolves]){
  if(!se142.rigs.has(actor)){
   se142.rigs.set(actor,se142CapturePivots(actor));
   se142.lastPositions.set(actor,actor.position.clone());
   se142.distance.set(actor,0);
  }
  const prev=se142.lastPositions.get(actor);
  const distance=Math.hypot(actor.position.x-prev.x,actor.position.z-prev.z);
  const total=(se142.distance.get(actor)||0)+distance;
  se142.distance.set(actor,total);
  prev.copy(actor.position);
  // A moving actor needs actual joint motion, not just a translating root.
  const speed=step>0?distance/step:0,blend=Math.min(1,speed/1.25);
  const isWolf=actor.userData?.actorType==='st-wolf';
  const phase=total*(isWolf?8.6:9.7);
  for(const joint of se142.rigs.get(actor)){
   const j=joint.node,base=joint.rotation;
   j.rotation.copy(base);
   if(/^stLeg/.test(joint.name)){
    const i=Number(joint.name.slice(5));
    j.rotation.x+=Math.sin(phase+(i===0||i===3?0:Math.PI))*
      (isWolf?.52:.64)*blend;
   }else if(joint.name==='stHead'){
    j.rotation.x+=Math.sin(phase*.36)*.08*blend;
   }else if(joint.name==='stTail'){
    j.rotation.y+=Math.sin(phase*.59)*.22*blend;
   }
  }
 }
}
const se142MenuTickBase=seLevelsMenuTick;
seLevelsMenuTick=function(dt){
 const running=seLevels.playingMenu;
 se142MenuTickBase(dt);
 if(running&&seLevels.playingMenu)se142Gait(dt);
};
const se142PlayMenuBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 se142RestoreLevelMeta();
 const started=se142PlayMenuBase(...args);
 if(started){
  se142SyncStop();
  const panel=seLevels.overlay;
  if(panel){
   panel.hidden=false;
   panel.style.pointerEvents='auto';
   const button=panel.querySelector('#st141StartGame');
   if(button){button.disabled=false;button.hidden=false;button.style.pointerEvents='auto';}
  }
 }
 return started;
};
const se142StopMenuBase=seLevelsStopMenu;
seLevelsStopMenu=function(...args){
 se142ResetRig();
 const result=se142StopMenuBase(...args);
 if(result){
  setSessionButtons();
  se142SyncStop();
 }
 return result;
};
const se142StopBase=stopSession;
stopSession=function(...args){
 const stopped=se142StopBase(...args);
 se142SyncStop();
 return stopped;
};
// Retain the ordinary native button's original callback when gameplay starts.
// The patched stopSession above dispatches to the menu when required.
const se142PlayBase=beginPlay;
beginPlay=function(...args){
 se142RestoreLevelMeta();
 const result=se142PlayBase(...args);
 se142SyncStop();
 return result;
};
const se142OriginalStatus=window.SWYRL_ENGINE_LEVELS.status;
window.SWYRL_ENGINE_LEVELS.status=function(){
 return {...se142OriginalStatus(),owned:seLevelsOwns(),
   stopVisible:!!$('stopBtn')&&!$('stopBtn').classList.contains('hidden'),
   menuButtonVisible:!!seLevels.overlay?.querySelector('#st141StartGame'),
   gaitRigActors:se142.rigs.size};
};
