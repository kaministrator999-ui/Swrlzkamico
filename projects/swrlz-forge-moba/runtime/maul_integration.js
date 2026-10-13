// Native editor session adapter. Pure match state never replaces the saved map.
let maulSession=null,maulAuthorBaseline=null,maulEditorView=null,maulRuntime=null;
const maulObjects=new Map(),maulRay=new THREE.Raycaster(),maulGround=new THREE.Plane(new THREE.Vector3(0,1,0),0);
let maulEventCursor=0,maulLastDt=0,maulResultSealed=false,maulRouteKey='';
function maulRules(){return MAUL_CORE.cleanRules(currentProject.maul||{});}
function maulConfigureRules(patch={}){
  if(playing||simulating||currentProject.kind!=='maul')return {ok:false,reason:'Open a stopped Maul project to edit its rules.'};
  const proposed={...maulRules(),...patch},validation=MAUL_CORE.validateRules(proposed);
  if(!validation.ok)return {...validation,reason:validation.errors?.[0]||'Invalid rules.'};
  beginTransaction('Edit Maul rules');currentProject.maul=MAUL_CORE.cleanRules(proposed);commitTransaction('Edit Maul rules');return {ok:true,rules:maulRules()};
}
const maulNativeTerrainHeight=terrainHeight;
terrainHeight=function(x,z){return currentProject.kind==='maul'?0:maulNativeTerrainHeight(x,z);};
const maulNativeEnvironment=applyEnvironmentSettings;
applyEnvironmentSettings=function(){maulNativeEnvironment();if(currentProject.kind==='maul'){if(terrainMesh)terrainMesh.visible=false;terrainShellGroup.visible=false;waterGroup.visible=false;}};
const maulNativeMeta=applyProjectMeta;
applyProjectMeta=function(meta={}){maulNativeMeta(meta);if(currentProject.kind==='maul'){currentProject.maul=MAUL_CORE.cleanRules(currentProject.maul);perspectiveCamera.far=1200;perspectiveCamera.updateProjectionMatrix();}if($('maulRulesBtn'))maulRefreshHUD(true);};
const maulNativeActorData=actorData,maulNativeFromData=fromData;
actorData=function(actor){const data=maulNativeActorData(actor);if(actor.userData.actorType?.startsWith('maul-'))data.maul=structuredClone(actor.userData.maul||{});return data;};
fromData=function(data){const actor=maulNativeFromData(data);if(actor&&data.type?.startsWith('maul-'))actor.userData.maul=structuredClone(data.maul||{});return actor;};
const maulNativeProjectData=projectData;
projectData=function(){const data=maulNativeProjectData();if(maulSession&&maulAuthorBaseline){data.scene=structuredClone(maulAuthorBaseline.scene);data.editor.layers=structuredClone(maulAuthorBaseline.editor.layers);}return data;};
function maulBuildStarterNative(){
  clearAll();applyProjectMeta({name:'Maul · Frostveil Bastion',template:'maul-frostveil',canonicalId:'maul-frostveil',kind:'maul',environment:'spatial-workspace',environmentSettings:{background:'#142832',fogNear:350,fogFar:1300,exposure:1.08,showTerrain:false,showScenery:false},maul:{...MAUL_CORE.defaults}});
  setProjectBackground('#142832');rebuildTerrain();terrainMesh.visible=false;clearGroup(waterGroup);clearGroup(helperGroup);clearGroup(debugGroup);
  const map=MAUL_CORE.mapDefault(),layers=['Frostveil Ground','Cliffs and Boundaries','Routes and Spawns','Builders','Winter Scenery','Authored Towers'];
  editorLayers=layers.map((name,i)=>({id:'maul-layer-'+i,name,visible:true}));activeEditorLayerId=editorLayers[0].id;
  const make=(kind,cx,cz,name,layer=0,scale=null,meta={})=>{const p=MAUL_CORE.cellToWorld(map,cx,cz),a=maulPrefab('maul-'+kind,[p.x,0,p.z],true,name);a.userData.editorLayerIds=[editorLayers[layer].id];a.userData.maul=meta;if(scale)a.scale.fromArray(scale);return a;};
  for(let row=0;row<3;row++)for(let col=0;col<3;col++){
    const sector=row*3+col;make('sector',col*10+5,row*11+5.5,'Sector '+(sector+1)+' · froststone tiles',0);
    make('spawn',col*10+5,row*11+1,'Entrance '+(sector+1),2,null,{sector});make('gate',col*10+5,row*11+11,'Waypoint '+(sector+1),2,null,{sector});
    make('builder',col*10+2,row*11+4,'Builder '+(sector+1),3,null,{sector});
    make('banner',col*10+1.2,row*11+2,'Sector '+(sector+1)+' standard',4);
  }
  for(const cx of [0,10,20,30])make('cliff',cx,16.5,'Divider '+cx,1,[1,1,34]);
  make('cliff',15,0,'Northern ridge',1,[29,1,1]);
  for(const row of [11,22,33])for(const col of [0,10,20])for(const offset of [2.5,7.5])make('cliff',col+offset,row,'Ridge '+row+' / '+(col+offset),1,[4,1,1]);
  make('cliff',15,37,'Southern ridge',1,[31,1,1]);for(const cx of [0,30])make('cliff',cx,35,'Exit collector boundary '+cx,1,[1,1,3]);
  const collector=make('sector',15,35,'Last stand · shared exit approach',0,[3.22,1,.3]);
  make('exit',15,36,'Heart of Frostveil · shared lives',2);
  for(let i=0;i<8;i++){const side=i%2?-1:1;const pine=maulPrefab('maul-pine',[side*34,0,-31+Math.floor(i/2)*21],true,'Snow pine '+(i+1));pine.userData.editorLayerIds=[editorLayers[4].id];}
  make('maze-wall',2,7,'Example maze wall A',5);make('maze-wall',3,7,'Example maze wall B',5);make('arrow',3,6,'Example Arrow Spire',5);
  renderLayerPanel();finishTemplate('maul-builder');maulFrameMap();initializeHistory('Built Frostveil Maul in native editor');markSaved();return projectData();
}
function maulLoadStarter(){if(MAUL_CANONICAL_PROJECT?.scene?.actors?.length){loadProject(structuredClone(MAUL_CANONICAL_PROJECT),{workspaceLocal:true});maulFrameMap();initializeHistory('Opened Frostveil Maul');markSaved();}else maulBuildStarterNative();toast('Frostveil Bastion · Maul tower defense');return true;}
function maulSetActorWorldPosition(actor,position){actor.position.copy(actor.parent?actor.parent.worldToLocal(position.clone()):position);}
function maulActorCell(map,actor){const p=actor.getWorldPosition(new THREE.Vector3());return MAUL_CORE.worldToCell(map,p.x,p.z);}
function maulAuthoredMap(){
  const map=MAUL_CORE.mapDefault(),pieces=actors.filter(a=>a.userData.baked&&walkingObjectVisible(a)&&a.userData.manualVisible!==false),towers=[],errors=[];
  if(new Set(pieces.map(a=>a.userData.id)).size!==pieces.length)errors.push('Authored actors must have unique IDs.');
  scene.updateMatrixWorld(true);
  const spawns=pieces.filter(a=>a.userData.actorType==='maul-spawn'),gates=pieces.filter(a=>a.userData.actorType==='maul-gate'),exits=pieces.filter(a=>a.userData.actorType==='maul-exit');
  if(spawns.length!==9||gates.length!==9||exits.length!==1)errors.push('Bake nine entrance markers, nine waypoints and exactly one shared exit.');
  map.blocked=[];
  for(const actor of pieces){const type=actor.userData.actorType,kind=type?.slice(5),position=actor.getWorldPosition(new THREE.Vector3()),scale=actor.getWorldScale(new THREE.Vector3()),rotation=new THREE.Euler().setFromQuaternion(actor.getWorldQuaternion(new THREE.Quaternion()));if(type==='maul-cliff'){
      if(Math.abs(Math.sin(rotation.y*2))>.001||Math.abs(rotation.x)+Math.abs(rotation.z)>.001)errors.push(actor.name+': use a grid-aligned cliff rotation.');
      const bounds=new THREE.Box3().setFromObject(actor);for(let z=0;z<map.rows;z++)for(let x=0;x<map.cols;x++){const p=MAUL_CORE.cellToWorld(map,x,z);if(p.x>bounds.min.x-.001&&p.x<bounds.max.x+.001&&p.z>bounds.min.z-.001&&p.z<bounds.max.z+.001)map.blocked.push({x,z});}
    }else if(MAUL_CORE.definitions[kind]){
      const c=MAUL_CORE.worldToCell(map,position.x,position.z),p=MAUL_CORE.cellToWorld(map,c.x,c.z);
      if(Math.abs(p.x-position.x)+Math.abs(p.z-position.z)>.01||scale.distanceTo(new THREE.Vector3(1,1,1))>.001)errors.push(actor.name+': tower footprints use one 2 × 2 grid cell; snap the actor to its cell and keep unit scale.');
      towers.push({id:actor.userData.id,kind,cx:c.x,cz:c.z,level:Math.min(3,Math.max(1,Number(actor.userData.maul?.level)||1)),priority:actor.userData.maul?.priority||'first',owner:'player'});
    }
  }
  const keyed=(list,label)=>{const result=new Map();for(const a of list){const sector=Number(a.userData.maul?.sector);if(!Number.isInteger(sector)||sector<0||sector>8||result.has(sector))errors.push('Give each '+label+' a unique sector number from 0 to 8.');else result.set(sector,a);}return result;};
  const bySpawn=keyed(spawns,'entrance'),byGate=keyed(gates,'waypoint');
  for(let i=0;i<9;i++){const spawn=bySpawn.get(i),gate=byGate.get(i);if(spawn){const c=maulActorCell(map,spawn);map.spawns[i]={...c,sector:i};map.sectors[i].spawn={...c};}if(gate)map.sectors[i].gate=maulActorCell(map,gate);}
  if(exits[0])map.exit=maulActorCell(map,exits[0]);
  for(const sector of map.sectors)sector.gates=map.sectors.filter(s=>s.id%3===sector.id%3&&s.id>=sector.id).map(s=>({...s.gate}));
  map.reserved=[...map.spawns.map(({x,z})=>({x,z})),...map.sectors.map(s=>s.gate),map.exit];
  const check=MAUL_CORE.preflight(map,towers);if(!check.ok)errors.push(...(check.errors||[check.reason]));return {ok:!errors.length,reason:errors[0]||'',errors,map,towers};
}
function maulFrameAt(target,overview=false){
  setCameraView('perspective');orbit.maxDistance=800;perspectiveCamera.far=1600;perspectiveCamera.fov=50;perspectiveCamera.updateProjectionMatrix();
  orbit.target.set(target.x,0,target.z);perspectiveCamera.position.set(target.x,overview?92:27,target.z+(overview?70:19));perspectiveCamera.lookAt(orbit.target);
  const width=overview?66:21,height=overview?78:25;
  for(let pass=0;pass<6;pass++){perspectiveCamera.updateMatrixWorld();let fit=0;for(const dx of [-width/2,width/2])for(const dz of [-height/2,height/2]){const p=new THREE.Vector3(target.x+dx,0,target.z+dz).project(perspectiveCamera);fit=Math.max(fit,Math.abs(p.x),Math.abs(p.y));}if(fit<.8)break;perspectiveCamera.position.sub(orbit.target).multiplyScalar(fit/.78).add(orbit.target);perspectiveCamera.lookAt(orbit.target);}
  if(scene.fog?.isFog){scene.fog.near=350;scene.fog.far=1300;}orbit.update();
}
function maulFrameMap(){maulFrameAt({x:0,z:0},true);}
function maulFrameSector(index){const map=maulSession?.map||MAUL_CORE.mapDefault();index=Math.max(0,Math.min(8,Number(index)||0));maulUI.sector=index;if($('maulSector'))$('maulSector').value=String(index);if(maulSession)maulSession.selectedSector=index;const sector=map.sectors[index],p=MAUL_CORE.cellToWorld(map,(sector.minX+sector.maxX)/2,(sector.minZ+sector.maxZ)/2);maulFrameAt(p);maulClearPreview();maulRefreshHUD(true);}
function maulPanCamera(dx,dy){const factor=perspectiveCamera.position.distanceTo(orbit.target)/800;const x=-dx*factor,z=-dy*factor;orbit.target.x+=x;orbit.target.z+=z;perspectiveCamera.position.x+=x;perspectiveCamera.position.z+=z;perspectiveCamera.lookAt(orbit.target);maulClearPreview();}
function maulScreenWorld(clientX,clientY){const rect=renderer.domElement.getBoundingClientRect();if(clientX<rect.left||clientY<rect.top||clientX>rect.right||clientY>rect.bottom)return null;camera.updateMatrixWorld();maulRay.setFromCamera(new THREE.Vector2((clientX-rect.left)/rect.width*2-1,-(clientY-rect.top)/rect.height*2+1),camera);const point=new THREE.Vector3();return maulRay.ray.intersectPlane(maulGround,point)?point:null;}
function maulSetBuildKind(kind){maulUI.buildKind=MAUL_CORE.definitions[kind]?kind:null;maulUI.selectedTowerId=null;maulClearPreview();maulRefreshHUD(true);}
function maulPreviewAt(clientX,clientY,isTouch=false){
  maulClearPreview();if(!maulSession||!maulUI.buildKind||paused)return null;
  const point=maulScreenWorld(clientX,clientY-(isTouch?80:0));if(!point)return null;
  const cell=MAUL_CORE.worldToCell(maulSession.map,point.x,point.z),world=MAUL_CORE.cellToWorld(maulSession.map,cell.x,cell.z),check=MAUL_CORE.canBuild(maulSession,maulUI.buildKind,cell.x,cell.z);
  maulUI.preview={...cell,cx:cell.x,cz:cell.z,world,valid:check.ok,reason:check.reason||''};
  const group=new THREE.Group();group.name='Maul placement footprint';group.userData.editorOnly=true;group.position.set(world.x,.08,world.z);
  const material=new THREE.MeshBasicMaterial({color:check.ok?'#6fffc2':'#ff6d76',transparent:true,opacity:.3,depthWrite:false});const plane=new THREE.Mesh(new THREE.PlaneGeometry(1.95,1.95),material);plane.rotation.x=-Math.PI/2;group.add(plane);
  const outline=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(2,.10,2)),new THREE.LineBasicMaterial({color:check.ok?'#a1ffe0':'#ff7c88'}));group.add(outline);
  const ghost=maulMakeVisual(maulUI.buildKind);ghost.traverse(n=>{if(n.material){n.material.transparent=true;n.material.opacity=.42;n.material.depthWrite=false;}});group.add(ghost);maulRuntime.add(group);maulObjects.set('preview',group);return {...maulUI.preview};
}
function maulClearPreview(){const obj=maulObjects.get('preview');if(obj)maulDisposeObject(obj);maulObjects.delete('preview');if(typeof maulUI!=='undefined')maulUI.preview=null;}
function maulCommitPreview(){const preview=maulUI.preview;if(!preview||!maulUI.buildKind)return {ok:false,reason:'Tap visible ground to choose a grid cell.'};return maulBuildAt(maulUI.buildKind,preview.cx,preview.cz);}
function maulBuildAt(kind,cx,cz){if(!maulSession||paused)return {ok:false,reason:'Resume Play to build.'};const result=MAUL_CORE.build(maulSession,kind,cx,cz);
  if(result.ok)for(const builder of actors.filter(a=>a.userData.actorType==='maul-builder')){const c=maulActorCell(maulSession.map,builder);if(c.x===cx&&c.z===cz)for(const [dx,dz]of [[-1,0],[1,0],[0,-1],[0,1]]){const free={x:cx+dx,z:cz+dz};if(!maulSession.map.blocked.some(p=>p.x===free.x&&p.z===free.z)&&!maulSession.towers.some(t=>t.cx===free.x&&t.cz===free.z)){const p=MAUL_CORE.cellToWorld(maulSession.map,free);maulSetActorWorldPosition(builder,new THREE.Vector3(p.x,0,p.z));break;}}}
  maulSyncVisuals();maulFlushEvents();if(!result.ok){maulUIFeedback(result.reason,true);stRunGuard(()=>stRunNote('maul-build-rejected',null,{kind,cx,cz,reason:result.reason}));}maulClearPreview();maulRefreshHUD(true);return result;}
