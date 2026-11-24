/* §E v11.554: distinct native UV-first modeling starter.
   Delivery-only addition to the sealed v11.552 engine. Existing starters and
   user-owned projects are not overwritten or migrated. */
const se554Scene='scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json';
let se554Loading=false;
function se554Validate(data){
 const p=data?.project,part=p?.modelAtelier?.parts?.[0],m=part?.topologyMesh;
 if(data?.version!==11.554||p?.canonicalId!=='clean-topology-humanoid'||
    p?.template!=='clean-topology-humanoid'||p?.modelAtelier?.parts?.length!==1||
    part?.id!=='clean-topology-humanoid-base'||part?.kind!=='topologyMesh'||
    !m||m.positions.length<1000||m.positions.length/3>9000||
    m.indices.length%3||m.indices.length/3>16000||
    m.uvs.length!==m.positions.length/3*2||
    !m.uvs.every(v=>Number.isFinite(v)&&v>=0&&v<=1)||
    !/^data:image\\/png;base64,/.test(part.uvPaintPNG||''))
  throw Error('UV-first starter failed native geometry/UV contract');
 return {vertices:m.positions.length/3,triangles:m.indices.length/3};
}
async function se554Open(force=false){
 if(se554Loading)return false;
 if(dirty&&!force&&!confirm('Open Clean Topology Humanoid? Unsaved workspace changes will be discarded.'))return false;
 se554Loading=true;
 try{
  const response=await fetch(new URL(se554Scene,document.baseURI),{cache:'no-cache'});
  if(!response.ok)throw Error('Clean Topology Humanoid scene HTTP '+response.status);
  const scene=await response.json(),stats=se554Validate(scene);
  ModelAtelier.close();
  loadProject(scene,{workspaceLocal:true});
  if(currentProject?.canonicalId!=='clean-topology-humanoid')throw Error('Native scene did not load');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened Clean Topology Humanoid · UV-first sculpt base');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('UV-first humanoid · '+stats.vertices+' vertices · '+stats.triangles+
        ' triangles · 6 anatomical UV regions. Sculpt and inspect the grid.');
  return true;
 }catch(e){
  console.error('§E UV-first starter',e);
  toast('Clean Topology Humanoid unavailable: '+String(e?.message||e).slice(0,150));
  return false;
 }finally{se554Loading=false;}
}
function se554Install(){
 if(document.querySelector('[data-project-template="clean-topology-humanoid"]'))return true;
 const reference=document.querySelector('button[data-project-template="robotic-humanoid-mannequin"]');
 if(!reference)return false;
 const card=document.createElement('button');
 card.type='button';card.className='project-card den';
 card.dataset.projectTemplate='clean-topology-humanoid';
 card.innerHTML='<span class="project-icon">◇</span>'+
  '<strong>Clean Topology Humanoid · UV-First</strong>'+
  '<span class="template-tag">STARTER MODEL · QUAD LOOPS · CLEAN UV TEST</span>'+
  '<p>Experimental T-pose sculpt base built from ordered quad loops: shaped head,'+
  ' torso, arms, hands, fingers, legs and feet. Regular UV atlas with a neutral'+
  ' checker diagnostic skin. Original robotic humanoid unchanged.</p>'+
  '<span class="hint den-glow">Open in Model Studio</span>';
 // Own click handler is registered in capture phase before existing
 // delegated template click handlers. No fake or inert starter UI.
 card.addEventListener('click',e=>{
  e.preventDefault();e.stopImmediatePropagation();e.stopPropagation();
  void se554Open(false);
 },true);
 reference.insertAdjacentElement('afterend',card);
 return true;
}
se554Install();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se554Install,{once:true});
window.SWYRL_ENGINE_CLEAN_TOPOLOGY=Object.freeze({
 open:se554Open,validate:se554Validate,install:se554Install,
 status:()=>({busy:se554Loading,card:!!document.querySelector('[data-project-template="clean-topology-humanoid"]'),
             active:currentProject?.canonicalId==='clean-topology-humanoid'})
});
/* SE554_UV_FIRST_STARTER_END */
