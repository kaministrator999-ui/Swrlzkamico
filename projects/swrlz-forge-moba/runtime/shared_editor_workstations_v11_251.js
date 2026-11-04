// §E v11.251 · shared layout conventions for Game, Model and Materials.
// Reuses native editor state and controls; no cloned renderer or scene mutation.
(function(){
'use strict';
const q=s=>document.querySelector(s);
const state={mode:'auto',model:{left:205,right:305,collapsed:false},
 materials:{left:205,right:335,collapsed:false},installed:false};
const key='se251-studio-docks';
function save(){try{localStorage.setItem(key,JSON.stringify(state))}catch(e){}}
function restore(){try{
 const v=JSON.parse(localStorage.getItem(key)||'{}');
 if(['auto','desktop','compact'].includes(v.mode))state.mode=v.mode;
 for(const k of ['model','materials']){
  const r=v[k]||{};
  for(const side of ['left','right'])if(Number.isFinite(r[side]))
   state[k][side]=Math.max(140,Math.min(480,r[side]));
  state[k].collapsed=r.collapsed===true;
  state[k].rightCollapsed=r.rightCollapsed===true;
 }
}catch(e){}}
function layout(){return state.mode==='auto'?(innerWidth<700?'compact':'desktop'):state.mode}
function sync(){
 const mode=layout();
 document.documentElement.dataset.se251UnifiedLayout=mode;
 for(const key of ['model','materials']){
  const root=key==='model'?q('#modelAtelierPanel'):q('#se225Shell');
  if(!root)continue;
  root.style.setProperty('--se251-left',Math.round(state[key].left)+'px');
  root.style.setProperty('--se251-right',Math.round(state[key].right)+'px');
  root.dataset.se251Layout=mode;
  root.dataset.se251Collapsed=String(state[key].collapsed);
  root.dataset.se251RightCollapsed=String(!!state[key].rightCollapsed);
 }
 syncLayoutInputs();
 q('#se251UnifiedMode')?.setAttribute('data-mode',state.mode);
 const names=q('#se251UnifiedMode');
 if(names&&names.value!==state.mode)names.value=state.mode;
}
function mode(v){
 if(!['auto','desktop','compact'].includes(v))return;
 state.mode=v;
 // Sync Particle Studio mode with the shared editor choice, but leave its
 // current owner overrides intact if its controls are not installed.
 window.SWYRL_ENGINE_PARTICLE_DOCKS_250?.layout?.(v);
 sync();save();
}
function dragResize(node,what,side,dir){
 if(!node||node.dataset.se251Splitter==='1')return;
 node.dataset.se251Splitter='1';
 node.className+=' se251-resize-grip';
 node.tabIndex=0;
 node.setAttribute('role','separator');
 node.setAttribute('aria-label','Resize '+what+' '+side+' dock');
 node.setAttribute('aria-orientation','vertical');
 let start=null;
 node.addEventListener('pointerdown',e=>{
  if(e.button!==0||layout()!=='desktop')return;
  start={pointer:e.pointerId,x:e.clientX,width:state[what][side]};
  node.setPointerCapture?.(e.pointerId);e.preventDefault();
 });
 node.addEventListener('pointermove',e=>{
  if(!start||e.pointerId!==start.pointer)return;
  const w=state[what][side];
  const next=start.width+(e.clientX-start.x)*dir;
  const bound=Math.max(180,innerWidth-430);
  state[what][side]=Math.min(bound,Math.max(145,Math.round(next)));
  if(w!==state[what][side]){sync();window.dispatchEvent(new Event('resize'))}
 });
 const end=()=>{if(start){start=null;save();window.dispatchEvent(new Event('resize'))}};
 node.addEventListener('pointerup',end);node.addEventListener('pointercancel',end);
 node.addEventListener('keydown',e=>{
  const dirKey=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;
  if(!dirKey)return;e.preventDefault();
  state[what][side]=Math.max(145,Math.min(475,state[what][side]+dirKey*10*dir));sync();save();
  window.dispatchEvent(new Event('resize'));
 });
}
function addSeparator(parent,what,side,dir){
 const id='se251-split-'+what+'-'+side;
 if(q('#'+id))return;
 const divider=document.createElement('div');divider.id=id;
 dragResize(divider,what,side,dir);
 parent.append(divider);
}
function smallButton(label,title,fn){
 const b=document.createElement('button');b.type='button';b.textContent=label;
 b.title=title;b.setAttribute('aria-label',title);b.addEventListener('click',fn);return b;
}
function modelHierarchy(){
 const panel=q('#modelAtelierPanel'),body=panel?.querySelector('.atelier-body');
 const native=panel?.querySelector('#modelAtelierParts');
 if(!body||!native)return false;
 if(q('#se251ModelLibrary'))return true;
 const aside=document.createElement('aside');aside.id='se251ModelLibrary';aside.className='se251-side-library';
 const heading=document.createElement('div');heading.className='se251-side-title';heading.textContent='Project · Meshes';
 const scroll=document.createElement('div');scroll.className='se251-model-scroll';scroll.id='se251ModelTree';
 const search=document.createElement('input');search.type='search';search.placeholder='Find model part…';
 search.setAttribute('aria-label','Filter model hierarchy');
 search.addEventListener('input',renderModel);
 const bar=document.createElement('div');bar.className='se251-side-actions';
 bar.append(smallButton('Collapse','Collapse model tree',()=>{
  state.model.collapsed=!state.model.collapsed;sync();save();
 }));
 aside.append(heading,search,bar,scroll);body.prepend(aside);
 addSeparator(body,'model','left',1);
 addSeparator(body,'model','right',-1);
 const selected=()=>native.value;
 function renderModel(){
  const find=search.value.toLowerCase(),value=selected();scroll.replaceChildren();
  for(const item of [...native.options].filter(o=>o.textContent.toLowerCase().includes(find))){
   const row=smallButton('◇ '+item.textContent,'Select '+item.textContent,()=>{
    native.value=item.value;native.dispatchEvent(new Event('change',{bubbles:true}));
    renderModel();
   });
   row.className='se251-model-tree-item';row.setAttribute('aria-pressed',String(item.value===value));
   scroll.append(row);
  }
 }
 const observe=new MutationObserver(()=>renderModel());
 observe.observe(native,{childList:true,subtree:true,attributes:true,attributeFilter:['selected']});
 native.addEventListener('change',renderModel);
 renderModel();return true;
}
function materialHierarchy(){
 const root=q('#se225Shell'),panel=q('#se225MaterialsPanel');
 const native=panel?.querySelector('#se225MList');
 if(!root||!native)return false;
 if(q('#se251MaterialLibrary'))return true;
 const aside=document.createElement('aside');aside.id='se251MaterialLibrary';aside.className='se251-side-library';
 const heading=document.createElement('div');heading.className='se251-side-title';heading.textContent='Project · Materials';
 const scroll=document.createElement('div');scroll.id='se251MaterialsTree';scroll.className='se251-model-scroll';
 const search=document.createElement('input');search.type='search';search.placeholder='Find material…';
 search.setAttribute('aria-label','Filter material library');
 search.addEventListener('input',render);
 const add=smallButton('+ New material','Create an editable material',()=>q('#se225MCreate')?.click());
 const collapse=smallButton('Collapse','Collapse material library',()=>{
  state.materials.collapsed=!state.materials.collapsed;sync();save();
 });
 const actions=document.createElement('div');actions.className='se251-side-actions';actions.append(add,collapse);
 aside.append(heading,search,actions,scroll);root.append(aside);
 addSeparator(root,'materials','left',1);
 addSeparator(root,'materials','right',-1);
 function render(){
  const value=native.value,filter=search.value.toLowerCase();scroll.replaceChildren();
  for(const option of [...native.options].filter(o=>o.textContent.toLowerCase().includes(filter))){
   const item=smallButton('▣ '+option.textContent,'Edit '+option.textContent,()=>{
    native.value=option.value;native.dispatchEvent(new Event('change',{bubbles:true}));render();
   });
   item.className='se251-model-tree-item';item.setAttribute('aria-pressed',String(option.value===value));
   scroll.append(item);
  }
 }
 const mo=new MutationObserver(render);mo.observe(native,{childList:true,subtree:true});
 native.addEventListener('change',render);render();return true;
}
function layoutControls(root,which){
 if(!root||root.querySelector('.se251-external-layout'))return;
 const host=which==='model'?root.querySelector('.atelier-head'):
  root.querySelector('#se225MaterialsPanel .se225-m-title');
 if(!host)return;
 const wrap=document.createElement('label');wrap.className='se251-external-layout';
 const title=document.createElement('span');title.textContent='Layout';
 const input=document.createElement('select');input.setAttribute('aria-label',which+' editor layout');
 for(const [k,name]of [['auto','Auto'],['desktop','Desktop / VR'],['compact','Compact']]){
  input.append(new Option(name,k));
 }
 input.value=state.mode;
 input.addEventListener('change',()=>{mode(input.value);syncLayoutInputs()});
 wrap.append(title,input);
 const collapse=smallButton('‹ Inspector','Collapse or restore the '+which+' modifier dock',()=>{
  state[which].rightCollapsed=!state[which].rightCollapsed;
  sync();save();
 });
 collapse.className='se251-external-collapse';
 host.append(wrap,collapse);
}
function syncLayoutInputs(){
 for(const el of document.querySelectorAll('.se251-external-layout select')){
  if(el.value!==state.mode)el.value=state.mode;
 }
}
function modes(){
 if(q('#se251UnifiedMode'))return;
 const header=q('#se249Root .se249-commandbar');
 if(!header)return;
 const group=document.createElement('label');group.className='se251-unified-mode';
 const label=document.createElement('span');label.textContent='All editors';
 const input=document.createElement('select');input.id='se251UnifiedMode';
 for(const [v,name]of [['auto','Auto'],['desktop','Desktop / VR'],['compact','Compact']]){
  const option=new Option(name,v);input.append(option);
 }
 input.value=state.mode;input.addEventListener('change',()=>mode(input.value));
 group.append(label,input);header.append(group);
}
function boot(){
 const changed=modelHierarchy()|materialHierarchy();
 layoutControls(q('#modelAtelierPanel'),'model');
 layoutControls(q('#se225Shell'),'materials');
 modes();sync();
 if(changed)state.installed=true;
}
restore();
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
const observer=new MutationObserver(()=>{
 if(!q('#se251ModelLibrary')||!q('#se251MaterialLibrary')||!q('#se251UnifiedMode'))boot();
});
observer.observe(document.body,{childList:true,subtree:true});
window.addEventListener('resize',sync,{passive:true});
window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251=Object.freeze({
 mode,setMode:mode,
 inspect:()=>({layout:layout(),modelHierarchy:!!q('#se251ModelLibrary'),
 materialsHierarchy:!!q('#se251MaterialLibrary')})
});
})();