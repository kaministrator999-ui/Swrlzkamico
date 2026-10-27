// §E v11.141 · project-wide authored level collection, Sheep Tag menu example.
// Editor loads SCENE DATA only. Runtime animations are confined to native Play.
// Full project exports contain separate level snapshots with no cyclic nesting.
st140MenuOpen=function(){return false;};
const seLevels={records:new Map(),root:'',active:'',loading:false,playingMenu:false,
 baseline:null,camera:null,overlay:null,bar:null,preview:null,inspector:null,
 time:0,ordinal:0,playCount:0,stopCount:0};
function seLevelKey(data){
 const p=data?.project||currentProject||{};
 return String(p.levelPack?.root||p.canonicalId||p.name||'unsaved-project');
}
function seLevelStrip(data){
 const value=structuredClone(data);
 if(value?.project){delete value.project.levelPack;delete value.project.levelSystem;}
 return value;
}
function seLevelRecord(id,name,data,role='map',next=''){
 return {id,name,role,next,data:seLevelStrip(data)};
}
function seLevelsCurrent(){return seLevels.records.get(seLevels.active)||null;}
function seLevelsOwns(){return seLevels.records.size>0 && currentProject &&
 seLevelKey({project:currentProject})===seLevels.root;}
function seLevelsRaw(){return seLevelStrip(seLevelRawProjectData());}
function seLevelsCapture(){
 if(!seLevelsOwns()||seLevels.playingMenu||playing||simulating||stSession)return;
 const rec=seLevelsCurrent();if(!rec)return;
 const data=seLevelsRaw();
 rec.data=data;
}
function seLevelsHydrate(data){
 const pkg=data?.project?.levelPack;
 if(!pkg||pkg.schema!=='se-levels-v1'||!Array.isArray(pkg.levels)||!pkg.levels.length)return false;
 const records=new Map();
 for(const l of pkg.levels){
  if(typeof l.id!=='string'||!l.id||records.has(l.id)||!l.data?.project||!l.data?.scene)continue;
  records.set(l.id,seLevelRecord(l.id,String(l.name||l.id).slice(0,90),l.data,
    l.role==='menu'?'menu':l.role==='game'?'game':'map',typeof l.next==='string'?l.next:''));
 }
 if(!records.size)return false;
 seLevels.records=records;
 seLevels.root=String(pkg.root||seLevelKey(data));
 seLevels.active=records.has(pkg.active)?pkg.active:records.keys().next().value;
 seLevels.ordinal=records.size;
 return true;
}
function seLevelsInitSingle(data){
 const root=seLevelKey(data);
 seLevels.root=root;seLevels.records=new Map();
 seLevels.records.set('level-1',seLevelRecord('level-1',data?.project?.name||'Level 1',data,
  data?.project?.kind==='sheep-tag'?'game':'map'));
 seLevels.active='level-1';seLevels.ordinal=1;
}
function seLevelsBundle(){
 const levels=[...seLevels.records.values()].map(x=>({
  id:x.id,name:x.name,role:x.role,next:x.next,data:seLevelStrip(x.data)
 }));
 return {schema:'se-levels-v1',root:seLevels.root,active:seLevels.active,levels};
}
const seLevelRawProjectData=projectData;
projectData=function(...args){
 const data=seLevelRawProjectData(...args);
 if(!seLevels.loading&&seLevelsOwns()&&!playing&&!simulating&&!stSession&&!seLevels.playingMenu){
  seLevelsCapture();
  data.project.levelPack=seLevelsBundle();
  data.project.levelSystem={schema:'se-levels-v1',current:seLevels.active,
   levels:[...seLevels.records.values()].map(l=>({id:l.id,name:l.name,role:l.role,next:l.next}))};
 }
 return data;
};
const seLevelRawLoadProject=loadProject;
loadProject=function(data,...args){
 if(seLevels.playingMenu)seLevelsStopMenu();
 const internal=seLevels.loading;
 const result=seLevelRawLoadProject(data,...args);
 if(!internal){
  if(!seLevelsHydrate(data))seLevelsInitSingle(data);
  // If opening a project bundle with a different saved active level, load
  // the selected level using the native loader but without recursive wrappers.
  const chosen=seLevelsCurrent();
  if(chosen?.data?.scene&&data.project?.levelPack){
   seLevels.loading=true;
   try{seLevelRawLoadProject(structuredClone(chosen.data),{workspaceLocal:true});}
   finally{seLevels.loading=false;}
  }
 }
 seLevelsEnsureUI();seLevelsRefresh();
 return result;
};
function seLevelsSwitch(id){
 if(!seLevels.records.has(id)||seLevels.playingMenu||playing||simulating||stSession)return false;
 if(!seLevels.loading)seLevelsCapture();
 const selected=seLevels.records.get(id);
 seLevels.loading=true;
 try{
  seLevelRawLoadProject(structuredClone(selected.data),{workspaceLocal:true});
  seLevels.active=id;
  initializeHistory('Opened '+selected.name);
  if(currentProject?.kind==='sheep-tag'&&selected.role==='game')stFrameMap();
  if(selected.role==='menu'&&currentProject?.kind==='sheep-tag')seLevelsMenuEditorCamera();
 }finally{seLevels.loading=false;}
 seLevelsEnsureUI();seLevelsRefresh();return true;
}
function seLevelsCreate(name){
 if(!seLevelsOwns()||seLevels.playingMenu||playing||simulating||stSession)return null;
 seLevelsCapture();
 const source=seLevelsRaw(),id='level-'+(++seLevels.ordinal);
 const title=String(name||'New Map '+seLevels.ordinal).trim().slice(0,90)||'New Level';
 source.project.name=title;
 source.project.canonicalId=seLevels.root+'-'+id;
 source.scene.actors=currentProject?.kind==='sheep-tag'?
  source.scene.actors.filter(a=>a.type==='st-meadow').map(a=>structuredClone(a)):[];
 if(source.project.kind==='sheep-tag')source.project.sheepTagLevel='map';
 seLevels.records.set(id,seLevelRecord(id,title,source,'map'));
 seLevelsSwitch(id);return id;
}
function seLevelsLink(from,to){
 if(!seLevels.records.has(from)||to&&!seLevels.records.has(to))return false;
 seLevels.records.get(from).next=to||'';seLevelsRefresh();return true;
}
function seLevelsRename(id,name){
 if(!seLevels.records.has(id))return false;
 const value=String(name||'').trim().slice(0,90);if(!value)return false;
 seLevels.records.get(id).name=value;
 if(id===seLevels.active)currentProject.name=value;
 seLevelsRefresh();return true;
}
function seLevelsTransition(to,autoPlay=true){
 const from=seLevelsCurrent(),destination=to||from?.next;
 if(!destination||!seLevels.records.has(destination))return false;
 if(seLevels.playingMenu)seLevelsStopMenu();
 if(playing||simulating||stSession)stopSession();
 if(!seLevelsSwitch(destination))return false;
 if(autoPlay)return !!beginPlay();
 return true;
}
function seLevelsEditUI(){
 if(!seLevelsOwns()||seLevelsCurrent()?.role!=='menu'||seLevels.playingMenu)return;
 const panel=seLevels.inspector;if(!panel)return;
 panel.hidden=!panel.hidden;
 if(panel.hidden)return;
 const values=seLevelsMenuText();
 for(const input of panel.querySelectorAll('[data-menu-field]'))input.value=values[input.dataset.menuField];
}
function seLevelsMenuText(){
 const c=currentProject?.sheepTagMenu||{};
 return {eyebrow:String(c.eyebrow||'MOONBELL MEADOW').slice(0,90),
 title:String(c.title||'SHEEP TAG').slice(0,100),
 subtitle:String(c.subtitle||'Build. Flee. Survive.').slice(0,130),
 button:String(c.button||'START GAME').slice(0,64),
 buttonColor:/^#[0-9a-f]{6}$/i.test(c.buttonColor||'')?c.buttonColor:'#e6c66b',
 orbitSeconds:Math.max(25,Math.min(120,Number(c.orbitSeconds)||60))};
}
function seLevelsPaintMenu(root){
 if(!root)return;
 const m=seLevelsMenuText();
 for(const el of root.querySelectorAll('[data-menu-text]'))el.textContent=m[el.dataset.menuText];
 root.style.setProperty('--st141-gold',m.buttonColor);
}
function seLevelsEnsureUI(){
 const play=$('playBtn'),viewport=$('viewport');
 if(!play||!viewport)return;
 if(!seLevels.bar){
  const bar=document.createElement('div');
  bar.id='st141LevelBar';bar.className='st141-levelbar';
  bar.innerHTML='<span class="st141-caption">Project Levels</span>'+
   '<select id="st141LevelSelect" aria-label="Edit level"></select>'+
   '<button type="button" id="st141NewLevel">+ New Map</button>'+
   '<input id="st141LevelName" aria-label="Level name" maxlength="90">'+
   '<label>Next <select id="st141LevelNext" aria-label="Connect next level"></select></label>'+
   '<button type="button" id="st141Customize">Menu UI</button>'+
   '<button type="button" id="st141Export">Export Level</button>';
  play.before(bar);
  bar.querySelector('#st141LevelSelect').onchange=e=>seLevelsSwitch(e.target.value);
  bar.querySelector('#st141NewLevel').onclick=()=>seLevelsCreate();
  bar.querySelector('#st141LevelName').onchange=e=>seLevelsRename(seLevels.active,e.target.value);
  bar.querySelector('#st141LevelNext').onchange=e=>seLevelsLink(seLevels.active,e.target.value);
  bar.querySelector('#st141Customize').onclick=seLevelsEditUI;
  bar.querySelector('#st141Export').onclick=seLevelsExportLevel;
  seLevels.bar=bar;
 }
 if(!seLevels.inspector){
  const panel=document.createElement('section');panel.id='st141MenuInspector';
  panel.hidden=true;panel.className='st141-inspector';
  panel.innerHTML='<div class="st141-inspector-head"><b>Edit Main Menu UI</b>'+
   '<button id="st141InspectorClose" type="button" aria-label="Close">×</button></div>'+
   '<label>Overline<input data-menu-field="eyebrow" maxlength="90"></label>'+
   '<label>Title<input data-menu-field="title" maxlength="100"></label>'+
   '<label>Subtitle<input data-menu-field="subtitle" maxlength="130"></label>'+
   '<label>Start button label<input data-menu-field="button" maxlength="64"></label>'+
   '<label>Button color<input type="color" data-menu-field="buttonColor"></label>'+
   '<label>Camera orbit seconds<input type="number" min="25" max="120" data-menu-field="orbitSeconds"></label>'+
   '<p>All menu actors are editable in the normal viewport. Camera and chase animation run only in Play. Save Project to retain all levels.</p>';
  panel.querySelector('#st141InspectorClose').onclick=()=>{panel.hidden=true;};
  for(const input of panel.querySelectorAll('[data-menu-field]'))input.oninput=()=>{
   if(!seLevelsOwns()||seLevelsCurrent()?.role!=='menu'||seLevels.playingMenu)return;
   const key=input.dataset.menuField;
   currentProject.sheepTagMenu={...seLevelsMenuText(),[key]:key==='orbitSeconds'?
    Math.max(25,Math.min(120,Number(input.value)||60)):input.value};
   seLevelsPaintMenu(seLevels.preview);
  };
  viewport.parentElement?.appendChild(panel);seLevels.inspector=panel;
 }
 if(!seLevels.preview){
  const el=document.createElement('section');el.id='st141MenuPreview';
  el.className='st141-menu-ui st141-preview';
  el.innerHTML='<div class="st141-menu-panel"><small data-menu-text="eyebrow"></small>'+
   '<h1 data-menu-text="title"></h1><p data-menu-text="subtitle"></p>'+
   '<button type="button" tabindex="-1" disabled data-menu-text="button"></button></div>';
  viewport.appendChild(el);seLevels.preview=el;
 }
}
function seLevelsRefresh(){
 if(!seLevels.bar)return;
 const visible=seLevelsOwns()&&!playing&&!simulating&&!stSession&&!seLevels.playingMenu;
 seLevels.bar.hidden=!visible;
 const current=seLevelsCurrent();
 if(!current)return;
 const levelSelect=seLevels.bar.querySelector('#st141LevelSelect'),
 nextSelect=seLevels.bar.querySelector('#st141LevelNext');
 if(visible){
  levelSelect.replaceChildren(...[...seLevels.records.values()].map(l=>{
   const el=document.createElement('option');el.value=l.id;el.textContent=l.name;return el;
  }));
  levelSelect.value=seLevels.active;
  nextSelect.replaceChildren(...[{id:'',name:'None'},...[...seLevels.records.values()].filter(l=>l.id!==seLevels.active)].map(l=>{
   const el=document.createElement('option');el.value=l.id;el.textContent=l.name;return el;
  }));
  nextSelect.value=current.next;
  const name=seLevels.bar.querySelector('#st141LevelName');
  if(document.activeElement!==name)name.value=current.name;
  seLevels.bar.querySelector('#st141Customize').hidden=current.role!=='menu';
 }
 if(seLevels.preview){seLevels.preview.hidden=!(visible&&current.role==='menu');
  if(!seLevels.preview.hidden)seLevelsPaintMenu(seLevels.preview);}
 if(seLevels.inspector&&(!visible||current.role!=='menu'))seLevels.inspector.hidden=true;
}
function seLevelsExportLevel(){
 if(!seLevelsOwns()||playing||simulating||stSession)return false;
 seLevelsCapture();
 const current=seLevelsCurrent();
 if(!current)return false;
 const blob=new Blob([JSON.stringify(current.data,null,2)+'\n'],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download=current.id+'.swyrl.json';
 document.body.appendChild(a);a.click();a.remove();
 URL.revokeObjectURL(url);return true;
}
// Cinematic uses native menu actors and preserves author-edited transforms.
function seLevelsMenuActors(type){
 return actors.filter(a=>a.userData?.actorType===type);
}
function seLevelsMenuEditorCamera(){
 setCameraView('perspective');
 perspectiveCamera.position.set(0,29,32);orbit.target.set(0,0,0);
 perspectiveCamera.lookAt(orbit.target);orbit.enabled=true;orbit.update();
}
function seLevelsStopMenu(){
 if(!seLevels.playingMenu)return false;
 seLevels.playingMenu=false;seLevels.stopCount++;
 seLevels.overlay?.remove();seLevels.overlay=null;
 $('viewport')?.classList.remove('st141-runtime-menu');
 for(const old of seLevels.baseline||[]){
  old.actor.position.copy(old.position);old.actor.rotation.copy(old.rotation);
  old.actor.scale.copy(old.scale);old.actor.visible=old.visible;
 }
 seLevels.baseline=null;
 const c=seLevels.camera;seLevels.camera=null;
 if(c){
  perspectiveCamera.position.copy(c.position);perspectiveCamera.quaternion.copy(c.quaternion);
  perspectiveCamera.up.copy(c.up);perspectiveCamera.fov=c.fov;
  perspectiveCamera.updateProjectionMatrix();
  orbit.target.copy(c.target);orbit.enabled=c.enabled;orbit.update();
 }
 seLevelsRefresh();return true;
}
function seLevelsPlayMenu(){
 if(seLevels.playingMenu||!seLevelsOwns()||seLevelsCurrent()?.role!=='menu'||
  playing||simulating||stSession)return false;
 const viewport=$('viewport');if(!viewport)return false;
 seLevelsCapture();
 seLevels.baseline=actors.map(actor=>({actor,position:actor.position.clone(),
  rotation:actor.rotation.clone(),scale:actor.scale.clone(),visible:actor.visible}));
 seLevels.camera={position:perspectiveCamera.position.clone(),quaternion:perspectiveCamera.quaternion.clone(),
  up:perspectiveCamera.up.clone(),fov:perspectiveCamera.fov,target:orbit.target.clone(),enabled:orbit.enabled};
 orbit.enabled=false;seLevels.playingMenu=true;seLevels.time=0;seLevels.playCount++;
 const el=document.createElement('section');el.id='st141RuntimeMenu';el.className='st141-menu-ui st141-runtime';
 el.innerHTML='<div class="st141-menu-panel"><small data-menu-text="eyebrow"></small>'+
  '<h1 data-menu-text="title"></h1><p data-menu-text="subtitle"></p>'+
  '<button type="button" id="st141StartGame" data-menu-text="button"></button></div>';
 el.querySelector('#st141StartGame').onclick=()=>seLevelsTransition('',true);
 for(const type of ['pointerdown','pointerup','click'])el.addEventListener(type,e=>e.stopPropagation());
 viewport.appendChild(el);viewport.classList.add('st141-runtime-menu');
 seLevels.overlay=el;seLevelsPaintMenu(el);seLevelsRefresh();seLevelsMenuTick(0);return true;
}
function seLevelsMenuTick(dt){
 if(!seLevels.playingMenu||seLevelsCurrent()?.role!=='menu')return;
 const t=seLevels.time+=Math.max(0,Math.min(Number(dt)||0,.05)),cycle=t%17;
 const baseline=new Map((seLevels.baseline||[]).map(e=>[e.actor,e]));
 const m=seLevelsMenuText(),angle=t*Math.PI*2/m.orbitSeconds;
 perspectiveCamera.position.set(Math.cos(angle)*32,21+Math.sin(t*.18)*1.6,Math.sin(angle)*35);
 perspectiveCamera.lookAt(0,1,0);perspectiveCamera.updateMatrixWorld();
 seLevelsMenuActors('st-sheep').forEach((actor,i)=>{
  const b=baseline.get(actor);if(!b)return;
  const run=Math.max(0,cycle-3);
  actor.position.set(b.position.x-(cycle<3?Math.sin(t*1.3+i)*.35:Math.min(run,10)*(1.15+i*.13)),
   b.position.y+Math.abs(Math.sin(t*8+i))*.08,b.position.z+Math.sin(t*1.3+i)*.3);
  actor.rotation.y=b.rotation.y+(cycle<3?Math.sin(t*.5+i)*.3:-Math.PI/2);
  actor.visible=!(i===2&&cycle>10&&cycle<13);
 });
 seLevelsMenuActors('st-wolf').forEach((actor,i)=>{
  const b=baseline.get(actor);if(!b)return;
  const chase=Math.min(11,Math.max(0,cycle-3));
  actor.position.set(b.position.x-chase*1.4,b.position.y+Math.abs(Math.sin(t*9+i))*.05,
   b.position.z+Math.sin(chase*.7)*1.3);
  actor.rotation.y=b.rotation.y-Math.PI/2;
 });
 const house=seLevelsMenuActors('st-farm').at(-1),base=baseline.get(house);
 if(base){
  const growth=cycle<1?.06:cycle<4?Math.min(1,.06+(cycle-1)/2.8):cycle<15?1:.06;
  house.scale.set(base.scale.x,base.scale.y*growth,base.scale.z);
 }
}
// Starter opens the editable menu LEVEL in edit mode, not its cinematic.
stLoadStarter=function(){
 seLevelsStopMenu();
 const menu=seLevelStrip(ST141_CANONICAL_MENU);
 const game=seLevelStrip(ST_CANONICAL_PROJECT);
 game.project.sheepTagLevel='game';
 seLevels.root='sheep-tag-meadow';
 seLevels.records=new Map([
  ['menu',seLevelRecord('menu','Main Menu',menu,'menu','game')],
  ['game',seLevelRecord('game','Gameplay',game,'game','')]
 ]);
 seLevels.active='menu';seLevels.ordinal=2;seLevels.loading=true;
 try{seLevelRawLoadProject(structuredClone(menu),{workspaceLocal:true});}
 finally{seLevels.loading=false;}
 seLevelsMenuEditorCamera();initializeHistory('Opened editable Sheep Tag Main Menu');
 seLevelsEnsureUI();seLevelsRefresh();toast('Sheep Tag · edit Main Menu or Gameplay');
};
const seLevelNativeBeginPlay=beginPlay;
beginPlay=function(...args){
 if(seLevelsOwns()&&seLevelsCurrent()?.role==='menu')return seLevelsPlayMenu();
 return seLevelNativeBeginPlay(...args);
};
const seLevelNativeBeginSimulate=beginSimulate;
beginSimulate=function(...args){
 if(seLevelsOwns()&&seLevelsCurrent()?.role==='menu')return seLevelsPlayMenu();
 return seLevelNativeBeginSimulate(...args);
};
const seLevelNativeStop=stopSession;
stopSession=function(...args){
 if(seLevels.playingMenu)return seLevelsStopMenu();
 return seLevelNativeStop(...args);
};
// Retire all editor-time v11.140 cinematic objects and redirect its frame
// tick to authored menu actors in Play only. No second frame loop.
st140MenuOpen=function(){return false;};
st140MenuTick=function(dt){seLevelsMenuTick(dt);};
window.SWYRL_ENGINE_LEVELS={
 list:()=>[...seLevels.records.values()].map(x=>({id:x.id,name:x.name,role:x.role,next:x.next})),
 current:()=>seLevels.active,
 create:name=>seLevelsCreate(name),
 open:id=>seLevelsSwitch(id),
 link:(from,to)=>seLevelsLink(from,to),
 rename:(id,name)=>seLevelsRename(id,name),
 transition:to=>seLevelsTransition(to,true),
 exportCurrent:()=>seLevelsExportLevel(),
 status:()=>({active:seLevels.active,root:seLevels.root,menuPlaying:seLevels.playingMenu,
  levels:seLevels.records.size,menuStarts:seLevels.playCount,menuStops:seLevels.stopCount})
};
