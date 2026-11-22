/* §E v11.542 — paint-ready relaxed humanoid UV atlas starter.
   The baked atlas is loaded, never parameterized on an Android/Quest device.
   Keep the stable Starter Models ID and account/project ownership intact. */
const se542HumanoidAsset='scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json';
let se542LoadingHumanoid=false;
function se542ValidateHumanoid(scene){
 const base=se538ValidateHumanoid(scene);
 const part=scene?.project?.modelAtelier?.parts?.[0], m=part?.topologyMesh;
 if(scene?.version!==11.542||part?.id!=='humanoid-body-unified'||
   !part?.name?.includes('relaxed non-overlapping paint atlas')||
   !scene.project.modelAtelier.reference.includes('xatlas-relaxed')||
   m.indices.length/3<12500||m.indices.length/3>16000||
   !/^data:image\/png;base64,/.test(part.uvPaintPNG))
    throw Error('UV-ready mannequin asset is incomplete or not the verified atlas.');
 return base;
}
async function se542OpenHumanoid(force=false){
 if(se542LoadingHumanoid)return false;
 if(dirty&&!force&&!confirm('Open the UV-ready humanoid and discard unsaved edits?'))return false;
 se542LoadingHumanoid=true;
 try{
  toast('Opening refined humanoid with relaxed paint-ready UV charts…');
  const response=await fetch(new URL(se542HumanoidAsset,document.baseURI).href,{cache:'no-cache'});
  if(!response.ok)throw Error('UV-ready mannequin unavailable (HTTP '+response.status+').');
  const source=await response.json();
  const counts=se542ValidateHumanoid(source);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
   throw Error('Model Studio is not initialized.');
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
     currentProject?.modelAtelier?.parts?.length!==1||
     currentProject?.modelAtelier?.parts?.[0]?.id!=='humanoid-body-unified')
   throw Error('Native scene did not load the verified unified humanoid body.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened UV-ready detailed humanoid starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Humanoid UV atlas ready · '+counts.vertices+' vertices · existing painted material retained');
  return true;
 }catch(error){
  console.error('§E UV-ready humanoid starter',error);
  toast('UV-ready humanoid could not open: '+String(error?.message||error).slice(0,155));
  return false;
 }finally{se542LoadingHumanoid=false;}
}
se537OpenMannequin=se542OpenHumanoid;
window.SWYRL_ENGINE_HUMANOID_542=Object.freeze({
 open:se542OpenHumanoid,validate:se542ValidateHumanoid,
 status:()=>({busy:se542LoadingHumanoid,
  active:currentProject?.canonicalId==='robotic-humanoid-mannequin',
  cardExists:!!document.querySelector('button[data-project-template="robotic-humanoid-mannequin"]')})
});
/* SE542_HUMANOID_UV_STARTER_END */
