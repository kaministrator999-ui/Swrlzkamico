let atelierAnimalLoading=0;
async function loadAnimalProject(species,force=false,rebuild=false){
 if(!['sheep','wolf'].includes(species))throw Error('Choose sheep or wolf.');
 if(dirty&&!force&&!confirm('Open the '+species+' model and discard unsaved changes?'))return false;
 const ticket=++atelierAnimalLoading;toast('Opening organic '+species+' model…');
 const response=await fetch('scenes/model-atelier-organic-'+species+'-v11-87.swyrl.json');if(!response.ok)throw Error('The bundled '+species+' starter could not load.');const data=await response.json();if(ticket!==atelierAnimalLoading)return false;
 if(rebuild)data.project.modelAtelier=atelierAnimalBuild(species);
 ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory('Opened organic '+species+' starter');markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();const panel=document.getElementById('modelAtelierPanel'),studio=document.getElementById('modelAtelierCourierStudio');panel.classList.add('courier-studio');studio.hidden=false;studio.textContent='Edit model';studio.setAttribute('aria-pressed','true');requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view('three')));return true;
}
const atelierAnimalTemplateBase=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){if(['sheep-model','wolf-model','comet-courier'].includes(template))return loadAnimalProject(template==='sheep-model'?'sheep':'wolf',force).catch(e=>{toast(e.message);return false;});return atelierAnimalTemplateBase(template,force);};
if(['sheep-model','wolf-model'].includes(new URLSearchParams(location.search).get('project')))queueMicrotask(()=>loadAnimalProject(new URLSearchParams(location.search).get('project')==='sheep-model'?'sheep':'wolf',true).catch(e=>toast(e.message)));
