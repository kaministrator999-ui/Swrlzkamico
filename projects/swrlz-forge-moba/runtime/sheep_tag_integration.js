// Native project data is the starter's authority; gameplay owns only its session.
const ST_TYPES=['st-sheep','st-wolf','st-farm','st-income','st-fort','st-pen','st-tree','st-rock','st-pond','st-shop','st-meadow'];
for(const type of ST_TYPES)ASSET_LIBRARY.push({id:type,name:type.slice(3).replace(/\b\w/g,letter=>letter.toUpperCase())+' · Sheep Tag',path:'/Engine/SheepTag',desc:'Editable Sheep Tag map piece; place, transform and bake before Play.'});
let stAuthorBaseline=null,stEditorViewSnapshot=null;
function stCleanRules(value={}){
  if(!value||typeof value!=='object'||Array.isArray(value))value={};
  const number=(key,fallback,min,max)=>Math.min(max,Math.max(min,Number.isFinite(Number(value[key]))?Number(value[key]):fallback));
  const duration=number('duration',1200,30,3600);
  return {duration,headstart:Math.min(duration,number('headstart',30,0,120)),bounds:number('bounds',40,16,80),
    startGold:number('startGold',80,0,1000),role:value.role==='wolf'?'wolf':'sheep'};
}
function stRules(){return stCleanRules(currentProject.sheepTag||{});}
const stNativeApplyProjectMeta=applyProjectMeta;
applyProjectMeta=function(meta={}){stNativeApplyProjectMeta(meta);if(currentProject.kind==='sheep-tag')currentProject.sheepTag=stCleanRules(currentProject.sheepTag);};
function stConfigureRules(update={}){
  if(playing||simulating)return {ok:false,reason:'Stop the match before editing its rules.'};
  if(currentProject.kind!=='sheep-tag')return {ok:false,reason:'Open a Sheep Tag project first.'};
  beginTransaction('Edit Sheep Tag rules');currentProject.sheepTag=stCleanRules({...stRules(),...update});
  commitTransaction('Edit Sheep Tag rules');return {ok:true,rules:stRules()};
}
function stFrameMap(){
  setCameraView('perspective');perspectiveCamera.fov=50;perspectiveCamera.updateProjectionMatrix();
  perspectiveCamera.position.set(0,82,65);orbit.target.set(0,0,0);perspectiveCamera.lookAt(orbit.target);orbit.update();
}
function stLoadStarter(){
  loadProject(structuredClone(ST_CANONICAL_PROJECT),{workspaceLocal:true});
  currentProject.sheepTag=stCleanRules(currentProject.sheepTag);stFrameMap();
  initializeHistory('Opened Moonbell Meadow Sheep Tag');markSaved();
  editorLog('Sheep Tag · native meadow map · build farms, escape wolves, rescue wisps','ok');toast('Moonbell Meadow · Sheep Tag');
}
function stMakeSpirit(){
  // Reuse the Den's exact glow, core, rings and motes, without its hero combat.
  const spirit=makeWispHero('blue',[0,0,0],true,'Captured Sheep Wisp');
  const index=actors.indexOf(spirit);if(index>=0)actors.splice(index,1);scene.remove(spirit);
  spirit.userData={stSpirit:true};return spirit;
}
function stAnimateSpirit(spirit,time,phase=0){
  const visual=spirit.getObjectByName('WispVisual');if(!visual)return;
  visual.position.y=1.08+Math.sin(time*2.15+phase)*.08;
  const outer=visual.getObjectByName('WispOuterGlow');if(outer){const pulse=1+.08*Math.sin(time*3.4+phase);outer.scale.set(2.15*pulse,2.15*pulse,1);}
  for(const child of visual.children){const orbit=child.userData.wispOrbit;if(orbit){const angle=time*orbit.speed+orbit.phase+phase;child.position.set(Math.cos(angle)*orbit.radius,orbit.y+Math.sin(angle*1.7)*.13,Math.sin(angle)*orbit.radius);}if(child.userData.wispArc!==undefined)child.rotation.z+=.002;}
}
const stNativeProjectData=projectData;
projectData=function(){
  const data=stNativeProjectData();
  if(stAuthorBaseline&&stSession){data.scene=structuredClone(stAuthorBaseline.scene);data.editor.layers=structuredClone(stAuthorBaseline.editor.layers);}
  return data;
};
const stNativeBeginPlay=beginPlay,stNativeBeginSimulate=beginSimulate,stNativeStop=stopSession;
function stBeginNativeSession(simulate=false){
  if(playing||simulating)stopSession();
  const sheep=actors.filter(a=>a.userData.actorType==='st-sheep'&&walkingObjectVisible(a)&&a.userData.baked);
  const wolves=actors.filter(a=>a.userData.actorType==='st-wolf'&&walkingObjectVisible(a)&&a.userData.baked);
  const pen=actors.find(a=>a.userData.actorType==='st-pen'&&walkingObjectVisible(a)&&a.userData.baked);
  if(!sheep.length||!wolves.length||!pen){toast('Add and bake at least one sheep, one wolf and a Spirit Pen before Play.');return false;}
  closeTeleportMenu(false);closeWorkspacePanel(false);stAuthorBaseline=structuredClone(projectData());
  stEditorViewSnapshot={position:camera.position.clone(),quaternion:camera.quaternion.clone(),up:camera.up.clone(),target:orbit.target.clone(),fov:perspectiveCamera.fov};
  preSessionCameraView=editorCameraView;savePlaySnapshot();playing=!simulate;simulating=simulate;paused=false;keepSimulationChanges=false;
  transform.detach();if(selectionBox)selectionBox.visible=false;setActiveCamera(perspectiveCamera);orbit.enabled=simulate;
  if(document.pointerLockElement)document.exitPointerLock?.();
  for(const id of ['mobileDrawer','mobileToolsPanel','contentDrawer'])$(id)?.classList.remove('show');
  stStart(simulate);stShowHUD(true);setSessionButtons();updatePerformanceOverlay(true);
  $('viewLabel').textContent=simulate?'Sheep Tag · Simulate':'Sheep Tag · Play In Editor';
  editorLog('Sheep Tag match started · '+stRules().role,'ok');return true;
}
beginPlay=function(fromHere=null){if(currentProject.kind==='sheep-tag')return stBeginNativeSession(false);return stNativeBeginPlay(fromHere);};
beginSimulate=function(){if(currentProject.kind==='sheep-tag')return stBeginNativeSession(true);return stNativeBeginSimulate();};
stopSession=function(){
  const view=stSession?stEditorViewSnapshot:null;
  if(stSession){stDisposeUI();stStop();}stAuthorBaseline=null;stEditorViewSnapshot=null;
  const result=stNativeStop();
  if(view){camera.position.copy(view.position);camera.quaternion.copy(view.quaternion);camera.up.copy(view.up);orbit.target.copy(view.target);perspectiveCamera.fov=view.fov;perspectiveCamera.updateProjectionMatrix();orbit.update();}
  if(typeof stRefreshHUD==='function'&&$('sheepTagRulesBtn'))stRefreshHUD(true);
  return result;
};
const stNativeSessionButtons=setSessionButtons;
setSessionButtons=function(){stNativeSessionButtons();if(stSession)$('keepBtn').classList.add('hidden');};
// Existing listeners referenced the original function object; rebind the native buttons.
$('playBtn').onclick=()=>beginPlay();$('simulateBtn').onclick=()=>beginSimulate();$('stopBtn').onclick=()=>stopSession();
$('playFromHereBtn').onclick=()=>{if(currentProject.kind==='sheep-tag')beginPlay();else if(selected)beginPlay(selected.getWorldPosition(new THREE.Vector3()));};
window.SWYRL_ENGINE_SHEEP_TAG={
  status:()=>stStatus(),command:(action,payload={})=>stCommand(action,payload),configure:(update)=>stConfigureRules(update),
  rules:()=>stRules(),load:()=>stLoadStarter(),project:()=>projectData(),catalog:()=>ST_BUILDINGS,
  canBuild:(kind,x,z)=>stCanBuild(kind,x,z),
  pointScreen:(x,z)=>{const point=new THREE.Vector3(x,0,z).project(camera),rect=$('viewport').getBoundingClientRect();return {x:rect.left+(point.x+1)*rect.width/2,y:rect.top+(1-point.y)*rect.height/2,visible:point.z>=-1&&point.z<=1&&Math.abs(point.x)<=1&&Math.abs(point.y)<=1};},
  frame:()=>stFrameMap(),focus:(position)=>stCameraFocus(position)
};
