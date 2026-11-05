// §E v11.280 · Mage Spell Lab. Native Particle Studio presets + WebXR glove cast tests.
// No second renderer or frame loop, no casting into other starter games.
const SE280_SPELLS=Object.freeze({
 emberBolt:{name:'Ember Bolt',desc:'Fast orange fire streak with sparks',motion:'bolt',school:'Fire'},
 infernoBreath:{name:'Inferno Breath',desc:'Wide blazing cone from the palm',motion:'cone',school:'Fire'},
 frostNova:{name:'Frost Nova',desc:'Expanding ring of icy crystal motes',motion:'ring',school:'Ice'},
 iceLance:{name:'Ice Lance',desc:'Needle-sharp cyan projectile trail',motion:'bolt',school:'Ice'},
 stormArc:{name:'Storm Arc',desc:'Electric bolt with crackling fragments',motion:'storm',school:'Storm'},
 chainStorm:{name:'Chain Storm',desc:'Wide branching electric energy',motion:'storm',school:'Storm'},
 arcaneMissile:{name:'Arcane Missile',desc:'Purple/blue focused energy projectile',motion:'bolt',school:'Arcane'},
 runeCircle:{name:'Runic Halo',desc:'Rotating arcane ritual circle',motion:'ring',school:'Arcane'},
 healingCircle:{name:'Healing Bloom',desc:'Rising green healing star motes',motion:'bloom',school:'Life'},
 holyNova:{name:'Radiant Nova',desc:'Golden radiant shockwave',motion:'nova',school:'Light'},
 shadowPulse:{name:'Shadow Pulse',desc:'Dark violet expanding shockwave',motion:'nova',school:'Shadow'},
 voidOrb:{name:'Void Orb',desc:'Dense swirling singularity motes',motion:'spiral',school:'Void'},
 gravityWell:{name:'Gravity Well',desc:'Orbiting cosmic gravity ribbons',motion:'spiral',school:'Void'},
 earthBurst:{name:'Stone Burst',desc:'Erupting earthy rock and dust energy',motion:'nova',school:'Earth'},
 meteorShower:{name:'Meteor Rain',desc:'Falling fiery comet fragments',motion:'rain',school:'Fire'},
 windSpiral:{name:'Wind Cyclone',desc:'Teal curling wind trails',motion:'spiral',school:'Wind'},
 crystalBloom:{name:'Crystal Bloom',desc:'Gemlike prismatic ice energy',motion:'bloom',school:'Ice'},
 thunderRing:{name:'Thunder Ring',desc:'A bright electric ring blast',motion:'ring',school:'Storm'}
});
const SE280_CYCLE=['arcaneMissile','emberBolt','frostNova','stormArc','healingCircle','shadowPulse','windSpiral','holyNova','voidOrb','infernoBreath','iceLance','meteorShower'];
const SE280_PACK=['emberBolt','frostNova','stormArc','arcaneMissile','healingCircle','shadowPulse','gravityWell','holyNova'];
const se280SpellState={
 left:'frostNova',right:'emberBolt',castCount:0,lastError:'',live:[],
 edge:{left:false,right:false},stick:{left:false,right:false},
 signs:new Map(),lastFrame:0,glow:null
};
function se280ReadLoadout(){
 try{
  const raw=JSON.parse(localStorage.getItem('swyrl.mage.gloves.v1')||'null');
  for(const side of ['left','right'])if(SE223_PRESETS[raw?.[side]])se280SpellState[side]=raw[side];
 }catch(_){}
}
se280ReadLoadout();
function se280Equip(side,key){
 if(!['left','right'].includes(side)||!Object.prototype.hasOwnProperty.call(SE223_PRESETS,key))return false;
 se280SpellState[side]=key;
 try{localStorage.setItem('swyrl.mage.gloves.v1',JSON.stringify({
  left:se280SpellState.left,right:se280SpellState.right
 }));}catch(_){}
 for(const select of document.querySelectorAll('[data-se280-equip="'+side+'"]'))select.value=key;
 const sign=se280SpellState.signs.get(side);
 if(sign)se280PaintSign(sign,side);
 return true;
}
function se280Cycle(side){
 const old=SE280_CYCLE.indexOf(se280SpellState[side]);
 se280Equip(side,SE280_CYCLE[(old+1)%SE280_CYCLE.length]);
}
function se280AddPreset(key){
 if(!Object.prototype.hasOwnProperty.call(SE223_PRESETS,key))return false;
 const emitter=se223Create(key);
 if(!emitter)return false;
 if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='particles')
  window.SWYRL_ENGINE_STUDIOS?.open?.('particles');
 se223State.selected=emitter.id;se223State.preview=true;se223UIRefresh();
 document.getElementById('projectHub')?.classList.remove('show');
 toast('Added editable '+SE223_PRESETS[key].label+' particles to this project.');
 return true;
}
function se280LoadPack(){
 if(playing||simulating){toast('Stop Play before adding a spell pack.');return false;}
 const result=se223Mutate('Load Mage Spell particle pack',draft=>{
  if(draft.emitters.length+SE280_PACK.length>SE223_MAX_EMITTERS)
   throw Error('Mage pack needs '+SE280_PACK.length+' free slots (12 maximum).');
  const created=SE280_PACK.map((key,i)=>{
   const e=se223Default(key);
   e.position=[(i%4-1.5)*2,1.7,Math.floor(i/4)*-2];
   draft.emitters.push(e);return e;
  });
  return created[0].id;
 });
 if(!result)return false;
 se223State.selected=result;se223State.preview=true;se223Reset();
 document.getElementById('projectHub')?.classList.remove('show');
 window.SWYRL_ENGINE_STUDIOS?.open?.('particles');se223UIRefresh();
 toast('8-spell Mage Pack added to the native Particle Studio · editable and exportable');
 return true;
}
function se280CatalogEntries(){
 return Object.entries(SE223_PRESETS).map(([key,p])=>({
  key,name:SE280_SPELLS[key]?.name||p.label,
  description:SE280_SPELLS[key]?.desc||('Native '+p.shape+' · '+p.mode+' · '+p.blend),
  category:SE280_SPELLS[key]?'Mage Spells':/^vortex/i.test(key)?'Astral Vortex':'Engine Originals',
  accent:p.startColor
 }));
}
function se280MakeLoadoutControls(){
 const wrap=document.createElement('div');wrap.className='se280-equip';
 const title=document.createElement('strong');title.textContent='🥽 Quest VR spell loadout';
 const hint=document.createElement('small');
 hint.textContent='Pull either trigger to cast. Click that hand’s thumbstick (L3/R3) to cycle spells. Grip still bends the glove.';
 wrap.append(title,hint);
 for(const side of ['left','right']){
  const label=document.createElement('label');label.textContent=(side==='left'?'Left':'Right')+' glove';
  const select=document.createElement('select');select.dataset.se280Equip=side;
  for(const entry of se280CatalogEntries()){
   const option=document.createElement('option');option.value=entry.key;
   option.textContent=entry.name;select.append(option);
  }
  select.value=se280SpellState[side];
  select.addEventListener('change',()=>se280Equip(side,select.value));
  label.append(select);wrap.append(label);
 }
 return wrap;
}
function se280MakeCatalog(host,compact=false){
 if(!host||host.querySelector('[data-se280-catalog]'))return;
 const panel=document.createElement('section');panel.className='se280-catalog'+(compact?' se280-compact':'');
 panel.dataset.se280Catalog='true';
 const header=document.createElement('div');header.className='se280-head';
 const heading=document.createElement('h3');heading.textContent='⚡ §E Particle & Spell Library';
 const desc=document.createElement('p');desc.textContent='All registered native particle presets, plus 18 new mage spells. Each adds editable emitters to the current project.';
 const pack=document.createElement('button');pack.type='button';pack.className='se280-pack';
 pack.textContent='+ Load 8-spell Mage Particle Pack';
 pack.addEventListener('click',se280LoadPack);
 const filter=document.createElement('input');filter.type='search';filter.placeholder='Find a particle or spell…';
 filter.setAttribute('aria-label','Filter particle library');
 header.append(heading,desc,pack,filter,se280MakeLoadoutControls());
 const grid=document.createElement('div');grid.className='se280-grid';
 const entries=se280CatalogEntries();
 const nodes=[];
 for(const entry of entries){
  const card=document.createElement('article');card.className='se280-effect';
  card.style.setProperty('--se280-accent',entry.accent);
  const top=document.createElement('div');top.className='se280-effect-top';
  const dot=document.createElement('span');dot.className='se280-swatch';dot.setAttribute('aria-hidden','true');
  const badge=document.createElement('small');badge.textContent=entry.category;
  top.append(dot,badge);
  const name=document.createElement('strong');name.textContent=entry.name;
  const copy=document.createElement('p');copy.textContent=entry.description;
  const actions=document.createElement('div');actions.className='se280-actions';
  const add=document.createElement('button');add.type='button';add.textContent='+ Add emitter';
  add.addEventListener('click',()=>se280AddPreset(entry.key));
  actions.append(add);
  if(SE280_SPELLS[entry.key]){
   for(const side of ['left','right']){
    const equip=document.createElement('button');equip.type='button';
    equip.textContent=side==='left'?'L glove':'R glove';equip.title='Equip '+entry.name+' to '+side+' VR hand';
    equip.addEventListener('click',()=>{se280Equip(side,entry.key);equip.textContent='✓ '+(side==='left'?'L':'R');});
    actions.append(equip);
   }
  }
  card.append(top,name,copy,actions);grid.append(card);
  nodes.push({card,query:(entry.name+' '+entry.description+' '+entry.category+' '+entry.key).toLowerCase()});
 }
 const count=document.createElement('small');count.className='se280-count';
 const render=()=>{
  const q=filter.value.trim().toLowerCase();let visible=0;
  for(const row of nodes){row.card.hidden=!!q&&!row.query.includes(q);if(!row.card.hidden)visible++;}
  count.textContent=visible+' / '+entries.length+' effects · '+Object.keys(SE280_SPELLS).length+' new spells';
 };
 filter.addEventListener('input',render);render();
 panel.append(header,count,grid);host.append(panel);
}
function se280InstallCatalog(){
 const starter=document.getElementById('se248StarterParticles');
 const studio=document.querySelector('#se248Library .se248-library-scroll');
 if(starter)se280MakeCatalog(starter,false);
 if(studio)se280MakeCatalog(studio,true);
 return !!starter&&!!studio;
}
function se280Boot(){
 if(se280InstallCatalog())return;
 const observer=new MutationObserver(()=>{
  if(se280InstallCatalog())observer.disconnect();
 });
 observer.observe(document.body,{subtree:true,childList:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se280Boot,{once:true});
else se280Boot();
// Reuse the same native Particle Studio point-cloud geometry/material/color scheme.
// Transient hand casts are NOT saved in authored scenes or added as editor actors.
function se280Glow(){
 if(se280SpellState.glow)return se280SpellState.glow;
 const c=document.createElement('canvas');c.width=64;c.height=64;
 const context=c.getContext('2d');if(!context)return null;
 const gradient=context.createRadialGradient(32,32,1,32,32,32);
 gradient.addColorStop(0,'rgba(255,255,255,1)');
 gradient.addColorStop(.17,'rgba(255,255,255,.96)');
 gradient.addColorStop(.52,'rgba(255,255,255,.42)');
 gradient.addColorStop(1,'rgba(255,255,255,0)');
 context.fillStyle=gradient;context.fillRect(0,0,64,64);
 se280SpellState.glow=new THREE.CanvasTexture(c);return se280SpellState.glow;
}
function se280Cast(side,record,key){
 if(!record?.controller||!SE223_PRESETS[key])return false;
 const cfg=se223Default(key),style=SE280_SPELLS[key]?.motion||'bolt';
 const origin=record.controller.localToWorld(new THREE.Vector3(0,-.025,-.16));
 const forward=new THREE.Vector3(0,0,-1).transformDirection(record.controller.matrixWorld).normalize();
 const across=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0));
 if(across.lengthSq()<.01)across.set(1,0,0);across.normalize();
 const upper=new THREE.Vector3().crossVectors(across,forward).normalize();
 const cloud=se223PointCloud(cfg);cloud.cloud.name='Mage · '+side+' · '+cfg.name;
 const texture=se280Glow();if(texture){cloud.material.map=texture;cloud.material.needsUpdate=true;}
 const count=style==='storm'?55:style==='ring'||style==='nova'?54:style==='spiral'?44:36;
 const speed=Math.max(1,Math.min(10,cfg.speed||4)),r=()=>Math.random()*2-1;
 const life=Math.max(.55,Math.min(2.4,cfg.life||1.4));
 for(let i=0;i<count;i++){
  const theta=i/count*Math.PI*2;
  const dir=forward.clone();
  let off=new THREE.Vector3();
  if(style==='nova'||style==='bloom'){
   dir.set(r(),r(),r()).normalize();
   if(style==='bloom')dir.y=Math.abs(dir.y)*.8+.2;
  }else if(style==='ring'||style==='spiral'){
   dir.copy(across).multiplyScalar(Math.cos(theta)).addScaledVector(upper,Math.sin(theta));
   if(style==='spiral')dir.addScaledVector(forward,.36).normalize();
  }else if(style==='rain'){
   dir.set(r()*.2,-1,r()*.2).normalize();
   off=across.clone().multiplyScalar(r()*1.2).addScaledVector(upper,r()*.8);
  }else{
   dir.addScaledVector(across,r()*(style==='cone'?.47:style==='storm'?.28:.10));
   dir.addScaledVector(upper,r()*(style==='cone'?.47:style==='storm'?.28:.10)).normalize();
  }
  const p=origin.clone().add(off).addScaledVector(dir,Math.random()*.055);
  const velocity=dir.multiplyScalar(style==='ring'?speed*.65:style==='spiral'?speed*.35:speed*(.72+Math.random()*.36));
  cloud.particles.push({x:p.x,y:p.y,z:p.z,vx:velocity.x,vy:velocity.y,vz:velocity.z,
   age:0,life:life*(.72+Math.random()*.42),seed:Math.random()*Math.PI*2,index:i});
 }
 if(se280SpellState.live.length>=6){
  const first=se280SpellState.live.shift();se223DisposeRecord(first.cloud);
 }
 se280SpellState.live.push({key,style,cloud,origin,forward,across,upper,life});
 se280SpellState.castCount++;
 return true;
}
const se280Color=new THREE.Color();
function se280UpdateCast(fx,dt){
 const cfg=SE223_PRESETS[fx.key],rec=fx.cloud,ps=rec.particles;
 const positions=rec.geometry.getAttribute('position'),colors=rec.geometry.getAttribute('color');
 const resistance=Math.exp(-Math.max(0,cfg.drag)*dt);
 for(let i=ps.length-1;i>=0;i--){
  const p=ps[i];p.age+=dt;
  if(p.age>=p.life){ps[i]=ps[ps.length-1];ps.pop();continue;}
  const phase=p.age/p.life;
  if(fx.style==='storm'){
   p.x+=p.vx*dt;p.y+=p.vy*dt;p.z+=p.vz*dt;
   p.x+=Math.sin(p.seed+phase*32)*.014;p.y+=Math.cos(p.seed+phase*40)*.012;
  }else if(fx.style==='spiral'){
   const angle=p.seed+phase*12+p.index*.21;
   const distance=.16+.28*phase;
   p.x=fx.origin.x+fx.forward.x*phase*1.5+(fx.across.x*Math.cos(angle)+fx.upper.x*Math.sin(angle))*distance;
   p.y=fx.origin.y+fx.forward.y*phase*1.5+(fx.across.y*Math.cos(angle)+fx.upper.y*Math.sin(angle))*distance;
   p.z=fx.origin.z+fx.forward.z*phase*1.5+(fx.across.z*Math.cos(angle)+fx.upper.z*Math.sin(angle))*distance;
  }else{
   p.vy-=cfg.gravity*dt*.45;p.vx*=resistance;p.vy*=resistance;p.vz*=resistance;
   p.x+=p.vx*dt;p.y+=p.vy*dt;p.z+=p.vz*dt;
  }
 }
 for(let i=0;i<ps.length;i++){
  const p=ps[i],t=Math.min(1,p.age/p.life);
  positions.setXYZ(i,p.x,p.y,p.z);
  const brightness=Math.min(1,t*13, (1-t)*(fx.style==='storm'?9:4));
  se280Color.copy(rec.startColor).lerp(rec.endColor,t).multiplyScalar(brightness*1.3);
  colors.setXYZ(i,se280Color.r,se280Color.g,se280Color.b);
 }
 rec.material.size=Math.min(.45,Math.max(.075,cfg.size*(fx.style==='storm'?.65:1.2)));
 rec.geometry.setDrawRange(0,ps.length);
 positions.needsUpdate=true;colors.needsUpdate=true;
 return ps.length>0;
}
function se280PaintSign(label,side){
 const cfg=SE223_PRESETS[se280SpellState[side]];
 const ctx=label.canvas.getContext('2d');if(!ctx)return;
 ctx.clearRect(0,0,384,104);
 ctx.fillStyle='rgba(9,14,29,.78)';ctx.fillRect(0,0,384,104);
 ctx.strokeStyle=cfg?.startColor||'#bd93f9';ctx.lineWidth=6;ctx.strokeRect(3,3,378,98);
 ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.font='bold 31px sans-serif';ctx.fillStyle='#f3efff';
 ctx.fillText((side==='left'?'L · ':'R · ')+(SE280_SPELLS[se280SpellState[side]]?.name||cfg?.label||'Spell'),192,51,357);
 label.texture.needsUpdate=true;
}
function se280MakeSign(side,record){
 const canvas=document.createElement('canvas');canvas.width=384;canvas.height=104;
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const mat=new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false});
 const sprite=new THREE.Sprite(mat);sprite.name='Mage '+side+' spell label';
 sprite.position.set(side==='left'?.02:-.02,.105,-.27);
 sprite.scale.set(.36,.098,1);sprite.renderOrder=10012;record.controller.add(sprite);
 const sign={record,canvas,texture,mat,sprite};se280PaintSign(sign,side);
 return sign;
}
function se280Reset(){
 for(const fx of se280SpellState.live)se223DisposeRecord(fx.cloud);
 se280SpellState.live.length=0;
 for(const sign of se280SpellState.signs.values()){
  sign.sprite.removeFromParent();sign.mat.dispose();sign.texture.dispose();
 }
 se280SpellState.signs.clear();
 se280SpellState.edge.left=se280SpellState.edge.right=false;
 se280SpellState.stick.left=se280SpellState.stick.right=false;
 se280SpellState.lastFrame=0;
}
function se280MageFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting||currentProject?.kind!==se279GameId){
  if(se280SpellState.live.length||se280SpellState.signs.size)se280Reset();
  return;
 }
 const now=performance.now(),dt=se280SpellState.lastFrame?Math.min(.05,(now-se280SpellState.lastFrame)/1000):0;
 se280SpellState.lastFrame=now;
 for(const side of ['left','right']){
  const record=se181XR.controllers.find(r=>r.input?.handedness===side);
  if(!record){se280SpellState.edge[side]=false;se280SpellState.stick[side]=false;
   const sign=se280SpellState.signs.get(side);
   if(sign){sign.sprite.removeFromParent();sign.mat.dispose();sign.texture.dispose();se280SpellState.signs.delete(side);}
   continue;
  }
  const current=se280SpellState.signs.get(side);
  if(!current||current.record!==record){
   if(current){current.sprite.removeFromParent();current.mat.dispose();current.texture.dispose();}
   se280SpellState.signs.set(side,se280MakeSign(side,record));
  }
  const press=Number(record.input?.gamepad?.buttons?.[0]?.value||0)>.72;
  const click=!!record.input?.gamepad?.buttons?.[3]?.pressed;
  if(click&&!se280SpellState.stick[side])se280Cycle(side);
  if(press&&!se280SpellState.edge[side]&&se279Hands.attached.has(side)){
   try{se280Cast(side,record,se280SpellState[side]);}
   catch(e){se280SpellState.lastError=String(e);console.error('Mage cast',e);}
  }
  se280SpellState.edge[side]=press;se280SpellState.stick[side]=click;
 }
 for(let i=se280SpellState.live.length-1;i>=0;i--){
  const fx=se280SpellState.live[i];
  if(!se280UpdateCast(fx,dt)){
   se223DisposeRecord(fx.cloud);se280SpellState.live.splice(i,1);
  }
 }
}
const se280PreviousXRFrame=se279XRFrame;
se279XRFrame=function(){se280PreviousXRFrame();se280MageFrame();};
const se280PreviousCleanup=se279Cleanup;
se279Cleanup=function(){se280Reset();return se280PreviousCleanup();};
window.SWYRL_ENGINE_MAGE_SPELL_LAB=Object.freeze({
 list:()=>se280CatalogEntries().map(({key,name,category})=>({key,name,category})),
 equip:se280Equip,loadPack:se280LoadPack,add:se280AddPreset,
 status:()=>({active:currentProject?.kind===se279GameId,castCount:se280SpellState.castCount,
  left:se280SpellState.left,right:se280SpellState.right,live:se280SpellState.live.length,
  error:se280SpellState.lastError,catalog:se280CatalogEntries().length})
});