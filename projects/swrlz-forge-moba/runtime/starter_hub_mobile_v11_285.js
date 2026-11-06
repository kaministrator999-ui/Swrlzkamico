// §E v11.285: finish categorization after the Chat-host project hub mounts.
// se236InstallStarterGroups is private to a closure; never reference it here.
// Observe the actual native hub's categories, move existing card wrappers once,
// and preserve their attached click listeners and default preference inputs.
function se285ConnectStarterSorter(){
 const hub=document.getElementById('projectHub');
 if(!hub)return false;
 let done=false;
 let observer=null;
 const sort=()=>{
  const games=hub.querySelector('#se236StarterGames');
  const models=hub.querySelector('#se236StarterModels');
  if(!games||!models)return;
  observer?.disconnect();
  se284SortStarterCards(); // original nodes, no cloning or reinitialization
  done=true;
  hub.dataset.se285Sorted='true';
 };
 sort();
 if(!done){
  observer=new MutationObserver(sort);
  observer.observe(hub,{childList:true,subtree:true});
 }
 return true;
}
if(document.readyState==='loading'){
 document.addEventListener('DOMContentLoaded',se285ConnectStarterSorter,{once:true});
}else se285ConnectStarterSorter();
window.SWYRL_ENGINE_STARTER_SORT_285=Object.freeze({
 refresh:()=>se284SortStarterCards(),
 status:()=>{
  const games=document.getElementById('se236StarterGames');
  const models=document.getElementById('se236StarterModels');
  const cards=container=>[...(container?.querySelectorAll('button[data-project-template]')||[])];
  return {groupsReady:!!games&&!!models,gameCount:cards(games).length,
   modelCount:cards(models).length,
   misplacedModels:cards(games).filter(se284ModelCard).map(x=>x.dataset.projectTemplate)};
 }
});
