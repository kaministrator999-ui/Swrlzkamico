// §E v11.46 — local adaptive *indexed* topology refinement.
// Uses actual triangle lengths and a chosen object-local region, not cosmetic
// density metadata. Shared physical edges are split consistently across all
// incident triangles; UV-seam duplicates keep their independent texcoords.
// Atomic candidate only; no original procedural mesh or file is mutated.
function atelierAdaptiveRefineCandidate(part,center,radius,maxEdge){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
   return {ok:false,reason:'Select a valid separately baked indexed topology mesh'};
 if(!Array.isArray(center)||center.length!==3||
    !center.every(v=>Number.isFinite(v)&&Math.abs(v)<=4)||
    !Number.isFinite(radius)||radius<.05||radius>4||
    !Number.isFinite(maxEdge)||maxEdge<.025||maxEdge>4)
   return {ok:false,reason:'Finite XYZ center (±4), radius 0.05–4 and edge target 0.025–4 required'};
 const src=part.topologyMesh,pos=src.positions,uv=src.uvs,indices=src.indices,
   faces=indices.length/3,vertices=pos.length/3;
 // Edges are keyed by actual 3D endpoints, not by mutable vertex indices:
 // duplicate positions at an image/UV seam will receive coincident midpoint
 // geometry with their own interpolated UVs.
 const coord=i=>pos.slice(i*3,i*3+3);
 const xyzKey=i=>coord(i).map(x=>Math.round(x*1e6)).join(',');
 const edgeKey=(a,b)=>[xyzKey(a),xyzKey(b)].sort().join('|');
 const xyzDistance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);
 const usage=new Map(),marked=new Set(),selected=[];
 for(let f=0;f<faces;f++){
   const ids=indices.slice(f*3,f*3+3),p=ids.map(coord);
   const bary=[0,1,2].map(k=>(p[0][k]+p[1][k]+p[2][k])/3);
   const local=xyzDistance(bary,center)<=radius;
   const e=[0,1,2].map(j=>({key:edgeKey(ids[j],ids[(j+1)%3]),
      len:xyzDistance(p[j],p[(j+1)%3])}));
   for(const x of e)usage.set(x.key,(usage.get(x.key)||0)+1);
   if(local&&Math.max(...e.map(x=>x.len))>maxEdge){
     selected.push(f);
     // Subdivide all three sides of a selected source triangle; neighboring
     // triangles that share those edges are automatically stitched below.
     for(const x of e)marked.add(x.key);
   }
 }
 if(!selected.length)
   return {ok:false,reason:'No triangles near that center exceed the requested edge length'};
 if(Array.from(marked).some(key=>usage.get(key)>2))
   return {ok:false,reason:'Target region contains a nonmanifold physical edge'};
 const data={positions:pos.slice(),uvs:uv.slice(),indices:[]},
       cache=new Map();
 const append=(p,t)=>{
   const i=data.positions.length/3;
   data.positions.push(...p);data.uvs.push(...t);
   return i;
 };
 const uvOf=i=>uv.slice(i*2,i*2+2);
 const midpoint=(a,b)=>{
   const key=[a,b].sort((x,y)=>x-y).join(':');
   if(cache.has(key))return cache.get(key);
   const p=coord(a).map((v,k)=>(v+pos[3*b+k])/2),
         t=uvOf(a).map((v,k)=>(v+uv[2*b+k])/2);
   const id=append(p,t);cache.set(key,id);return id;
 };
 let affected=0;
 for(let f=0;f<faces;f++){
   const v=indices.slice(f*3,f*3+3);
   const polygon=[];
   for(let e=0;e<3;e++){
     const a=v[e],b=v[(e+1)%3];
     polygon.push(a);
     if(marked.has(edgeKey(a,b)))polygon.push(midpoint(a,b));
   }
   if(polygon.length===3){data.indices.push(...v);continue;}
   affected++;
   const cp=[0,1,2].map(k=>(pos[v[0]*3+k]+pos[v[1]*3+k]+pos[v[2]*3+k])/3),
     cu=[0,1].map(k=>(uv[v[0]*2+k]+uv[v[1]*2+k]+uv[v[2]*2+k])/3);
   // Interior centroid fan avoids the zero-area collinear triangles that
   // a boundary fan would create when edge midpoints are inserted.
   const mid=append(cp,cu);
   for(let i=0;i<polygon.length;i++)
     data.indices.push(mid,polygon[i],polygon[(i+1)%polygon.length]);
   if(data.positions.length/3>atelierLODSavedVertices||
      data.indices.length/3>atelierLODSavedTriangles)
     return {ok:false,reason:'Refinement exceeds saved mesh limits (9k vertices / 16k triangles)'};
 }
 if(data.positions.length/3>atelierLODSavedVertices||
   data.indices.length/3>atelierLODSavedTriangles||
   !atelierTopologyValid({kind:'topologyMesh',topologyMesh:data}))
   return {ok:false,reason:'Generated mesh exceeds native schema budget'};
 const result=atelierTopologyAudit(data);
 if(!result.ok||result.nonManifoldEdges||result.zeroAreaFaces)
   return {ok:false,reason:'Generated indexed mesh failed integrity audit'};
 return {ok:true,data,sourceFaces:faces,newFaces:data.indices.length/3,
   sourceVertices:vertices,newVertices:data.positions.length/3,
   selectedFaces:selected.length,affectedFaces:affected,
   hasNewBoundary:result.boundaryEdges>atelierTopologyAudit(src).boundaryEdges,
   dropsRuntimeLOD:!!part.runtimeLOD};
}
let atelierAdaptivePreview=null;
function atelierAdaptiveRefresh(){
 const p=partById(selection),panel=$m('AdaptiveTopologyTools');
 if(!panel)return;
 panel.hidden=p?.kind!=='topologyMesh';
 if(p?.kind==='topologyMesh'){
   const t=p.topologyMesh;
   $m('AdaptiveTopologyStatus').textContent=t.indices.length/3+
     ' triangles, '+t.positions.length/3+
     ' indexed vertices. Set an object-local center, radius and maximum triangle edge length. Preview before applying.';
 }else atelierAdaptivePreview=null;
}
function atelierAdaptiveInstall(){
 const el=k=>$m('AdaptiveTopology'+k);
 const compute=()=>{
   const part=partById(selection);
   const center=[0,1,2].map(i=>Number(el('Center'+i).value));
   const radius=Number(el('Radius').value),edge=Number(el('Edge').value);
   return atelierAdaptiveRefineCandidate(part,center,radius,edge);
 };
 el('Preview').addEventListener('click',()=>{
   const r=compute(),p=partById(selection);
   atelierAdaptivePreview=r.ok?{...r,id:p.id,
     baseline:JSON.stringify(p.topologyMesh)}:null;
   if(!r.ok){status('Adaptive refine preview rejected: '+r.reason,true);return;}
   el('Status').textContent=r.sourceFaces+' → '+r.newFaces+
     ' actual triangles; '+r.sourceVertices+' → '+r.newVertices+
     ' vertices, '+r.selectedFaces+' target faces, '+r.affectedFaces+
     ' stitched triangles. '+(r.dropsRuntimeLOD?'Existing LOD must be regenerated.':'');
   status('Local adaptive refinement measured. Source geometry unchanged until Apply.');
 });
 el('Apply').addEventListener('click',()=>{
   const p=partById(selection),r=atelierAdaptivePreview;
   if(!r?.ok||!p||p.id!==r.id||
      JSON.stringify(p.topologyMesh)!==r.baseline){
     status('Preview this same, unchanged indexed mesh before applying.',true);return;
   }
   const candidate={...p,topologyMesh:r.data};
   delete candidate.runtimeLOD;
   if(!checkPart(candidate)){
     status('Native mesh validation rejected adaptive refinement.',true);return;
   }
   checkpoint();p.topologyMesh=r.data;
   delete p.runtimeLOD;
   atelierAdaptivePreview=null;
   signalEdited();select(p.id);
   status('Committed stitched local triangle subdivision. Original procedural model unaffected. Undo restores previous mesh.');
 });
}
