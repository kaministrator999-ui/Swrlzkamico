// Opt-in, session-owned evidence. Recording must never drive gameplay, change
// project data, or replace the player's fog-filtered controls with omniscience.
const ST_RUN_SCHEMA='swyrl-editor-play-run-v1';
const ST_RUN_PREF_KEY='swyrl-editor-play-run-settings-v1';
const stRunState={settings:{enabled:false,cadence:'full'},active:null,completed:[],error:null};
const stRunRoot=typeof window!=='undefined'?window:globalThis;
let stRunIdSerial=0;
try{
  const saved=JSON.parse(localStorage.getItem(ST_RUN_PREF_KEY)||'null');
  if(saved&&typeof saved.enabled==='boolean')stRunState.settings.enabled=saved.enabled;
  if(saved&&[.1,.5].includes(Number(saved.cadence)))stRunState.settings.cadence=Number(saved.cadence);
}catch(error){/* A device without storage can still record and export. */}

function stRunNumber(value){return Number.isFinite(Number(value))?Math.round(Number(value)*1e5)/1e5:null;}
function stRunVector(value){return Array.from(value||[],stRunNumber);}
function stRunSafe(value,seen=new WeakSet()){
  if(value===null||typeof value==='string'||typeof value==='boolean')return value;
  if(typeof value==='number')return stRunNumber(value);
  if(typeof value!=='object')return null;
  if(seen.has(value))return '[circular]';seen.add(value);
  let result;
  if(Array.isArray(value)||ArrayBuffer.isView(value))result=Array.from(value,item=>stRunSafe(item,seen));
  else if(value instanceof Map)result=Object.fromEntries([...value].map(([key,item])=>[String(key),stRunSafe(item,seen)]));
  else if(value instanceof Set)result=[...value].map(item=>stRunSafe(item,seen));
  else{result={};for(const key of Object.keys(value))if(!['__proto__','constructor','prototype'].includes(key))result[key]=stRunSafe(value[key],seen);}
  seen.delete(value);return result;
}
function stRunClone(value){return JSON.parse(JSON.stringify(value));}
function stRunTime(run=stRunState.active){return stRunNumber(run?.mode==='sheep-tag'?stSession?.elapsed??run.duration:run?._elapsed??run?.duration??0);}
function stRunParts(run,object){
  let catalog=run._parts.get(object);
  if(!catalog){
    const nodes=[],parts=[],index=new Map();object.traverse(node=>{index.set(node,nodes.length);nodes.push(node);});
    for(const node of nodes)parts.push({name:node.name||node.type,parent:index.get(node.parent)??-1,type:node.type,geometry:node.geometry?.type||null,position:stRunVector(node.position.toArray()),quaternion:stRunVector(node.quaternion.toArray()),scale:stRunVector(node.scale.toArray()),visible:node.visible,opacity:stRunOpacity(node)});
    catalog={nodes,parts};run._parts.set(object,catalog);
  }
  const partTransforms={};catalog.nodes.forEach((node,i)=>{const now={position:stRunVector(node.position.toArray()),quaternion:stRunVector(node.quaternion.toArray()),scale:stRunVector(node.scale.toArray()),visible:node.visible,opacity:stRunOpacity(node)},change=stRunDifference(catalog.parts[i],now);
    delete change.name;delete change.parent;delete change.type;delete change.geometry;if(Object.keys(change).length)partTransforms[i]=change;});
  return {parts:catalog.parts,partTransforms};
}
function stRunCollectProject(run){
  const entities={},frustum=stRunFrustum(),owned=new Set([...actors,...liveUnits]);
  const extras=scene.children.filter(object=>!owned.has(object)&&!object.isCamera&&(object.isMesh||object.isSprite||object.isPoints||object.isLine||object.isLight));
  const all=[...owned,...extras];
  for(const object of all){
    const id=object.userData.id||stRunEffectId(run,object,'runtime'),spec=run._catalog[id]||{},data=object.userData;
    run._rendererObjects.set(id,object);
    entities[id]=stRunBaseEntity(run,id,object,{name:object.name||spec.name||id,type:data.actorType||spec.type||object.type,kind:data.actorType||spec.type||object.type,origin:actors.includes(object)?'authored':extras.includes(object)?'scene':'runtime',baked:!!data.baked,authoredVisible:spec.visible!==false&&spec.manualVisible!==false,playerVisible:stRunObjectVisible(object),destroyed:!!data.dead,hp:Number.isFinite(data.hp)?stRunNumber(data.hp):null,maxHp:Number.isFinite(data.maxHp)?stRunNumber(data.maxHp):null,team:data.team||null,layers:[...(spec.editorLayerIds||[])],tags:[...(spec.tags||[])],components:[...(spec.components||[])],motion:stRunSafe(data.motion||data.animation||null),lighting:object.isLight?{intensity:stRunNumber(object.intensity),color:'#'+object.color.getHexString(),distance:stRunNumber(object.distance)}:null,...stRunParts(run,object)},frustum);
  }
  const hero=heroActor();
  return {entities,camera:stRunCamera(),game:{kind:currentProject.kind,project:currentProject.name,role:'spectator',paused:!!paused,winner:null,controlledId:hero?.userData.id||null,heroVelocity:stRunVector(heroVel.toArray()),input:{move:{x:fpMove.x,y:fpMove.y},look:{x:fpLook.x,y:fpLook.y},keys:[...keys].sort()},runtimeCount:liveUnits.length,cinematic:typeof animeCine!=='undefined'&&animeCine?.active?{elapsed:stRunNumber(animeCine.elapsed),duration:stRunNumber(animeCine.duration),rate:animeCine.rate??1,chapter:typeof storyBeat==='function'?storyBeat(animeCine.elapsed)?.title||null:null}:null}};
}
function stRunAfterTick(dt){
  const run=stRunState.active;if(!run||run.mode==='sheep-tag')return;
  stRunGuard(()=>{stRunPause();if(playing&&!paused&&!workspacePanelOpen){run._tick++;run._elapsed+=Math.max(0,Number(dt)||0);run.duration=stRunTime(run);stRunCapture(false,dt);}stRunRefreshUI();});
}
function stRunLocked(){return !!(typeof playing!=='undefined'&&playing||typeof simulating!=='undefined'&&simulating||stRunState.active);}
function stRunConfigure(update={}){
  if(stRunLocked())return {ok:false,reason:'Stop Play or Simulate before changing recording settings.',settings:{...stRunState.settings}};
  if(!update||typeof update!=='object'||Array.isArray(update))return {ok:false,reason:'Choose valid recording settings.'};
  const next={...stRunState.settings};
  if(Object.hasOwn(update,'enabled')){if(typeof update.enabled!=='boolean')return {ok:false,reason:'Recording enabled must be true or false.'};next.enabled=update.enabled;}
  if(Object.hasOwn(update,'cadence')){
    const cadence=update.cadence==='full'?'full':Number(update.cadence);
    if(cadence!=='full'&&![.1,.5].includes(cadence))return {ok:false,reason:'Choose every update, 0.1 seconds, or 0.5 seconds.'};next.cadence=cadence;
  }
  stRunState.settings=next;try{localStorage.setItem(ST_RUN_PREF_KEY,JSON.stringify(next));}catch(error){}
  return {ok:true,settings:{...next}};
}
function stRunSummary(run){return {id:run.id,startedAt:run.startedAt,duration:run.duration,complete:run.complete,endReason:run.endReason,frameCount:run.frames.length,eventCount:run.events.length,observationCount:run.observations.length};}
function stRunStatus(){return {settings:{...stRunState.settings},stateLocked:stRunLocked(),active:stRunState.active?stRunSummary(stRunState.active):null,runs:stRunState.completed.map(stRunSummary),error:stRunState.error};}
function stRunResolve(run=null){
  if(run&&typeof run==='object')return run;
  if(typeof run==='string')return stRunState.active?.id===run?stRunState.active:stRunState.completed.find(item=>item.id===run)||null;
  return stRunState.active||stRunState.completed[0]||null;
}
function stRunPublic(run){const result={};for(const key of Object.keys(run))if(!key.startsWith('_'))result[key]=run[key];return result;}
function stRunData(id=null){const run=stRunResolve(id);return run?stRunClone(stRunPublic(run)):null;}
function stRunGuard(action){
  try{return action();}catch(error){
    const message=String(error?.message||error);stRunState.error=message;
    const run=stRunState.active;if(run){run.complete=false;run.capture.incomplete=true;run.capture.errors.push({tick:run._tick,t:stRunNumber(stRunTime(run)),message});
      try{run.events.push({seq:++run._eventSerial,tick:run._tick,t:stRunNumber(stRunTime(run)),type:'recording-error',details:{message}});}catch(appendError){}
    }return null;
  }
}
function stRunTransform(object){
  if(!object)return {position:[0,0,0],quaternion:[0,0,0,1],scale:[1,1,1]};
  object.updateWorldMatrix(true,false);
  return {position:stRunVector(object.getWorldPosition(new THREE.Vector3()).toArray()),quaternion:stRunVector(object.getWorldQuaternion(new THREE.Quaternion()).toArray()),scale:stRunVector(object.getWorldScale(new THREE.Vector3()).toArray())};
}
function stRunObjectVisible(object){return !!object&&(typeof walkingObjectVisible==='function'?!!walkingObjectVisible(object):object.visible!==false);}
function stRunAppearance(run,object){
  if(!object)return {colors:[],opacityMin:0,opacityMax:0,meshCount:0,shape:[],size:[0,0,0]};
  let cached=run._appearances.get(object);if(cached)return cached;
  const colors=new Set(),opacity=[],shape=[];object.updateWorldMatrix(true,true);
  object.traverse(node=>{if(!node.isMesh&&!node.isSprite)return;const materials=Array.isArray(node.material)?node.material:[node.material];
    for(const material of materials){if(material?.color)colors.add('#'+material.color.getHexString());if(material)opacity.push(Number.isFinite(material.opacity)?material.opacity:1);}
    shape.push({name:node.name||'',geometry:node.isSprite?'Sprite':node.geometry?.type||'',vertices:node.geometry?.attributes?.position?.count||0});
  });
  const box=new THREE.Box3().setFromObject(object),size=box.isEmpty()?[0,0,0]:stRunVector(box.getSize(new THREE.Vector3()).toArray());
  cached={colors:[...colors].sort(),opacityMin:stRunNumber(opacity.length?Math.min(...opacity):1),opacityMax:stRunNumber(opacity.length?Math.max(...opacity):1),meshCount:shape.length,shape,size};run._appearances.set(object,cached);return cached;
}
function stRunOpacity(object){
  let min=1,max=0,found=false;if(object)object.traverse(node=>{for(const material of Array.isArray(node.material)?node.material:[node.material])if(material){const n=Number.isFinite(material.opacity)?material.opacity:1;min=Math.min(min,n);max=Math.max(max,n);found=true;}});
  return found?[stRunNumber(min),stRunNumber(max)]:[0,0];
}
function stRunLimbs(run,unit){
  let catalog=run._limbs.get(unit.actor);
  if(!catalog){
    const limbs={},order=[];for(const pivot of unit.pivots||[]){const node=pivot.node,name=node.name||'part-'+order.length,axis=node.name==='stTail'?'y':'x';order.push(name);
      limbs[name]={localPosition:stRunVector(node.position.toArray()),localRotation:stRunVector(pivot.rotation.toArray().slice(0,3)),localScale:stRunVector(node.scale.toArray()),parent:node.parent?.name||'',axis};
    }catalog={limbs,limbOrder:order};run._limbs.set(unit.actor,catalog);
  }
  return {...catalog,limbAngles:(unit.pivots||[]).map(pivot=>stRunNumber(pivot.node.rotation[pivot.node.name==='stTail'?'y':'x']))};
}
function stRunEffectId(run,object,prefix='effect'){
  if(!object)return prefix;let id=run._effectIds.get(object);if(!id){id='st-observation-'+prefix+'-'+(++run._effectSerial);run._effectIds.set(object,id);}return id;
}
function stRunCamera(){
  if(typeof camera==='undefined'||!camera)return null;
  const result={...stRunTransform(camera),type:camera.isPerspectiveCamera?'perspective':'orthographic',fov:stRunNumber(camera.fov),aspect:stRunNumber(camera.aspect),near:stRunNumber(camera.near),far:stRunNumber(camera.far)};
  if(typeof orbit!=='undefined'&&orbit?.target)result.target=stRunVector(orbit.target.toArray());return result;
}
function stRunFrustum(){
  if(typeof camera==='undefined'||!camera)return null;camera.updateMatrixWorld(true);
  return new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse));
}
function stRunInFrustum(object,frustum){
  if(!object||!frustum)return null;const box=new THREE.Box3().setFromObject(object);return !box.isEmpty()&&frustum.intersectsBox(box);
}
function stRunBaseEntity(run,id,object,extra={},frustum=null){
  const appearance=stRunAppearance(run,object),transform=stRunTransform(object),opacity=stRunOpacity(object);
  const box=object?new THREE.Box3().setFromObject(object):null,hasBounds=box&&!box.isEmpty();
  run._rendererObjects.set(id,object);
  return {id,...transform,size:[...appearance.size],worldBounds:hasBounds?{min:stRunVector(box.min.toArray()),max:stRunVector(box.max.toArray())}:null,appearance,opacity,visible:stRunObjectVisible(object),inFrustum:hasBounds&&frustum?frustum.intersectsBox(box):null,floor:stRunNumber(terrainHeight(transform.position[0],transform.position[2])),...extra};
}
function stRunCollect(run){
  if(run.mode!=='sheep-tag')return stRunCollectProject(run);
  const s=stSession;if(!s)throw Error('The native Play session is unavailable to the recorder.');
  const entities={},frustum=stRunFrustum(),byId=new Map(actors.map(actor=>[actor.userData.id,actor]));
  for(const [id,spec]of Object.entries(run._catalog)){
    const object=byId.get(id);entities[id]=stRunBaseEntity(run,id,object,{name:spec.name||spec.type||id,type:spec.type||'actor',kind:spec.type||'actor',origin:'authored',baked:spec.baked!==false,authoredVisible:spec.visible!==false&&spec.manualVisible!==false,manualVisible:spec.manualVisible!==false,layers:[...(spec.editorLayerIds||[])],tags:[...(spec.tags||[])],playerVisible:stRunObjectVisible(object)},frustum);
  }
  for(const unit of s.units){
    const object=unit.spirit||unit.actor,existing=entities[unit.id]||{},transform=stRunBaseEntity(run,unit.id,object,{},frustum);
    entities[unit.id]={...existing,...transform,name:unit.name||unit.id,type:unit.captured?'st-wisp':unit.kind==='wolf'?'st-wolf':'st-sheep',kind:unit.captured?'wisp':unit.kind,origin:unit.isIllusion?'runtime':existing.origin||'runtime',baked:existing.baked??true,authoredVisible:existing.authoredVisible??true,playerVisible:!!stSeenByRole(unit),captured:!!unit.captured,isIllusion:!!unit.isIllusion,sourceId:unit.sourceId||null,bodyVisible:stRunObjectVisible(unit.actor),bodyTransform:unit.captured?stRunTransform(unit.actor):null,floor:stRunNumber(terrainHeight(unit.pos.x,unit.pos.z)),onUpper:!!unit.archiveOnUpper,falling:!!unit.archiveFalling,order:stRunSafe(unit.order||unit.spiritOrder&&{action:'move',...unit.spiritOrder}||null),controlled:unit.id===s.controlledId,selected:unit.id===s.selectedId,radius:stRunNumber(stUnitRadius(unit)),speed:stRunNumber(unit.speed),damage:stRunNumber(unit.damage),level:unit.level,resources:stRunNumber(s.resources[unit.id]||0),concealment:stRunNumber(unit.concealAmount||0),protectionUntil:stRunNumber(unit.invulnerableUntil||0),scentUntil:stRunNumber(unit.archiveScentUntil||0),expiresAt:stRunNumber(unit.archiveExpires),progression:{xp:stRunNumber(unit.archiveXp||0),level:unit.archiveLevel||unit.level,splitAt:stRunNumber(unit.archiveSplitAt),totemUsed:!!unit.archiveTotemUsed,totemAt:stRunNumber(unit.archiveTotemAt)},ai:{intent:unit.aiIntent||'',base:unit.base?stRunVector(unit.base.toArray()):null,lastKnown:[...(unit.memory?.values()||[])].map(item=>({id:item.id,position:stRunVector(item.pos.toArray()),seenAt:stRunNumber(item.at)}))},traffic:unit.traffic?{mode:unit.traffic.mode,blockedBy:unit.traffic.blockedBy||null,yieldTarget:unit.traffic.yieldTarget?stRunVector(unit.traffic.yieldTarget.toArray()):null}:null,route:unit.archiveRoute?{action:unit.archiveRoute.action||null,target:unit.archiveRoute.target?stRunVector(unit.archiveRoute.target.toArray()):null,index:unit.archiveRoute.index??unit.archiveRoute.cursor??null,waypoints:(unit.archiveRoute.waypoints||[]).map(point=>({position:stRunVector((point.pos||point.point||point).toArray?.()||[]),surfaceId:point.surfaceId||null}))}:null,...stRunLimbs(run,unit)};
  }
  for(const building of s.buildings){
    const existing=entities[building.id]||{},alive=building.hp>0,visual=alive?stRunBaseEntity(run,building.id,building.mesh,{},frustum):run._last?.entities[building.id]||stRunBaseEntity(run,building.id,building.mesh,{},frustum);
    if(!alive)run._rendererObjects.set(building.id,null);
    entities[building.id]={...existing,...visual,name:ST_BUILDINGS[building.kind]?.name||building.kind,type:building.kind,kind:building.kind,origin:building.authored?'authored':'runtime',baked:true,authoredVisible:existing.authoredVisible??true,position:stRunVector(building.pos.toArray()),visible:alive&&stRunObjectVisible(building.mesh),inFrustum:alive?visual.inFrustum:false,playerVisible:alive&&!!stSeenByRole(building),destroyed:!alive,hp:stRunNumber(building.hp),maxHp:stRunNumber(building.maxHp),progress:stRunNumber(building.progress),owner:building.owner||null,level:building.level,income:stRunNumber(building.income),cost:stRunNumber(building.cost),rotation:stRunNumber(building.rotation),footprint:{halfX:stRunNumber(building.halfX),halfZ:stRunNumber(building.halfZ),localHalfX:stRunNumber(building.localHalfX),localHalfZ:stRunNumber(building.localHalfZ),corners:stRunSafe(building.corners)},floor:stRunNumber(terrainHeight(building.pos.x,building.pos.z)),selected:building.id===s.selectedId};
  }
  for(const effect of s.archive?.effects||[]){
    const clue=s.archive.scentClues.find(item=>item.mesh===effect),supply=s.archive.supply?.mesh===effect?s.archive.supply:null;
    const id=stRunEffectId(run,effect,clue?'scent':supply?'supply':'effect');entities[id]=stRunBaseEntity(run,id,effect,{name:clue?'Approximate thorn scent':supply?'Supply crate':effect.name||'Magical effect',type:clue?'scent-clue':supply?'supply':'effect',kind:clue?'scent-clue':supply?'supply':'effect',origin:'runtime',baked:false,authoredVisible:true,playerVisible:stRunObjectVisible(effect),radius:clue?stRunNumber(clue.radius):null,expiresAt:clue?stRunNumber(clue.expires):null,approximate:!!clue,floor:stRunNumber(terrainHeight(effect.position.x,effect.position.z))},frustum);
  }
  const view=typeof stViewStatus==='function'?stViewStatus():null;
  const game={role:s.role,simulate:s.simulate,winner:s.winner||null,message:s.message||'',selectedId:s.selectedId,controlledId:s.controlledId,resources:stRunSafe(s.resources),rules:stRunSafe(s.rules),headstartReleased:s.elapsed>=s.rules.headstart,paused:!!paused,navVersion:s.navVersion,houseLanes:stRunSafe(s.lastBuilderExit||null),archive:s.archive?{seed:s.archive.seed,event:stRunSafe(s.archive.event),damageMultiplier:stRunNumber(s.archive.damageMultiplier),visionMultiplier:stRunNumber(s.archive.visionMultiplier),nextEvent:stRunNumber(s.archive.nextEvent)}:null,playerVision:{scope:s.simulate?'all':s.rules.fogMode,visibleIds:view?.units?.map(unit=>unit.id)||[],visibleBuildingIds:view?.buildings?.map(building=>building.id)||[],lastKnown:stRunSafe(view?.lastKnown||[]),fog:view?.fog?stRunSafe(view.fog):null}};
  return {entities,camera:stRunCamera(),game};
}
function stRunDifference(before,after){
  const patch={};for(const [key,value]of Object.entries(after))if(before?.[key]!==value&&JSON.stringify(before?.[key])!==JSON.stringify(value))patch[key]=value;
  for(const key of Object.keys(before||{}))if(!Object.hasOwn(after,key))patch[key]=null;return patch;
}
function stRunEvent(type,actorId=null,details={}){
  const run=stRunState.active;if(!run)return;const event={seq:++run._eventSerial,tick:run._tick,t:stRunNumber(stRunTime(run)),type,details:stRunSafe(details)};
  if(actorId)event.actorId=String(actorId);run.events.push(event);run._meaningful=true;return event;
}
function stRunNote(type,actorId=null,details={}){
  return stRunGuard(()=>{const event=stRunEvent(type,actorId,details);if(event&&!stRunState.active._inUpdate&&!stRunState.active._commandDepth)stRunCapture(true,0);return event;});
}
function stRunPause(){
  const run=stRunState.active;if(!run||run._paused===!!paused)return;run._paused=!!paused;stRunEvent(paused?'paused':'resumed',null,{wallTime:new Date().toISOString()});stRunCapture(true,0);
}
function stRunPostView(){
  const run=stRunState.active||stRunState._pendingFinished;if(!run?._last)return;
  const currentCamera=stRunCamera(),frustum=stRunFrustum(),frame=run.frames.at(-1),sameFrame=frame&&frame.tick===run._tick&&Math.abs(frame.t-run.duration)<1e-5;
  if(sameFrame){if(JSON.stringify(run._last.camera)!==JSON.stringify(currentCamera))frame.camera=currentCamera;run._last.camera=currentCamera;
    for(const [id,entity]of Object.entries(run._last.entities)){const object=run._rendererObjects.get(id),included=entity.destroyed?false:stRunInFrustum(object,frustum);if(included!==entity.inFrustum){entity.inFrustum=included;frame.patch[id]={...(frame.patch[id]||{}),inFrustum:included};}}
    const checkpoint=run.checkpoints.at(-1);if(checkpoint?.index===run.frames.length-1){checkpoint.camera=stRunClone(currentCamera);checkpoint.entities=stRunClone(run._last.entities);}
  }else if(!frame){run.initial.camera=currentCamera;for(const [id,entity]of Object.entries(run.initial.entities))entity.inFrustum=entity.destroyed?false:stRunInFrustum(run._rendererObjects.get(id),frustum);}
  if(stRunState._pendingFinished===run){stRunState._pendingFinished=null;run._rendererObjects.clear();run._observedSupply=null;}
}
function stRunDetect(run,before,after){
  if(run.mode!=='sheep-tag'){
    for(const [id,next]of Object.entries(after.entities)){
      const prior=before.entities[id];if(!prior){stRunEvent('entity-created',id,{type:next.type,position:next.position});continue;}
      if(!prior.destroyed&&next.destroyed)stRunEvent('entity-destroyed',id,{position:next.position});
      if(Number.isFinite(next.hp)&&prior.hp!==next.hp)stRunEvent('health-changed',id,{before:prior.hp,hp:next.hp});
    }
    for(const id of Object.keys(before.entities))if(!after.entities[id])stRunEvent('entity-removed',id);
    if(before.game.cinematic?.chapter!==after.game.cinematic?.chapter)stRunEvent('chapter-changed',null,after.game.cinematic||{});
  }
  for(const [id,next]of Object.entries(after.entities)){
    const previous=before.entities[id];if(!previous)continue;
    if(previous.progress<1&&next.progress===1)stRunEvent('construction-completed',id);
    if(previous.level!==next.level&&next.level)stRunEvent('level-changed',id,{before:previous.level,level:next.level});
    if(previous.onUpper!==next.onUpper)stRunEvent(next.onUpper?'upper-entered':'upper-left',id,{position:next.position});
    if(previous.falling!==next.falling)stRunEvent(next.falling?'fall-started':'fall-ended',id,{position:next.position});
    if(previous.traffic?.mode!==next.traffic?.mode&&next.traffic)stRunEvent('traffic-changed',id,next.traffic);
    if((previous.scentUntil||0)<(next.scentUntil||0))stRunEvent('thorn-scent-started',id,{until:next.scentUntil});
    if((previous.concealment>=.5)!==(next.concealment>=.5))stRunEvent('concealment-changed',id,{amount:next.concealment});
  }
  const oldEvent=before.game.archive?.event,newEvent=after.game.archive?.event;
  if(oldEvent?.kind!==newEvent?.kind||oldEvent?.state!==newEvent?.state)stRunEvent(newEvent?'event-'+newEvent.state:'event-ended',null,newEvent||oldEvent||{});
  if(!before.game.headstartReleased&&after.game.headstartReleased)stRunEvent('headstart-ended');
}
function stRunObservation(run,current,force=false){
  const t=stRunTime(run);if(!force&&t+1e-5<run._nextObservation&&!run._meaningful)return;
  const changed=[];for(const [id,entity]of Object.entries(current.entities))if(run.mode!=='sheep-tag'||entity.origin==='runtime'||['sheep','wolf','wisp'].includes(entity.kind)||ST_BUILDINGS[entity.type]){
    if(JSON.stringify(run._wordEntities[id])!==JSON.stringify(entity)){changed.push(stRunDescribe(entity,current.entities));run._wordEntities[id]=entity;}
  }
  for(const id of Object.keys(run._wordEntities))if(!Object.hasOwn(current.entities,id)){changed.push(id+' is no longer present.');delete run._wordEntities[id];}
  const text='At '+t+' simulation seconds; '+(current.game.winner?'winner: '+current.game.winner+'.':'role '+current.game.role+'.')+' '+(changed.length?changed.join('\n'):'No creature, structure, or effect changed since the previous observation.')+'\nStatic surroundings are retained in the initial catalog; full words at this time enumerate every object.';
  run.observations.push({tick:run._tick,t,text});run._nextObservation=Math.floor(t)+1;run._meaningful=false;
}
function stRunCapture(force=false,dt=0){
  const run=stRunState.active;if(!run||!playing||run.mode==='sheep-tag'&&!stSession)return null;
  const cadence=run.capture.cadence,t=stRunTime(run),due=cadence==='full'||t+1e-5>=run._nextFrame;
  if(!force&&!due&&!run._meaningful)return null;
  const current=stRunCollect(run),previous=run._last;stRunDetect(run,previous,current);
  const patch={};for(const [id,entity]of Object.entries(current.entities)){const change=stRunDifference(previous.entities[id],entity);if(Object.keys(change).length)patch[id]=change;}
  for(const id of Object.keys(previous.entities))if(!Object.hasOwn(current.entities,id))patch[id]=null;
  const frame={tick:run._tick,t,dt:stRunNumber(dt),patch};if(JSON.stringify(previous.camera)!==JSON.stringify(current.camera))frame.camera=current.camera;
  const game=stRunDifference(previous.game,current.game);if(Object.keys(game).length)frame.game=game;
  // Full cadence preserves even an update without a visible state change.
  run.frames.push(frame);run.duration=t;run._last=current;
  if(cadence!=='full'&&due)run._nextFrame=(Math.floor((t+1e-5)/cadence)+1)*cadence;
  if(t+1e-5>=run._nextCheckpoint){run.checkpoints.push({index:run.frames.length-1,t,...stRunClone(current)});run._nextCheckpoint=(Math.floor(t/5)+1)*5;}
  stRunObservation(run,current,force&&run._meaningful);return frame;
}
function stRunBegin(baseline=null){
  const s=stSession;if(!stRunState.settings.enabled||!playing||simulating||s?.simulate)return;
  const project=stRunSafe(baseline||stAuthorBaseline||projectData()),build=stRunRoot.SWYRL_ENGINE_BUILD||stRunRoot.SWRLZ_FORGE_BUILD||{};
  const run={schema:ST_RUN_SCHEMA,mode:s?'sheep-tag':currentProject.kind||'scene',id:'editor-play-'+Date.now().toString(36)+'-'+(++stRunIdSerial),startedAt:new Date().toISOString(),endedAt:null,duration:0,complete:false,endReason:null,project,engine:{version:build.version||null,sourceScene:s&&typeof ST_ARCHIVE_SOURCE_SCENE==='string'?ST_ARCHIVE_SOURCE_SCENE:project.project.canonicalId||null},initialSeed:s?.archive?.seed??null,capture:{cadence:stRunState.settings.cadence,incomplete:false,errors:[],coordinates:'Y up; +X east; -Z north; positions are world units.',scope:'Omniscient analysis export; player visibility and camera frustum are separate observations.',evidence:'Native transforms, geometry/material catalog and gameplay state. Camera inclusion is frustum-tested; no occlusion test or pixel/video capture is claimed.',frameEncoding:'Initial state plus changed top-level entity fields; null entity removes it. Frame game fields merge; camera replaces. Checkpoints contain full reconstructed state.',poseEncoding:'limbs is the immutable local-transform catalog; limbOrder indexes limbAngles. Replace each catalog rotation axis with its recorded limb angle. Other local axes, position and scale stay at their catalog values. Generic entities use parts (parent-indexed local catalog) plus partTransforms (per-index fields relative to the catalog; an empty map restores the catalog pose).',historyRetention:'The three most recently completed runs are retained in this browser tab. The active run has no frame or event cap.'},initial:null,frames:[],checkpoints:[],events:[],observations:[]};
  Object.assign(run,{_tick:0,_elapsed:0,_parts:new WeakMap(),_eventSerial:0,_effectSerial:0,_appearances:new WeakMap(),_limbs:new WeakMap(),_effectIds:new WeakMap(),_rendererObjects:new Map(),_catalog:Object.fromEntries((project.scene?.actors||[]).map(actor=>[actor.id,actor])),_nextFrame:0,_nextCheckpoint:5,_nextObservation:1,_paused:!!paused,_inUpdate:false,_commandDepth:0,_meaningful:false,_wordEntities:{},_last:null,_observedSupply:null});
  stRunState.active=run;stRunState.error=null;run.initial=stRunCollect(run);run._last=run.initial;stRunEvent('match-start',null,{initialSeed:run.initialSeed,role:s?.role||'spectator',project:project.project.name,kind:run.mode});
  run.observations.push({tick:0,t:0,text:'Play began. The initial catalog contains '+Object.keys(run.initial.entities).length+' authored and runtime entities. '+run.capture.coordinates});run._meaningful=false;
}
function stRunFinish(reason='stopped'){
  const run=stRunState.active;if(!run)return null;stRunGuard(()=>stRunCapture(true,0));stRunGuard(()=>stRunEvent('match-end',null,{reason,winner:stSession?.winner||null}));
  run.endedAt=new Date().toISOString();run.endReason=reason;run.complete=!run.capture.incomplete;run.duration=stRunNumber(stRunTime(run));if(run._last)stRunGuard(()=>stRunObservation(run,run._last,true));
  stRunState.active=null;stRunState.completed.unshift(run);stRunState.completed.length=Math.min(3,stRunState.completed.length);
  if(reason==='winner')stRunState._pendingFinished=run;else{run._rendererObjects.clear();run._observedSupply=null;}return run;
}
function stRunFrame(runOrId=null,time=null){
  const run=stRunResolve(runOrId);if(!run?.initial)return null;const t=time===null||time===undefined?run.duration:Number(time);if(!Number.isFinite(t))return null;
  const target=Math.max(0,Math.min(run.duration,t));let result=stRunClone(run.initial),start=0,at=0;
  for(const checkpoint of run.checkpoints||[])if(checkpoint.t<=target+1e-5){result=stRunClone({entities:checkpoint.entities,camera:checkpoint.camera,game:checkpoint.game});start=checkpoint.index+1;at=checkpoint.t;}else break;
  for(let index=start;index<run.frames.length;index++){const frame=run.frames[index];if(frame.t>target+1e-5)break;
    for(const [id,change]of Object.entries(frame.patch||{}))if(change===null)delete result.entities[id];else result.entities[id]={...(result.entities[id]||{}),...stRunClone(change)};
    if(Object.hasOwn(frame,'camera'))result.camera=stRunClone(frame.camera);if(frame.game)result.game={...result.game,...stRunClone(frame.game)};at=frame.t;
  }return {t:at,...result};
}
function stRunLocation(position){const [x,y,z]=position||[0,0,0];return 'x '+x+', y '+y+', z '+z+' ('+(Math.abs(x)<.01?'center':Math.abs(x)+' units '+(x>0?'east':'west'))+', '+(Math.abs(z)<.01?'center':Math.abs(z)+' units '+(z<0?'north':'south'))+')';}
function stRunDescribe(entity,entities){
  const point=entity.position||[0,0,0],floor=entity.floor,above=Number.isFinite(floor)?stRunNumber(point[1]-floor):null;
  const nearby=Object.values(entities).filter(other=>other.id!==entity.id&&other.position&&!other.destroyed&&other.type!=='st-meadow').map(other=>({other,distance:Math.hypot(point[0]-other.position[0],point[2]-other.position[2])})).sort((a,b)=>a.distance-b.distance).slice(0,2);
  let text=(entity.name||entity.type||entity.id)+' ['+entity.id+'], '+entity.kind+', at '+stRunLocation(point)+'. '+(above===null?'Floor height was not measured.':Math.abs(above)<.06?'At the terrain floor.':above+' units above its terrain floor.')+' '+(entity.onUpper?'On a raised route. ':'')+(entity.falling?'Falling toward the ground. ':'');
  text+='World scale '+(entity.scale||[]).join(', ')+', world orientation quaternion '+(entity.quaternion||[]).join(', ')+'. Catalog visual extent '+(entity.size||[]).join(' × ')+' units; colors '+(entity.appearance?.colors?.join(', ')||'unmeasured')+', opacity '+(entity.opacity||[]).join(' to ')+'. ';
  text+=(entity.origin==='authored'?'Authored':'Runtime')+', '+(entity.baked?'baked':'unbaked')+', '+(entity.authoredVisible?'authored visible':'authored hidden')+'. '+(entity.visible?'Renderer object enabled':'Renderer object hidden')+'; '+(entity.playerVisible?'available to the player vision':'hidden from player vision')+'; '+(entity.inFrustum===null?'camera frustum unmeasured':entity.inFrustum?'inside the camera frustum':'outside the camera frustum')+'. Occlusion is untested. ';
  if(entity.destroyed)text+='Destroyed; no standing structure remains. ';if(entity.captured)text+='Captured sheep represented by a glowing wisp. ';if(entity.isIllusion)text+='Magical decoy of '+entity.sourceId+'. ';
  if(Number.isFinite(entity.hp))text+='Health '+entity.hp+'/'+entity.maxHp+(entity.progress!==undefined?', construction '+stRunNumber(entity.progress*100)+'%, owner '+(entity.owner||'none'):'')+'. ';
  if(entity.level!==undefined)text+='Level '+entity.level+(entity.resources!==undefined?', '+entity.resources+' gold':'')+'. ';
  if(entity.order)text+='Order '+JSON.stringify(entity.order)+'. ';if(entity.ai?.intent)text+='Recorded bot intent: '+entity.ai.intent+'. ';if(entity.traffic)text+='Traffic '+entity.traffic.mode+(entity.traffic.blockedBy?', blocked by '+entity.traffic.blockedBy:'')+'. ';
  if(entity.approximate)text+='This scent area is approximate and does not itself identify a sheep. ';
  if(entity.limbOrder?.length)text+='Limb rotations in radians: '+entity.limbOrder.map((name,index)=>name+' '+entity.limbs[name].axis+'='+entity.limbAngles[index]).join('; ')+'. ';
  if(entity.parts?.length)text+='Articulated parts: '+entity.parts.length+' catalogued nodes; current local changes '+JSON.stringify(entity.partTransforms||{})+'. ';
  if(nearby.length)text+='Nearby: '+nearby.map(({other,distance})=>(other.name||other.id)+' '+stRunNumber(distance)+' horizontal units away'+(Math.abs(point[1]-other.position[1])>=1.2?', on a different height':'')).join('; ')+'.';return text;
}
function stRunWords(runOrId=null,time=null){
  const run=stRunResolve(runOrId),frame=stRunFrame(run,time);if(!frame)return 'No recorded Play run is available.';
  const game=frame.game,lines=['Editor spectator observation at '+frame.t+' simulation seconds.','Omniscient saved evidence. Y is up, +X is east, -Z is north. Camera frustum membership does not prove unobstructed pixel visibility.',game.winner?'Winner: '+game.winner+'.':'Role: '+game.role+'; '+(game.paused?'paused':'running')+'.'];
  if(frame.camera)lines.push('Camera at '+stRunLocation(frame.camera.position)+', orientation quaternion '+frame.camera.quaternion.join(', ')+', '+frame.camera.type+', field of view '+frame.camera.fov+' degrees, aspect '+frame.camera.aspect+'.');
  for(const entity of Object.values(frame.entities).sort((a,b)=>a.id.localeCompare(b.id)))lines.push(stRunDescribe(entity,frame.entities));return lines.join('\n\n');
}
function stRunTranscript(runOrId=null){
  const run=stRunResolve(runOrId);if(!run)return 'No recorded Play run is available.';
  const header=['Editor Play recording '+run.id,'Started '+run.startedAt+'; '+run.duration+' simulation seconds; '+(run.complete?'complete':'incomplete or still active')+'; end '+(run.endReason||'pending')+'.',run.capture?.evidence||'',run.capture?.coordinates||'',stRunWords(run,0)];
  const timeline=[...(run.events||[]).map(event=>({t:event.t,order:event.seq,text:'['+event.t+' s; tick '+event.tick+'; event '+event.seq+'] '+event.type+(event.actorId?' '+event.actorId:'')+' '+JSON.stringify(event.details||{})})),...(run.observations||[]).map((observation,index)=>({t:observation.t,order:1e12+index,text:'['+observation.t+' s; tick '+observation.tick+'] '+observation.text}))].sort((a,b)=>a.t-b.t||a.order-b.order);
  return header.concat(timeline.map(item=>item.text),['Final spectator state:',stRunWords(run,run.duration)]).join('\n\n');
}
function stRunValidate(run){
  const errors=[];if(!run||typeof run!=='object'||Array.isArray(run))return {ok:false,errors:['Choose a Play recording JSON object.'],reason:'Choose a Play recording JSON object.'};
  if(run.schema!==ST_RUN_SCHEMA)errors.push('Unsupported Play recording schema.');if(typeof run.id!=='string'||!run.id)errors.push('The run needs an identifier.');
  if(typeof run.startedAt!=='string'||!Number.isFinite(Date.parse(run.startedAt)))errors.push('The run start date is invalid.');
  if(!Number.isFinite(run.duration)||run.duration<0)errors.push('The run duration is invalid.');if(!run.initial||!run.initial.entities||typeof run.initial.entities!=='object'||Array.isArray(run.initial.entities)||!run.initial.game||typeof run.initial.game!=='object'||Array.isArray(run.initial.game))errors.push('The initial state is missing.');
  for(const key of ['frames','checkpoints','events','observations'])if(!Array.isArray(run[key]))errors.push('The run needs '+key+'.');
  const vector=(value,length)=>Array.isArray(value)&&value.length===length&&value.every(Number.isFinite);
  const entity=(item,complete=false)=>{
    if(!item||typeof item!=='object'||Array.isArray(item))return false;
    for(const key of ['id','name','type','kind'])if((complete||Object.hasOwn(item,key))&&typeof item[key]!=='string')return false;
    for(const [key,length]of [['position',3],['quaternion',4],['scale',3]])if((complete||Object.hasOwn(item,key))&&!vector(item[key],length))return false;
    if(item.worldBounds&&(!vector(item.worldBounds.min,3)||!vector(item.worldBounds.max,3)||item.worldBounds.min.some((n,i)=>n>item.worldBounds.max[i])))return false;
    if(Object.hasOwn(item,'opacity')&&(!vector(item.opacity,2)||item.opacity.some(n=>n<0||n>1)))return false;
    if(Object.hasOwn(item,'size')&&!vector(item.size,3))return false;
    if(Object.hasOwn(item,'appearance')){const a=item.appearance;if(!a||typeof a!=='object'||!Array.isArray(a.colors)||!a.colors.every(color=>typeof color==='string')||!Number.isInteger(a.meshCount)||a.meshCount<0||!Array.isArray(a.shape))return false;}
    if(Object.hasOwn(item,'limbAngles')&&(!Array.isArray(item.limbAngles)||!item.limbAngles.every(Number.isFinite)))return false;
    if(Object.hasOwn(item,'limbOrder')&&(!Array.isArray(item.limbOrder)||!item.limbOrder.every(name=>typeof name==='string')))return false;
    if(Object.hasOwn(item,'limbs')){if(!item.limbs||typeof item.limbs!=='object'||Array.isArray(item.limbs))return false;for(const limb of Object.values(item.limbs))if(!limb||!['x','y','z'].includes(limb.axis)||!vector(limb.localPosition,3)||!vector(limb.localRotation,3)||!vector(limb.localScale,3)||typeof limb.parent!=='string')return false;}
    if(complete&&item.limbOrder&&(item.limbOrder.length!==item.limbAngles?.length||!item.limbOrder.every(name=>Object.hasOwn(item.limbs||{},name))))return false;
    return true;
  };
  const validCamera=item=>!!item&&typeof item==='object'&&!Array.isArray(item)&&vector(item.position,3)&&vector(item.quaternion,4)&&vector(item.scale,3)&&['perspective','orthographic'].includes(item.type)&&Number.isFinite(item.near)&&Number.isFinite(item.far)&&item.far>item.near&&(item.type==='orthographic'||Number.isFinite(item.fov)&&item.fov>0&&item.fov<180&&Number.isFinite(item.aspect)&&item.aspect>0);
  if(run.initial?.entities)for(const [id,item]of Object.entries(run.initial.entities))if(!id||!entity(item,true))errors.push('Invalid initial entity '+id+'.');
  if(run.initial&&!validCamera(run.initial.camera))errors.push('Invalid initial camera.');
  const reconstructed={...(run.initial?.entities||{})};
  let lastT=-Infinity,lastTick=-Infinity;for(const frame of Array.isArray(run.frames)?run.frames:[]){if(!frame||!Number.isFinite(frame.t)||frame.t<0||frame.t<lastT||frame.t>run.duration+1e-4||!Number.isInteger(frame.tick)||frame.tick<0||frame.tick<lastTick||!Number.isFinite(frame.dt)||frame.dt<0||!frame.patch||typeof frame.patch!=='object'||Array.isArray(frame.patch)){errors.push('Invalid or unordered frame.');break;}
    for(const [id,item]of Object.entries(frame.patch))if(!id||item!==null&&!entity(item)){errors.push('Invalid entity frame patch.');break;}lastT=frame.t;lastTick=frame.tick;
    for(const [id,item]of Object.entries(frame.patch))if(item===null)delete reconstructed[id];else{reconstructed[id]={...(reconstructed[id]||{}),...item};if(!entity(reconstructed[id],true)||reconstructed[id].id!==id)errors.push('Invalid reconstructed entity '+id+'.');}
    if(Object.hasOwn(frame,'camera')&&!validCamera(frame.camera))errors.push('Invalid frame camera.');
    if(Object.hasOwn(frame,'game')&&(!frame.game||typeof frame.game!=='object'||Array.isArray(frame.game)))errors.push('Invalid frame game patch.');
  }
  let lastIndex=-1;for(const checkpoint of Array.isArray(run.checkpoints)?run.checkpoints:[]){if(!checkpoint||!Number.isInteger(checkpoint.index)||checkpoint.index<=lastIndex||checkpoint.index>=run.frames?.length||checkpoint.t!==run.frames?.[checkpoint.index]?.t||!checkpoint.entities||typeof checkpoint.entities!=='object'||Array.isArray(checkpoint.entities)||!checkpoint.game||!validCamera(checkpoint.camera)){errors.push('Invalid checkpoint.');break;}for(const item of Object.values(checkpoint.entities))if(!entity(item,true))errors.push('Invalid checkpoint entity.');lastIndex=checkpoint.index;}
  let seq=0,eventTime=-Infinity;for(const event of Array.isArray(run.events)?run.events:[])if(!event||!Number.isInteger(event.seq)||event.seq<=seq||!Number.isInteger(event.tick)||event.tick<0||!Number.isFinite(event.t)||event.t<0||event.t<eventTime||event.t>run.duration+1e-4||typeof event.type!=='string'||!event.details||typeof event.details!=='object'||Array.isArray(event.details)){errors.push('Invalid event sequence.');break;}else{seq=event.seq;eventTime=event.t;}
  for(const observation of Array.isArray(run.observations)?run.observations:[])if(!observation||!Number.isFinite(observation.t)||observation.t<0||observation.t>run.duration+1e-4||typeof observation.text!=='string'){errors.push('Invalid observation.');break;}
  const seen=new WeakSet(),inspect=value=>{if(!value||typeof value!=='object')return; if(seen.has(value)){errors.push('Circular imported data is not supported.');return;}seen.add(value);
    for(const [key,item]of Object.entries(value)){if(['__proto__','constructor','prototype'].includes(key))errors.push('Unsafe imported data key: '+key+'.');if(typeof item==='number'&&!Number.isFinite(item))errors.push('Imported numbers must be finite.');if(typeof item==='function'||typeof item==='symbol'||typeof item==='bigint')errors.push('Imported data must contain only JSON values.');inspect(item);}seen.delete(value);};
  inspect(run);
  return {ok:!errors.length,errors,reason:errors[0]||''};
}

