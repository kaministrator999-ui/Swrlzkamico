// §E v11.361 · Reliable native starter opening, plus editable Quest 2 Touch models.
// Reuse Model Studio's one project loader, renderer and workspace; no extra panel.
const se361StarterSpecs=Object.freeze({
 'webxr-hand-left':Object.freeze({kind:'hand',side:'left'}),
 'webxr-hand-right':Object.freeze({kind:'hand',side:'right'}),
 'webxr-touch-left':Object.freeze({kind:'controller',side:'left'}),
 'webxr-touch-right':Object.freeze({kind:'controller',side:'right'})
});
const se361ControllerCache=new Map();
let se361Loading=false;
function se361StarterCheck(asset,spec){
 if(asset?.schema!=='swrlz-webxr-controller-v1'||asset.side!==spec.side||
    !Array.isArray(asset.parts)||asset.parts.length!==7||
    typeof asset.colorTexturePNG!=='string'||asset.colorTexturePNG.length>360000||
    !/^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(asset.colorTexturePNG))
  throw Error('Invalid bundled Quest controller geometry or texture.');
 for(const part of asset.parts){
  const t=part.mesh;
  if(!t||!Array.isArray(t.positions)||t.positions.length<9||
     t.positions.length>27000||t.positions.length%3||
     !Array.isArray(t.uvs)||t.uvs.length!==t.positions.length/3*2||
     !Array.isArray(t.indices)||!t.indices.length||t.indices.length%3||
     t.indices.length>48000||!t.positions.every(v=>Number.isFinite(v)&&Math.abs(v)<=100)||
     !t.uvs.every(v=>Number.isFinite(v)&&Math.abs(v)<=20)||
     !t.indices.every(i=>Number.isInteger(i)&&i>=0&&i<t.positions.length/3))
   throw Error('One Quest controller part exceeds the native mesh limits.');
 }
 return true;
}
async function se361ControllerScene(side){
 const id='webxr-touch-'+side,spec=se361StarterSpecs[id];
 if(!spec)throw Error('Unknown Quest controller.');
 let asset=se361ControllerCache.get(side);
 if(!asset){
  const url=new URL('assets/models/webxr-touch-v3/'+side+'.json',document.baseURI);
  const response=await fetch(url.href);
  if(!response.ok)throw Error('Quest 2 '+side+' asset missing (HTTP '+response.status+').');
  asset=await response.json();
  se361StarterCheck(asset,spec);
  se361ControllerCache.set(side,asset);
 }
 const source=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT);
 const model=source.project.modelAtelier;
 const label=side==='left'?'Left':'Right';
 const prefix='webxr-touch-'+side;
 model.name='Quest 2 Touch · '+label+' Controller';
 model.parts=asset.parts.map((section,i)=>({
  id:prefix+'-'+i,
  name:section.title,
  group:'Quest 2 Touch / '+(section.key.startsWith('controller')?'Housing':'Controls'),
  kind:'topologyMesh',topologyMesh:structuredClone(section.mesh),
  position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
  color:'#ffffff',material:'matte',
  uvPaintPNG:asset.colorTexturePNG
 }));
 model.meshGroups=[{
  id:prefix+'-assembly',name:label+' Quest 2 Touch assembly',
  members:model.parts.map(part=>part.id)
 }];
 model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';
 model.reference='WebXR Input Profiles oculus-touch-v3/'+side+'.glb (Quest 2). Seven individually editable native mesh sections, original UV color artwork and one selectable assembly. Source MIT license: assets/models/webxr-touch-v3/LICENSE.md. This is a modeling starter, not a live controller input model.';
 source.project.name=model.name;
 source.project.template=id;
 source.project.canonicalId=id;
 source.project.kind='model-atelier';
 source.project.environmentSettings={...source.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#20202a'};
 source.engine='§wyrl§ Engine · Maker v11.361';source.version=11.361;
 return source;
}
async function se361OpenStarter(id,force=false){
 const spec=se361StarterSpecs[id];
 if(!spec||se361Loading)return false;
 if(dirty&&!force&&!confirm('Open '+(spec.kind==='hand'?'WebXR '+spec.side+' hand':'Quest 2 '+spec.side+' controller')+' and discard unsaved changes?'))return false;
 se361Loading=true;
 try{
  const label=spec.kind==='hand'?'WebXR '+spec.side+' hand':'Quest 2 '+spec.side+' controller';
  toast('Loading '+label+' modeling project…');
  const source=spec.kind==='hand'?await se358WebXRHandScene(spec.side):await se361ControllerScene(spec.side);
  const parts=source?.project?.modelAtelier?.parts;
  if(!Array.isArray(source?.scene?.actors)||!parts?.length||
     source.project?.kind!=='model-atelier')
   throw Error('Starter data does not contain a complete Model Studio scene.');
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')
   throw Error('Model Studio is not available in this editor.');
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.kind!=='model-atelier'||
     currentProject?.modelAtelier?.parts?.length!==parts.length)
   throw Error('Project loader did not install the starter meshes.');
  // The native modeler owns renderer initialization; do not open an
  // independent preview or silently report success while Game is active.
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  const state=ModelAtelier.status();
  if(!state.open||window.SWYRL_ENGINE_WORKSPACES?.active?.()!=='modeler')
   throw Error('Model Studio did not open the loaded starter.');
  initializeHistory('Opened '+label+' native starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast(label+' · '+parts.length+' editable mesh section'+(parts.length===1?'':'s')+' ready');
  return true;
 }catch(error){
  console.error('§E reference starter load failed',id,error);
  toast('Could not open '+id+': '+String(error?.message||error).slice(0,145));
  return false;
 }finally{se361Loading=false;}
}
const se361PriorCreateTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(Object.prototype.hasOwnProperty.call(se361StarterSpecs,template))
  return se361OpenStarter(template,force);
 return se361PriorCreateTemplate(template,force);
};
// The legacy project grid binds onClick early. Capture the four starter cards
// at their existing host so reparenting or template wrapper order cannot
// bypass the native loading route. No duplicate cards or buttons.
function se361InstallStarterClicks(){
 const hub=document.getElementById('projectHub');
 if(!hub||hub.dataset.se361StarterClicks)return;
 hub.dataset.se361StarterClicks='true';
 hub.addEventListener('click',event=>{
  const card=event.target?.closest?.('button[data-project-template]');
  const id=card?.dataset.projectTemplate;
  if(!Object.prototype.hasOwnProperty.call(se361StarterSpecs,id))return;
  event.preventDefault();event.stopImmediatePropagation();
  void se361OpenStarter(id);
 },true);
}
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',se361InstallStarterClicks,{once:true});
else se361InstallStarterClicks();
window.SWYRL_ENGINE_WEBXR_MODEL_STARTERS_361=Object.freeze({
 open:se361OpenStarter,controllerScene:se361ControllerScene,
 validate:se361StarterCheck,
 status:()=>({busy:se361Loading,templates:Object.keys(se361StarterSpecs),
  cards:Object.keys(se361StarterSpecs).map(id=>({id,exists:!!document.querySelector(
   'button[data-project-template="'+id+'"]')}))})
});
