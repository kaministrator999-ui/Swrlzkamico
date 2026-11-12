/* SE423_LEVEL_SELECTOR_RECOVERY_START
 * The level collection is owned by seLevels. Never replace saved records.
 * Reattach one existing toolbar when editor chrome is reconstructed.
 */
const se423PriorLevelsEnsure=seLevelsEnsureUI;
seLevelsEnsureUI=function se423EnsureLevels(...args){
 const play=$('playBtn'),stop=$('stopBtn'),viewport=$('viewport');
 if(play&&seLevels.bar&&
    (seLevels.bar.parentElement!==play.parentElement||seLevels.bar.nextSibling!==play))
  play.before(seLevels.bar);
 if(stop&&seLevels.nextButton&&seLevels.nextButton.previousElementSibling!==stop)
  stop.after(seLevels.nextButton);
 if(viewport&&seLevels.preview&&seLevels.preview.parentElement!==viewport)
  viewport.appendChild(seLevels.preview);
 if(viewport?.parentElement&&seLevels.inspector&&
    seLevels.inspector.parentElement!==viewport.parentElement)
  viewport.parentElement.appendChild(seLevels.inspector);
 return se423PriorLevelsEnsure(...args);
};
const se423PriorLevelsHydrate=seLevelsHydrate;
seLevelsHydrate=function se423HydrateLevels(data){
 const ok=se423PriorLevelsHydrate(data);
 if(ok)for(const entry of seLevels.records.values()){
  if(entry.data?.project&&!entry.data.project.levelProjectRoot)
   entry.data.project.levelProjectRoot=seLevels.root;
 }
 return ok;
};
const se423PriorLevelsRefresh=seLevelsRefresh;
seLevelsRefresh=function se423RefreshLevels(...args){
 if(seLevels.records.size)seLevelsEnsureUI();
 return se423PriorLevelsRefresh(...args);
};
let se423LevelObserver=null,se423ObservedToolbar=null,se423LevelRepairPending=false;
function se423RepairLevels(){
 se423LevelRepairPending=false;
 if(!seLevels.records.size)return;
 seLevelsEnsureUI();
 se423PriorLevelsRefresh();
}
function se423ScheduleLevels(){
 if(se423LevelRepairPending)return;
 se423LevelRepairPending=true;
 queueMicrotask(se423RepairLevels);
}
function se423WatchLevelToolbar(){
 const play=$('playBtn'),toolbar=play?.parentElement;
 if(!toolbar||typeof MutationObserver!=='function')return;
 if(se423ObservedToolbar===toolbar)return;
 se423LevelObserver?.disconnect();
 se423ObservedToolbar=toolbar;
 se423LevelObserver=new MutationObserver(()=>{
  const bar=seLevels.bar;
  const currentPlay=$('playBtn');
  if(seLevels.records.size&&currentPlay&&
    (!bar||bar.parentElement!==currentPlay.parentElement||bar.nextSibling!==currentPlay))
   se423ScheduleLevels();
 });
 se423LevelObserver.observe(toolbar,{childList:true});
}
function se423InitLevelRecovery(){
 se423WatchLevelToolbar();
 se423ScheduleLevels();
}
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',se423InitLevelRecovery,{once:true});
else queueMicrotask(se423InitLevelRecovery);
window.addEventListener('swrlz:project-loaded',()=>{
 se423WatchLevelToolbar();se423ScheduleLevels();
});
document.addEventListener('click',event=>{
 if(event.target?.closest?.('#projectBtn,#se320ModelProjects,.project-card,[data-project-template]'))
  requestAnimationFrame(()=>{se423WatchLevelToolbar();se423ScheduleLevels();});
},true);
window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423=Object.freeze({
 repair:()=>{se423InitLevelRecovery();return window.SWYRL_ENGINE_LEVEL_UI_RECOVERY_423.inspect();},
 inspect:()=>({levels:seLevels.records.size,active:seLevels.active,root:seLevels.root,
  owns:!!seLevelsOwns(),barAttached:!!seLevels.bar?.isConnected,
  barVisible:!!seLevels.bar&&!seLevels.bar.hidden,
  toolbarWatched:!!se423ObservedToolbar})
});
/* SE423_LEVEL_SELECTOR_RECOVERY_END */