function maulHitTower(clientX,clientY){const p=maulScreenWorld(clientX,clientY);if(!p||!maulSession)return null;const ids=new Set(maulSession.towers.map(t=>t.id)),objects=maulSession.towers.map(t=>maulObjects.get(t.id)).filter(Boolean);const hit=maulRay.intersectObjects(objects,true)[0];if(hit){let node=hit.object;while(node&&!ids.has(node.userData.id))node=node.parent;if(node)return node.userData.id;}const c=MAUL_CORE.worldToCell(maulSession.map,p.x,p.z);return maulSession.towers.find(t=>t.cx===c.x&&t.cz===c.z)?.id||null;}
function maulSelectTower(id){maulUI.selectedTowerId=id;maulUI.buildKind=null;maulClearPreview();maulRefreshHUD(true);}
function maulOrder(command){
  if(!maulSession||paused||['won','lost'].includes(maulSession.phase))return {ok:false,reason:'Resume an active match to give an order.'};
  let result={ok:false,reason:'Unknown Maul order.'};
  if(command.type==='start-wave')result=MAUL_CORE.startWave(maulSession);
  if(command.type==='upgrade')result=MAUL_CORE.upgrade(maulSession,command.id||maulUI.selectedTowerId);
  if(command.type==='sell')result=MAUL_CORE.sell(maulSession,command.id||maulUI.selectedTowerId);
  if(command.type==='priority')result=MAUL_CORE.setPriority(maulSession,command.id||maulUI.selectedTowerId,command.priority);
  if(command.type==='move-builder'){const p=maulScreenWorld(command.clientX,command.clientY);if(p){const c=MAUL_CORE.worldToCell(maulSession.map,p.x,p.z),builder=actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===maulSession.selectedSector);if(builder){const start=maulActorCell(maulSession.map,builder),path=MAUL_CORE.path(maulSession.map,maulSession.towers,start,c);if(path){maulSession.builderOrders??={};maulSession.builderOrders[builder.userData.id]={path:path.slice(1),index:0};result={ok:true};}else result={ok:false,reason:'The builder needs a clear route to that cell.'};}}}
  if(!result.ok)maulUIFeedback(result.reason,true);maulSyncVisuals();maulFlushEvents();stRunGuard(()=>stRunNote('maul-command',command.id||null,{...command,result:{ok:result.ok,reason:result.reason||null}}));maulRefreshHUD(true);return result;
}
function maulDisposeObject(object){object.removeFromParent();object.traverse(n=>{n.geometry?.dispose?.();for(const m of Array.isArray(n.material)?n.material:n.material?[n.material]:[])m.dispose?.();});}
function maulSyncVisuals(){
  if(!maulSession||!maulRuntime)return;
  const active=new Set(['preview','range','routes']);
  for(const tower of maulSession.towers){active.add(tower.id);let object=maulObjects.get(tower.id);if(!object||object.userData.level!==tower.level){if(object)maulDisposeObject(object);object=maulMakeVisual(tower.kind,tower.level);object.userData={id:tower.id,level:tower.level};maulRuntime.add(object);maulObjects.set(tower.id,object);}const p=MAUL_CORE.cellToWorld(maulSession.map,tower.cx,tower.cz);object.position.set(p.x,0,p.z);}
  for(const unit of maulSession.units.filter(u=>u.alive!==false)){
    active.add(unit.id);let object=maulObjects.get(unit.id);if(!object){object=maulMakeVisual(unit.boss?'boss':unit.air?'air-creep':'creep');object.userData.id=unit.id;maulRuntime.add(object);maulObjects.set(unit.id,object);}
    const old=object.position.clone();object.position.set(unit.x,unit.air?2.8+Math.sin(maulSession.elapsed*2.2)*.12:0,unit.z);if(old.distanceTo(object.position)>.001)object.rotation.y=Math.atan2(unit.x-old.x,unit.z-old.z);
    for(let i=0;i<4;i++){const leg=object.getObjectByName('CreepLeg'+i);if(leg)leg.rotation.x=Math.sin(maulSession.elapsed*8+i%2*Math.PI)*.4;}
    for(const side of [-1,1]){const wing=object.getObjectByName('CreepWing'+side);if(wing)wing.rotation.z=side*Math.sin(maulSession.elapsed*10)*.3;}
    const bar=object.getObjectByName('HealthFill');if(bar)bar.scale.x=Math.max(.02,unit.hp/unit.maxHp);
  }
  for(const shot of maulSession.shots||[]){active.add(shot.id);let object=maulObjects.get(shot.id);if(!object){const from=shot.from,to=shot.to;const vec=p=>new THREE.Vector3(p.x??p[0],p.y??2,p.z??p[2]);object=new THREE.Line(new THREE.BufferGeometry().setFromPoints([vec(from),vec(to)]),new THREE.LineBasicMaterial({color:MAUL_COLORS[shot.kind]||'#fff'}));maulRuntime.add(object);maulObjects.set(shot.id,object);}}
  for(const [id,object]of maulObjects)if(!active.has(id)){maulDisposeObject(object);maulObjects.delete(id);}
  const prior=maulObjects.get('range');if(prior)maulDisposeObject(prior);maulObjects.delete('range');
  const selected=maulSession.towers.find(t=>t.id===maulUI.selectedTowerId);if(selected){const range=MAUL_CORE.definitions[selected.kind].levels[selected.level-1].range;if(range){const points=Array.from({length:65},(_,i)=>new THREE.Vector3(Math.cos(i/64*Math.PI*2)*range,.11,Math.sin(i/64*Math.PI*2)*range));const ring=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:MAUL_COLORS[selected.kind]}));ring.position.copy(maulObjects.get(selected.id).position);maulRuntime.add(ring);maulObjects.set('range',ring);}}
  const routeKey=JSON.stringify([maulSession.selectedSector,maulSession.towers.map(t=>[t.cx,t.cz])]);
  if(routeKey!==maulRouteKey){maulRouteKey=routeKey;const old=maulObjects.get('routes');if(old)maulDisposeObject(old);const routes=new THREE.Group();routes.name='Ground creep route guides';routes.userData.editorOnly=true;
    for(const spawn of maulSession.map.spawns){const path=MAUL_CORE.route(maulSession.map,maulSession.towers,spawn,spawn.sector);if(!path)continue;const points=path.map(c=>{const p=MAUL_CORE.cellToWorld(maulSession.map,c);return new THREE.Vector3(p.x,.075,p.z);});routes.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:spawn.sector===maulSession.selectedSector?'#ffd27b':'#83e1e1',transparent:true,opacity:spawn.sector===maulSession.selectedSector?.75:.18,depthWrite:false})));}
    maulRuntime.add(routes);maulObjects.set('routes',routes);
  }
}
function maulFlushEvents(){if(!maulSession)return;const events=maulSession.events.slice(maulEventCursor);maulEventCursor=maulSession.events.length;for(const event of events)stRunGuard(()=>{const saved=stRunEvent('maul-'+event.type,event.details?.id||null,{...event.details,simulationTime:event.t});if(saved)saved.t=stRunNumber(event.t);});}
function maulUpdate(dt){
  if(!maulSession)return;if(['won','lost'].includes(maulSession.phase)){maulLastDt=0;return;}maulLastDt=dt*Math.max(1,Math.min(4,maulSession.speed||1));const run=stRunState.active;
  if(run?.mode==='maul'){run._tick++;run._inUpdate=true;}
  const beforeElapsed=maulSession.elapsed;MAUL_CORE.tick(maulSession,maulLastDt);maulLastDt=maulSession.elapsed-beforeElapsed;
  if(run?.mode==='maul'){run._elapsed=maulSession.elapsed;run.duration=stRunTime(run);}
  for(const [id,order]of Object.entries(maulSession.builderOrders||{})){const a=actors.find(a=>a.userData.id===id),next=order.path?.[order.index];if(!a||!next){delete maulSession.builderOrders[id];continue;}if(maulSession.towers.some(t=>t.cx===next.x&&t.cz===next.z)){delete maulSession.builderOrders[id];continue;}const p=MAUL_CORE.cellToWorld(maulSession.map,next),current=a.getWorldPosition(new THREE.Vector3()),d=new THREE.Vector3(p.x,0,p.z).sub(current);if(d.length()<.15){order.index++;continue;}const step=Math.min(d.length(),maulLastDt*7),dir=d.normalize();maulSetActorWorldPosition(a,current.addScaledVector(dir,step));a.rotation.y=Math.atan2(dir.x,dir.z);}
  maulSyncVisuals();maulFlushEvents();if(run?.mode==='maul')run._inUpdate=false;
}
function maulAfterView(){if(!maulSession)return;orbit.update();maulRefreshHUD();}
const maulNativeAfterTick=stRunAfterTick;
stRunAfterTick=function(dt){const run=stRunState.active;if(run?.mode!=='maul')return maulNativeAfterTick(dt);stRunGuard(()=>{stRunPause();if(playing&&!paused&&!workspacePanelOpen)stRunCapture(false,maulLastDt);if(['won','lost'].includes(maulSession?.phase)&&!maulResultSealed){maulResultSealed=true;stRunEvent('winner',null,{winner:maulSession.phase==='won'?'builders':'creeps',gold:maulSession.gold,lives:maulSession.lives,wave:maulSession.wave});stRunFinish('winner');stRunPostView();}stRunRefreshUI();});};
const maulNativeCollect=stRunCollectProject;
stRunCollectProject=function(run){const record=maulNativeCollect(run);if(run.mode!=='maul'||!maulSession)return record;const frustum=stRunFrustum(),s=maulSession;
  for(const tower of s.towers){const object=maulObjects.get(tower.id);if(!object)continue;record.entities[tower.id]=stRunBaseEntity(run,tower.id,object,{name:MAUL_CORE.definitions[tower.kind].name+' '+tower.id,type:'maul-'+tower.kind,kind:'tower',origin:run._catalog[tower.id]?'authored':'runtime',layers:[...(run._catalog[tower.id]?.editorLayerIds||[])],tags:[...(run._catalog[tower.id]?.tags||[])],playerVisible:true,baked:true,authoredVisible:true,floor:0,level:tower.level,grid:[tower.cx,tower.cz],owner:tower.owner,priority:tower.priority,spent:tower.spent,...stRunParts(run,object)},frustum);}
  for(const unit of s.units.filter(u=>u.alive!==false)){const object=maulObjects.get(unit.id);if(!object)continue;record.entities[unit.id]=stRunBaseEntity(run,unit.id,object,{name:unit.boss?'Frostveil siege beast':unit.air?'Sky raider':'Frost raider',type:'maul-creep',kind:unit.air?'flying-creep':'ground-creep',origin:'runtime',playerVisible:true,baked:true,authoredVisible:true,hp:unit.hp,maxHp:unit.maxHp,air:unit.air,armor:unit.armor,speed:unit.speed,remaining:unit.remaining,route:stRunSafe({index:unit.pathIndex,waypoints:unit.path}),...stRunParts(run,object)},frustum);}
  for(const shot of s.shots||[]){const object=maulObjects.get(shot.id);if(!object)continue;const from=[shot.from.x,shot.from.y,shot.from.z],to=[shot.to.x,shot.to.y,shot.to.z];record.entities[shot.id]=stRunBaseEntity(run,shot.id,object,{name:shot.kind+' attack trace',type:'maul-shot',kind:'projectile',origin:'runtime',playerVisible:true,baked:true,authoredVisible:true,floor:0,position:from.map((v,i)=>stRunNumber((v+to[i])/2)),from:stRunVector(from),to:stRunVector(to),attackKind:shot.kind,targetId:shot.targetId,ttl:stRunNumber(shot.ttl),...stRunParts(run,object)},frustum);}
  record.game={kind:'maul',project:currentProject.name,role:'builder',paused:!!paused,winner:s.phase==='won'?'builders':s.phase==='lost'?'creeps':null,elapsed:s.elapsed,gold:s.gold,lives:s.lives,wave:s.wave,phase:s.phase,timer:s.timer,kills:s.kills,leaks:s.leaks,rules:stRunSafe(s.rules),map:stRunSafe(s.map),pendingSpawns:stRunSafe(s.pendingSpawns||s.spawnQueue||[]),builderOrders:stRunSafe(s.builderOrders||{}),shots:stRunSafe(s.shots||[]),selectedSector:s.selectedSector,selectedTowerId:maulUI.selectedTowerId,buildKind:maulUI.buildKind,speed:s.speed,controlledId:actors.find(a=>a.userData.actorType==='maul-builder'&&a.userData.maul?.sector===s.selectedSector)?.userData.id||null};return record;};
