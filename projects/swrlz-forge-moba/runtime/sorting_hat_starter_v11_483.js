// §E v11.483 — native editable Sorting Hat starter.
// Scene is authored as Model Atelier topology meshes. This is not a second
// renderer, image billboard, or imported proprietary film/game asset.
const se483SortingHatId='sorting-hat';
let se483SortingHatBusy=false;
function se483ValidateSortingHat(scene){
 const project=scene?.project,model=project?.modelAtelier,parts=model?.parts;
 if(project?.kind!=='model-atelier'||project.canonicalId!==se483SortingHatId||
    model?.schema!=='swyrl-model-atelier-v1'||!Array.isArray(parts)||
    parts.length<12||parts.length>400||!Array.isArray(scene?.scene?.actors))
  throw Error('Sorting Hat model file has an invalid native project envelope.');
 const seen=new Set();
 for(const part of parts){
  const mesh=part?.topologyMesh,xyz=mesh?.positions,uv=mesh?.uvs,ix=mesh?.indices;
  if(typeof part.id!=='string'||seen.has(part.id)||part.kind!=='topologyMesh'||
     !Array.isArray(xyz)||xyz.length<9||xyz.length%3||
     !Array.isArray(uv)||uv.length!==xyz.length/3*2||
     !Array.isArray(ix)||ix.length<3||ix.length%3||
     !xyz.every(n=>Number.isFinite(n)&&Math.abs(n)<=100)||
     !uv.every(n=>Number.isFinite(n)&&Math.abs(n)<=20)||
     !ix.every(n=>Number.isInteger(n)&&n>=0&&n<xyz.length/3))
    throw Error('Sorting Hat mesh section is malformed: '+String(part?.name||part?.id));
  seen.add(part.id);
 }
 return parts.length;
}
async function se483OpenSortingHat(force=false){
 if(se483SortingHatBusy)return false;
 if(dirty&&!force&&!confirm('Open The Sorting Hat and discard unsaved changes?'))return false;
 se483SortingHatBusy=true;
 try{
  toast('Opening The Sorting Hat in Model Studio…');
  const url=new URL('scenes/model-atelier-sorting-hat.swyrl.json',document.baseURI);
  const response=await fetch(url.href,{cache:'no-cache'});
  if(!response.ok)throw Error('Sorting Hat asset unavailable (HTTP '+response.status+').');
  const scene=await response.json();
  const numberOfMeshes=se483ValidateSortingHat(scene);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
   throw Error('Native Model Studio is unavailable.');
  ModelAtelier.close();
  loadProject(scene,{workspaceLocal:true});
  if(currentProject?.kind!=='model-atelier'||currentProject?.canonicalId!==se483SortingHatId||
     currentProject?.modelAtelier?.parts?.length!==numberOfMeshes)
   throw Error('Native project loader did not install Sorting Hat geometry.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  const state=ModelAtelier.status();
  if(!state?.open||window.SWYRL_ENGINE_WORKSPACES?.active?.()!=='modeler')
   throw Error('Model Studio did not open after loading The Sorting Hat.');
  initializeHistory('Opened The Sorting Hat native starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('The Sorting Hat · '+numberOfMeshes+' native editable sections ready');
  return true;
 }catch(error){
  console.error('§E Sorting Hat starter load failed',error);
  toast('Sorting Hat could not open: '+String(error?.message||error).slice(0,150));
  return false;
 }finally{se483SortingHatBusy=false;}
}
const se483PriorCreateProjectFromTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se483SortingHatId)return se483OpenSortingHat(force);
 return se483PriorCreateProjectFromTemplate(template,force);
};
function se483InstallSortingHatCard(){
 const hub=document.getElementById('projectHub');
 if(!hub||hub.dataset.se483SortingHatClick)return;
 hub.dataset.se483SortingHatClick='true';
 hub.addEventListener('click',event=>{
  const button=event.target?.closest?.('button[data-project-template="sorting-hat"]');
  if(!button)return;
  event.preventDefault();
  event.stopImmediatePropagation();
  void se483OpenSortingHat();
 },true);
}
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',se483InstallSortingHatCard,{once:true});
else se483InstallSortingHatCard();
window.SWYRL_ENGINE_SORTING_HAT_483=Object.freeze({
 open:se483OpenSortingHat,validate:se483ValidateSortingHat,
 status:()=>({busy:se483SortingHatBusy,
  cardExists:!!document.querySelector('button[data-project-template="sorting-hat"]'),
  active:currentProject?.canonicalId===se483SortingHatId})
});
/* SE483_SORTING_HAT_END */
