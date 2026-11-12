/* SE430_MODEL_MESH_OPERATIONS_START */
// Small, controlled topology operators. They build validated candidates only;
// document ownership, transient preview and native history belong to the bridge.
const se430MeshOps=(()=>{
 const MAX_VERTICES=9000,MAX_FACES=16000,EPS=1e-9;
 const fail=reason=>({ok:false,reason,error:reason});
 const add=(a,b)=>a.map((n,k)=>n+b[k]),sub=(a,b)=>a.map((n,k)=>n-b[k]);
 const mul=(a,s)=>a.map(n=>n*s),dot=(a,b)=>a.reduce((s,n,k)=>s+n*b[k],0);
 const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const length=a=>Math.hypot(...a),normalize=a=>mul(a,1/length(a));
 const key=(a,b)=>a<b?a+':'+b:b+':'+a;
 const point=(d,id)=>d.positions.slice(id*3,id*3+3);
 const uv=(d,id)=>d.uvs.slice(id*2,id*2+2);
 const face=(d,id)=>d.indices.slice(id*3,id*3+3);
 const copy=d=>({positions:[...d.positions],uvs:[...d.uvs],indices:[...d.indices]});
 function audit(data){
  if(!data||!Array.isArray(data.positions)||!Array.isArray(data.uvs)||!Array.isArray(data.indices)||
   data.positions.length<9||data.positions.length%3||data.positions.length>MAX_VERTICES*3||
   data.uvs.length!==data.positions.length/3*2||!data.indices.length||data.indices.length%3||data.indices.length>MAX_FACES*3||
   !data.positions.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=100)||
   !data.uvs.every(n=>typeof n==='number'&&Number.isFinite(n)&&Math.abs(n)<=20))return fail('The mesh exceeds native bounds or has invalid position/UV data.');
  const count=data.positions.length/3,edges=new Map(),seen=new Set();let zeroAreaFaces=0;
  for(let f=0;f<data.indices.length/3;f++){
   const ids=face(data,f);if(ids.some(id=>!Number.isInteger(id)||id<0||id>=count)||new Set(ids).size!==3)return fail('The mesh has invalid triangle indices.');
   const fkey=[...ids].sort((a,b)=>a-b).join(':');if(seen.has(fkey))return fail('The mesh has duplicate coincident triangles.');seen.add(fkey);
   const [a,b,c]=ids.map(id=>point(data,id));if(length(cross(sub(b,a),sub(c,a)))<EPS)zeroAreaFaces++;
   for(let i=0;i<3;i++){const from=ids[i],to=ids[(i+1)%3],k=key(from,to);if(!edges.has(k))edges.set(k,[]);edges.get(k).push({face:f,from,to});}
  }
  let boundaryEdges=0,nonManifoldEdges=0,oppositeWindingErrors=0;
  for(const list of edges.values()){
   if(list.length===1)boundaryEdges++;else if(list.length>2)nonManifoldEdges++;
   else if(list[0].from===list[1].from)oppositeWindingErrors++;
  }
  if(zeroAreaFaces||nonManifoldEdges||oppositeWindingErrors)return fail('Repair zero-area faces, nonmanifold edges or inconsistent winding before this operation.');
  return {ok:true,edges,vertices:count,faces:data.indices.length/3,boundaryEdges,nonManifoldEdges,oppositeWindingErrors,zeroAreaFaces};
 }
 function faceNormal(data,id){const p=face(data,id).map(i=>point(data,i));return cross(sub(p[1],p[0]),sub(p[2],p[0]));}
 function selected(data,ids){
  if(!Array.isArray(ids)||!ids.length||ids.length>MAX_FACES||ids.some(id=>!Number.isInteger(id)||id<0||id>=data.indices.length/3))return null;
  return [...new Set(ids)].sort((a,b)=>a-b);
 }
 function region(data,triangleIds,options={}){
  const source=audit(data);if(!source.ok)return source;
  let ids=selected(data,triangleIds);if(!ids)return fail('Select at least one valid face first.');
  const seed=ids[0],n=normalize(faceNormal(data,seed)),origin=point(data,face(data,seed)[0]);
  const all=Array.from({length:data.positions.length/3},(_,i)=>point(data,i));
  const size=[0,1,2].map(k=>Math.max(...all.map(p=>p[k]))-Math.min(...all.map(p=>p[k]))),tolerance=Math.max(1e-7,length(size)*1e-6);
  const planar=id=>dot(normalize(faceNormal(data,id)),n)>1-1e-6&&face(data,id).every(v=>Math.abs(dot(sub(point(data,v),origin),n))<=tolerance);
  if(ids.some(id=>!planar(id)))return fail('Select one planar face region. Curved or oppositely facing faces cannot share this preview.');
  const adjacency=new Map();for(const list of source.edges.values())if(list.length===2){
   const [a,b]=list.map(e=>e.face);if(!adjacency.has(a))adjacency.set(a,[]);if(!adjacency.has(b))adjacency.set(b,[]);adjacency.get(a).push(b);adjacency.get(b).push(a);
  }
  const wanted=new Set(ids),connected=new Set([seed]),queue=[seed];
  for(let i=0;i<queue.length;i++)for(const next of adjacency.get(queue[i])||[]){
   if(connected.has(next)||(!options.expand&&!wanted.has(next))||!planar(next))continue;connected.add(next);queue.push(next);
  }
  if(ids.some(id=>!connected.has(id)))return fail('Select one connected face region. Separate patches need separate operations.');
  ids=[...connected].sort((a,b)=>a-b);const set=new Set(ids),boundary=[];
  for(const list of source.edges.values()){
   const chosen=list.filter(e=>set.has(e.face));if(chosen.length===1)boundary.push(chosen[0]);
  }
  if(boundary.length<3)return fail('Select a surface face region with an outer edge, not the whole closed object.');
  const outgoing=new Map(),incoming=new Map();
  for(const edge of boundary){if(outgoing.has(edge.from))return fail('The selected region has a branching boundary.');outgoing.set(edge.from,edge.to);incoming.set(edge.to,(incoming.get(edge.to)||0)+1);}
  if([...outgoing.keys()].some(id=>incoming.get(id)!==1))return fail('The selected boundary is open or branching.');
  const loop=[],seen=new Set();let at=boundary[0].from;
  while(!seen.has(at)&&at!==undefined&&loop.length<=boundary.length){seen.add(at);loop.push(at);at=outgoing.get(at);}
  if(at!==loop[0]||loop.length!==boundary.length)return fail('Select one simple region without holes or separate boundary loops.');
  const points=loop.map(id=>point(data,id)),centroid=mul(points.reduce((s,p)=>add(s,p),[0,0,0]),1/points.length);
  const u=normalize(sub(points[1],points[0])),v=normalize(cross(n,u));
  const planarPoints=points.map(p=>[dot(sub(p,centroid),u),dot(sub(p,centroid),v)]);
  const orient=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  let polygonArea=0,convex=true;
  for(let i=0;i<planarPoints.length;i++){
   const a=planarPoints[i],b=planarPoints[(i+1)%points.length],c=planarPoints[(i+2)%points.length];
   polygonArea+=a[0]*b[1]-b[0]*a[1];if(orient(a,b,c)<-tolerance*tolerance)convex=false;
  }
  polygonArea/=2;const triangleArea=ids.reduce((sum,id)=>sum+length(faceNormal(data,id))*.5,0);
  if(polygonArea<=EPS||Math.abs(polygonArea-triangleArea)>Math.max(1e-8,triangleArea*1e-5))return fail('The selected faces overlap or do not form a simple filled region.');
  return {ok:true,triangleIds:ids,selectedFaces:ids,boundary:loop,normal:n,origin,centroid,convex,source,
   stats:{selectedFaces:ids.length,boundaryVertices:loop.length,area:triangleArea}};
 }
 function compact(data){
  const mapping=new Map(),positions=[],uvs=[],indices=[];
  for(const id of data.indices){if(!mapping.has(id)){mapping.set(id,mapping.size);positions.push(...point(data,id));uvs.push(...uv(data,id));}indices.push(mapping.get(id));}
  return {positions,uvs,indices};
 }
 function finish(before,data,selectedFaces,extra={}){
  const result=compact(data),checked=audit(result);if(!checked.ok)return checked;
  return {ok:true,data:result,selectedFaces,stats:{verticesBefore:before.vertices,verticesAfter:checked.vertices,facesBefore:before.faces,facesAfter:checked.faces,boundaryEdges:checked.boundaryEdges,...extra}};
 }
 function extract(data,r){
  const chosen=new Set(r.triangleIds),indices=[];for(let f=0;f<data.indices.length/3;f++)if(!chosen.has(f))indices.push(...face(data,f));
  return {positions:[...data.positions],uvs:[...data.uvs],indices};
 }
 function inset(data,triangleIds,options={}){
  const fraction=options.fraction??.2;if(typeof fraction!=='number'||!Number.isFinite(fraction)||fraction<.03||fraction>.8)return fail('Inset amount must be between 3% and 80% of this region.');
  const r=region(data,triangleIds);if(!r.ok)return r;if(!r.convex)return fail('Inset currently needs one convex planar region. Split a concave shape into simpler faces first.');
  const next=extract(data,r),used=[...new Set(r.triangleIds.flatMap(id=>face(data,id)))],mapping=new Map();
  const centerUV=mul(r.boundary.reduce((s,id)=>add(s,uv(data,id)),[0,0]),1/r.boundary.length);
  for(const id of used){mapping.set(id,next.positions.length/3);next.positions.push(...add(r.centroid,mul(sub(point(data,id),r.centroid),1-fraction)));next.uvs.push(...add(centerUV,mul(sub(uv(data,id),centerUV),1-fraction)));}
  for(let i=0;i<r.boundary.length;i++){const a=r.boundary[i],b=r.boundary[(i+1)%r.boundary.length],ap=mapping.get(a),bp=mapping.get(b);next.indices.push(a,b,bp,a,bp,ap);}
  const cap=[];for(const id of r.triangleIds){cap.push(next.indices.length/3);next.indices.push(...face(data,id).map(v=>mapping.get(v)));}
  const result=finish(r.source,next,cap,{operation:'inset',fraction});
  return result.ok&&result.stats.boundaryEdges!==r.source.boundaryEdges?fail('Inset changed the outer boundary unexpectedly.'):result;
 }
 function shiftedUV(data,r){
  const area=(a,b,c)=>Math.abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]));
  for(const shift of [[.013,.027],[.027,-.013],[.019,.043],[-.031,.017],[.037,.021],[.017,.049]]){
   const valid=r.boundary.every((id,i)=>{const a=uv(data,id),b=uv(data,r.boundary[(i+1)%r.boundary.length]),ap=add(a,shift),bp=add(b,shift);return [...ap,...bp].every(n=>Math.abs(n)<=20)&&area(a,b,bp)>1e-12&&area(a,bp,ap)>1e-12;});
   if(valid)return shift;
  }
  return null;
 }
 function clearance(data,r,direction){
  // Clip every other triangle against the convex region's footprint, rather
  // than sampling a few rays that could miss a small interior obstacle. The
  // axial depth is linear on each clipped polygon, so its extrema are at the
  // resulting vertices. A tiny inset excludes mere outer-edge contact.
  const selected=new Set(r.triangleIds),planes=r.boundary.map((id,i)=>{
   const origin=point(data,id),edge=sub(point(data,r.boundary[(i+1)%r.boundary.length]),origin);
   return {origin,inward:normalize(cross(r.normal,edge)),length:length(edge)};
  });
  const margin=Math.max(1e-10,Math.min(...planes.map(p=>p.length))*1e-7),depthEpsilon=1e-8;
  let nearest=Infinity,work=0;
  for(let id=0;id<data.indices.length/3;id++)if(!selected.has(id)){
   let polygon=face(data,id).map(v=>point(data,v));
   for(const plane of planes){
    if(!polygon.length)break;
    const next=[];let previous=polygon.at(-1),before=dot(sub(previous,plane.origin),plane.inward)-margin;
    for(const current of polygon){
     if(++work>2000000)return {budgetExceeded:true};
     const after=dot(sub(current,plane.origin),plane.inward)-margin;
     if((before>=0)!==(after>=0))next.push(add(previous,mul(sub(current,previous),before/(before-after))));
     if(after>=0)next.push(current);previous=current;before=after;
    }
    polygon=next;
   }
   if(!polygon.length)continue;
   const depths=polygon.map(p=>dot(sub(p,r.origin),direction)),min=Math.min(...depths),max=Math.max(...depths);
   if(max<=depthEpsilon)continue;
   nearest=Math.min(nearest,min<=depthEpsilon?depthEpsilon:min);
  }
  return {distance:nearest,budgetExceeded:false};
 }
 function overlappingBoundaryWall(data,r,direction){
  // Pulling an entire cube face inward without first forming a rim otherwise
  // adds sidewalls directly on top of its existing walls. Indexed manifold
  // checks alone cannot detect those coincident, oppositely facing surfaces.
  const chosen=new Set(r.triangleIds);
  return r.boundary.some((a,i)=>{
   const b=r.boundary[(i+1)%r.boundary.length],other=r.source.edges.get(key(a,b)).find(e=>!chosen.has(e.face));
   if(!other)return false;
   const normal=normalize(faceNormal(data,other.face));
   if(Math.abs(dot(normal,direction))>1e-7)return false;
   const third=face(data,other.face).find(id=>id!==a&&id!==b);
   return dot(sub(point(data,third),point(data,a)),direction)>1e-8;
  });
 }
 function extrude(data,triangleIds,options={}){
  const depth=options.depth??.15;if(typeof depth!=='number'||!Number.isFinite(depth)||Math.abs(depth)<.005||Math.abs(depth)>4)return fail('Extrusion depth must be a signed value from 0.005 to 4 local units.');
  const r=region(data,triangleIds);if(!r.ok)return r;if(!r.convex)return fail('Extrude currently needs one convex planar region.');
  if(r.boundary.some((a,i)=>r.source.edges.get(key(a,r.boundary[(i+1)%r.boundary.length])).length!==2))return fail('This region has open outer edges. Use Solidify to give a complete open surface thickness.');
  const direction=mul(r.normal,Math.sign(depth));
  if(overlappingBoundaryWall(data,r,direction))return fail('This extrusion would overlap an existing boundary wall. Inset first to create a rim, then extrude its selected inner face.');
  if((1+r.boundary.length+r.triangleIds.length)*(r.source.faces-r.triangleIds.length)>2000000)return fail('This dense region exceeds the interactive collision-check budget. Select a smaller face region or reduce the mesh density first.');
  const contact=clearance(data,r,direction);
  if(contact.budgetExceeded)return fail('This dense region exceeds the interactive collision-check budget. Select a smaller face region or reduce the mesh density first.');
  const distance=contact.distance;
  if(Number.isFinite(distance)&&Math.abs(depth)>=distance*.98)return fail('This extrusion would reach or pass another surface. Use a shallower depth to retain the container floor.');
  const shift=shiftedUV(data,r);if(!shift)return fail('The boundary UVs are collapsed. Convert a plain primitive or repair its UV mapping before extruding.');
  const next=extract(data,r),mapping=new Map(),used=[...new Set(r.triangleIds.flatMap(id=>face(data,id)))];
  for(const id of used){mapping.set(id,next.positions.length/3);next.positions.push(...add(point(data,id),mul(r.normal,depth)));next.uvs.push(...add(uv(data,id),shift));}
  for(let i=0;i<r.boundary.length;i++){const a=r.boundary[i],b=r.boundary[(i+1)%r.boundary.length],ap=mapping.get(a),bp=mapping.get(b);next.indices.push(a,b,bp,a,bp,ap);}
  const cap=[];for(const id of r.triangleIds){cap.push(next.indices.length/3);next.indices.push(...face(data,id).map(v=>mapping.get(v)));}
  const result=finish(r.source,next,cap,{operation:'extrude',depth,clearance:Number.isFinite(distance)?distance:null,capUVShift:[...shift]});
  return result.ok&&result.stats.boundaryEdges!==r.source.boundaryEdges?fail('Extrusion changed the outer boundary unexpectedly.'):result;
 }
 function deleteFaces(data,triangleIds){
  const source=audit(data);if(!source.ok)return source;const ids=selected(data,triangleIds);
  if(!ids)return fail('Select faces to delete.');if(ids.length===source.faces)return fail('Use Delete object to remove the entire mesh.');
  return finish(source,extract(data,{triangleIds:ids}),[],{operation:'delete-faces',deletedFaces:ids.length});
 }
 function solidify(data,triangleIds,options={}){
  const thickness=options.thickness??.1;if(typeof thickness!=='number'||!Number.isFinite(thickness)||thickness<.005||thickness>4)return fail('Thickness must be between 0.005 and 4 local units.');
  const r=region(data,triangleIds);if(!r.ok)return r;
  if(!r.convex||r.triangleIds.length!==r.source.faces||r.source.boundaryEdges!==r.boundary.length)return fail('Solidify currently needs one complete convex planar open surface. Select that surface, or use region Extrude on a closed mesh.');
  const shift=shiftedUV(data,r);if(!shift)return fail('This surface has collapsed boundary UVs; repair or reproject them before Solidify.');
  const next=copy(data),count=data.positions.length/3;next.indices=[];
  for(let id=0;id<count;id++){next.positions.push(...add(point(data,id),mul(r.normal,thickness)));next.uvs.push(...add(uv(data,id),shift));}
  for(let id=0;id<r.source.faces;id++){const [a,b,c]=face(data,id);next.indices.push(c,b,a);}
  for(let i=0;i<r.boundary.length;i++){const a=r.boundary[i],b=r.boundary[(i+1)%r.boundary.length];next.indices.push(a,b,b+count,a,b+count,a+count);}
  const cap=[];for(let id=0;id<r.source.faces;id++){cap.push(next.indices.length/3);next.indices.push(...face(data,id).map(v=>v+count));}
  const result=finish(r.source,next,cap,{operation:'solidify',thickness,capUVShift:[...shift]});
  return result.ok&&result.stats.boundaryEdges?fail('The solidified shell is not closed.'):result;
 }
 function convert(geometry){
  const p=geometry?.getAttribute?.('position'),index=geometry?.getIndex?.();
  if(!p||p.itemSize!==3||p.count<3||p.count>180000)return fail('Choose a bounded native primitive with position geometry.');
  if(geometry.getAttribute('skinIndex')||geometry.getAttribute('skinWeight')||geometry.getAttribute('color')||Object.keys(geometry.morphAttributes||{}).length)return fail('Skinned, morphed or vertex-painted geometry cannot use plain-mesh conversion.');
  const count=index?index.count:p.count;if(count%3||count>MAX_FACES*3)return fail('This primitive exceeds the editable triangle budget. Lower its density first.');
  const positions=[],uvs=[],indices=[],map=new Map(),remap=new Map();
  const boxMin=[Infinity,Infinity,Infinity],boxMax=[-Infinity,-Infinity,-Infinity];
  for(let id=0;id<p.count;id++)for(let k=0;k<3;k++){const n=k===0?p.getX(id):k===1?p.getY(id):p.getZ(id);if(!Number.isFinite(n)||Math.abs(n)>100)return fail('The primitive has invalid or out-of-bounds positions.');boxMin[k]=Math.min(boxMin[k],n);boxMax[k]=Math.max(boxMax[k],n);}
  const tolerance=Math.max(1e-9,length(sub(boxMax,boxMin))*1e-8);
  function vertex(id){
   if(!Number.isInteger(id)||id<0||id>=p.count)throw Error('invalid primitive index');if(remap.has(id))return remap.get(id);
   const values=[p.getX(id),p.getY(id),p.getZ(id)],k=values.map(n=>Math.round(n/tolerance)).join(':');
   if(!map.has(k)){map.set(k,positions.length/3);positions.push(...values);}remap.set(id,map.get(k));return remap.get(id);
  }
  try{for(let i=0;i<count;i+=3){const ids=[0,1,2].map(j=>vertex(index?index.getX(i+j):i+j));if(new Set(ids).size===3)indices.push(...ids);}}catch{return fail('The primitive has invalid triangle indices.');}
  if(positions.length/3>MAX_VERTICES)return fail('This primitive exceeds 9,000 editable vertices. Lower its density first.');
  const U=normalize([4,1,2]),V=normalize([-2,4,2]),projected=[];
  for(let id=0;id<positions.length/3;id++){const pt=positions.slice(id*3,id*3+3);projected.push([dot(pt,U),dot(pt,V)]);}
  const min=[0,1].map(k=>Math.min(...projected.map(p=>p[k]))),max=[0,1].map(k=>Math.max(...projected.map(p=>p[k])));
  for(const pt of projected)uvs.push(...pt.map((n,k)=>(n-min[k])/Math.max(1e-7,max[k]-min[k])));
  const data={positions,uvs,indices},checked=audit(data);if(!checked.ok)return checked;
  return {ok:true,data,selectedFaces:[],stats:{operation:'convert',sourceVertices:p.count,verticesAfter:positions.length/3,facesAfter:indices.length/3,boundaryEdges:checked.boundaryEdges,uvReprojected:true,weldTolerance:tolerance}};
 }
 return Object.freeze({region,inset,extrude,deleteFaces,solidify,convert,audit,limits:Object.freeze({vertices:MAX_VERTICES,faces:MAX_FACES})});
})();
/* SE430_MODEL_MESH_OPERATIONS_END */
