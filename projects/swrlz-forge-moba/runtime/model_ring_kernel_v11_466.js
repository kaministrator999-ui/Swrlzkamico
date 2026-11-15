/* SE466_RING_KERNEL_START */
// Pure, bounded native topology candidates; workshop owns preview, history, and commit.
const se466RingKernel=(()=>{
 const fail=reason=>({ok:false,reason,error:reason});
 const point=(d,i)=>d.positions.slice(i*3,i*3+3);
 const uv=(d,i)=>d.uvs.slice(i*2,i*2+2);
 const add=(a,b)=>a.map((v,i)=>v+b[i]);
 const mul=(a,k)=>a.map(v=>v*k);
 const sub=(a,b)=>a.map((v,i)=>v-b[i]);
 const key=(a,b)=>a<b?a+':'+b:b+':'+a;
 const finite=(v,min,max)=>typeof v==='number'&&Number.isFinite(v)&&v>=min&&v<=max;
 function checked(d){return se430MeshOps.audit(d);}
 function selected(d,ids){
  const n=d.positions.length/3;
  if(!Array.isArray(ids)||!ids.length||ids.length>9000||ids.some(i=>!Number.isInteger(i)||i<0||i>=n))return null;
  return [...new Set(ids)];
 }
 function graph(d){
  const adjacency=Array.from({length:d.positions.length/3},()=>new Set());
  for(let i=0;i<d.indices.length;i+=3){
   const a=d.indices[i],b=d.indices[i+1],c=d.indices[i+2];
   for(const [u,v] of [[a,b],[b,c],[c,a]]){adjacency[u].add(v);adjacency[v].add(u);}
  }
  return adjacency;
 }
 function ringSelect(d,seed,options={}){
  const a=checked(d);if(!a.ok)return a;
  if(!Number.isInteger(seed)||seed<0||seed>=a.vertices)return fail('Select an existing vertex as the ring center.');
  const steps=options.steps??2,mode=options.mode??'outline',start=options.arcStart??0,sweep=options.arcSweep??360,plane=options.plane??'xz';
  if(!Number.isInteger(steps)||steps<0||steps>40||!['outline','fill'].includes(mode)||
    !finite(start,-360,360)||!finite(sweep,1,360)||!['xy','xz','yz'].includes(plane))return fail('Invalid ring radius, arc or plane.');
  const adj=graph(d),dist=new Int32Array(a.vertices).fill(-1),queue=[seed];dist[seed]=0;
  for(let i=0;i<queue.length;i++){const u=queue[i];if(dist[u]>=steps)continue;for(const v of adj[u])if(dist[v]===-1){dist[v]=dist[u]+1;queue.push(v);}}
  const axes=plane==='xy'?[0,1]:plane==='yz'?[1,2]:[0,2],center=point(d,seed),result=[];
  for(let i=0;i<a.vertices;i++){
   if(mode==='outline'?dist[i]!==steps:dist[i]<0||dist[i]>steps)continue;
   if(sweep<360&&i!==seed){
    const p=point(d,i),angle=((Math.atan2(p[axes[1]]-center[axes[1]],p[axes[0]]-center[axes[0]])*180/Math.PI)%360+360)%360;
    const origin=(start%360+360)%360,delta=(angle-origin+360)%360;
    if(delta>sweep+1e-7)continue;
   }
   result.push(i);
  }
  return result.length?{ok:true,vertexIds:result,seed,steps,mode,arcStart:start,arcSweep:sweep}:
    fail('No connected vertices intersect this radius and arc. Reduce the radius or widen the selection.');
 }
 function rotate(v,degrees){
  let [x,y,z]=v;const angles=degrees.map(n=>n*Math.PI/180);
  if(angles[0]){const c=Math.cos(angles[0]),s=Math.sin(angles[0]);[y,z]=[y*c-z*s,y*s+z*c];}
  if(angles[1]){const c=Math.cos(angles[1]),s=Math.sin(angles[1]);[x,z]=[x*c+z*s,-x*s+z*c];}
  if(angles[2]){const c=Math.cos(angles[2]),s=Math.sin(angles[2]);[x,y]=[x*c-y*s,x*s+y*c];}
  return [x,y,z];
 }
 function parameters(opts={}){
  const offset=opts.offset??[0,0,0],tilt=opts.tilt??[0,0,0];
  const scale=opts.scale??1,left=opts.leftScale??1,right=opts.rightScale??1;
  if(!Array.isArray(offset)||offset.length!==3||!offset.every(n=>finite(n,-30,30))||
   !Array.isArray(tilt)||tilt.length!==3||!tilt.every(n=>finite(n,-180,180))||
   !finite(scale,.02,8)||!finite(left,.02,8)||!finite(right,.02,8))return null;
  return {offset,tilt,scale,left,right};
 }
 function capPoint(p,center,opts={}){
  const args=parameters(opts);if(!args)return null;
  const relative=sub(p,center),factor=args.scale*(relative[0]<0?args.left:args.right);
  return add(center,add(rotate(mul(relative,factor),args.tilt),args.offset));
 }
 function transform(d,ids,opts={}){
  const a=checked(d);if(!a.ok)return a;const verts=selected(d,ids),args=parameters(opts);if(!verts||!args)return fail('Select vertices and provide bounded move, scale and rotation values.');
  const center=verts.reduce((sum,id)=>add(sum,point(d,id)),[0,0,0]).map(v=>v/verts.length);
  const falloff=opts.falloff??0;
  if(!Number.isInteger(falloff)||falloff<0||falloff>8)return fail('Falloff must be 0–8 connected edge rows.');
  const adj=graph(d),dist=new Int32Array(a.vertices).fill(-1),queue=[...verts];
  for(const id of verts)dist[id]=0;
  if(falloff)for(let i=0;i<queue.length;i++){
   const at=queue[i];if(dist[at]>=falloff)continue;
   for(const next of adj[at])if(dist[next]===-1){dist[next]=dist[at]+1;queue.push(next);}
  }
  const out={positions:[...d.positions],uvs:[...d.uvs],indices:[...d.indices]};
  for(let i=0;i<a.vertices;i++){
   if(dist[i]===-1)continue;
   const original=point(d,i),target=capPoint(original,center,args);
   const t=dist[i]===0?1:Math.pow(1-dist[i]/(falloff+1),2)*(3-2*(1-dist[i]/(falloff+1)));
   for(let k=0;k<3;k++)out.positions[i*3+k]=original[k]+(target[k]-original[k])*t;
  }
  const result=checked(out);if(!result.ok)return result;
  return {ok:true,data:out,selectedVertices:verts,stats:{operation:'ring-transform',affectedVertices:queue.length,selectedVertices:verts.length}};
 }
 function refine(d,ids,options={}){
  const a=checked(d);if(!a.ok)return a;const verts=selected(d,ids);if(!verts)return fail('Select a vertex ring or arc before refining.');
  const chosen=new Set(verts),midpoints=new Map(),out={positions:[...d.positions],uvs:[...d.uvs],indices:[]};
  const edgeIds=new Set();
  for(let i=0;i<d.indices.length;i+=3){
   const [a,b,c]=d.indices.slice(i,i+3);
   for(const [u,v] of [[a,b],[b,c],[c,a]])if(chosen.has(u)&&chosen.has(v))edgeIds.add(key(u,v));
  }
  if(!edgeIds.size)return fail('No mesh edges connect the selected vertices.');
  if(edgeIds.size>1000)return fail('Refine at most 1000 selected edges per operation.');
  for(const k of edgeIds){
   const [a,b]=k.split(':').map(Number),idx=out.positions.length/3;
   out.positions.push(...mul(add(point(d,a),point(d,b)),.5));
   out.uvs.push(...mul(add(uv(d,a),uv(d,b)),.5));
   midpoints.set(k,idx);
  }
  for(let i=0;i<d.indices.length;i+=3){
   const tri=d.indices.slice(i,i+3),[a,b,c]=tri;
   const mab=midpoints.get(key(a,b)),mbc=midpoints.get(key(b,c)),mca=midpoints.get(key(c,a));
   const count=[mab,mbc,mca].filter(v=>v!==undefined).length;
   if(count===0)out.indices.push(a,b,c);
   else if(count===3)out.indices.push(a,mab,mca,mab,b,mbc,mca,mbc,c,mab,mbc,mca);
   else if(count===1){
    if(mab!==undefined)out.indices.push(a,mab,c,mab,b,c);
    else if(mbc!==undefined)out.indices.push(b,mbc,a,mbc,c,a);
    else out.indices.push(c,mca,b,mca,a,b);
   }else{
    let shared;
    if(mab!==undefined&&mbc!==undefined)shared=1;
    else if(mbc!==undefined&&mca!==undefined)shared=2;
    else shared=0;
    const v=tri[shared],next=tri[(shared+1)%3],prev=tri[(shared+2)%3],m1=midpoints.get(key(v,next)),m2=midpoints.get(key(prev,v));
    out.indices.push(v,m1,m2,m1,next,prev,m1,prev,m2);
   }
  }
  const b=checked(out);if(!b.ok)return b;
  return {ok:true,data:out,selectedVertices:[...verts,...midpoints.values()],stats:{operation:'ring-refine',addedVertices:midpoints.size,facesAfter:out.indices.length/3}};
 }
 function extrudeBoundary(d,ids,options={}){
  const a=checked(d);if(!a.ok)return a;const verts=selected(d,ids),args=parameters(options);
  const height=options.depth??.15,axis=options.axis??'y';
  if(!verts||!args||!finite(height,-30,30)||Math.abs(height)<.0001||!['x','y','z'].includes(axis))return fail('Select a boundary loop and a valid extrusion distance.');
  const set=new Set(verts),outgoing=new Map(),incoming=new Map();
  for(const edges of a.edges.values())if(edges.length===1){
   const e=edges[0];if(set.has(e.from)&&set.has(e.to)){
    if(outgoing.has(e.from)||incoming.has(e.to))return fail('Selected boundary branches; choose one simple loop.');
    outgoing.set(e.from,e.to);incoming.set(e.to,e.from);
   }
  }
  if(outgoing.size!==verts.length||verts.length<3||verts.some(id=>!outgoing.has(id)||!incoming.has(id)))
   return fail('Ring extrusion needs a complete open boundary loop. For an interior face ring, use Face Inset then Extrude.');
  const loop=[],seen=new Set();let next=verts[0];
  while(!seen.has(next)&&loop.length<=verts.length){seen.add(next);loop.push(next);next=outgoing.get(next);}
  if(next!==loop[0]||loop.length!==verts.length)return fail('Select exactly one connected boundary loop.');
  const center=loop.reduce((sum,id)=>add(sum,point(d,id)),[0,0,0]).map(v=>v/loop.length);
  const dir=axis==='x'?[height,0,0]:axis==='y'?[0,height,0]:[0,0,height];
  const out={positions:[...d.positions],uvs:[...d.uvs],indices:[...d.indices]},mapping=new Map();
  for(const id of loop){
   const p=capPoint(point(d,id),center,{...args,offset:add(args.offset,dir)});
   mapping.set(id,out.positions.length/3);out.positions.push(...p);out.uvs.push(...add(uv(d,id),[0,.03]));
  }
  for(const id of loop){
   const to=outgoing.get(id),a=mapping.get(id),b=mapping.get(to);
   out.indices.push(to,id,a,to,a,b);
  }
  const check=checked(out);if(!check.ok)return check;
  return {ok:true,data:out,selectedVertices:loop.map(id=>mapping.get(id)),stats:{operation:'ring-extrude',depth:height,selectedVertices:loop.length}};
 }
 return Object.freeze({ringSelect,transform,refine,extrudeBoundary,capPoint});
})();
/* SE466_RING_KERNEL_END */