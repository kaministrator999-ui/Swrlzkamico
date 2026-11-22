/* §E v11.540 — true five-digit continuous humanoid starter. */
const se540ScenePath='scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json';
let se540Opening=false;
function se540ValidateHandScene(data){
 const stats=se538ValidateHumanoid(data);
 const model=data.project.modelAtelier;
 if(data.version!==11.540||
    !/five-finger hands/i.test(model.parts[0].name)||
    !/opposable thumb/i.test(model.reference)||
    !/Four separate tapered fingertips/i.test(model.reference))
  throw Error('Futuristic mannequin hand geometry is not the verified five-digit starter.');
 if(stats.vertices<6000||stats.triangles<12000||
    stats.vertices>9000||stats.triangles>16000)
  throw Error('Hand-detail topology exceeds safe native limits.');
 return stats;
}
async function se540OpenHumanoid(force=false){
 if(se540Opening)return false;
 if(dirty&&!force&&!confirm('Open the refined humanoid and discard unsaved edits?'))return false;
 se540Opening=true;
 try{
  toast('Opening refined one-piece humanoid with five-digit hands…');
  const response=await fetch(new URL(se540ScenePath,document.baseURI).href,{cache:'no-cache'});
  if(!response.ok)throw Error('Refined mannequin asset unavailable (HTTP '+response.status+').');
  const source=await response.json();
  const stats=se540ValidateHandScene(source);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
    throw Error('Native Model Studio is not ready.');
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
     currentProject?.modelAtelier?.parts?.length!==1||
     currentProject?.modelAtelier?.parts?.[0]?.id!=='humanoid-body-unified')
    throw Error('Unified hand-detail scene was not installed by the project loader.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
    window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened five-digit futuristic humanoid');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Refined humanoid · 5 fingers per hand · '+stats.vertices+' UV vertices');
  return true;
 }catch(error){
  console.error('§E refined humanoid starter',error);
  toast('Cannot open refined humanoid: '+String(error?.message||error).slice(0,160));
  return false;
 }finally{se540Opening=false;}
}
// Preserve old direct-link and Projects UI callbacks by changing only their
// target function; do not mutate user-saved copies or historical starter data.
se537OpenMannequin=se540OpenHumanoid;
window.SWYRL_ENGINE_HUMANOID_540=Object.freeze({
  open:se540OpenHumanoid,validate:se540ValidateHandScene,
  status:()=>({busy:se540Opening,
    active:currentProject?.canonicalId==='robotic-humanoid-mannequin',
    cardExists:!!document.querySelector('button[data-project-template="robotic-humanoid-mannequin"]')})
});
/* SE540_HUMANOID_HANDS_END */
