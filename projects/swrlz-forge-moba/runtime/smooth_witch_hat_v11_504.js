// §E v11.504 — independent smooth witch hat, one editable UV-painted cloth mesh.
// Keeps the verified Sorting Hat index topology, UV atlas, and original texture.
const se504Template='smooth-witch-hat';
let se504Loading=false;
function se504SmoothHat(scene){
 const project=scene?.project,model=project?.modelAtelier;
 const part=model?.parts?.[0],mesh=part?.topologyMesh;
 if(project?.canonicalId!=='sorting-hat'||model?.parts?.length!==1||
    part?.kind!=='topologyMesh'||mesh?.positions?.length!==7859*3||
    mesh?.uvs?.length!==7859*2||mesh?.indices?.length!==15714*3||
    typeof part.uvPaintPNG!=='string')
   throw Error('Expected original single-mesh, UV-painted Sorting Hat source.');
 const xyz=mesh.positions,original=xyz.slice(),SIDES=96,STRIDE=97,TAU=Math.PI*2;
 const round=n=>Math.round(n*1e5)/1e5;
 const crownRadius=y=>{
   const t=Math.max(0,Math.min(1,(4.075-y)/(4.075-.22)));
   return .012+(.888)*Math.pow(t,.82);
 };
 const brimR=[.96,1.09,1.22,1.35,1.48,1.61,1.61,1.49,1.346,1.202,1.058,.914,.77];
 const brimY=[.203,.191,.178,.165,.153,.140,.067,.079,.093,.107,.121,.135,.140];
 for(let row=0;row<=80;row++){
   let meanY=0;
   for(let j=0;j<SIDES;j++)meanY+=original[(row*STRIDE+j)*3+1]/SIDES;
   const y=row<60?meanY:row<=72?brimY[row-60]:meanY;
   const radius=row<60?crownRadius(y):row<=72?brimR[row-60]:
     Math.max(.055,crownRadius(y)-.13);
   for(let j=0;j<=SIDES;j++){
     const a=-Math.PI/2+TAU*j/SIDES,k=(row*STRIDE+j)*3;
     xyz[k]=round(Math.cos(a)*radius);
     xyz[k+1]=round(y);
     xyz[k+2]=round(Math.sin(a)*radius*.90);
   }
 }
 // Existing two cap vertices close the crown and inner lining.
 xyz[7857*3]=0;xyz[7857*3+1]=4.09;xyz[7857*3+2]=0;
 xyz[7858*3]=0;xyz[7858*3+1]=2.85;xyz[7858*3+2]=0;
 if(xyz.some(n=>!Number.isFinite(n)||Math.abs(n)>20))
   throw Error('Invalid smooth witch-hat geometry.');
 project.canonicalId=se504Template;
 project.template=se504Template;
 project.name='Smooth Witch Hat';
 model.name='Smooth Witch Hat · Texture-First Experiment';
 model.reference='Third standalone §E starter. Smooth upright witch cone, flat continuous brim and inner lining; one sealed editable mesh. Reuses the original Sorting Hat UV layout and painted texture without sculpted eyes or mouth. Compare texture-only face against the other two Sorting Hat starters. No changes to either original.';
 part.id='smooth-witch-hat-cloth';
 part.name='Smooth Witch Hat · single cloth surface';
 part.group='One connected textured mesh';
 return scene;
}
async function se504OpenSmoothWitchHat(force=false){
 if(se504Loading)return false;
 if(dirty&&!force&&!confirm('Open Smooth Witch Hat and discard unsaved changes?'))return false;
 se504Loading=true;
 try{
  toast('Preparing smooth textured witch hat…');
  const url=new URL('scenes/model-atelier-sorting-hat.swyrl.json',document.baseURI);
  const response=await fetch(url.href,{cache:'no-cache'});
  if(!response.ok)throw Error('Sorting Hat source asset HTTP '+response.status);
  const scene=await response.json();
  se504SmoothHat(scene);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
   throw Error('Native Model Studio is unavailable.');
  ModelAtelier.close();
  loadProject(scene,{workspaceLocal:true});
  if(currentProject?.canonicalId!==se504Template||
     currentProject?.modelAtelier?.parts?.length!==1)
   throw Error('Smooth Witch Hat failed to load into native Model Studio.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  if(!ModelAtelier.status()?.open)throw Error('Model Studio did not open.');
  initializeHistory('Opened Smooth Witch Hat independent starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
    window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Smooth Witch Hat · one UV-painted editable cloth mesh ready');
  return true;
 }catch(error){
  console.error('§E Smooth Witch Hat load failed',error);
  toast('Smooth Witch Hat failed: '+String(error?.message||error).slice(0,150));
  return false;
 }finally{se504Loading=false;}
}
const se504PreviousTemplateCreate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se504Template)return se504OpenSmoothWitchHat(force);
 return se504PreviousTemplateCreate(template,force);
};
function se504InstallCard(){
 const hub=document.getElementById('projectHub');
 if(!hub||hub.dataset.se504SmoothHatInstalled)return;
 hub.dataset.se504SmoothHatInstalled='true';
 hub.addEventListener('click',event=>{
  const button=event.target?.closest?.('button[data-project-template="smooth-witch-hat"]');
  if(!button)return;
  event.preventDefault();event.stopImmediatePropagation();
  void se504OpenSmoothWitchHat();
 },true);
}
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',se504InstallCard,{once:true});
else se504InstallCard();
window.SWYRL_ENGINE_SMOOTH_WITCH_HAT_504=Object.freeze({
 open:se504OpenSmoothWitchHat,smooth:se504SmoothHat,
 status:()=>({busy:se504Loading,active:currentProject?.canonicalId===se504Template,
 cardExists:!!document.querySelector('button[data-project-template="smooth-witch-hat"]')})
});
/* SE504_SMOOTH_WITCH_HAT_END */
