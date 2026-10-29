// Native project data is the starter's authority; gameplay owns only its session.
const ST_TYPES=['st-sheep','st-wolf','st-farm','st-income','st-fort','st-pen','st-tree','st-rock','st-pond','st-shop','st-meadow','st-thorn','st-wall','st-ramp','st-totem','st-road','st-grass','st-earth','st-zone'];
for(const type of ST_TYPES)ASSET_LIBRARY.push({id:type,name:type.slice(3).replace(/\b\w/g,letter=>letter.toUpperCase())+' · Sheep Tag',path:'/Engine/SheepTag',desc:'Editable Sheep Tag map piece; place, transform and bake before Play.'});
let stAuthorBaseline=null,stEditorViewSnapshot=null;
const ST_ARCHIVE_RULE_DEFAULTS=Object.freeze({
  duration:1200,headstart:30,bounds:40,startGold:80,role:'sheep',preset:'classic',buildSnap:.15,
  sheepSpeed:5.4,wolfSpeed:7.2,wolfDamage:85,attackInterval:.65,farmHp:180,incomeHp:240,fortHp:650,
  sheepRadius:.27,wolfRadius:.68,houseLimit:28,fogMode:'team',sheepVision:18,wolfVision:20,
  rescueProtection:3,rescueHold:.6,thorns:false,totems:false,elevated:false,split:false,events:false,
  thornChance:.35,thornDuration:15,thornCooldown:6,scentInterval:2,densityRadius:8,totemRadius:5.5,
  fadeSeconds:3,revealSeconds:2,totemLimit:'once',totemCooldown:120,wallCost:45,rampCost:55,
  wallHp:360,rampHp:300,wallHeight:3.3,wolvesUseRamps:true,splitUnlock:2,progressionSeconds:45,
  rescueXp:30,splitCooldown:30,splitLifetime:5,eventInterval:150,eventWarning:8,eventDuration:15,
  eventPool:['pressure','fog','supply'],seed:0,permittedStructures:['st-farm','st-income','st-fort','st-wall','st-ramp']
});
function stCleanRules(value={}){
  if(!value||typeof value!=='object'||Array.isArray(value))value={};
  const defaults=ST_ARCHIVE_RULE_DEFAULTS;
  const number=(key,min,max)=>Math.min(max,Math.max(min,Number.isFinite(Number(value[key]))&&value[key]!==null&&value[key]!==''?Number(value[key]):defaults[key]));
  const choice=(key,options)=>options.includes(value[key])?value[key]:defaults[key];
  const flag=key=>typeof value[key]==='boolean'?value[key]:defaults[key];
  const result={duration:number('duration',30,3600),headstart:number('headstart',0,120),bounds:number('bounds',16,80),
    startGold:number('startGold',0,1000),role:choice('role',['sheep','wolf']),preset:choice('preset',['classic','archive']),
    buildSnap:Number(value.buildSnap)===3?3:.15,sheepSpeed:number('sheepSpeed',2,10),wolfSpeed:number('wolfSpeed',2,12),
    wolfDamage:number('wolfDamage',20,200),attackInterval:number('attackInterval',.25,2),farmHp:number('farmHp',80,600),
    incomeHp:number('incomeHp',100,800),fortHp:number('fortHp',200,1600),sheepRadius:number('sheepRadius',.2,.45),
    wolfRadius:number('wolfRadius',.5,1),houseLimit:Math.round(number('houseLimit',9,40)),fogMode:choice('fogMode',['team','solo','off']),
    sheepVision:number('sheepVision',6,40),wolfVision:number('wolfVision',6,40),rescueProtection:number('rescueProtection',0,8),
    rescueHold:number('rescueHold',.2,3),thorns:flag('thorns'),totems:flag('totems'),elevated:flag('elevated'),split:flag('split'),events:flag('events'),
    thornChance:number('thornChance',0,1),thornDuration:number('thornDuration',2,30),thornCooldown:number('thornCooldown',1,30),
    scentInterval:number('scentInterval',1,5),densityRadius:number('densityRadius',5,14),totemRadius:number('totemRadius',3,10),
    fadeSeconds:number('fadeSeconds',.5,8),revealSeconds:number('revealSeconds',.5,8),totemLimit:choice('totemLimit',['once','cooldown']),
    totemCooldown:number('totemCooldown',15,900),wallCost:number('wallCost',0,200),rampCost:number('rampCost',0,200),
    wallHp:number('wallHp',100,1200),rampHp:number('rampHp',100,1000),wallHeight:number('wallHeight',2.5,4.5),wolvesUseRamps:flag('wolvesUseRamps'),
    splitUnlock:Math.round(number('splitUnlock',2,4)),progressionSeconds:number('progressionSeconds',5,180),rescueXp:number('rescueXp',0,100),
    splitCooldown:number('splitCooldown',5,120),splitLifetime:number('splitLifetime',2,12),eventInterval:number('eventInterval',30,900),
    eventWarning:number('eventWarning',5,20),eventDuration:number('eventDuration',5,45),seed:Math.round(number('seed',0,2147483647))};
  result.headstart=Math.min(result.duration,result.headstart);
  // Disruptive rounds cannot overlap their announced warning and recovery.
  result.eventInterval=Math.max(result.eventInterval,result.eventWarning+result.eventDuration+15);
  const pool=Array.isArray(value.eventPool)?value.eventPool:defaults.eventPool;
  result.eventPool=[...new Set(pool.filter(kind=>defaults.eventPool.includes(kind)))];
  if(!result.eventPool.length)result.events=false;
  const allow=Array.isArray(value.permittedStructures)?value.permittedStructures:defaults.permittedStructures;
  const aliases={farm:'st-farm',income:'st-income',fort:'st-fort',wall:'st-wall',ramp:'st-ramp'};
  result.permittedStructures=[...new Set(allow.map(kind=>aliases[kind]||kind).filter(kind=>defaults.permittedStructures.includes(kind)))];
  return result;
}
function stRules(){return stCleanRules(currentProject.sheepTag||{});}
// Check only occupied starting space. A legal pocket need not have an exit:
// closing that pocket later remains a player's tactical choice.
function stAuthoredMapPreflight({rules=stRules(),pieces=[],requireRoster=true}={}){
  const active=pieces.filter(p=>p.active!==false),errors=[],obstacles=[];
  const footprint=(p,hx,hz)=>stFootprint(p.position[0],p.position[2],hx*Math.abs(p.scale?.[0]??1),hz*Math.abs(p.scale?.[2]??1),p.rotation?.[1]||0,p.id);
  for(const p of active){
    if(['st-tree','st-rock'].includes(p.type))obstacles.push({id:p.id,x:p.position[0],z:p.position[2],radius:(p.type==='st-tree'?1.7:1.8)*Math.max(Math.abs(p.scale?.[0]??1),Math.abs(p.scale?.[2]??1))});
    else if(['st-pond','st-shop'].includes(p.type))obstacles.push(footprint(p,p.type==='st-pond'?3:1.5,p.type==='st-pond'?3:1.5));
    else if(ST_BUILDINGS[p.type])obstacles.push(footprint(p,1.2,['st-wall','st-ramp'].includes(p.type)?3:1.2));
  }
  const spawns=active.filter(p=>['st-sheep','st-wolf'].includes(p.type)),pens=active.filter(p=>p.type==='st-pen');
  if(requireRoster){
    if(!spawns.some(p=>p.type==='st-sheep'))errors.push('Add and bake at least one visible sheep spawn.');
    if(!spawns.some(p=>p.type==='st-wolf'))errors.push('Add and bake at least one visible wolf spawn.');
    if(pens.length!==1)errors.push('Use exactly one visible, baked Spirit Pen.');
  }
  const context={rules,obstacles};
  for(const p of spawns){
    const radius=stUnitRadius(p.type==='st-wolf'?'wolf':'sheep',rules),[x,y,z]=p.position;
    if(![x,y,z].every(Number.isFinite)||stContextBlocked(context,x,z,radius))errors.push((p.name||p.type.slice(3))+' starts inside an obstacle or beyond the map boundary. Move this spawn to clear ground.');
  }
  for(const p of pens){
    const area=footprint(p,5,5);
    if(area.corners.some(([x,z])=>!Number.isFinite(x)||!Number.isFinite(z)||Math.abs(x)>rules.bounds||Math.abs(z)>rules.bounds))errors.push('The whole Spirit Pen must fit inside the map boundary.');
    if(stContextBlocked(context,p.position[0],p.position[2],rules.sheepRadius))errors.push('The Spirit Pen center is blocked. Clear its ground before Play.');
  }
  return {ok:!errors.length,reason:errors[0]||'',errors};
}
const stNativeApplyProjectMeta=applyProjectMeta;
const ST_NATIVE_VIEW_LIMITS={distance:orbit.maxDistance,far:perspectiveCamera.far};
applyProjectMeta=function(meta={}){
  stNativeApplyProjectMeta(meta);
  if(currentProject.kind==='sheep-tag')currentProject.sheepTag=stCleanRules(currentProject.sheepTag);
  else{orbit.maxDistance=ST_NATIVE_VIEW_LIMITS.distance;perspectiveCamera.far=ST_NATIVE_VIEW_LIMITS.far;perspectiveCamera.updateProjectionMatrix();if(stCreator.open)stCreatorClose();}
};
function stConfigureRules(update={}){
  if(playing||simulating)return {ok:false,reason:'Stop the match before editing its rules.'};
  if(currentProject.kind!=='sheep-tag')return {ok:false,reason:'Open a Sheep Tag project first.'};
  const previous=stRules(),patch=update&&typeof update==='object'&&!Array.isArray(update)?{...update}:{};
  if((patch.preset==='classic'||patch.preset==='archive')&&patch.preset!==previous.preset){
    for(const flag of ['thorns','totems','elevated','split'])if(!Object.prototype.hasOwnProperty.call(patch,flag))patch[flag]=patch.preset==='archive';
    if(!Object.prototype.hasOwnProperty.call(patch,'events'))patch.events=false;
  }
  beginTransaction('Edit Sheep Tag rules');currentProject.sheepTag=stCleanRules({...previous,...patch});
  commitTransaction('Edit Sheep Tag rules');return {ok:true,rules:stRules()};
}
function stFrameMap(){
  const priorLimit=orbit.maxDistance;orbit.maxDistance=Infinity;
  setCameraView('perspective');perspectiveCamera.fov=50;perspectiveCamera.updateProjectionMatrix();
  perspectiveCamera.position.set(0,82,65);orbit.target.set(0,0,0);perspectiveCamera.lookAt(orbit.target);orbit.update();
  // Portrait canvases need more distance to show both sides of the meadow.
  const extent=stRules().bounds;
  for(let pass=0;pass<6;pass++){
    perspectiveCamera.updateMatrixWorld();let fit=0;
    for(const x of [-extent,extent])for(const z of [-extent,extent]){const p=new THREE.Vector3(x,0,z).project(perspectiveCamera);fit=Math.max(fit,Math.abs(p.x),Math.abs(p.y));}
    if(fit<=.94)break;
    perspectiveCamera.position.multiplyScalar(fit/.9);perspectiveCamera.lookAt(orbit.target);orbit.update();
  }
  const distance=perspectiveCamera.position.distanceTo(orbit.target);
  orbit.maxDistance=Math.max(priorLimit,distance*1.25);perspectiveCamera.far=Math.max(300,distance+extent*4);perspectiveCamera.updateProjectionMatrix();
  if(scene.fog?.isFog){scene.fog.near=Math.max(130,distance+extent);scene.fog.far=scene.fog.near+extent*3;}
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
  const preflight=stAuthoredMapPreflight({pieces:stCreatorNativePreflightPieces()});
  if(!preflight.ok){toast(preflight.reason);editorLog(preflight.reason,'error');return false;}
  if(typeof stCreatorBeforePlay==='function')stCreatorBeforePlay();
  closeTeleportMenu(false);closeWorkspacePanel(false);stAuthorBaseline=structuredClone(projectData());
  stEditorViewSnapshot={position:camera.position.clone(),quaternion:camera.quaternion.clone(),up:camera.up.clone(),target:orbit.target.clone(),fov:perspectiveCamera.fov,fog:scene.fog?.clone()||null};
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
  if(view){camera.position.copy(view.position);camera.quaternion.copy(view.quaternion);camera.up.copy(view.up);orbit.target.copy(view.target);perspectiveCamera.fov=view.fov;scene.fog=view.fog;perspectiveCamera.updateProjectionMatrix();orbit.update();}
  if(typeof stRefreshHUD==='function'&&$('sheepTagRulesBtn'))stRefreshHUD(true);
  if(typeof stCreatorAfterStop==='function')stCreatorAfterStop();
  return result;
};
const stNativeSessionButtons=setSessionButtons;
setSessionButtons=function(){stNativeSessionButtons();if(stSession)$('keepBtn').classList.add('hidden');};
// Existing listeners referenced the original function object; rebind the native buttons.
$('playBtn').onclick=()=>beginPlay();$('simulateBtn').onclick=()=>beginSimulate();$('stopBtn').onclick=()=>stopSession();
$('playFromHereBtn').onclick=()=>{if(currentProject.kind==='sheep-tag')beginPlay();else if(selected)beginPlay(selected.getWorldPosition(new THREE.Vector3()));};
function stRenderStatus(id=null){
  const inspect=(entity)=>{
    const object=entity.spirit||entity.actor||entity.mesh;if(!object)return null;
    object.updateWorldMatrix(true,true);const p=object.getWorldPosition(new THREE.Vector3());
    const materials=new Set(),meshes=[];
    object.traverse(node=>{
      if(node.isMesh||node.isSprite){
        const list=Array.isArray(node.material)?node.material:[node.material];for(const m of list)if(m)materials.add(m);
        meshes.push({name:node.name||'',type:node.isSprite?'Sprite':node.geometry?.type||'',vertices:node.geometry?.attributes?.position?.count||0,
          colors:list.filter(m=>m?.color).map(m=>m.color.getHexString())});
      }
    });
    const opacity=[...materials].map(m=>Number.isFinite(m.opacity)?m.opacity:1);
    const bounds=new THREE.Box3().setFromObject(object),size=bounds.getSize(new THREE.Vector3());
    return {id:entity.id,kind:entity.captured?'wisp':entity.kind,visible:walkingObjectVisible(object),bodyVisible:entity.actor?walkingObjectVisible(entity.actor):walkingObjectVisible(object),
      pos:p.toArray(),scale:object.getWorldScale(new THREE.Vector3()).toArray(),bounds:size.toArray(),meshCount:meshes.length,
      opacity:opacity.length?Math.min(...opacity):1,opacityMin:opacity.length?Math.min(...opacity):1,opacityMax:opacity.length?Math.max(...opacity):1,
      geometrySignature:JSON.stringify(meshes.map(({name,type,vertices})=>({name,type,vertices}))),meshes};
  };
  const units=stSession?stSession.units.map(inspect).filter(Boolean):[];
  const buildings=stSession?stSession.buildings.filter(b=>b.hp>0).map(inspect).filter(Boolean):[];
  if(id)return [...units,...buildings].find(item=>item.id===id)||null;
  return {active:!!stSession,units,buildings,minimap:typeof stUiStatus==='function'?stUiStatus().minimap:null};
}
window.SWYRL_ENGINE_SHEEP_TAG={
  sourceScene:ST_ARCHIVE_SOURCE_SCENE,status:()=>stStatus(),renderStatus:(id)=>stRenderStatus(id),uiStatus:()=>typeof stUiStatus==='function'?stUiStatus():null,command:(action,payload={})=>stCommand(action,payload),configure:(update)=>stConfigureRules(update),
  viewStatus:()=>stViewStatus(),previewPath:(payload)=>stInspectPath(payload),archiveDefaults:()=>structuredClone(ST_ARCHIVE_RULE_DEFAULTS),
  validateStarts:()=>stAuthoredMapPreflight({pieces:stCreatorNativePreflightPieces()}),
  rules:()=>stRules(),load:()=>stLoadStarter(),project:()=>projectData(),catalog:()=>ST_BUILDINGS,
  canBuild:(kind,x,z,rotation=0)=>stCanBuild(kind,x,z,null,rotation),
  pointScreen:(x,z,y=0)=>{const point=new THREE.Vector3(x,y,z).project(camera),rect=$('viewport').getBoundingClientRect();return {x:rect.left+(point.x+1)*rect.width/2,y:rect.top+(1-point.y)*rect.height/2,visible:point.z>=-1&&point.z<=1&&Math.abs(point.x)<=1&&Math.abs(point.y)<=1};},
  frame:()=>stFrameMap(),focus:(position)=>stCameraFocus(position)
};
