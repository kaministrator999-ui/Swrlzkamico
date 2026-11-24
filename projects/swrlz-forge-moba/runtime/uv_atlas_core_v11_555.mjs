import {flattenSeamedMesh} from './uv_lscm_core_v11_555.mjs';
/* §E v11.555 — reusable geometry-derived UV atlas core.
   xatlas (MIT): real chart segmentation, conformal parameterization and packing.
   Usable from Node authoring and the browser's selected topology mesh.
   Does not edit source arrays. The caller handles undo, textures and saves. */
const finite=a=>Array.isArray(a)||ArrayBuffer.isView(a);
export function validateMesh(positions,indices){
 if(!finite(positions)||!finite(indices)||positions.length%3||indices.length%3||
    positions.length<9||indices.length<3)throw Error('Expected indexed triangle mesh');
 if(positions.length/3>120000||indices.length/3>220000)
    throw Error('Mesh exceeds mobile UV unwrapping safety limit');
 for(const x of positions)if(!Number.isFinite(x))throw Error('Non-finite 3D coordinate');
 for(const i of indices)if(!Number.isInteger(i)||i<0||i>=positions.length/3)
    throw Error('Invalid triangle index');
 return {vertices:positions.length/3,triangles:indices.length/3};
}
function weldPositions(pos,idx){
 const xyz=[],oldToNew=[],map=new Map();
 for(let i=0;i<pos.length;i+=3){
  const key=pos.slice(i,i+3).map(n=>Number(n).toFixed(6)).join(',');
  let id=map.get(key);
  if(id===undefined){id=xyz.length/3;map.set(key,id);xyz.push(...pos.slice(i,i+3));}
  oldToNew.push(id);
 }
 return {positions:xyz,indices:Array.from(idx,i=>oldToNew[i]),welded:oldToNew.length-xyz.length/3};
}
const physicalTriangleKey=(p,idx,k)=>{
 const ids=[idx[k],idx[k+1],idx[k+2]];
 return ids.map(i=>p.slice(i*3,i*3+3).map(n=>n.toFixed(5)).join(',')).sort().join('|');
};
export function triangleSignature(positions,indices){
 const map=new Map();
 for(let k=0;k<indices.length;k+=3){
  const key=physicalTriangleKey(positions,indices,k);
  map.set(key,(map.get(key)||0)+1);
 }
 return map;
}
export function assertSameTriangles(source,target){
 const a=triangleSignature(source.positions,source.indices);
 const b=triangleSignature(target.positions,target.indices);
 if(a.size!==b.size)throw Error('Unwrap altered original 3D triangle geometry');
 for(const [key,count] of a)if(b.get(key)!==count)
    throw Error('Unwrap changed triangle connectivity / positions');
}
export function distortionStats(positions,uvs,indices){
 const density=[];
 for(let k=0;k<indices.length;k+=3){
  const a=indices[k],b=indices[k+1],c=indices[k+2];
  const p=[a,b,c].map(i=>positions.slice(i*3,i*3+3));
  const u=[a,b,c].map(i=>uvs.slice(i*2,i*2+2));
  const A=p[1].map((v,i)=>v-p[0][i]),B=p[2].map((v,i)=>v-p[0][i]);
  const area3=Math.hypot(A[1]*B[2]-A[2]*B[1],A[2]*B[0]-A[0]*B[2],A[0]*B[1]-A[1]*B[0]);
  const area2=Math.abs((u[1][0]-u[0][0])*(u[2][1]-u[0][1])-
                       (u[1][1]-u[0][1])*(u[2][0]-u[0][0]));
  if(area3>1e-10&&area2>1e-12)density.push(Math.sqrt(area2/area3));
 }
 if(density.length===0)throw Error('Unwrap produced no usable UV triangles');
 density.sort((a,b)=>a-b);
 const pct=p=>density[Math.max(0,Math.min(density.length-1,Math.floor(p*(density.length-1))))];
 return {p05:pct(.05),p95:pct(.95),p95P05:pct(.95)/Math.max(pct(.05),1e-12),
         trianglesChecked:density.length};
}
export async function unwrapMesh(createXAtlas,source,options={}){
 validateMesh(source.positions,source.indices);
 const normalized={
  positions:Array.from(source.positions),
  indices:Array.from(source.indices)
 };
 const isLSCM=options.method==='lscm';
 const input=isLSCM?flattenSeamedMesh({
  ...normalized,uvs:Array.from(source.uvs||[])
 },options.faceMaterialData):options.weldSeams?
  weldPositions(normalized.positions,normalized.indices):
  {...normalized,welded:0};
 const materials=options.faceMaterialData
  ?new Uint32Array(Array.from(options.faceMaterialData)):null;
 if(materials&&materials.length!==input.indices.length/3)throw Error('Face seam groups must match triangles');
 const xatlas=await createXAtlas();
 const atlas=xatlas.createAtlas();
 try{
  const declaration={indices:new Uint32Array(input.indices)};
  if(isLSCM){
   declaration.uvs=new Float32Array(input.uvs);
   declaration.faceMaterialData=input.faceMaterialData;
  }else{
   declaration.positions=new Float32Array(input.positions);
   if(materials)declaration.faceMaterialData=materials;
  }
  const error=isLSCM?atlas.addUvMesh(declaration):atlas.addMesh(declaration);
  if(error!==xatlas.AddMeshError.Success)
   throw Error('xatlas '+(isLSCM?'addUvMesh':'addMesh')+': '+xatlas.addMeshErrorString(error));
  const pack={
    resolution:options.resolution||1024,
    padding:Math.max(4,Math.min(24,options.padding||8)),
    rotateCharts:true,rotateChartsToAxis:true
  };
  if(isLSCM)atlas.packCharts(pack);
  else atlas.generate({
    maxCost:options.maxCost||10,maxIterations:2,
    straightnessWeight:2,normalSeamWeight:4,
    textureSeamWeight:2,fixWinding:true
  },pack);
  if(atlas.atlasCount!==1||!atlas.width||!atlas.height)
   throw Error('UV solver needs more than one atlas; increase resolution or simplify seams');
  const mesh=atlas.getMesh(0);
  if(mesh.indexCount!==input.indices.length)throw Error('xatlas lost triangle indices');
  const positions=[],uvs=[];
  for(const v of mesh.vertices){
   const k=v.xref;
   if(!Number.isInteger(k)||k<0||k*3+2>=input.positions.length)
    throw Error('xatlas returned invalid input vertex reference');
   positions.push(...input.positions.slice(k*3,k*3+3));
   uvs.push(v.uv[0]/atlas.width,v.uv[1]/atlas.height);
  }
  const indices=Array.from(mesh.indices);
  if(mesh.vertexCount!==positions.length/3||!uvs.every(v=>Number.isFinite(v)&&v>=-1e-5&&v<=1+1e-5))
   throw Error('UV atlas contains invalid coordinates');
  const result={positions,indices,uvs:uvs.map(v=>Math.min(1,Math.max(0,v))),
   charts:mesh.chartCount,width:atlas.width,height:atlas.height,
   weldedInputVertices:input.welded||0,
   method:isLSCM?'LSCM+xatlas-packing':'xatlas-automatic',
   lscmIterations:isLSCM?input.totalIterations:0};
  validateMesh(result.positions,result.indices);
  assertSameTriangles(normalized,result);
  result.distortion=distortionStats(result.positions,result.uvs,result.indices);
  if(options.maxVertices&&result.positions.length/3>options.maxVertices)
   throw Error('Too many UV seam vertices ('+result.positions.length/3+
     '); edit seams or raise the project vertex budget');
  if(options.maxCharts&&result.charts>options.maxCharts)
   throw Error('UV atlas has '+result.charts+' islands; adjust seam chart settings');
  return result;
 }finally{atlas.destroy();}
}
