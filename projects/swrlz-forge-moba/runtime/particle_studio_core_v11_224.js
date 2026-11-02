// §E v11.224 — project-native reusable particle emitters.
// Particle definitions belong to the engine project; GPU objects never enter actors,
// scene JSON, history, networking, collision, or standalone model topology.
const SE223_SCHEMA='swyrl-particle-studio-v1';
const SE223_MAX_EMITTERS=12,SE223_PER_EMITTER=96,SE223_TOTAL=576;
const SE223_PRESETS=Object.freeze({
 magic:{label:'Arcane motes',mode:'continuous',shape:'sphere',rate:24,life:2.4,speed:1.1,spread:1.0,gravity:-.4,drag:.65,size:.17,radius:.5,direction:[0,1,0],startColor:'#8e75ff',endColor:'#3de5f8',blend:'additive'},
 fire:{label:'Flame',mode:'continuous',shape:'circle',rate:40,life:1.35,speed:2.2,spread:.7,gravity:-.3,drag:.35,size:.22,radius:.33,direction:[0,1,0],startColor:'#ffe07d',endColor:'#ee4629',blend:'additive'},
 smoke:{label:'Smoke',mode:'continuous',shape:'circle',rate:20,life:3.7,speed:.65,spread:.45,gravity:-.14,drag:1.4,size:.34,radius:.42,direction:[0,1,0],startColor:'#b0b9cb',endColor:'#434d67',blend:'normal'},
 sparks:{label:'Sparks',mode:'burst',shape:'point',rate:10,burst:50,life:1.3,speed:4.1,spread:2.6,gravity:5.6,drag:.12,size:.11,radius:.04,direction:[0,1,0],startColor:'#fff4a5',endColor:'#f28530',blend:'additive'},
 snow:{label:'Snowfall',mode:'continuous',shape:'box',rate:44,life:5.2,speed:.75,spread:.18,gravity:.36,drag:1.15,size:.12,radius:3,direction:[0,-1,0],startColor:'#f5ffff',endColor:'#90bcf3',blend:'normal'},
 rain:{label:'Rain',mode:'continuous',shape:'box',rate:70,life:2.1,speed:5.7,spread:.16,gravity:4.2,drag:.05,size:.085,radius:3,direction:[0,-1,0],startColor:'#d8faff',endColor:'#4b85d4',blend:'normal'},
 healing:{label:'Healing wisps',mode:'continuous',shape:'circle',rate:30,life:2.0,speed:1.5,spread:.48,gravity:-.95,drag:.7,size:.18,radius:1,direction:[0,1,0],startColor:'#8effb0',endColor:'#24d8b4',blend:'additive'},
 build:{label:'Building magic',mode:'continuous',shape:'box',rate:26,life:1.4,speed:1.7,spread:1.2,gravity:2.4,drag:.6,size:.13,radius:.8,direction:[0,1,0],startColor:'#fce98e',endColor:'#f7a34d',blend:'additive'},
 portal:{label:'Portal shimmer',mode:'continuous',shape:'circle',rate:48,life:2.8,speed:.42,spread:.35,gravity:-.2,drag:.3,size:.15,radius:1.4,direction:[0,1,0],startColor:'#df99ff',endColor:'#519dff',blend:'additive'},
 celebration:{label:'Confetti burst',mode:'burst',shape:'sphere',rate:8,burst:75,life:2.8,speed:4.0,spread:1.7,gravity:3.0,drag:.15,size:.15,radius:.25,direction:[0,1,0],startColor:'#ffadf5',endColor:'#65ffce',blend:'normal'}
});
const SE223_NUMERIC=Object.freeze({
 rate:[0,80],burst:[1,96],life:[.1,8],speed:[0,12],spread:[0,4],
 gravity:[-12,16],drag:[0,5],size:[.025,.8],radius:[0,6]
});
const se223State={project:null,scene:null,live:new Map(),selected:null,
 preview:false,panel:false,playingLast:false,ui:null,toolbar:null};
