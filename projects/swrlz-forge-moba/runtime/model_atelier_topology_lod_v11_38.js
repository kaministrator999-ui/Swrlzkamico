// §E v11.38: explicit low-poly topology copies and OBJ LOD authoring.
// A spatial vertex-cluster reducer, NOT a watertight/QEM decimator or
// automatic distance-switching runtime LOD. No source mesh is overwritten.
MODEL_ATELIER_KINDS.push('topologyMesh');
const atelierLODMaxSourceTriangles=180000,atelierLODSavedVertices=9000,
  atelierLODSavedTriangles=16000;
let atelierLODCandidate=null;
function atelierTopologyValid(part){
 if(part.kind!=='topologyMesh')return part.topologyMesh===undefined&&part.runtimeLOD===undefined;
 const t=part.topologyMesh;
 if(!t||typeof t!=='object'||Array.isArray(t)||
   Object.keys(t).sort().join('|')!=='indices|positions|uvs')return false;
 const {positions,uvs,indices}=t;
 if(!Array.isArray(positions)||positions.length<9||
   positions.length>atelierLODSavedVertices*3||positions.length%3||
   !positions.every(v=>Number.isFinite(v)&&Math.abs(v)<=100))return false;
 const count=positions.length/3;
 if(!Array.isArray(uvs)||uvs.length!==count*2||
   !uvs.every(v=>Number.isFinite(v)&&Math.abs(v)<=20))return false;
 if(!Array.isArray(indices)||!indices.length||indices.length%3||
   indices.length>atelierLODSavedTriangles*3||
   !indices.every(v=>Number.isInteger(v)&&v>=0&&v<count))return false;
 for(let i=0;i<indices.length;i+=3){
   const a=indices[i],b=indices[i+1],c=indices[i+2];
   if(a===b||b===c||c===a)return false;
 }
 if(part.runtimeLOD!==undefined){
   const lod=part.runtimeLOD;
   if(!lod||typeof lod!=='object'||Array.isArray(lod)||
      Object.keys(lod).sort().join('|')!=='enabled|low|switchDistance'||
      typeof lod.enabled!=='boolean'||!Number.isFinite(lod.switchDistance)||
      lod.switchDistance<.5||lod.switchDistance>120||
      !atelierTopologyValid({kind:'topologyMesh',topologyMesh:lod.low})||
      lod.low.indices.length>=indices.length)return false;
 }
 return true;
}
function atelierTopologyGeometry(part){
 const t=part.topologyMesh;
 const out=new THREE.BufferGeometry();
 out.setAttribute('position',new THREE.Float32BufferAttribute(t.positions,3));
 out.setAttribute('uv',new THREE.Float32BufferAttribute(t.uvs,2));
 out.setIndex(t.indices);
 out.computeVertexNormals();out.computeBoundingSphere();out.computeBoundingBox();
 return out;
}
function atelierLODOne(g,grid,strictUV=false){
 const positions=g.getAttribute('position'),uvs=g.getAttribute('uv'),idx=g.getIndex();
 const points=positions.count,triangles=Math.floor((idx?.count||points)/3);
 const box=new THREE.Box3().setFromBufferAttribute(positions);
 if(box.isEmpty()||!Number.isFinite(box.min.x))return null;
 const dx=box.max.x-box.min.x,dy=box.max.y-box.min.y,dz=box.max.z-box.min.z;
 const edge=Math.max(dx,dy,dz);if(edge<1e-8)return null;
 const cell=edge/grid;
 const groups=new Map(),remap=new Int32Array(points);
 const seam=u=>u<.01?'low':u>.99?'high':'middle';
 for(let i=0;i<points;i++){
   const x=positions.getX(i),y=positions.getY(i),z=positions.getZ(i);
   const u=uvs?.getX(i)||0,v=uvs?.getY(i)||0;
   // Isolate UV boundary duplicates while clustering in 3D object space.
   const key=[Math.floor((x-box.min.x)/cell),Math.floor((y-box.min.y)/cell),
     Math.floor((z-box.min.z)/cell),uvs?seam(u):'',uvs?seam(v):'',
     // Strict chart guard stops inside-UV seams from merging across distant
     // atlas coordinates inside one spatial cluster. It is opt-in, bounded,
     // and never rewrites the original source geometry.
     strictUV&&uvs?Math.floor(u*32+1e-9):'',
     strictUV&&uvs?Math.floor(v*32+1e-9):''].join(':');
   let group=groups.get(key);
   if(!group){group={id:groups.size,sx:0,sy:0,sz:0,su:0,sv:0,n:0};
     groups.set(key,group);}
   group.sx+=x;group.sy+=y;group.sz+=z;group.su+=u;group.sv+=v;group.n++;
   remap[i]=group.id;
 }
 const out=Array.from(groups.values());
 const packed=out.map(v=>[v.sx/v.n,v.sy/v.n,v.sz/v.n,v.su/v.n,v.sv/v.n]);
 const kept=[],dupes=new Set();
 const inputIndex=i=>idx?idx.getX(i):i;
 for(let t=0;t<triangles;t++){
   const a=remap[inputIndex(t*3)],b=remap[inputIndex(t*3+1)],
         c=remap[inputIndex(t*3+2)];
   if(a===b||b===c||a===c)continue;
   const A=packed[a],B=packed[b],C=packed[c];
   const ux=B[0]-A[0],uy=B[1]-A[1],uz=B[2]-A[2],
     vx=C[0]-A[0],vy=C[1]-A[1],vz=C[2]-A[2];
   const nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
   if(nx*nx+ny*ny+nz*nz<1e-17)continue;
   const signature=[a,b,c].sort((l,r)=>l-r).join(',');
   if(dupes.has(signature))continue;dupes.add(signature);
   kept.push(a,b,c);
 }
 if(kept.length<3)return null;
 // Remove unused vertices to measure actual surviving topology.
 const used=new Map(),indices=[],positionsOut=[],uvOut=[];
 for(const old of kept){
   if(!used.has(old)){
     const newId=used.size;used.set(old,newId);
     positionsOut.push(...packed[old].slice(0,3));
     uvOut.push(...packed[old].slice(3,5));
   }
   indices.push(used.get(old));
 }
 return {positions:positionsOut,uvs:uvOut,indices};
}
function atelierLODPlan(g,ratio,strictUV=false){
 if(!g?.attributes?.position||typeof strictUV!=='boolean'||
    (strictUV&&!g.attributes.uv)||!Number.isFinite(ratio)||ratio<.05||ratio>.9||
   g.groups?.length>1||g.morphAttributes?.position?.length)
   return {ok:false,reason:'Single-material geometry and a ratio of 5–90% required'};
 const source=Math.floor((g.index?.count||g.attributes.position.count)/3);
 if(source<12||source>atelierLODMaxSourceTriangles)
   return {ok:false,reason:'Source must contain 12–180,000 triangles'};
 const desired=Math.max(4,Math.floor(source*ratio));
 let low=2,high=160,best=null;
 // Binary search a 3D cell-grid resolution; report ACTUAL result rather
 // than promising exactly desired triangles.
 for(let iteration=0;iteration<10&&low<=high;iteration++){
   const grid=Math.floor((low+high)/2),data=atelierLODOne(g,grid,strictUV);
   if(!data){low=grid+1;continue;}
   const count=data.indices.length/3;
   if(count<source&&(!best||Math.abs(count-desired)<Math.abs(best.after-desired)))
     best={ok:true,data,before:source,after:count,vertices:data.positions.length/3,
       requested:desired,grid,strictUV};
   if(count<desired)low=grid+1;else high=grid-1;
 }
 if(!best||best.after>=source)
   return {ok:false,reason:'No reduction possible with these bounds; try a smaller ratio'};
 return {...best,canBake:best.vertices<=atelierLODSavedVertices&&
   best.after<=atelierLODSavedTriangles};
}
function atelierLODRefresh(){
 atelierTopologyRefresh();
 const p=partById(selection),el=$m('LODTools');if(!el)return;
 el.hidden=!p;
 if($m('LODStats'))$m('LODStats').textContent=
   'Vertex-cluster LOD authoring: Preview before Bake or OBJ export. '+
   'Creates a separate topology mesh; does not alter the original, guarantee manifoldness, '+
   'or automatically switch LOD by camera distance.';
}
function atelierLODInstall(){
 atelierTopologyInstall();
 const id=s=>$m('LOD'+s);
 id('Preview').addEventListener('click',()=>{
   const part=partById(selection),mesh=modelRoot?.children.find(x=>x.isMesh&&
     x.userData.atelierId===selection);
   const ratio=Number(id('Ratio').value);
   atelierLODCandidate=null;
   const strictUV=!!$m('LODProtectUV')?.checked;
    const planned=atelierLODPlan(mesh?.geometry,ratio,strictUV);
   if(!part||!planned.ok){status(planned.reason||'Select a mesh to plan LOD.',true);return;}
   atelierLODCandidate={...planned,id:part.id,ratio};
   id('Stats').textContent=planned.before.toLocaleString()+' → '+
     planned.after.toLocaleString()+' actual triangles · '+
     planned.vertices.toLocaleString()+' actual mesh vertices · '+
     (planned.canBake?'Native topology copy available':'OBJ export only: copy exceeds portable native cap')+
      (strictUV?' · strict 32-bin UV-island separation':' · legacy seam-boundary mode');
   status('Measured LOD reduction ready. Review before baking or exporting.');
 });
 id('Bake').addEventListener('click',()=>{
   const plan=atelierLODCandidate,src=partById(selection);
   if(!plan||!src||plan.id!==src.id||!plan.canBake){
     status('Preview a portable LOD for the selected mesh first.',true);return;}
   if(model().parts.length>=MODEL_ATELIER_LIMIT){
     status('Model part limit reached.',true);return;}
   const copy={id:'lod-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8),
     name:src.name.slice(0,64)+' · reduced LOD',
     group:'Baked LOD copies',kind:'topologyMesh',
     topologyMesh:structuredClone(plan.data),
     position:[...src.position],rotation:[...src.rotation],
     scale:[...src.scale],color:src.color,material:src.material};
   if(!checkPart(copy)){status('Rejected LOD topology payload; original unchanged.',true);return;}
   checkpoint();model().parts.push(copy);signalEdited();select(copy.id);
   atelierLODCandidate=null;
   status('Baked a real indexed topology LOD as a separate editable model part. Original preserved; Undo available.');
 });
 id('OBJ').addEventListener('click',()=>{
   const plan=atelierLODCandidate,src=partById(selection);
   if(!plan||!src||plan.id!==src.id){status('Preview this selected part first.',true);return;}
   const mesh=modelRoot?.children.find(x=>x.isMesh&&x.userData.atelierId===src.id);
   if(!mesh)return;
   mesh.updateMatrixWorld(true);
   const t=plan.data,lines=['# §E explicit LOD authoring: one selected reduced mesh',
     '# source triangles '+plan.before+', generated triangles '+plan.after,
      '# strict UV-island guard '+(plan.strictUV?'enabled':'off (legacy mode)'),
     'o atelier_LOD_'+Math.round(plan.ratio*100)];
   for(let i=0;i<t.positions.length;i+=3){
     const p=new THREE.Vector3(t.positions[i],t.positions[i+1],t.positions[i+2])
       .applyMatrix4(mesh.matrixWorld);
     lines.push('v '+p.x+' '+p.y+' '+p.z);
   }
   for(let i=0;i<t.uvs.length;i+=2)lines.push('vt '+t.uvs[i]+' '+t.uvs[i+1]);
   for(let i=0;i<t.indices.length;i+=3){
     const ids=t.indices.slice(i,i+3).map(j=>(j+1)+'/'+(j+1));
     lines.push('f '+ids.join(' '));
   }
   download('atelier-reduced-lod-'+Math.round(plan.ratio*100)+'.obj',
     lines.join('\n')+'\n','text/plain');
   status('Exported actual reduced triangle mesh OBJ with UV coordinates. LOD switching is not automatic.');
 });
}

