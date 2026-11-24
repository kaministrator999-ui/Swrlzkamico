/* §E reusable Least Squares Conformal Mapping (LSCM).
   Mesh-conformal Cauchy-Riemann least squares with two pinned boundary
   vertices per connected UV chart, matrix-free conjugate gradient solve.
   Preserves intentional UV seam cuts; xatlas handles final chart packing.
   No bundled CDN, no assumptions about humanoid geometry. */
const xyz=(p,i)=>p.slice(3*i,3*i+3);
const uv=(u,i)=>u.slice(2*i,2*i+2);
const coordKey=(p,i)=>xyz(p,i).map(x=>Number(x).toFixed(6)).join(',');
const uvKey=(u,i)=>uv(u,i).map(x=>Number(x).toFixed(6)).join(',');
const dist2=(a,b)=>a.reduce((s,x,i)=>s+(x-b[i])**2,0);
const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const norm=a=>Math.hypot(...a);
class UnionFind{
 constructor(n){this.a=Array.from({length:n},(_,i)=>i);}
 root(i){while(this.a[i]!==i){this.a[i]=this.a[this.a[i]];i=this.a[i];}return i;}
 join(i,j){i=this.root(i);j=this.root(j);if(i!==j)this.a[j]=i;}
}
export function deriveSeamCharts(source,faceMaterialData=null){
 const {positions:p,uvs:u,indices:ix}=source;
 if(!u||u.length!==p.length/3*2)throw Error('LSCM requires a premarked UV seam layout');
 const n=ix.length/3,dsu=new UnionFind(n),edges=new Map();
 for(let f=0;f<n;f++){
  for(let k=0;k<3;k++){
   const a=ix[3*f+k],b=ix[3*f+(k+1)%3];
   const aa=coordKey(p,a)+'@'+uvKey(u,a),bb=coordKey(p,b)+'@'+uvKey(u,b);
   const key=aa<bb?aa+'|'+bb:bb+'|'+aa;
   if(edges.has(key)){
    const prev=edges.get(key);
    if(!faceMaterialData||faceMaterialData[f]===faceMaterialData[prev])
     dsu.join(f,prev);
   }else edges.set(key,f);
  }
 }
 const faces=new Map();
 for(let f=0;f<n;f++){
  const root=dsu.root(f);
  if(!faces.has(root))faces.set(root,[]);
  faces.get(root).push(f);
 }
 const groups=[...faces.values()].sort((a,b)=>b.length-a.length);
 return groups;
}
function flattenChart(source,faceIDs){
 const {positions:p,uvs:u,indices:ix}=source;
 const nodes=[],nodeIndex=new Map(),triangles=[],localFaces=[];
 for(const f of faceIDs){
  const tri=[];
  for(let j=0;j<3;j++){
   const original=ix[f*3+j];
   const key=coordKey(p,original)+'@'+uvKey(u,original);
   if(!nodeIndex.has(key)){
    nodeIndex.set(key,nodes.length);
    nodes.push({position:xyz(p,original),original});
   }
   tri.push(nodeIndex.get(key));
  }
  if(new Set(tri).size!==3)throw Error('Collapsed 3D UV chart triangle');
  triangles.push(tri);localFaces.push(f);
 }
 const n=nodes.length;if(n<3)throw Error('Invalid small UV chart');
 const edgeCount=new Map();
 const terms=[];
 for(const tri of triangles){
  for(let k=0;k<3;k++){
   const a=tri[k],b=tri[(k+1)%3],key=a<b?a+'|'+b:b+'|'+a;
   edgeCount.set(key,{a,b,count:(edgeCount.get(key)?.count||0)+1});
  }
  const [a,b,c]=tri.map(i=>nodes[i].position);
  const e1=b.map((v,k)=>v-a[k]),e2=c.map((v,k)=>v-a[k]);
  const x1=norm(e1),x2=dot(e1,e2)/(x1||1);
  const y2=Math.sqrt(Math.max(0,dot(e2,e2)-x2*x2));
  if(x1<1e-9||y2<1e-9)throw Error('Degenerate triangle in LSCM chart');
  const w=x1*y2/2,den=2*w;
  const gx=[-y2/den,y2/den,0];
  const gy=[(x2-x1)/den,-x2/den,x1/den];
  const ids=[tri[0],tri[1],tri[2],n+tri[0],n+tri[1],n+tri[2]];
  terms.push({ids,a:[...gx,...gy.map(x=>-x)],b:[...gy,...gx],w});
 }
 const boundaries=new Set();
 for(const v of edgeCount.values())if(v.count===1){boundaries.add(v.a);boundaries.add(v.b);}
 if(boundaries.size<2)throw Error('Chart has no usable seam boundary; mark a cut before LSCM');
 // Geodesically distant boundary pins stabilize scale, translation and
 // rotation while allowing the remaining vertices to relax conformally.
 const boundary=[...boundaries];
 let pinA=boundary[0],pinB=boundary[1],max=-1;
 for(let i=0;i<boundary.length;i++)for(let j=i+1;j<boundary.length;j++){
  const d=dist2(nodes[boundary[i]].position,nodes[boundary[j]].position);
  if(d>max){max=d;pinA=boundary[i];pinB=boundary[j];}
 }
 if(max<1e-12)throw Error('UV chart has coincident boundary pins');
 const fixed=new Float64Array(n*2);fixed[pinB]=Math.sqrt(max);
 const pinned=new Set([pinA,pinB,n+pinA,n+pinB]);
 const apply=x=>{
  const out=new Float64Array(n*2);
  for(const {ids,a,b,w} of terms){
   let x1=0,x2=0;
   for(let k=0;k<6;k++){x1+=a[k]*x[ids[k]];x2+=b[k]*x[ids[k]];}
   for(let k=0;k<6;k++)out[ids[k]]+=w*(a[k]*x1+b[k]*x2);
  }
  for(const k of pinned)out[k]=0;
  return out;
 };
 const b=apply(fixed);for(let k=0;k<b.length;k++)b[k]=-b[k];
 const sol=new Float64Array(n*2),r=b.slice(),direction=b.slice();
 let rr=dot(r,r),init=rr,iterations=0;
 for(;iterations<Math.max(120,Math.min(1000,n*2));iterations++){
  if(rr<=init*1e-13+1e-18)break;
  const q=apply(direction),den=dot(direction,q);
  if(!(den>1e-20))break;
  const alpha=rr/den;
  for(let k=0;k<sol.length;k++){
   sol[k]+=alpha*direction[k];
   r[k]-=alpha*q[k];
  }
  const next=dot(r,r);
  if(next<=init*1e-13+1e-18){rr=next;break;}
  const beta=next/rr;
  for(let k=0;k<direction.length;k++)direction[k]=r[k]+beta*direction[k];
  rr=next;
 }
 for(let k=0;k<sol.length;k++)sol[k]+=fixed[k];
 if(sol.some(x=>!Number.isFinite(x)))throw Error('LSCM linear solve diverged');
 let positive=0,negative=0,area2=0,area3=0;
 for(const tri of triangles){
  const [a,b,c]=tri.map(i=>[sol[i],sol[n+i]]);
  const area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  if(area>1e-11)positive++;if(area< -1e-11)negative++;
  area2+=Math.abs(area)/2;
 }
 const flip=negative>positive;
 const bad=flip?positive:negative;
 if(bad>Math.max(2,triangles.length*.035))
  throw Error('LSCM chart folds over: '+bad+'/'+triangles.length+' faces; add seam');
 if(area2<1e-12)throw Error('LSCM chart collapses');
 for(const {w} of terms)area3+=w;
 const scale=Math.sqrt(area3/area2);
 const values=nodes.map((_,i)=>[sol[i]*scale,(flip?-sol[n+i]:sol[n+i])*scale]);
 const minx=Math.min(...values.map(v=>v[0])),miny=Math.min(...values.map(v=>v[1]));
 for(const v of values){v[0]-=minx;v[1]-=miny;}
 return {nodes,triangles,faces:localFaces,uvs:values,iterations,foldovers:bad};
}
export function flattenSeamedMesh(source,faceMaterialData=null){
 const groups=deriveSeamCharts(source,faceMaterialData);
 if(groups.length>96)throw Error('Existing UV seams fragment the mesh into '+groups.length+' charts; simplify seams');
 const p=[],uv=[],indices=Array(source.indices.length),materials=new Uint32Array(source.indices.length/3);
 let chartIndex=0,totalIterations=0;
 for(const group of groups){
  const chart=flattenChart(source,group);
  const offset=p.length/3;
  chart.nodes.forEach((n,i)=>{
   p.push(...n.position);uv.push(...chart.uvs[i]);
  });
  chart.faces.forEach((face,i)=>{
   for(let k=0;k<3;k++)indices[face*3+k]=offset+chart.triangles[i][k];
   materials[face]=chartIndex+1;
  });
  totalIterations+=chart.iterations;chartIndex++;
 }
 if(indices.some(v=>!Number.isInteger(v)))throw Error('LSCM output has missing triangle indices');
 return {positions:p,uvs:uv,indices,faceMaterialData:materials,
         charts:groups.length,totalIterations};
}
