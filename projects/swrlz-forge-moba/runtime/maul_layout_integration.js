// The existing cooperative match consumes an authored classic-shaped map.
function maulLayoutActive(){return currentProject.kind==='maul'&&currentProject.maulLayout==='classic-v2';}
const maulLayoutNativeFromData=fromData;
fromData=function(data){const actor=maulLayoutNativeFromData(data);if(actor&&maulLayoutActive())maulLayoutTint(actor);return actor;};
function maulLayoutBuildNative(){
  clearAll();applyProjectMeta({name:'Maul · Frostveil Bastion',template:'maul-frostveil',canonicalId:'maul-frostveil',kind:'maul',maulLayout:'classic-v2',environment:'spatial-workspace',environmentSettings:{background:'#152b3c',fogNear:350,fogFar:1300,exposure:1.1,showTerrain:false,showScenery:false},maul:{...MAUL_CORE.defaults}});
  setProjectBackground('#152b3c');rebuildTerrain();terrainMesh.visible=false;clearGroup(waterGroup);clearGroup(helperGroup);clearGroup(debugGroup);
  const map=MAUL_LAYOUT_CORE.mapDefault(),names=['Continuous Snowlands','Cliff Ridges','Routes and Shared Ship','Nine Builders','Winter Scenery','Authored Towers','Southern Harbor'];
  editorLayers=names.map((name,i)=>({id:'maul-layer-'+i,name,visible:true}));activeEditorLayerId=editorLayers[0].id;
  const make=(kind,cx,cz,name,layer=0,scale=null,meta={})=>{const p=MAUL_CORE.cellToWorld(map,cx,cz),type='maul-'+kind,a=MAUL_LAYOUT_TYPES.includes(type)?maulLayoutPrefab(type,[p.x,0,p.z],true,name):maulPrefab(type,[p.x,0,p.z],true,name);a.userData.editorLayerIds=[editorLayers[layer].id];a.userData.maul=meta;if(scale)a.scale.fromArray(scale);maulLayoutTint(a);return a;};
  make('water',20,22,'Frostveil sea and blue trenches',6,[51,1,53]);
  for(const s of map.sectors.slice(0,3))make('snowfield',(s.minX+s.maxX)/2,11,'Long '+s.name+' snow bay',0,[s.maxX-s.minX+1,1,21]);
  make('snowfield',20,23,'Broad middle defense crossbar',0,[37,1,7]);
  for(const [cx,width]of [[3,3],[20,9],[37,3]])make('snowfield',cx,27,'Snow pass into the lower terraces',0,[width,1,1]);
  make('snowfield',20,34.5,'Lower side terraces and rear catcher',0,[37,1,14]);
  make('snowfield',20,43,'Shared harbor approach',0,[5,1,3]);
  for(const ridge of MAUL_LAYOUT_CORE.geometry())make(ridge.kind==='coast'?'water':'cliff',ridge.cx,ridge.cz,ridge.name,ridge.kind==='coast'?6:1,[ridge.width,1,ridge.depth],{noBuild:ridge.kind==='coast'});
  const builderCells=[[5,10],[18,10],[31,10],[5,23],[18,24],[35,23],[8,35],[19,37],[32,35]];
  for(const sector of map.sectors){const i=sector.id;make('spawn',sector.spawn.x,sector.spawn.z,sector.name+' entrance',2,null,{sector:i});make('gate',sector.gate.x,sector.gate.z,sector.name+' route beacon',2,null,{sector:i});make('builder',...builderCells[i],sector.name+' builder',3,null,{sector:i});make('banner',builderCells[i][0]+1,builderCells[i][1]+1,sector.name+' standard',4,null,{sector:i});}
  for(const [key,point]of Object.entries(map.turns))make('route-turn',point.x,point.z,key+' lower-lane turn',2,null,{turnKey:key});
  make('exit',map.exit.x,map.exit.z,'Last ship · shared Maul lives',2);
  for(const [i,c]of [[0,[12.8,5]],[1,[27,5]],[2,[13.1,15]],[3,[27.1,15]],[4,[6,28]],[5,[34,28]],[6,[16,30.8]],[7,[24,30.8]]]){const a=make('pine',c[0],c[1],'Snow ridge pine '+(i+1),4);a.position.y=2.1;}
  make('maze-wall',4,12,'Example maze wall A',5);make('maze-wall',5,12,'Example maze wall B',5);make('arrow',5,11,'Example Arrow Spire',5);
  renderLayerPanel();finishTemplate('maul-builder');maulFrameMap();initializeHistory('Built classic Maul terrain in native editor');markSaved();return projectData();
}
maulLoadStarter=function(){if(MAUL_LAYOUT_CANONICAL_PROJECT?.scene?.actors?.length){loadProject(structuredClone(MAUL_LAYOUT_CANONICAL_PROJECT),{workspaceLocal:true});maulFrameMap();initializeHistory('Opened classic Frostveil Maul');markSaved();}else maulLayoutBuildNative();toast('Frostveil Maul · classic cooperative map');return true;};
const maulLayoutNativePreflight=maulAuthoredMap;
maulAuthoredMap=function(){
  if(!maulLayoutActive())return maulLayoutNativePreflight();const map=MAUL_LAYOUT_CORE.mapDefault(),pieces=actors.filter(a=>a.userData.baked&&walkingObjectVisible(a)&&a.userData.manualVisible!==false),towers=[],errors=[];scene.updateMatrixWorld(true);
  if(new Set(pieces.map(a=>a.userData.id)).size!==pieces.length)errors.push('Give every authored actor a unique ID.');
  const typed=kind=>pieces.filter(a=>a.userData.actorType==='maul-'+kind),spawns=typed('spawn'),gates=typed('gate'),exits=typed('exit'),builders=typed('builder');if(spawns.length!==9||gates.length!==9||builders.length!==9||exits.length!==1)errors.push('Bake nine entrances, nine route beacons, nine builders and one shared ship.');map.blocked=[];
  for(const a of pieces){const type=a.userData.actorType,kind=type?.slice(5),position=a.getWorldPosition(new THREE.Vector3()),scale=a.getWorldScale(new THREE.Vector3()),rotation=new THREE.Euler().setFromQuaternion(a.getWorldQuaternion(new THREE.Quaternion()));
    if(type==='maul-cliff'||type==='maul-water'&&a.userData.maul?.noBuild){if(Math.abs(Math.sin(rotation.y*2))>.001||Math.abs(rotation.x)+Math.abs(rotation.z)>.001)errors.push(a.name+': align terrain blocks to the ground grid.');const box=new THREE.Box3().setFromObject(a);for(let z=0;z<map.rows;z++)for(let x=0;x<map.cols;x++){const p=MAUL_CORE.cellToWorld(map,x,z);if(p.x>box.min.x-.001&&p.x<box.max.x+.001&&p.z>box.min.z-.001&&p.z<box.max.z+.001)map.blocked.push({x,z});}}
    else if(MAUL_CORE.definitions[kind]){const c=maulActorCell(map,a),p=MAUL_CORE.cellToWorld(map,c);if(Math.abs(p.x-position.x)+Math.abs(p.z-position.z)+Math.abs(position.y)>.01||scale.distanceTo(new THREE.Vector3(1,1,1))>.001)errors.push(a.name+': snap the 2 × 2 tower to ground and keep unit scale.');towers.push({id:a.userData.id,kind,cx:c.x,cz:c.z,level:Number(a.userData.maul?.level)||1,priority:a.userData.maul?.priority||'first',owner:'player'});}
  }
  const keyed=(list,label)=>{const result=new Map();for(const a of list){const sector=a.userData.maul?.sector;if(!Number.isInteger(sector)||sector<0||sector>8||result.has(sector))errors.push('Give each '+label+' a unique sector from 0 to 8.');else result.set(sector,a);}return result;};
  const bySpawn=keyed(spawns,'entrance'),byGate=keyed(gates,'beacon');keyed(builders,'builder');for(let i=0;i<9;i++){if(bySpawn.has(i)){const p=maulActorCell(map,bySpawn.get(i));map.spawns[i]={...p,sector:i};map.sectors[i].spawn={...p};}if(byGate.has(i))map.sectors[i].gate=maulActorCell(map,byGate.get(i));}if(exits[0])map.exit=maulActorCell(map,exits[0]);const turns=typed('route-turn'),seenTurns=new Set();for(const a of turns){const key=a.userData.maul?.turnKey;if(!Object.hasOwn(map.turns,key)||seenTurns.has(key))errors.push('Give every lower turn its unique route key.');else{const cell=maulActorCell(map,a),grid=MAUL_CORE.cellToWorld(map,cell),position=a.getWorldPosition(new THREE.Vector3());if(Math.abs(grid.x-position.x)+Math.abs(grid.z-position.z)+Math.abs(position.y)>.01)errors.push(a.name+': snap the lower-lane turn to the 2 × 2 ground grid (Y = 0).');map.turns[key]=cell;seenTurns.add(key);}}if(seenTurns.size!==6)errors.push('Bake all six editable lower-lane turns.');MAUL_LAYOUT_CORE.withGates(map);
  const check=MAUL_LAYOUT_CORE.preflight(map,towers);if(!check.ok)errors.push(...check.errors);for(const a of builders){const c=maulActorCell(map,a),p=a.getWorldPosition(new THREE.Vector3());if(Math.abs(p.y)>.01||map.blocked.some(b=>b.x===c.x&&b.z===c.z)||towers.some(t=>t.cx===c.x&&t.cz===c.z))errors.push(a.name+': place the builder on clear ground.');}
  return {ok:!errors.length,reason:errors[0]||'',errors,map,towers,paths:check.paths};
};
const maulLayoutNativeFrameAt=maulFrameAt,maulLayoutNativeFrameSector=maulFrameSector;
let maulLayoutLastFrame=null;
maulFrameAt=function(target,overview=false){
  if(!maulLayoutActive())return maulLayoutNativeFrameAt(target,overview);
  maulLayoutLastFrame={target:{x:target.x,z:target.z},overview};
  setCameraView('perspective');orbit.maxDistance=800;perspectiveCamera.far=1600;perspectiveCamera.fov=50;perspectiveCamera.clearViewOffset();perspectiveCamera.updateProjectionMatrix();
  orbit.target.set(target.x,0,target.z);perspectiveCamera.position.set(target.x,overview?120:42,target.z+(overview?90:31));perspectiveCamera.lookAt(orbit.target);
  const sector=(maulSession?.map||MAUL_LAYOUT_CORE.mapDefault()).sectors[maulSession?.selectedSector??maulUI.sector??0],width=overview?110:Math.max(24,(sector.maxX-sector.minX+1)*2+5),height=overview?112:Math.max(22,(sector.maxZ-sector.minZ+1)*2+5);
  const rect=renderer.domElement.getBoundingClientRect(),runtime=!!maulSession&&(playing||simulating),touch=innerWidth<=620;
  let safeTop=rect.top+rect.height*.10,safeBottom=rect.bottom-rect.height*.10;
  if(runtime){const header=$('maulHUD')?.querySelector('.maul-wave-banner')?.getBoundingClientRect(),bar=$('maulHUD')?.querySelector('.maul-commandbar')?.getBoundingClientRect();safeTop=Math.max(safeTop,(header?.bottom||rect.top)+16);safeBottom=Math.min(safeBottom,(bar?.top||rect.bottom)-16-(touch?80:0));}
  if(safeBottom-safeTop<120){safeTop=rect.top+rect.height*.24;safeBottom=rect.top+rect.height*.58;}
  const center=(safeTop+safeBottom)/2,half=(safeBottom-safeTop)/2;
  if(runtime)perspectiveCamera.setViewOffset(rect.width,rect.height,0,rect.top+rect.height/2-center,rect.width,rect.height);
  for(let pass=0;pass<8;pass++){perspectiveCamera.updateMatrixWorld();let fit=0;for(const dx of [-width/2,width/2])for(const dz of [-height/2,height/2]){const p=new THREE.Vector3(target.x+dx,0,target.z+dz).project(perspectiveCamera),y=rect.top+(1-p.y)*rect.height/2;fit=Math.max(fit,Math.abs(p.x)/.88,Math.abs(y-center)/half);}if(fit<=1)break;perspectiveCamera.position.sub(orbit.target).multiplyScalar(fit*1.025).add(orbit.target);perspectiveCamera.lookAt(orbit.target);}
  if(scene.fog?.isFog){scene.fog.near=350;scene.fog.far=1300;}orbit.update();
};
maulFrameSector=function(index){if(!maulLayoutActive())return maulLayoutNativeFrameSector(index);index=Math.max(0,Math.min(8,Number(index)||0));maulUI.sector=index;if($('maulSector'))$('maulSector').value=String(index);if(maulSession)maulSession.selectedSector=index;const map=maulSession?.map||MAUL_LAYOUT_CORE.mapDefault(),p=MAUL_CORE.cellToWorld(map,map.sectors[index].focus);maulFrameAt(p);maulClearPreview();maulRefreshHUD(true);};
window.SWYRL_ENGINE_MAUL.preflight=()=>maulAuthoredMap();window.SWYRL_ENGINE_MAUL.frameSector=index=>maulFrameSector(index);window.SWYRL_ENGINE_MAUL.frameMap=()=>maulFrameMap();window.SWYRL_ENGINE_MAUL.layoutStatus=()=>({layout:currentProject.maulLayout||'tile-board-v1',classic:maulLayoutActive(),project:currentProject.canonicalId});
const maulLayoutNativeCollect=stRunCollectProject;
stRunCollectProject=function(run){const record=maulLayoutNativeCollect(run);if(run.mode==='maul'&&maulSession?.map.layout==='classic-v2')for(const unit of maulSession.units){const entity=record.entities[unit.id];if(entity){entity.stage=unit.stage;entity.route.stage=unit.stage;}}return record;};
const maulLayoutNativeCamera=stRunCamera;
stRunCamera=function(){const data=maulLayoutNativeCamera();if(data&&maulLayoutActive()){data.projectionMatrix=perspectiveCamera.projectionMatrix.elements.slice();data.view=perspectiveCamera.view?{...perspectiveCamera.view}:null;}return data;};
const maulLayoutNativeWords=stRunWords;
stRunWords=function(runOrId=null,time=null){const text=maulLayoutNativeWords(runOrId,time),run=stRunResolve(runOrId),frame=stRunFrame(run,time);if(run?.project?.project?.maulLayout==='classic-v2'&&frame?.camera?.view?.enabled){const v=frame.camera.view;return text+'\n\nRecorded lens window: '+v.width+' × '+v.height+' pixels; shift '+v.offsetX+', '+v.offsetY+' pixels within '+v.fullWidth+' × '+v.fullHeight+'. The saved projection matrix preserves this framing.';}return text;};
window.SWYRL_ENGINE_RUNS.words=stRunWords;
const maulLayoutNativeBuildKind=maulSetBuildKind,maulLayoutNativeSelectTower=maulSelectTower,maulLayoutNativeHandleTap=maulUIHandleTap;
let maulLayoutHUDRefitDepth=0,maulLayoutHUDRefitPending=false;
function maulLayoutRefitHUD(){
  if(!maulLayoutActive()||!maulSession||innerWidth>620||!maulLayoutLastFrame||maulUI.gesture)return;
  if(maulLayoutHUDRefitDepth){maulLayoutHUDRefitPending=true;return;}
  maulFrameAt({x:orbit.target.x,z:orbit.target.z},maulLayoutLastFrame.overview);
}
maulSetBuildKind=function(...args){const result=maulLayoutNativeBuildKind(...args);maulLayoutRefitHUD();return result;};
maulSelectTower=function(...args){const result=maulLayoutNativeSelectTower(...args);maulLayoutRefitHUD();return result;};
maulUIHandleTap=function(...args){
  if(!maulLayoutActive()||innerWidth>620)return maulLayoutNativeHandleTap(...args);
  // Deselecting a tower changes HUD height. Keep the same lens until the
  // original tap has raycast its screen coordinates and issued the order.
  maulLayoutHUDRefitDepth++;
  try{return maulLayoutNativeHandleTap(...args);}
  finally{maulLayoutHUDRefitDepth--;if(!maulLayoutHUDRefitDepth&&maulLayoutHUDRefitPending){maulLayoutHUDRefitPending=false;maulLayoutRefitHUD();}}
};

let maulLayoutEditorProjection=null;
const maulLayoutNativeStart=maulStartSession,maulLayoutNativeStop=stopSession;
maulStartSession=function(simulate=false){if(maulLayoutActive()){if(playing||simulating)stopSession();maulLayoutEditorProjection=perspectiveCamera.view?{...perspectiveCamera.view}:null;}return maulLayoutNativeStart(simulate);};
stopSession=function(...args){const classic=maulSession?.map.layout==='classic-v2',view=maulLayoutEditorProjection,result=maulLayoutNativeStop(...args);if(classic){if(view?.enabled)perspectiveCamera.setViewOffset(view.fullWidth,view.fullHeight,view.offsetX,view.offsetY,view.width,view.height);else perspectiveCamera.clearViewOffset();perspectiveCamera.updateProjectionMatrix();maulLayoutEditorProjection=null;}return result;};
window.addEventListener('resize',()=>{if(maulLayoutActive()&&maulSession)requestAnimationFrame(()=>{if(maulSession)maulFrameSector(maulSession.selectedSector);});});
