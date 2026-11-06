// §E v11.284 · Plain Hand Base and correct Starter Games/Models categorization.
// New independent rigged, organic 3D hand anatomy; no glove, armor, rocks,
// runes, effects or decorations. The existing rocky/glove starters stay intact.
const se284HandId='plain-hand-base';
function se284PlainHandScene(){
 // Original watertight sculptable hand surface already matches the real native
 // 17-bone hand rest pose. Retain only its anatomical mesh; discard ALL costume
 // geometry. Do not simplify the full 3D hand to a primitive approximation.
 const scene=se212HandScene();
 const model=scene.project.modelAtelier;
 const source=model.parts.find(p=>p.kind==='topologyMesh'&&
  p.organicSurface?.region==='shell'&&p.topologyMesh?.positions?.length);
 if(!source)throw Error('Plain Hand needs the connected five-finger anatomy mesh.');
 if(!se220RigValidate(model.rigging)||model.rigging.bones.length!==17)
  throw Error('The 17-joint hand rig is missing.');
 const part=structuredClone(source);
 part.id='plain-hand-anatomy';
 part.name='Plain anatomy · connected palm, wrist, thumb and fingers';
 part.color='#c2ac98';
 part.material='matte';
 part.group='Plain Hand / editable anatomy';
 part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];
 // The organicSurface tag selects the connected sculptable topology. It does
 // not add a costume, glow or wrapper to the visible geometry.
 part.organicSurface={species:'plain-hand',region:'shell'};
 model.parts=[part];
 model.name='Plain Hand Base';
 model.meshGroups=[];
 model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';
 model.reference='One smooth, plain five-finger hand anatomy mesh; neutral matte clay color. No armor, glove, rocks, runes, floating effects or other accessories. Native 17-joint animation ready.';
 scene.project.name='Plain Hand Base';
 scene.project.kind='model-atelier';
 scene.project.template=se284HandId;
 scene.project.canonicalId=se284HandId;
 scene.project.environmentSettings={
  ...scene.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#20202a'
 };
 scene.engine='§wyrl§ Engine · Maker v11.284';scene.version=11.284;
 return scene;
}
function se284OpenPlainHand(force=false){
 if(dirty&&!force&&!confirm('Open Plain Hand Base and discard unsaved scene changes?'))
  return false;
 try{
  const source=se284PlainHandScene();
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  initializeHistory('Opened Plain Hand Base starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  se232ActivateSelectedModelWorkspace();
  ModelAtelier.syncProject();
  requestAnimationFrame(()=>requestAnimationFrame(()=>
    window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Plain Hand Base · clean anatomical mesh and 17-bone finger rig ready');
  return true;
 }catch(error){
  console.error('Plain Hand starter',error);
  toast('Unable to open Plain Hand Base: '+String(error.message||error).slice(0,120));
  return false;
 }
}
const se284PriorTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se284HandId)return se284OpenPlainHand(force);
 return se284PriorTemplate(template,force);
};
// The v11.236 categories were installed before several newer Model Atelier
// starters were added. Recognize explicit type labels and known model IDs,
// not just the old hand/wolf regex. Reparent existing cards, never clone them,
// so click handling, saved defaults, references and event listeners remain.
const se284ModelStarterIds=new Set([
 'plain-hand-base','rocky-anime-hand','floating-hand-glove','arcane-glove-left',
 'comet-courier','blank-model','festival-girl-saved',
 'sheep-free-shelter','sheep-thatched-hut','sheep-cottage',
 'sheep-barn','sheep-ram-house','sheep-model','wolf-model'
]);
const se284GameStarterIds=new Set(['blank-vr-hands']);
function se284ModelCard(card){
 const id=card?.dataset?.projectTemplate||'';
 if(!id||se284GameStarterIds.has(id))return false;
 if(se284ModelStarterIds.has(id))return true;
 const label=(card.querySelector('.template-tag')?.textContent||'')
  .trim().toLowerCase();
 // An explicitly tagged game must stay in games regardless of its name.
 if(/starter game|game starter|playable game/.test(label))return false;
 if(/starter model|native 3d model|model atelier|model starter|rigged model/.test(label))
  return true;
 if(/(?:^|[-_])(?:model|atelier|sculpt|ferret|glove|character)(?:$|[-_])/.test(id))
  return true;
 return false;
}
function se284CardNode(child){
 const card=child.matches?.('button[data-project-template]')?child:
  child.querySelector?.('button[data-project-template]');
 return card||null;
}
function se284SortStarterCards(){
 const pane=document.getElementById('se170-pane-starter');
 const games=pane?.querySelector('#se236StarterGames');
 const models=pane?.querySelector('#se236StarterModels');
 if(!games||!models)return false;
 let moved=0;
 for(const child of [...games.children]){
  const card=se284CardNode(child);
  if(card&&se284ModelCard(card)){models.append(child);moved++;}
 }
 // Also repair the reverse classification for a real game if older regex
 // accidentally categorized it as a Model (e.g. a game with "glove" in name).
 for(const child of [...models.children]){
  const card=se284CardNode(child);
  if(card&&se284GameStarterIds.has(card.dataset.projectTemplate)){
   games.append(child);moved++;
  }
 }
 return moved>=0;
}
const se284PriorGroups=se236InstallStarterGroups;
se236InstallStarterGroups=function(){
 const result=se284PriorGroups.apply(this,arguments);
 se284SortStarterCards();
 return result;
};
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',()=>se284SortStarterCards(),{once:true});
else se284SortStarterCards();
window.SWYRL_ENGINE_PLAIN_HAND_BASE=Object.freeze({
 id:se284HandId,createScene:se284PlainHandScene,open:se284OpenPlainHand,
 status:()=>({
  modelCard:!!document.querySelector('[data-project-template="plain-hand-base"]'),
  categoryReady:!!document.getElementById('se236StarterModels'),
  isModelCard:se284ModelCard(document.querySelector('[data-project-template="plain-hand-base"]')),
  nativeRig:typeof se220RigValidate==='function'
 })
});
