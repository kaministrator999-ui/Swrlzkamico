async function loadAnimeGirl(force=false,{saved=false,rebuild=false}={}){
 if(dirty&&!force&&!confirm('Open the girl model and discard unsaved scene changes?'))return false;
 const path=saved?'scenes/model-atelier-girl-saved-v11-90.swyrl.json':'scenes/model-atelier-organic-anime-girl-v11-91.swyrl.json';let data;
 if(rebuild&&!saved)data=ModelAtelier.createAnimeGirl();else{const response=await fetch(path);if(!response.ok)throw Error('Girl starter could not be loaded. Reload the published editor.');data=await response.json();}
 ModelAtelier.close();loadProject(data,{workspaceLocal:true});initializeHistory(saved?'Opened saved girl starter v11.90':'Opened organic anime girl');markSaved();document.getElementById('projectHub')?.classList.remove('show');ModelAtelier.syncProject();ModelAtelier.open();const panel=document.getElementById('modelAtelierPanel');panel.classList.add('courier-studio');document.getElementById('modelAtelierCourierStudio').hidden=false;document.getElementById('modelAtelierCourierStudio').textContent='Edit model';if(!saved)requestAnimationFrame(()=>requestAnimationFrame(()=>ModelAtelier.frameAnimeGirl('body','three')));return true;
}
loadModelAtelierStarter=function(force=false){return loadAnimeGirl(force).catch(e=>{toast(e.message);return false;});};
const atelierAnimeTemplateBase=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){if(['model-atelier','organic-anime-girl','festival-girl-saved'].includes(template))return loadAnimeGirl(force,{saved:template==='festival-girl-saved'}).catch(e=>{toast(e.message);return false;});return atelierAnimeTemplateBase(template,force);};
const atelierAnimeProjectId=new URLSearchParams(location.search).get('project');
if(['organic-anime-girl','festival-girl-saved'].includes(atelierAnimeProjectId))queueMicrotask(()=>loadAnimeGirl(true,{saved:atelierAnimeProjectId==='festival-girl-saved'}).catch(e=>toast(e.message)));
