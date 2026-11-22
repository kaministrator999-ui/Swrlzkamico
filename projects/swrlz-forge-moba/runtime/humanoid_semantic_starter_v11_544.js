/* §E v11.544 — launch geometry-anchored mannequin, preserve template/save ID. */
const se544HumanoidAsset='scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json';
let se544Opening=false;
function se544ValidateSemanticHumanoid(scene){
 const result=se538ValidateHumanoid(scene);
 const p=scene?.project?.modelAtelier?.parts?.[0],mesh=p?.topologyMesh;
 if(scene?.version!==11.544||p?.id!=='humanoid-body-unified'||
   !p?.name?.includes('surface-anchored robotic paint')||
   !scene?.project?.modelAtelier?.reference?.includes('barycentric')||
   mesh?.indices?.length!==13932*3||mesh?.positions?.length!==8792*3)
   throw Error('Verified geometry-anchored humanoid asset is missing or incompatible.');
 return result;
}
async function se544OpenHumanoid(force=false){
 if(se544Opening)return false;
 if(dirty&&!force&&!confirm('Open the repaired mannequin starter and discard unsaved edits?'))
  return false;
 se544Opening=true;
 try{
  toast('Opening mannequin with correctly mapped robotic surfaces…');
  const response=await fetch(new URL(se544HumanoidAsset,document.baseURI),{cache:'no-cache'});
  if(!response.ok)throw Error('Verified humanoid asset unavailable (HTTP '+response.status+').');
  const source=await response.json(),stats=se544ValidateSemanticHumanoid(source);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
    throw Error('Model Studio is not ready.');
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
     currentProject?.modelAtelier?.parts?.length!==1)
    throw Error('Native scene did not install the verified robotic model.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
    window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened true 3D-to-UV mapped humanoid');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Real surface-mapped robot ready · '+stats.vertices+
   ' UV vertices · one connected body · five digits/hand');
  return true;
 }catch(error){
  console.error('§E humanoid semantic material loader',error);
  toast('Humanoid material unavailable: '+String(error?.message||error).slice(0,150));
  return false;
 }finally{se544Opening=false;}
}
se537OpenMannequin=se544OpenHumanoid;
window.SWYRL_ENGINE_HUMANOID_544=Object.freeze({
 open:se544OpenHumanoid,validate:se544ValidateSemanticHumanoid,
 status:()=>({busy:se544Opening,active:currentProject?.canonicalId==='robotic-humanoid-mannequin'})
});
/* SE544_MAPPED_HUMANOID_STARTER_END */
