/* SE503_UV_ISLAND_MATH_START
   Deterministic panel-projection UV atlas for editable indexed topologyMesh.
   Source positions and triangle order remain unchanged. UV seam vertices are
   duplicated only when needed. This is a beta projection, not a claim that
   arbitrary concave surfaces have a non-overlapping conformal unwrap. */
const se503AtlasMath=(()=>{
 'use strict';
 const LIMIT_VERTICES=9000, LIMIT_FACES=16000;
 const layouts=[
  {name:'Front',rect:[.025,.310,.485,.975],color:'#4ac6e9'},
  {name:'Back',rect:[.515,.310,.975,.975],color:'#bd91e5'},
  {name:'Brim / top',rect:[.025,.025,.485,.275],color:'#eac96f'},
  {name:'Underside',rect:[.515,.025,.975,.275],color:'#71cc9d'}
 ];
 const finite=a=>Array.isArray(a)&&a.every(Number.isFinite);
 const vector=(t,id)=>t.positions.slice(id*3,id*3+3);
 function groupFor(p,cut,normal,preset){
  const cy=(p[0][1]+p[1][1]+p[2][1])/3;
  const cz=(p[0][2]+p[1][2]+p[2][2])/3;
  const ny=normal[1],size=Math.hypot(...normal);
  if(preset==='panels-rim'&&cy<=cut&&size>1e-12&&Math.abs(ny)/size>=.65)
   return ny>=0?2:3;
  return cz>=0?0:1;
 }
 function project(p,kind){
  if(kind===0)return [Math.atan2(p[0],Math.abs(p[2])+1e-10),p[1]];
  if(kind===1)return [Math.atan2(-p[0],Math.abs(p[2])+1e-10),p[1]];
  if(kind===2)return [p[0],p[2]];
  return [p[0],-p[2]];
 }
 function unwrap(source,options={}){
  const t=source;
  if(!t||!finite(t.positions)||!finite(t.uvs)||!Array.isArray(t.indices))
   throw Error('Select a valid indexed, editable topology mesh.');
  const n=t.positions.length/3,f=t.indices.length/3;
  if(!Number.isInteger(n)||!Number.isInteger(f)||n<3||f<1||n>LIMIT_VERTICES||f>LIMIT_FACES
    ||t.uvs.length!==n*2||!t.indices.every(i=>Number.isInteger(i)&&i>=0&&i<n))
   throw Error('Mesh exceeds supported native vertices/faces or has invalid indices.');
  const preset=options.preset==='panels'?'panels':'panels-rim';
  const cutFraction=Math.max(.08,Math.min(.34,Number(options.brimFraction)||.18));
  let yMin=Infinity,yMax=-Infinity;
  for(let i=1;i<t.positions.length;i+=3){
   yMin=Math.min(yMin,t.positions[i]);yMax=Math.max(yMax,t.positions[i]);
  }
  if(yMax-yMin<1e-6)throw Error('A vertical model axis is required. Rotate the mesh to upright first.');
  const cut=yMin+(yMax-yMin)*cutFraction;
  const tris=[],stats=layouts.map((x,id)=>({id,name:x.name,color:x.color,
    count:0,bounds:[Infinity,Infinity,-Infinity,-Infinity],rect:x.rect,collapsed:0}));
  for(let i=0;i<t.indices.length;i+=3){
   const ids=t.indices.slice(i,i+3);
   if(new Set(ids).size!==3)throw Error('A mesh triangle repeats a vertex.');
   const p=ids.map(id=>vector(t,id));
   const ab=p[1].map((v,k)=>v-p[0][k]),ac=p[2].map((v,k)=>v-p[0][k]);
   const normal=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
   if(Math.hypot(...normal)<1e-13)throw Error('Source contains a zero-area 3D triangle.');
   const group=groupFor(p,cut,normal,preset);
   const coords=p.map(v=>project(v,group));
   const info=stats[group];info.count++;
   for(const [u,v] of coords){
    info.bounds[0]=Math.min(info.bounds[0],u);info.bounds[1]=Math.min(info.bounds[1],v);
    info.bounds[2]=Math.max(info.bounds[2],u);info.bounds[3]=Math.max(info.bounds[3],v);
   }
   tris.push({ids,group,coords});
  }
  for(const s of stats){
   if(!s.count)continue;
   const [a,b,c,d]=s.bounds;
   if(c-a<1e-9||d-b<1e-9)throw Error('Projected '+s.name+' island has no width or height.');
   const [u0,v0,u1,v1]=s.rect;
   const inner=.005;
   const availableU=u1-u0-2*inner,availableV=v1-v0-2*inner;
   s.factor=Math.min(availableU/(c-a),availableV/(d-b));
   s.center=[(u0+u1)/2,(v0+v1)/2];s.base=[(a+c)/2,(b+d)/2];
  }
  const next={positions:t.positions.slice(),uvs:t.uvs.slice(),indices:[]},map=new Map();
  const meshToAtlas=[],newFaces=[];
  for(const tri of tris){
   const s=stats[tri.group],uvTriangle=[],idx=[];
   for(let k=0;k<3;k++){
    const original=tri.ids[k],key=original+':'+tri.group;
    let mapped=map.get(key);
    if(mapped===undefined){
     // Preserve the original vertex index for the first island using it.
     mapped=map.has(original+':owned')?next.positions.length/3:original;
     if(mapped===next.positions.length/3){
      if(mapped>=LIMIT_VERTICES)throw Error(
       'Seam duplication needs more than 9000 vertices; reduce mesh density or simplify seams.');
      next.positions.push(...vector(t,original));
      next.uvs.push(0,0);
     }else map.set(original+':owned',true);
     map.set(key,mapped);
    }
    const q=tri.coords[k];
    const u=s.center[0]+(q[0]-s.base[0])*s.factor;
    const v=s.center[1]+(q[1]-s.base[1])*s.factor;
    if(u<0||u>1||v<0||v>1)throw Error('UV packing overflow.');
    next.uvs[mapped*2]=u;next.uvs[mapped*2+1]=v;
    idx.push(mapped);uvTriangle.push([u,v]);
   }
   const area=Math.abs((uvTriangle[1][0]-uvTriangle[0][0])*
    (uvTriangle[2][1]-uvTriangle[0][1])-
    (uvTriangle[2][0]-uvTriangle[0][0])*
    (uvTriangle[1][1]-uvTriangle[0][1]))*.5;
   if(area<1e-10)s.collapsed++;
   next.indices.push(...idx);
   newFaces.push({group:tri.group,ids:idx,sourceIds:tri.ids,uv:uvTriangle});
  }
  if(next.positions.length/3>LIMIT_VERTICES)
   throw Error('Native vertex limit exceeded after UV seams.');
  if(!finite(next.uvs)||next.uvs.length!==next.positions.length/3*2)
   throw Error('Generated UV coordinates are invalid.');
  return {data:next,stats:stats.filter(s=>s.count).map(({id,name,color,count,rect,collapsed})=>({
    id,name,color,triangles:count,rect,collapsed})),
   faces:newFaces,originalVertices:n,vertices:next.positions.length/3,
   duplicatedVertices:next.positions.length/3-n,triangles:f,
   collapsed:newFaces.length?stats.reduce((n,s)=>n+s.collapsed,0):0,
   preset,brimFraction:cutFraction};
 }
 // Remap a saved face marker by barycentric location on the FRONT island.
 // Ambiguous source UVs must be re-picked by the artist after applying.
 function remapCenter(source,result,u,v){
  if(!Number.isFinite(u)||!Number.isFinite(v))return null;
  let found=null;
  for(const face of result.faces){
   if(face.group!==0)continue;
   const ids=face.sourceIds,a=ids.map(i=>source.uvs.slice(i*2,i*2+2));
   const [a0,b,c]=a,den=(b[1]-c[1])*(a0[0]-c[0])+(c[0]-b[0])*(a0[1]-c[1]);
   if(Math.abs(den)<1e-12)continue;
   const w0=((b[1]-c[1])*(u-c[0])+(c[0]-b[0])*(v-c[1]))/den;
   const w1=((c[1]-a0[1])*(u-c[0])+(a0[0]-c[0])*(v-c[1]))/den;
   const w2=1-w0-w1;
   if(Math.min(w0,w1,w2)<-1e-5)continue;
   const z=ids.reduce((sum,id)=>sum+source.positions[id*3+2],0)/3;
   if(!found||z>found.z){
    found={z,uv:[face.uv[0][0]*w0+face.uv[1][0]*w1+face.uv[2][0]*w2,
     face.uv[0][1]*w0+face.uv[1][1]*w1+face.uv[2][1]*w2]};
   }
  }
  return found?.uv||null;
 }
 return Object.freeze({unwrap,remapCenter});
})();
 // SE503_UV_ISLAND_MATH_END
