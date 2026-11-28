// Replay the measured anatomically grouped layout on the exact packed humanoid.
// Input must be candidate 1 or a candidate with the same chart topology and extents.
// No original scene is overwritten. Preserve existing whole-atlas diagnostic checker.
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const receipt=JSON.parse(fs.readFileSync(new URL('../docs/qa/uv-grouped-20261127.json',import.meta.url),'utf8'));
export function groupedPack(mesh){
 const {positions,indices,uvs}=mesh,n=positions.length/3,parent=Array.from({length:n},(_,i)=>i);
 const find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i]}return i};
 const join=(a,b)=>{a=find(a);b=find(b);if(a!==b)parent[b]=a};
 for(let k=0;k<indices.length;k+=3){join(indices[k],indices[k+1]);join(indices[k],indices[k+2]);}
 const g=new Map();for(const i of new Set(indices)){const id=find(i);if(!g.has(id))g.set(id,[]);g.get(id).push(i);}
 const groups=[...g.values()];
 if(n!==6418||indices.length/3!==11492||JSON.stringify(groups.map(x=>x.length))!==JSON.stringify(receipt.chartVertexCounts))throw Error('Wrong humanoid chart topology');
 const scale=receipt.scaleRelativeToCandidate1,out=uvs.slice(),boxes=[];
 for(const [id,x,y,rot] of receipt.placement){
  const ids=groups[id],u=ids.map(i=>uvs[2*i]),v=ids.map(i=>uvs[2*i+1]),a=Math.min(...u),b=Math.min(...v),w=Math.max(...u)-a,h=Math.max(...v)-b;
  const W=(rot?h:w)*scale,H=(rot?w:h)*scale;
  for(const i of ids){const U=uvs[2*i]-a,V=uvs[2*i+1]-b;out[2*i]=x+(rot?V:U)*scale;out[2*i+1]=y+(rot?w-U:V)*scale;}
  boxes.push({id,x,y,w:W,h:H});
 }
 if(out.some(x=>!Number.isFinite(x)||x<0||x>1+1e-8))throw Error('UV bounds regression');
 const gutter=16/2048-1e-7;
 for(const b of boxes)if(b.x<8/2048-1e-7||b.y<8/2048-1e-7||b.x+b.w>1-8/2048+1e-7||b.y+b.h>1-8/2048+1e-7)throw Error('Atlas edge gutter regression');
 for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){
  const a=boxes[i],b=boxes[j],sep=Math.max(b.x-a.x-a.w,a.x-b.x-b.w,b.y-a.y-a.h,a.y-b.y-b.h);
  if(sep<gutter)throw Error('Chart gutter regression '+a.id+' '+b.id);
 }
 const area=(arr,k)=>{const [a,b,c]=indices.slice(k,k+3).map(i=>[arr[2*i],arr[2*i+1]]);return ((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2};
 let before=0,after=0;
 for(let k=0;k<indices.length;k+=3){const a=area(uvs,k),b=area(out,k);if(a<=0||b<=0||Math.abs(b-a*scale*scale)>1e-10)throw Error('UV shape/winding regression');before+=a;after+=b;}
 if(after<.52)throw Error('Grouped layout failed minimum coverage');
 return {uvs:out,report:{before,after,charts:groups.length,geometryChanged:false,pairedAnatomicalGroups:true}};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const source=process.argv[2],out=process.argv[3];if(!source||!out)throw Error('Usage: node group_humanoid_uv_candidate.mjs PACKED_SCENE OUT_DIR');
 const doc=JSON.parse(fs.readFileSync(source,'utf8')),part=doc.project.modelAtelier.parts[0],r=groupedPack(part.topologyMesh);
 part.topologyMesh.uvs=r.uvs;delete part.uvPaintPNG;
 fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'candidate.untextured.json'),JSON.stringify(doc));fs.writeFileSync(path.join(out,'grouped-report.json'),JSON.stringify(r.report,null,2)+'\n');console.log('SWRLZ_UV_GROUPED_PACK_PASS',JSON.stringify(r.report));
}
