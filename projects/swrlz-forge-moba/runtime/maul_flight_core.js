// Frostveil flying construction primitives; independent of rendering and old walk-v1 saves.
const MAUL_FLIGHT_CORE=(()=>{
  const HEIGHT=3.25,SPEED=15;
  const inside=(map,p)=>Number.isInteger(p?.x)&&Number.isInteger(p?.z)&&p.x>=0&&p.z>=0&&p.x<map.cols&&p.z<map.rows;
  const allowed=(map,p,sector)=>inside(map,p)&&MAUL_BUILDER_CORE.insideSector(map,p,sector);
  function plan(map,start,site,sector){
    if(!allowed(map,site,sector))return {ok:false,reason:'Select a cell inside your defense territory.'};
    if(MAUL_BUILDER_CORE.protectedSpawn(map,site))return {ok:false,reason:'Enemy entrance pads are no-build zones.'};
    return {ok:true,destination:{x:site.x,z:site.z},path:[{x:start.x,z:start.z},{x:site.x,z:site.z}]};
  }
  function travel(from,to,dt,speed=SPEED){
    const dx=to.x-from.x,dz=to.z-from.z,distance=Math.hypot(dx,dz);
    if(distance<=.15)return {x:to.x,z:to.z,arrived:true};
    const budget=Math.min(distance,Math.max(0,dt)*Math.max(0,speed)),ratio=budget/distance;
    return {x:from.x+dx*ratio,z:from.z+dz*ratio,arrived:budget>=distance-.15};
  }
  return Object.freeze({HEIGHT,SPEED,inside,allowed,plan,travel});
})();
// MAUL_FLIGHT_CORE_END
