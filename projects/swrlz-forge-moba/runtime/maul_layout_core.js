// Classic cooperative Maul terrain and downstream defender layout. Combat and
// construction continue to use the published, deterministic Maul simulation.
const MAUL_LAYOUT_CORE = (() => {
  const copy = value => JSON.parse(JSON.stringify(value));
  const downstream = Object.freeze({
    0:Object.freeze([0,3,'westEntry','westOuter',6,'westReturn',7]),
    1:Object.freeze([1,4,3,'westEntry','westOuter',6,'westReturn',7]),
    2:Object.freeze([2,5,'eastEntry','eastOuter',8,'eastReturn',7]),
    3:Object.freeze([3,'westEntry','westOuter',6,'westReturn',7]),
    4:Object.freeze([4,5,'eastEntry','eastOuter',8,'eastReturn',7]),
    5:Object.freeze([5,'eastEntry','eastOuter',8,'eastReturn',7]),
    6:Object.freeze(['westOuter',6,'westReturn',7]),7:Object.freeze([7]),
    8:Object.freeze(['eastOuter',8,'eastReturn',7])
  });
  const defaultTurns=Object.freeze({westEntry:Object.freeze({x:4,z:31}),westOuter:Object.freeze({x:6,z:38}),westReturn:Object.freeze({x:15,z:33}),eastEntry:Object.freeze({x:36,z:31}),eastOuter:Object.freeze({x:34,z:38}),eastReturn:Object.freeze({x:25,z:33})});
  const pieces = [];
  const rectangle = (name,minX,maxX,minZ,maxZ,kind='cliff') => pieces.push({name,cx:(minX+maxX)/2,cz:(minZ+maxZ)/2,width:maxX-minX+1,depth:maxZ-minZ+1,kind});
  rectangle('West snowbank',0,1,0,44);
  rectangle('East snowbank',39,40,0,44);
  rectangle('Northern ridge',2,38,0,1);
  rectangle('North west dividing ridge',12,14,2,19);
  rectangle('North east dividing ridge',26,28,2,19);
  rectangle('West lower ridge crown',5,15,27,27);
  rectangle('East lower ridge crown',25,35,27,27);
  rectangle('West outside ridge',5,7,28,31);
  rectangle('East outside ridge',33,35,28,31);
  rectangle('West inside ridge upper step',13,15,28,29);
  rectangle('East inside ridge upper step',25,27,28,29);
  rectangle('West inside ridge middle step',14,16,30,30);
  rectangle('East inside ridge middle step',24,26,30,30);
  rectangle('West inside ridge lower step',15,17,31,31);
  rectangle('East inside ridge lower step',23,25,31,31);
  rectangle('West harbor coast',2,17,42,44,'coast');
  rectangle('East harbor coast',23,38,42,44,'coast');
  const records = [
    {id:0,name:'North West',bounds:[2,11,2,20],spawn:[7,3],gate:[7,21]},
    {id:1,name:'North Heart',bounds:[15,25,2,20],spawn:[20,3],gate:[20,21]},
    {id:2,name:'North East',bounds:[29,38,2,20],spawn:[33,3],gate:[33,21]},
    {id:3,name:'Crossbar West',bounds:[2,13,22,26],spawn:[3,24],gate:[8,26]},
    {id:4,name:'Crossbar Heart',bounds:[14,26,22,26],spawn:[20,23],gate:[20,26]},
    {id:5,name:'Crossbar East',bounds:[27,38,22,26],spawn:[37,24],gate:[32,26]},
    {id:6,name:'Lower West',bounds:[2,16,28,39],spawn:[4,33],gate:[10,39]},
    {id:7,name:'Rear Catcher',bounds:[17,23,31,41],spawn:[20,34],gate:[20,41]},
    {id:8,name:'Lower East',bounds:[24,38,28,39],spawn:[36,33],gate:[30,39]}
  ];
  const geometry = () => copy(pieces);
  const objectives=(map,sector)=>[...(map.sectors||[]).find(record=>record.id===sector)?.gates||[],map.exit];
  function withGates(map) {
    const byId = new Map((map.sectors||[]).map(sector=>[sector.id,sector]));
    map.turns={...copy(defaultTurns),...map.turns};
    for(const sector of map.sectors||[])sector.gates=(downstream[sector.id]||[]).map(id=>typeof id==='number'?byId.get(id)?.gate:map.turns[id]).filter(Boolean).map(gate=>({...gate}));
    const unique = new Map();
    for(const p of [...(map.spawns||[]),...(map.sectors||[]).map(sector=>sector.gate),...Object.values(map.turns),map.exit])if(p)unique.set(`${p.x},${p.z}`,{x:p.x,z:p.z});
    map.reserved=[...unique.values()];return map;
  }
  function mapDefault() {
    const blocked = new Map();
    for(const piece of pieces)for(let z=piece.cz-(piece.depth-1)/2;z<=piece.cz+(piece.depth-1)/2;z++)for(let x=piece.cx-(piece.width-1)/2;x<=piece.cx+(piece.width-1)/2;x++)blocked.set(`${x},${z}`,{x,z});
    const sectors=records.map(record=>({id:record.id,name:record.name,minX:record.bounds[0],maxX:record.bounds[1],minZ:record.bounds[2],maxZ:record.bounds[3],spawn:{x:record.spawn[0],z:record.spawn[1]},gate:{x:record.gate[0],z:record.gate[1]},focus:{x:(record.bounds[0]+record.bounds[1])/2,z:(record.bounds[2]+record.bounds[3])/2}}));
    return withGates({layout:'classic-v2',cols:41,rows:45,cell:2,origin:{x:-40,z:-44},blocked:[...blocked.values()],reserved:[],spawns:sectors.map(sector=>({...sector.spawn,sector:sector.id})),sectors,exit:{x:20,z:43}});
  }
  function route(map,blocked,start,sector,air=false,stage=0) {
    const cursor={x:Number(start?.x??start?.cx),z:Number(start?.z??start?.cz)},points=objectives(map,sector);
    stage=Math.max(0,Math.min(points.length,Number.isInteger(stage)?stage:0));
    const joined=[{...cursor,stage}];let from=cursor;
    for(let index=stage;index<points.length;index++){
      const target=points[index];if(!target)return null;
      if(air){joined.push({...target,stage:index+1});from=target;continue;}
      const part=MAUL_CORE.path(map,blocked,from,target);if(!part)return null;
      if(part.length===1)joined[joined.length-1].stage=index+1;
      else joined.push(...part.slice(1).map((p,i)=>({...p,stage:i===part.length-2?index+1:index})));
      from=target;
    }
    return joined;
  }
  function preflight(map=mapDefault(),towers=[]) {
    const check=MAUL_CORE.preflight(map,towers),errors=[...check.errors];
    const sectors=Array.isArray(map?.sectors)?map.sectors:[],ids=new Set(sectors.map(sector=>sector.id));
    if(sectors.length!==9||ids.size!==9||[...ids].some(id=>!Number.isInteger(id)||id<0||id>8))errors.push('The classic Maul layout needs nine uniquely numbered defender sectors.');
    for(const sector of sectors){
      const points=sector.gates||[];
      if(points.length!==(downstream[sector.id]?.length||0))errors.push(`Sector ${sector.id+1} must keep its ordered downstream defender waypoints.`);
      for(let i=0;i<points.length;i++){const ref=downstream[sector.id]?.[i],target=typeof ref==='number'?sectors.find(record=>record.id===ref)?.gate:map.turns?.[ref];if(!target||points[i].x!==target.x||points[i].z!==target.z)errors.push(`Sector ${sector.id+1} has a waypoint outside its downstream defender chain.`);}
      for(const point of points)if(!Number.isInteger(point.x)||!Number.isInteger(point.z)||point.x<0||point.x>=map.cols||point.z<0||point.z>=map.rows)errors.push(`Sector ${sector.id+1} has a waypoint outside the map grid.`);
      if(!route(map,towers,sector.spawn,sector.id))errors.push(`Sector ${sector.id+1} has no route around its ordered lower ridge turns.`);
    }
    return {...check,ok:errors.length===0,errors};
  }
  function createSession({rules={},map=mapDefault(),towers=[]}={}) {
    const check=preflight(map,towers);if(!check.ok)throw new Error(check.errors.join(' '));
    return MAUL_CORE.createSession({rules,map,towers});
  }
  return Object.freeze({...MAUL_CORE,downstream,geometry,withGates,mapDefault,route,preflight,createSession});
})();
// MAUL_LAYOUT_CORE_END
