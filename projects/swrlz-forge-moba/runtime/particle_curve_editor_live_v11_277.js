// §E v11.277 — precision curve manipulation with zero-commit live sampling.
// The five persisted channels and native se223Update undo transaction remain
// authoritative. Drag writes only a short-lived preview overlay until release.
(function(){
'use strict';
const SVG='http://www.w3.org/2000/svg';
const q=s=>document.querySelector(s);
const defs=SE251_CURVE_DEFAULTS;
const channels=[
 ['emission','Emission','#ba63ff','Spawn-rate multiplier'],
 ['size','Size','#4bbcff','Particle size envelope'],
 ['opacity','Opacity','#53ddbe','Particle alpha over lifetime'],
 ['color','Color','#ea55d0','Start-to-end color blend'],
 ['rotation','Rotation','#ead267','Vortex rotational speed']
];
const state={channel:'size',draft:null,drag:null,fine:false,root:null,graph:null,
 nodes:[],inputs:[],path:null,help:null,readout:null,selection:null,lastEmitter:null,installed:false};
const clamp=x=>Math.max(0,Math.min(1,Number(x)||0));
const quant=x=>Math.round(clamp(x)*1000)/1000;
const cfg=()=>se223Get(se223State.selected)||se223Data()?.emitters?.[0]||null;
const saved=(c,key)=>Array.isArray(c?.curves?.[key])&&c.curves[key].length===5?
 c.curves[key].slice():defs[key].slice();
const active=c=>state.draft&&c&&c.id===state.draft.id&&state.channel===state.draft.channel?
 state.draft.values:null;
// Used directly by se251CurveValue in the native renderer. Never writes the
// saved project during a gesture, so native Undo/Redo can capture old values.
const api=Object.freeze({
 value:(c,key)=>state.draft&&c?.id===state.draft.id&&key===state.draft.channel?
  state.draft.values:null,
 inspect:()=>({precisionDrag:true,liveRendererSampling:true,channel:state.channel,
   fineMode:state.fine,dragging:!!state.drag,staged:!!state.draft,
   emitterId:state.draft?.id||null,savesPerDrag:1}),
 select:key=>{
  if(!defs[key])return;
  if(state.drag)cancel();
  state.draft=null;state.channel=key;
  q('#se249Root [data-se249-tab=curves]')?.click();
  render();
 }
});
window.SWYRL_ENGINE_CURVE_LIVE_277=api;
window.SWYRL_ENGINE_PARTICLE_CURVES_251=api;
function el(tag,cls,text){
 const n=document.createElement(tag);
 if(cls)n.className=cls;
 if(text!=null)n.textContent=text;
 return n;
}
function svg(tag,attrs={}){
 const n=document.createElementNS(SVG,tag);
 for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));
 return n;
}
const X=i=>28+i*106;
const Y=v=>184-quant(v)*150;
function curvePath(a,xfn=X,yfn=Y){
 let d='';
 for(let i=0;i<5;i++){
  const x=xfn(i),y=yfn(a[i]);
  if(!i)d='M'+x+' '+y;
  else {
   const px=xfn(i-1),py=yfn(a[i-1]);
   const bend=(x-px)*.38;
   d+=' C'+(px+bend)+' '+py+' '+(x-bend)+' '+y+' '+x+' '+y;
  }
 }
 return d;
}
function updateLane(arr){
 // Update only the selected lane, without re-rendering the entire timeline.
 const row=q('#se249LayerRows [data-se251-channel="'+state.channel+'"]');
 const p=row?.querySelector('.se251-timeline-curve path');
 if(!p)return;
 p.setAttribute('d',curvePath(arr,i=>i*105,v=>26-quant(v)*23));
}
function currentValues(){
 const c=cfg();return active(c)||saved(c,state.channel);
}
function paint(){
 if(!state.graph||!state.root)return;
 const c=cfg(),arr=currentValues();
 const ink=channels.find(x=>x[0]===state.channel)?.[2]||'#ba63ff';
 state.path.setAttribute('d',curvePath(arr));
 state.path.setAttribute('stroke',ink);
 for(let i=0;i<5;i++){
  const n=state.nodes[i],x=X(i),y=Y(arr[i]);
  n.dot.setAttribute('cx',x);n.dot.setAttribute('cy',y);
  n.dot.setAttribute('stroke',ink);
  n.hit.setAttribute('cx',x);n.hit.setAttribute('cy',y);
  n.hit.setAttribute('aria-valuenow',Math.round(arr[i]*1000)/10);
  n.hit.setAttribute('aria-valuetext',(arr[i]*100).toFixed(1)+' percent');
  if(document.activeElement!==state.inputs[i])
   state.inputs[i].value=(arr[i]*100).toFixed(1);
  state.inputs[i].disabled=!c;
 }
 const staged=!!active(c);
 const target=state.drag?.index??state.draft?.index??null;
 state.readout.textContent=staged&&target!=null?
  'LIVE · Point '+(target+1)+' · '+(arr[target]*100).toFixed(1)+'%':
  (c?'LIVE PREVIEW READY · '+(state.fine?'FINE ×10':'NORMAL'):'NO EMITTER');
 state.root.dataset.live=String(staged);
 const description=channels.find(x=>x[0]===state.channel)?.[3]||'';
 state.help.textContent=!c?'Select or create a particle emitter to edit curves.':
  (staged?'Previewing live · release to save one Undo step':
  description+' · Drag a node or graph · Fine ×10 for precise moves');
 updateLane(arr);
}
function stage(i,value){
 const c=cfg();if(!c)return;
 if(!state.draft||state.draft.id!==c.id||state.draft.channel!==state.channel)
  state.draft={id:c.id,channel:state.channel,values:saved(c,state.channel),index:i};
 state.draft.index=i;
 const val=quant(value);
 if(state.draft.values[i]===val)return;
 state.draft.values[i]=val;
 paint(); // renderer samples this draft on its next existing engine frame.
}
function cancel(){
 state.drag=null;state.draft=null;
 paint();
}
function commit(){
 const d=state.draft;
 state.drag=null;state.draft=null;
 const c=cfg();
 if(!d||!c||c.id!==d.id)return render();
 const previous=saved(c,d.channel);
 if(previous.every((x,i)=>Math.abs(x-d.values[i])<.0005))return render();
 // Exactly one validated project mutation / undo entry per gesture.
 se223Update(d.id,{curves:{...c.curves,[d.channel]:d.values.slice()}});
 render();
 window.SWYRL_ENGINE_PARAMETER_TIMELINE_251?.refresh?.();
}
function setChannel(key){
 if(!defs[key])return;
 if(state.drag)cancel();
 state.draft=null;state.channel=key;
 render();
}
function begin(e){
 const c=cfg();
 if(!c||state.drag||(e.pointerType==='mouse'&&e.button!==0))return;
 const graph=state.graph,box=graph.getBoundingClientRect();
 if(box.width<=0||box.height<=0)return;
 const indexed=e.target?.getAttribute?.('data-index');
 const guessed=Math.round((e.clientX-box.left)*480/box.width/106-28/106);
 const i=indexed!=null?Number(indexed):Math.max(0,Math.min(4,guessed));
 const values=saved(c,state.channel);
 state.drag={pointerId:e.pointerId,index:i,id:c.id,channel:state.channel,
  startY:e.clientY,startValue:values[i]};
 state.draft={id:c.id,channel:state.channel,values,index:i};
 graph.setPointerCapture?.(e.pointerId);
 paint();e.preventDefault();
}
function move(e){
 const d=state.drag;
 if(!d||d.pointerId!==e.pointerId)return;
 if(cfg()?.id!==d.id||state.channel!==d.channel){cancel();return;}
 const h=state.graph.getBoundingClientRect().height;
 if(!h)return;
 const fine=(state.fine||e.shiftKey||e.altKey)?0.1:1;
 // Delta rather than absolute-y movement: no sudden jump upon grabbing a node.
 const value=d.startValue-(e.clientY-d.startY)*210/(Math.max(24,h)*150)*fine;
 stage(d.index,value);
 e.preventDefault();
}
function end(e){
 if(!state.drag||state.drag.pointerId!==e.pointerId)return;
 commit();
}
function graphNode(i,group){
 const dot=svg('circle',{cx:X(i),cy:Y(.5),r:8.5,fill:'#281735',
  stroke:'#bca0de','stroke-width':2.5,'pointer-events':'none'});
 const hit=svg('circle',{cx:X(i),cy:Y(.5),r:20,fill:'transparent',
  'data-index':i,role:'slider',tabindex:0,
  'aria-label':'Curve point '+(i+1),
  'aria-valuemin':0,'aria-valuemax':100,
  'aria-valuenow':50});
 group.append(dot,hit);
 hit.addEventListener('keydown',e=>{
  if(!['ArrowUp','ArrowDown','Home','End','PageUp','PageDown'].includes(e.key))return;
  e.preventDefault();
  const c=cfg();if(!c)return;
  const arr=saved(c,state.channel);
  const amount=(state.fine||e.shiftKey)?.001:.01;
  const value=e.key==='Home'?0:e.key==='End'?1:
   arr[i]+(e.key==='ArrowUp'||e.key==='PageUp'?1:-1)*
    (e.key.startsWith('Page')?amount*10:amount);
  stage(i,value);commit();
 });
 return {dot,hit};
}
function install(){
 const dock=q('#se249Root [data-se249-bottom=curves]');
 if(!dock)return false;
 if(state.root?.isConnected)return true;
 if(dock.querySelector('#se251CurvePanel'))return true;
 dock.querySelector('#se249CurveSvg')?.setAttribute('hidden','');
 const oldHeader=dock.querySelector('div');
 if(oldHeader)oldHeader.hidden=true;
 const root=el('section','se251-curves se277-live-curve');
 root.id='se251CurvePanel';
 const head=el('div','se251-curves-head');
 head.append(el('strong','', 'CURVE STUDIO'));
 const select=el('select');select.id='se251CurveChannel';
 select.setAttribute('aria-label','Choose particle curve parameter');
 for(const [key,title]of channels)select.append(new Option(title,key));
 select.value=state.channel;
 select.addEventListener('change',()=>setChannel(select.value));
 const fine=el('button','se277-fine','Fine ×10');
 fine.type='button';fine.title='Drag with 10× finer sensitivity';
 fine.setAttribute('aria-pressed','false');
 fine.addEventListener('click',()=>{
  state.fine=!state.fine;fine.setAttribute('aria-pressed',String(state.fine));
  paint();
 });
 const reset=el('button','', '↺ Reset');
 reset.type='button';reset.title='Restore the current channel defaults (undoable)';
 reset.addEventListener('click',()=>{
  const c=cfg();if(!c)return;
  cancel();
  se223Update(c.id,{curves:{...c.curves,[state.channel]:defs[state.channel].slice()}});
  render();
  window.SWYRL_ENGINE_PARAMETER_TIMELINE_251?.refresh?.();
 });
 head.append(select,fine,reset);
 const readout=el('output','se277-curve-readout');
 readout.id='se277CurveReadout';
 readout.setAttribute('aria-live','off');
 const help=el('span');help.id='se251CurveHelp';
 const graph=svg('svg',{id:'se251CurveGraph',viewBox:'0 0 480 210',
  'aria-label':'Fine control curve graph, five draggable points',role:'group'});
 graph.setAttribute('preserveAspectRatio','none');
 for(let i=0;i<5;i++){
  const x=X(i);
  graph.append(svg('line',{x1:x,y1:24,x2:x,y2:192,
   stroke:'#825d9a','stroke-opacity':'.26','pointer-events':'none'}));
  const lab=svg('text',{x,y:202,'text-anchor':'middle',fill:'#8e82a1','font-size':10,
    'pointer-events':'none'});lab.textContent=(i*25)+'%';graph.append(lab);
 }
 for(let i=0;i<=4;i++){
  const y=34+i*37.5;
  graph.append(svg('line',{x1:28,y1:y,x2:452,y2:y,
   stroke:'#825d9a','stroke-opacity':'.25','pointer-events':'none'}));
 }
 const path=svg('path',{id:'se277CurvePath',fill:'none',stroke:'#ba63ff',
  'stroke-width':3.2,'stroke-linejoin':'round','stroke-linecap':'round',
  'pointer-events':'none'});
 graph.append(path);
 const nodes=[];
 for(let i=0;i<5;i++)nodes.push(graphNode(i,graph));
 graph.addEventListener('pointerdown',begin);
 graph.addEventListener('pointermove',move);
 graph.addEventListener('pointerup',end);
 graph.addEventListener('pointercancel',e=>{
  if(state.drag?.pointerId!==e.pointerId)return;
  cancel();
 });
 graph.addEventListener('lostpointercapture',e=>{
  if(state.drag?.pointerId===e.pointerId)commit();
 });
 const values=el('div','se251-curve-values');
 values.id='se251CurveValues';
 const inputs=[];
 for(let i=0;i<5;i++){
  const label=el('label');label.append(el('span','',(25*i)+'%'));
  const input=el('input');input.type='number';input.inputMode='decimal';
  input.min='0';input.max='100';input.step='0.1';
  input.setAttribute('aria-label','Curve value at '+(25*i)+' percent');
  input.addEventListener('input',()=>{
   const n=Number(input.value);
   if(input.value!==''&&Number.isFinite(n))stage(i,n/100);
  });
  input.addEventListener('change',()=>{
   const n=Number(input.value);
   if(input.value!==''&&Number.isFinite(n))stage(i,n/100);
   commit();
  });
  input.addEventListener('keydown',e=>{
   if(e.key==='Escape'){e.preventDefault();cancel();input.blur();}
   if(e.key==='Enter'){input.blur();}
  });
  label.append(input);values.append(label);inputs.push(input);
 }
 root.append(head,readout,help,graph,values);dock.append(root);
 Object.assign(state,{root,graph,help,readout,path,nodes,inputs,selection:select,installed:true});
 const prevRefresh=se223UIRefresh;
 se223UIRefresh=function(...args){
  const out=prevRefresh(...args);
  render();return out;
 };
 render();
 return true;
}
function render(){
 if(!state.root?.isConnected)return;
 const c=cfg();
 if(state.draft&&(!c||c.id!==state.draft.id))cancel();
 state.selection.value=state.channel;
 paint();
}
function boot(){
 if(install())return;
 const mo=new MutationObserver(()=>{if(install())mo.disconnect()});
 mo.observe(document.body,{childList:true,subtree:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();
