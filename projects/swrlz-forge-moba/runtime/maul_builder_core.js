// Maul builder orders: deterministic walk-to-build planning, independent of Three.js.
// Towers provide the actual maze footprint; existing historic maze walls stay readable.
const MAUL_BUILDER_CORE=(()=>{
  const key=p=>p.x+','+p.z;
  const blocked=(map,towers)=>new Set([...(map.blocked||[]).map(key),...towers.map(t=>key({x:t.cx,z:t.cz}))]);
  const inside=(map,p)=>Number.isInteger(p.x)&&Number.isInteger(p.z)&&p.x>=0&&p.z>=0&&p.x<map.cols&&p.z<map.rows;
  const insideSector=(map,p,sector)=>{
    const s=map.sectors?.find(s=>s.id===sector);
    return !!s&&p.x>=s.minX&&p.x<=s.maxX&&p.z>=s.minZ&&p.z<=s.maxZ;
  };
  const protectedSpawn=(map,p)=>{
    if((map.reserved||[]).some(c=>c.x===p.x&&c.z===p.z))return true;
    const areas=map.spawnAreas||[];
    if(areas.some(a=>a.cells?.some(c=>c.x===p.x&&c.z===p.z)))return true;
    // Protect the full actual 5-by-5 entrance pad, even on older maps
    // whose spawnAreas haven't yet been populated by the grouped scheduler.
    return (map.spawns||[]).some(s=>Math.abs(s.x-p.x)<=2&&Math.abs(s.z-p.z)<=2&&insideSector(map,p,s.sector));
  };
  function plan(map,towers,start,site,sector){
    if(!inside(map,site)||!insideSector(map,site,sector))return {ok:false,reason:'Build inside your selected defense sector.'};
    if(protectedSpawn(map,site))return {ok:false,reason:'Enemy entrance pads are no-build zones.'};
    const used=blocked(map,towers);
    const options=[[0,-1],[-1,0],[1,0],[0,1]].map(([dx,dz])=>({x:site.x+dx,z:site.z+dz}))
      .filter(p=>inside(map,p)&&insideSector(map,p,sector)&&!used.has(key(p)));
    const routes=options.map(destination=>({destination,path:MAUL_CORE.path(map,towers,start,destination)}))
      .filter(x=>x.path?.length).sort((a,b)=>a.path.length-b.path.length||a.destination.z-b.destination.z||a.destination.x-b.destination.x);
    if(!routes.length)return {ok:false,reason:'The builder cannot reach a clear side of this tower.'};
    return {ok:true,...routes[0]};
  }
  return Object.freeze({plan,protectedSpawn,insideSector});
})();
