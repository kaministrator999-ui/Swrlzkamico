// §E v11.249 · actual workstation for the ONE native Particle Studio renderer.
// Existing emitters, transactions, touch input, project files and stage remain authoritative.
(function(){
'use strict';
const vq=s=>document.querySelector(s);
const vn=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!=null)el.textContent=text;return el};
const isVortex=k=>/^vortex(?:Cyan|Core|Spark)?$/.test(k||'');
const state={installed:false,left:'project',right:'properties',bottom:'timeline',tool:'orbit',
 view:'perspective',mobile:'timeline',paused:false,clock:0,lastDraw:0,selected:null,
 messages:[],grid:true};
const getPanel=()=>document.getElementById('se223Panel');
const current=()=>se223Get(se223State.selected)||se223Data()?.emitters?.[0]||null;
function report(s){state.messages.unshift(new Date().toLocaleTimeString()+' · '+s);state.messages.length=25;
 const o=vq('#se249Output');if(o)o.textContent=state.messages.join('\n');}
function action(id){const b=getPanel()?.querySelector('#'+id);if(b&&!b.disabled){b.click();return true}return false}
function nativeButton(label){
 const match=[...document.querySelectorAll('.app>.topbar button')].find(b=>b.textContent.trim().toLowerCase()===label.toLowerCase());
 if(match&&!match.disabled){match.click();return true}return false;
}
function perform(name){
 const cfg=current(),stage=window.SWYRL_ENGINE_PARTICLE_STAGE_240;
 switch(name){
 case 'new':action('se223Create');report('New emitter created');break;
 case 'project':document.getElementById('projectHub')?.classList.add('show');break;
 case 'load':window.SWYRL_ENGINE_VORTEX_248?.load?.();break;
 case 'import':action('se223Import');break;
 case 'export':action('se223Export');break;
 case 'save':if(!nativeButton('Save')&&!nativeButton('Save Project'))report('Use Projects > Save to save this project');break;
 case 'undo':if(typeof undo==='function')undo();else if(!nativeButton('Undo'))report('Undo unavailable here');break;
 case 'redo':if(typeof redo==='function')redo();else if(!nativeButton('Redo'))report('Redo unavailable here');break;
 case 'duplicate':if(cfg){se223Duplicate(cfg.id);report('Duplicated '+cfg.name);}break;
 case 'delete':if(cfg&&confirm('Delete particle emitter "'+cfg.name+'"?')){se223Remove(cfg.id);report('Deleted '+cfg.name);}break;
 case 'preview':action('se223Preview');break;
 case 'pause':state.paused=!state.paused;se223State.preview=!state.paused;
    if(!state.paused)se223State.playingLast=false;report(state.paused?'Preview paused':'Preview resumed');break;
 case 'stop':se223State.preview=false;se223State.playingLast=false;se223Reset();report('Preview stopped');break;
 case 'restart':se223Reset();se223State.preview=true;state.paused=false;state.clock=0;report('Preview restarted');break;
 case 'burst':if(cfg)se223Trigger(cfg.id);report('Triggered burst');break;
 case 'focus':stage?.adjust?.('reset');break;
 case 'zoomin':stage?.adjust?.('zoom',-.9);break;
 case 'zoomout':stage?.adjust?.('zoom',1.1);break;
 case 'grid':state.grid=!state.grid;const g=scene?.getObjectByName?.('VFX grid');if(g)g.visible=state.grid;
    vq('#se249Grid')?.setAttribute('aria-pressed',String(state.grid));break;
 case 'left':toggleMobile('left');break;
 case 'right':toggleMobile('right');break;
 case 'bottom':toggleMobile('timeline');break;
 case 'resetlayout':document.body.dataset.se249Mobile='timeline';state.mobile='timeline';
    vq('#se249Root')?.classList.remove('se249-hide-left','se249-hide-right','se249-hide-bottom');break;
 default:break;
 }
 sync();
}
function menu(title,actions){
 const d=vn('details','se249-menu');const s=vn('summary','',title);d.append(s);
 const body=vn('div','se249-menu-pop');
 for(const [name,act] of actions){const b=vn('button','',name);b.type='button';b.onclick=()=>{
   d.open=false;if(act.startsWith('view:'))selectView(act.slice(5));else perform(act);
 };body.append(b)}
 d.append(body);return d;
}
function button(label,actionName,cls=''){
 const b=vn('button',cls,label);b.type='button';b.dataset.se249Action=actionName;
 b.onclick=()=>perform(actionName);return b;
}
function tabs(holder,items,type,selected,fn){
 const h=vn('div','se249-tabbar');h.setAttribute('role','tablist');
 h.setAttribute('aria-label',type+' tabs');
 for(const [key,name] of items){const b=vn('button','',name);b.type='button';b.dataset.se249Tab=key;
 b.setAttribute('role','tab');b.setAttribute('aria-selected',String(key===selected));
 b.tabIndex=key===selected?0:-1;b.onclick=()=>fn(key);
 b.onkeydown=e=>{if(!['ArrowRight','ArrowLeft'].includes(e.key))return;
   e.preventDefault();const i=items.findIndex(x=>x[0]===key),next=items[(i+(e.key==='ArrowRight'?1:-1)+items.length)%items.length][0];
   fn(next);h.querySelector('[data-se249-tab="'+next+'"]')?.focus();
 };h.append(b)}
 holder.append(h);return h;
}
function setTab(kind,value){
 state[kind]=value;const root=vq('#se249Root');if(!root)return;
 const bar=root.querySelector('[data-se249-tabs="'+kind+'"]');
 for(const b of bar?.querySelectorAll('[role=tab]')||[]){
  const on=b.dataset.se249Tab===value;b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;
 }
 if(kind==='left'){
  for(const p of root.querySelectorAll('[data-se249-left]'))p.hidden=p.dataset.se249Left!==value;
 } else if(kind==='bottom'){
  for(const p of root.querySelectorAll('[data-se249-bottom]'))p.hidden=p.dataset.se249Bottom!==value;
 } else if(kind==='right'){
  for(const section of getPanel()?.querySelectorAll('[data-se249-category]')||[]){
   section.hidden=section.dataset.se249Category!==value;
  }
 }sync();
}
function toggleMobile(which){
 const next=state.mobile===which&&which!=='timeline'?'timeline':which;
 state.mobile=next;document.body.dataset.se249Mobile=next;
 const pane=vq('#se249Root');for(const b of pane?.querySelectorAll('[data-se249-mobile]')||[]){
  const active=b.dataset.se249Mobile===next;b.setAttribute('aria-pressed',String(active));
 }sync();
}
function selectView(which){
 state.view=which;
 const stage=window.SWYRL_ENGINE_PARTICLE_STAGE_240;
 stage?.adjust?.('view',which);
 const v=vq('#se249CameraSelect');if(v)v.value=which;
 report('Camera: '+which);
}
function chooseTool(which){
 state.tool=which;
 for(const b of vq('#se249VerticalTools')?.querySelectorAll('[data-se249-tool]')||[]){
  const active=b.dataset.se249Tool===which;b.setAttribute('aria-pressed',String(active));
 }
 const shield=vq('#se240ParticleStageOrbit');
 if(shield)shield.style.cursor=which==='pan'?'move':which==='orbit'?'grab':'crosshair';
}
function makeTool(icon,label,mode){
 const b=vn('button','',icon);b.type='button';b.dataset.se249Tool=mode;
 b.title=label;b.setAttribute('aria-label',label);b.setAttribute('aria-pressed',String(mode==='orbit'));
 b.onclick=()=>chooseTool(mode);return b;
}
function findField(input){return input.closest('.se223-range-row,.se223-field,.se223-vector')||input.parentElement;}
function restructure(){
 const editor=getPanel()?.querySelector('#se223Editor');if(!editor||editor.dataset.se249Organized)return;
 const sections=[
 ['properties','Emitter', ['name','enabled']],
 ['emission','Emission & spawn',['mode','rate','burst']],
 ['emission','Shape',['shape','radius']],
 ['forces','Motion',['speed','spread','direction']],
 ['forces','Forces',['gravity','drag']],
 ['properties','Lifetime',['life']],
 ['material','Appearance',['size','startColor','endColor','blend']],
 ['properties','Placement & attachment',['position']]
 ];
 const sources=new Map();
 for(const item of editor.querySelectorAll('[data-se223-field]')){
  if(sources.has(item.dataset.se223Field))continue;
  sources.set(item.dataset.se223Field,findField(item));
 }
 const fragments=document.createDocumentFragment();
 for(const [category,title,fields] of sections){
  const group=document.createElement('details');group.open=true;group.className='se249-modifier';
  group.dataset.se249Category=category;
  const head=document.createElement('summary');head.textContent=title;group.append(head);
  for(const field of fields){const row=sources.get(field);if(row){group.append(row);sources.delete(field)}}
  if(title==='Placement & attachment'){
   const existing=editor.querySelector('#se223Attach');
   if(existing){const row=existing.closest('.se223-actions');if(row)group.append(row);}
   const label=editor.querySelector('#se223AttachInfo');if(label)group.append(label);
  }
  if(title==='Forces'){
   const vortex=vn('div','se249-vortex-settings');vortex.id='se249VortexSettings';
   for(const [key,label,min,max,step] of [
    ['vortexSpin','Vortex rotation',.1,5,.1],
    ['vortexPull','Radial pull',.1,2.5,.1],
    ['vortexGlow','Ribbon intensity',.05,2,.05],
    ['vortexTilt','Spiral tilt',0,1.8,.1]]){
    const wrap=vn('label','se249-vortex-field'),desc=vn('span','',label),num=document.createElement('input');
    num.type='number';num.min=String(min);num.max=String(max);num.step=String(step);
    num.dataset.se249Param=key;num.setAttribute('aria-label',label);
    const slider=document.createElement('input');slider.type='range';
    slider.min=num.min;slider.max=num.max;slider.step=num.step;slider.dataset.se249Param=key+'-slider';
    num.onchange=()=>setVortex(key,Number(num.value));
    slider.onchange=()=>{num.value=slider.value;setVortex(key,Number(slider.value))};
    wrap.append(desc,num,slider);vortex.append(wrap);
   }group.append(vortex);
  }
  fragments.append(group);
 }
 editor.replaceChildren(fragments);editor.dataset.se249Organized='1';
}
function setVortex(key,value){
 const cfg=current();if(!cfg||!isVortex(cfg.preset))return;
 if(se223Update(cfg.id,{[key]:value})!==false)report('Updated '+key+' to '+value);
 sync();
}
function selectEmitter(id){
 if(!se223Get(id))return;
 se223State.selected=id;se223UIRefresh();report('Selected '+se223Get(id).name);
 setTab('left','project');
}
function renderTree(){
 const tree=vq('#se249EmitterTree'),assets=vq('#se249Assets'),preview=vq('#se249PreviewTitle');
 if(!tree)return;const data=se223Data();const emitters=data?.emitters||[];
 const search=vq('#se249Search')?.value.toLowerCase()||'';
 const frag=document.createDocumentFragment();
 for(const item of emitters.filter(e=>e.name.toLowerCase().includes(search))){
  const row=vn('div','se249-tree-item'+(item.id===se223State.selected?' selected':''));
  const choose=vn('button','se249-tree-select',(item.enabled?'✧ ':'○ ')+item.name);
  choose.type='button';choose.onclick=()=>selectEmitter(item.id);
  const eye=vn('button','se249-tree-eye',item.enabled?'◉':'○');eye.type='button';
  eye.title=item.enabled?'Disable emitter':'Enable emitter';
  eye.onclick=()=>{se223Update(item.id,{enabled:!item.enabled});sync()};
  row.append(choose,eye);frag.append(row);
 }tree.replaceChildren(frag);
 const n=vq('#se249ProjectCount');if(n)n.textContent=emitters.length+' / 12';
 if(preview)preview.textContent=current()?.name||'Astral Vortex';
 if(assets&&assets.childNodes.length===0){
  const presets=document.createElement('details');presets.open=true;
  const title=document.createElement('summary');title.textContent='◈ Native particle presets';presets.append(title);
  for(const [key,def] of Object.entries(SE223_PRESETS)){
   const b=vn('button','se249-preset',def.label);b.type='button';
   b.onclick=()=>{se223Create(key);se223UIRefresh();report('Added '+def.label)};
   presets.append(b);
  }assets.append(presets);
 }
 const title=vq('#se249SelectedName');if(title)title.textContent=current()?.name||'No emitter selected';
}
function syncVortex(){
 const el=vq('#se249VortexSettings');if(!el)return;
 const cfg=current(),enabled=!!cfg&&isVortex(cfg.preset);el.hidden=!enabled;
 if(!enabled)return;
 for(const input of el.querySelectorAll('[data-se249-param]')){
  const key=input.dataset.se249Param.replace('-slider',''),v=cfg[key];
  if(v!=null&&document.activeElement!==input)input.value=String(v);
 }
}
function syncTimeline(){
 const cfg=current();const name=vq('#se249TimelineName');
 if(name)name.textContent=cfg?.name||'No emitter';
 for(const [id,value] of [['Rate',cfg?.rate],['Life',cfg?.life],['Size',cfg?.size],['Blend',cfg?.blend]]){
  const node=vq('#se249Stat'+id);if(node)node.textContent=value==null?'—':id==='Rate'?value+' /s':id==='Life'?value+' s':String(value);
 }
 const legend=vq('#se249LayerRows');if(legend){
  const rows=se223Data()?.emitters||[];const frag=document.createDocumentFragment();
  for(const [i,e] of rows.entries()){
   const row=vn('button','se249-layer-row'+(e.id===cfg?.id?' selected':''));row.type='button';
   row.innerHTML='<span class="se249-layer-eye">'+(e.enabled?'◉':'○')+'</span>'+
     '<span class="se249-layer-color"></span><span class="se249-layer-name"></span>'+
     '<span class="se249-layer-rate"></span><span class="se249-layer-track"></span>';
   row.querySelector('.se249-layer-color').style.background=e.startColor;
   row.querySelector('.se249-layer-name').textContent=e.name;
   row.querySelector('.se249-layer-rate').textContent=e.rate+'/s';
   row.querySelector('.se249-layer-track').style.background=
    'linear-gradient(90deg,'+e.startColor+'cc,'+e.endColor+'55)';
   row.onclick=()=>selectEmitter(e.id);frag.append(row);if(i>=11)break;
  }
  legend.replaceChildren(frag);
 }
 const curves=vq('#se249CurveSvg');
 if(curves&&cfg){
  const rate=Math.min(1,cfg.rate/80),life=Math.min(1,cfg.life/8);
  curves.innerHTML='<path d="M0 82 C70 '+(82-rate*64)+' 130 '+(82-rate*64)+' 220 82 S370 82 480 82" stroke="#b65cff" fill="none" stroke-width="3"/>'+
  '<path d="M0 102 Q170 '+(102-life*90)+' 300 '+(102-life*80)+' T480 102" stroke="#38c9fd" fill="none" stroke-width="3"/>'+
  '<path d="M0 126 C60 60 120 145 185 95 S300 150 370 96 S440 130 480 95" stroke="#80e3cd" fill="none" stroke-width="2"/>';
 }
}
function sync(){
 if(!state.installed)return;
 renderTree();syncVortex();syncTimeline();
 const p=current();const n=vq('#se249Status');if(n)n.textContent=p?'Selected · '+p.name:'Choose or create a particle emitter';
 const b=vq('#se249Play');if(b){b.textContent=se223State.preview?'■ Stop preview':'▶ Preview';b.setAttribute('aria-pressed',String(!!se223State.preview))}
 for(const x of vq('#se249Root')?.querySelectorAll('[data-se249-dependent]')||[]){
  x.disabled=!p;
 }
}
function build(){
 const shell=vq('#se225Shell'),panel=getPanel();if(!shell||!panel)return false;
 if(vq('#se249Root'))return true;
 const root=vn('div','se249-root');root.id='se249Root';
 const header=vn('header','se249-header');
 const menus=vn('div','se249-menubar');
 const mark=vn('div','se249-mark');mark.innerHTML='<span>§e</span><b>Particle Editor</b>';
 menus.append(mark);
 const space=vn('div','se249-workspaces');
 for(const [id,label] of [['game','Game Engine'],['modeler','Modeling'],['particles','Particle Studio'],['materials','Materials & Textures']]){
  const b=vn('button','',label);b.type='button';b.dataset.se249Workspace=id;
  b.setAttribute('aria-pressed',String(id==='particles'));
  b.onclick=()=>window.SWYRL_ENGINE_STUDIOS?.change?.(id);space.append(b);
 }
 menus.append(space);
 const dropdown=vn('div','se249-menus');
 for(const [title,actions] of [
  ['File',[['New emitter','new'],['Projects','project'],['Save project','save'],['Import VFX','import'],['Export VFX','export']]],
  ['Edit',[['Duplicate emitter','duplicate'],['Delete emitter','delete'],['Undo','undo'],['Redo','redo']]],
  ['View',[['Perspective','view:perspective'],['Top','view:top'],['Front','view:front'],['Reset camera','focus'],['Toggle grid','grid']]],
  ['Tools',[['Restart preview','restart'],['Burst selected','burst'],['Load Astral Vortex','load']]],
  ['Window',[['Project browser','left'],['Properties','right'],['Timeline','bottom'],['Reset layout','resetlayout']]],
  ['Help',[['Open project library','project']]]])dropdown.append(menu(title,actions));
 menus.append(dropdown);header.append(menus);
 const cmd=vn('div','se249-commandbar');
 for(const [label,op,cls] of [['▤ New','new',''],['▱ Projects','project',''],['▣ Save','save',''],['↶','undo','se249-square'],['↷','redo','se249-square'],['▶ Preview','preview','se249-primary'],['↺ Restart','restart',''],['■ Stop','stop',''],['✦ Burst','burst',''],['⇧ Export','export','se249-export']])cmd.append(button(label,op,cls));
 const projectLabel=vn('span','se249-current-project','PROJECT · VFX WORKSPACE');cmd.append(projectLabel);
 header.append(cmd);root.append(header);
 const left=vn('aside','se249-left');
 const ltab=tabs(left,[['project','Project'],['assets','Assets']],'Library',state.left,k=>setTab('left',k));ltab.dataset.se249Tabs='left';
 const lcontent=vn('div','se249-left-main');
 const project=vn('div','se249-left-pane');project.dataset.se249Left='project';
 const title=vn('div','se249-project-title','⌄  §E Project');
 project.append(title);
 const nested=vn('details','se249-folder');nested.open=true;nested.innerHTML='<summary>▾ Particles <span id="se249ProjectCount"></span></summary>';
 const find=document.createElement('input');find.id='se249Search';find.placeholder='Search emitters…';
 find.setAttribute('aria-label','Filter project emitters');find.oninput=renderTree;
 nested.append(find);const tree=vn('div','se249-emitter-tree');tree.id='se249EmitterTree';nested.append(tree);
 project.append(nested);lcontent.append(project);
 const assets=vn('div','se249-left-pane');assets.dataset.se249Left='assets';assets.id='se249Assets';assets.hidden=true;
 lcontent.append(assets);left.append(lcontent);
 const lpreview=vn('div','se249-left-preview');
 lpreview.innerHTML='<div class="se249-preview-heading">Preview</div>'+
  '<div class="se249-preview-graphic" role="img" aria-label="Purple and cyan vortex thumbnail">'+
  '<i class="se249-preview-orbit p"></i><i class="se249-preview-orbit c"></i><i class="se249-preview-core"></i></div>'+
  '<strong id="se249PreviewTitle">Astral Vortex</strong><small>Native VFX · Editable emitters</small>';
 const load=button('✦ Load Astral Vortex','load','se249-load');lpreview.append(load);left.append(lpreview);root.append(left);
 const stage=vn('main','se249-center');
 const top=vn('div','se249-stage-tabs');
 const stabs=tabs(top,[['viewport','Viewport'],['guide','Camera / Stage']],'Stage','viewport',k=>{
  const note=vq('#se249StageNote');if(note)note.hidden=k==='viewport';
  for(const b of top.querySelectorAll('[role=tab]'))b.setAttribute('aria-selected',String(b.dataset.se249Tab===k));
 });top.append(vn('div','se249-stage-label','3D Particle Chamber'));stage.append(top);
 const viewing=vn('div','se249-stage');
 const vtools=vn('div','se249-vertical-tools');vtools.id='se249VerticalTools';
 for(const [icon,label,mode] of [['⌖','Select emitter','select'],['✥','Pan camera','pan'],['↻','Orbit camera','orbit'],['⊕','Zoom preview','zoom']])
  vtools.append(makeTool(icon,label,mode));
 viewing.append(vtools);
 const htools=vn('div','se249-horizontal-tools');
 const cam=document.createElement('select');cam.id='se249CameraSelect';cam.setAttribute('aria-label','Particle stage camera');
 for(const key of ['perspective','top','front','side']){const o=new Option(key[0].toUpperCase()+key.slice(1),key);cam.append(o);}
 cam.onchange=()=>selectView(cam.value);htools.append(cam);
 for(const [label,op] of [['⛶','focus'],['+','zoomin'],['−','zoomout'],['⌗','grid']]){
  const b=button(label,op,'');if(op==='grid')b.id='se249Grid';
  b.title={focus:'Frame particle',zoomin:'Zoom in',zoomout:'Zoom out',grid:'Toggle stage grid'}[op];
  htools.append(b);
 }viewing.append(htools);
 const note=vn('div','se249-stage-note','Stage camera: drag to orbit, scroll to zoom. Project emitter positions stay unchanged.');
 note.id='se249StageNote';note.hidden=true;viewing.append(note);
 const status=vn('div','se249-stage-status','No emitter selected');status.id='se249Status';viewing.append(status);
 const badge=vn('div','se249-axis','<span class="se249-x">X</span> <span class="se249-y">Y</span> <span class="se249-z">Z</span>');
 badge.innerHTML='<span class="se249-x">X</span> <span class="se249-y">Y</span> <span class="se249-z">Z</span>';
 viewing.append(badge);stage.append(viewing);
 const bottom=vn('section','se249-bottom');
 const btab=tabs(bottom,[['timeline','Timeline'],['curves','Curves'],['output','Output']],'Bottom dock',state.bottom,k=>setTab('bottom',k));btab.dataset.se249Tabs='bottom';
 const timeline=vn('div','se249-bottom-view');timeline.dataset.se249Bottom='timeline';
 timeline.innerHTML='<div class="se249-timeline-tools"><span>✦ <b id="se249TimelineName">Emitter</b></span><span>0.0s</span><span>1.0s</span><span>2.0s</span><span>3.0s</span><span>4.0s</span><span>5.0s</span></div>'+
 '<div id="se249LayerRows" class="se249-layer-rows"></div><div class="se249-playhead" id="se249Playhead"></div>';
 bottom.append(timeline);
 const curves=vn('div','se249-bottom-view se249-curves');curves.dataset.se249Bottom='curves';curves.hidden=true;
 curves.innerHTML='<div>Native parameter preview curves · rate / lifetime / modulation</div><svg id="se249CurveSvg" viewBox="0 0 480 150" preserveAspectRatio="none" aria-label="Read-only derived particle curves"></svg>';
 bottom.append(curves);
 const output=vn('pre','se249-bottom-view se249-output');output.id='se249Output';output.dataset.se249Bottom='output';output.hidden=true;bottom.append(output);
 const stats=vn('div','se249-stats');stats.innerHTML='<span>Rate <b id="se249StatRate">—</b></span>'+
 '<span>Lifetime <b id="se249StatLife">—</b></span>'+
 '<span>Size <b id="se249StatSize">—</b></span>'+
 '<span>Blend <b id="se249StatBlend">—</b></span>';
 bottom.append(stats);stage.append(bottom);root.append(stage);
 const right=vn('aside','se249-right');
 const rtab=tabs(right,[['properties','Properties'],['emission','Emission'],['forces','Forces'],['material','Material']],'Inspector',state.right,k=>setTab('right',k));
 rtab.dataset.se249Tabs='right';
 const selected=vn('div','se249-selected');selected.innerHTML='<span>PARTICLE SYSTEM</span><strong id="se249SelectedName">No emitter selected</strong>';
 right.append(selected);
 const holder=vn('div','se249-native-holder');holder.id='se249NativeHolder';right.append(holder);
 root.append(right);
 const mobile=vn('nav','se249-mobile-dock');mobile.setAttribute('aria-label','Mobile editor docks');
 for(const [name,label] of [['left','▤ Project'],['timeline','▦ Timeline'],['right','☷ Modifiers']]){
  const b=vn('button','',label);b.type='button';b.dataset.se249Mobile=name;
  b.setAttribute('aria-pressed',String(name==='timeline'));b.onclick=()=>toggleMobile(name);
  mobile.append(b);
 }root.append(mobile);shell.append(root);
 holder.append(panel);restructure();
 panel.hidden=false;panel.classList.add('se225-docked');
 const legacy=panel.querySelector('.se223-scroll');
 if(legacy){legacy.querySelector('.se223-editor')?.removeAttribute('hidden');}
 state.installed=true;document.body.dataset.se249Mobile='timeline';
 setTab('left','project');setTab('right','properties');setTab('bottom','timeline');
 chooseTool('orbit');report('§E Particle Editor workstation initialized');
 return true;
}
const previousRefresh=se223UIRefresh;
se223UIRefresh=function(...args){const result=previousRefresh(...args);sync();return result;};
function frame(dt){
 if(!state.installed||document.body.dataset.se225Workspace!=='particles')return;
 if(se223State.preview&&!state.paused)state.clock+=Math.min(Math.max(dt||0,0),.05);
 const now=performance.now();if(now-state.lastDraw<70)return;state.lastDraw=now;
 const line=vq('#se249Playhead');if(line)line.style.left=(12+(state.clock%5)/5*87)+'%';
 const b=vq('#se249Play');if(b)b.textContent=se223State.preview?'■ Stop preview':'▶ Preview';
}
window.SWYRL_ENGINE_PARTICLE_UI_249=Object.freeze({inspect:()=>({
 installed:state.installed,left:state.left,right:state.right,bottom:state.bottom,mobile:state.mobile,
 emitterCount:se223List().length}),refresh:sync,frame});
function boot(){
 if(build())return;
 const observer=new MutationObserver(()=>{if(build())observer.disconnect()});
 observer.observe(document.body,{childList:true,subtree:true});
 window.addEventListener('pagehide',()=>observer.disconnect(),{once:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();