const se223Empty=Object.freeze({schema:SE223_SCHEMA,emitters:[]});
const se223Clean=(v,max=64)=>String(v||'').trim().slice(0,max);
const se223Hex=v=>typeof v==='string'&&/^#[0-9a-fA-F]{6}$/.test(v);
function se223Default(key='magic'){
 const name=SE223_PRESETS[key]?key:'magic',p=SE223_PRESETS[name];
 return {id:uid(),name:p.label,preset:name,enabled:true,
  mode:p.mode,shape:p.shape,rate:p.rate,burst:p.burst||48,
  life:p.life,speed:p.speed,spread:p.spread,gravity:p.gravity,drag:p.drag,
  size:p.size,radius:p.radius,direction:[...p.direction],position:[0,1.7,0],
  startColor:p.startColor,endColor:p.endColor,blend:p.blend,attachActorId:null};
}
function se223ValidateEmitter(value){
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Emitter data must be an object.');
 const p=se223Default(value.preset);
 const v={...p,...value};
 if(typeof v.id!=='string'||!/^[a-zA-Z0-9_-]{2,70}$/.test(v.id))throw Error('Invalid emitter ID.');
 if(typeof v.name!=='string'||!se223Clean(v.name)||v.name.length>64)throw Error('Name must be 1–64 characters.');
 if(typeof v.enabled!=='boolean')throw Error('Invalid enabled state.');
 if(!['continuous','burst'].includes(v.mode))throw Error('Invalid emission mode.');
 if(!['point','sphere','circle','box'].includes(v.shape))throw Error('Invalid emission shape.');
 if(!['additive','normal'].includes(v.blend))throw Error('Invalid blending mode.');
 if(!se223Hex(v.startColor)||!se223Hex(v.endColor))throw Error('Choose valid hex colors.');
 if(v.attachActorId!==null&&(typeof v.attachActorId!=='string'||!/^[a-zA-Z0-9_-]{1,90}$/.test(v.attachActorId)))throw Error('Invalid attachment.');
 for(const [k,[lo,hi]] of Object.entries(SE223_NUMERIC)){
  if(typeof v[k]!=='number'||!Number.isFinite(v[k])||v[k]<lo||v[k]>hi)
   throw Error('Invalid '+k+' ('+lo+'–'+hi+').');
 }
 for(const key of ['position','direction']){
  if(!Array.isArray(v[key])||v[key].length!==3||!v[key].every(n=>
   typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=(key==='position'?250:3)))
   throw Error('Invalid '+key+' 3D vector.');
 }
 return {id:v.id,name:v.name,preset:SE223_PRESETS[v.preset]?v.preset:'custom',
  enabled:v.enabled,mode:v.mode,shape:v.shape,
  rate:v.rate,burst:Math.round(v.burst),life:v.life,speed:v.speed,
  spread:v.spread,gravity:v.gravity,drag:v.drag,size:v.size,radius:v.radius,
  position:[...v.position],direction:[...v.direction],
  startColor:v.startColor.toLowerCase(),endColor:v.endColor.toLowerCase(),
  blend:v.blend,attachActorId:v.attachActorId};
}
function se223ValidateModel(v){
 if(!v||v.schema!==SE223_SCHEMA||!Array.isArray(v.emitters)||v.emitters.length>SE223_MAX_EMITTERS)
  throw Error('Expected a Particle Studio v1 file with up to 12 emitters.');
 const emitters=v.emitters.map(se223ValidateEmitter);
 if(new Set(emitters.map(x=>x.id)).size!==emitters.length)throw Error('Duplicate emitter IDs.');
 return {schema:SE223_SCHEMA,emitters};
}
const se223VerifiedModels=new WeakSet();
function se223Data(create=false){
 if(!currentProject||typeof currentProject!=='object')return null;
 if(!currentProject.particleStudio){
  if(!create)return se223Empty;
  currentProject.particleStudio={schema:SE223_SCHEMA,emitters:[]};
 }
 const data=currentProject.particleStudio;
 if(!data||typeof data!=='object')return null;
 if(!se223VerifiedModels.has(data)){
  // Validate once per project metadata object. External saved levels and
  // imported project JSON bypass the Studio-specific Import dialog.
  try{se223ValidateModel(data);se223VerifiedModels.add(data);}
  catch(error){return null;}
 }
 return data;
}
function se223List(){
 const data=se223Data();return data?data.emitters.map(e=>structuredClone(e)):[];
}
function se223Get(id){return se223Data()?.emitters.find(e=>e.id===id)||null;}
function se223DisposeRecord(rec){
 if(!rec)return;
 rec.cloud?.removeFromParent();
 rec.geometry?.dispose();rec.material?.dispose();rec.particles.length=0;
}
function se223Drop(id){
 const rec=se223State.live.get(id);
 if(rec){se223DisposeRecord(rec);se223State.live.delete(id);}
}
function se223Reset(){
 for(const x of se223State.live.values())se223DisposeRecord(x);
 se223State.live.clear();se223State.playingLast=false;
 se223State.project=currentProject||null;se223State.scene=scene||null;
}
function se223PointCloud(config){
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(SE223_PER_EMITTER*3),3));
 g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(SE223_PER_EMITTER*3),3));
 g.setDrawRange(0,0);
 const material=new THREE.PointsMaterial({size:config.size,vertexColors:true,transparent:true,
  depthWrite:false,blending:config.blend==='additive'?THREE.AdditiveBlending:THREE.NormalBlending,
  sizeAttenuation:true,opacity:.95});
 const cloud=new THREE.Points(g,material);
 cloud.name='Particle Studio · '+config.name;
 cloud.userData.se223EditorEffect=true;
 cloud.frustumCulled=false;
 scene.add(cloud);
 return {cloud,geometry:g,material,particles:[],carry:0,burstFired:false,
  startColor:new THREE.Color(config.startColor),endColor:new THREE.Color(config.endColor)};
}
function se223Runtime(config){
 let r=se223State.live.get(config.id);
 if(!r){r=se223PointCloud(config);se223State.live.set(config.id,r);}
 if(r.cloud.parent!==scene)scene.add(r.cloud);
 r.cloud.name='Particle Studio · '+config.name;
 r.material.size=config.size;
 r.material.blending=config.blend==='additive'?THREE.AdditiveBlending:THREE.NormalBlending;
 r.startColor.set(config.startColor);r.endColor.set(config.endColor);
 return r;
}
function se223Origin(cfg){
 if(cfg.attachActorId){
  const a=actors.find(a=>a.userData?.id===cfg.attachActorId);
  if(a?.parent){a.updateWorldMatrix(true,false);
   return a.localToWorld(new THREE.Vector3(...cfg.position));}
 }
 return new THREE.Vector3(...cfg.position);
}
function se223Spawn(cfg,n){
 if(!cfg.enabled)return 0;
 const r=se223Runtime(cfg),max=SE223_PER_EMITTER-r.particles.length;
 let global=0;for(const x of se223State.live.values())global+=x.particles.length;
 const count=Math.min(max,SE223_TOTAL-global,Math.max(0,Math.round(n)));
 if(count<=0)return 0;
 const origin=se223Origin(cfg);
 for(let i=0;i<count;i++){
  const u=Math.random()*2-1,v=Math.random()*2-1,a=Math.random()*Math.PI*2;
  const d=cfg.radius*Math.sqrt(Math.random());
  let offset;
  if(cfg.shape==='sphere'){const z=Math.random()*2-1,r=Math.sqrt(1-z*z);
   offset=[r*Math.cos(a)*d,z*d,r*Math.sin(a)*d];}
  else if(cfg.shape==='circle')offset=[Math.cos(a)*d,0,Math.sin(a)*d];
  else if(cfg.shape==='box')offset=[u*cfg.radius,(Math.random()*2-1)*cfg.radius,v*cfg.radius];
  else offset=[0,0,0];
  const heading=new THREE.Vector3(
   cfg.direction[0]+u*cfg.spread,
   cfg.direction[1]+(Math.random()*2-1)*cfg.spread,
   cfg.direction[2]+v*cfg.spread);
  if(heading.lengthSq()<.001)heading.set(0,1,0);
  heading.normalize().multiplyScalar(cfg.speed*(.65+Math.random()*.7));
  r.particles.push({x:origin.x+offset[0],y:origin.y+offset[1],
   z:origin.z+offset[2],vx:heading.x,vy:heading.y,vz:heading.z,
   age:0,life:cfg.life*(.75+Math.random()*.5)});
 }
 return count;
}
function se223Step(cfg,dt){
 const r=se223Runtime(cfg),ps=r.particles;
 const positions=r.geometry.getAttribute('position'),colors=r.geometry.getAttribute('color');
 const k=Math.exp(-cfg.drag*dt),color=new THREE.Color();
 for(let i=ps.length-1;i>=0;i--){
  const p=ps[i];p.age+=dt;
  if(p.age>=p.life){ps[i]=ps[ps.length-1];ps.pop();continue;}
  p.vy-=cfg.gravity*dt;p.vx*=k;p.vy*=k;p.vz*=k;
  p.x+=p.vx*dt;p.y+=p.vy*dt;p.z+=p.vz*dt;
 }
 for(let i=0;i<ps.length;i++){
  const p=ps[i],phase=Math.min(1,p.age/p.life),fade=1-phase;
  positions.setXYZ(i,p.x,p.y,p.z);
  color.copy(r.startColor).lerp(r.endColor,phase).multiplyScalar(fade);
  colors.setXYZ(i,color.r,color.g,color.b);
 }
 r.geometry.setDrawRange(0,ps.length);
 positions.needsUpdate=true;colors.needsUpdate=true;
}
function se223Frame(dt,t){
 if(!scene||!currentProject||!renderer)return;
 const data=se223Data();
 if(currentProject!==se223State.project||scene!==se223State.scene ||
  [...se223State.live.values()].some(r=>r.cloud.parent!==scene)){
  se223Reset();
  if(typeof se223UIRefresh==='function'&&se223State.panel)se223UIRefresh();
 }
 const active=!paused&&(!!playing||!!simulating||se223State.preview);
 if(!data||!data.emitters.length){if(se223State.live.size)se223Reset();return;}
 if(document.visibilityState==='hidden')return;
 if(!active){
  if(se223State.playingLast){
   for(const r of se223State.live.values()){r.particles.length=0;r.geometry.setDrawRange(0,0);}
   se223State.playingLast=false;
  }
  for(const r of se223State.live.values())r.cloud.visible=false;
  return;
 }
 const delta=Math.max(0,Math.min(Number(dt)||0,.05));
 if(!se223State.playingLast){
  for(const r of se223State.live.values()){r.particles.length=0;r.carry=0;r.burstFired=false;}
 }
 se223State.playingLast=true;
 const ids=new Set(data.emitters.map(x=>x.id));
 for(const id of [...se223State.live.keys()])if(!ids.has(id))se223Drop(id);
 for(const cfg of data.emitters){
  const r=se223Runtime(cfg);r.cloud.visible=cfg.enabled;
  if(!cfg.enabled){r.particles.length=0;r.geometry.setDrawRange(0,0);continue;}
  if(cfg.mode==='burst'){if(!r.burstFired){se223Spawn(cfg,cfg.burst);r.burstFired=true;}}
  else{r.carry+=delta*cfg.rate;const amount=Math.min(24,Math.floor(r.carry));
   r.carry-=amount;if(amount)se223Spawn(cfg,amount);}
  se223Step(cfg,delta);
 }
}
function se223Mutate(label,fn,allowRepair=false){
 if(playing||simulating){toast('Stop Play to edit particle definitions.');return false;}
 const previous=se223Data();
 if(!previous&&!allowRepair){toast('Invalid particle source. Use Import to repair.');return false;}
 try{
  // Build a fully validated draft BEFORE touching history or the live project.
  // Rejected edits never leave a half-mutated emitter or an orphan transaction.
  const draft=structuredClone(previous||se223Empty),result=fn(draft);
  const validated=se223ValidateModel(draft);
  beginTransaction(label);
  currentProject.particleStudio=validated;
  commitTransaction(label);
  if(typeof se223UIRefresh==='function')se223UIRefresh();
  return result;
 }catch(error){
  toast('Particle edit rejected: '+String(error?.message||error).slice(0,120));
  return false;
 }
}
function se223Create(key='magic'){
 if(!SE223_PRESETS[key])key='magic';
 const added=se223Mutate('Create '+SE223_PRESETS[key].label+' emitter',model=>{
  if(model.emitters.length>=SE223_MAX_EMITTERS)throw Error('12 emitters maximum.');
  const e=se223Default(key);
  model.emitters.push(e);se223State.selected=e.id;return structuredClone(e);
 });
 if(added){se223State.preview=true;se223Drop(added.id);}
 return added;
}
function se223Update(id,changes){
 if(!se223Get(id))return false;
 return se223Mutate('Edit particle emitter',model=>{
  const i=model.emitters.findIndex(x=>x.id===id),original=model.emitters[i];
  const candidate=se223ValidateEmitter({...original,...changes,id:original.id});
  model.emitters[i]=candidate;se223Drop(id);return structuredClone(candidate);
 });
}
function se223Remove(id){
 if(!se223Get(id))return false;
 return se223Mutate('Delete particle emitter',model=>{
  model.emitters=model.emitters.filter(e=>e.id!==id);
  se223Drop(id);if(se223State.selected===id)se223State.selected=model.emitters[0]?.id||null;
  return true;
 });
}
function se223Duplicate(id){
 const source=se223Get(id);if(!source)return false;
 return se223Mutate('Duplicate particle emitter',model=>{
  if(model.emitters.length>=SE223_MAX_EMITTERS)throw Error('12 emitters maximum.');
  const copy=se223ValidateEmitter({...structuredClone(source),id:uid(),
   name:(source.name+' copy').slice(0,64),position:[source.position[0]+.5,...source.position.slice(1)]});
  model.emitters.push(copy);se223State.selected=copy.id;return structuredClone(copy);
 });
}
function se223Replace(model){
 let validated;
 try{validated=se223ValidateModel(model);}catch(error){toast('Particle import rejected: '+error.message);return false;}
 const result=se223Mutate('Import Particle Studio library',draft=>{
  draft.emitters=validated.emitters;return true;
 },true);
 if(result){
  se223Reset();se223State.selected=validated.emitters[0]?.id||null;
  if(typeof se223UIRefresh==='function')se223UIRefresh();
 }
 return result;
}
function se223Trigger(id,count=null){
 const cfg=se223Get(id);if(!cfg||!cfg.enabled)return 0;
 se223State.playingLast=true;
 const n=se223Spawn(cfg,count==null?cfg.burst:Math.min(96,Math.max(1,Number(count)||1)));
 const rec=se223State.live.get(id);if(rec&&cfg.mode==='burst')rec.burstFired=true;
 return n;
}
window.SWYRL_ENGINE_PARTICLES=Object.freeze({
 schema:SE223_SCHEMA,presets:()=>Object.keys(SE223_PRESETS),
 list:se223List,create:se223Create,update:se223Update,
 duplicate:se223Duplicate,remove:se223Remove,trigger:se223Trigger,
 import:se223Replace,inspect:()=>({project:currentProject?.name||'',
  preview:se223State.preview,emitters:se223List().length,
  particles:[...se223State.live.values()].reduce((n,x)=>n+x.particles.length,0),
  cap:SE223_TOTAL,perEmitter:SE223_PER_EMITTER})
});
