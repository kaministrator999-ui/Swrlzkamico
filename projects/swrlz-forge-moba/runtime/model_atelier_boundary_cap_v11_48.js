// §E v11.48: explicit conservative planar boundary-hole fill on a BAKED
// indexed topology mesh. Not a generalized mesh healer. Only one uniquely
// traceable, simple, nearly planar boundary ring is capped; everything else
// is unchanged until atomic user Apply with native Undo/Redo.
function atelierBoundaryCapCandidate(part,startVertex){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
  return {ok:false,reason:'Select a saved indexed topology mesh'};
 const src=part.topologyMesh,audit=atelierTopologyAudit(src);
 if(!audit.ok||audit.nonManifoldEdges||audit.zeroAreaFaces||
    audit.oppositeWindingErrors)
  return {ok:false,reason:'Repair requires nondegenerate consistently wound manifold source faces'};
 const n=src.positions.length/3;
 if(!Number.isInteger(startVertex)||startVertex<0||startVertex>=n)
  return {ok:false,reason:'Choose an existing boundary vertex index'};
 const out=new Map(),inCount=new Map(),boundary=new Set();
 for(const edges of audit.edges.values()){
  if(edges.length!==1)continue;
  const e=edges[0];
  // The new cap must traverse each exposed edge opposite to its
  // sole existing incident triangle.
  const from=e.to,to=e.from;
  boundary.add(from);boundary.add(to);
  if(out.has(from))return {ok:false,reason:'Branching boundary vertex: cannot isolate one simple loop'};
  out.set(from,to);inCount.set(to,(inCount.get(to)||0)+1);
 }
 if(!out.has(startVertex))
  return {ok:false,reason:'Vertex is not on a boundary edge'};
 if([...boundary].some(i=>!out.has(i)||inCount.get(i)!==1))
  return {ok:false,reason:'Open or branching boundaries require manual repair before capping'};
 const ring=[],seen=new Set();let current=startVertex;
 for(let k=0;k<=256;k++){
  if(seen.has(current))break;
  seen.add(current);ring.push(current);
  current=out.get(current);
  if(current===undefined)return {ok:false,reason:'Dangling boundary arc'};
 }
 if(current!==startVertex||ring.length<3||ring.length>256)
  return {ok:false,reason:'Selected boundary must be one closed 3–256-vertex ring'};
 // All distinct indices on this ring must be spatially distinct.
 const coord=i=>src.positions.slice(i*3,i*3+3);
 const ps=ring.map(coord),centroid=[0,1,2].map(j=>ps.reduce((sum,p)=>sum+p[j],0)/ps.length);
 const mag=v=>Math.hypot(...v);
 const norm=[0,0,0],cross=(a,b)=>[
  a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 const dot=(a,b)=>a.reduce((sum,v,i)=>sum+v*b[i],0);
 for(let i=0;i<ps.length;i++){
  const p=ps[i],q=ps[(i+1)%ps.length];
  norm[0]+=(p[1]-q[1])*(p[2]+q[2]);
  norm[1]+=(p[2]-q[2])*(p[0]+q[0]);
  norm[2]+=(p[0]-q[0])*(p[1]+q[1]);
 }
 const len=mag(norm);
 if(len<1e-9)return {ok:false,reason:'Boundary has no stable planar normal'};
 const N=norm.map(v=>v/len);
 const diagonal=mag([0,1,2].map(j=>Math.max(...ps.map(p=>p[j]))-Math.min(...ps.map(p=>p[j]))));
 const tolerance=Math.max(1e-6,diagonal*.005);
 if(ps.some(p=>Math.abs(dot(p.map((v,j)=>v-centroid[j]),N))>tolerance))
  return {ok:false,reason:'Boundary is nonplanar; controlled surface patching required'};
 let basis=null,best=0;
 for(let i=0;i<ps.length;i++){
  const d=ps[(i+1)%ps.length].map((v,j)=>v-ps[i][j]);
  const projected=d.map((v,j)=>v-N[j]*dot(d,N));
  const l=mag(projected);
  if(l>best){best=l;basis=projected.map(v=>v/l);}
 }
 if(best<=1e-8)return {ok:false,reason:'Boundary edges collapse to one point'};
 const V=cross(N,basis),poly=ps.map(p=>{
  const d=p.map((v,j)=>v-centroid[j]);
  return [dot(d,basis),dot(d,V)];
 });
 const orient=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 const area=poly.reduce((sum,p,i)=>sum+p[0]*poly[(i+1)%poly.length][1]-
  poly[(i+1)%poly.length][0]*p[1],0)/2;
 if(Math.abs(area)<1e-10)return {ok:false,reason:'Boundary projects to zero surface area'};
 const sign=Math.sign(area),EPS=Math.max(1e-12,Math.abs(area)*1e-10);
 for(let i=0;i<poly.length;i++)
  for(let j=i+1;j<poly.length;j++)
   if((poly[i][0]-poly[j][0])**2+(poly[i][1]-poly[j][1])**2<EPS*EPS)
    return {ok:false,reason:'Overlapping boundary points'};
 const onSegment=(a,b,c)=>Math.min(a[0],b[0])-EPS<=c[0]&&
  c[0]<=Math.max(a[0],b[0])+EPS&&Math.min(a[1],b[1])-EPS<=c[1]&&
  c[1]<=Math.max(a[1],b[1])+EPS;
 const segmentsIntersect=(a,b,c,d)=>{
  const x=orient(a,b,c),y=orient(a,b,d),z=orient(c,d,a),w=orient(c,d,b);
  return (x*y<-EPS&&z*w<-EPS)||
   (Math.abs(x)<EPS&&onSegment(a,b,c))||
   (Math.abs(y)<EPS&&onSegment(a,b,d))||
   (Math.abs(z)<EPS&&onSegment(c,d,a))||
   (Math.abs(w)<EPS&&onSegment(c,d,b));
 };
 for(let i=0;i<ring.length;i++)for(let j=i+1;j<ring.length;j++){
  if(i===j||(i+1)%ring.length===j||(j+1)%ring.length===i)continue;
  if(segmentsIntersect(poly[i],poly[(i+1)%ring.length],
    poly[j],poly[(j+1)%ring.length]))
   return {ok:false,reason:'Self-intersecting boundary cannot be triangulated safely'};
 }
 const remaining=Array.from({length:ring.length},(_,i)=>i),triangles=[];
 const inside=(a,b,c,p)=>{
  const x=orient(a,b,p)*sign,y=orient(b,c,p)*sign,z=orient(c,a,p)*sign;
  return x>=-EPS&&y>=-EPS&&z>=-EPS;
 };
 while(remaining.length>3){
  let clipped=false;
  for(let i=0;i<remaining.length;i++){
   const prev=remaining[(i+remaining.length-1)%remaining.length],
     here=remaining[i],next=remaining[(i+1)%remaining.length];
   const A=poly[prev],B=poly[here],C=poly[next];
   if(orient(A,B,C)*sign<=EPS)continue;
   if(remaining.some(id=>id!==prev&&id!==here&&id!==next&&
     inside(A,B,C,poly[id])))continue;
   triangles.push(ring[prev],ring[here],ring[next]);
   remaining.splice(i,1);clipped=true;break;
  }
  if(!clipped)return {ok:false,reason:'No nondegenerate ear found for boundary'};
 }
 triangles.push(...remaining.map(i=>ring[i]));
 const result={positions:src.positions.slice(),uvs:src.uvs.slice(),
  indices:[...src.indices,...triangles]};
 if(result.indices.length/3>atelierLODSavedTriangles||
   !atelierTopologyValid({kind:'topologyMesh',topologyMesh:result}))
  return {ok:false,reason:'Capped mesh exceeds native topology budget'};
 const after=atelierTopologyAudit(result);
 if(!after.ok||after.zeroAreaFaces||after.nonManifoldEdges||
   after.oppositeWindingErrors||after.boundaryEdges!==audit.boundaryEdges-ring.length)
  return {ok:false,reason:'Proposed cap would compromise topology or edge winding'};
 // A cap is not a meaningful closed surface if it only creates a
 // coincident double-sided plane; reject zero-volume completions.
 if(after.boundaryEdges===0){
  let volume=0;
  for(let i=0;i<result.indices.length;i+=3){
   const [a,b,c]=result.indices.slice(i,i+3).map(coord);
   volume+=dot(a,cross(b,c))/6;
  }
  if(Math.abs(volume)<1e-9)
   return {ok:false,reason:'Mesh would be zero volume after closure'};
 }
 return {ok:true,data:result,startVertex,boundaryVertices:ring.length,
   addedTriangles:triangles.length/3,before:audit,after,
   dropsRuntimeLOD:!!part.runtimeLOD};
}
let atelierBoundaryCapPreview=null;
function atelierBoundaryCapRefresh(){
 const part=partById(selection),pane=$m('BoundaryCapTools');
 if(!pane)return;
 pane.hidden=part?.kind!=='topologyMesh';
 if(part?.kind!=='topologyMesh'){atelierBoundaryCapPreview=null;return;}
 const audit=atelierTopologyAudit(part.topologyMesh);
 $m('BoundaryCapStatus').textContent=audit.boundaryEdges+
  ' exposed edges. Choose an actual vertex index on one unbranched, nearly planar boundary ring. Only one ring is filled per Apply.';
}
function atelierBoundaryCapInstall(){
 const el=k=>$m('BoundaryCap'+k);
 el('Preview').addEventListener('click',()=>{
  const part=partById(selection),start=Number(el('Vertex').value);
  const result=atelierBoundaryCapCandidate(part,start);
  atelierBoundaryCapPreview=result.ok?{...result,id:part.id,
   baseline:JSON.stringify(part.topologyMesh)}:null;
  if(!result.ok){status('Hole-cap preview rejected: '+result.reason,true);return;}
  el('Status').textContent='Boundary loop '+result.boundaryVertices+
   ' vertices, +'+result.addedTriangles+' real triangles. Remaining open edges: '+
   result.after.boundaryEdges+'. '+(result.dropsRuntimeLOD?
    'Existing runtime LOD will be invalidated.':'')+' Original geometry unchanged.';
  status('Reviewed one planar hole cap; apply only after inspecting the target ring.');
 });
 el('Apply').addEventListener('click',()=>{
  const p=partById(selection),candidate=atelierBoundaryCapPreview;
  if(!candidate?.ok||!p||p.id!==candidate.id||
   JSON.stringify(p.topologyMesh)!==candidate.baseline){
   status('Preview the current unchanged boundary mesh before filling.',true);return;
  }
  const part={...p,topologyMesh:candidate.data};
  delete part.runtimeLOD;
  if(!checkPart(part)){status('Hole cap failed native import validation.',true);return;}
  checkpoint();p.topologyMesh=candidate.data;delete p.runtimeLOD;
  atelierBoundaryCapPreview=null;
  signalEdited();select(p.id);
  status('Filled one verified planar boundary loop with '+candidate.addedTriangles+
   ' actual triangles. Undo restores the open edge and any prior LOD.');
 });
}