// §E v11.40. Explicit topological operations ONLY on separately baked
// topologyMesh instances. All inputs are validated before a single checkpoint.
// No source procedural mesh, UV reference, detail layer or sibling is mutated.
function atelierTopologyEditCandidate(part,command,faceIndex=0,edgeSlot=0,vertexIndex=0,delta=[0,0,0]){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
   return {ok:false,reason:'Select a separately baked indexed topology mesh'};
 const src=part.topologyMesh,faces=src.indices.length/3,vertices=src.positions.length/3;
 const validFace=Number.isInteger(faceIndex)&&faceIndex>=0&&faceIndex<faces;
 const validVertex=Number.isInteger(vertexIndex)&&vertexIndex>=0&&vertexIndex<vertices;
 const data={positions:src.positions.slice(),uvs:src.uvs.slice(),indices:src.indices.slice()};
 if(command==='split-edge'){
   if(!validFace||!Number.isInteger(edgeSlot)||edgeSlot<0||edgeSlot>2)
     return {ok:false,reason:'Select existing face and edge slot (0–2)'};
   const tri=src.indices.slice(faceIndex*3,faceIndex*3+3),
     a=tri[edgeSlot],b=tri[(edgeSlot+1)%3],incident=[];
   for(let f=0;f<faces;f++){
     const t=src.indices.slice(f*3,f*3+3);
     const idx=t.findIndex((v,i)=>v===a&&t[(i+1)%3]===b||
       v===b&&t[(i+1)%3]===a);
     if(idx>=0)incident.push(f);
   }
   if(incident.length===0||incident.length>2)
     return {ok:false,reason:'Nonmanifold or missing selected edge; edit rejected'};
   if(vertices>=atelierLODSavedVertices||faces+incident.length>atelierLODSavedTriangles)
     return {ok:false,reason:'Portable vertex/triangle limits reached'};
   const m=vertices;data.positions.push(
     (src.positions[a*3]+src.positions[b*3])/2,
     (src.positions[a*3+1]+src.positions[b*3+1])/2,
     (src.positions[a*3+2]+src.positions[b*3+2])/2);
   data.uvs.push((src.uvs[a*2]+src.uvs[b*2])/2,
     (src.uvs[a*2+1]+src.uvs[b*2+1])/2);
   data.indices=[];
   for(let f=0;f<faces;f++){
     const t=src.indices.slice(f*3,f*3+3);
     if(!incident.includes(f)){data.indices.push(...t);continue;}
     const i=t.findIndex((v,k)=>v===a&&t[(k+1)%3]===b||
       v===b&&t[(k+1)%3]===a);
     const A=t[i],B=t[(i+1)%3],C=t[(i+2)%3];
     data.indices.push(A,m,C,m,B,C);
   }
 }else if(command==='move-vertex'){
   if(!validVertex||!Array.isArray(delta)||delta.length!==3||
      !delta.every(v=>Number.isFinite(v)&&Math.abs(v)<=.4)||
      delta.every(v=>v===0))
     return {ok:false,reason:'Select valid vertex and nonzero signed XYZ offsets ≤0.4'};
   for(let axis=0;axis<3;axis++)data.positions[vertexIndex*3+axis]+=delta[axis];
 }else if(command==='remove-face'){
   if(!validFace||faces<=1)return {ok:false,reason:'Choose a removable face'};
   data.indices.splice(faceIndex*3,3);
   // Strip unused vertices rather than leaving hidden stale control IDs.
   const keep=new Map(),pos=[],uv=[],next=[];
   for(const id of data.indices){
     if(!keep.has(id)){
       keep.set(id,keep.size);
       pos.push(...data.positions.slice(id*3,id*3+3));
       uv.push(...data.uvs.slice(id*2,id*2+2));
     }
     next.push(keep.get(id));
   }
   data.positions=pos;data.uvs=uv;data.indices=next;
 }else return {ok:false,reason:'Unknown topology command'};
 // Validate the edited high mesh without a low LOD that is being invalidated.
 const candidate={...part,topologyMesh:data};
 delete candidate.runtimeLOD;
 if(!atelierTopologyValid(candidate))
   return {ok:false,reason:'Proposed topology does not meet native bounds'};
 // Refuse collapsed faces introduced by movement or malformed inputs.
 for(let i=0;i<data.indices.length;i+=3){
   const ids=data.indices.slice(i,i+3);
   const [a,b,c]=ids.map(id=>data.positions.slice(id*3,id*3+3));
   const ab=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],
     ac=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
   const cross=[ab[1]*ac[2]-ab[2]*ac[1],
     ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
   if(cross.reduce((sum,x)=>sum+x*x,0)<1e-18)
     return {ok:false,reason:'Operation would collapse a face'};
 }
 return {ok:true,data,beforeFaces:faces,afterFaces:data.indices.length/3,
   beforeVertices:vertices,afterVertices:data.positions.length/3};
}
function atelierTopologyRefresh(){
 const p=partById(selection),pane=$m('TopologyTools');if(!pane)return;
 pane.hidden=p?.kind!=='topologyMesh';
 if(p?.kind==='topologyMesh'){
   $m('TopologyStats').textContent='Indexed topology: '+
     p.topologyMesh.positions.length/3+' vertices, '+
     p.topologyMesh.indices.length/3+' triangles. Editing is explicit and undoable.';
 }
}
function atelierTopologyInstall(){
 const id=k=>$m('Topology'+k);
 for(const [button,command]of [['Split','split-edge'],['Move','move-vertex'],['Remove','remove-face']]){
   id(button).addEventListener('click',()=>{
     const part=partById(selection),face=Number(id('Face').value),
       edge=Number(id('Edge').value),vertex=Number(id('Vertex').value),
       delta=[0,1,2].map(axis=>Number(id('Delta'+axis).value));
     const result=atelierTopologyEditCandidate(part,command,face,edge,vertex,delta);
     if(!result.ok){status('Topology edit rejected: '+result.reason,true);return;}
     const candidate={...part,topologyMesh:result.data};
     // Changing high topology makes its previous low LOD obsolete.
     delete candidate.runtimeLOD;
     if(!checkPart(candidate)){status('Native project validation rejected edit.',true);return;}
     checkpoint();part.topologyMesh=result.data;delete part.runtimeLOD;
     signalEdited();select(part.id);
     status(command+' applied: '+result.beforeFaces+'→'+result.afterFaces+
       ' real triangles, '+result.beforeVertices+'→'+result.afterVertices+
       ' vertices. Original procedural mesh untouched; Undo/Redo available.');
   });
 }
}
