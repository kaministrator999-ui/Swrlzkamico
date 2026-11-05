// §E v11.274 · viewport Nerd Stats (browser editor; Quest uses existing L3 panel).
// One opt-in DOM overlay, no new WebGL context or animation loop.
(function(){
'use strict';
const s={on:false,mode:'',root:null,button:null,panel:null,body:null,title:null,
 samples:0,timer:null};
const q=sel=>document.querySelector(sel);
const n=v=>Number.isFinite(Number(v))?Math.round(Number(v)).toLocaleString('en-US'):'—';
const f=v=>Number.isFinite(Number(v))?Number(v).toFixed(1):'—';
const present=()=>typeof renderer!=='undefined'&&!!renderer?.xr?.isPresenting;
function active(){
 const a=q('#modelAtelierPanel');
 if(a&&!a.hidden&&q('#modelAtelierViewport'))return 'modeler';
 return window.SWYRL_ENGINE_STUDIOS?.active?.()||'game';
}
function target(mode){
 if(mode==='modeler'&&q('#modelAtelierPanel')&&!q('#modelAtelierPanel').hidden)
  return q('#modelAtelierViewport');
 if(mode==='particles')return q('#se249Root .se249-stage');
 if(mode==='materials')return q('#se225Shell')||null;
 return typeof renderer!=='undefined'?renderer?.domElement:null;
}
function sheepHud(){
 return active()==='game'&&!present()&&typeof stSession!=='undefined'&&
  !!stSession&&!stSession.simulate&&typeof currentProject!=='undefined'&&
  currentProject?.kind==='sheep-tag';
}
function snapshot(m){
 const stress=window.SWYRL_ENGINE_STRESS_TEST_252?.inspect?.()||{};
 const model=m==='modeler'?window.SWYRL_ENGINE_MODEL_STRESS_252?.inspect?.():null;
 const primary=typeof renderer!=='undefined'?renderer?.info:null;
 const ri=model?null:primary;
 const rect=target(m)?.getBoundingClientRect?.();
 const heap=performance?.memory?.usedJSHeapSize;
 return {
  mode:m,rafFPS:stress.approximateFPS??null,rafMS:stress.approximateFrameMs??null,
  calls:model?model.calls:ri?.render?.calls,
  triangles:model?model.drawnTriangles:ri?.render?.triangles,
  points:model?null:ri?.render?.points,
  geometries:model?null:ri?.memory?.geometries,
  textures:model?null:ri?.memory?.textures,
  particleTest:stress.particles?.active?stress.particles.count:0,
  bufferUpdates:stress.particles?.active?stress.particles.updates:0,
  modelTest:stress.model?.active?stress.model.triangles:0,
  emitters:m==='particles'?window.SWYRL_ENGINE_PARTICLES?.inspect?.()?.emitters:null,
  width:rect?Math.round(rect.width):0,height:rect?Math.round(rect.height):0,
  jsMiB:Number.isFinite(heap)?heap/1048576:null
 };
}
function print(d){
 const rows=[
  'RAF FPS       '+n(d.rafFPS),
  'Frame avg     '+f(d.rafMS)+' ms',
  'Draw calls    '+n(d.calls),
  'Triangles     '+n(d.triangles)
 ];
 if(d.points!=null)rows.push('Points drawn  '+n(d.points));
 if(d.geometries!=null)rows.push('GPU objects    '+n(d.textures)+' tex / '+n(d.geometries)+' geo');
 if(d.emitters!=null)rows.push('Emitters       '+n(d.emitters));
 if(d.particleTest)rows.push('Particle load  '+n(d.particleTest)+' pts',
  'Buffer updates '+n(d.bufferUpdates));
 if(d.modelTest)rows.push('Model load     '+n(d.modelTest)+' tris');
 if(d.jsMiB!=null)rows.push('JS heap est.  '+f(d.jsMiB)+' MiB');
 rows.push('Viewport      '+d.width+' × '+d.height);
 return rows.join('\n');
}
function install(){
 if(s.root?.isConnected)return;
 const css=document.createElement('style');css.id='se274Style';
 css.textContent=
 '#se274HUD{position:fixed;left:0;top:0;z-index:10018;pointer-events:none;'+
 'color:#f1e7ff;font:12px/1.55 ui-monospace,Consolas,monospace}'+
 '#se274HUD[hidden],#se274HUD section[hidden]{display:none!important}'+
 '#se274HUD button{pointer-events:auto;background:#301947ed;color:#f3e2ff;'+
 'border:1px solid #a978ea;border-radius:7px;padding:7px 10px;'+
 'font:bold 12px system-ui;box-shadow:0 2px 8px #0009}'+
 '#se274HUD button[aria-pressed=true]{background:#5b3480}'+
 '#se274HUD section{margin-top:5px;width:min(278px,70vw);max-height:48vh;'+
 'overflow:hidden;box-sizing:border-box;background:#0b0b21ef;'+
 'border:1px solid #8054ba;border-radius:9px;padding:9px;'+
 'white-space:pre-wrap;font-variant-numeric:tabular-nums}'+
 '#se274HUD .title{font:bold 11px system-ui;color:#d2adff;margin-bottom:6px}'+
 '#se274HUD small{display:block;color:#b2b8cc;font:10px/1.4 system-ui;margin-top:7px}';
 document.head.append(css);
 s.root=document.createElement('div');s.root.id='se274HUD';s.root.hidden=true;
 s.button=document.createElement('button');s.button.type='button';
 s.button.textContent='▥ Nerd Stats';
 s.button.setAttribute('aria-label','Toggle viewport performance statistics');
 s.button.setAttribute('aria-pressed','false');
 s.panel=document.createElement('section');s.panel.hidden=true;
 s.panel.setAttribute('aria-label','Viewport performance statistics');
 s.title=document.createElement('div');s.title.className='title';
 s.body=document.createElement('div');
 const note=document.createElement('small');
 note.textContent='Approximate RAF cadence, not GPU time. GPU objects are counts, not VRAM bytes.';
 s.panel.append(s.title,s.body,note);s.root.append(s.button,s.panel);
 s.button.addEventListener('click',()=>toggle());
 document.body.append(s.root);
}
function toggle(value){
 s.on=typeof value==='boolean'?value:!s.on;
 s.button?.setAttribute('aria-pressed',String(s.on));
 refresh();return s.on;
}
function refresh(){
 if(!s.root?.isConnected)install();
 const m=active(),rect=target(m)?.getBoundingClientRect?.();
 const valid=!!rect&&rect.width>=120&&rect.height>=120&&!present()&&
  !sheepHud()&&document.visibilityState!=='hidden';
 if(!valid){s.root.hidden=true;return;}
 if(s.mode!==m){s.mode=m;s.on=false;s.button.setAttribute('aria-pressed','false');}
 const x=Math.min(Math.max(5,rect.left+68),Math.max(5,innerWidth-98));
 const y=Math.min(Math.max(5,rect.top+12),Math.max(5,innerHeight-80));
 s.root.style.transform='translate('+Math.round(x)+'px,'+Math.round(y)+'px)';
 s.root.hidden=false;s.panel.hidden=!s.on;
 if(s.on){const data=snapshot(m);s.title.textContent='§E / '+m.toUpperCase();
  s.body.textContent=print(data);s.samples++;}
}
function onKey(e){
 if(e.key!=='F3'||e.repeat||e.altKey||e.ctrlKey||e.metaKey||
  e.target?.closest?.('input,textarea,[contenteditable="true"]'))return;
 if(present()||sheepHud())return;
 e.preventDefault();toggle();
}
function boot(){
 install();refresh();s.timer=setInterval(refresh,800);
 document.addEventListener('keydown',onKey);
 window.addEventListener('pagehide',()=>{
  clearInterval(s.timer);document.removeEventListener('keydown',onKey);
 },{once:true});
}
window.SWYRL_ENGINE_VIEWPORT_NERD_STATS_274=Object.freeze({
 toggle,inspect:()=>({...snapshot(active()),enabled:s.on,samples:s.samples}),
 state:()=>({enabled:s.on,mode:s.mode,shown:!!s.root&&!s.root.hidden})
});
if(document.readyState==='loading')
 document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();