// Wrappers preserve the final governed gameplay implementations and return
// values. Logging failures are caught only around recording, never gameplay.
const stRunNativeStart=stStart;
stStart=function(...args){if(stRunState.active)stRunGuard(()=>stRunFinish('restart'));const result=stRunNativeStart(...args);if(stSession&&!stSession.simulate)stRunGuard(stRunBegin);return result;};
const stRunNativeStop=stStop;
stStop=function(...args){stRunGuard(()=>stRunFinish('stopped'));return stRunNativeStop(...args);};
const stRunNativeStopSession=stopSession;
stopSession=function(...args){stRunGuard(()=>stRunFinish(stRunState.active?._requestedEndReason||'stopped'));return stRunNativeStopSession(...args);};
const stRunNativeUpdate=stUpdate;
stUpdate=function(dt,t){
  const run=stRunState.active;if(!run)return stRunNativeUpdate(dt,t);const before=stSession?.elapsed;stRunGuard(stRunPause);const advancing=!!stSession&&!paused&&!stSession.winner;
  if(advancing){run._tick++;run._inUpdate=true;}let result;try{result=stRunNativeUpdate(dt,t);}finally{if(run)run._inUpdate=false;}
  if(advancing&&stRunState.active===run&&stSession&&stSession.elapsed>before){run.duration=stRunNumber(stSession.elapsed);stRunGuard(()=>{stRunCapture(false,stSession.elapsed-before);if(stSession.winner){stRunEvent('winner',null,{winner:stSession.winner});stRunFinish('winner');}});}return result;
};
const stRunNativeCommand=stCommand;
stCommand=function(action,payload={}){
  const run=stRunState.active;if(!run)return stRunNativeCommand(action,payload);run._commandDepth++;let result;
  try{result=stRunNativeCommand(action,payload);}finally{if(run)run._commandDepth--;}
  if(action!=='preview')stRunGuard(()=>{if(stRunState.active===run&&run){stRunEvent('command',payload.id||stSession?.controlledId,{action,payload:stRunSafe(payload),ok:!!result?.ok,reason:result?.reason||'',result:stRunSafe(result)});stRunCapture(true,0);}});return result;
};
const stRunNativeSetOrder=stSetOrder;
stSetOrder=function(unit,order){if(!stRunState.active)return stRunNativeSetOrder(unit,order);const before=JSON.stringify(unit.order);const result=stRunNativeSetOrder(unit,order);if(before!==JSON.stringify(unit.order))stRunNote('order',unit.id,{order:unit.order,source:stRunState.active?._commandDepth?'player-command':'native-bot-or-lifecycle'});return result;};
const stRunNativeNewBuilding=stNewBuilding;
stNewBuilding=function(...args){if(!stRunState.active)return stRunNativeNewBuilding(...args);const result=stRunNativeNewBuilding(...args);if(result&&!args[4])stRunNote('building-created',result.id,{id:result.id,owner:result.owner,kind:result.kind,position:result.pos.toArray(),rotation:result.rotation,cost:result.cost});return result;};
const stRunNativeRemoveBuilding=stRemoveBuilding;
stRemoveBuilding=function(building){if(!stRunState.active)return stRunNativeRemoveBuilding(building);const hp=building.hp,kind=building.kind;const result=stRunNativeRemoveBuilding(building);if(hp>0&&building.hp<=0)stRunNote('building-removed',building.id,{id:building.id,owner:building.owner,kind,position:building.pos.toArray()});return result;};
const stRunNativeAttackBuilding=stAttackBuilding;
stAttackBuilding=function(wolf,building){if(!stRunState.active)return stRunNativeAttackBuilding(wolf,building);const before=stSession?.attacks.length||0;const result=stRunNativeAttackBuilding(wolf,building);for(const attack of stSession?.attacks.slice(before)||[])stRunNote('attack',wolf.id,attack);return result;};
const stRunNativeCapture=stCapture;
stCapture=function(unit,wolf=null){if(!stRunState.active)return stRunNativeCapture(unit,wolf);const captured=unit.captured,illusion=unit.isIllusion;const result=stRunNativeCapture(unit,wolf);if(!captured&&unit.captured&&!illusion)stRunNote('capture',wolf?.id,{unitId:unit.id,position:unit.pos.toArray(),wispPosition:unit.spirit?.position.toArray()||null});return result;};
const stRunNativeRescue=stRescue;
stRescue=function(unit,rescuer){if(!stRunState.active)return stRunNativeRescue(unit,rescuer);const captured=unit.captured;const result=stRunNativeRescue(unit,rescuer);if(captured&&!unit.captured&&result)stRunNote('rescue',rescuer?.id,{unitId:unit.id,position:unit.pos.toArray(),protectionUntil:unit.invulnerableUntil});return result;};
const stRunNativeArchiveCommand=stArchiveCommand;
stArchiveCommand=function(...args){if(!stRunState.active)return stRunNativeArchiveCommand(...args);const result=stRunNativeArchiveCommand(...args);if(result?.ok)stRunNote('archive-command',args[2]?.id,{action:args[0],payload:args[1],result});return result;};
const stRunNativeCloneSheep=stArchiveCloneSheep;
stArchiveCloneSheep=function(...args){if(!stRunState.active)return stRunNativeCloneSheep(...args);const result=stRunNativeCloneSheep(...args);if(result)stRunNote('decoy-created',args[1]?.id,{id:result.id,sourceId:result.sourceId,position:result.pos.toArray(),expiresAt:result.archiveExpires});return result;};
const stRunNativeRemoveDecoy=stArchiveRemoveDecoy;
stArchiveRemoveDecoy=function(s,unit){if(!stRunState.active)return stRunNativeRemoveDecoy(s,unit);const existed=s.archive?.decoys.has(unit);const result=stRunNativeRemoveDecoy(s,unit);if(existed)stRunNote('decoy-removed',unit.sourceId,{id:unit.id,position:unit.pos.toArray(),expired:s.elapsed>=unit.archiveExpires});return result;};
const stRunNativeConvertTotem=stArchiveConvertTotem;
stArchiveConvertTotem=function(s,unit,building){if(!stRunState.active)return stRunNativeConvertTotem(s,unit,building);const original=building?.kind;const result=stRunNativeConvertTotem(s,unit,building);if(result?.ok)stRunNote('totem-converted',unit.id,{id:building.id,original,kind:building.kind,position:building.pos.toArray()});return result;};
const stRunNativeScent=stArchiveScent;
stArchiveScent=function(s,unit){if(!stRunState.active)return stRunNativeScent(s,unit);const before=s.archive?.scentClues.length||0;const result=stRunNativeScent(s,unit);for(const clue of s.archive?.scentClues.slice(before)||[])stRunGuard(()=>stRunNote('scent-created',unit.id,{id:stRunEffectId(stRunState.active,clue.mesh,'scent'),position:[clue.x,terrainHeight(clue.x,clue.z),clue.z],radius:clue.radius,expiresAt:clue.expires,approximate:true}));return result;};
const stRunNativeSupply=stArchiveSupply;
stArchiveSupply=function(s){if(!stRunState.active)return stRunNativeSupply(s);const result=stRunNativeSupply(s);const run=stRunState.active;if(run&&s.archive.supply){run._observedSupply=s.archive.supply;stRunNote('supply-created',null,{id:stRunEffectId(run,s.archive.supply.mesh,'supply'),position:s.archive.supply.pos.toArray()});}return result;};
const stRunNativeEvents=stArchiveEvents;
stArchiveEvents=function(s){const run=stRunState.active;if(!run)return stRunNativeEvents(s);const before=run._observedSupply||s.archive?.supply;const result=stRunNativeEvents(s);const observed=run._observedSupply||before;if(observed&&observed!==s.archive?.supply){stRunNote(observed.collected?'supply-collected':'supply-removed',null,{id:stRunEffectId(run,observed.mesh,'supply'),position:observed.pos.toArray()});run._observedSupply=null;}return result;};
const stRunNativeRefreshHUD=stRefreshHUD;
stRefreshHUD=function(...args){const result=stRunNativeRefreshHUD(...args);if(stRunState.active||stRunState._pendingFinished){stRunGuard(stRunPause);stRunGuard(stRunPostView);}return result;};
stRunRoot.SWYRL_ENGINE_SHEEP_TAG_RUNS={configure:stRunConfigure,status:stRunStatus,data:stRunData,frame:stRunFrame,words:stRunWords,transcript:stRunTranscript,validate:stRunValidate};
stRunRoot.SWYRL_ENGINE_RUNS=stRunRoot.SWYRL_ENGINE_SHEEP_TAG_RUNS;
const stRunNativeBeginPlay=beginPlay;
beginPlay=function(...args){
  if(currentProject.kind==='sheep-tag'||!stRunState.settings.enabled)return stRunNativeBeginPlay(...args);
  const baseline=stRunSafe(projectData());if(stRunState.active)stRunGuard(()=>stRunFinish('restart'));
  const result=stRunNativeBeginPlay(...args);if(playing&&!simulating)stRunGuard(()=>stRunBegin(baseline));stRunRefreshUI();return result;
};
