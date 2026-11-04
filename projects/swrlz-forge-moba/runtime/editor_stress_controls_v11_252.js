// §E v11.252 · opt-in model/particle stress diagnostics.
// This module shares the already existing Three.js renderers and edit-mode scenes.
(function(){
'use strict';
const MAX={model:1000000,particles:1000000};
const defaults={model:10000,particles:1000};
const state={particle:null,canvas:null,started:0,raf:0,last:0,frames:0,fps:0,ms:0,modelHost:null,particleHost:null};
const q=s=>document.querySelector(s);
const fmt=n=>Math.round(n||0).toLocaleString('en-US');
function stopParticles(){
 const p=state.particle;
 if(p){
  p.points.removeFromParent();
  p.geometry.dispose();p.material.dispose();
  state.particle=null;
 }
 return {active:false,count:0};
}
function validStage(){
 return !!(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.()
   &&scene&&renderer&&!playing&&!simulating&&!renderer.xr?.isPresenting
   &&window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles');
}
function applyParticles(requested){
 const count=Number(requested);
 if(!Number.isSafeInteger(count)||count<100||count>MAX.particles)
  return {error:'Choose 100–1,000,000 particles.'};
 if(!validStage())return {error:'Open Particle Studio in Edit mode and enter the test chamber first.'};
 let geometry=null,material=null,points=null;
 try{
  const pos=new Float32Array(count*3),color=new Float32Array(count*3);
  const angles=new Float32Array(count),radii=new Float32Array(count),heights=new Float32Array(count);
  for(let i=0,j=0;i<count;i++,j+=3){
   const a=Math.random()*Math.PI*2, r=.25+2.15*Math.sqrt(Math.random()),h=(Math.random()-.5)*1.5;
   angles[i]=a;radii[i]=r;heights[i]=h;
   pos[j]=Math.cos(a)*r;pos[j+1]=2.75+h;pos[j+2]=Math.sin(a)*r;
   const cyan=i%3===0;
   color[j]=cyan?.18:.68;color[j+1]=cyan?.79:.23;color[j+2]=1;
  }
  geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.BufferAttribute(pos,3));
  geometry.setAttribute('color',new THREE.BufferAttribute(color,3));
  material=new THREE.PointsMaterial({size:.052,vertexColors:true,
   transparent:true,opacity:.82,depthWrite:false,blending:THREE.AdditiveBlending,
   sizeAttenuation:true});
  points=new THREE.Points(geometry,material);
  points.layers.set(25);
  points.frustumCulled=false;
  points.name='Diagnostic particle cloud (temporary, unsaved)';
  points.userData.se252Diagnostic=true;
  const previous=state.particle;
  scene.add(points);
  state.particle={points,geometry,material,angles,radii,heights,count,
   scene,project:currentProject,stage:window.SWYRL_ENGINE_PARTICLE_STAGE_240,
   frame:0};
  if(previous){previous.points.removeFromParent();previous.geometry.dispose();previous.material.dispose();}
  return {active:true,count};
 }catch(error){
  points?.removeFromParent();geometry?.dispose();material?.dispose();
  return {error:'Particle test allocation failed: '+String(error?.message||error).slice(0,90)};
 }
}
function updateParticles(now){
 const p=state.particle;
 if(!p)return;
 if(document.visibilityState==='hidden'||!validStage()||scene!==p.scene||currentProject!==p.project){
  stopParticles();paint('particles');return;
 }
 // Update real buffer positions each frame so this tests CPU simulation +
 // GPU point-cloud upload/drawing, not merely a static shader decoration.
 const t=Math.min(86400,(now-state.started)/1000);
 const a=p.geometry.getAttribute('position'),pos=a.array;
 for(let i=0,j=0;i<p.count;i++,j+=3){
  const angle=p.angles[i]+t*(.27+(i%7)*.035),radius=p.radii[i];
  pos[j]=Math.cos(angle)*radius;
  pos[j+1]=2.75+p.heights[i]+.12*Math.sin(angle*2);
  pos[j+2]=Math.sin(angle)*radius;
 }
 a.needsUpdate=true;p.frame++;
}
function stopModel(){
 return window.SWYRL_ENGINE_MODEL_STRESS_252?.stop?.()||{active:false,triangles:0};
}
function stop(which){
 const result=which==='model'?stopModel():stopParticles();
 paint(which);return result;
}
function inspect(){
 return {model:window.SWYRL_ENGINE_MODEL_STRESS_252?.inspect?.()||null,
  particles:{active:!!state.particle,count:state.particle?.count||0,
   updates:state.particle?.frame||0},
  approximateFPS:state.fps,approximateFrameMs:state.ms};
}
function apply(which,value){
 const result=which==='model'?
  window.SWYRL_ENGINE_MODEL_STRESS_252?.apply?.(value)||{error:'Model Atelier is not ready.'}:
  applyParticles(value);
 const panel=q('#se252-'+which);
 const output=panel?.querySelector('[data-se252-status]');
 if(output)output.textContent=result.error||('Running '+fmt(result.triangles||result.count)+' '+(which==='model'?'triangles':'particles'));
 paint(which);
 return result;
}
function paint(which){
 const panel=q('#se252-'+which);
 if(!panel)return;
 const running=which==='model'?
  window.SWYRL_ENGINE_MODEL_STRESS_252?.inspect?.():
  {active:!!state.particle,triangles:0,count:state.particle?.count||0};
 const info=panel.querySelector('[data-se252-readout]');
 if(info)info.textContent=running?.active?
  (which==='model'?fmt(running.triangles)+' triangles · '+fmt(running.calls)+' model draw calls':
   fmt(running.count)+' particles · '+fmt(state.particle?.frame)+' buffer updates'):
  'No diagnostic geometry active';
 const perf=panel.querySelector('[data-se252-fps]');
 if(perf)perf.textContent=fmt(state.fps)+' RAF FPS · '+(state.ms||0).toFixed(1)+' ms/frame (approx.)';
 panel.querySelector('[data-se252-stop]').disabled=!running?.active;
}
function makePanel(which){
 const host=which==='model'?q('#modelAtelierPanel .atelier-inspector'):q('#se249Root .se249-right');
 if(!host||q('#se252-'+which))return;
 const panel=document.createElement('details');
 panel.id='se252-'+which;panel.className='se252-stress';
 const heading=document.createElement('summary');
 heading.textContent='⚙ Stress Test · '+(which==='model'?'Model Geometry':'Particles');
 const note=document.createElement('p');
 note.textContent=which==='model'?
  'Temporary high-poly sphere in the model viewport; actual generated triangle count. Never saved.' :
  'Temporary animated point cloud in the Particle Chamber. Native emitter limits and project files stay unchanged.';
 const controls=document.createElement('div');controls.className='se252-controls';
 const slider=document.createElement('input');slider.type='range';slider.min='100';
 slider.max=String(MAX[which]);slider.step='100';slider.value=String(defaults[which]);
 slider.setAttribute('aria-label',which+' stress count slider');
 const num=document.createElement('input');num.type='number';num.min='100';
 num.max=String(MAX[which]);num.step='100';num.value=String(defaults[which]);
 num.inputMode='numeric';num.setAttribute('aria-label',which+' stress count numeric input');
 slider.addEventListener('input',()=>{num.value=slider.value;});
 num.addEventListener('input',()=>{if(num.value&&Number.isFinite(+num.value))slider.value=num.value;});
 controls.append(slider,num);
 const buttons=document.createElement('div');buttons.className='se252-actions';
 const start=document.createElement('button');start.type='button';start.textContent='▶ Apply load';
 const halt=document.createElement('button');halt.type='button';halt.textContent='■ Stop';
 halt.dataset.se252Stop='';
 start.addEventListener('click',()=>{
  const n=Number(num.value);
  if(!Number.isSafeInteger(n)||n<100||n>MAX[which]){status.textContent='Enter a whole number from 100 to 1,000,000.';return;}
  apply(which,n);
 });
 halt.addEventListener('click',()=>{
  stop(which);status.textContent='Diagnostic stopped; saved scene unchanged.';
 });
 buttons.append(start,halt);
 const status=document.createElement('output');status.dataset.se252Status='';status.textContent='Ready (nothing is running).';
 const counts=document.createElement('div');counts.dataset.se252Readout='';
 const fps=document.createElement('div');fps.dataset.se252Fps='';
 const foot=document.createElement('small');foot.textContent=
  'Apply is manual, not continuous while sliding. High values may freeze a slow device; use Stop when responsive. FPS is an approximate browser animation-frame sample, not a GPU timer.';
 panel.append(heading,note,controls,buttons,status,counts,fps,foot);
 host.append(panel);paint(which);
}
function boot(){makePanel('model');makePanel('particles');}
const observer=new MutationObserver(()=>{if(!q('#se252-model')||!q('#se252-particles'))boot();});
function frame(now){
 state.raf=requestAnimationFrame(frame);
 if(!state.started)state.started=now;
 const dt=state.last?now-state.last:16.67;state.last=now;
 state.frames++;
 if(!state.sample)state.sample=now;
 if(now-state.sample>=700){
  state.fps=Math.round(state.frames*1000/(now-state.sample));
  state.ms=(now-state.sample)/state.frames;
  state.frames=0;state.sample=now;
  paint('model');paint('particles');
 }
 const modelState=window.SWYRL_ENGINE_MODEL_STRESS_252?.inspect?.();
 if(modelState?.active&&!modelState.open){stopModel();paint('model');}
 updateParticles(now);
}
window.addEventListener('pagehide',()=>{stopParticles();stopModel();cancelAnimationFrame(state.raf);observer.disconnect()});
document.addEventListener('visibilitychange',()=>{
 if(document.visibilityState==='hidden'){stopParticles();stopModel();paint('model');paint('particles');}
});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
observer.observe(document.body,{childList:true,subtree:true});
state.raf=requestAnimationFrame(frame);
window.SWYRL_ENGINE_STRESS_TEST_252=Object.freeze({apply,stop,inspect});
})();
