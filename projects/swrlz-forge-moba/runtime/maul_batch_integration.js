// Grouped arrival starter and clearer native placement, scoped to the new profile.
function maulBatchActive(){return maulLayoutActive()&&currentProject.maulSpawnStyle===MAUL_BATCH_CORE.profile;}
function maulBatchTouchLift(){return maulBatchActive()?140:80;}
maulLoadStarter=function(){loadProject(structuredClone(MAUL_BATCH_CANONICAL_PROJECT),{workspaceLocal:true});maulFrameMap();initializeHistory('Opened Frostveil Maul · grouped arrivals');markSaved();toast('Frostveil Maul · empty builder starts');return true;};
const maulBatchNativePreflight=maulAuthoredMap;
maulAuthoredMap=function(){
  const authored=maulBatchNativePreflight();if(!maulBatchActive())return authored;
  authored.map.spawnStyle=MAUL_BATCH_CORE.profile;MAUL_BATCH_CORE.reserveAreas(authored.map);
  const check=MAUL_BATCH_CORE.preflight(authored.map,authored.towers),errors=[...new Set([...authored.errors,...check.errors])];
  return {...authored,ok:!errors.length,reason:errors[0]||'',errors,paths:check.paths};
};
window.SWYRL_ENGINE_MAUL.batchStatus=()=>({enabled:maulBatchActive(),spawnStyle:maulBatchActive()?MAUL_BATCH_CORE.profile:'sequential-v1',touchLift:maulBatchTouchLift(),groups:MAUL_BATCH_CORE.groups,groupInterval:MAUL_BATCH_CORE.groupInterval});

const maulBatchNativeRefreshHUD=maulRefreshHUD;
maulRefreshHUD=function(force=false){
  app.classList.toggle('maul-batch-project',maulBatchActive());
  app.classList.toggle('maul-batch-placement',maulBatchActive()&&!!maulSession&&!!maulUI.buildKind);
  const result=maulBatchNativeRefreshHUD(force);
  if(maulBatchActive()&&maulSession?.phase==='wave'){
    maulUIText('maulWave','Round '+maulSession.wave+' / '+maulSession.rules.waves);
    const next=maulSession.spawnQueue[0];
    if(next?.members){const seconds=Math.max(0,Math.ceil(next.at-maulSession.waveElapsed));maulUIText('maulTimer',seconds?'Group '+next.group+' / 3 · arrives in '+seconds+'s':'Group '+next.group+' / 3 · arrival area clearing');}
  }
  return result;
};

