/* SE559: experimental anatomical painting atlas. Rigid chart rotation, translation and uniform scale only. */
export function anatomicalUV559(mesh,{resolution=2048,padding=8}={}){
 const {positions:p,uvs:u,indices:ix}=mesh,counts=[715,715,135,475,475,193,99,777,64,64,64,64,50,99,777,64,64,64,64,50,673,673];
 if(!Array.isArray(p)||!Array.isArray(u)||!Array.isArray(ix)||u.length!==p.length/3*2||ix.length%3||!ix.length||u.some(v=>!Number.isFinite(v)||v<0||v>1)||p.some(v=>!Number.isFinite(v))||ix.some(v=>!Number.isInteger(v)||v<0||v>=u.length/2)||!Number.isInteger(resolution)||resolution<256||resolution>4096||!Number.isInteger(padding)||padding<2||padding>24)throw Error("Invalid anatomical atlas input");
 const par=Array.from({length:u.length/2},(_,i)=>i),root=i=>{while(par[i]!==i){par[i]=par[par[i]];i=par[i]}return i};
 for(let k=0;k<ix.length;k+=3){par[root(ix[k+1])]=root(ix[k]);par[root(ix[k+2])]=root(ix[k])}
 const groups=new Map();for(let k=0;k<ix.length;k+=3){const r=root(ix[k]);if(!groups.has(r))groups.set(r,new Set());ix.slice(k,k+3).forEach(i=>groups.get(r).add(i))}
 const shells=[...groups.values()].map(s=>[...s]);
 if(shells.length!==22||shells.some((s,i)=>s.length!==counts[i]))throw Error("Requires verified 22-shell humanoid topology");
 const mean=(vs,fn)=>vs.reduce((a,v)=>a+fn(v),0)/vs.length;
 for(const [a,b] of [[0,1],[3,4]])if(mean(shells[a],v=>p[3*v+2])<mean(shells[b],v=>p[3*v+2]))[shells[a],shells[b]]=[shells[b],shells[a]];
 const g=Object.fromEntries(shells.map((vs,i)=>{
  const id=i+1,M=fn=>mean(vs,fn),world=[0,1,2].map(k=>M(v=>p[3*v+k]));
  if(([1,4].includes(id)&&world[2]<=0)||([2,5].includes(id)&&world[2]>=0)||([7,8,9,10,11,12,13,21].includes(id)&&world[0]>=0)||([14,15,16,17,18,19,20,22].includes(id)&&world[0]<=0)||([4,5,6].includes(id)&&world[1]<4)||([21,22].includes(id)&&world[1]>2.3))throw Error("Unexpected anatomy "+id);
  const x=M(v=>u[2*v]),y=M(v=>u[2*v+1]);let angle=0,alignment=null;
  if([1,2,4,5,8,15,21,22].includes(id)){
   const axis=[8,15].includes(id)?0:1,sign=id===15?-1:1,z=world[axis]*sign;
   const a=M(v=>(u[2*v]-x)**2),b=M(v=>(u[2*v]-x)*(u[2*v+1]-y)),c=M(v=>(u[2*v+1]-y)**2),d=M(v=>(u[2*v]-x)*(p[3*v+axis]*sign-z)),e=M(v=>(u[2*v+1]-y)*(p[3*v+axis]*sign-z)),det=a*c-b*b;
   if(det<1e-15)throw Error("Degenerate orientation fit");
   const gx=(c*d-b*e)/det,gy=(a*e-b*d)/det;
   if(Math.hypot(gx,gy)<1e-8)throw Error("Undefined orientation");
   angle=Math.PI/2-Math.atan2(gy,gx);alignment=(gx*Math.sin(angle)+gy*Math.cos(angle))/Math.hypot(gx,gy);
  }
  const c=Math.cos(angle),s=Math.sin(angle),points=vs.map(v=>[u[2*v]*c-u[2*v+1]*s,u[2*v]*s+u[2*v+1]*c]),min=[0,1].map(k=>Math.min(...points.map(v=>v[k]))),max=[0,1].map(k=>Math.max(...points.map(v=>v[k])));
  return [id,{vs,points,min,w:max[0]-min[0],h:max[1]-min[1],alignment}];
 }));
 const margin=padding/resolution,gap=2*margin;
 function pack(scale){
  const boxes={},w=id=>g[id].w*scale,h=id=>g[id].h*scale,put=(id,x,y)=>boxes[id]={id,x,y,w:w(id),h:h(id)},center=(id,x,y)=>put(id,x-w(id)/2,y);
  const legW=w(21)+w(22)+gap,legH=Math.max(h(21),h(22)),total=legH+h(1)+h(4)+2*gap,bottom=(1-total)/2;
  put(21,(1-legW)/2,bottom);put(22,(1-legW)/2+w(21)+gap,bottom);center(1,.5,bottom+legH+gap);center(4,.5,bottom+legH+gap+h(1)+gap);
  put(8,margin,1-margin-h(8));put(15,1-margin-w(15),1-margin-h(15));
  const leftCenter=(margin+boxes[21].x-gap)/2,rightCenter=(boxes[22].x+boxes[22].w+gap+1-margin)/2;
  center(2,leftCenter,margin);center(5,leftCenter,margin+h(2)+gap);center(3,rightCenter,margin);center(6,rightCenter,margin+h(3)+gap);
  function fingers(rows,arm){let top=boxes[arm].y-gap,mid=boxes[arm].x+boxes[arm].w/2;for(const row of rows){const width=row.reduce((s,id)=>s+w(id),0)+(row.length-1)*gap,height=Math.max(...row.map(h));let x=mid-width/2;for(const id of row){put(id,x,top-height);x+=w(id)+gap}top-=height+gap}}
  fingers([[7,9,10],[11,12,13]],8);fingers([[14,16,17],[18,19,20]],15);
  const list=Object.values(boxes);if(list.length!==22||list.some(b=>b.x<margin||b.y<margin||b.x+b.w>1-margin||b.y+b.h>1-margin))return null;
  for(let i=0;i<list.length;i++)for(let j=i+1;j<list.length;j++){const a=list[i],b=list[j];if(a.x<b.x+b.w+gap-1e-10&&b.x<a.x+a.w+gap-1e-10&&a.y<b.y+b.h+gap-1e-10&&b.y<a.y+a.h+gap-1e-10)return null}
  return boxes;
 }
 let lo=0,hi=1.5,boxes=null;for(let k=0;k<48;k++){const mid=(lo+hi)/2,b=pack(mid);if(b){lo=mid;boxes=b}else hi=mid}
 if(!boxes||lo<.4)throw Error("No adequate anatomical packing");
 const out=u.slice();for(const b of Object.values(boxes)){const sh=g[b.id];sh.vs.forEach((v,k)=>{out[2*v]=b.x+(sh.points[k][0]-sh.min[0])*lo;out[2*v+1]=b.y+(sh.points[k][1]-sh.min[1])*lo})}
 const area=(a,k)=>{const [i,j,l]=ix.slice(k,k+3);return ((a[2*j]-a[2*i])*(a[2*l+1]-a[2*i+1])-(a[2*j+1]-a[2*i+1])*(a[2*l]-a[2*i]))/2};let before=0,after=0,maxAreaError=0;
 for(let k=0;k<ix.length;k+=3){const a=area(u,k),b=area(out,k);if(a<=1e-12||b<=1e-12)throw Error("Invalid UV winding or collapsed face");before+=a;after+=b;maxAreaError=Math.max(maxAreaError,Math.abs(b-a*lo*lo))}
 if(maxAreaError>1e-10||out.some(v=>!Number.isFinite(v)||v<0||v>1))throw Error("Anatomical packing integrity failure");
 return {positions:p,indices:ix,uvs:out,changed:true,report:{mode:"ai-anatomical",packing:{baselineTriangleArea:before,candidateTriangleArea:after,scale:lo,paddingPixels:padding,atlasResolution:resolution,maxAreaError,geometryChanged:false,interChartBoundingBoxOverlap:false},alignment:Object.fromEntries([1,2,4,5,8,15,21,22].map(i=>[i,g[i].alignment])),boxes}};
}
