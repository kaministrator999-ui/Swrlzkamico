// §E v11.141 · native, independently editable Sheep Tag menu/game levels.
// Replace v11.140's transient editor cinematic with authored scene data.
// Preview in editor is STATIC. Playback animates native actors only in Play.
st140MenuOpen=function(){return false;}; // old editor autorun is retired
const st141Levels={menu:null,game:null,bar:null,inspector:null,preview:null,active:false,
 baseline:null,camera:null,overlay:null,time:0,loadGuard:false,playCount:0,stopCount:0};
function st141Which(){
 if(currentProject?.sheepTagLevel==='menu'||currentProject?.canonicalId==='sheep-tag-menu-level')return 'menu';
 if(currentProject?.sheepTagLevel==='game'||currentProject?.canonicalId==='sheep-tag-meadow')return 'game';
 return null;
}
function st141IsPackage(){return !!st141Levels.menu&&!!st141Levels.game&&
 currentProject?.kind==='sheep-tag'&&!!st141Which();}
function st141Text(){const c=currentProject?.sheepTagMenu||{};
 return {eyebrow:String(c.eyebrow||'MOONBELL MEADOW').slice(0,90),
 title:String(c.title||'SHEEP TAG').slice(0,100),
 subtitle:String(c.subtitle||'Build. Flee. Survive.').slice(0,130),
 button:String(c.button||'START GAME').slice(0,64),
 buttonColor:/^#[a-f0-9]{6}$/i.test(c.buttonColor||'')?c.buttonColor:'#e6c66b',
 orbitSeconds:Math.max(25,Math.min(120,Number(c.orbitSeconds)||60))};}
