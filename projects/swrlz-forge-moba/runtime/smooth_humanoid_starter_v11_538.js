/* §E v11.538 — native smooth humanoid starter replacing 178-piece mannequin. */
const se538ScenePath='scenes/model-atelier-futuristic-humanoid-v11-538.swyrl.json';
let se538Opening=false;
function se538ValidateHumanoid(data){
 const project=data?.project,model=project?.modelAtelier,parts=model?.parts;
 if(project?.canonicalId!=='robotic-humanoid-mannequin'||
    project?.kind!=='model-atelier'||model?.schema!=='swyrl-model-atelier-v1'||
    !Array.isArray(parts)||parts.length!==1||
    !Array.isArray(data?.scene?.actors))
  throw Error('Smooth humanoid scene has an invalid native project envelope.');
 const p=parts[0],m=p?.topologyMesh;
 const verts=m?.positions?.length/3,faces=m?.indices?.length/3;
 if(p?.kind!=='topologyMesh'||p?.id!=='humanoid-body-unified'||
    !Number.isInteger(verts)||verts<2000||verts>9000||
    !Number.isInteger(faces)||faces<4000||faces>16000||
    m?.uvs?.length!==verts*2||
    !m.positions.every(n=>Number.isFinite(n)&&Math.abs(n)<=100)||
    !m.uvs.every(n=>Number.isFinite(n)&&n>=0&&n<=1)||
    !m.indices.every(n=>Number.isInteger(n)&&n>=0&&n<verts))
  throw Error('Smooth humanoid topology or UV coordinates are malformed.');
 if(p.color!=='#ffffff'||p.material!=='silk'||
    typeof p.uvPaintPNG!=='string'||p.uvPaintPNG.length>360000||
    !/^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(p.uvPaintPNG))
  throw Error('Smooth humanoid embedded material atlas is invalid.');
 if(model.meshGroups?.length||model.poseFrames?.length)
  throw Error('Smooth humanoid was authored with unexpected assembly or animation data.');
 return {vertices:verts,triangles:faces,parts:parts.length,hasAtlas:true};
}
async function se538OpenHumanoid(force=false){
 if(se538Opening)return false;
 if(dirty&&!force&&!confirm('Open the smooth futuristic humanoid and discard unsaved changes?'))return false;
 se538Opening=true;
 try{
  toast('Opening continuous UV-ready humanoid body…');
  const response=await fetch(new URL(se538ScenePath,document.baseURI).href,{cache:'no-cache'});
  if(!response.ok)throw Error('Smooth humanoid asset unavailable (HTTP '+response.status+').');
  const source=await response.json();
  const details=se538ValidateHumanoid(source);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
   throw Error('Native Model Studio is not ready.');
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='robotic-humanoid-mannequin'||
     currentProject?.modelAtelier?.parts?.length!==1)
   throw Error('Native project loader did not install the unified body mesh.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened futuristic unified humanoid mannequin');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Futuristic Humanoid · one continuous body · '+details.vertices+' UV vertices / '+details.triangles+' triangles');
  return true;
 }catch(error){
  console.error('§E smooth humanoid starter failed',error);
  toast('Futuristic Humanoid could not open: '+String(error?.message||error).slice(0,155));
  return false;
 }finally{se538Opening=false;}
}
// Preserve the original card/deep-link wiring; both call this replaced function
// dynamically. The earlier generator remains as an archival source only.
se537OpenMannequin=se538OpenHumanoid;
window.SWYRL_ENGINE_HUMANOID_538=Object.freeze({
 open:se538OpenHumanoid,validate:se538ValidateHumanoid,
 status:()=>({busy:se538Opening,
  active:currentProject?.canonicalId==='robotic-humanoid-mannequin',
  cardExists:!!document.querySelector('button[data-project-template="robotic-humanoid-mannequin"]')})
});
/* SE538_SMOOTH_HUMANOID_END */
