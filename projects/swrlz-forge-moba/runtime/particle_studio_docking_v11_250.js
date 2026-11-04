// §E v11.250 · explicit responsive mode and physically resizable workstation docks.
// Browser "Desktop site" and Quest browser may expose a 800–1000 CSS-px viewport;
// do NOT infer mobile UI from pointer:coarse or the old 1080px breakpoint.
(function(){
'use strict';
const q=s=>document.querySelector(s);
const state={mode:'auto',effective:'desktop',width:{left:270,right:350,bottom:225},
 collapsed:{left:false,right:false,bottom:false},dragging:null,changes:0};
const key='se250-particle-layout';
function readSaved(){
 try{
  const raw=JSON.parse(localStorage.getItem(key)||'{}');
  if(['auto','desktop','compact'].includes(raw.mode))state.mode=raw.mode;
  for(const k of ['left','right','bottom']){
   const n=Number(raw.width?.[k]);if(Number.isFinite(n)&&n>=34&&n<1000)state.width[k]=n;
   state.collapsed[k]=raw.collapsed?.[k]===true;
  }
 }catch(e){/* private browsing: continue without persistence */}
}
function save(){
 try{localStorage.setItem(key,JSON.stringify({mode:state.mode,width:state.width,collapsed:state.collapsed}))}
 catch(e){/* no storage: current session layout still works */}
}
function limit(v,a,b){return Math.max(a,Math.min(b,v))}
function effective(){return state.mode==='auto'?(innerWidth<700?'compact':'desktop'):state.mode}
function sizes(){
 const width=Math.max(innerWidth,320);
 const left=limit(state.width.left,175,Math.max(180,Math.min(480,width-490)));
 const right=limit(state.width.right,210,Math.max(220,Math.min(540,width-left-260)));
 const bottom=limit(state.width.bottom,135,Math.max(150,innerHeight-220));
 return {left,right,bottom};
}
function apply(){
 const root=q('#se249Root');if(!root)return;
 state.effective=effective();
 document.body.dataset.se250Layout=state.effective;
 document.body.dataset.se250Requested=state.mode;
 root.dataset.se250LeftCollapsed=String(state.collapsed.left);
 root.dataset.se250RightCollapsed=String(state.collapsed.right);
 root.dataset.se250BottomCollapsed=String(state.collapsed.bottom);
 const s=sizes();
 for(const k of ['left','right','bottom'])root.style.setProperty('--se250-'+k,s[k]+'px');
 const select=q('#se250LayoutMode');
 if(select&&select.value!==state.mode)select.value=state.mode;
 for(const k of ['left','right','bottom']){
  const b=q('#se250Collapse-'+k);
  if(b){b.textContent=state.collapsed[k]?(k==='left'?'›':k==='right'?'‹':'⌃'):(k==='left'?'‹':k==='right'?'›':'⌄');
   b.setAttribute('aria-expanded',String(!state.collapsed[k]));
   b.title=state.collapsed[k]?'Expand '+k+' dock':'Collapse '+k+' dock';}
  const h=q('#se250Handle-'+k);
  if(h)h.setAttribute('aria-valuenow',String(Math.round(s[k])));
 }
 const t=q('#se250ModeHint');if(t)t.textContent=state.effective==='desktop'?'Side docks':'Compact docks';
}
function modeTo(v){
 if(!['auto','desktop','compact'].includes(v))return;
 state.mode=v;apply();save();
}
function collapse(which,desired){
 if(!Object.hasOwn(state.collapsed,which))return;
 state.collapsed[which]=desired==null?!state.collapsed[which]:!!desired;
 // For mobile, leave the old bottom navigation in charge of which drawer opens.
 if(state.effective==='compact'&&which!=='bottom'){
  const open=which==='left'?'left':'right';
  const target=state.collapsed[which]?'timeline':open;
  document.body.dataset.se249Mobile=target;
  for(const b of q('#se249Root')?.querySelectorAll('[data-se249-mobile]')||[])
   b.setAttribute('aria-pressed',String(b.dataset.se249Mobile===target));
 }
 apply();save();
}
function addButton(target,which){
 if(!target||q('#se250Collapse-'+which))return;
 const b=document.createElement('button');b.type='button';
 b.className='se250-collapse';b.id='se250Collapse-'+which;
 b.setAttribute('aria-label','Collapse or expand '+which+' dock');
 b.onclick=()=>collapse(which);
 target.append(b);
}
function addHandle(root,which){
 const h=document.createElement('div');h.id='se250Handle-'+which;
 h.className='se250-splitter se250-'+which+'-splitter';
 h.tabIndex=0;h.setAttribute('role','separator');
 h.setAttribute('aria-label','Resize '+which+' dock');
 h.setAttribute('aria-orientation',which==='bottom'?'horizontal':'vertical');
 h.setAttribute('aria-valuemin',String(which==='bottom'?135:which==='left'?175:210));
 h.setAttribute('aria-valuemax',String(which==='bottom'?600:600));
 const grip=document.createElement('span');grip.textContent=which==='bottom'?'⋯':'⋮';h.append(grip);
 h.addEventListener('pointerdown',e=>{
  if(e.button!==0||state.effective!=='desktop'||state.collapsed[which])return;
  state.dragging={which,id:e.pointerId,x:e.clientX,y:e.clientY,start:state.width[which]};
  h.setPointerCapture?.(e.pointerId);h.classList.add('is-dragging');
  e.preventDefault();e.stopPropagation();
 });
 h.addEventListener('pointermove',e=>{
  const d=state.dragging;if(!d||d.which!==which||d.id!==e.pointerId)return;
  const delta=which==='left'?e.clientX-d.x:which==='right'?d.x-e.clientX:d.y-e.clientY;
  state.width[which]=Math.round(d.start+delta);
  // Splitters can resize only their own axis. Clamp against remaining scene.
  const limited=sizes();state.width[which]=limited[which];
  apply();e.preventDefault();e.stopPropagation();
 });
 const stop=e=>{
  const d=state.dragging;if(d?.which!==which)return;
  state.dragging=null;h.classList.remove('is-dragging');save();e.stopPropagation();
 };
 h.addEventListener('pointerup',stop);
 h.addEventListener('pointercancel',stop);
 h.addEventListener('keydown',e=>{
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(e.key))return;
  e.preventDefault();
  if(e.key==='Home'){state.width[which]={left:270,right:350,bottom:225}[which];}
  else{
   const offset=which==='bottom'?(e.key==='ArrowUp'?12:e.key==='ArrowDown'?-12:0):
    which==='left'?(e.key==='ArrowRight'?12:e.key==='ArrowLeft'?-12:0):
    (e.key==='ArrowLeft'?12:e.key==='ArrowRight'?-12:0);
   state.width[which]=sizes()[which]+offset;
  }
  apply();save();
 });
 root.append(h);
}
function commandBar(){
 const bar=q('#se249Root .se249-commandbar');
 if(!bar||q('#se250LayoutMode'))return;
 const group=document.createElement('label');group.className='se250-mode-selector';
 const label=document.createElement('span');label.textContent='Layout';
 const select=document.createElement('select');select.id='se250LayoutMode';
 select.setAttribute('aria-label','Particle Studio layout: automatic, desktop or compact');
 for(const [id,name]of [['auto','Auto'],['desktop','Desktop / VR'],['compact','Compact']]){
  const opt=document.createElement('option');opt.value=id;opt.textContent=name;select.append(opt);
 }
 select.onchange=()=>modeTo(select.value);group.append(label,select);
 bar.append(group);
 const hint=document.createElement('span');hint.id='se250ModeHint';hint.className='se250-mode-hint';bar.append(hint);
}
function detailsGroup(){
 // Both the left project tree and right modifier groups already use native
 // <details>. Keep these individually collapsible and add real bulk controls.
 const inspector=q('#se249Root .se249-selected');if(inspector&&!q('#se250RightControls')){
  const group=document.createElement('div');group.id='se250RightControls';group.className='se250-group-controls';
  for(const [label,open]of [['Expand all',true],['Collapse all',false]]){
   const b=document.createElement('button');b.type='button';b.textContent=label;
   b.onclick=()=>{for(const d of q('#se249Root #se223Editor')?.querySelectorAll('details.se249-modifier:not([hidden])')||[])d.open=open};
   group.append(b);
  }inspector.after(group);
 }
 const left=q('#se249Root .se249-project-title');if(left&&!q('#se250TreeControls')){
  const group=document.createElement('div');group.id='se250TreeControls';group.className='se250-group-controls';
  for(const [label,open]of [['Expand',true],['Collapse',false]]){
   const b=document.createElement('button');b.type='button';b.textContent=label;
   b.onclick=()=>{for(const d of q('#se249Root .se249-left-main')?.querySelectorAll('details')||[])d.open=open};
   group.append(b);
  }left.after(group);
 }
}
function init(){
 const root=q('#se249Root');if(!root)return false;
 if(root.dataset.se250Installed==='true')return true;
 root.dataset.se250Installed='true';
 state.width.left=Math.min(270,Math.round(innerWidth*.22));
 state.width.right=Math.min(350,Math.round(innerWidth*.28));
 readSaved();
 commandBar();
 addButton(root.querySelector('.se249-left>.se249-tabbar'),'left');
 addButton(root.querySelector('.se249-right>.se249-tabbar'),'right');
 addButton(root.querySelector('.se249-bottom>.se249-tabbar'),'bottom');
 for(const k of ['left','right','bottom'])addHandle(root,k);
 detailsGroup();
 window.addEventListener('resize',apply,{passive:true});
 apply();return true;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>init(),{once:true});else init();
window.SWYRL_ENGINE_PARTICLE_DOCKS_250=Object.freeze({
 inspect:()=>({mode:state.mode,effective:state.effective,width:{...sizes()},
  collapsed:{...state.collapsed},resizers:!!q('#se250Handle-left')}),
 layout:modeTo,collapse,init
});
})();