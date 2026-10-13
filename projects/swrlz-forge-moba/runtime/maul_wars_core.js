// Wintermaul Wars-inspired deterministic Tower Wars simulation. This is JSON-only;
// native editor actors, cameras and input remain the responsibility of the adapter.
const MAUL_WARS_CORE = (() => {
  const defaults=Object.freeze({lives:25,startGold:450,startIncome:25,preparation:30,incomeInterval:25,spawnInterval:.55,soloSupport:true,opponentAI:true,difficulty:1,selectedSector:0,seed:1317});
  const bounds={lives:[1,200,true],startGold:[0,100000,true],startIncome:[0,1000,true],preparation:[0,180,false],incomeInterval:[5,120,false],spawnInterval:[.1,2,false],difficulty:[.25,4,false],selectedSector:[0,2,true],seed:[0,4294967295,true]};
  const definitions=MAUL_CORE.definitions,priorities=MAUL_CORE.priorities;
  const sends=Object.freeze({
    wisp:Object.freeze({kind:'wisp',name:'Snow Wisp',cost:15,income:1,hp:30,speed:3,bounty:3,armor:0,air:false,boss:false}),
    brute:Object.freeze({kind:'brute',name:'Frost Brute',cost:40,income:3,hp:150,speed:2.8,bounty:7,armor:15,air:false,boss:false}),
    flyer:Object.freeze({kind:'flyer',name:'Winter Drake',cost:60,income:4,hp:100,speed:4,bounty:9,armor:5,air:true,boss:false}),
    siege:Object.freeze({kind:'siege',name:'Glacial Siege',cost:120,income:7,hp:450,speed:2.3,bounty:18,armor:25,air:false,boss:true})
  });
  const copy=value=>JSON.parse(JSON.stringify(value)),key=(x,z)=>`${x},${z}`;
  const integer=n=>Number.isFinite(n)&&Number.isInteger(n),cell=p=>({x:Number(p?.x??p?.cx),z:Number(p?.z??p?.cz)});
  const result=(ok,code,reason,extra={})=>({ok,code,reason,...extra});
  const worldToCell=MAUL_CORE.worldToCell,cellToWorld=MAUL_CORE.cellToWorld,path=MAUL_CORE.path,stats=MAUL_CORE.stats;
  const inside=(m,p)=>integer(p.x)&&integer(p.z)&&p.x>=0&&p.z>=0&&p.x<m.cols&&p.z<m.rows;
  function validateRules(value={}) {
    const errors=[];
    if(!value||typeof value!=='object'||Array.isArray(value))return {ok:false,errors:['Wars rules must be an object.']};
    for(const [name,[min,max,whole]] of Object.entries(bounds)){if(value[name]===undefined)continue;const n=Number(value[name]);if(!Number.isFinite(n)||n<min||n>max||(whole&&!integer(n)))errors.push(`${name} must be ${whole?'a whole number':'a number'} from ${min} to ${max}.`);}
    for(const name of ['soloSupport','opponentAI'])if(value[name]!==undefined&&typeof value[name]!=='boolean')errors.push(`${name} must be true or false.`);
    return {ok:!errors.length,errors};
  }
  function cleanRules(value={}) {
    const rules={...defaults};if(!value||typeof value!=='object'||Array.isArray(value))return rules;
    for(const [name,[min,max,whole]] of Object.entries(bounds)){const n=Number(value[name]);if(value[name]!==undefined&&Number.isFinite(n)&&n>=min&&n<=max&&(!whole||integer(n)))rules[name]=n;}
    for(const name of ['soloSupport','opponentAI'])if(typeof value[name]==='boolean')rules[name]=value[name];
    return rules;
  }
  function mapDefault() {
    const blocked=[],reserved=[],sectors=[],routes=[];
    for(let z=0;z<51;z++)for(let x=0;x<49;x++)if(x===0||x===48||z===0||z===50||z===25||(x>=10&&x<=38&&((z>=8&&z<=15)||(z>=35&&z<=42))))blocked.push({x,z});
    const first=[{x:45,z:3},{x:45,z:20},{x:24,z:20},{x:3,z:20},{x:3,z:10},{x:6,z:10}];
    for(let team=0;team<2;team++){
      const mirror=p=>({x:p.x,z:team?50-p.z:p.z}),spawn=mirror({x:3,z:3}),waypoints=first.map(mirror),exit=waypoints.at(-1);
      routes.push({team,spawn,waypoints,exit:{...exit}});reserved.push({...spawn},...waypoints.map(p=>({...p})));
      for(let local=0;local<3;local++){
        const id=team*3+local,range=local===0?{minX:1,maxX:23,minZ:1,maxZ:15}:local===1?{minX:24,maxX:47,minZ:1,maxZ:15}:{minX:1,maxX:47,minZ:16,maxZ:24};
        const focus=mirror(local===0?{x:12,z:5}:local===1?{x:39,z:7}:{x:24,z:20});
        if(team){const lo=50-range.maxZ,hi=50-range.minZ;range.minZ=lo;range.maxZ=hi;}
        sectors.push({id,team,name:`${team?'Crimson':'Azure'} ${['West','East','Rear'][local]}`,...range,focus,...(local===0?{spawn:{...spawn}}:{})});
      }
    }
    return {cols:49,rows:51,cell:2,origin:{x:-48,z:-50},blocked,reserved,routes,sectors};
  }
  function slotAt(map,cx,cz) {
    const p={x:cx,z:cz};if(!inside(map,p))return null;
    // Sector extents are authored metadata, so transformed starter fixtures keep
    // ownership consistent with the six visible defense territories.
    const matches=(map.sectors||[]).filter(v=>cx>=v.minX&&cx<=v.maxX&&cz>=v.minZ&&cz<=v.maxZ);
    return matches.length===1?matches[0].id:null;
  }
  function route(map,blocked,start,team,air=false,stage=0) {
    start=cell(start);const record=(map.routes||[]).find(r=>r.team===team);
    if(!record||!Array.isArray(record.waypoints)||!inside(map,start)||!integer(stage)||stage<0||stage>record.waypoints.length)return null;
    const joined=[{...start,stage}];let cursor=start;
    for(let i=stage;i<record.waypoints.length;i++){
      const target=cell(record.waypoints[i]);
      if(air){joined.push({...target,stage:i+1});cursor=target;continue;}
      const part=path(map,blocked,cursor,target);if(!part)return null;
      if(part.length===1)joined.push({...target,stage:i+1});
      else for(let j=1;j<part.length;j++)joined.push({...part[j],stage:j===part.length-1?i+1:i});
      cursor=target;
    }
    return joined;
  }
  function preflight(map,towers=[]) {
    const errors=[],paths=[];
    if(!map||!integer(map.cols)||!integer(map.rows)||map.cols<3||map.rows<3||map.cols>100||map.rows>100||!Number.isFinite(map.cell)||map.cell<.25||map.cell>10||!Number.isFinite(map.origin?.x)||!Number.isFinite(map.origin?.z))return {ok:false,errors:['Wars map grid dimensions or origin are invalid.'],paths};
    if(!Array.isArray(map.blocked)||!Array.isArray(map.reserved))return {ok:false,errors:['Wars blocked and protected cells must be arrays.'],paths};
    const walls=new Set((map.blocked||[]).map(p=>key(p.x,p.z))),reserved=new Set((map.reserved||[]).map(p=>key(p.x,p.z))),occupied=new Set();
    if(!Array.isArray(map.sectors)||map.sectors.length!==6||new Set(map.sectors?.map(v=>v.id)).size!==6)errors.push('The Wars map needs six unique defense sectors.');
    for(const sector of map.sectors||[])if(!integer(sector.id)||sector.id<0||sector.id>5||sector.team!==Math.floor(sector.id/3)||![sector.minX,sector.maxX,sector.minZ,sector.maxZ].every(integer)||sector.minX>sector.maxX||sector.minZ>sector.maxZ||!inside(map,{x:sector.minX,z:sector.minZ})||!inside(map,{x:sector.maxX,z:sector.maxZ}))errors.push('A defense sector has invalid ownership or bounds.');
    if(!Array.isArray(map.routes)||map.routes.length!==2||new Set(map.routes?.map(v=>v.team)).size!==2)errors.push('The Wars map needs one ordered route for each team.');
    for(const p of map.blocked||[])if(!inside(map,cell(p)))errors.push('A map wall lies outside the grid.');
    for(const record of map.routes||[]){
      if(![0,1].includes(record.team)||!Array.isArray(record.waypoints)||record.waypoints.length<2||record.waypoints.length>24){errors.push('A team route needs valid ordered waypoints.');continue;}
      const points=[record.spawn,...record.waypoints];
      for(const p of points)if(!inside(map,cell(p))||walls.has(key(p?.x,p?.z))||!reserved.has(key(p?.x,p?.z))||Math.floor((slotAt(map,p?.x,p?.z)??-3)/3)!==record.team)errors.push(`Team ${record.team+1} has a blocked, unprotected or out-of-team route point.`);
      if(record.exit?.x!==record.waypoints.at(-1)?.x||record.exit?.z!==record.waypoints.at(-1)?.z)errors.push(`Team ${record.team+1} route must end at its ship.`);
    }
    for(const [index,value] of towers.entries()){
      const p=cell(value),d=definitions[value.kind],level=value.level??1,token=key(p.x,p.z),slot=slotAt(map,p.x,p.z);
      if(!d){errors.push(`Tower ${index+1} has an unknown kind.`);continue;}
      if(!integer(level)||level<1||level>d.levels.length)errors.push(`Tower ${index+1} has an invalid level.`);
      if(!inside(map,p)||walls.has(token)||reserved.has(token)||slot===null)errors.push(`Tower ${index+1} occupies a wall, protected point or outside a defense sector.`);
      if(value.owner!==undefined&&value.owner!==slot)errors.push(`Tower ${index+1} must belong to the builder of its defense sector.`);
      if(occupied.has(token))errors.push(`Tower ${index+1} overlaps another tower.`);occupied.add(token);
    }
    if(!errors.length)for(const record of map.routes){const p=route(map,towers,record.spawn,record.team);paths.push(p);if(!p)errors.push(`Team ${record.team+1} needs an open route through every waypoint to its ship.`);else if(p.some(v=>Math.floor((slotAt(map,v.x,v.z)??-3)/3)!==record.team))errors.push(`Team ${record.team+1} route leaves its defense territory.`);}
    return {ok:!errors.length,errors,paths};
  }
  function event(s,type,details={}){const e={seq:++s.eventSeq,t:s.elapsed,type,details};s.events.push(e);return e;}
  const mutable=s=>s&&s.phase!=='won'&&s.phase!=='lost';
  const player=(s,id)=>integer(id)&&id>=0&&id<6?s.players[id]:null;
  function costAtLevel(kind,level){let total=definitions[kind].cost;for(let i=0;i<level-1;i++)total+=definitions[kind].levels[i].upgradeCost;return total;}
  function createSession({rules={},map=mapDefault(),towers=[]}={}) {
    const rulesCheck=validateRules(rules);if(!rulesCheck.ok)throw new Error(rulesCheck.errors.join(' '));
    const check=preflight(map,towers);if(!check.ok)throw new Error(check.errors.join(' '));
    const clean=cleanRules(rules),normalized=towers.map((t,i)=>{const p=cell(t),owner=slotAt(map,p.x,p.z),level=t.level??1;return {id:String(t.id||`wars-tower-${i+1}`),kind:t.kind,cx:p.x,cz:p.z,owner,team:Math.floor(owner/3),level,spent:costAtLevel(t.kind,level),priority:priorities.includes(t.priority)?t.priority:'first',cooldown:0};});
    if(new Set(normalized.map(t=>t.id)).size!==normalized.length)throw new Error('Authored towers must have unique IDs.');
    const lastId=Math.max(normalized.length,...normalized.map(t=>Number(/^wars-(?:tower|creep|shot)-(\d+)$/.exec(t.id)?.[1])||0));
    const players=Array.from({length:6},(_,id)=>({id,team:Math.floor(id/3),gold:clean.startGold,income:clean.startIncome,ai:id>=3?clean.opponentAI:id>0&&clean.soloSupport,nextDecision:0,nextSend:clean.preparation+7+id*.8}));
    const s={elapsed:0,phase:clean.preparation>0?'preparation':'battle',winner:null,timer:clean.preparation,incomeTimer:clean.incomeInterval,rules:clean,map:copy(map),players,teams:[{id:0,lives:clean.lives,kills:0,leaks:0},{id:1,lives:clean.lives,kills:0,leaks:0}],selectedSector:clean.selectedSector,towers:normalized,units:[],shots:[],events:[],idSeq:lastId,eventSeq:0,spawnQueue:[],seed:clean.seed||1};
    event(s,'session-started',{rules:copy(clean),authoredTowers:normalized.length,initialSeed:clean.seed,localTeam:0});
    if(s.phase==='battle')event(s,'battle-started',{teams:2,players:6});return s;
  }
  function canBuild(s,kind,cx,cz,playerId=s?.selectedSector??0) {
    if(!mutable(s))return result(false,'finished','The match has finished.');
    const owner=player(s,playerId),d=definitions[kind],p={x:cx,z:cz};
    if(!owner)return result(false,'player','Choose a valid builder.');if(!d)return result(false,'kind','Choose a tower or maze wall.');
    if(!inside(s.map,p))return result(false,'outside','Place the structure inside the grid.');
    if((s.map.blocked||[]).some(p=>p.x===cx&&p.z===cz))return result(false,'wall','Raised cliffs and the central divider cannot be built on.');
    if((s.map.reserved||[]).some(p=>p.x===cx&&p.z===cz))return result(false,'reserved','Entrances, route turns and ships must stay open.');
    if(slotAt(s.map,cx,cz)!==playerId)return result(false,'territory','Build inside the selected builder’s defense sector.');
    if(s.towers.some(t=>t.cx===cx&&t.cz===cz))return result(false,'occupied','A structure already occupies this cell.');
    const site=cellToWorld(s.map,cx,cz);
    if(s.units.some(u=>u.alive&&!u.air&&Math.abs(u.x-site.x)<=.95+(u.boss?.8:.45)&&Math.abs(u.z-site.z)<=.95+(u.boss?.8:.45)))return result(false,'creep','A ground creep overlaps the structure footprint.');
    if(owner.gold<d.cost)return result(false,'gold',`This structure costs ${d.cost} gold.`,{cost:d.cost});
    const towers=[...s.towers,{kind,cx,cz,level:1,owner:playerId}],check=preflight(s.map,towers);
    if(!check.ok)return result(false,'blocked','Leave both teams’ ordered routes open to their ships.',{cost:d.cost,errors:check.errors});
    const routes={};for(const u of s.units){if(!u.alive||u.air)continue;const p=route(s.map,towers,{x:u.cx,z:u.cz},u.defendTeam,false,u.stage);if(!p)return result(false,'trapped','This would trap a ground creep.',{cost:d.cost});routes[u.id]=p;}
    return result(true,'ready','Placement is valid.',{cost:d.cost,routes});
  }
  function remaining(s,u) {let d=0,previous={x:u.x,z:u.z};for(let i=u.pathIndex;i<(u.path?.length||0);i++){const p=cellToWorld(s.map,u.path[i]);d+=Math.hypot(p.x-previous.x,p.z-previous.z);previous=p;}return d;}
  function reroute(s,routes=null){for(const u of s.units){if(!u.alive||u.air)continue;const p=routes?.[u.id]||route(s.map,s.towers,{x:u.cx,z:u.cz},u.defendTeam,false,u.stage);if(p){u.path=p;u.pathIndex=0;u.remaining=remaining(s,u);}}}
  function build(s,kind,cx,cz,playerId=s?.selectedSector??0) {
    const fit=canBuild(s,kind,cx,cz,playerId);if(!fit.ok)return fit;
    const owner=s.players[playerId],t={id:`wars-tower-${++s.idSeq}`,kind,cx,cz,level:1,spent:definitions[kind].cost,priority:'first',cooldown:0,owner:playerId,team:owner.team};
    owner.gold-=t.spent;s.towers.push(t);reroute(s,fit.routes);event(s,'built',{id:t.id,kind,cx,cz,owner:playerId,team:t.team,cost:t.spent,gold:owner.gold,ai:owner.ai});
    return result(true,'built',`${definitions[kind].name} constructed.`,{tower:t});
  }
  function ownedTower(s,id,playerId){if(!mutable(s))return result(false,'finished','The match has finished.');const t=s.towers.find(t=>t.id===id);if(!t)return result(false,'missing','Select a structure.');if(!player(s,playerId)||t.owner!==playerId)return result(false,'owner','Select the builder who owns this structure.');return {ok:true,tower:t,player:s.players[playerId]};}
  function upgrade(s,id,playerId=s?.selectedSector??0) {
    const fit=ownedTower(s,id,playerId);if(!fit.ok)return fit;const t=fit.tower,d=definitions[t.kind],v=stats(t);
    if(t.level>=d.levels.length)return result(false,'maximum','This structure is at its highest level.');
    if(fit.player.gold<v.upgradeCost)return result(false,'gold',`The upgrade costs ${v.upgradeCost} gold.`);
    const cost=v.upgradeCost;fit.player.gold-=cost;t.spent+=cost;t.level++;t.cooldown=Math.min(t.cooldown,stats(t).interval);event(s,'upgraded',{id,owner:t.owner,level:t.level,cost,gold:fit.player.gold});return result(true,'upgraded',`${d.name} upgraded to level ${t.level}.`,{tower:t,cost});
  }
  function sell(s,id,playerId=s?.selectedSector??0) {
    const fit=ownedTower(s,id,playerId);if(!fit.ok)return fit;const t=fit.tower,refund=Math.floor(t.spent*.7);s.towers.splice(s.towers.indexOf(t),1);fit.player.gold+=refund;reroute(s);event(s,'sold',{id,owner:t.owner,kind:t.kind,refund,gold:fit.player.gold});return result(true,'sold',`Structure sold for ${refund} gold.`,{refund});
  }
  function setPriority(s,id,priority,playerId=s?.selectedSector??0) {
    const fit=ownedTower(s,id,playerId);if(!fit.ok)return fit;if(!priorities.includes(priority))return result(false,'priority','Choose first, last, strongest or nearest.');fit.tower.priority=priority;event(s,'priority',{id,owner:playerId,priority});return result(true,'priority','Target priority changed.',{tower:fit.tower});
  }
  function send(s,kind,playerId=s?.selectedSector??0,count=1) {
    if(!mutable(s))return result(false,'finished','The match has finished.');if(s.phase!=='battle')return result(false,'preparation','Sending opens when preparation finishes.');
    const owner=player(s,playerId),d=sends[kind];if(!owner)return result(false,'player','Choose a valid sender.');if(!d)return result(false,'kind','Choose a creep to send.');if(!integer(count)||count<1||count>8)return result(false,'count','Send one to eight creeps at a time.');
    const outstanding=s.units.filter(u=>u.alive).length+s.spawnQueue.length;
    if(outstanding+count>240||s.units.filter(u=>u.alive&&u.sourcePlayer===playerId).length+s.spawnQueue.filter(u=>u.sourcePlayer===playerId).length+count>60)return result(false,'capacity','The battlefield send queue is full. Wait for creeps to clear.');
    const cost=d.cost*count;if(owner.gold<cost)return result(false,'gold',`This send costs ${cost} gold.`,{cost});
    owner.gold-=cost;owner.income+=d.income*count;const defendTeam=1-owner.team;
    let at=Math.max(s.elapsed+.05,...s.spawnQueue.filter(v=>v.defendTeam===defendTeam).map(v=>v.at+s.rules.spawnInterval));
    for(let i=0;i<count;i++){s.spawnQueue.push({at,kind,sourcePlayer:playerId,defendTeam});at+=s.rules.spawnInterval;}
    s.spawnQueue.sort((a,b)=>a.at-b.at||a.sourcePlayer-b.sourcePlayer);event(s,'sent',{kind,count,sourcePlayer:playerId,sourceTeam:owner.team,defendTeam,cost,incomeGain:d.income*count,income:owner.income,gold:owner.gold});
    return result(true,'sent',`${count} ${d.name}${count>1?'s':''} sent to the opposing team.`,{kind,count,cost,incomeGain:d.income*count,defendTeam});
  }
  function random(s){let x=s.seed;x^=x<<13;x^=x>>>17;x^=x<<5;s.seed=x>>>0;return s.seed/4294967296;}
  function spawnUnit(s,item) {
    const d=sends[item.kind],record=s.map.routes.find(r=>r.team===item.defendTeam),p=cellToWorld(s.map,record.spawn),hp=Math.max(1,Math.round(d.hp*s.rules.difficulty));
    const u={id:`wars-creep-${++s.idSeq}`,kind:item.kind,sourcePlayer:item.sourcePlayer,defendTeam:item.defendTeam,team:item.defendTeam,sector:item.defendTeam*3,x:p.x,z:p.z,cx:record.spawn.x,cz:record.spawn.z,hp,maxHp:hp,speed:d.speed,air:d.air,boss:d.boss,armor:d.armor,bounty:d.bounty,stage:0,path:route(s.map,s.towers,record.spawn,item.defendTeam,d.air,0),pathIndex:1,progress:0,remaining:0,alive:true,slowUntil:0,slowFactor:1,variant:Math.floor(random(s)*3)};
    u.remaining=remaining(s,u);s.units.push(u);event(s,'spawned',{id:u.id,kind:u.kind,sourcePlayer:u.sourcePlayer,defendTeam:u.defendTeam,air:u.air,boss:u.boss,hp:u.hp,armor:u.armor});
  }
  function moveUnit(s,u,dt) {
    if(u.slowUntil<=s.elapsed){u.slowUntil=0;u.slowFactor=1;}
    let budget=u.speed*(u.slowUntil>s.elapsed?u.slowFactor:1)*dt;
    while(budget>0&&u.pathIndex<u.path.length){const mark=u.path[u.pathIndex],target=cellToWorld(s.map,mark),dx=target.x-u.x,dz=target.z-u.z,distance=Math.hypot(dx,dz);
      if(distance<=budget+1e-9){u.x=target.x;u.z=target.z;u.progress+=distance;budget-=distance;u.stage=Math.max(u.stage,mark.stage??u.stage);u.pathIndex++;}
      else{u.x+=dx/distance*budget;u.z+=dz/distance*budget;u.progress+=budget;budget=0;}}
    const p=worldToCell(s.map,u.x,u.z);u.cx=p.x;u.cz=p.z;u.sector=slotAt(s.map,p.x,p.z)??u.defendTeam*3;u.remaining=remaining(s,u);
    if(u.pathIndex>=u.path.length){u.alive=false;u.endedAt=s.elapsed;const team=s.teams[u.defendTeam];team.leaks++;team.lives=Math.max(0,team.lives-1);event(s,'leaked',{id:u.id,defendTeam:u.defendTeam,sourcePlayer:u.sourcePlayer,boss:u.boss,lives:team.lives});
      if(team.lives<=0){s.winner=1-u.defendTeam;s.phase=s.winner===0?'won':'lost';s.timer=0;event(s,s.phase,{winner:s.winner,loser:u.defendTeam,teams:copy(s.teams)});}}
  }
  function targetCandidates(s,t,range) {
    const d=definitions[t.kind],p=cellToWorld(s.map,t.cx,t.cz),list=s.units.filter(u=>u.alive&&u.defendTeam===t.team&&(u.air?d.air:d.ground)&&Math.hypot(u.x-p.x,u.z-p.z)<=range+1e-9);
    list.sort((a,b)=>{let delta=t.priority==='last'?b.remaining-a.remaining:t.priority==='strong'?b.hp-a.hp:t.priority==='near'?Math.hypot(a.x-p.x,a.z-p.z)-Math.hypot(b.x-p.x,b.z-p.z):a.remaining-b.remaining;return delta||a.id.localeCompare(b.id);});return list;
  }
  function hit(s,t,u,damage) {
    if(!u.alive||u.defendTeam!==t.team)return;const amount=damage*100/(100+u.armor);u.hp=Math.max(0,u.hp-amount);const v=stats(t);
    if(v.slow){u.slowUntil=Math.max(u.slowUntil,s.elapsed+v.slowDuration);u.slowFactor=Math.min(u.slowFactor,v.slow);}
    if(u.hp<=0){u.alive=false;u.endedAt=s.elapsed;s.teams[t.team].kills++;s.players[t.owner].gold+=u.bounty;event(s,'killed',{id:u.id,towerId:t.id,owner:t.owner,team:t.team,defendTeam:u.defendTeam,bounty:u.bounty,gold:s.players[t.owner].gold});}
  }
  function attack(s,t,dt) {
    const v=stats(t);if(v.damage<=0)return;t.cooldown=Math.max(0,t.cooldown-dt);if(t.cooldown>1e-9)return;
    const target=targetCandidates(s,t,v.range)[0];if(!target)return;const origin=cellToWorld(s.map,t.cx,t.cz),visited=new Set();
    const shoot=(u,from,scale=1)=>{visited.add(u.id);s.shots.push({id:`wars-shot-${++s.idSeq}`,from:{x:from.x,y:from.y??2.6,z:from.z},to:{x:u.x,y:u.air?3.8:.8,z:u.z},kind:t.kind,ttl:.2,targetId:u.id,team:t.team,owner:t.owner});hit(s,t,u,v.damage*scale);};
    const location={x:target.x,z:target.z};shoot(target,origin);
    if(v.splash)for(const u of s.units)if(u.alive&&u.defendTeam===t.team&&!u.air&&u.id!==target.id&&Math.hypot(u.x-location.x,u.z-location.z)<=v.splash)hit(s,t,u,v.damage*.7);
    if(v.chain){let previous=location;for(let i=1;i<v.chain;i++){const next=s.units.filter(u=>u.alive&&u.defendTeam===t.team&&!visited.has(u.id)&&(u.air?definitions[t.kind].air:definitions[t.kind].ground)&&Math.hypot(u.x-previous.x,u.z-previous.z)<=v.chainRange).sort((a,b)=>Math.hypot(a.x-previous.x,a.z-previous.z)-Math.hypot(b.x-previous.x,b.z-previous.z)||a.id.localeCompare(b.id))[0];if(!next)break;const at={x:next.x,y:next.air?3.8:.8,z:next.z};shoot(next,previous,Math.pow(.8,i));previous=at;}}
    t.cooldown=v.interval;
  }
  function aiCandidates(s,id) {
    const sector=s.map.sectors.find(v=>v.id===id),record=s.map.routes.find(r=>r.team===Math.floor(id/3)),near=route(s.map,s.towers,record.spawn,record.team)||[],seen=new Set(),out=[];
    for(const p of near)for(const [dx,dz] of [[0,-1],[-1,0],[1,0],[0,1],[0,-2],[-2,0],[2,0],[0,2]]){const cx=p.x+dx,cz=p.z+dz,k=key(cx,cz);if(!seen.has(k)&&slotAt(s.map,cx,cz)===id){seen.add(k);out.push({cx,cz});}}
    // Prefer rearward positions in each territory; the first route segment has
    // room for a human maze instead of a guaranteed block at the entrance.
    return out.reverse().filter(p=>p.cx>=sector.minX&&p.cx<=sector.maxX);
  }
  function aiTurn(s,p) {
    if(!p.ai)return;
    if(s.elapsed+1e-9>=p.nextDecision){p.nextDecision=s.elapsed+5+(p.id%3)*.3;const own=s.towers.filter(t=>t.owner===p.id),budget=p.gold;
      const upgradeable=own.filter(t=>t.level<definitions[t.kind].levels.length&&t.kind!=='maze-wall').sort((a,b)=>a.level-b.level||a.id.localeCompare(b.id));
      if(own.length>=4&&upgradeable.length&&budget>stats(upgradeable[0]).upgradeCost+60)upgrade(s,upgradeable[0].id,p.id);
      else if(own.length<6){const kind=['arrow','frost','cannon','storm','arrow','storm'][own.length];if(budget>=definitions[kind].cost+(s.phase==='battle'?40:0))for(const pos of aiCandidates(s,p.id)){if(build(s,kind,pos.cx,pos.cz,p.id).ok)break;}}
    }
    if(s.phase==='battle'&&s.elapsed+1e-9>=p.nextSend){p.nextSend=s.elapsed+Math.max(3,9/s.rules.difficulty)+(p.id%3)*.35;
      const battleTime=s.elapsed-s.rules.preparation,kind=battleTime>100&&p.gold>=190?'siege':battleTime>50&&p.gold>=100?'flyer':battleTime>25&&p.gold>=70?'brute':'wisp';
      const reserve=s.towers.filter(t=>t.owner===p.id).length<4?45:15;
      const count=Math.min(3,Math.floor((p.gold-reserve)/sends[kind].cost));if(count>0)send(s,kind,p.id,count);
    }
  }
  function tick(s,dt) {
    if(!mutable(s)||!Number.isFinite(dt)||dt<=0)return status(s);let left=Math.min(dt,1);
    while(left>1e-9&&mutable(s)){const step=Math.min(.05,left);left-=step;s.elapsed+=step;s.shots=s.shots.filter(v=>(v.ttl-=step)>0);s.units=s.units.filter(u=>u.alive||s.elapsed-(u.endedAt??s.elapsed)<1.2);
      s.incomeTimer-=step;if(s.incomeTimer<=1e-9){s.incomeTimer+=s.rules.incomeInterval;for(const p of s.players){p.gold+=p.income;event(s,'income-paid',{player:p.id,team:p.team,amount:p.income,gold:p.gold,income:p.income});}}
      if(s.phase==='preparation'){s.timer=Math.max(0,s.timer-step);if(s.timer<=1e-9){s.timer=0;s.phase='battle';event(s,'battle-started',{teams:2,players:6});}}
      for(const p of s.players)aiTurn(s,p);
      if(s.phase!=='battle')continue;
      while(s.spawnQueue.length&&s.spawnQueue[0].at<=s.elapsed+1e-9)spawnUnit(s,s.spawnQueue.shift());
      for(const u of s.units){if(u.alive)moveUnit(s,u,step);if(!mutable(s))break;}if(!mutable(s))break;
      for(const t of s.towers)attack(s,t,step);
    }
    return status(s);
  }
  function status(s) {
    if(!s)return null;const selected=player(s,s.selectedSector)||s.players[0],team=s.teams[selected.team],enemy=s.teams[1-selected.team];
    return {elapsed:s.elapsed,phase:s.phase,winner:s.winner,timer:s.timer,incomeTimer:s.incomeTimer,selectedSector:selected.id,gold:selected.gold,income:selected.income,lives:team.lives,enemyLives:enemy.lives,kills:team.kills,leaks:team.leaks,creeps:s.units.filter(u=>u.alive).length,queued:s.spawnQueue.length,towers:s.towers.length,playerTowers:s.towers.filter(t=>t.owner===selected.id).length,allyTowers:s.towers.filter(t=>t.team===selected.team&&t.owner!==selected.id).length,enemyTowers:s.towers.filter(t=>t.team!==selected.team).length};
  }
  return Object.freeze({defaults,definitions,priorities,sends,cleanRules,validateRules,mapDefault,worldToCell,cellToWorld,path,route,slotAt,preflight,createSession,canBuild,build,upgrade,sell,setPriority,send,tick,status,stats});
})();
// MAUL_WARS_CORE_END