function st141EnsureUI(){
 if(!$('playBtn')||!$('viewport'))return;
 if(!st141Levels.bar){
  const bar=document.createElement('div');
  bar.id='st141LevelBar';bar.className='st141-levelbar';
  bar.innerHTML='<span class="st141-caption">Sheep Tag · Levels</span>'+
   '<button type="button" data-level="menu">Edit Menu</button>'+
   '<button type="button" data-level="game">Edit Gameplay</button>'+
   '<button type="button" id="st141Customize">Menu UI</button>'+
   '<button type="button" id="st141Export">Export Level</button>';
  $('playBtn').before(bar);
  bar.querySelector('[data-level="menu"]').onclick=()=>st141Switch('menu');
  bar.querySelector('[data-level="game"]').onclick=()=>st141Switch('game');
  bar.querySelector('#st141Customize').onclick=()=>st141ToggleInspector();
  bar.querySelector('#st141Export').onclick=st141ExportCurrentLevel;
  st141Levels.bar=bar;
 }
 if(!st141Levels.inspector){
  const panel=document.createElement('section');
  panel.id='st141MenuInspector';panel.hidden=true;panel.className='st141-inspector';
  panel.setAttribute('aria-label','Edit Sheep Tag menu UI');
  panel.innerHTML='<div class="st141-inspector-head"><b>Edit Main Menu UI</b><button id="st141InspectorClose" type="button" aria-label="Close">×</button></div>'+
   '<label>Overline<input data-menu-field="eyebrow" maxlength="90"></label>'+
   '<label>Title<input data-menu-field="title" maxlength="100"></label>'+
   '<label>Subtitle<input data-menu-field="subtitle" maxlength="130"></label>'+
   '<label>Start button label<input data-menu-field="button" maxlength="64"></label>'+
   '<label>Button color<input type="color" data-menu-field="buttonColor"></label>'+
   '<label>Camera orbit seconds<input type="number" min="25" max="120" data-menu-field="orbitSeconds"></label>'+
   '<p>Move and scale sheep, houses, wolves and trees with the normal §e editor tools. The title and button are editable here; their animation plays only in Play mode.</p>';
  panel.querySelector('#st141InspectorClose').onclick=()=>{panel.hidden=true;};
  for(const input of panel.querySelectorAll('[data-menu-field]')){
   input.addEventListener('input',()=>{
    if(!st141IsPackage()||st141Which()!=='menu')return;
    const key=input.dataset.menuField;
    currentProject.sheepTagMenu={...st141Text(),[key]:key==='orbitSeconds'?Math.max(25,Math.min(120,Number(input.value)||60)):input.value};
    st141RefreshPreview();
   });
  }
  $('viewport').parentElement?.appendChild(panel);
  st141Levels.inspector=panel;
 }
 if(!st141Levels.preview){
  const section=document.createElement('section');
  section.id='st141MenuPreview';section.className='st141-menu-ui st141-preview';
  section.setAttribute('aria-label','Editable menu UI preview');
  section.innerHTML='<div class="st141-menu-panel"><small data-menu-text="eyebrow"></small>'+
   '<h1 data-menu-text="title"></h1><p data-menu-text="subtitle"></p>'+
   '<button type="button" tabindex="-1" disabled data-menu-text="button"></button></div>';
  $('viewport').appendChild(section);st141Levels.preview=section;
 }
 st141RefreshEditor();
}
function st141RefreshPreview(root=st141Levels.preview){
 if(!root)return;
 const c=st141Text();
 for(const el of root.querySelectorAll('[data-menu-text]'))el.textContent=c[el.dataset.menuText];
 root.style.setProperty('--st141-gold',c.buttonColor);
}
function st141RefreshEditor(){
 const editing=st141IsPackage()&&!st141Levels.active;
 const level=st141Which();
 if(st141Levels.bar){
  st141Levels.bar.hidden=!editing;
  for(const button of st141Levels.bar.querySelectorAll('[data-level]')){
   button.setAttribute('aria-pressed',String(button.dataset.level===level));
  }
  const ui=st141Levels.bar.querySelector('#st141Customize');
  if(ui)ui.hidden=level!=='menu';
 }
 if(st141Levels.inspector){
  if(!editing||level!=='menu')st141Levels.inspector.hidden=true;
 }
 if(st141Levels.preview){
  st141Levels.preview.hidden=!(editing&&level==='menu');
  if(!st141Levels.preview.hidden)st141RefreshPreview();
 }
}
function st141ToggleInspector(){
 if(st141Which()!=='menu'||st141Levels.active)return;
 st141EnsureUI();
 const panel=st141Levels.inspector;
 panel.hidden=!panel.hidden;
 if(!panel.hidden){
  const values=st141Text();
  for(const input of panel.querySelectorAll('[data-menu-field]'))input.value=values[input.dataset.menuField];
 }
}
function st141SnapshotCurrent(){
 if(!st141IsPackage()||st141Levels.active)return;
 const level=st141Which();
 if(level)st141Levels[level]=structuredClone(projectData());
}
function st141MenuEditorCamera(){
 if(currentProject?.kind!=='sheep-tag'||st141Which()!=='menu')return;
 setCameraView('perspective');
 perspectiveCamera.position.set(0,29,32);orbit.target.set(0,0,0);
 perspectiveCamera.lookAt(orbit.target);orbit.enabled=true;orbit.update();
}
function st141Switch(level){
 if(!['menu','game'].includes(level)||!st141Levels[level]||st141Levels.active||playing||simulating)return false;
 if(st141Which()===level){st141RefreshEditor();return true;}
 st141SnapshotCurrent();
 st141Levels.loadGuard=true;
 try{
  loadProject(structuredClone(st141Levels[level]),{workspaceLocal:true});
  if(level==='menu')st141MenuEditorCamera();
  else stFrameMap();
  initializeHistory('Opened Sheep Tag '+(level==='menu'?'Main Menu':'Gameplay')+' Level');
  markSaved();
  st141EnsureUI();
  return true;
 }finally{st141Levels.loadGuard=false;}
}
function st141ExportCurrentLevel(){
 if(!st141IsPackage()||st141Levels.active)return false;
 st141SnapshotCurrent();
 const level=st141Which(),source=st141Levels[level];
 const blob=new Blob([JSON.stringify(source,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download=level==='menu'?'sheep-tag-main-menu.swyrl.json':'sheep-tag-gameplay.swyrl.json';
 document.body.appendChild(a);a.click();a.remove();
 URL.revokeObjectURL(url);return true;
}
function st141RemoveOverlay(){
 st141Levels.overlay?.remove();st141Levels.overlay=null;
 $('viewport')?.classList.remove('st141-runtime-menu');
}
function st141Restore(){
 for(const entry of st141Levels.baseline||[]){
  const actor=entry.actor;actor.position.copy(entry.position);
  actor.rotation.copy(entry.rotation);actor.scale.copy(entry.scale);
  actor.visible=entry.visible;
 }
 st141Levels.baseline=null;
 const c=st141Levels.camera;st141Levels.camera=null;
 if(c){
  perspectiveCamera.position.copy(c.position);perspectiveCamera.quaternion.copy(c.quaternion);
  perspectiveCamera.up.copy(c.up);perspectiveCamera.fov=c.fov;
  perspectiveCamera.updateProjectionMatrix();
  orbit.target.copy(c.target);orbit.enabled=c.enabled;orbit.update();
 }
}
function st141StopMenu(){
 if(!st141Levels.active)return false;
 st141Levels.active=false;st141Levels.stopCount++;
 st141RemoveOverlay();
 st141Restore();
 st141RefreshEditor();
 return true;
}
function st141Actor(type){
 return actors.filter(a=>a.userData.actorType===type&&a.userData.baked!==false);
}
function st141StartMenu(){
 if(st141Levels.active||!st141IsPackage()||st141Which()!=='menu'||stSession||playing||simulating)return false;
 const viewport=$('viewport');if(!viewport)return false;
 st141SnapshotCurrent();
 st141Levels.baseline=actors.map(actor=>({actor,position:actor.position.clone(),
  rotation:actor.rotation.clone(),scale:actor.scale.clone(),visible:actor.visible}));
 st141Levels.camera={position:perspectiveCamera.position.clone(),quaternion:perspectiveCamera.quaternion.clone(),
  up:perspectiveCamera.up.clone(),fov:perspectiveCamera.fov,target:orbit.target.clone(),enabled:orbit.enabled};
 orbit.enabled=false;
 st141Levels.active=true;st141Levels.time=0;st141Levels.playCount++;
 const panel=document.createElement('section');
 panel.id='st141RuntimeMenu';panel.className='st141-menu-ui st141-runtime';
 panel.setAttribute('aria-label','Sheep Tag main menu');
 panel.innerHTML='<div class="st141-menu-panel"><small data-menu-text="eyebrow"></small>'+
  '<h1 data-menu-text="title"></h1><p data-menu-text="subtitle"></p>'+
  '<button id="st141StartGame" type="button" data-menu-text="button"></button></div>';
 const button=panel.querySelector('#st141StartGame');
 button.onclick=()=>st141StartGame();
 panel.addEventListener('pointerdown',event=>event.stopPropagation());
 panel.addEventListener('pointerup',event=>event.stopPropagation());
 panel.addEventListener('click',event=>event.stopPropagation());
 st141Levels.overlay=panel;viewport.appendChild(panel);viewport.classList.add('st141-runtime-menu');
 st141RefreshPreview(panel);st141RefreshEditor();
 st141MenuTick(0);
 return true;
}
function st141StartGame(){
 if(!st141Levels.active)return false;
 st141StopMenu();
 if(!st141Switch('game'))return false;
 // The original native Sheep Tag preflight and Play session starts the game.
 return beginPlay();
}
function st141MenuTick(dt){
 if(!st141Levels.active||st141Which()!=='menu')return;
 const now=st141Levels.time+=Math.max(0,Math.min(Number(dt)||0,.05));
 const cycle=now%17,sceneActors=st141Levels.baseline||[];
 const originals=new Map(sceneActors.map(b=>[b.actor,b]));
 const cam=st141Text(),angle=now*Math.PI*2/cam.orbitSeconds;
 const focus=orbit.target;
 perspectiveCamera.position.set(focus.x+Math.cos(angle)*32,21+Math.sin(now*.19)*1.5,focus.z+Math.sin(angle)*35);
 perspectiveCamera.lookAt(focus);perspectiveCamera.updateMatrixWorld();
 const sheep=st141Actor('st-sheep'),wolf=st141Actor('st-wolf'),houses=st141Actor('st-farm');
 sheep.forEach((a,i)=>{
  const b=originals.get(a);if(!b)return;
  const dash=Math.max(0,cycle-3);
  a.position.set(b.position.x-(cycle<3?Math.sin(now*1.5+i)*.35:Math.min(dash,11)*(1.1+i*.12)),
   b.position.y+Math.abs(Math.sin(now*8+i))*.07,
   b.position.z+Math.sin(now*1.2+i)*.25);
  a.rotation.y=b.rotation.y+(cycle<3?Math.sin(now*.5+i)*.3:-Math.PI/2);
  a.visible=!(i===sheep.length-1&&cycle>10&&cycle<13);
 });
 wolf.forEach((a,i)=>{
  const b=originals.get(a);if(!b)return;
  const chase=Math.min(11,Math.max(0,cycle-3));
  a.position.set(b.position.x-chase*1.4,b.position.y+Math.abs(Math.sin(now*9+i))*.04,
   b.position.z+Math.sin(chase*.7)*1.4);
  a.rotation.y=b.rotation.y-Math.PI/2;
 });
 const last=houses[houses.length-1];
 if(last){const b=originals.get(last);if(b){
  const progress=cycle<1?.06:cycle<4?Math.min(1,.06+(cycle-1)/2.8):cycle<15?1:.06;
  last.scale.set(b.scale.x,b.scale.y*progress,b.scale.z);
 }}
}
// Existing v11.140 load wrappers are intentionally bypassed: never run
// attract actors in the editor or auto-start on project load.
const st141LoadProjectBase=loadProject;
loadProject=function(...args){
 if(st141Levels.active)st141StopMenu();
 const result=st141LoadProjectBase(...args);
 if(!st141Levels.loadGuard)st141EnsureUI();
 else st141RefreshEditor();
 return result;
};
stLoadStarter=function(){
 st141StopMenu();
 st141Levels.menu=structuredClone(ST141_CANONICAL_MENU);
 st141Levels.game=structuredClone(ST_CANONICAL_PROJECT);
 st141Levels.game.project.sheepTagLevel='game';
 st141Levels.loadGuard=true;
 try{
  loadProject(structuredClone(st141Levels.menu),{workspaceLocal:true});
 }finally{st141Levels.loadGuard=false;}
 st141MenuEditorCamera();
 initializeHistory('Opened Sheep Tag Main Menu Level');
 markSaved();
 st141EnsureUI();
 editorLog('Sheep Tag · editable Main Menu and Gameplay levels · Play menu to start','ok');
 toast('Sheep Tag · Main Menu Level');
};
const st141NativeBeginPlay=beginPlay;
beginPlay=function(...args){
 if(st141IsPackage()&&st141Which()==='menu')return st141StartMenu();
 return st141NativeBeginPlay(...args);
};
const st141NativeBeginSimulate=beginSimulate;
beginSimulate=function(...args){
 if(st141IsPackage()&&st141Which()==='menu')return st141StartMenu();
 return st141NativeBeginSimulate(...args);
};
const st141NativeStop=stopSession;
stopSession=function(...args){
 if(st141Levels.active){st141StopMenu();return true;}
 return st141NativeStop(...args);
};
// No editor cinematic; the previous callback is a harmless no-op.
const st141LegacyTick=st140MenuTick;
st140MenuTick=function(dt){st141MenuTick(dt);};
window.SWYRL_ENGINE_SHEEP_LEVELS={
 current:()=>st141Which(),
 switchTo:level=>st141Switch(level),
 startMenu:()=>st141StartMenu(),
 stopMenu:()=>st141StopMenu(),
 project:level=>structuredClone(st141Levels[level]||null),
 status:()=>({level:st141Which(),playingMenu:st141Levels.active,menuActors:st141Actor('st-sheep').length,
  menuStarts:st141Levels.playCount,menuStops:st141Levels.stopCount})
};
