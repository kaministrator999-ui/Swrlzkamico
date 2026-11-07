/* SE320_PROJECT_STUDIO_ROUTING_START */
// Route a completed native load, never a snapshot/selection or partial import.
const se320StudioNames=new Set(['game','modeler','particles','materials']);
function se320ProjectStudio(data){
 const p=data?.project||{};
 if(p.kind==='model-atelier'&&p.modelAtelier)return 'modeler';
 const hint=data?.editor?.studioWorkspace;
 if(se320StudioNames.has(hint)&&hint!=='modeler')return hint;
 if(['particle-studio','particle-project','vfx'].includes(p.kind))return 'particles';
 // VFX in an authored game remains a game. Only old empty-scene VFX documents
 // are inferred; current exports carry an explicit editor workspace hint.
 if(Array.isArray(data?.scene?.actors)&&!data.scene.actors.length&&
    Array.isArray(p.particleStudio?.emitters)&&p.particleStudio.emitters.length)return 'particles';
 return 'game';
}
let se320RouteTicket=0;
function se320RouteLoadedStudio(mode,expectedProject){
 const ticket=++se320RouteTicket;
 queueMicrotask(()=>{
  if(ticket!==se320RouteTicket||currentProject!==expectedProject||playing||simulating)return;
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!==mode)
   window.SWYRL_ENGINE_STUDIOS?.change?.(mode);
  if(mode==='modeler')ModelAtelier.syncProject();
  document.getElementById('projectHub')?.classList.remove('show');
  window.dispatchEvent(new CustomEvent('swrlz:project-loaded',{detail:{studio:mode}}));
 });
}
const se320LoadProjectBase=loadProject;
loadProject=function(data,...args){
 const result=se320LoadProjectBase.call(this,data,...args);
 if(Array.isArray(data?.scene?.actors)&&args[0]?.preserveHistory!==true)
  se320RouteLoadedStudio(se320ProjectStudio(data),currentProject);
 return result;
};
const se320ProjectDataBase=projectData;
projectData=function(...args){
 const data=se320ProjectDataBase.apply(this,args);
 const mode=window.SWYRL_ENGINE_STUDIOS?.active?.();
 if(data?.editor&&se320StudioNames.has(mode))data.editor.studioWorkspace=mode;
 return data;
};
const se320CreateTemplateBase=createProjectFromTemplate;
createProjectFromTemplate=function(...args){
 const previous=currentProject;
 const finish=result=>{
  if(result!==false&&currentProject!==previous){
   const mode=currentProject?.kind==='model-atelier'?'modeler':'game';
   se320RouteLoadedStudio(mode,currentProject);
  }
  return result;
 };
 const result=se320CreateTemplateBase.apply(this,args);
 return result&&typeof result.then==='function'?result.then(finish):finish(result);
};
// A successful particle-library import belongs in its full authoring studio.
const se320ParticleImportBase=se223UIImport;
se223UIImport=async function(file){
 const before=currentProject?.particleStudio;
 const result=await se320ParticleImportBase.call(this,file);
 if(file&&currentProject?.particleStudio!==before)
  se320RouteLoadedStudio('particles',currentProject);
 return result;
};
window.SWYRL_ENGINE_PROJECT_ROUTING_320=Object.freeze({classify:se320ProjectStudio});
/* SE320_PROJECT_STUDIO_ROUTING_END */
