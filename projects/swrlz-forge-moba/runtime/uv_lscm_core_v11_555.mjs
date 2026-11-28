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


/** Place LSCM charts in one atlas without changing their relative scale.
 * Deterministic shelf packing with a globally uniform scale and pixel gutters.
 * Used if xatlas's UV-mesh packing yields no atlas. */
export function packSeamedCharts(flat,{resolution=2048,padding=8}={}){
 const groups=new Map();
 for(let f=0;f<flat.indices.length/3;f++){
  const id=flat.faceMaterialData[f];
  if(!groups.has(id))groups.set(id,new Set());
  for(let j=0;j<3;j++)groups.get(id).add(flat.indices[f*3+j]);
 }
 if(groups.size!==flat.charts||groups.size<1)throw Error('LSCM packing chart mismatch');
 const rects=[...groups].map(([id,ids])=>{
  const indices=[...ids],coords=indices.map(i=>flat.uvs.slice(2*i,2*i+2));
  const minU=Math.min(...coords.map(q=>q[0])),maxU=Math.max(...coords.map(q=>q[0]));
  const minV=Math.min(...coords.map(q=>q[1])),maxV=Math.max(...coords.map(q=>q[1]));
  const width=maxU-minU,height=maxV-minV;
  if(!(width>1e-8&&height>1e-8))throw Error('Collapsed LSCM chart '+id);
  return {id,indices,minU,minV,width,height};
 });
 const margin=Math.max(2,Math.min(24,padding))/resolution;
 function layout(scale){
  const order=rects.map(r=>({...r,w:r.width*scale+2*margin,h:r.height*scale+2*margin}))
   .sort((a,b)=>b.h-a.h||b.w-a.w||a.id-b.id);
  const shelves=[],placement=new Map();
  let usedHeight=0;
  for(const r of order){
   if(r.w>1||r.h>1)return null;
   let shelf=null;
   for(const s of shelves){
    if(r.h<=s.h+1e-10&&s.x+r.w<=1+1e-10){
     if(!shelf||s.x<shelf.x)shelf=s;
    }
   }
   if(!shelf){
    if(usedHeight+r.h>1+1e-10)return null;
    shelf={x:0,y:usedHeight,h:r.h};
    shelves.push(shelf);usedHeight+=r.h;
   }
   placement.set(r.id,{x:shelf.x+margin,y:shelf.y+margin});
   shelf.x+=r.w;
  }
  return placement;
 }
 let maxDim=Math.max(...rects.map(r=>Math.max(r.width,r.height)));
 let lower=0,upper=2/maxDim,best=null;
 for(let n=0;n<45;n++){
  const mid=(lower+upper)/2,attempt=layout(mid);
  if(attempt){lower=mid;best=attempt;}else upper=mid;
 }
 if(!best||lower<1e-7)throw Error('Could not pack LSCM seam charts with required padding');
 const uvs=new Array(flat.uvs.length).fill(NaN);
 for(const r of rects){
  const place=best.get(r.id);
  for(const i of r.indices){
   uvs[2*i]=place.x+(flat.uvs[2*i]-r.minU)*lower;
   uvs[2*i+1]=place.y+(flat.uvs[2*i+1]-r.minV)*lower;
  }
 }
 if(uvs.some(v=>!Number.isFinite(v)||v<0||v>1))
  throw Error('Packed LSCM charts leave UV 0–1 atlas');
 // Exact rectangle overlap test; do not infer success from a generated PNG.
 const boxes=rects.map(r=>({
  id:r.id,x:best.get(r.id).x-margin,
  y:best.get(r.id).y-margin,
  w:r.width*lower+2*margin,h:r.height*lower+2*margin
 }));
 for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
  const a=boxes[i],b=boxes[j];
  if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1e-7&&
     Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>1e-7)
     throw Error('Packed chart rectangles overlap: '+a.id+', '+b.id);
 }
 return {
  positions:flat.positions,indices:flat.indices,uvs,
  charts:flat.charts,width:resolution,height:resolution,
  lscmIterations:flat.totalIterations,
  packing:'deterministic-shelf',chartBoxes:boxes,
  chartScale:lower,paddingPixels:padding
 };
}


