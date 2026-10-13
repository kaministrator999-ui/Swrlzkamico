// Deterministic, JSON-only Maul simulation. The editor owns rendering and input;
// this module owns the same construction, path and combat rules in Play and tests.
const MAUL_CORE = (() => {
  const defaults = Object.freeze({waves:30,lives:30,startGold:900,preparation:40,intermission:12,difficulty:1,spawnInterval:.5,autoWaves:true,soloSupport:true,selectedSector:0,seed:1317});
  const bounds = {waves:[1,30,true],lives:[1,200,true],startGold:[0,100000,true],preparation:[0,180,false],intermission:[0,60,false],difficulty:[.25,4,false],spawnInterval:[.1,2,false],selectedSector:[0,8,true],seed:[0,4294967295,true]};
  const definitions = {
    arrow:{kind:'arrow',name:'Arrow Spire',cost:20,ground:true,air:true,levels:[{damage:11,range:8,interval:.6,upgradeCost:35},{damage:27,range:9,interval:.5,upgradeCost:65},{damage:58,range:10,interval:.4,upgradeCost:0}]},
    cannon:{kind:'cannon',name:'Siege Bastion',cost:50,ground:true,air:false,levels:[{damage:26,range:8,interval:1.4,splash:3,upgradeCost:70},{damage:64,range:9,interval:1.25,splash:3.5,upgradeCost:125},{damage:145,range:10,interval:1.1,splash:4,upgradeCost:0}]},
    frost:{kind:'frost',name:'Frost Obelisk',cost:45,ground:true,air:true,levels:[{damage:7,range:7,interval:.8,slow:.55,slowDuration:2,upgradeCost:60},{damage:17,range:8,interval:.7,slow:.45,slowDuration:2.4,upgradeCost:100},{damage:38,range:9,interval:.6,slow:.35,slowDuration:3,upgradeCost:0}]},
    storm:{kind:'storm',name:'Storm Beacon',cost:70,ground:true,air:true,levels:[{damage:17,range:9,interval:.95,chain:3,chainRange:6,upgradeCost:85},{damage:39,range:10,interval:.8,chain:4,chainRange:6,upgradeCost:140},{damage:80,range:11,interval:.65,chain:5,chainRange:7,upgradeCost:0}]},
    'maze-wall':{kind:'maze-wall',name:'Maze Wall',cost:5,ground:false,air:false,levels:[{damage:0,range:0,interval:0,upgradeCost:0}]}
  };
  const priorities = Object.freeze(['first','last','strong','near']);
  const key = (x,z) => `${x},${z}`;
  const cell = value => ({x:Number(value?.x ?? value?.cx),z:Number(value?.z ?? value?.cz)});
  const integer = n => Number.isInteger(n) && Number.isFinite(n);
  const copy = value => JSON.parse(JSON.stringify(value));
  const result = (ok,code,reason,extra={}) => ({ok,code,reason,...extra});
  function validateRules(value={}) {
    const errors=[];
    if (!value || typeof value!=='object' || Array.isArray(value)) return {ok:false,errors:['Rules must be an object.']};
    for (const [name,[min,max,whole]] of Object.entries(bounds)) {
      if (value[name]===undefined) continue;
      const n=Number(value[name]);
      if (!Number.isFinite(n)||n<min||n>max||(whole&&!Number.isInteger(n))) errors.push(`${name} must be ${whole?'a whole number':'a number'} from ${min} to ${max}.`);
    }
    for (const name of ['autoWaves','soloSupport']) if (value[name]!==undefined&&typeof value[name]!=='boolean') errors.push(`${name} must be true or false.`);
    return {ok:errors.length===0,errors};
  }
  function cleanRules(value={}) {
    const rules={...defaults};
    if (!value||typeof value!=='object'||Array.isArray(value)) return rules;
    for (const [name,[min,max,whole]] of Object.entries(bounds)) {
      const n=Number(value[name]);
      if (value[name]!==undefined&&Number.isFinite(n)&&n>=min&&n<=max&&(!whole||integer(n))) rules[name]=n;
    }
    for (const name of ['autoWaves','soloSupport']) if (typeof value[name]==='boolean') rules[name]=value[name];
    return rules;
  }
  function mapDefault() {
    const blocked=[],reserved=[],spawns=[],sectors=[];
    for (let z=0;z<38;z++) for (let x=0;x<31;x++) {
      const vertical=[0,10,20,30].includes(x)&&z<=33;
      const horizontal=[0,11,22,33,37].includes(z)&&(z===0||z===37||![5,15,25].includes(x));
      if (vertical||horizontal||((x===0||x===30)&&z>=34)) blocked.push({x,z});
    }
    const rowNames=['North','Middle','South'],columnNames=['West','Heart','East'];
    for (let row=0;row<3;row++) for (let column=0;column<3;column++) {
      const id=row*3+column,spawn={x:column*10+5,z:row*11+1},gate={x:column*10+5,z:row*11+11};
      const gates=[];for(let next=row;next<3;next++) gates.push({x:spawn.x,z:next*11+11});
      spawns.push({...spawn,sector:id});sectors.push({id,name:`${rowNames[row]} ${columnNames[column]}`,minX:column*10+1,maxX:column*10+9,minZ:row*11+1,maxZ:row*11+10,spawn,gate,gates});
      reserved.push(spawn,gate);
    }
    const exit={x:15,z:36};reserved.push(exit);
    return {cols:31,rows:38,cell:2,origin:{x:-30,z:-37},blocked,reserved,spawns,sectors,exit};
  }
  function worldToCell(map,x,z) {return {x:Math.round((x-map.origin.x)/map.cell),z:Math.round((z-map.origin.z)/map.cell)};}
  function cellToWorld(map,x,z) {if(typeof x==='object'){z=x.z??x.cz;x=x.x??x.cx;}return {x:map.origin.x+x*map.cell,z:map.origin.z+z*map.cell};}
  function inside(map,p) {return integer(p.x)&&integer(p.z)&&p.x>=0&&p.z>=0&&p.x<map.cols&&p.z<map.rows;}
  function blockedSet(map,additional=[]) {
    const set=new Set();
    for (const p of map.blocked||[]) {const c=cell(p);set.add(key(c.x,c.z));}
    const list=additional instanceof Set?[...additional]:additional||[];
    for (const value of list) {if(typeof value==='string')set.add(value);else{const p=cell(value);set.add(key(p.x,p.z));}}
    return set;
  }
  function path(map,blocked,start,end) {
    start=cell(start);end=cell(end);
    const cells=blockedSet(map,blocked);
    if (!inside(map,start)||!inside(map,end)||cells.has(key(start.x,start.z))||cells.has(key(end.x,end.z))) return null;
    const width=map.cols,size=width*map.rows,startIndex=start.z*width+start.x,endIndex=end.z*width+end.x;
    const visited=new Uint8Array(size),parent=new Int32Array(size),queue=new Int32Array(size);parent.fill(-1);
    let head=0,tail=1;queue[0]=startIndex;visited[startIndex]=1;
    // Forward first makes open routes easy to read; all moves remain cardinal.
    const directions=[[0,1],[-1,0],[1,0],[0,-1]];
    while(head<tail&&!visited[endIndex]) {
      const index=queue[head++],x=index%width,z=Math.floor(index/width);
      for(const [dx,dz] of directions){const nx=x+dx,nz=z+dz;if(nx<0||nz<0||nx>=width||nz>=map.rows||cells.has(key(nx,nz)))continue;
        const next=nz*width+nx;if(visited[next])continue;visited[next]=1;parent[next]=index;queue[tail++]=next;}
    }
    if(!visited[endIndex])return null;
    const route=[];for(let index=endIndex;index!==-1;index=parent[index]){route.push({x:index%width,z:Math.floor(index/width)});if(index===startIndex)break;}
    route.reverse();return route;
  }
  function waypoints(map,start,sector) {
    const record=(map.sectors||[]).find(s=>s.id===sector);
    const gateX=record?.gate?.x??(Math.min(2,Math.max(0,Math.floor(start.x/10)))*10+5);
    const gates=record?.gates || (map.sectors||[]).filter(s=>s.gate?.x===gateX).map(s=>s.gate).sort((a,b)=>a.z-b.z);
    const points=gates.filter(p=>p.z>=start.z).map(p=>({...p}));
    points.push({...map.exit});return points;
  }
  function route(map,blocked,start,sector,air=false) {
    start=cell(start);const points=waypoints(map,start,sector);
    if(air)return [start,...points.filter((p,i)=>i!==0||p.x!==start.x||p.z!==start.z)];
    const joined=[start];let cursor=start;
    for(const target of points){const part=path(map,blocked,cursor,target);if(!part)return null;joined.push(...part.slice(1));cursor=target;}
    return joined;
  }
  function preflight(map,towers=[]) {
    const errors=[],valid=[];
    if(!map||!integer(map.cols)||!integer(map.rows)||map.cols<3||map.rows<3||map.cols>100||map.rows>100||!Number.isFinite(map.cell)||map.cell<.25||map.cell>10||!Number.isFinite(map.origin?.x)||!Number.isFinite(map.origin?.z)) return {ok:false,errors:['Map grid dimensions or world origin are invalid.'],paths:[]};
    if(!Array.isArray(map.spawns)||map.spawns.length!==9)errors.push('The Maul map needs nine sector spawns.');
    const walls=blockedSet(map),reserved=new Set((map.reserved||[]).map(p=>key(p.x,p.z))),occupied=new Set();
    for(const p of map.blocked||[])if(!inside(map,cell(p)))errors.push('A map wall is outside the grid.');
    if(!inside(map,cell(map.exit))||walls.has(key(map.exit?.x,map.exit?.z)))errors.push('The shared exit must be an open grid cell.');
    for(const spawn of map.spawns||[])if(!inside(map,cell(spawn))||walls.has(key(spawn.x,spawn.z)))errors.push(`Sector ${spawn.sector??'?'} spawn is outside or blocked.`);
    for(const [index,value] of towers.entries()) {
      const p=cell(value),definition=definitions[value.kind],level=value.level??1,token=key(p.x,p.z);
      if(!definition){errors.push(`Tower ${index+1} has an unknown kind.`);continue;}
      if(!integer(level)||level<1||level>definition.levels.length)errors.push(`Tower ${index+1} has an invalid level.`);
      if(!inside(map,p)||walls.has(token)||reserved.has(token)){errors.push(`Tower ${index+1} occupies a wall, protected cell or outside the grid.`);continue;}
      if(occupied.has(token))errors.push(`Tower ${index+1} overlaps another tower.`);
      occupied.add(token);valid.push(p);
    }
    const paths=[];
    for(const spawn of map.spawns||[]){const p=route(map,valid,spawn,spawn.sector);paths.push(p);if(!p)errors.push(`Sector ${(spawn.sector??0)+1} has no route through its gates to the shared exit.`);}
    return {ok:errors.length===0,errors,paths};
  }
  function event(s,type,details={}) {const e={seq:++s.eventSeq,t:s.elapsed,type,details};s.events.push(e);return e;}
  function stats(tower) {return definitions[tower.kind].levels[tower.level-1];}
  function costAtLevel(kind,level) {const d=definitions[kind];let cost=d.cost;for(let i=0;i<level-1;i++)cost+=d.levels[i].upgradeCost;return cost;}
  function normalizeTower(value,index) {
    const d=definitions[value.kind],level=value.level??1,p=cell(value);
    return {id:String(value.id||`maul-tower-${index+1}`),kind:d.kind,cx:p.x,cz:p.z,level,spent:costAtLevel(d.kind,level),priority:priorities.includes(value.priority)?value.priority:'first',cooldown:0,owner:value.owner==='player'||String(value.owner||'').startsWith('ally-')?String(value.owner):'player'};
  }
  function createSession({rules={},map=mapDefault(),towers=[]}={}) {
    const ruleCheck=validateRules(rules);if(!ruleCheck.ok)throw new Error(ruleCheck.errors.join(' '));
    const check=preflight(map,towers);if(!check.ok)throw new Error(check.errors.join(' '));
    const clean=cleanRules(rules),normalized=towers.map(normalizeTower),ids=new Set(normalized.map(t=>t.id));
    if(ids.size!==normalized.length)throw new Error('Authored towers must have unique IDs.');
    const lastId=Math.max(normalized.length,...normalized.map(t=>Number(/^maul-tower-(\d+)$/.exec(t.id)?.[1])||0));
    const s={elapsed:0,gold:clean.startGold,lives:clean.lives,wave:0,phase:'preparation',timer:clean.preparation,kills:0,leaks:0,rules:clean,map:copy(map),towers:normalized,units:[],shots:[],events:[],eventSeq:0,idSeq:lastId,spawnQueue:[],waveElapsed:0,allyBudgets:{},seed:clean.seed||1};
    event(s,'session-started',{rules:copy(clean),authoredTowers:normalized.length});
    if(clean.soloSupport)installAllies(s);
    return s;
  }
  function mutable(s) {return s&&s.phase!=='won'&&s.phase!=='lost';}
  function canBuild(s,kind,cx,cz) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    const d=definitions[kind],p={x:cx,z:cz};
    if(!d)return result(false,'kind','Choose a tower or maze wall.');
    if(!inside(s.map,p))return result(false,'outside','Place the structure inside the grid.');
    if(blockedSet(s.map).has(key(cx,cz)))return result(false,'wall','Map walls cannot be built on.');
    if((s.map.reserved||[]).some(p=>p.x===cx&&p.z===cz)||(s.map.spawns||[]).some(p=>p.x===cx&&p.z===cz)||(s.map.sectors||[]).some(p=>p.gate?.x===cx&&p.gate?.z===cz)||(s.map.exit.x===cx&&s.map.exit.z===cz))return result(false,'reserved','Spawns, gates and the shared exit must stay open.');
    if(s.towers.some(t=>t.cx===cx&&t.cz===cz))return result(false,'occupied','A structure already occupies this cell.');
    const site=cellToWorld(s.map,cx,cz);
    if(s.units.some(u=>{const clearance=.95+(u.boss?.8:.45);return u.alive&&!u.air&&Math.abs(u.x-site.x)<=clearance&&Math.abs(u.z-site.z)<=clearance;}))return result(false,'creep','A ground creep overlaps this structure footprint.');
    if(s.gold<d.cost)return result(false,'gold',`This structure costs ${d.cost} gold.`,{cost:d.cost});
    const towers=[...s.towers,{kind,cx,cz,level:1}],check=preflight(s.map,towers);
    if(!check.ok)return result(false,'blocked','Leave a route through every sector to the shared exit.',{errors:check.errors,cost:d.cost});
    const routes={};
    for(const u of s.units){if(!u.alive||u.air)continue;const p=route(s.map,towers,{x:u.cx,z:u.cz},u.sector);if(!p)return result(false,'trapped','This would trap a ground creep.',{cost:d.cost});routes[u.id]=p;}
    return result(true,'ready','Placement is valid.',{cost:d.cost,routes});
  }
  function reroute(s,routes=null) {
    for(const u of s.units){if(!u.alive||u.air)continue;const p=routes?.[u.id]||route(s.map,s.towers,{x:u.cx,z:u.cz},u.sector);if(p){u.path=p;u.pathIndex=0;u.remaining=remaining(s,u);}}
  }
  function build(s,kind,cx,cz) {
    const fit=canBuild(s,kind,cx,cz);if(!fit.ok)return fit;
    const t={id:`maul-tower-${++s.idSeq}`,kind,cx,cz,level:1,spent:definitions[kind].cost,priority:'first',cooldown:0,owner:'player'};
    s.gold-=t.spent;s.towers.push(t);reroute(s,fit.routes);event(s,'built',{id:t.id,kind,cx,cz,cost:t.spent,gold:s.gold});
    return result(true,'built',`${definitions[kind].name} constructed.`,{tower:t});
  }
  function upgrade(s,id) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    const t=s.towers.find(t=>t.id===id);if(!t)return result(false,'missing','Select a tower.');
    if(t.owner!=='player')return result(false,'ally','Allied builders manage their own towers.');
    const d=definitions[t.kind],v=stats(t);if(t.level>=d.levels.length)return result(false,'maximum','This structure is at its highest level.');
    if(s.gold<v.upgradeCost)return result(false,'gold',`The upgrade costs ${v.upgradeCost} gold.`);
    const cost=v.upgradeCost;s.gold-=cost;t.spent+=cost;t.level++;t.cooldown=Math.min(t.cooldown,stats(t).interval);event(s,'upgraded',{id,level:t.level,cost,gold:s.gold});
    return result(true,'upgraded',`${d.name} upgraded to level ${t.level}.`,{tower:t,cost});
  }
  function sell(s,id) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    const index=s.towers.findIndex(t=>t.id===id);if(index<0)return result(false,'missing','Select a structure.');
    const t=s.towers[index];if(t.owner!=='player')return result(false,'ally','Allied builders manage their own towers.');
    const refund=Math.floor(t.spent*.7);s.towers.splice(index,1);s.gold+=refund;reroute(s);event(s,'sold',{id,kind:t.kind,refund,gold:s.gold});
    return result(true,'sold',`Structure sold for ${refund} gold.`,{refund});
  }
  function setPriority(s,id,priority) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    const t=s.towers.find(t=>t.id===id);if(!t)return result(false,'missing','Select a tower.');
    if(!priorities.includes(priority))return result(false,'priority','Choose first, last, strongest or nearest.');
    if(t.owner!=='player')return result(false,'ally','Allied builders manage their own towers.');
    t.priority=priority;event(s,'priority',{id,priority});return result(true,'priority','Target priority changed.',{tower:t});
  }
  function installAllies(s) {
    for(const sector of s.map.sectors||[]){if(sector.id===s.rules.selectedSector)continue;
      const owner=`ally-${sector.id}`;s.allyBudgets[owner]=120;
      const proposals=[{kind:'arrow',cx:sector.spawn.x-2,cz:sector.maxZ-2},{kind:'storm',cx:sector.spawn.x+2,cz:sector.maxZ-2}];
      for(const p of proposals){if(!preflight(s.map,[...s.towers,{...p,level:1}]).ok)continue;
        const d=definitions[p.kind];if(s.allyBudgets[owner]<d.cost)continue;
        const t={id:`maul-tower-${++s.idSeq}`,...p,level:1,spent:d.cost,priority:'first',cooldown:0,owner};
        s.towers.push(t);s.allyBudgets[owner]-=d.cost;event(s,'ally-built',{id:t.id,owner,kind:t.kind,cx:t.cx,cz:t.cz,cost:d.cost});}
    }
  }
  function upgradeAllies(s) {
    for(const owner of Object.keys(s.allyBudgets)){s.allyBudgets[owner]+=40+s.wave*4;
      const towers=s.towers.filter(t=>t.owner===owner).sort((a,b)=>a.level-b.level||a.id.localeCompare(b.id));
      for(const t of towers){const v=stats(t);if(t.level>=definitions[t.kind].levels.length||s.allyBudgets[owner]<v.upgradeCost)continue;
        s.allyBudgets[owner]-=v.upgradeCost;t.spent+=v.upgradeCost;t.level++;event(s,'ally-upgraded',{id:t.id,owner,level:t.level,cost:v.upgradeCost});}
    }
  }
  function startWave(s) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    if(s.phase==='wave')return result(false,'active','The current wave is still running.');
    if(s.wave>=s.rules.waves)return result(false,'complete','All waves are complete.');
    const check=preflight(s.map,s.towers);if(!check.ok)return result(false,'blocked','The map must have an open route for every sector.',{errors:check.errors});
    s.wave++;s.phase='wave';s.timer=0;s.waveElapsed=0;s.spawnQueue=[];
    const boss=s.wave%10===0,air=s.wave%5===0&&!boss,count=boss?5:air?6+Math.floor(s.wave/6):Math.min(16,6+Math.floor(s.wave/3));
    for(let index=0;index<count;index++)for(const spawn of s.map.spawns)s.spawnQueue.push({at:index*s.rules.spawnInterval+(spawn.sector%3)*.035,sector:spawn.sector,spawn:{x:spawn.x,z:spawn.z},air,boss:boss&&index===count-1,index});
    s.spawnQueue.sort((a,b)=>a.at-b.at||a.sector-b.sector);event(s,'wave-started',{wave:s.wave,air,boss,count:s.spawnQueue.length});
    return result(true,'wave',`Wave ${s.wave} started.`);
  }
  function random(s) {let x=s.seed;x^=x<<13;x^=x>>>17;x^=x<<5;s.seed=x>>>0;return s.seed/4294967296;}
  function spawnUnit(s,item) {
    const base=24*Math.pow(1+.12*s.wave,1.4)*s.rules.difficulty,hp=Math.round(base*(item.boss?6:1)*(item.air?.9:1)),p=cellToWorld(s.map,item.spawn);
    const unit={id:`maul-creep-${++s.idSeq}`,sector:item.sector,x:p.x,z:p.z,cx:item.spawn.x,cz:item.spawn.z,hp,maxHp:hp,speed:(item.air?3.9:2.9)+s.wave*.03,air:item.air,boss:item.boss,armor:s.wave%4===0?10+Math.floor(s.wave/3):item.boss?12:0,bounty:(item.boss?30:5)+Math.floor(s.wave/4),path:route(s.map,s.towers,item.spawn,item.sector,item.air),pathIndex:1,progress:0,remaining:0,alive:true,slowUntil:0,slowFactor:1,variant:Math.floor(random(s)*3)};
    unit.remaining=remaining(s,unit);s.units.push(unit);event(s,'spawned',{id:unit.id,sector:unit.sector,air:unit.air,boss:unit.boss,hp:unit.hp,armor:unit.armor});
  }
  function remaining(s,u) {
    if(!u.path||u.pathIndex>=u.path.length)return 0;
    let distance=0,previous={x:u.x,z:u.z};
    for(let i=u.pathIndex;i<u.path.length;i++){const point=cellToWorld(s.map,u.path[i]);distance+=Math.hypot(point.x-previous.x,point.z-previous.z);previous=point;}
    return distance;
  }
  function moveUnit(s,u,dt) {
    if(u.slowUntil<=s.elapsed){u.slowUntil=0;u.slowFactor=1;}
    let budget=u.speed*(u.slowUntil>s.elapsed?u.slowFactor:1)*dt;
    while(budget>0&&u.pathIndex<u.path.length){const target=cellToWorld(s.map,u.path[u.pathIndex]),dx=target.x-u.x,dz=target.z-u.z,distance=Math.hypot(dx,dz);
      if(distance<=budget+1e-9){u.x=target.x;u.z=target.z;u.progress+=distance;budget-=distance;u.pathIndex++;}
      else{u.x+=dx/distance*budget;u.z+=dz/distance*budget;u.progress+=budget;budget=0;}}
    const p=worldToCell(s.map,u.x,u.z);u.cx=p.x;u.cz=p.z;u.remaining=remaining(s,u);
    if(u.pathIndex>=u.path.length){u.alive=false;u.endedAt=s.elapsed;s.leaks++;s.lives--;event(s,'leaked',{id:u.id,sector:u.sector,boss:u.boss,lives:s.lives});
      if(s.lives<=0){s.lives=0;s.phase='lost';s.timer=0;event(s,'lost',{wave:s.wave,kills:s.kills,leaks:s.leaks});}}
  }
  function targetCandidates(s,t,range) {
    const d=definitions[t.kind],p=cellToWorld(s.map,t.cx,t.cz),list=s.units.filter(u=>u.alive&&(u.air?d.air:d.ground)&&Math.hypot(u.x-p.x,u.z-p.z)<=range+1e-9);
    list.sort((a,b)=>{
      let delta=0;if(t.priority==='last')delta=b.remaining-a.remaining;else if(t.priority==='strong')delta=b.hp-a.hp;else if(t.priority==='near')delta=Math.hypot(a.x-p.x,a.z-p.z)-Math.hypot(b.x-p.x,b.z-p.z);else delta=a.remaining-b.remaining;
      return delta||a.id.localeCompare(b.id);
    });return list;
  }
  function hit(s,t,u,damage) {
    if(!u.alive)return;
    const amount=damage*100/(100+u.armor);u.hp=Math.max(0,u.hp-amount);const v=stats(t);
    if(v.slow){u.slowUntil=Math.max(u.slowUntil,s.elapsed+v.slowDuration);u.slowFactor=Math.min(u.slowFactor,v.slow);}
    if(u.hp<=0){u.alive=false;u.endedAt=s.elapsed;s.kills++;
      if(t.owner==='player')s.gold+=u.bounty;else s.allyBudgets[t.owner]=(s.allyBudgets[t.owner]||0)+u.bounty;
      event(s,'killed',{id:u.id,towerId:t.id,owner:t.owner,bounty:u.bounty,gold:s.gold,sector:u.sector});}
  }
  function attack(s,t,dt) {
    const v=stats(t);if(v.damage<=0)return;
    t.cooldown=Math.max(0,t.cooldown-dt);if(t.cooldown>1e-9)return;
    const target=targetCandidates(s,t,v.range)[0];if(!target)return;
    const origin=cellToWorld(s.map,t.cx,t.cz),visited=new Set();
    const shoot=(u,from,scale=1)=>{visited.add(u.id);s.shots.push({id:`maul-shot-${++s.idSeq}`,from:{x:from.x,y:from.y??2.6,z:from.z},to:{x:u.x,y:u.air?3.8:.8,z:u.z},kind:t.kind,ttl:.2,targetId:u.id});hit(s,t,u,v.damage*scale);};
    const location={x:target.x,z:target.z};shoot(target,origin);
    if(v.splash)for(const u of s.units)if(u.alive&&!u.air&&u.id!==target.id&&Math.hypot(u.x-location.x,u.z-location.z)<=v.splash)hit(s,t,u,v.damage*.7);
    if(v.chain){let previous=location;for(let i=1;i<v.chain;i++){
      const next=s.units.filter(u=>u.alive&&!visited.has(u.id)&&(u.air?definitions[t.kind].air:definitions[t.kind].ground)&&Math.hypot(u.x-previous.x,u.z-previous.z)<=v.chainRange).sort((a,b)=>Math.hypot(a.x-previous.x,a.z-previous.z)-Math.hypot(b.x-previous.x,b.z-previous.z)||a.id.localeCompare(b.id))[0];
      if(!next)break;const at={x:next.x,y:next.air?3.8:.8,z:next.z};shoot(next,previous,Math.pow(.8,i));previous=at;}}
    t.cooldown=v.interval;
  }
  function finishWave(s) {
    const bonus=40+s.wave*4;s.gold+=bonus;event(s,'wave-cleared',{wave:s.wave,bonus,gold:s.gold,kills:s.kills,leaks:s.leaks});
    if(s.wave>=s.rules.waves){s.phase='won';s.timer=0;event(s,'won',{wave:s.wave,kills:s.kills,leaks:s.leaks,lives:s.lives});return;}
    if(s.rules.soloSupport)upgradeAllies(s);s.phase='intermission';s.timer=s.rules.intermission;
  }
  function tick(s,dt) {
    if(!mutable(s)||!Number.isFinite(dt)||dt<=0)return status(s);
    // The native editor supplies <= .05 s. Large requests are split internally,
    // so tests, throttled tabs and imported review clocks cannot tunnel creeps.
    let left=Math.min(dt,1);
    while(left>1e-9&&mutable(s)){const step=Math.min(.05,left);left-=step;s.elapsed+=step;
      s.shots=s.shots.filter(shot=>(shot.ttl-=step)>0);
      s.units=s.units.filter(u=>u.alive||s.elapsed-(u.endedAt??s.elapsed)<1.2);
      if(s.phase!=='wave'){s.timer=Math.max(0,s.timer-step);if(s.timer<=0&&s.rules.autoWaves)startWave(s);continue;}
      s.waveElapsed+=step;while(s.spawnQueue.length&&s.spawnQueue[0].at<=s.waveElapsed+1e-9)spawnUnit(s,s.spawnQueue.shift());
      for(const u of s.units){if(u.alive)moveUnit(s,u,step);if(s.phase==='lost')break;}
      if(s.phase==='lost')break;
      for(const t of s.towers)attack(s,t,step);
      if(!s.spawnQueue.length&&!s.units.some(u=>u.alive))finishWave(s);
    }
    return status(s);
  }
  function status(s) {
    if(!s)return null;
    return {elapsed:s.elapsed,gold:s.gold,lives:s.lives,wave:s.wave,totalWaves:s.rules.waves,phase:s.phase,timer:s.timer,kills:s.kills,leaks:s.leaks,creeps:s.units.filter(u=>u.alive).length,queued:s.spawnQueue.length,towers:s.towers.length,playerTowers:s.towers.filter(t=>t.owner==='player').length,allyTowers:s.towers.filter(t=>t.owner!=='player').length};
  }
  return Object.freeze({defaults,definitions,priorities,cleanRules,validateRules,mapDefault,worldToCell,cellToWorld,path,route,preflight,createSession,canBuild,build,upgrade,sell,setPriority,startWave,tick,status,stats});
})();
// MAUL_CORE_END
