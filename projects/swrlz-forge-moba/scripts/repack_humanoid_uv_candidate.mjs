// Experimental non-destructive packing of the exact native starter UV charts.
// Preserves mesh geometry, chart connectivity, triangle shape and winding.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
export function repack(mesh, resolution=2048, padding=8){
 const {positions,uvs,indices}=mesh, n=positions.length/3, parent=Array.from({length:n},(_,i)=>i);
 const find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i]}return i};
 const join=(a,b)=>{a=find(a);b=find(b);if(a!==b)parent[b]=a};
 for(let k=0;k<indices.length;k+=3){join(indices[k],indices[k+1]);join(indices[k],indices[k+2]);}
 const g=new Map();for(const i of new Set(indices)){const id=find(i);if(!g.has(id))g.set(id,[]);g.get(id).push(i)}
 const rects=[...g.values()].map((ids,id)=>{const u=ids.map(i=>uvs[2*i]),v=ids.map(i=>uvs[2*i+1]);const x=Math.min(...u),y=Math.min(...v);return {id,ids,x,y,w:Math.max(...u)-x,h:Math.max(...v)-y}});
 if(rects.some(r=>r.w<=0||r.h<=0))throw Error("collapsed chart");
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
 if(!best||best.scale<=1.00001)throw Error("No packing improvement; preserve original");
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
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const source=process.argv[2],out=process.argv[3];
 if(!source||!out)throw Error('Usage: node repack_humanoid_uv_candidate.mjs SOURCE OUT_DIR');
 fs.mkdirSync(out,{recursive:true});
 const doc=JSON.parse(fs.readFileSync(source,'utf8'));
 const part=doc.project.modelAtelier.parts[0];
 const result=repack(part.topologyMesh);
 part.topologyMesh.uvs=result.uvs;
 // The original paint does not match new UVs. Rebuilt by the QA renderer before use.
 delete part.uvPaintPNG;
 fs.writeFileSync(path.join(out,'candidate.untextured.json'),JSON.stringify(doc));
 fs.writeFileSync(path.join(out,'packing-report.json'),JSON.stringify(result.report,null,2)+'\n');
 console.log(JSON.stringify(result.report));
}
