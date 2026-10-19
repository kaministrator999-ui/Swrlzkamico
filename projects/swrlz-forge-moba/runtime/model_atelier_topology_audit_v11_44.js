// §E v11.44 — exact indexed-edge topology inspection & conservative
// local orientation repair. Open boundaries are observations, not auto-filled
// holes. Never edit procedural source or attempt speculative manifold fixes.
function atelierTopologyAudit(data){
 if(!data||!Array.isArray(data.positions)||!Array.isArray(data.indices)||
    data.positions.length%3||data.indices.length%3)return {ok:false,reason:'Malformed indexed geometry'};
 const vcount=data.positions.length/3,edges=new Map(),faces=data.indices.length/3;
 let zeroArea=0,invalid=0;
 for(let face=0;face<faces;face++){
   const ids=data.indices.slice(face*3,face*3+3);
   if(ids.some(id=>!Number.isInteger(id)||id<0||id>=vcount)){
     invalid++;continue;
   }
   const pts=ids.map(id=>data.positions.slice(id*3,id*3+3));
   const a=pts[0],b=pts[1],c=pts[2];
   const ab=b.map((x,i)=>x-a[i]),ac=c.map((x,i)=>x-a[i]);
   const cross=[ab[1]*ac[2]-ab[2]*ac[1],
      ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
   if(cross.reduce((sum,v)=>sum+v*v,0)<1e-18)zeroArea++;
   for(let j=0;j<3;j++){
     const from=ids[j],to=ids[(j+1)%3],
       key=from<to?from+':'+to:to+':'+from;
     if(!edges.has(key))edges.set(key,[]);
     edges.get(key).push({face,from,to});
   }
 }
 let boundaryEdges=0,nonManifoldEdges=0,oppositeWindingErrors=0;
 for(const incidents of edges.values()){
   if(incidents.length===1)boundaryEdges++;
   else if(incidents.length>2)nonManifoldEdges++;
   else if(incidents[0].from===incidents[1].from)oppositeWindingErrors++;
 }
 return {ok:invalid===0,faces,vertices:vcount,boundaryEdges,
   nonManifoldEdges,oppositeWindingErrors,zeroAreaFaces:zeroArea,
   invalidFaces:invalid,edges};
}
function atelierTopologyReorientCandidate(part){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
   return {ok:false,reason:'Select a valid separately baked indexed mesh'};
 const audit=atelierTopologyAudit(part.topologyMesh);
 if(!audit.ok||audit.zeroAreaFaces||audit.nonManifoldEdges)
   return {ok:false,reason:'Repair blocked: bad indices, zero-area faces or nonmanifold edges'};
 const adjacent=Array.from({length:audit.faces},()=>[]);
 for(const edge of audit.edges.values()){
   if(edge.length!==2)continue;
   const [a,b]=edge,same=a.from===b.from;
   adjacent[a.face].push([b.face,same]);adjacent[b.face].push([a.face,same]);
 }
 const parity=Array(audit.faces).fill(-1);
 for(let seed=0;seed<audit.faces;seed++){
   if(parity[seed]!==-1)continue;
   parity[seed]=0;
   const queue=[seed];
   for(let i=0;i<queue.length;i++){
     const face=queue[i];
     for(const [other,same]of adjacent[face]){
       const proposed=parity[face]^(same?1:0);
       if(parity[other]===-1){parity[other]=proposed;queue.push(other);}
       else if(parity[other]!==proposed)
         return {ok:false,reason:'Conflicting winding cycle cannot be resolved safely'};
     }
   }
 }
 const flips=parity.filter(x=>x===1).length;
 if(flips===0)return {ok:false,reason:'All shared face edges already have consistent winding'};
 const indices=part.topologyMesh.indices.slice();
 for(let f=0;f<parity.length;f++)if(parity[f]){
   const index=f*3;[indices[index+1],indices[index+2]]=
      [indices[index+2],indices[index+1]];
 }
 const data={...part.topologyMesh,indices};
 const after=atelierTopologyAudit(data);
 if(!after.ok||after.oppositeWindingErrors||
    after.nonManifoldEdges||after.zeroAreaFaces||
    after.boundaryEdges!==audit.boundaryEdges||
    !atelierTopologyValid({...part,topologyMesh:data,runtimeLOD:undefined}))
   return {ok:false,reason:'Proposed orientation fails topology validation'};
 return {ok:true,data,flips,before:audit,after};
}
function atelierTopologyAuditRefresh(){
 const part=partById(selection),pane=$m('TopologyAuditTools');
 if(!pane)return;
 pane.hidden=part?.kind!=='topologyMesh';
 if(part?.kind==='topologyMesh'){
   const a=atelierTopologyAudit(part.topologyMesh);
   $m('TopologyAuditStats').textContent= a.ok?
     a.faces+' triangles · '+a.vertices+' vertices · '+a.boundaryEdges+
     ' open boundary edges · '+a.nonManifoldEdges+' nonmanifold edges · '+
     a.oppositeWindingErrors+' inconsistent shared edges · '+
     a.zeroAreaFaces+' zero-area faces.':'Invalid indexed mesh.';
 }
}
function atelierTopologyAuditInstall(){
 $m('TopologyAuditCheck').addEventListener('click',()=>{
   atelierTopologyAuditRefresh();
   status('Indexed mesh inspected. Open boundary is a finding, not proof of a hole.');
 });
 $m('TopologyAuditRepair').addEventListener('click',()=>{
   const p=partById(selection),result=atelierTopologyReorientCandidate(p);
   if(!result.ok){status('Conservative winding repair declined: '+result.reason,true);return;}
   const candidate={...p,topologyMesh:result.data};
   if(!checkPart(candidate)){status('Reoriented mesh failed native validation.',true);return;}
   checkpoint();p.topologyMesh=result.data;
   // Lower-detail profile is now stale if parent geometry flips; explicitly
   // disable and detach it instead of misrepresenting synchronized LODs.
   delete p.runtimeLOD;
   signalEdited();select(p.id);
   status('Fixed winding on '+result.flips+' triangles; boundary count unchanged. Stored old state in Undo.');
 });
}
