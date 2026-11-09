// §E v11.358 · independent left/right WebXR hand reference starters.
// Native editable topology and original UV layout, converted from MIT-licensed
// public generic-hand GLB assets. No remote loader, extra renderer or XR input changes.
const se358HandSides=Object.freeze({left:'webxr-hand-left',right:'webxr-hand-right'});
const se358HandCache=new Map();
let se358HandLoadTicket=0;
async function se358WebXRHandScene(side){
 if(!Object.hasOwn(se358HandSides,side))throw Error('Choose the left or right reference hand.');
 let asset=se358HandCache.get(side);
 if(!asset){
  const response=await fetch('assets/models/webxr-hands/'+side+'.json');
  if(!response.ok)throw Error('Bundled hand geometry missing; reload the published editor.');
  asset=await response.json();
  if(asset.schema!=='swrlz-webxr-reference-hand-v1'||asset.side!==side||
     !Array.isArray(asset.mesh?.positions)||asset.mesh.positions.length!==4080||
     !Array.isArray(asset.mesh?.uvs)||asset.mesh.uvs.length!==2720||
     !Array.isArray(asset.mesh?.indices)||asset.mesh.indices.length!==6942||
     !Array.isArray(asset.joints)||asset.joints.length!==25)
   throw Error('Invalid WebXR hand asset; please reload the editor.');
  se358HandCache.set(side,asset);
 }
 const source=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT);
 const m=source.project.modelAtelier;
 const label=side==='left'?'Left':'Right';
 m.name='WebXR '+label+' Hand · Reference';
 m.parts=[{
  id:'webxr-hand-'+side+'-surface',
  name:label+' hand · editable anatomical surface and UVs',
  kind:'topologyMesh',
  position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
  color:'#cbb6a7',material:'matte',group:'WebXR hand reference',
  topologyMesh:structuredClone(asset.mesh)
 }];
 m.meshGroups=[];m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';
 // Source 25-joint coordinates are reference landmarks, NOT an authored
 // Model Atelier skin/animation rig; never claim live tracking in this starter.
 m.referenceJoints=structuredClone(asset.joints);
 m.reference='Derived from WebXR Input Profiles generic-hand/'+side+'.glb; 1,360 vertices, 2,314 triangles, original UVs and 25 reference joint landmarks. MIT license in assets/models/webxr-hands/LICENSE.md. The mesh is editable; XR joint tracking is not attached to this starter.';
 source.project.kind='model-atelier';
 source.project.name=m.name;
 source.project.canonicalId=se358HandSides[side];
 source.project.template=se358HandSides[side];
 source.project.environmentSettings={
  ...source.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#20202a'
 };
 source.engine='§wyrl§ Engine · Maker v11.358';source.version=11.358;
 return source;
}
async function se358OpenWebXRHand(side,force=false){
 if(!Object.hasOwn(se358HandSides,side))return false;
 if(dirty&&!force&&!confirm('Open WebXR '+side+' hand and discard unsaved scene changes?'))return false;
 const ticket=++se358HandLoadTicket;
 try{
  toast('Opening WebXR '+side+' reference hand…');
  const scene=await se358WebXRHandScene(side);
  if(ticket!==se358HandLoadTicket)return false;
  ModelAtelier.close();
  loadProject(scene,{workspaceLocal:true});
  initializeHistory('Opened WebXR '+side+' hand reference starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  se232ActivateSelectedModelWorkspace();
  ModelAtelier.syncProject();
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('WebXR '+side+' hand · native mesh, original UVs and 25 reference landmarks ready');
  return true;
 }catch(error){
  if(ticket===se358HandLoadTicket){
   console.error('WebXR reference hand starter',error);
   toast('Unable to open WebXR hand: '+String(error.message||error).slice(0,130));
  }
  return false;
 }
}
const se358PreviousCreateTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se358HandSides.left)return se358OpenWebXRHand('left',force);
 if(template===se358HandSides.right)return se358OpenWebXRHand('right',force);
 return se358PreviousCreateTemplate(template,force);
};
window.SWYRL_ENGINE_WEBXR_HAND_STARTERS=Object.freeze({
 open:se358OpenWebXRHand,createScene:se358WebXRHandScene,
 status:()=>({
  cards:['left','right'].map(side=>({
   side,exists:!!document.querySelector('[data-project-template="'+se358HandSides[side]+'"]'),
   loaded:se358HandCache.has(side)
  }))
 })
});