/* SE557: geometry-independent, bounded optimization of existing seam-split UVs.
   Derived from the validated humanoid experiments; no anatomical IDs. */
function se557Repack(mesh, resolution=2048, padding=8){
 const {positions,uvs,indices}=mesh, n=positions.length/3, parent=Array.from({length:n},(_,i)=>i);
 const find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i]}return i};
 const join=(a,b)=>{a=find(a);b=find(b);if(a!==b)parent[b]=a};
 for(let k=0;k<indices.length;k+=3){join(indices[k],indices[k+1]);join(indices[k],indices[k+2]);}
 const g=new Map();for(const i of new Set(indices)){const id=find(i);if(!g.has(id))g.set(id,[]);g.get(id).push(i)}
 const rects=[...g.values()].map((ids,id)=>{const u=ids.map(i=>uvs[2*i]),v=ids.map(i=>uvs[2*i+1]);const x=Math.min(...u),y=Math.min(...v);return {id,ids,x,y,w:Math.max(...u)-x,h:Math.max(...v)-y}});
 if(rects.some(r=>r.w<=0||r.h<=0))throw Error("collapsed chart");
 if(rects.length>96)throw Error('Too many UV islands for bounded interactive optimization');
 const pad=padding/resolution, eps=1e-10;
 const intersects=(a,b)=>a.x<b.x+b.w-eps&&b.x<a.x+a.w-eps&&a.y<b.y+b.h-eps&&b.y<a.y+a.h-eps;
 const inside=(a,b)=>a.x>=b.x-eps&&a.y>=b.y-eps&&a.x+a.w<=b.x+b.w+eps&&a.y+a.h<=b.y+b.h+eps;
 function pack(scale,sort,scoreMode,rotate){
  let free=[{x:0,y:0,w:1,h:1}],out=[];
  const order=rects.slice().sort((a,b)=>sort(b)-sort(a)||a.id-b.id);
  for(const r of order){
   let best=null;
   for(const f of free)for(const turn of (rotate?[false,true]:[false])){
    const w=(turn?r.h:r.w)*scale+2*pad,h=(turn?r.w:r.h)*scale+2*pad;
    if(w>f.w+eps||h>f.h+eps)continue;
    const dw=f.w-w,dh=f.h-h;
    const score=scoreMode===0?[Math.min(dw,dh),Math.max(dw,dh),f.y,f.x]:[f.w*f.h-w*h,Math.min(dw,dh),f.y,f.x];
    if(!best||score.some((v,i)=>v<best.score[i]-eps&&score.slice(0,i).every((x,j)=>Math.abs(x-best.score[j])<=eps)))best={id:r.id,x:f.x,y:f.y,w,h,turn,score};
   }
   if(!best)return null;
   let next=[];
   for(const f of free){
    if(!intersects(f,best)){next.push(f);continue;}
    const x2=f.x+f.w,y2=f.y+f.h,bx=best.x+best.w,by=best.y+best.h;
    if(best.x>f.x+eps)next.push({x:f.x,y:f.y,w:best.x-f.x,h:f.h});
    if(bx<x2-eps)next.push({x:bx,y:f.y,w:x2-bx,h:f.h});
    if(best.y>f.y+eps)next.push({x:f.x,y:f.y,w:f.w,h:best.y-f.y});
    if(by<y2-eps)next.push({x:f.x,y:by,w:f.w,h:y2-by});
   }
   free=next.filter((a,i)=>!next.some((b,j)=>i!==j&&inside(a,b)&&(!inside(b,a)||j<i)));
   out.push(best);
  }
  return out;
 }
 const sorts=[r=>r.w*r.h,r=>Math.max(r.w,r.h),r=>r.h,r=>r.w,r=>r.w+r.h];
 let best=null,attempts=[];
 for(let si=0;si<sorts.length;si++)for(let mode=0;mode<2;mode++)for(const rotate of [false,true]){
  let lo=0,hi=1/Math.max(...rects.map(r=>Math.max(r.w,r.h))),result=null;
  for(let k=0;k<30;k++){const mid=(lo+hi)/2,p=pack(mid,sorts[si],mode,rotate);if(p){lo=mid;result=p}else hi=mid}
  attempts.push({sort:si,scoreMode:mode,rotate,scale:lo});
  if(result&&(!best||lo>best.scale))best={scale:lo,result,sort:si,scoreMode:mode,rotate};
 }
 if(!best||best.scale<=1.00001)return null;
 const output=uvs.slice(), boxes=best.result;
 for(const b of boxes){const r=rects[b.id];for(const i of r.ids){const u=uvs[2*i]-r.x,v=uvs[2*i+1]-r.y;output[2*i]=b.x+pad+(b.turn?v:u)*best.scale;output[2*i+1]=b.y+pad+(b.turn?r.w-u:v)*best.scale;}}
 if(output.some(x=>!Number.isFinite(x)||x<0||x>1))throw Error("out of atlas");
 for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++)if(intersects(boxes[i],boxes[j]))throw Error("chart overlap");
 function area(arr,k){const [a,b,c]=indices.slice(k,k+3).map(i=>[arr[2*i],arr[2*i+1]]);return ((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2}
 let before=0,after=0,flips=0,degenerate=0,maxAreaError=0;
 for(let k=0;k<indices.length;k+=3){const a=area(uvs,k),b=area(output,k);before+=Math.abs(a);after+=Math.abs(b);if(a*b<0)flips++;if(Math.abs(b)<1e-12)degenerate++;maxAreaError=Math.max(maxAreaError,Math.abs(b-a*best.scale**2));}
 if(flips||maxAreaError>1e-10)throw Error("chart shape or winding changed");
 return {uvs:output,report:{charts:rects.length,triangles:indices.length/3,vertices:n,baselineTriangleArea:before,candidateTriangleArea:after,relativeAreaGain:after/before-1,linearTexelGain:best.scale-1,scale:best.scale,flips,degenerate,maxAreaError,paddingPixels:padding,atlasResolution:resolution,rotatedCharts:boxes.filter(x=>x.turn).length,attempts,selected:{sort:best.sort,scoreMode:best.scoreMode,rotate:best.rotate},geometryChanged:false,interChartBoundingBoxOverlap:false}};
}
function se557Relax(mesh){
 const {positions:p,uvs:u,indices:ix}=mesh, out=u.slice(), n=p.length/3,faces=[],vFaces=Array.from({length:n},()=>[]),edges=new Map(),neighbors=Array.from({length:n},()=>new Set());
 for(let k=0;k<ix.length;k+=3){
  const ids=ix.slice(k,k+3),[a,b,c]=ids.map(i=>p.slice(i*3,i*3+3)),A=b.map((x,i)=>x-a[i]),B=c.map((x,i)=>x-a[i]),l=Math.hypot(...A),x=A.reduce((s,v,i)=>s+v*B[i],0)/l,y=Math.sqrt(Math.max(0,Math.hypot(...B)**2-x*x));
  if(!(l>1e-12&&y>1e-12))throw Error("Invalid triangle");
  const f={ids,l,x,y};faces.push(f);
  for(const i of ids)vFaces[i].push(faces.length-1);
  for(let j=0;j<3;j++){const i=ids[j],a=ids[(j+1)%3],key=i<a?i+":"+a:a+":"+i;edges.set(key,(edges.get(key)||0)+1);neighbors[i].add(a);neighbors[a].add(i);}
 }
 const boundary=new Set();for(const [key,count] of edges)if(count===1)key.split(":").map(Number).forEach(i=>boundary.add(i));
 function metrics(f,uv){
  const [a,b,c]=f.ids.map(i=>[uv[i*2],uv[i*2+1]]),du=b[0]-a[0],dv=b[1]-a[1],eu=c[0]-a[0],ev=c[1]-a[1],j00=du/f.l,j10=dv/f.l,j01=(eu-f.x*j00)/f.y,j11=(ev-f.x*j10)/f.y;
  const det=j00*j11-j01*j10,fro=j00*j00+j01*j01+j10*j10+j11*j11;
  return {ratio:det>0?(fro+Math.sqrt(Math.max(0,fro*fro-4*det*det)))/(2*det):Infinity,det};
 }
 const original=faces.map(f=>metrics(f,u));
 if(original.some(m=>!Number.isFinite(m.ratio)))throw Error("Baseline contains invalid UV triangles");
 function stats(uv){const m=faces.map(f=>metrics(f,uv)),a=m.map(m=>m.ratio).sort((a,b)=>a-b),d=m.map(m=>Math.sqrt(m.det)).sort((a,b)=>a-b),q=(ar,f)=>ar[Math.floor((ar.length-1)*f)];return {median:q(a,.5),p95:q(a,.95),p99:q(a,.99),max:a.at(-1),over2:a.filter(x=>x>2).length,densityP95P05:q(d,.95)/q(d,.05),invalid:m.filter(x=>!Number.isFinite(x.ratio)).length};}
 function local(i){let max=0,sum=0;for(const f of vFaces[i]){const m=metrics(faces[f],out),d=m.det/original[f].det;if(d<.35||d>2.85||!Number.isFinite(m.ratio))return [Infinity,Infinity];max=Math.max(max,m.ratio);sum+=Math.log(m.ratio)**2;}return [max,sum];}
 const moved=new Set(),history=[];
 for(let pass=0;pass<16;pass++){
  const ordered=faces.map((f,i)=>({i,ratio:metrics(f,out).ratio})).filter(x=>x.ratio>1.9).sort((a,b)=>b.ratio-a.ratio||a.i-b.i);
  const target=[...new Set(ordered.flatMap(x=>faces[x.i].ids).filter(i=>!boundary.has(i)))];let count=0;
  for(const i of target){
   const ox=out[i*2],oy=out[i*2+1],old=local(i);
   if(!Number.isFinite(old[0]))throw Error("Invalid local baseline");
   let best={x:ox,y:oy,score:old};
   const mean=[...neighbors[i]].reduce((s,j)=>s+Math.hypot(ox-out[j*2],oy-out[j*2+1]),0)/neighbors[i].size;
   for(const fraction of [.3,.15,.075,.0375,.01875,.009375]){
    const step=mean*fraction;
    for(let a=0;a<16;a++){const ang=a*Math.PI/8,x=ox+step*Math.cos(ang),y=oy+step*Math.sin(ang);if(x<0||x>1||y<0||y>1)continue;out[2*i]=x;out[2*i+1]=y;const s=local(i);
     if(s[0]<best.score[0]-1e-7||(Math.abs(s[0]-best.score[0])<1e-7&&s[1]<best.score[1]-1e-8))best={x,y,score:s};}
   }
   out[2*i]=best.x;out[2*i+1]=best.y;if(best.x!==ox||best.y!==oy){moved.add(i);count++;}
  }
  history.push({pass:pass+1,moved:count,...stats(out)});if(!count)break;
 }
 const before=stats(u),after=stats(out);
 if(after.invalid||after.max>=before.max||after.p95>before.p95*1.01||after.p99>before.p99*1.05||after.densityP95P05>before.densityP95P05*1.01)throw Error("Relaxation did not meet quality gate");
 for(const i of boundary)if(out[i*2]!==u[i*2]||out[i*2+1]!==u[i*2+1])throw Error("Boundary moved");
 return {uvs:out,report:{before,after,movedVertices:moved.size,fixedBoundaryVertices:boundary.size,history,geometryChanged:false,seamsChanged:false}};
}
function se557Audit(mesh){
 const {uvs:u,indices:ix}=mesh,tris=[],bins=new Map(),N=64;
 const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
 const polyArea=poly=>Math.abs(poly.reduce((v,a,i)=>{const b=poly[(i+1)%poly.length];return v+a[0]*b[1]-a[1]*b[0]},0))/2;
 function intersect(a,b){let poly=a.slice(),sign=cross(...b)>0?1:-1;for(let k=0;k<3;k++){const c=b[k],d=b[(k+1)%3],next=[];for(let i=0;i<poly.length;i++){const x=poly[i],y=poly[(i+1)%poly.length],dx=sign*cross(c,d,x),dy=sign*cross(c,d,y);if(dx>=-1e-13)next.push(x);if((dx>0&&dy<0)||(dx<0&&dy>0)){const t=dx/(dx-dy);next.push([x[0]+(y[0]-x[0])*t,x[1]+(y[1]-x[1])*t]);}}poly=next;if(poly.length<3)return 0;}return polyArea(poly);}
 let overlapCount=0,overlapArea=0,degenerate=0,neg=0,positive=0,checkedPairs=0;
 for(let k=0;k<ix.length;k+=3){
  const t=ix.slice(k,k+3).map(i=>u.slice(i*2,i*2+2)),area=cross(...t)/2;
  if(area<0)neg++;if(area>0)positive++;if(Math.abs(area)<1e-12){degenerate++;continue;}
  const box=[Math.min(...t.map(a=>a[0])),Math.min(...t.map(a=>a[1])),Math.max(...t.map(a=>a[0])),Math.max(...t.map(a=>a[1]))];
  const cells=[],seen=new Set();
  for(let a=Math.max(0,Math.floor(box[0]*N));a<=Math.min(N-1,Math.floor(box[2]*N));a++)for(let b=Math.max(0,Math.floor(box[1]*N));b<=Math.min(N-1,Math.floor(box[3]*N));b++){const key=b*N+a;cells.push(key);for(const i of bins.get(key)||[])seen.add(i);}
  for(const i of seen){const o=tris[i];if(o.box[0]>=box[2]||o.box[1]>=box[3]||o.box[2]<=box[0]||o.box[3]<=box[1])continue;checkedPairs++;const a=intersect(t,o.t);if(a>1e-10){overlapCount++;overlapArea+=a;}}
  const id=tris.length;tris.push({t,box});for(const c of cells){if(!bins.has(c))bins.set(c,[]);bins.get(c).push(id);}
 }
 return {triangles:ix.length/3,degenerate,positiveWinding:positive,negativeWinding:neg,checkedPairs,positiveAreaOverlapPairs:overlapCount,overlapAreaPairwise:overlapArea,overlapTolerance:1e-10};
}
export function optimizeExistingUV(source,{resolution=2048,padding=8}={}){
 const {positions,indices,uvs}=source;
 if(!Array.isArray(positions)||!Array.isArray(indices)||!Array.isArray(uvs)||positions.length%3||indices.length%3||uvs.length!==positions.length/3*2||!indices.length||positions.length>60000||indices.length>120000)throw Error('Expected a bounded indexed editable topology mesh');
 if(positions.some(x=>!Number.isFinite(x))||uvs.some(x=>!Number.isFinite(x)||x<0||x>1)||indices.some(i=>!Number.isInteger(i)||i<0||i>=positions.length/3))throw Error('Unsupported UV coordinates or indices');
 if(!Number.isInteger(resolution)||resolution<256||resolution>4096||!Number.isInteger(padding)||padding<2||padding>24)throw Error('Invalid atlas parameters');
 const before=se557Audit(source);
 if(before.degenerate||before.negativeWinding||before.positiveAreaOverlapPairs)throw Error('Existing UVs contain overlaps, reversed faces or collapsed triangles; use a separate unwrap preview');
 let result=source,relaxation=null,packing=null;
 try{
  const r=se557Relax(source),a=se557Audit({...source,uvs:r.uvs});
  if(!a.degenerate&&!a.negativeWinding&&!a.positiveAreaOverlapPairs){result={...source,uvs:r.uvs};relaxation=r.report;}
 }catch(e){if(!/Relaxation did not meet quality gate/.test(String(e)))throw e;}
 const packed=se557Repack(result,resolution,padding);
 if(packed){result={...source,uvs:packed.uvs};packing=packed.report;}
 const after=se557Audit(result);
 if(after.degenerate||after.negativeWinding||after.positiveAreaOverlapPairs)throw Error('Optimized atlas failed exact triangle audit');
 return {positions,indices,uvs:result.uvs.slice(),changed:!!(packing||relaxation),report:{before,after,packing,relaxation,geometryChanged:false,seamsChanged:false}};
}
