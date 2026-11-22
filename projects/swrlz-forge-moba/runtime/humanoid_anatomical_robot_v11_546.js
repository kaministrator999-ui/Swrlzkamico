/* §E v11.546 — one-piece anatomical UV robot with a newly baked skin. */
const se546Asset='scenes/model-atelier-futuristic-humanoid-v11-546.swyrl.json';
let se546Opening=false;
function se546Verify(scene){
 const metrics=se538ValidateHumanoid(scene);
 const part=scene?.project?.modelAtelier?.parts?.[0],mesh=part?.topologyMesh;
 if(scene?.version!==11.546||scene?.project?.canonicalId!=='robotic-humanoid-mannequin'||
    part?.id!=='humanoid-body-unified'||
    !part?.name?.includes('anatomy-mapped new robotic shell')||
    !scene?.project?.modelAtelier?.reference?.includes('anatomy-oriented xatlas UV charts')||
    mesh?.indices?.length!==13932*3||
    mesh?.uvs?.length!==mesh?.positions?.length/3*2||
    mesh?.positions?.length/3>9000||
    !/^data:image\/png;base64,/.test(part.uvPaintPNG))
   throw Error('Anatomical UV robot scene failed native structure validation.');
 return metrics;
}
async function se546Open(force=false){
 if(se546Opening)return false;
 if(dirty&&!force&&!confirm('Open the newly UV-mapped robotic mannequin? Unsaved edits in the current workspace will be discarded.'))
  return false;
 se546Opening=true;
 try{
  toast('Opening anatomical UV robot and new ceramic/graphite skin…');
  const response=await fetch(new URL(se546Asset,document.baseURI),{cache:'no-cache'});
  if(!response.ok)throw Error('Anatomical robot scene unavailable (HTTP '+response.status+').');
  const scene=await response.json(),metrics=se546Verify(scene);
  ModelAtelier.close();
  loadProject(scene,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
     currentProject?.modelAtelier?.parts?.length!==1)
    throw Error('Loaded project does not match the expected native humanoid.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
    window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened anatomy-mapped robot and new baked material');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
    window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Anatomical UV mannequin · '+metrics.vertices+
    ' UV vertices · 13,932 triangles · new robotic skin · 4K UV export available');
  return true;
 }catch(error){
  console.error('§E anatomical robot starter',error);
  toast('Anatomical robot unavailable: '+String(error?.message||error).slice(0,155));
  return false;
 }finally{se546Opening=false;}
}
se537OpenMannequin=se546Open;
window.SWYRL_ENGINE_HUMANOID_546=Object.freeze({
 open:se546Open,validate:se546Verify,
 status:()=>({busy:se546Opening,active:currentProject?.canonicalId==='robotic-humanoid-mannequin'})
});
/* SE546_ANATOMY_ROBOT_STARTER_END */