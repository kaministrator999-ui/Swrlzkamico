// §E v11.194 — Emberfall: Shattered Vale. Original top-down ARPG starter.
// Authored native editor actors; combat/loot/AI are temporary Play session state.
// No external art or audio and no second renderer, scene engine or frame loop.
const ef194={
 id:'emberfall-arpg',kind:'emberfall-arpg',session:null,hud:null,installed:false,
 down:new Set(),lastHud:0,lastError:'',lastAction:'',ray:new THREE.Raycaster(),
 plane:new THREE.Plane(new THREE.Vector3(0,1,0),0)
};
const EF194_COLORS={common:0xc8d4df,magic:0x62bbff,rare:0xf9c96d};
const EF194_ITEMS=[
 {name:'Iron Fang',attack:3},{name:'Sootbound Axe',attack:5},
 {name:'Runescar Blade',attack:7},{name:'Wanderer Boots',armor:2},
 {name:'Ashguard Vest',armor:3},{name:'Stormglass Charm',attack:4}
];
function ef194Actor(role){return actors.find(a=>a.userData?.role===role)||null;}
function ef194MakeStarter(){
 clearAll();
 applyProjectMeta({name:'Emberfall · Shattered Vale',template:ef194.id,
  kind:ef194.kind,environment:'starter',arpg:{schema:'emberfall-arpg-v1',zone:'Shattered Vale',seed:194}});
 setProjectBackground('#111b24');
 rebuildTerrain();makeGroundActor();buildSceneryExtras();
 const hero=makeHero('blue',[0,0,10],true,'Wayfarer · Player');
 hero.userData.role='emberfall-player';hero.userData.folder='Emberfall/Player';
 hero.userData.tags=['emberfall','player'];
 const exit=makePortal([0,0,16],'#65b9ff',true,'Wayfarer Camp Portal');
 exit.userData.folder='Emberfall/Camp';
 for(const cfg of [[-5,12],[-2,17],[3,17],[6,11]]){
  const a=makeCrystal([cfg[0],0,cfg[1]],'#ec965c',true,'Camp Emberlight',.5);
  a.userData.folder='Emberfall/Camp';
 }
 for(let i=0;i<16;i++){
  const a=i/16*Math.PI*2,x=Math.cos(a)*23.5,z=Math.sin(a)*22;
  const rock=makeRock([x,0,z],[1.35+(i%3)*.23,1.3+(i%4)*.12,1.4],true,'Shattered Vale Cliff '+(i+1));
  rock.userData.folder='Emberfall/Cliffs';
 }
 for(const p of [[-9,8],[-13,2],[11,6],[12,-7],[-8,-13],[6,-15]]){
  const tree=makeTree([p[0],0,p[1]],[.9,1.15,.9],true,'Blightwood');
  tree.userData.folder='Emberfall/Blightwoods';
 }
 for(const cfg of [[-9,-5],[8,-4],[-13,-11],[12,-13]]){
  const c=makeCrystal([cfg[0],0,cfg[1]],'#b44aff',true,'Corrupted Ember',.8);
  c.userData.folder='Emberfall/Corruption';
 }
 for(const p of [[-5,-9],[1,-10],[6,-9]]){
  const a=makeWall([p[0],0,p[1]],[1.4,1.8,.5],true,'Fallen Shrine Pillar');
  a.userData.folder='Emberfall/Ruins';
 }
 const spawn=[
  [-7,5,'Cinder Thrall'],[6,6,'Cinder Thrall'],[-11,1,'Ash Ravager'],
  [9,0,'Cinder Thrall'],[-5,-1,'Ash Ravager'],[4,-2,'Cinder Thrall'],
  [-12,-7,'Cinder Thrall'],[12,-7,'Ash Ravager'],[-3,-12,'Cinder Thrall'],
  [8,-13,'Ash Ravager'],[0,-17,'Cinder Thrall'],[1,-7,'The Cinder Warden']
 ];
 spawn.forEach(([x,z,name],i)=>{
  const a=makeHero('red',[x,0,z],true,name+' '+(i+1));
  a.userData.role=name==='The Cinder Warden'?'emberfall-boss':'emberfall-enemy';
  a.userData.folder='Emberfall/Enemies';
  a.userData.tags=['emberfall',name==='The Cinder Warden'?'boss':'monster'];
  const scale=name==='The Cinder Warden'?1.8:name==='Ash Ravager'?1.3:.92;
  a.scale.setScalar(scale);
 });
 finishTemplate('hero');
 ef194FrameMap(true);
 initializeHistory('Created Emberfall original ARPG starter');
 markSaved();
 document.getElementById('projectHub')?.classList.remove('show');
 ef194Status('Emberfall created · Edit the map or press Play.');
 return true;
}
function ef194Status(message){ef194.lastAction=String(message||'');if(typeof toast==='function')toast(ef194.lastAction);}
function ef194FrameMap(overview=false){
 setCameraView('perspective');
 const point=overview?new THREE.Vector3(0,0,0):ef194Actor('emberfall-player')?.position||new THREE.Vector3();
 perspectiveCamera.position.set(point.x+20,overview?34:26,point.z+25);
 perspectiveCamera.lookAt(point.x,0,point.z);
 perspectiveCamera.updateProjectionMatrix();
 orbit.target.set(point.x,0,point.z);orbit.enabled=true;orbit.update();
}
function ef194CombatObject(color,scale=.16){
 const mesh=new THREE.Mesh(new THREE.IcosahedronGeometry(scale,1),
  new THREE.MeshBasicMaterial({color,transparent:true,opacity:.92,depthWrite:false}));
 mesh.userData.ef194Runtime=true;return mesh;
}
function ef194Vfx(point,color,size=.25,life=.4){
 const s=ef194.session;if(!s)return;
 const visual=ef194CombatObject(color,size);
 visual.position.copy(point);visual.position.y+=.75;
 s.group.add(visual);
 s.vfx.push({mesh:visual,ttl:life,full:life});
}
function ef194Dispose(obj){
 if(!obj)return;
 obj.removeFromParent();
 obj.traverse(n=>{
  n.geometry?.dispose?.();
  for(const m of Array.isArray(n.material)?n.material:n.material?[n.material]:[])m.dispose?.();
 });
}
function ef194HeroPosition(s){return s.hero.getWorldPosition(new THREE.Vector3());}
function ef194Start(){
 if(ef194.session)return true;
 const hero=ef194Actor('emberfall-player');
 const foes=actors.filter(a=>['emberfall-enemy','emberfall-boss'].includes(a.userData.role));
 if(!hero||foes.length<2){ef194Status('Emberfall needs its Player and Enemy actors.');return false;}
 const group=new THREE.Group();group.name='Emberfall · transient Play visuals';scene.add(group);
 const pet=ef194CombatObject(0x75e4fa,.30);pet.name='Wayfarer Lantern · companion';
 group.add(pet);
 const monsters=foes.map((a,i)=>({actor:a,id:a.userData.id,
  boss:a.userData.role==='emberfall-boss',hp:a.userData.role==='emberfall-boss'?220:38+(i%4)*12,
  maxHp:a.userData.role==='emberfall-boss'?220:38+(i%4)*12,
  attackAt:0,spawn:a.position.clone(),alive:true,aggro:false,
  speed:a.userData.role==='emberfall-boss'?2.1:2.5+i%3*.24}));
 ef194.session={
  hero,monsters,group,pet,vfx:[],loot:[],inventory:[],hp:115,maxHp:115,
  mana:65,maxMana:65,potions:3,level:1,xp:0,xpNeeded:50,
  skillPoints:0,skills:{slash:1,bolt:1,nova:1},attackBonus:0,armor:0,
  gold:0,kills:0,quest:'Defeat the Cinder Warden',complete:false,dead:false,
  target:null,attackTarget:null,cooldowns:{slash:0,bolt:0,nova:0,pet:0},
  look:new THREE.Vector3(0,0,-1),cameraDistance:1.0,lastDamage:0,time:0
 };
 ef194.down.clear();
 orbit.enabled=false;document.exitPointerLock?.();
 ef194ShowHud(true);ef194MoveCamera(true);ef194RefreshHud(true);
 ef194Status('Shattered Vale · Hunt the Cinder Warden · click to move.');
 return true;
}
function ef194Damage(enemy,amount,color=0xffa36c){
 const s=ef194.session;
 if(!s||!enemy?.alive||s.dead)return false;
 enemy.hp=Math.max(0,enemy.hp-amount);
 ef194Vfx(enemy.actor.position,color,enemy.boss?.38:.22,.35);
 if(enemy.hp>0)return true;
 enemy.alive=false;enemy.actor.visible=false;s.kills++;
 const xp=enemy.boss?125:16+(s.level*2);
 s.xp+=xp;s.gold+=enemy.boss?75:7+Math.floor(Math.random()*9);
 const chance=enemy.boss?1:.68;
 if(Math.random()<chance)ef194SpawnLoot(enemy.actor.position,enemy.boss);
 while(s.xp>=s.xpNeeded){
  s.xp-=s.xpNeeded;s.level++;s.skillPoints++;
  s.maxHp+=14;s.maxMana+=8;s.hp=Math.min(s.maxHp,s.hp+25);
  s.mana=s.maxMana;s.xpNeeded=Math.round(s.xpNeeded*1.35);
  ef194Vfx(s.hero.position,0x90e6ff,.46,.7);
 }
 if(enemy.boss){
  s.complete=true;s.quest='WARDEN DEFEATED · Starter complete!';
  ef194Status('Victory! The Vale is reclaimed. Explore, collect loot, or stop.');
 }
 ef194RefreshHud(true);return true;
}
function ef194SpawnLoot(pos,guaranteedRare){
 const s=ef194.session;if(!s)return;
 const def=EF194_ITEMS[Math.floor(Math.random()*EF194_ITEMS.length)];
 const rare=guaranteedRare||Math.random()<.14;
 const magic=!rare&&Math.random()<.45;
 const rarity=rare?'rare':magic?'magic':'common';
 const bonus=rare?5:magic?2:0;
 const item={name:(rare?'Wardenforged ':magic?'Glowing ':'')+def.name,
  rarity,attack:(def.attack||0)+bonus,armor:(def.armor||0)+bonus,
  id:'loot-'+s.time+'-'+Math.random().toString(36).slice(2,7)};
 const orb=ef194CombatObject(EF194_COLORS[rarity],.22);
 orb.position.copy(pos);orb.position.y+=.6;s.group.add(orb);
 s.loot.push({item,mesh:orb,phase:Math.random()*6.3});
}
function ef194Pickup(){
 const s=ef194.session;if(!s)return;
 const pos=ef194HeroPosition(s);
 for(let i=s.loot.length-1;i>=0;i--){
  const drop=s.loot[i];
  if(pos.distanceTo(drop.mesh.position)>1.9)continue;
  s.inventory.push(drop.item);
  if(drop.item.attack>s.attackBonus)s.attackBonus=drop.item.attack;
  if(drop.item.armor>s.armor)s.armor=drop.item.armor;
  ef194Status('Found '+drop.item.name+' · '+drop.item.rarity);
  ef194Dispose(drop.mesh);s.loot.splice(i,1);
 }
}
function ef194Nearest(radius=5){
 const s=ef194.session;if(!s)return null;
 const pos=ef194HeroPosition(s);
 let best=null,d=radius;
 for(const e of s.monsters){
  if(!e.alive)continue;
  const dist=Math.hypot(pos.x-e.actor.position.x,pos.z-e.actor.position.z);
  if(dist<d){d=dist;best=e;}
 }
 return best;
}
function ef194Cast(which,enemy){
 const s=ef194.session;if(!s||s.dead||paused)return false;
 if(s.cooldowns[which]>0)return false;
 const pos=ef194HeroPosition(s);
 if(which==='slash'){
  const victim=enemy?.alive?enemy:ef194Nearest(2.65);
  if(!victim||pos.distanceTo(victim.actor.position)>2.8)return false;
  s.cooldowns.slash=.38;
  s.look.copy(victim.actor.position).sub(pos).setY(0).normalize();
  s.hero.rotation.y=Math.atan2(s.look.x,s.look.z);
  ef194Damage(victim,13+s.skills.slash*5+s.attackBonus,0xffc16a);
  ef194Vfx(pos,0xffbf6b,.44,.22);
 }else if(which==='bolt'){
  if(s.mana<12)return false;
  const victim=enemy?.alive?enemy:ef194Nearest(11);
  if(!victim||pos.distanceTo(victim.actor.position)>11.5)return false;
  s.mana-=12;s.cooldowns.bolt=1.1;
  s.look.copy(victim.actor.position).sub(pos).setY(0).normalize();
  s.hero.rotation.y=Math.atan2(s.look.x,s.look.z);
  ef194Damage(victim,17+s.skills.bolt*7+s.attackBonus*.3,0x60ddff);
  ef194Vfx(victim.actor.position,0x56dcff,.47,.3);
 }else if(which==='nova'){
  if(s.mana<26)return false;
  s.mana-=26;s.cooldowns.nova=4.0;
  let hits=0;
  for(const foe of s.monsters){
   if(foe.alive&&pos.distanceTo(foe.actor.position)<5.4){
    ef194Damage(foe,14+s.skills.nova*8,0xc38cff);hits++;
   }
  }
  ef194Vfx(pos,0xb989ff,1.2,.5);
  if(!hits)ef194Status('The arcane pulse missed.');
 }else return false;
 ef194RefreshHud(true);return true;
}
function ef194Potion(){
 const s=ef194.session;if(!s||s.dead||paused||!s.potions||s.hp>=s.maxHp)return false;
 s.potions--;s.hp=Math.min(s.maxHp,s.hp+55+s.level*4);
 ef194Vfx(s.hero.position,0x80f9b7,.55,.6);ef194RefreshHud(true);return true;
}
function ef194SkillUp(id){
 const s=ef194.session;
 if(!s||!s.skillPoints||!['slash','bolt','nova'].includes(id))return false;
 s.skills[id]++;s.skillPoints--;ef194RefreshHud(true);return true;
}
function ef194MoveCamera(immediate=false){
 const s=ef194.session;if(!s)return;
 const p=ef194HeroPosition(s),d=23*s.cameraDistance;
 const desired=new THREE.Vector3(p.x+d*.77,19*s.cameraDistance,p.z+d);
 if(immediate)perspectiveCamera.position.copy(desired);
 else perspectiveCamera.position.lerp(desired,.12);
 perspectiveCamera.fov=48;
 perspectiveCamera.lookAt(p.x,0.5,p.z);perspectiveCamera.updateProjectionMatrix();
 perspectiveCamera.updateMatrixWorld(true);
}
function ef194PointerPoint(event){
 const rect=renderer.domElement.getBoundingClientRect();
 if(!rect.width||!rect.height)return null;
 ef194.ray.setFromCamera(new THREE.Vector2(
  (event.clientX-rect.left)/rect.width*2-1,
  -(event.clientY-rect.top)/rect.height*2+1),perspectiveCamera);
 return ef194.ray.ray.intersectPlane(ef194.plane,new THREE.Vector3());
}
function ef194SelectPoint(p,button=0){
 const s=ef194.session;if(!s||s.dead||!p)return false;
 let target=null,dist=1.45;
 for(const e of s.monsters){
  if(!e.alive)continue;
  const d=Math.hypot(e.actor.position.x-p.x,e.actor.position.z-p.z);
  if(d<dist){target=e;dist=d;}
 }
 if(target){
  s.attackTarget=target;s.target=target.actor.position.clone();
  if(button===2)ef194Cast('bolt',target);
 }else{s.attackTarget=null;s.target=new THREE.Vector3(
  THREE.MathUtils.clamp(p.x,-21.5,21.5),0,
  THREE.MathUtils.clamp(p.z,-20.5,20.5));}
 return true;
}
function ef194Update(dt){
 const s=ef194.session;if(!s||paused)return;
 dt=Math.max(0,Math.min(.05,Number(dt)||0));s.time+=dt;
 for(const key of Object.keys(s.cooldowns))s.cooldowns[key]=Math.max(0,s.cooldowns[key]-dt);
 if(!s.dead){
  const pos=s.hero.position;
  let dx=(ef194.down.has('d')||ef194.down.has('arrowright')?1:0)-
   (ef194.down.has('a')||ef194.down.has('arrowleft')?1:0);
  let dz=(ef194.down.has('s')||ef194.down.has('arrowdown')?1:0)-
   (ef194.down.has('w')||ef194.down.has('arrowup')?1:0);
  if(!dx&&!dz&&s.target){
   dx=s.target.x-pos.x;dz=s.target.z-pos.z;
   if(Math.hypot(dx,dz)<.26){s.target=null;dx=0;dz=0;}
  }
  const mag=Math.hypot(dx,dz);
  if(mag>.001){
   dx/=mag;dz/=mag;
   const step=Math.min(7*dt,mag);
   pos.x=THREE.MathUtils.clamp(pos.x+dx*step,-21.5,21.5);
   pos.z=THREE.MathUtils.clamp(pos.z+dz*step,-20.5,20.5);
   pos.y=terrainHeight(pos.x,pos.z);
   s.look.set(dx,0,dz);s.hero.rotation.y=Math.atan2(dx,dz);
  }
  if(s.attackTarget?.alive){
   const e=s.attackTarget;
   const distance=Math.hypot(pos.x-e.actor.position.x,pos.z-e.actor.position.z);
   if(distance<2.65){s.target=null;ef194Cast('slash',e);}
  }else s.attackTarget=null;
  s.mana=Math.min(s.maxMana,s.mana+dt*2.8);
 }
 for(const e of s.monsters){
  if(!e.alive)continue;
  const pos=e.actor.position,h=s.hero.position;
  const dist=Math.hypot(h.x-pos.x,h.z-pos.z);
  if(!s.dead&&dist<(e.boss?12:9.5)){
   e.aggro=true;
   if(dist>(e.boss?2.0:1.4)){
    const vx=(h.x-pos.x)/Math.max(dist,.01),vz=(h.z-pos.z)/Math.max(dist,.01);
    pos.x+=vx*dt*e.speed;pos.z+=vz*dt*e.speed;
    pos.y=terrainHeight(pos.x,pos.z);
    e.actor.rotation.y=Math.atan2(vx,vz);
   }else if(s.time>=e.attackAt){
    e.attackAt=s.time+(e.boss?1.6:1.35);
    s.hp=Math.max(0,s.hp-Math.max(2,(e.boss?17:9)-s.armor));
    s.lastDamage=s.time;ef194Vfx(h,0xff6476,.23,.25);
    if(s.hp<=0){s.dead=true;s.quest='FALLEN · Stop and Play to retry';ef194Status('You fell in the Shattered Vale. Stop and Play to retry.');}
   }
  }
 }
 s.pet.position.copy(s.hero.position).add(new THREE.Vector3(
  Math.cos(s.time*2)*1.1,1.2+Math.sin(s.time*3)*.23,Math.sin(s.time*2)*1.1));
 if(!s.dead&&s.cooldowns.pet<=0){
  const near=ef194Nearest(5);
  if(near){ef194Damage(near,4+s.level*.6,0x80f4e4);s.cooldowns.pet=1.8;}
 }
 for(let i=s.vfx.length-1;i>=0;i--){
  const p=s.vfx[i];p.ttl-=dt;p.mesh.scale.setScalar(Math.max(.03,p.ttl/p.full));
  if(p.ttl<=0){ef194Dispose(p.mesh);s.vfx.splice(i,1);}
 }
 for(const drop of s.loot){drop.phase+=dt*2.5;drop.mesh.rotation.y+=dt*1.7;
  drop.mesh.position.y=terrainHeight(drop.mesh.position.x,drop.mesh.position.z)+.65+Math.sin(drop.phase)*.1;}
 ef194Pickup();ef194MoveCamera();
 if(s.time-ef194.lastHud>0.15){ef194.lastHud=s.time;ef194RefreshHud();}
}
function ef194RefreshHud(force=false){
 const s=ef194.session;if(!s||!ef194.hud)return;
 const by=id=>ef194.hud.querySelector('#'+id);
 const txt=(id,v)=>{const n=by(id);if(n&&n.textContent!==String(v))n.textContent=String(v);};
 const hp=by('ef194HpBar'),mp=by('ef194ManaBar'),xp=by('ef194XpBar');
 if(hp)hp.style.width=(s.hp/s.maxHp*100).toFixed(1)+'%';
 if(mp)mp.style.width=(s.mana/s.maxMana*100).toFixed(1)+'%';
 if(xp)xp.style.width=(s.xp/s.xpNeeded*100).toFixed(1)+'%';
 txt('ef194Hp',Math.ceil(s.hp)+'/'+s.maxHp);
 txt('ef194Mana',Math.ceil(s.mana)+'/'+s.maxMana);
 txt('ef194Stats','LEVEL '+s.level+'  ·  '+s.kills+' KILLS  ·  '+s.gold+' GOLD');
 txt('ef194Quest',s.quest);
 txt('ef194Potions','POTION ×'+s.potions);
 txt('ef194Gear','Gear  +'+Math.round(s.attackBonus)+' attack · '+Math.round(s.armor)+' armor');
 txt('ef194Loot',s.inventory.slice(-3).map(i=>i.name).join(' · ')||'No spoils collected');
 txt('ef194SkillPts',s.skillPoints?'UPGRADE POINTS: '+s.skillPoints:'Skills earn upgrades on level-up');
 for(const key of ['slash','bolt','nova']){
  const b=by('ef194'+key[0].toUpperCase()+key.slice(1));
  if(b){b.disabled=s.dead||paused||s.cooldowns[key]>0;
   const t=b.querySelector('small');if(t)t.textContent='Lv '+s.skills[key]+' · '+(s.cooldowns[key]>0?s.cooldowns[key].toFixed(1)+'s':'READY');}
  const u=by('ef194Up'+key);if(u)u.hidden=s.skillPoints===0;
 }
 const revive=by('ef194Retry');if(revive)revive.hidden=!s.dead;
}
function ef194ShowHud(show){
 if(!ef194.hud)ef194InstallHud();
 ef194.hud.hidden=!show;
 if(!show)ef194.down.clear();
}
function ef194InstallHud(){
 if(ef194.hud)return ef194.hud;
 const hud=document.createElement('section');hud.id='ef194Hud';hud.hidden=true;
 hud.setAttribute('aria-label','Emberfall action RPG game controls');
 hud.innerHTML='<div class="ef194-top"><div class="ef194-heading"><strong>EMBERFALL</strong><span>SHATTERED VALE</span></div>'+
  '<div class="ef194-bars"><div class="ef194-bar ef194-life"><i id="ef194HpBar"></i></div><b id="ef194Hp"></b>'+
  '<div class="ef194-bar ef194-mana"><i id="ef194ManaBar"></i></div><b id="ef194Mana"></b>'+
  '<div class="ef194-bar ef194-xp"><i id="ef194XpBar"></i></div></div>'+
  '<div class="ef194-overview"><b id="ef194Stats"></b><span id="ef194Quest"></span></div></div>'+
  '<div class="ef194-side"><b>WAYFARER GEAR</b><span id="ef194Gear"></span><small id="ef194Loot"></small>'+
  '<label id="ef194SkillPts">Skills earn upgrades on level-up</label>'+
  '<div class="ef194-upgrades"><button id="ef194Upslash">+ Slash</button><button id="ef194Upbolt">+ Bolt</button><button id="ef194Upnova">+ Nova</button></div>'+
  '<button id="ef194Retry" hidden>↻ RESTART RUN</button></div>'+
  '<div class="ef194-actions"><button id="ef194Slash"><b>⚔ SLASH</b><small>SPACE · Lv 1</small></button>'+
  '<button id="ef194Bolt"><b>✧ BOLT</b><small>Q · Lv 1</small></button>'+
  '<button id="ef194Nova"><b>◉ NOVA</b><small>E · Lv 1</small></button>'+
  '<button id="ef194Potion"><b>♥ HEAL</b><small id="ef194Potions">POTION ×3</small></button></div>'+
  '<div class="ef194-tip">Tap ground to move · tap enemy to chase + strike · WASD / arrows · click loot to collect automatically</div>';
 (document.getElementById('viewport')?.parentElement||document.body).appendChild(hud);
 ef194.hud=hud;
 const el=id=>hud.querySelector('#'+id);
 el('ef194Slash').onclick=()=>ef194Cast('slash');
 el('ef194Bolt').onclick=()=>ef194Cast('bolt');
 el('ef194Nova').onclick=()=>ef194Cast('nova');
 el('ef194Potion').onclick=ef194Potion;
 el('ef194Upslash').onclick=()=>ef194SkillUp('slash');
 el('ef194Upbolt').onclick=()=>ef194SkillUp('bolt');
 el('ef194Upnova').onclick=()=>ef194SkillUp('nova');
 el('ef194Retry').onclick=()=>{document.getElementById('stopBtn')?.click();
  document.getElementById('playBtn')?.click();};
 for(const e of ['pointerdown','pointerup','click'])hud.addEventListener(e,ev=>ev.stopPropagation());
 return hud;
}
function ef194InstallInput(){
 if(ef194.installed)return;ef194.installed=true;
 renderer.domElement.addEventListener('pointerdown',event=>{
  if(!ef194.session||!playing)return;
  event.preventDefault();event.stopImmediatePropagation();
  if(event.button!==0&&event.button!==2)return;
  const p=ef194PointerPoint(event);if(p)ef194SelectPoint(p,event.button);
 },true);
 renderer.domElement.addEventListener('contextmenu',event=>{
  if(ef194.session){event.preventDefault();event.stopImmediatePropagation();}
 },true);
 renderer.domElement.addEventListener('wheel',event=>{
  if(!ef194.session)return;
  event.preventDefault();event.stopImmediatePropagation();
  ef194.session.cameraDistance=THREE.MathUtils.clamp(
   ef194.session.cameraDistance*(event.deltaY>0?1.09:.92),.73,1.55);
 },{capture:true,passive:false});
 window.addEventListener('keydown',event=>{
  if(!ef194.session||event.target?.closest?.('input,textarea,select,[contenteditable]'))return;
  const key=event.key.toLowerCase(),accept=['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright',' ','q','e','r'];
  if(!accept.includes(key))return;
  event.preventDefault();event.stopImmediatePropagation();
  if(key===' '){if(!event.repeat)ef194Cast('slash');}
  else if(key==='q'){if(!event.repeat)ef194Cast('bolt');}
  else if(key==='e'){if(!event.repeat)ef194Cast('nova');}
  else if(key==='r'){if(!event.repeat)ef194Potion();}
  else ef194.down.add(key);
 },true);
 window.addEventListener('keyup',event=>{
  if(!ef194.session)return;
  const key=event.key.toLowerCase();
  if(ef194.down.has(key)){ef194.down.delete(key);event.stopImmediatePropagation();}
 },true);
 window.addEventListener('blur',()=>ef194.down.clear());
}
function ef194Stop(){
 if(!ef194.session)return;
 const s=ef194.session;ef194.session=null;ef194.down.clear();
 ef194ShowHud(false);
 for(const obj of [...s.group.children])ef194Dispose(obj);
 s.group.removeFromParent();
 ef194.lastAction='Emberfall run stopped · authored world preserved';
}
function ef194Diagnostics(){
 const s=ef194.session;
 return {starter:currentProject?.kind===ef194.kind,active:!!s,
  hero:!!ef194Actor('emberfall-player'),authoredFoes:actors.filter(a=>['emberfall-enemy','emberfall-boss'].includes(a.userData.role)).length,
  level:s?.level||null,kills:s?.kills||0,loot:s?.loot.length||0,hp:s?.hp||null,
  quest:s?.quest||null,lastError:ef194.lastError};
}
window.SWYRL_ENGINE_EMBERFALL=Object.freeze({
 load:ef194MakeStarter,status:ef194Diagnostics,
 slash:()=>ef194Cast('slash'),bolt:()=>ef194Cast('bolt'),
 nova:()=>ef194Cast('nova'),potion:ef194Potion,skillUp:ef194SkillUp
});

if(document.readyState==='complete')ef194InstallInput();
else window.addEventListener('load',ef194InstallInput,{once:true});
