// §E v11.248 · Astral Vortex starter: native particles and real UI.
(function(){
'use strict';
const vortexKey=k=>typeof k==='string'&&/^vortex(?:Cyan|Core|Spark)?$/.test(k);
const oldSpawn=se223Spawn,oldStep=se223Step,oldRefresh=se223UIRefresh;
let glow=null;
function glowMap(){
 if(glow)return glow;
 const c=document.createElement('canvas');c.width=64;c.height=64;
 const ctx=c.getContext('2d');if(!ctx)return null;
 const g=ctx.createRadialGradient(32,32,0,32,32,32);
 g.addColorStop(0,'rgba(255,255,255,1)');
 g.addColorStop(.19,'rgba(255,255,255,.95)');
 g.addColorStop(.43,'rgba(255,255,255,.44)');
 g.addColorStop(1,'rgba(255,255,255,0)');
 ctx.fillStyle=g;ctx.fillRect(0,0,64,64);
 glow=new THREE.CanvasTexture(c);return glow;
}
se223Spawn=function(cfg,n){
 const count=oldSpawn(cfg,n);
 if(!vortexKey(cfg.preset)||!count)return count;
 const rec=se223State.live.get(cfg.id),o=se223Origin(cfg);
 const core=cfg.preset==='vortexCore',sparks=cfg.preset==='vortexSpark';
 for(let i=rec.particles.length-count;i<rec.particles.length;i++){
  const p=rec.particles[i];
  const angle=Math.floor(Math.random()*4)*Math.PI/2+(Math.random()-.5)*(sparks?2.5:.5);
  const radius=core?.03+Math.random()*.16:.18+Math.sqrt(Math.random())*cfg.radius;
  p.se248={angle,radius,height:(Math.random()-.5)*(core?.2:.44),
   speed:(sparks?1.6:2.2)+Math.random()*.55,core,sparks,ox:o.x,oy:o.y,oz:o.z};
  p.x=o.x+Math.cos(angle)*radius;p.y=o.y+p.se248.height;p.z=o.z+Math.sin(angle)*radius;
 }
 const texture=glowMap();if(texture){rec.material.map=texture;rec.material.needsUpdate=true;}
 return count;
};
se223Step=function(cfg,dt){
 if(!vortexKey(cfg.preset))return oldStep(cfg,dt);
 const rec=se223Runtime(cfg),ps=rec.particles;
 const pos=rec.geometry.getAttribute('position'),colors=rec.geometry.getAttribute('color');
 const color=new THREE.Color();
 for(let i=ps.length-1;i>=0;i--){
  const p=ps[i];p.age+=dt;
  if(p.age>=p.life){ps[i]=ps[ps.length-1];ps.pop();continue;}
  const s=p.se248;if(!s)continue;
  const phase=p.age/p.life,remaining=1-phase;
  const radius=s.core?s.radius*(.7+.3*Math.sin(p.age*4)):
   s.sparks?s.radius*(.76+.34*phase):s.radius*(.97-.73*phase);
  const theta=s.angle+(s.core?3.4:s.speed)*p.age+radius*1.24;
  p.x=s.ox+Math.cos(theta)*radius;
  p.z=s.oz+Math.sin(theta)*radius;
  p.y=s.oy+s.height*(.85+.15*remaining)+Math.sin(theta*2.1+phase*4)*radius*(s.core?.12:.11);
 }
 for(let i=0;i<ps.length;i++){
  const p=ps[i],phase=Math.min(1,p.age/p.life);
  const shine=Math.min(1,Math.min(phase*9,(1-phase)*5));
  pos.setXYZ(i,p.x,p.y,p.z);
  color.copy(rec.startColor).lerp(rec.endColor,phase).multiplyScalar(shine*(p.se248?.core?1.5:1.15));
  colors.setXYZ(i,color.r,color.g,color.b);
 }
 rec.material.size=cfg.size*(cfg.preset==='vortexCore'?1.8:1.35);
 rec.geometry.setDrawRange(0,ps.length);pos.needsUpdate=true;colors.needsUpdate=true;
};
function selectedIsVortex(){return vortexKey(se223Get(se223State.selected)?.preset);}
function loadStarter(){
 if(playing||simulating){toast('Stop Play before loading Starter Particles.');return false;}
 const keys=['vortex','vortexCyan','vortexCore','vortexSpark'];
 const result=se223Mutate('Load Astral Vortex starter particles',draft=>{
  if(draft.emitters.length+keys.length>SE223_MAX_EMITTERS)
   throw Error('Astral Vortex needs four empty emitter slots (12 maximum).');
  const created=keys.map(k=>se223Default(k));
  created.forEach(e=>draft.emitters.push(e));
  return created[0].id;
 });
 if(!result)return false;
 se223State.selected=result;se223State.preview=true;se223Reset();
 document.getElementById('projectHub')?.classList.remove('show');
 if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='particles')
  window.SWYRL_ENGINE_STUDIOS?.open?.('particles');
 se223UIRefresh();toast('Astral Vortex loaded · four real emitters · live 3D preview');
 return true;
}
function thumb(){
 const s=document.createElement('div');s.className='se248-thumb';
 s.setAttribute('aria-hidden','true');
 s.innerHTML='<i class="se248-ring one"></i><i class="se248-ring two"></i>'+
  '<i class="se248-ring three"></i><i class="se248-core"></i>';
 return s;
}
function starterCard(){
 const card=document.createElement('article');card.className='se248-starter-card';
 card.append(thumb());
 const t=document.createElement('div');t.className='se248-starter-description';
 t.innerHTML='<strong>Astral Vortex</strong>'+
  '<small>Four native emitters · purple/cyan spirals · luminous core · sparks</small>';
 const b=document.createElement('button');b.type='button';b.textContent='+ Load starter particle';
 b.addEventListener('click',loadStarter);t.append(b);card.append(t);return card;
}
function installProjectTab(){
 const tabs=document.getElementById('se236StarterGroups');
 if(!tabs||document.getElementById('se248StarterTab-particles'))return !!tabs;
 const games=document.getElementById('se236StarterGames');
 const models=document.getElementById('se236StarterModels');
 if(!games||!models)return false;
 const panel=document.createElement('div');panel.id='se248StarterParticles';
 panel.className='se236-starter-grid se248-hub-grid';panel.hidden=true;
 panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','se248StarterTab-particles');
 panel.append(starterCard());models.after(panel);
 const b=document.createElement('button');b.type='button';
 b.id='se248StarterTab-particles';b.textContent='Starter Particles';
 b.setAttribute('role','tab');b.setAttribute('aria-controls',panel.id);
 b.setAttribute('aria-selected','false');b.tabIndex=-1;
 b.addEventListener('click',()=>{
  games.hidden=true;models.hidden=true;panel.hidden=false;
  for(const tab of tabs.querySelectorAll('[role=tab]')){
   const active=tab===b;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;
  }
 });
 for(const tab of tabs.querySelectorAll('[role=tab]'))tab.addEventListener('click',()=>{
  panel.hidden=true;b.setAttribute('aria-selected','false');b.tabIndex=-1;
 });
 b.addEventListener('keydown',e=>{
  if(!['ArrowLeft','ArrowRight'].includes(e.key))return;
  e.preventDefault();tabs.querySelector('#se236StarterTab-games')?.click();
  tabs.querySelector('#se236StarterTab-games')?.focus();
 });
 tabs.append(b);return true;
}
function updateLibrary(){
 const list=document.getElementById('se248EmitterList');if(!list)return;
 const data=se223Data(),frag=document.createDocumentFragment();
 for(const cfg of data?.emitters||[]){
  const b=document.createElement('button');b.type='button';
  b.className='se248-emitter-item';b.classList.toggle('selected',cfg.id===se223State.selected);
  b.textContent=(cfg.enabled?'✦ ':'○ ')+cfg.name;
  b.addEventListener('click',()=>{se223State.selected=cfg.id;se223UIRefresh();});frag.append(b);
 }
 list.replaceChildren(frag);
 const count=document.getElementById('se248EmitterCount');
 if(count)count.textContent=(data?.emitters?.length||0)+' / 12 emitters';
}
se223UIRefresh=function(...args){const r=oldRefresh(...args);updateLibrary();return r;};
function installLibrary(){
 const shell=document.getElementById('se225Shell'),panel=document.getElementById('se223Panel');
 if(!shell||!panel||document.getElementById('se248Library'))
  return !!document.getElementById('se248Library');
 const lib=document.createElement('aside');lib.id='se248Library';lib.className='se248-library';
 lib.innerHTML='<div class="se248-library-head"><strong>PROJECT / PARTICLES</strong>'+
  '<span id="se248EmitterCount"></span></div>'+
  '<div class="se248-library-scroll"><h3>Starter Particles</h3></div>'+
  '<h3>Project Emitters</h3><div id="se248EmitterList" class="se248-emitter-list"></div>';
 lib.querySelector('.se248-library-scroll').append(starterCard());shell.append(lib);
 const nav=shell.querySelector('.se225-workspace-header');
 if(nav&&!document.getElementById('se248Toolbar')){
  const tools=document.createElement('div');tools.id='se248Toolbar';tools.className='se248-toolbar';
  tools.innerHTML='<span class="se248-logo">§E</span><strong>Particle Editor</strong>'+
   '<button type="button" id="se248LibraryToggle">Starter Particles</button>'+
   '<button type="button" id="se248Create">+ New emitter</button>'+
   '<button type="button" id="se248Play">▶ Preview</button>'+
   '<button type="button" id="se248Export">⇧ Export</button>';
  nav.append(tools);
  tools.querySelector('#se248LibraryToggle').onclick=()=>{
   const open=document.body.dataset.se248LibraryOpen!=='true';
   document.body.dataset.se248LibraryOpen=String(open);
   tools.querySelector('#se248LibraryToggle').setAttribute('aria-expanded',String(open));
  };
  tools.querySelector('#se248Create').onclick=()=>panel.querySelector('#se223Create')?.click();
  tools.querySelector('#se248Play').onclick=()=>panel.querySelector('#se223Preview')?.click();
  tools.querySelector('#se248Export').onclick=()=>panel.querySelector('#se223Export')?.click();
 }
 updateLibrary();return true;
}
function boot(){
 installLibrary();installProjectTab();
 const observer=new MutationObserver(()=>{
  if(!document.getElementById('se248Library'))installLibrary();
  if(!document.getElementById('se248StarterTab-particles'))installProjectTab();
  if(document.getElementById('se248Library')&&document.getElementById('se248StarterTab-particles'))
   observer.disconnect();
 });
 if(!document.getElementById('se248Library')||!document.getElementById('se248StarterTab-particles'))
  observer.observe(document.body,{childList:true,subtree:true});
}
window.SWYRL_ENGINE_VORTEX_248=Object.freeze({load:loadStarter,isSelected:selectedIsVortex,
 inspect:()=>({starterTab:!!document.getElementById('se248StarterTab-particles'),
 library:!!document.getElementById('se248Library'),
 emitters:se223List().filter(e=>vortexKey(e.preset)).length,
 selectedIsVortex:selectedIsVortex()})});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});
else boot();
})();