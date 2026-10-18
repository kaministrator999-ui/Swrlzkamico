// §E v11.38: explicit low-poly topology copies and OBJ LOD authoring.
// A spatial vertex-cluster reducer, NOT a watertight/QEM decimator or
// automatic distance-switching runtime LOD. No source mesh is overwritten.
MODEL_ATELIER_KINDS.push('topologyMesh');
const atelierLODMaxSourceTriangles=180000,atelierLODSavedVertices=9000,
  atelierLODSavedTriangles=16000;
let atelierLODCandidate=null;
function atelierTopologyValid(part){
 if(part.kind!=='topologyMesh')return part.topologyMesh===undefined;
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
function atelierLODOne(g,grid){
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
     Math.floor((z-box.min.z)/cell),uvs?seam(u):'',uvs?seam(v):''].join(':');
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
function atelierLODPlan(g,ratio){
 if(!g?.attributes?.position||!Number.isFinite(ratio)||ratio<.05||ratio>.9||
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
   const grid=Math.floor((low+high)/2),data=atelierLODOne(g,grid);
   if(!data){low=grid+1;continue;}
   const count=data.indices.length/3;
   if(count<source&&(!best||Math.abs(count-desired)<Math.abs(best.after-desired)))
     best={ok:true,data,before:source,after:count,vertices:data.positions.length/3,
       requested:desired,grid};
   if(count<desired)low=grid+1;else high=grid-1;
 }
 if(!best||best.after>=source)
   return {ok:false,reason:'No reduction possible with these bounds; try a smaller ratio'};
 return {...best,canBake:best.vertices<=atelierLODSavedVertices&&
   best.after<=atelierLODSavedTriangles};
}
function atelierLODRefresh(){
 const p=partById(selection),el=$m('LODTools');if(!el)return;
 el.hidden=!p;
 if($m('LODStats'))$m('LODStats').textContent=
   'Vertex-cluster LOD authoring: Preview before Bake or OBJ export. '+
   'Creates a separate topology mesh; does not alter the original, guarantee manifoldness, '+
   'or automatically switch LOD by camera distance.';
}
function atelierLODInstall(){
 const id=s=>$m('LOD'+s);
 id('Preview').addEventListener('click',()=>{
   const part=partById(selection),mesh=modelRoot?.children.find(x=>x.isMesh&&
     x.userData.atelierId===selection);
   const ratio=Number(id('Ratio').value);
   atelierLODCandidate=null;
   const planned=atelierLODPlan(mesh?.geometry,ratio);
   if(!part||!planned.ok){status(planned.reason||'Select a mesh to plan LOD.',true);return;}
   atelierLODCandidate={...planned,id:part.id,ratio};
   id('Stats').textContent=planned.before.toLocaleString()+' → '+
     planned.after.toLocaleString()+' actual triangles · '+
     planned.vertices.toLocaleString()+' actual mesh vertices · '+
     (planned.canBake?'Native topology copy available':'OBJ export only: copy exceeds portable native cap');
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
