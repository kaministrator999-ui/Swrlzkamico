// §E v11.250: reference-inspired bottom inspector tracks from real particle data.
// These are previews of validated settings, NOT nonexistent keyframe automation.
(function(){
'use strict';
const q=s=>document.querySelector(s);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const tracks=[
 {name:'Emission',category:'emission',color:'#b75aff',value:c=>c.rate/80,text:c=>c.rate+'/s',
  curve:c=>{const y=23-20*clamp(c.rate/80,0,1);return 'M0 '+y+' L420 '+y}},
 {name:'Size',category:'material',color:'#49bbff',value:c=>c.size/.8,text:c=>c.size.toFixed(2),
  curve:c=>{const y=30-22*clamp(c.size/.8,0,1);
   return 'M0 30 C100 '+y+' 235 '+y+' 420 30'}},
 {name:'Opacity',category:'material',color:'#52dabe',value:c=>1,text:()=> 'fade',
  curve:c=>'M0 24 C20 0 125 0 260 6 C330 12 385 24 420 30'},
 {name:'Color',category:'material',color:'#d85cff',value:c=>.6,text:c=>c.blend,
  curve:c=>'M0 17 C110 17 220 17 420 17'},
 {name:'Rotation',category:'forces',color:'#e2c94f',
  value:c=>(c.vortexSpin||1)/5,text:c=>(c.vortexSpin||1).toFixed(1)+'×',
  curve:c=>{const amp=6+12*clamp((c.vortexSpin||1)/5,0,1);
   return 'M0 16 Q26 '+(16-amp)+' 52 16 T104 16 T156 16 T208 16 T260 16 T312 16 T364 16 T416 16'}}
];
function section(category){
 const tab=q('#se249Root .se249-right .se249-tabbar [data-se249-tab="'+category+'"]');
 tab?.click();
 if(document.body.dataset.se250Layout==='compact'){
  const dock=q('#se249Root [data-se249-mobile=right]');dock?.click();
 }
}
function render(){
 const container=q('#se249LayerRows');if(!container)return;
 const cfg=se223Get(se223State.selected)||se223Data()?.emitters?.[0];
 if(!cfg){container.textContent='Create or select an emitter to see its live parameter profiles.';return;}
 const frag=document.createDocumentFragment();
 for(const track of tracks){
  const row=document.createElement('button');row.type='button';row.className='se250-profile-row';
  row.title='Open '+track.name+' modifier controls';row.onclick=()=>section(track.category);
  const swatch=document.createElement('i');swatch.className='se250-profile-swatch';
  swatch.style.background=track.color;
  const name=document.createElement('span');name.className='se250-profile-label';
  name.textContent=track.name;
  const val=document.createElement('span');val.className='se250-profile-value';
  val.textContent=track.text(cfg);
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.classList.add('se250-profile-curve');svg.setAttribute('viewBox','0 0 420 32');
  svg.setAttribute('preserveAspectRatio','none');svg.setAttribute('aria-hidden','true');
  const path=document.createElementNS('http://www.w3.org/2000/svg','path');
  path.setAttribute('d',track.curve(cfg));path.setAttribute('stroke',track.color);
  path.setAttribute('stroke-width','2.3');path.setAttribute('fill','none');
  svg.append(path);
  row.append(swatch,name,val,svg);frag.append(row);
 }
 container.replaceChildren(frag);
}
function install(){
 const root=q('#se249Root');if(!root)return false;
 if(q('#se250TimelineTools'))return true;
 const timeline=q('#se249Root [data-se249-bottom=timeline]');
 if(!timeline)return false;
 const header=document.createElement('div');header.id='se250TimelineTools';
 header.className='se250-timeline-tools';
 const title=document.createElement('span');title.textContent='PARAMETER PREVIEW · Click a lane to edit';
 header.append(title);
 for(const [label,action,titleText] of [
  ['+','new','Add emitter'],
  ['✕','delete','Delete selected emitter'],
  ['↺','restart','Restart preview']]){
  const b=document.createElement('button');b.type='button';
  b.textContent=label;b.title=titleText;b.setAttribute('aria-label',titleText);
  b.onclick=()=>q('#se249Root [data-se249-action="'+action+'"]')?.click();
  header.append(b);
 }
 timeline.prepend(header);
 const previous=se223UIRefresh;
 se223UIRefresh=function(...args){const result=previous(...args);render();return result;};
 render();return true;
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
else install();
window.SWYRL_ENGINE_PARTICLE_TRACKS_250=Object.freeze({refresh:render,inspect:()=>({
 lanes:tracks.length,persistedKeyframes:false
})});
})();