const maulNativeRunFinish=stRunFinish;
stRunFinish=function(reason='stopped'){const isMaul=stRunState.active?.mode==='maul',winner=maulSession?.phase==='won'?'builders':maulSession?.phase==='lost'?'creeps':null;const run=maulNativeRunFinish(reason);if(isMaul&&run){const end=run.events.at(-1);if(end?.type==='match-end')end.details.winner=winner;}return run;};
function maulStartSession(simulate=false){
  if(playing||simulating)stopSession();const preflight=maulAuthoredMap();if(!preflight.ok){toast(preflight.reason);editorLog(preflight.reason,'error');return false;}
  maulAuthorBaseline=structuredClone(projectData());maulEditorView={position:camera.position.clone(),quaternion:camera.quaternion.clone(),up:camera.up.clone(),target:orbit.target.clone(),fov:perspectiveCamera.fov,fog:scene.fog?.clone()||null};
  closeTeleportMenu(false);closeWorkspacePanel(false);preSessionCameraView=editorCameraView;savePlaySnapshot();playing=!simulate;simulating=simulate;paused=false;keepSimulationChanges=false;transform.detach();if(selectionBox)selectionBox.visible=false;setActiveCamera(perspectiveCamera);orbit.enabled=false;document.exitPointerLock?.();
  maulSession=MAUL_CORE.createSession({rules:maulRules(),map:preflight.map,towers:preflight.towers});maulSession.speed=1;maulSession.selectedSector=maulSession.rules.selectedSector;maulRuntime=new THREE.Group();maulRuntime.name='Maul Play runtime';scene.add(maulRuntime);maulObjects.clear();maulRouteKey='';maulEventCursor=0;maulResultSealed=false;
  for(const actor of actors)if(MAUL_CORE.definitions[actor.userData.actorType?.slice(5)])actor.visible=false;
  maulSyncVisuals();maulShowHUD(true);maulFrameSector(maulSession.selectedSector||0);setSessionButtons();$('keepBtn').classList.add('hidden');$('viewLabel').textContent='Frostveil Maul · '+(simulate?'Simulate':'Play In Editor');
  if(!simulate){stRunGuard(()=>stRunBegin(maulAuthorBaseline));if(stRunState.active?.mode==='maul'){const run=stRunState.active;run.initialSeed=maulSession.seed??maulSession.rules.seed;const start=run.events.find(e=>e.type==='match-start');if(start)Object.assign(start.details,{role:'builder',initialSeed:run.initialSeed});}maulFlushEvents();}return true;
}
const maulNativePlay=beginPlay,maulNativeSimulate=beginSimulate,maulNativeStop=stopSession;
beginPlay=function(fromHere=null){return currentProject.kind==='maul'?maulStartSession(false):maulNativePlay(fromHere);};
beginSimulate=function(){return currentProject.kind==='maul'?maulStartSession(true):maulNativeSimulate();};
stopSession=function(){const view=maulSession?maulEditorView:null;if(maulSession){if(stRunState.active?.mode==='maul')stRunGuard(()=>stRunFinish('stopped'));maulDisposeUI();for(const object of [...maulObjects.values()])maulDisposeObject(object);maulObjects.clear();maulRuntime?.removeFromParent();maulRuntime=null;maulSession=null;maulAuthorBaseline=null;maulEditorView=null;}
  const result=maulNativeStop();if(view){camera.position.copy(view.position);camera.quaternion.copy(view.quaternion);camera.up.copy(view.up);orbit.target.copy(view.target);perspectiveCamera.fov=view.fov;scene.fog=view.fog;perspectiveCamera.updateProjectionMatrix();orbit.update();}maulRefreshHUD(true);return result;};
