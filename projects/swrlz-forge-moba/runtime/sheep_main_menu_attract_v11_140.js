// §E v11.140 — Sheep Tag STARTER-only cinematic title menu.
// Uses the existing editor render clock and native Play; no second game session,
// save-actor creation, simulation, network connection or autonomous wolf AI.
const st140Menu={
 open:false,stage:null,panel:null,visuals:[],houses:[],time:0,cameraState:null,
 opening:false,starting:false,openCount:0,cleanupCount:0
};
function st140MenuRestoreCamera(){
 const c=st140Menu.cameraState;
 st140Menu.cameraState=null;
 if(!c)return;
 perspectiveCamera.position.copy(c.position);
 perspectiveCamera.quaternion.copy(c.quaternion);
 perspectiveCamera.up.copy(c.up);
 perspectiveCamera.fov=c.fov;
 perspectiveCamera.updateProjectionMatrix();
 orbit.target.copy(c.target);
 orbit.enabled=c.enabled;
 orbit.update();
}
function st140MenuClose(){
 if(!st140Menu.open&&!st140Menu.stage&&!st140Menu.panel)return;
 st140Menu.open=false;
 st140Menu.cleanupCount++;
 st140Menu.panel?.remove();
 st140Menu.panel=null;
 $('viewport')?.classList.remove('st140-menu-root');
 if(st140Menu.stage){
  scene.remove(st140Menu.stage);
  stDisposeVisual(st140Menu.stage);
  st140Menu.stage=null;
 }
 st140Menu.visuals.length=0;
 st140Menu.houses.length=0;
 st140MenuRestoreCamera();
}
function st140MenuMakeDemo(){
 const stage=new THREE.Group();
 stage.name='st140-SheepTag-Attract-Transient';
 // Deliberately not registered in actors, project, history, navigation or fog.
 const x=18,z=16,baseY=terrainHeight(x,z)+.12;
 stage.position.set(x,baseY,z);
 const grass=new THREE.Mesh(
  new THREE.CircleGeometry(24,48),
  new THREE.MeshStandardMaterial({color:0x688f60,roughness:1,metalness:0})
 );
 grass.rotation.x=-Math.PI/2;grass.position.y=-.04;grass.receiveShadow=true;
 stage.add(grass);
 const road=new THREE.Mesh(
  new THREE.PlaneGeometry(28,3.6),
  new THREE.MeshStandardMaterial({color:0xb9ae8c,roughness:1})
 );
 road.rotation.x=-Math.PI/2;road.position.y=.012;
 stage.add(road);
 for(const [xx,zz] of [[-13,-9],[-8,11],[13,8]]){
  const tree=stMakeVisual('st-tree');
  tree.position.set(xx,0,zz);tree.scale.setScalar(.75);stage.add(tree);
 }
 for(const [xx,zz] of [[-8,-3],[-4,-3],[0,-3],[-8,1]]){
  const house=stMakeVisual('st-farm');
  house.position.set(xx,0,zz);stage.add(house);
  st140Menu.houses.push(house);
 }
 for(let i=0;i<3;i++){
  const sheep=stMakeVisual('st-sheep');
  sheep.position.set(-2-i*2,0,5+i);stage.add(sheep);
  st140Menu.visuals.push({kind:'sheep',mesh:sheep,index:i});
 }
 const wolf=stMakeVisual('st-wolf');
 wolf.position.set(11,0,5);stage.add(wolf);
 st140Menu.visuals.push({kind:'wolf',mesh:wolf,index:0});
 scene.add(stage);
 return stage;
}
function st140MenuOpen(){
 if(st140Menu.open||st140Menu.opening||st140Menu.starting||
   stSession||playing||simulating||currentProject?.kind!=='sheep-tag')return false;
 const viewport=$('viewport');
 if(!viewport)return false;
 st140Menu.opening=true;
 try{
  st140MenuClose();
  st140Menu.cameraState={
   position:perspectiveCamera.position.clone(),quaternion:perspectiveCamera.quaternion.clone(),
   up:perspectiveCamera.up.clone(),fov:perspectiveCamera.fov,
   target:orbit.target.clone(),enabled:orbit.enabled
  };
  orbit.enabled=false;
  st140Menu.time=0;
  st140Menu.stage=st140MenuMakeDemo();
  const menu=document.createElement('section');
  menu.id='st140MainMenu';
  menu.className='st140-main-menu';
  menu.setAttribute('role','region');
  menu.setAttribute('aria-label','Sheep Tag main menu');
  menu.innerHTML='<div class="st140-menu-vignette" aria-hidden="true"></div>'+
   '<div class="st140-menu-content"><div class="st140-menu-eyebrow">MOONBELL MEADOW</div>'+
   '<h1>SHEEP <span>TAG</span></h1>'+
   '<p>Build. Flee. Survive.</p>'+
   '<button id="st140StartGame" type="button">▶ START GAME</button></div>';
  menu.addEventListener('pointerdown',event=>event.stopPropagation());
  menu.addEventListener('pointerup',event=>event.stopPropagation());
  menu.addEventListener('click',event=>event.stopPropagation());
  const start=menu.querySelector('#st140StartGame');
  start.addEventListener('click',st140MenuStart);
  viewport.classList.add('st140-menu-root');
  viewport.appendChild(menu);
  st140Menu.panel=menu;
  st140Menu.open=true;
  st140Menu.openCount++;
  st140MenuTick(0,0);
  return true;
 }catch(error){
  st140MenuClose();
  console.error('Sheep Tag menu could not initialize',error);
  return false; // editor/Play remains accessible, never strand the user
 }finally{st140Menu.opening=false;}
}
function st140MenuStart(){
 if(!st140Menu.open||st140Menu.starting)return false;
 st140Menu.starting=true;
 try{
  // The native editor Play handler owns preflight, session initialization,
  // bot rosters, camera/fog, timers and HUD. No duplicate state allowed.
  st140MenuClose();
  const play=$('playBtn');
  if(!play||play.disabled){toast('Sheep Tag Play is unavailable.');return false;}
  play.click();
  return true;
 }finally{st140Menu.starting=false;}
}
function st140MenuTick(dt){
 if(!st140Menu.open||!st140Menu.stage)return;
 // Lightweight scripted, purely visual 17-second attract cycle. Actors and
 // rules remain untouched; the expensive Sheep Tag navigation never runs.
 const m=st140Menu;
 m.time+=Math.max(0,Math.min(Number(dt)||0,.05));
 const t=m.time,cycle=t%17,center=m.stage.position;
 const a=t*.105;
 const focus=new THREE.Vector3(center.x,center.y+2,center.z);
 perspectiveCamera.position.set(center.x+Math.cos(a)*28,center.y+18+Math.sin(t*.16)*2,
  center.z+Math.sin(a)*29);
 perspectiveCamera.lookAt(focus);
 perspectiveCamera.updateMatrixWorld();
 // House #4 appears as though a sheep is building, then resets next loop.
 const growth=cycle<1?.04:cycle<4?Math.min(1,.04+(cycle-1)/2.4):cycle<15?1:.04;
 const building=m.houses[3];
 if(building){building.scale.set(1,Math.max(.04,growth),1);building.visible=true;}
 for(const actor of m.visuals){
  const obj=actor.mesh,i=actor.index;
  if(actor.kind==='wolf'){
   const chase=Math.max(0,cycle-3);
   obj.position.set(12-Math.min(chase,9)*1.6,.05+Math.sin(t*9)*.045,6+Math.sin(chase*.7)*2.2);
   obj.rotation.y=-Math.PI/2+.15*Math.sin(t);
  }else{
   const fleeing=Math.max(0,cycle-3);
   const drift=cycle<3?Math.sin(t*1.3+i)*.45:Math.min(fleeing,10)*(2.3+i*.17);
   obj.position.set(-3-i*2-drift,.07+Math.abs(Math.sin(t*8+i))*.08,4+i*2+Math.sin(t*1.2+i)*.6);
   obj.rotation.y=cycle<3?Math.sin(t*.8+i)*.4:-Math.PI/2;
   // Short visual disappearance indicates a tag, with a looped reset.
   obj.visible=!(i===2&&cycle>10.6&&cycle<13.1);
  }
 }
}
const st140LoadStarterBase=stLoadStarter;
stLoadStarter=function(...args){
 const value=st140LoadStarterBase(...args);
 st140MenuOpen();
 return value;
};
const st140LoadProjectBase=loadProject;
loadProject=function(...args){
 st140MenuClose();
 return st140LoadProjectBase(...args);
};
