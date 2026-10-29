// Optional grouped arrivals for the cooperative Maul map. Scheduling, scatter
// and congestion handling are JSON-only so saved runs reproduce native Play.
const MAUL_BATCH_CORE = (() => {
  const profile='grouped-v1',groupInterval=2.5,groups=3;
  const key=p=>`${p.x},${p.z}`;
  const enabled=map=>map?.spawnStyle===profile;
  const radius=boss=>boss?.85:.5;
  const mapCaches=new WeakMap();
  function spawnCells(map,spawn) {
    const sector=(map.sectors||[]).find(s=>s.id===spawn?.sector);
    if(!sector||!Number.isInteger(spawn?.x)||!Number.isInteger(spawn?.z))return [];
    const walls=new Set((map.blocked||[]).map(key));
    const protectedCells=new Set([...(map.sectors||[]).map(s=>s.gate),...Object.values(map.turns||{}),map.exit].filter(Boolean).map(key)),cells=[];
    for(let z=spawn.z-2;z<=spawn.z+2;z++)for(let x=spawn.x-2;x<=spawn.x+2;x++){
      const p={x,z};
      if(x<0||z<0||x>=map.cols||z>=map.rows||x<sector.minX||x>sector.maxX||z<sector.minZ||z>sector.maxZ||walls.has(key(p))||protectedCells.has(key(p)))continue;
      cells.push(p);
    }
    return cells;
  }
  function reserveAreas(map) {
    if(!enabled(map))return map;
    const reserved=new Map((map.reserved||[]).map(p=>[key(p),{x:p.x,z:p.z}]));
    map.spawnAreas=(map.spawns||[]).map(spawn=>({sector:spawn.sector,cells:spawnCells(map,spawn)}));
    for(const area of map.spawnAreas)for(const p of area.cells)reserved.set(key(p),{...p});
    map.reserved=[...reserved.values()];return map;
  }
  function mapDefault(){return reserveAreas({...MAUL_LAYOUT_CORE.mapDefault(),spawnStyle:profile});}
  function gridCache(map,towers){
    const fingerprint=JSON.stringify([map.cols,map.rows,map.blocked,map.sectors,map.turns,map.exit,(towers||[]).map(t=>[t.cx??t.x,t.cz??t.z])]);
    let cache=mapCaches.get(map);if(cache?.fingerprint===fingerprint)return cache;
    const occupied=new Set((towers||[]).map(t=>`${t.cx??t.x},${t.cz??t.z}`)),walls=new Set([...(map.blocked||[]).map(key),...occupied]);
    const valid=Number.isInteger(map.cols)&&Number.isInteger(map.rows)&&map.cols>=3&&map.rows>=3&&map.cols<=100&&map.rows<=100;
    const components=new Int32Array(valid?map.cols*map.rows:0),queue=new Int32Array(components.length);let component=0;
    if(valid)for(let start=0;start<components.length;start++){
      if(components[start]||walls.has(`${start%map.cols},${Math.floor(start/map.cols)}`))continue;
      let head=0,tail=1;queue[0]=start;components[start]=++component;
      while(head<tail){const index=queue[head++],x=index%map.cols,z=Math.floor(index/map.cols);for(const [dx,dz]of [[0,1],[-1,0],[1,0],[0,-1]]){const nx=x+dx,nz=z+dz;if(nx<0||nz<0||nx>=map.cols||nz>=map.rows||walls.has(`${nx},${nz}`))continue;const next=nz*map.cols+nx;if(components[next])continue;components[next]=component;queue[tail++]=next;}}
    }
    cache={fingerprint,occupied,components,pools:new Map()};mapCaches.set(map,cache);return cache;
  }
  function candidates(map,towers,spawn,air=false){
    const cache=gridCache(map,towers),token=`${spawn.sector}:${spawn.x},${spawn.z}:${air}`;if(cache.pools.has(token))return cache.pools.get(token);
    // Native preflight verifies the spawn's ordered route. On this undirected
    // grid every cell in its connected component can use that route as well.
    const component=cache.components[spawn.z*map.cols+spawn.x],cells=spawnCells(map,spawn).filter(p=>!cache.occupied.has(key(p))&&(air||component>0&&cache.components[p.z*map.cols+p.x]===component));
    cache.pools.set(token,cells);return cells;
  }
  function preflight(map=mapDefault(),towers=[]) {
    const check=map?.layout==='classic-v2'?MAUL_LAYOUT_CORE.preflight(map,towers):MAUL_CORE.preflight(map,towers),errors=[...check.errors];
    if(enabled(map))for(const spawn of map.spawns||[])if(candidates(map,towers,spawn).length<6)errors.push(`Sector ${spawn.sector+1} needs at least six clear, routable cells in its scattered spawn area.`);
    return {...check,ok:errors.length===0,errors};
  }
  function createSession({rules={},map=mapDefault(),towers=[]}={}){
    const check=preflight(map,towers);if(!check.ok)throw new Error(check.errors.join(' '));
    return MAUL_CORE.createSession({rules,map,towers});
  }
  function schedule(s,count,air,boss) {
    const queue=[],base=Math.floor(count/groups),extra=count%groups;
    for(let g=0,index=0;g<groups;g++){
      const members=[],size=base+(g<extra?1:0);
      for(const spawn of s.map.spawns)for(let n=0;n<size;n++)members.push({sector:spawn.sector,spawn:{x:spawn.x,z:spawn.z},air:!!air,boss:!!boss&&index+n===count-1,index:index+n,group:g+1});
      queue.push({at:g*groupInterval,group:g+1,members});index+=size;
    }
    return queue;
  }
  function shuffled(cells,seed) {
    const result=cells.map(p=>({...p}));let state=(seed>>>0)||1;
    const next=()=>{state^=state<<13;state^=state>>>17;state^=state<<5;state>>>=0;return state/4294967296;};
    for(let i=result.length-1;i>0;i--){const j=Math.floor(next()*(i+1));[result[i],result[j]]=[result[j],result[i]];}
    return result;
  }
  function seedFor(s,group,sector){return ((s.rules.seed>>>0)^Math.imul(s.wave,0x9e3779b1)^Math.imul(group,0x85ebca6b)^Math.imul(sector+1,0xc2b2ae35))>>>0;}
  function placements(s,batch) {
    const pools=new Map(),chosen=[],live=s.units.filter(u=>u.alive);
    for(const item of batch.members){
      if(!pools.has(item.sector))pools.set(item.sector,shuffled(candidates(s.map,s.towers,{...item.spawn,sector:item.sector},item.air),seedFor(s,batch.group,item.sector)));
      const nearby=chosen.filter(p=>p.item.sector===item.sector),pool=pools.get(item.sector);let best=-1,score=-1;
      for(let i=0;i<pool.length;i++){
        const cell=pool[i],world=MAUL_CORE.cellToWorld(s.map,cell),clearance=radius(item.boss);
        if(live.some(u=>Math.hypot(u.x-world.x,u.z-world.z)<clearance+radius(u.boss)+.1)||chosen.some(p=>Math.hypot(p.world.x-world.x,p.world.z-world.z)<clearance+radius(p.item.boss)+.1))continue;
        const distance=nearby.length?Math.min(...nearby.map(p=>Math.hypot(p.world.x-world.x,p.world.z-world.z))):0;
        if(best<0||distance>score){best=i;score=distance;}
      }
      if(best<0)return null;
      const spawn=pool.splice(best,1)[0];chosen.push({item:{...item,spawn},world:MAUL_CORE.cellToWorld(s.map,spawn)});
    }
    return chosen.map(p=>p.item);
  }
  function queued(s){return (s.spawnQueue||[]).reduce((n,item)=>n+(Array.isArray(item.members)?item.members.length:1),0);}
  function allyProposals(s,sector,canBuild){
    const proposals=[],trial={...s,towers:[...s.towers]},cells=[];
    for(let z=sector.minZ;z<=sector.maxZ;z++)for(let x=sector.minX;x<=sector.maxX;x++)cells.push({x,z});
    cells.sort((a,b)=>Math.hypot(a.x-sector.gate.x,a.z-sector.gate.z)-Math.hypot(b.x-sector.gate.x,b.z-sector.gate.z)||a.z-b.z||a.x-b.x);
    for(const kind of ['arrow','storm'])for(const cell of cells){if(!canBuild(trial,kind,cell.x,cell.z).ok)continue;const p={kind,cx:cell.x,cz:cell.z};proposals.push(p);trial.towers.push({...p,level:1});break;}
    return proposals;
  }
  function spawnDue(s,spawnUnit,event) {
    let completed=0;
    while(s.spawnQueue.length&&s.spawnQueue[0].at<=s.waveElapsed+1e-9){
      const batch=s.spawnQueue[0],items=placements(s,batch);if(!items)break;
      // Resolve every position before mutating the queue or creating a unit.
      // A congested sector delays the whole group, with no partial arrivals.
      s.spawnQueue.shift();const members=[];
      for(const item of items){
        spawnUnit(s,item);const unit=s.units.at(-1),spawned=s.events.at(-1);
        unit.spawnGroup=batch.group;unit.spawnIndex=item.index;unit.spawnOrigin={...item.spawn};
        if(spawned?.type==='spawned'&&spawned.details?.id===unit.id)Object.assign(spawned.details,{group:batch.group,index:item.index,cx:item.spawn.x,cz:item.spawn.z});
        members.push({id:unit.id,sector:item.sector,index:item.index,cx:item.spawn.x,cz:item.spawn.z});
      }
      event(s,'spawn-group',{group:batch.group,at:batch.at,count:members.length,members});completed++;
    }
    return completed;
  }
  return Object.freeze({profile,groups,groupInterval,enabled,spawnCells,reserveAreas,mapDefault,preflight,createSession,schedule,queued,spawnDue,allyProposals});
})();
// MAUL_BATCH_CORE_END
