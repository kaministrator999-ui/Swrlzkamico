// §E v11.251 — native five-point editable particle curves. No fake keyframe state.
// Each point is validated and saved via se223Update -> one native undo transaction.
(function(){
'use strict';
const qs=s=>document.querySelector(s),SVG='http://www.w3.org/2000/svg';
const channels=[
 ['emission','Emission','#ba63ff','Spawn-rate multiplier'],
 ['size','Size','#4bbcff','Particle and ribbon size'],
 ['opacity','Opacity','#53ddbe','Particle and ribbon alpha'],
 ['color','Color','#ea55d0','Start/end color mixing'],
 ['rotation','Rotation','#ead267','Vortex rotational speed']
];
const defaults={emission:[.64,.75,.88,.75,.64],size:[.45,.8,1,.8,.42],
 opacity:[0,.92,1,.92,0],color:[0,.22,.5,.78,1],
 rotation:[.47,.62,.75,.62,.47]};
const state={channel:'size',draft:null,drag:null,installed:false,lastId:null};
const cfg=()=>se223Get(se223State.selected)||se223Data()?.emitters?.[0]||null;
const clamp=x=>Math.max(0,Math.min(1,Number(x)||0));
function dataFor(c,key){
 const v=c?.curves?.[key];return Array.isArray(v)&&v.length===5?v.slice():defaults[key].slice();
}
function svg(tag,attr={}){
 const e=document.createElementNS(SVG,tag);
 for(const [k,v] of Object.entries(attr))e.setAttribute(k,String(v));return e;
}
function pathFor(a){
 let d='';
 for(let j=0;j<5;j++){
  const x=26+j*105,y=180-clamp(a[j])*150;
  if(j===0)d='M'+x+' '+y;
  else {
   const x0=26+(j-1)*105,y0=180-clamp(a[j-1])*150;
   d+=' C'+(x0+40)+' '+y0+' '+(x-40)+' '+y+' '+x+' '+y;
  }
 }
 return d;
}
function install(){
 const dock=qs('#se249Root [data-se249-bottom=curves]');
 if(!dock)return false;
 if(dock.querySelector('#se251CurvePanel'))return true;
 dock.querySelector('#se249CurveSvg')?.setAttribute('hidden','');
 const oldHeader=dock.querySelector('div');if(oldHeader)oldHeader.hidden=true;
 const panel=document.createElement('div');panel.id='se251CurvePanel';panel.className='se251-curves';
 const header=document.createElement('div');header.className='se251-curves-head';
 const caption=document.createElement('strong');caption.textContent='CURVE EDITOR';
 const select=document.createElement('select');select.id='se251CurveChannel';
 select.setAttribute('aria-label','Select the particle curve to edit');
 for(const [id,title] of channels){const o=new Option(title,id);select.append(o)}
 select.value=state.channel;select.addEventListener('change',()=>{
  state.channel=select.value;state.draft=null;render();
 });
 const reset=document.createElement('button');reset.type='button';reset.textContent='↺ Reset';
 reset.title='Restore the selected parameter curve to its default';
 reset.addEventListener('click',()=>{
  const c=cfg();if(!c)return;
  if(se223Update(c.id,{curves:{...c.curves,[state.channel]:defaults[state.channel].slice()}})!==false){
   state.draft=null;render();
  }
 });
 header.append(caption,select,reset);
 const help=document.createElement('span');help.id='se251CurveHelp';
 help.textContent='Drag nodes or edit values. Release to save an undoable curve change.';
 const graph=svg('svg',{id:'se251CurveGraph',viewBox:'0 0 472 207',
  role:'group','aria-label':'Editable five-node particle parameter curve'});
 graph.setAttribute('preserveAspectRatio','none');
 graph.addEventListener('pointermove',e=>{
  if(!state.drag)return;
  const r=graph.getBoundingClientRect();
  if(!r.width||!r.height)return;
  const y=207*(e.clientY-r.top)/r.height;
  updateDraft(state.drag.index,clamp((180-y)/150));
  e.preventDefault();
 });
 graph.addEventListener('pointerup',()=>saveDraft());
 graph.addEventListener('pointercancel',()=>cancelDrag());
 graph.addEventListener('lostpointercapture',()=>{if(state.drag)saveDraft();});
 const values=document.createElement('div');values.id='se251CurveValues';
 values.className='se251-curve-values';
 panel.append(header,help,graph,values);dock.append(panel);
 state.installed=true;
 const prevRefresh=se223UIRefresh;
 se223UIRefresh=function(...args){const result=prevRefresh(...args);render();return result;};
 render();return true;
}
function updateDraft(index,v){
 const c=cfg();if(!c)return;
 if(!state.draft)state.draft=dataFor(c,state.channel);
 state.draft[index]=Math.round(clamp(v)*1000)/1000;
 render(true);
}
function saveDraft(){
 if(!state.drag&&!state.draft)return;
 const c=cfg(),draft=state.draft;
 state.drag=null;state.draft=null;
 if(!c||!draft)return render();
 const current=dataFor(c,state.channel);
 if(current.every((x,i)=>Math.abs(x-draft[i])<.0005))return render();
 se223Update(c.id,{curves:{...c.curves,[state.channel]:draft.slice()}});
 render();
}
function cancelDrag(){state.drag=null;state.draft=null;render()}
function render(noInputUpdate=false){
 const root=qs('#se251CurvePanel');if(!root)return;
 const c=cfg(),values=root.querySelector('#se251CurveValues'),graph=root.querySelector('#se251CurveGraph');
 root.querySelector('#se251CurveChannel').value=state.channel;
 const lineColor=channels.find(x=>x[0]===state.channel)?.[2]||'#ae6bff';
 const arr=state.draft||dataFor(c,state.channel);
 graph.replaceChildren();
 for(let i=0;i<=5;i++){
  const x=26+i*84;graph.append(svg('line',{x1:x,y1:17,x2:x,y2:185,stroke:'#6a477a','stroke-opacity':'.32'}));
 }
 for(let i=0;i<=4;i++){
  const y=30+i*37.5;graph.append(svg('line',{x1:26,y1:y,x2:446,y2:y,stroke:'#6a477a','stroke-opacity':'.32'}));
 }
 graph.append(svg('path',{d:pathFor(arr),stroke:lineColor,'stroke-width':3.2,
  'stroke-linejoin':'round',fill:'none'}));
 for(let i=0;i<5;i++){
  const x=26+105*i,y=180-arr[i]*150;
  graph.append(svg('circle',{cx:x,cy:y,r:11,fill:'#2a1737',
   stroke:lineColor,'stroke-width':3}));
  const handle=svg('circle',{cx:x,cy:y,r:16,fill:'transparent',
   role:'slider','aria-label':'Curve point '+(i+1),
   'aria-valuemin':0,'aria-valuemax':100,
   'aria-valuenow':Math.round(arr[i]*100),tabindex:0,'data-index':i});
  handle.style.cursor='ns-resize';
  handle.addEventListener('pointerdown',e=>{
   if(!c||e.button!==0)return;
   state.drag={index:i,pointerId:e.pointerId,emitterId:c.id,channel:state.channel};
   state.draft=dataFor(c,state.channel);
   graph.setPointerCapture?.(e.pointerId);e.preventDefault();
  });
  handle.addEventListener('keydown',e=>{
   if(!['ArrowUp','ArrowDown','Home','End'].includes(e.key))return;
   e.preventDefault();const delta=e.shiftKey?.1:.025;
   const value=e.key==='Home'?0:e.key==='End'?1:
    arr[i]+(e.key==='ArrowUp'?delta:-delta);
   state.drag={index:i};updateDraft(i,value);saveDraft();
  });
  graph.append(handle);
 }
 if(!noInputUpdate){
  values.replaceChildren();
  for(let i=0;i<5;i++){
   const label=document.createElement('label');
   label.textContent=(i*25)+'%';
   const input=document.createElement('input');input.type='number';
   input.min='0';input.max='100';input.step='1';
   input.value=String(Math.round(arr[i]*100));input.disabled=!c;
   input.setAttribute('aria-label','Curve at '+(i*25)+' percent');
   input.addEventListener('change',()=>{
    const n=Number(input.value);
    if(!Number.isFinite(n)){render();return}
    state.drag={index:i};updateDraft(i,n/100);saveDraft();
   });
   label.append(input);values.append(label);
  }
 }
 const context=root.querySelector('#se251CurveHelp');
 const title=channels.find(x=>x[0]===state.channel)?.[3]||'';
 context.textContent=c?
   (title+' · drag handles / edit five values · native Undo/Redo supported'):
   'Create or select an emitter to edit and save its animation curves';
}
function boot(){
 if(install())return;
 const mo=new MutationObserver(()=>{if(install())mo.disconnect()});
 mo.observe(document.body,{childList:true,subtree:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
window.SWYRL_ENGINE_PARTICLE_CURVES_251=Object.freeze({
 inspect:()=>({editable:true,channel:state.channel,emitter:cfg()?.name||null,points:5}),
 select:key=>{if(defaults[key]){state.channel=key;state.draft=null;
 qs('#se249Root .se249-bottom [data-se249-tab=curves]')?.click();render();}}
});
})();