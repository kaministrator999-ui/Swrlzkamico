// §E v11.251: real 5-channel timeline, linked to editable saved Curves.
// Prior emitter-list rows were re-rendered every 70 ms and hid the parameter lanes.
(function(){
'use strict';
const q=s=>document.querySelector(s),NS='http://www.w3.org/2000/svg';
const chans=[
 ['emission','Emission','#b958f7'],
 ['size','Size','#42bbff'],
 ['opacity','Opacity','#58dec9'],
 ['color','Color','#ed56c8'],
 ['rotation','Rotation','#f3dc57']
];
function current(){return se223Get(se223State.selected)||se223Data()?.emitters?.[0]||null}
function curve(cfg,key){
 return cfg?.curves?.[key]||SE251_CURVE_DEFAULTS[key];
}
function makeSvg(cfg,key,color){
 const s=document.createElementNS(NS,'svg');s.classList.add('se251-timeline-curve');
 s.setAttribute('viewBox','0 0 420 27');s.setAttribute('preserveAspectRatio','none');
 s.setAttribute('aria-hidden','true');
 const v=curve(cfg,key),path=document.createElementNS(NS,'path');
 let d='M0 '+(26-v[0]*23);
 for(let i=1;i<5;i++){
  const x=105*i,y=26-v[i]*23,previousX=105*(i-1),lastY=26-v[i-1]*23;
  d+=' C'+(previousX+44)+' '+lastY+' '+(x-44)+' '+y+' '+x+' '+y;
 }
 path.setAttribute('d',d);path.setAttribute('stroke',color);
 path.setAttribute('stroke-width','2.7');path.setAttribute('fill','none');
 s.append(path);return s;
}
function render(){
 const box=q('#se249LayerRows');if(!box)return;
 const cfg=current();
 if(!cfg){box.textContent='Select an emitter to edit animation channels.';return;}
 const frag=document.createDocumentFragment();
 for(const [key,title,color]of chans){
  const row=document.createElement('button');row.type='button';
  row.className='se251-timeline-lane';row.dataset.se251Channel=key;
  row.title='Edit '+title+' animation curve';
  row.addEventListener('click',()=>window.SWYRL_ENGINE_PARTICLE_CURVES_251?.select?.(key));
  const dot=document.createElement('i');dot.style.background=color;
  const name=document.createElement('strong');name.textContent=title;
  const track=document.createElement('span');track.className='se251-lane-track';
  track.style.setProperty('--se251-lane',color);
  track.append(makeSvg(cfg,key,color));
  row.append(dot,name,track);frag.append(row);
 }
 box.replaceChildren(frag);
 const note=q('#se250TimelineTools span');
 if(note)note.textContent='ANIMATION · Five editable channels · Tap any track to open its curve';
}
function install(){
 if(!q('#se249LayerRows'))return false;
 if(q('#se249LayerRows').dataset.se251Ready)return true;
 q('#se249LayerRows').dataset.se251Ready='1';
 const prevRefresh=se223UIRefresh;
 se223UIRefresh=function(...args){
  const result=prevRefresh(...args);render();return result;
 };
 render();return true;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
else install();
window.SWYRL_ENGINE_PARAMETER_TIMELINE_251=Object.freeze({
 refresh:render,inspect:()=>({channels:chans.map(x=>x[0]),editable:true})
});
})();