// §E v11.50 — explicit face-local indexed triangle extrusion/intrusion.
// Only a single triangular face with three two-sided manifold edges may be
// moved, forming three stitched side quads. No blind procedural rebuild.
function atelierFaceExtrudeCandidate(part,faceIndex,distance){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
  return {ok:false,reason:'Select a separately baked indexed mesh'};
 const t=part.topologyMesh,total=t.indices.length/3;
 if(!Number.isInteger(faceIndex)||faceIndex<0||faceIndex>=total||
   !Number.isFinite(distance)||Math.abs(distance)<.005||Math.abs(distance)>.4)
  return {ok:false,reason:'Choose valid face and signed extrusion ±0.005–0.4'};
 if(total+6>atelierLODSavedTriangles||t.positions.length/3+3>atelierLODSavedVertices)
  return {ok:false,reason:'Portable mobile indexed triangle budget exceeded'};
 const audit=atelierTopologyAudit(t);
 if(!audit.ok||audit.nonManifoldEdges||audit.zeroAreaFaces||
   audit.oppositeWindingErrors)
  return {ok:false,reason:'A malformed, nonmanifold or inconsistent source cannot be extruded'};
 const ids=t.indices.slice(faceIndex*3,faceIndex*3+3);
 const key=(a,b)=>a<b?a+':'+b:b+':'+a;
 for(let e=0;e<3;e++){
  const incidents=audit.edges.get(key(ids[e],ids[(e+1)%3]));
  if(incidents?.length!==2)
   return {ok:false,reason:'Selected face touches a boundary or unattached edge; repair it first'};
 }
 const p=ids.map(i=>t.positions.slice(i*3,i*3+3));
 const ab=p[1].map((v,k)=>v-p[0][k]),ac=p[2].map((v,k)=>v-p[0][k]);
 const cross=(u,v)=>[u[1]*v[2]-u[2]*v[1],
  u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
 const normal=cross(ab,ac),norm=Math.hypot(...normal);
 if(norm<1e-9)return {ok:false,reason:'Selected triangle has zero area'};
 const sideLengths=[0,1,2].map(i=>
  Math.hypot(...p[i].map((v,k)=>v-p[(i+1)%3][k])));
 if(Math.abs(distance)>Math.min(...sideLengths)*.6)
  return {ok:false,reason:'Extrusion would exceed 60% of shortest face edge: subdivide region first'};
 const n=normal.map(v=>v/norm),old=t.positions.length/3,added=[];
 for(const v of p)added.push(...v.map((value,k)=>value+n[k]*distance));
 const index=t.indices.slice(0,faceIndex*3).concat(t.indices.slice(faceIndex*3+3));
 index.push(old,old+1,old+2);
 for(let e=0;e<3;e++){
  const a=ids[e],b=ids[(e+1)%3],ap=old+e,bp=old+(e+1)%3;
  index.push(a,b,bp,a,bp,ap);
 }
 // The native format currently binds ONE UV pair to each indexed vertex.
 // Search a tiny bounded per-face offset to avoid collapsed UV side walls;
 // full hard-seam unwrapping remains a separate authoring task.
 const uvsOriginal=ids.map(i=>t.uvs.slice(i*2,i*2+2));
 const uvArea=(a,b,c)=>Math.abs((b[0]-a[0])*(c[1]-a[1])-
  (b[1]-a[1])*(c[0]-a[0]))/2;
 if(uvArea(...uvsOriginal)<1e-11)
  return {ok:false,reason:'Selected triangle already has collapsed UVs; repair the UV map first'};
 let uvData=null;
 for(const shift of [[.013,.027],[.027,-.013],[.019,.043],[-.031,.017],[.037,.021]]){
  const proposed=uvsOriginal.map(u=>u.map((v,k)=>v+shift[k]));
  if(proposed.flat().some(v=>!Number.isFinite(v)||Math.abs(v)>20))continue;
  let valid=true;
  for(let e=0;e<3;e++){
   const a=uvsOriginal[e],b=uvsOriginal[(e+1)%3],
    ap=proposed[e],bp=proposed[(e+1)%3];
   if(uvArea(a,b,bp)<1e-11||uvArea(a,bp,ap)<1e-11){valid=false;break;}
  }
  if(valid){uvData=proposed.flat();break;}
 }
 if(!uvData)return {ok:false,reason:'Cannot map sidewall UVs without collapsed faces'};
 const data={positions:[...t.positions,...added],
  uvs:[...t.uvs,...uvData],indices:index};
 if(!atelierTopologyValid({kind:'topologyMesh',topologyMesh:data}))
  return {ok:false,reason:'Extruded mesh fails native indexed bounds'};
 const after=atelierTopologyAudit(data);
 if(!after.ok||after.zeroAreaFaces||after.nonManifoldEdges||
  after.oppositeWindingErrors||after.boundaryEdges!==audit.boundaryEdges)
  return {ok:false,reason:'Extrusion creates unsafe/inconsistent shared triangles'};
 return {ok:true,data,before:audit,after,faceIndex,distance,
  verticesBefore:t.positions.length/3,verticesAfter:data.positions.length/3,
  facesBefore:total,facesAfter:data.indices.length/3,
  dropsRuntimeLOD:!!part.runtimeLOD};
}
let atelierExtrudePreview=null;
function atelierExtrudeRefresh(){
 const part=partById(selection),el=$m('FaceExtrudeTools');
 if(!el)return;
 el.hidden=part?.kind!=='topologyMesh';
 if(part?.kind!=='topologyMesh'){atelierExtrudePreview=null;return;}
 $m('FaceExtrudeStatus').textContent=part.topologyMesh.indices.length/3+
  ' indexed faces. Only closed manifold interior face edges can extrude; editing an open edge is deliberately rejected.';
}
function atelierExtrudeInstall(){
 const el=k=>$m('FaceExtrude'+k);
 el('Preview').addEventListener('click',()=>{
  const p=partById(selection),face=Number(el('Face').value),
   distance=Number(el('Depth').value);
  const result=atelierFaceExtrudeCandidate(p,face,distance);
  atelierExtrudePreview=result.ok?{...result,id:p.id,
   baseline:JSON.stringify(p.topologyMesh)}:null;
  if(!result.ok){status('Face extrusion preview rejected: '+result.reason,true);return;}
  el('Status').textContent=result.facesBefore+' → '+result.facesAfter+
   ' real triangles, '+result.verticesBefore+' → '+result.verticesAfter+
   ' vertices. '+(distance>0?'Outward':'Inward')+
   ' local face edit; small UV shift on added top/side faces. '+
   (result.dropsRuntimeLOD?'Low runtime LOD will be invalidated.':'')+
   ' Source unchanged until Apply.';
  status('Actual face-wall geometry preview ready. Check topology/UV tradeoffs before commit.');
 });
 el('Apply').addEventListener('click',()=>{
  const p=partById(selection),result=atelierExtrudePreview;
  if(!result?.ok||!p||p.id!==result.id||
    JSON.stringify(p.topologyMesh)!==result.baseline){
   status('Preview this unchanged indexed face before committing.',true);return;
  }
  const candidate={...p,topologyMesh:result.data};
  delete candidate.runtimeLOD;
  if(!checkPart(candidate)){status('Native validation refused face extrusion.',true);return;}
  checkpoint();p.topologyMesh=result.data;delete p.runtimeLOD;
  atelierExtrudePreview=null;signalEdited();select(p.id);
  status((result.distance>0?'Extruded':'Intruded')+
   ' true indexed face and 3 attached sidewalls, recorded in Undo.');
 });
}
