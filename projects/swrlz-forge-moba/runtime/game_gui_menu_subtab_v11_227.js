// §E GUI/Menu subtab: a child of Game Engine, sharing the native viewport.
// This file is a release candidate until the governed builder seals its manifest.
(function seGuiMenuStudio(){
 const SCHEMA='swyrl-gui-studio-v1',CAP=24,MODES=['label','button','panel'],ACTIONS=['none','start','next','stop'];
 const state={tab:'scene',show:true,hidden:new Set(),selected:null,key:'',bar:null,panel:null,canvas:null};
 const clamp=(n,min,max)=>Math.max(min,Math.min(max,Number.isFinite(+n)?+n:min));
 const color=(v,fallback)=>/^#[0-9a-f]{6}$/i.test(v||'')?v:fallback;
 const editing=()=>!playing&&!simulating&&!stSession&&!seLevels.playingMenu;
 const game=()=>window.SWYRL_ENGINE_STUDIOS?.active?.()==='game' &&
  window.SWYRL_ENGINE_WORKSPACES?.active?.()!=='modeler';
 const projectKey=()=>String(currentProject?.canonicalId||currentProject?.name||'untitled')+':'+(seLevels.active||'');
 function cleanItem(v){
  if(!v||typeof v!=='object'||!MODES.includes(v.kind)||typeof v.id!=='string'||!v.id||v.id.length>100)throw Error('Invalid GUI item');
  return {id:v.id,kind:v.kind,name:String(v.name||v.kind).slice(0,60),
   text:String(v.text||'').slice(0,100),x:clamp(v.x,0,95),y:clamp(v.y,0,95),
   width:clamp(v.width,5,100),height:clamp(v.height,5,80),
   foreground:color(v.foreground,'#e8f7ff'),background:color(v.background,'#16354b'),
   action:ACTIONS.includes(v.action)?v.action:'none',inPlay:v.inPlay!==false};
 }
 function clean(data){
  if(!data)return {schema:SCHEMA,items:[]};
  if(data.schema!==SCHEMA||!Array.isArray(data.items)||data.items.length>CAP)throw Error('Invalid GUI library');
  const ids=new Set(),items=data.items.map(cleanItem);
  for(const item of items){if(ids.has(item.id))throw Error('Duplicate GUI item');ids.add(item.id);}
  return {schema:SCHEMA,items};
 }
 function library(){try{return clean(currentProject?.guiStudio);}catch{return {schema:SCHEMA,items:[]};}}
 function syncKey(){
  const key=projectKey();
  if(state.key!==key){state.key=key;state.hidden=new Set();state.selected=null;state.show=true;}
 }
 function mutate(label,fn){
  if(!currentProject||!editing())return false;
  try{
   const draft=library(),result=fn(draft);
   const validated=clean(draft);
   beginTransaction(label);currentProject.guiStudio=validated;commitTransaction(label);
   repaint();return result===undefined?true:result;
  }catch(error){if(typeof toast==='function')toast('GUI change rejected: '+String(error.message||error).slice(0,90));return false;}
 }
 function stamp(source){
  if(!currentProject)return;
  try{currentProject.guiStudio=clean(source);}catch{currentProject.guiStudio={schema:SCHEMA,items:[]};}
  syncKey();repaint();
 }
 const projectDataBase=projectData;
 projectData=function(...args){
  const data=projectDataBase(...args);
  if(data?.project&&currentProject)data.project.guiStudio=library();
  return data;
 };
 const loadProjectBase=loadProject;
 loadProject=function(data,...args){
  const result=loadProjectBase(data,...args);
  const level=data?.project?.levelPack?seLevelsCurrent()?.data?.project?.guiStudio:null;
  stamp(level||data?.project?.guiStudio);return result;
 };
 // seLevels v11.141 holds a reference to an older projectData function. Add
 // the GUI schema to that level's snapshot without modifying old level data.
 const captureBase=seLevelsCapture;
 seLevelsCapture=function(...args){
  const result=captureBase(...args),record=seLevelsCurrent();
  if(record?.data?.project&&seLevelsOwns()&&editing())
   record.data.project.guiStudio=library();
  return result;
 };
 const switchBase=seLevelsSwitch;
 seLevelsSwitch=function(id,...args){
  const result=switchBase(id,...args);
  if(result)stamp(seLevelsCurrent()?.data?.project?.guiStudio);
  return result;
 };
 const starterBase=stLoadStarter;
 stLoadStarter=function(...args){
  const result=starterBase(...args);stamp(seLevelsCurrent()?.data?.project?.guiStudio);return result;
 };
 function activate(tab){
  if(!['scene','gui'].includes(tab))return false;
  state.tab=tab;repaint();return true;
 }
 function visibleInEditor(id){return state.show&&!state.hidden.has(id);}
 function toggle(id){
  if(state.hidden.has(id))state.hidden.delete(id);else state.hidden.add(id);
  repaint();return !state.hidden.has(id);
 }
 function makeButton(label,onClick,title=''){
  const b=document.createElement('button');b.type='button';b.textContent=label;
  if(title)b.title=title;b.addEventListener('click',onClick);return b;
 }
 function renderPanel(){
  const panel=state.panel;if(!panel||state.tab!=='gui'||!editing()||!game())return;
  const keep=panel.scrollTop;panel.replaceChildren();
  const header=document.createElement('div');header.className='segui-head';
  header.innerHTML='<strong>GUI & Menu Setup</strong><small>Editor visibility is separate from Play visibility.</small>';
  panel.append(header);
  const top=document.createElement('div');top.className='segui-actions';
  top.append(makeButton('Show all',()=>{state.show=true;state.hidden.clear();repaint();}),
   makeButton('Hide all',()=>{state.show=false;repaint();}));
  panel.append(top);
  const native=seLevelsOwns()&&seLevelsCurrent()?.role==='menu';
  if(native){
   const row=document.createElement('div');row.className='segui-row';
   row.append(makeButton(visibleInEditor('native-menu')?'👁 Hide':'◌ Show',
    ()=>{state.show=true;toggle('native-menu');}),
    document.createTextNode('Sheep Tag · native main menu'));
   panel.append(row);
   const inspector=seLevels.inspector;
   if(inspector){
    inspector.classList.add('segui-native');
    if(inspector.parentElement!==panel)panel.append(inspector);
    if(inspector.hidden)seLevelsEditUI(); // Native labels, color and orbit handlers persist.
    inspector.hidden=false;
   }
  }else if(seLevels.inspector){seLevels.inspector.hidden=true;}
  const title=document.createElement('strong');title.textContent='Custom GUI layers';
  title.className='segui-section-title';panel.append(title);
  const add=document.createElement('div');add.className='segui-actions';
  for(const kind of MODES)add.append(makeButton('+ '+kind,()=>create(kind)));
  panel.append(add);
  const items=library().items;
  const list=document.createElement('div');list.className='segui-list';
  if(!items.length){const empty=document.createElement('small');empty.textContent='Add a label, button or panel to this level or project.';list.append(empty);}
  for(const item of items){
   const row=document.createElement('div');row.className='segui-row';
   const select=makeButton(item.name,()=>{state.selected=item.id;repaint();});
   select.className=state.selected===item.id?'segui-picked':'';
   select.title='Edit '+item.name;
   row.append(select,makeButton(visibleInEditor(item.id)?'👁':'◌',()=>toggle(item.id),
    'Toggle only the editor preview'));
   const play=document.createElement('input');play.type='checkbox';play.checked=item.inPlay;
   play.setAttribute('aria-label','Show '+item.name+' in Play');
   play.addEventListener('change',()=>change(item.id,{inPlay:play.checked}));
   const caption=document.createElement('label');caption.className='segui-in-play';
   caption.append(play,document.createTextNode('Play'));row.append(caption);list.append(row);
  }
  panel.append(list);
  const chosen=items.find(item=>item.id===state.selected);
  if(chosen){
   const form=document.createElement('div');form.className='segui-form';
   const heading=document.createElement('strong');heading.textContent='Edit '+chosen.kind;form.append(heading);
   const fields=[['name','Layer name','text'],['text','Displayed text','text'],
    ['x','Left %','number'],['y','Top %','number'],
    ['width','Width %','number'],['height','Height %','number'],
    ['foreground','Text color','color'],['background','Background','color']];
   for(const [key,label,type] of fields){
    if(chosen.kind==='panel'&&key==='text')continue;
    const row=document.createElement('label');row.textContent=label;
    const input=document.createElement('input');input.type=type;
    input.value=String(chosen[key]);input.setAttribute('aria-label',label);
    if(type==='number'){input.min='0';input.max='100';input.step='1';input.inputMode='numeric';}
    input.addEventListener('change',()=>change(chosen.id,{[key]:type==='number'?Number(input.value):input.value}));
    row.append(input);form.append(row);
   }
   if(chosen.kind==='button'){
    const row=document.createElement('label');row.textContent='Play action';
    const select=document.createElement('select');
    for(const [id,label] of [['none','Display only'],['start','Start game'],['next','Next level'],['stop','Stop game']]){
     const option=document.createElement('option');option.value=id;option.textContent=label;select.append(option);
    }
    select.value=chosen.action;select.addEventListener('change',()=>change(chosen.id,{action:select.value}));
    row.append(select);form.append(row);
   }
   form.append(makeButton('Delete layer',()=>remove(chosen.id)));
   panel.append(form);
  }
  const hint=document.createElement('small');hint.textContent='Position and size use viewport percentages. Save Project to keep GUI layers with the current scene and level.';panel.append(hint);
  panel.scrollTop=Math.min(keep,panel.scrollHeight);
 }
 function create(kind){
  if(!MODES.includes(kind))return false;
  const entry={id:'gui-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*9999).toString(36),
   kind,name:kind[0].toUpperCase()+kind.slice(1),text:kind==='button'?'Button':'New label',
   x:kind==='panel'?20:35,y:kind==='panel'?20:30,width:kind==='panel'?60:30,
   height:kind==='panel'?35:12,foreground:'#e8f7ff',background:'#16354b',
   action:'none',inPlay:true};
  const result=mutate('Add GUI '+kind,draft=>{
   if(draft.items.length>=CAP)throw Error('Maximum 24 GUI layers');draft.items.push(entry);
  });
  if(result){state.selected=entry.id;state.show=true;state.hidden.delete(entry.id);repaint();}
  return result;
 }
 function change(id,fields){return mutate('Edit GUI layer',draft=>{
  const idx=draft.items.findIndex(x=>x.id===id);if(idx<0)throw Error('Layer not found');
  draft.items[idx]=cleanItem({...draft.items[idx],...fields,id});
 });}
 function remove(id){
  const result=mutate('Delete GUI layer',draft=>{
   const idx=draft.items.findIndex(x=>x.id===id);if(idx<0)throw Error('Layer not found');
   draft.items.splice(idx,1);
  });
  if(result){state.selected=null;state.hidden.delete(id);repaint();}return result;
 }
 function onAction(action){
  if(action==='start'){
   if(seLevels.playingMenu)seLevelsTransition('',true);
   else if(!playing&&!simulating&&!stSession)beginPlay();
  }else if(action==='next')seLevelsTransition('',true);
  else if(action==='stop')stopSession();
 }
 function drawOverlay(){
  const root=state.canvas,host=se143ViewportHost(),canvas=document.getElementById('viewport');
  if(!root||!host||!canvas)return;
  const active=game(),runtime=!editing();
  root.hidden=!active||(!runtime&&!state.show);
  root.replaceChildren();
  if(root.hidden)return;
  const cr=canvas.getBoundingClientRect(),hr=host.getBoundingClientRect();
  Object.assign(root.style,{left:cr.left-hr.left+'px',top:cr.top-hr.top+'px',
   width:cr.width+'px',height:cr.height+'px'});
  for(const item of library().items){
   if(runtime?!item.inPlay:!visibleInEditor(item.id))continue;
   const node=document.createElement(item.kind==='button'?'button':'div');
   node.className='segui-item segui-'+item.kind;
   node.textContent=item.kind==='panel'?'':item.text;
   node.style.left=item.x+'%';node.style.top=item.y+'%';
   node.style.width=Math.min(item.width,100-item.x)+'%';
   node.style.height=Math.min(item.height,100-item.y)+'%';
   node.style.color=item.foreground;node.style.backgroundColor=item.background;
   if(item.kind==='button'){
    node.type='button';node.disabled=!runtime||item.action==='none';
    if(runtime&&item.action!=='none'){
     node.addEventListener('click',event=>{event.stopPropagation();onAction(item.action);});
     for(const type of ['pointerdown','pointerup'])node.addEventListener(type,event=>event.stopPropagation());
    }
   }
   if(!runtime)node.setAttribute('aria-hidden','true');
   root.append(node);
  }
 }
 function repaint(){
  syncKey();install();
  if(!state.bar)return;
  const canEdit=editing()&&game();
  state.bar.hidden=!canEdit;
  state.panel.hidden=!canEdit||state.tab!=='gui';
  state.bar.querySelector('[data-segui-tab=scene]').classList.toggle('active',state.tab==='scene');
  state.bar.querySelector('[data-segui-tab=gui]').classList.toggle('active',state.tab==='gui');
  state.bar.querySelector('[data-segui-toggle]').textContent=state.show?'👁 Show UI':'◌ Hidden UI';
  const native=seLevels.preview;
  if(native)native.hidden=!(canEdit&&seLevelsOwns()&&seLevelsCurrent()?.role==='menu'&&visibleInEditor('native-menu'));
  if(state.panel.hidden&&seLevels.inspector)seLevels.inspector.hidden=true;
  if(!state.panel.hidden)renderPanel();
  drawOverlay();
 }
 function install(){
  const nav=document.querySelector('.app>.topbar>.se187-game-tabs');
  const host=se143ViewportHost();
  if(nav&&!state.bar){
   const bar=document.createElement('div');bar.className='segui-mini';bar.setAttribute('role','group');
   bar.setAttribute('aria-label','Game Engine sub-tabs');
   for(const [id,label] of [['scene','Scene'],['gui','GUI / Menus']]){
    const b=makeButton(label,()=>activate(id));b.dataset.seguiTab=id;bar.append(b);
   }
   const toggleBtn=makeButton('👁 Show UI',()=>{state.show=!state.show;repaint();},
    'Show or hide menus and GUI previews in the editor, without changing Play');
   toggleBtn.dataset.seguiToggle='';bar.append(toggleBtn);
   const insertBefore=nav.querySelector('.se187-draft-state');
   if(insertBefore)nav.insertBefore(bar,insertBefore);else nav.append(bar);
   state.bar=bar;
  }
  if(host&&!state.panel){
   const panel=document.createElement('section');panel.id='seguiPanel';
   panel.className='segui-panel';panel.setAttribute('aria-label','GUI and menu setup');panel.hidden=true;
   host.append(panel);state.panel=panel;
   const overlay=document.createElement('div');overlay.id='seguiPreview';
   overlay.className='segui-preview';overlay.hidden=true;
   overlay.setAttribute('aria-label','Project GUI preview');host.append(overlay);state.canvas=overlay;
  }
  if(seLevels.bar){
   const edit=seLevels.bar.querySelector('#st141Customize');
   if(edit&&!edit.dataset.seguiLinked){
    edit.dataset.seguiLinked='1';edit.onclick=()=>activate('gui');
    edit.textContent='GUI / Menus';
   }
  }
 }
 const levelsRefreshBase=seLevelsRefresh;
 seLevelsRefresh=function(...args){const result=levelsRefreshBase(...args);repaint();return result;};
 const levelsEnsureBase=seLevelsEnsureUI;
 seLevelsEnsureUI=function(...args){const result=levelsEnsureBase(...args);install();return result;};
 for(const key of ['beginPlay','beginSimulate','stopSession']){
  // Existing gameplay functions are not changed; visibility is refreshed after
  // their native state transitions and the Sheep Tag menu lifecycle.
  if(key==='beginPlay'){const previous=beginPlay;beginPlay=function(...a){const r=previous(...a);repaint();return r;};}
  if(key==='beginSimulate'){const previous=beginSimulate;beginSimulate=function(...a){const r=previous(...a);repaint();return r;};}
  if(key==='stopSession'){const previous=stopSession;stopSession=function(...a){const r=previous(...a);repaint();return r;};}
 }
 const menuStart=seLevelsPlayMenu,menuStop=seLevelsStopMenu;
 seLevelsPlayMenu=function(...args){const r=menuStart(...args);repaint();return r;};
 seLevelsStopMenu=function(...args){const r=menuStop(...args);repaint();return r;};
 window.addEventListener('resize',()=>{if(state.canvas&&!state.canvas.hidden)drawOverlay();},{passive:true});
 window.addEventListener('popstate',()=>setTimeout(repaint,0));
 window.SWYRL_ENGINE_GUI_STUDIO=Object.freeze({
  open:()=>activate('gui'),scene:()=>activate('scene'),showAll:()=>{state.show=true;state.hidden.clear();repaint();},
  hideAll:()=>{state.show=false;repaint();},toggleEditor:toggle,
  create,edit:change,remove,
  inspect:()=>({mode:state.tab,editorPreview:state.show,hidden:[...state.hidden],
   count:library().items.length,active:game(),play:!editing(),project:state.key})
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(repaint,0),{once:true});
 else setTimeout(repaint,0);
})();