let maulBatchPlacementLabel=null;
function maulBatchLabel(){
  if(!maulBatchPlacementLabel){maulBatchPlacementLabel=document.createElement('div');maulBatchPlacementLabel.id='maulBatchPlacementLabel';maulBatchPlacementLabel.hidden=true;maulBatchPlacementLabel.setAttribute('aria-live','polite');document.body.appendChild(maulBatchPlacementLabel);}
  return maulBatchPlacementLabel;
}
const maulBatchNativeClearPreview=maulClearPreview;
maulClearPreview=function(){if(maulBatchPlacementLabel)maulBatchPlacementLabel.hidden=true;return maulBatchNativeClearPreview();};
const maulBatchNativePreview=maulPreviewAt;
maulPreviewAt=function(clientX,clientY,isTouch=false){
  if(!maulBatchActive())return maulBatchNativePreview(clientX,clientY,isTouch);
  maulClearPreview();if(!maulSession||!maulUI.buildKind||paused)return null;
  const touchLift=isTouch?maulBatchTouchLift():0,point=maulScreenWorld(clientX,clientY-touchLift);if(!point)return null;
  const cell=MAUL_CORE.worldToCell(maulSession.map,point.x,point.z),world=MAUL_CORE.cellToWorld(maulSession.map,cell),check=MAUL_CORE.canBuild(maulSession,maulUI.buildKind,cell.x,cell.z),valid=check.ok,color=valid?'#00ffd5':'#ff4663';
  maulUI.preview={...cell,cx:cell.x,cz:cell.z,world,valid,reason:check.reason||'',touchLift,finger:{x:clientX,y:clientY}};
  maulUIFeedback(valid?(isTouch?'Release to build here.':'Click to build here.'):(check.reason||'Unavailable'),!valid);
  const group=new THREE.Group();group.name='Visible Maul placement ghost';group.userData.editorOnly=true;group.position.set(world.x,.09,world.z);
  const dark=new THREE.Mesh(new THREE.PlaneGeometry(2,2),new THREE.MeshBasicMaterial({color:valid?'#062d37':'#401321',transparent:true,opacity:.82,depthWrite:false}));dark.rotation.x=-Math.PI/2;group.add(dark);
  for(const [width,opacity]of [[2,1],[2.10,.8]]){const edge=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(width,.16,width)),new THREE.LineBasicMaterial({color,transparent:true,opacity,depthTest:false}));edge.renderOrder=990;group.add(edge);}
  const ghost=maulMakeVisual(maulUI.buildKind);ghost.traverse(n=>{if(n.material)for(const m of Array.isArray(n.material)?n.material:[n.material]){m.transparent=true;m.opacity=.78;m.depthWrite=false;m.color?.lerp(new THREE.Color(color),.32);}});group.add(ghost);
  const corners=[[-1,-1],[-1,1],[1,-1],[1,1]];for(const [x,z]of corners){const pin=new THREE.Mesh(new THREE.SphereGeometry(.09,8,6),new THREE.MeshBasicMaterial({color,depthTest:false}));pin.position.set(x,.17,z);pin.renderOrder=991;group.add(pin);}
  maulRuntime.add(group);maulObjects.set('preview',group);
  if(isTouch){const rect=renderer.domElement.getBoundingClientRect(),p=new THREE.Vector3(world.x,1.8,world.z).project(camera),x=rect.left+(p.x+1)*rect.width/2,y=rect.top+(1-p.y)*rect.height/2,label=maulBatchLabel();label.textContent=(valid?'✓ ':'✕ ')+MAUL_CORE.definitions[maulUI.buildKind].name+(valid?' · release to build':' · '+(check.reason||'Unavailable'));label.dataset.valid=String(valid);label.style.left=Math.max(rect.left+96,Math.min(rect.right-96,x))+'px';label.style.top=Math.max(rect.top+8,y-32)+'px';label.hidden=false;}
  return {...maulUI.preview};
};

const maulBatchNativeCollect=stRunCollectProject;
stRunCollectProject=function(run){const record=maulBatchNativeCollect(run);if(run.mode==='maul'&&MAUL_BATCH_CORE.enabled(maulSession?.map))for(const unit of maulSession.units){const entity=record.entities[unit.id];if(entity){entity.spawnGroup=unit.spawnGroup;entity.spawnIndex=unit.spawnIndex;entity.spawnOrigin=unit.spawnOrigin?{...unit.spawnOrigin}:null;}}return record;};
const maulBatchNativeStart=maulStartSession;
maulStartSession=function(simulate=false){const result=maulBatchNativeStart(simulate);if(result&&maulBatchActive()){
  const arrivals=new THREE.Group();arrivals.name='Marked minion arrival areas';arrivals.userData.editorOnly=true;
  for(const area of maulSession.map.spawnAreas||[])for(const cell of area.cells){const p=MAUL_CORE.cellToWorld(maulSession.map,cell),mark=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.96,.02,1.96)),new THREE.LineBasicMaterial({color:'#7be2ed',transparent:true,opacity:.28,depthWrite:false}));mark.position.set(p.x,.035,p.z);arrivals.add(mark);}
  maulRuntime.add(arrivals);maulObjects.set('batch-arrivals',arrivals);
}return result;};
