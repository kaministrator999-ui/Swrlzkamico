// Candidate 2: fixed-boundary local conformal relaxation, followed by the tested packing search.
import fs from 'node:fs';
import path from 'node:path';
import {repack} from './repack_humanoid_uv_candidate.mjs';
export function relaxUV(mesh){
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
export function auditOverlap(mesh){
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
const source=process.argv[2],out=process.argv[3];
if(!source||!out)throw Error('Usage: node relax_humanoid_uv_candidate.mjs SOURCE OUT_DIR');
fs.mkdirSync(out,{recursive:true});
const doc=JSON.parse(fs.readFileSync(source,'utf8'));
const part=doc.project.modelAtelier.parts[0],mesh=part.topologyMesh;
const beforeAudit=auditOverlap(mesh),relaxation=relaxUV(mesh),relaxed={...mesh,uvs:relaxation.uvs};
const afterRelaxationAudit=auditOverlap(relaxed),packed=repack(relaxed),candidate={...mesh,uvs:packed.uvs};
const afterPackingAudit=auditOverlap(candidate);
for(const a of [beforeAudit,afterRelaxationAudit,afterPackingAudit])if(a.positiveAreaOverlapPairs||a.negativeWinding||a.degenerate)throw Error('UV overlap, winding or degeneracy regression');
part.topologyMesh=candidate;delete part.uvPaintPNG;
fs.writeFileSync(path.join(out,'candidate.untextured.json'),JSON.stringify(doc));
fs.writeFileSync(path.join(out,'packing-report.json'),JSON.stringify(packed.report,null,2)+'\n');
fs.writeFileSync(path.join(out,'relaxation-report.json'),JSON.stringify({...relaxation.report,beforeAudit,afterRelaxationAudit,afterPackingAudit},null,2)+'\n');
console.log('SWRLZ_UV_RELAX_PACK_AUDIT_PASS',JSON.stringify({stretch:relaxation.report.after,packing:packed.report,afterPackingAudit}));