$('playBtn').onclick=()=>beginPlay();$('simulateBtn').onclick=()=>beginSimulate();$('stopBtn').onclick=()=>stopSession();$('playFromHereBtn').onclick=()=>{if(currentProject.kind==='maul'||currentProject.kind==='sheep-tag')beginPlay();else if(selected)beginPlay(selected.getWorldPosition(new THREE.Vector3()));};
window.SWYRL_ENGINE_MAUL={status:()=>maulSession?stRunSafe({...MAUL_CORE.status(maulSession),active:true,paused,speed:maulSession.speed,selectedSector:maulSession.selectedSector,rules:maulSession.rules,units:maulSession.units,shots:maulSession.shots,towers:maulSession.towers,events:maulSession.events,map:maulSession.map}):{active:false,rules:maulRules()},uiStatus:()=>stRunSafe(maulUI),preflight:()=>maulAuthoredMap(),configure:maulConfigureRules,frameSector:maulFrameSector,frameMap:maulFrameMap,pointScreen:(x,z,y=0)=>{camera.updateMatrixWorld();const p=new THREE.Vector3(x,y,z).project(camera),rect=renderer.domElement.getBoundingClientRect();return {x:rect.left+(p.x+1)*rect.width/2,y:rect.top+(1-p.y)*rect.height/2,visible:Math.abs(p.x)<1&&Math.abs(p.y)<1&&p.z>-1&&p.z<1};},renderStatus:()=>({objects:maulObjects.size,meshes:[...maulObjects.values()].filter(o=>o.isMesh||o.children.length).length}),definitions:MAUL_CORE.definitions};
