/* SE483_RING_DETAIL_KERNEL_START */
// Pure source-UV-preserving ring refinement and affine transforms.
// Candidate calculations never mutate source. Native se430 workshop handles
// preview ownership, source validation, Apply/Cancel and Undo.
const se483RingDetailKernel=(()=>{
 'use strict';
 const BAD=reason=>({ok:false,reason,error:reason});
 const clone=d=>({positions:[...d.positions],uvs:[...d.uvs],indices:[...d.indices]});
 const P=(d,i)=>d.positions.slice(i*3,i*3+3),U=(d,i)=>d.uvs.slice(i*2,i*2+2);
 const key=(a,b)=>a<b?a+':'+b:b+':'+a;
 const close=(a,b,eps=1e-6)=>Math.abs(a-b)<eps;
 const axes=plane=>plane==='xy'?[0,1,2]:plane==='yz'?[1,2,0]:[0,2,1];
 const finite3=x=>Array.isArray(x)&&x.length===3&&x.every(v=>Number.isFinite(v)&&Math.abs(v)<=30);
 const physical=x=>x.map(v=>Math.round(v*100000)).join(':');
 const DIST=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
 const limits=()=>se430MeshOps.limits||{vertices:9000,faces:16000};
 function init(d,ids){
  const audit=se430MeshOps.audit(d);
  if(!audit.ok)return audit;
  if(!Array.isArray(ids)||!ids.length||ids.length>9000||
     ids.some(x=>!Number.isInteger(x)||x<0||x>=d.positions.length/3))
   return BAD('Select real editable vertices within one mesh first.');
  return {ok:true,ids:[...new Set(ids)],audit};
 }
 function centerOf(d,ids,plane,requested){
  if(requested!==undefined){if(!finite3(requested))return null;return [...requested];}
  const ps=ids.map(id=>P(d,id));
  const bounds=[0,1,2].map(k=>[Math.min(...ps.map(p=>p[k])),Math.max(...ps.map(p=>p[k]))]);
  return bounds.map(([a,b])=>(a+b)*.5);
 }
 function planeDistance(p,origin,ax){
  return Math.hypot(p[ax[0]]-origin[ax[0]],p[ax[1]]-origin[ax[1]]);
 }
 function splitEdges(d,cuts){
  const out=clone(d),lookup=new Map(),changed=[];
  // Adjacent faces share identical new indices on each indexed edge. UV
  // seam charts stay separate but interpolate their own UV coordinates.
  for(const [edge,roots] of cuts){
   const [a,b]=edge.split(':').map(Number),entries=[],unique=new Map();
   for(const raw of roots){
    const cut=typeof raw==='number'?{t:raw,tag:null}:raw;
    const t=Math.round(cut.t*1e7)/1e7;
    if(!(t>1e-5&&t<1-1e-5))continue;
    if(!unique.has(t))unique.set(t,{t,tags:new Set()});
    if(cut.tag!==null&&cut.tag!==undefined)unique.get(t).tags.add(cut.tag);
   }
   for(const {t,tags} of [...unique.values()].sort((a,b)=>a.t-b.t)){
    if(out.positions.length/3>=limits().vertices)
     return BAD('Vertex safety limit reached. Reduce subdivisions or select a smaller region.');
    const id=out.positions.length/3,pa=P(d,a),pb=P(d,b),ua=U(d,a),ub=U(d,b);
    out.positions.push(...pa.map((x,k)=>x+(pb[k]-x)*t));
    out.uvs.push(...ua.map((x,k)=>x+(ub[k]-x)*t));
    entries.push({id,t,tags:[...tags],edge});changed.push(id);
   }
   if(entries.length)lookup.set(edge,entries);
  }
  if(!changed.length)return BAD('No eligible connected edges intersect the requested ring detail.');
  out.indices=[];
  const edgeSeq=(a,b)=>{
   const seq=lookup.get(key(a,b))||[];
   return a<b?seq:seq.slice().reverse();
  };
  for(let f=0;f<d.indices.length;f+=3){
   const [a,b,c]=d.indices.slice(f,f+3);
   const ab=edgeSeq(a,b),bc=edgeSeq(b,c),ca=edgeSeq(c,a);
   if(!ab.length&&!bc.length&&!ca.length){out.indices.push(a,b,c);continue;}
   const contour=[{id:a,tags:[],edge:null},...ab,
    {id:b,tags:[],edge:null},...bc,
    {id:c,tags:[],edge:null},...ca];
   // Create actual edges between same-radius boundary points within each
   // triangle. These chords form connected concentric loops across adjacent
   // triangles, rather than merely painting dots over an unchanged surface.
   const byTag=new Map();
   for(const vertex of contour)for(const tag of vertex.tags||[]){
    if(!byTag.has(tag))byTag.set(tag,[]);
    byTag.get(tag).push(vertex);
   }
   let polygons=[contour.map(v=>v.id)];
   for(const vertices of byTag.values()){
    if(vertices.length%2)continue; // tangency: don't invent a connection
    for(let j=0;j<vertices.length;j+=2){
     const from=vertices[j],to=vertices[j+1];
     if(from.edge===to.edge)continue;
     let split=false;
     for(let q=0;q<polygons.length;q++){
      const poly=polygons[q],i=poly.indexOf(from.id),k=poly.indexOf(to.id);
      if(i<0||k<0||i===k)continue;
      const lo=Math.min(i,k),hi=Math.max(i,k);
      const one=poly.slice(lo,hi+1),two=[...poly.slice(hi),...poly.slice(0,lo+1)];
      if(one.length<3||two.length<3)continue;
      polygons.splice(q,1,one,two);split=true;break;
     }
     if(!split)return BAD('Internal ring chords crossed or touched another cut. Reduce ring count.');
    }
   }
   const pa=P(d,a),pb=P(d,b),pc=P(d,c);
   const n=[
    (pb[1]-pa[1])*(pc[2]-pa[2])-(pb[2]-pa[2])*(pc[1]-pa[1]),
    (pb[2]-pa[2])*(pc[0]-pa[0])-(pb[0]-pa[0])*(pc[2]-pa[2]),
    (pb[0]-pa[0])*(pc[1]-pa[1])-(pb[1]-pa[1])*(pc[0]-pa[0])
   ];
   function area(x,y,z){
    const p=P(out,x),q=P(out,y),r=P(out,z);
    const u=q.map((v,k)=>v-p[k]),v=r.map((w,k)=>w-p[k]);
    const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
    return cross.reduce((sum,val,k)=>sum+val*n[k],0);
   }
   for(const polygon of polygons){
    const poly=[...polygon];
    while(poly.length>3){
     let ear=-1;
     for(let k=0;k<poly.length;k++){
      const u=poly[(k-1+poly.length)%poly.length],v=poly[k],w=poly[(k+1)%poly.length];
      if(area(u,v,w)>1e-12){ear=k;break;}
     }
     if(ear<0)return BAD('Ring geometry would create a degenerate triangle. Reduce density.');
     out.indices.push(poly[(ear-1+poly.length)%poly.length],poly[ear],poly[(ear+1)%poly.length]);
     poly.splice(ear,1);
    }
    if(area(...poly)<=1e-12)return BAD('A ring cut collapsed one triangle. Adjust spacing.');
    out.indices.push(...poly);
   }
   if(out.indices.length/3>limits().faces)
    return BAD('Triangle safety limit reached. Reduce requested ring density.');
  }
  const result=se430MeshOps.audit(out);
  if(!result.ok)return BAD('The proposed topology was rejected: '+result.reason);
  return {ok:true,data:out,added:out.positions.length/3-d.positions.length/3,
   selectedVertices:changed,stats:{operation:'ring-detail',addedVertices:out.positions.length/3-d.positions.length/3,
    facesBefore:d.indices.length/3,facesAfter:out.indices.length/3}};
 }
 function radialCuts(d,ids,options={}){
  const plane=options.plane||'xz',ax=axes(plane);
  if(!['xy','xz','yz'].includes(plane))return BAD('Use XY, XZ, or YZ for circular topology.');
  const origin=centerOf(d,ids,plane,options.center);
  if(!origin)return BAD('Invalid circle center.');
  const requested=Number(options.innerRings);
  if(!Number.isInteger(requested)||requested<1||requested>8)
   return BAD('Choose 1–8 new internal rings.');
  const outer=options.radius!==undefined?Number(options.radius):
   Math.max(...ids.map(id=>planeDistance(P(d,id),origin,ax)));
  if(!Number.isFinite(outer)||outer<.01||outer>100)
   return BAD('Choose a filled circle with a valid outer radius.');
  const spacing=options.spacing??'even';
  if(!['even','inner','outer'].includes(spacing))
   return BAD('Choose Even, Inner, or Outer ring spacing.');
  const radii=Array.from({length:requested},(_,i)=>{
   const t=(i+1)/(requested+1);
   return outer*(spacing==='inner'?t*t:spacing==='outer'?1-(1-t)*(1-t):t);
  });
  const chosen=new Set(ids),cuts=new Map();
  const triangles=d.indices;
  const addedCandidates=new Set();
  for(let k=0;k<triangles.length;k+=3){
   const face=triangles.slice(k,k+3);
   // Work only on faces bordering at least one selected vertex, preserving
   // unrelated mesh regions and the hidden back side where possible.
   if(!face.some(id=>chosen.has(id)))continue;
   for(const [u,v] of [[face[0],face[1]],[face[1],face[2]],[face[2],face[0]]]){
    const e=key(u,v);if(addedCandidates.has(e))continue;addedCandidates.add(e);
    const p=P(d,Math.min(u,v)),q=P(d,Math.max(u,v)),dx=q[ax[0]]-p[ax[0]],dy=q[ax[1]]-p[ax[1]];
    const ox=p[ax[0]]-origin[ax[0]],oy=p[ax[1]]-origin[ax[1]];
    const A=dx*dx+dy*dy;if(A<1e-12)continue;
    const B=2*(ox*dx+oy*dy);
    for(const [tag,rad] of radii.entries()){
     const C=ox*ox+oy*oy-rad*rad;
     const disc=B*B-4*A*C;
     if(disc<=1e-12)continue;
     const sq=Math.sqrt(disc);
     for(const t of [(-B-sq)/(2*A),(-B+sq)/(2*A)]){
      if(t>1e-5&&t<1-1e-5){
       if(!cuts.has(e))cuts.set(e,[]);
       cuts.get(e).push({t,tag});
      }
     }
    }
   }
  }
  if(!cuts.size)return BAD('No edges cross the requested internal radii. Try a different number of rings.');
  const result=splitEdges(d,cuts);
  if(!result.ok)return result;
  result.ringRadii=radii;
  result.ringCenter=origin;
  result.ringPlane=plane;
  result.outerRadius=outer;
  const tolerance=Math.max(.00008,outer*.001);
  const eligible=[...new Set([...ids,...result.selectedVertices])];
  result.ringMembers=radii.map(rad=>eligible.filter(id=>
   Math.abs(planeDistance(P(result.data,id),origin,ax)-rad)<=tolerance));
  result.stats={...result.stats,operation:'internal-rings',internalRings:requested,
   radii:[...radii],spacing};
  return result;
 }
 function density(d,ids,options={}){
  const plane=options.plane||'xz',ax=axes(plane);
  if(!['xy','xz','yz'].includes(plane))return BAD('Choose an editable plane.');
  const selected=new Set(ids),origin=centerOf(d,ids,plane,options.center);
  if(!origin)return BAD('Invalid circle center.');
  const ps=ids.map(id=>P(d,id));
  const rad=Number.isFinite(options.radius)?options.radius:
    Math.max(...ps.map(p=>planeDistance(p,origin,ax)));
  const band=Math.max(.008,rad*.1),heightTolerance=Math.max(.012,rad*.08);
  const ringIds=ids.filter(id=>Math.abs(planeDistance(P(d,id),origin,ax)-rad)<band);
  const unique=new Map();
  for(const id of ringIds)unique.set(physical(P(d,id)),id);
  const count=unique.size,target=Number(options.target);
  if(!Number.isInteger(target)||target<3||target>256)
   return BAD('Target ring density must be 3–256 vertices.');
  if(target===count)return BAD('The selected ring already has '+count+' vertices.');
  const edgeKeys=new Map();
  const physEdge=(a,b)=>[physical(P(d,a)),physical(P(d,b))].sort().join('|');
  for(let i=0;i<d.indices.length;i+=3){
   const [a,b,c]=d.indices.slice(i,i+3);
   for(const [u,v] of [[a,b],[b,c],[c,a]]){
    if(!selected.has(u)||!selected.has(v)||
       Math.abs(planeDistance(P(d,u),origin,ax)-rad)>band||
       Math.abs(planeDistance(P(d,v),origin,ax)-rad)>band||
       Math.abs(P(d,u)[ax[2]]-P(d,v)[ax[2]])>heightTolerance)continue;
    const phys=physEdge(u,v),p=P(d,u),q=P(d,v);
    const angle=(Math.atan2((p[ax[1]]+q[ax[1]])*.5-origin[ax[1]],
     (p[ax[0]]+q[ax[0]])*.5-origin[ax[0]])+2*Math.PI)%(2*Math.PI);
    if(!edgeKeys.has(phys))edgeKeys.set(phys,{angle,edges:new Set()});
    edgeKeys.get(phys).edges.add(key(u,v));
   }
  }
  if(target>count){
   const sorted=[...edgeKeys.values()].sort((a,b)=>a.angle-b.angle),want=target-count;
   if(want>sorted.length)return BAD('This ring supports '+sorted.length+
    ' additional edge vertices in one step. Apply and repeat to increase further.');
   if(!sorted.length)return BAD('No connected perimeter edges are available to refine.');
   const chosen=new Set();
   for(let j=0;j<want;j++)chosen.add(Math.floor(j*sorted.length/want));
   const cuts=new Map();
   sorted.forEach((item,i)=>{if(chosen.has(i))for(const e of item.edges)cuts.set(e,[.5]);});
   const result=splitEdges(d,cuts);
   if(result.ok){
    result.selectedVertices=[...new Set([...ids,...result.selectedVertices])];
    result.stats={...result.stats,operation:'ring-density',
     ringBefore:count,ringTarget:target,addedPositions:want};
   }
   return result;
  }
  // Conservative inverse of a single midpoint-edge insertion. Do not
  // simplify arbitrary authored vertices, UV seams, or displaced geometry.
  return reduceSafeMidpoints(d,ids,target,count,origin,ax,rad,band);
 }
 function reduceSafeMidpoints(d,ids,target,count,origin,ax,rad,band){
  if(target<count-8)return BAD('Reduce ring density by at most 8 safe inserted vertices per operation.');
  let out=clone(d),collapsed=0;
  const layer=ids.reduce((sum,id)=>sum+P(d,id)[ax[2]],0)/ids.length;
  const layerTolerance=Math.max(.012,rad*.08);
  // Each exact midpoint from the earlier ring-density split appears in four
  // triangles. Its neighbors contain the original edge endpoints and two
  // opposing face vertices. Rebuild only when winding and UVs validate.
  function collapse(src,m){
   const faceIds=[],neighbors=new Set();
   for(let k=0;k<src.indices.length;k+=3){
    const tri=src.indices.slice(k,k+3);
    if(!tri.includes(m))continue;
    faceIds.push(k/3);tri.filter(id=>id!==m).forEach(id=>neighbors.add(id));
   }
   if(faceIds.length!==4||neighbors.size!==4)return null;
   const others=[...neighbors],mp=P(src,m),mu=U(src,m);
   for(let a=0;a<others.length;a++)for(let b=a+1;b<others.length;b++){
    const i=others[a],j=others[b],pi=P(src,i),pj=P(src,j),ui=U(src,i),uj=U(src,j);
    if(DIST(mp,pi.map((v,k)=>(v+pj[k])*.5))>1e-5||
       DIST(mu,ui.map((v,k)=>(v+uj[k])*.5))>1e-5)continue;
    const opposite=others.filter(x=>x!==i&&x!==j);
    const replacement=[];
    let compatible=true;
    for(const c of opposite){
     const pair=faceIds.filter(f=>{
      const tri=src.indices.slice(f*3,f*3+3);
      return tri.includes(c);
     });
     if(pair.length!==2){compatible=false;break;}
     const tri=src.indices.slice(pair[0]*3,pair[0]*3+3);
     const candidate=[i,j,c],reverse=[j,i,c];
     const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],
      a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
     const sub=(a,b)=>a.map((x,k)=>x-b[k]);
     const normal=t=>cross(sub(P(src,t[1]),P(src,t[0])),sub(P(src,t[2]),P(src,t[0])));
     const orig=normal(tri),fwd=normal(candidate),rev=normal(reverse);
     const dot=t=>t.reduce((s,x,k)=>s+x*orig[k],0);
     const chosen=dot(fwd)>dot(rev)?candidate:reverse;
     if(dot(normal(chosen))<1e-10){compatible=false;break;}
     replacement.push(chosen);
    }
    if(!compatible)continue;
    const keep=new Set(faceIds),candidate=clone(src);
    candidate.indices=[];
    for(let f=0;f<src.indices.length/3;f++)if(!keep.has(f))
     candidate.indices.push(...src.indices.slice(f*3,f*3+3));
    for(const t of replacement)candidate.indices.push(...t);
    const activeIds=[...new Set(candidate.indices)],remap=new Map();
    const compact={positions:[],uvs:[],indices:[]};
    for(const old of activeIds){
     remap.set(old,compact.positions.length/3);
     compact.positions.push(...P(src,old));compact.uvs.push(...U(src,old));
    }
    compact.indices=candidate.indices.map(id=>remap.get(id));
    if(se430MeshOps.audit(compact).ok)return compact;
   }
   return null;
  }
  // Only new midpoints still lying on the target ring qualify. A failed
  // collapse leaves the complete original geometry unchanged.
  for(let k=0;k<Math.min(count-target,8);k++){
   const ring=Array.from({length:out.positions.length/3},(_,i)=>i)
    .filter(id=>Math.abs(planeDistance(P(out,id),origin,ax)-rad)<band&&
     Math.abs(P(out,id)[ax[2]]-layer)<layerTolerance);
   let changed=false;
   for(const id of ring){
    const candidate=collapse(out,id);
    if(candidate){out=candidate;collapsed++;changed=true;break;}
   }
   if(!changed)break;
  }
  if(!collapsed)return BAD('No safe, unmodified midpoint detail can be reduced here. Use Undo or select a regular inserted ring.');
  const remaining=Array.from({length:out.positions.length/3},(_,i)=>i)
   .filter(id=>Math.abs(planeDistance(P(out,id),origin,ax)-rad)<band&&
    Math.abs(P(out,id)[ax[2]]-layer)<layerTolerance);
  return {ok:true,data:out,selectedVertices:remaining,
   stats:{operation:'ring-density-reduce',ringBefore:count,
    ringTarget:target,reducedVertices:collapsed}};
 }
 function rotate(v,angles){
  let [x,y,z]=v;
  for(let k=0;k<3;k++){
   const n=angles[k]*Math.PI/180;if(Math.abs(n)<1e-9)continue;
   const c=Math.cos(n),s=Math.sin(n);
   if(k===0)[y,z]=[y*c-z*s,y*s+z*c];
   if(k===1)[x,z]=[x*c+z*s,-x*s+z*c];
   if(k===2)[x,y]=[x*c-y*s,x*s+y*c];
  }
  return [x,y,z];
 }
 function transform(d,ids,options={}){
  const state=init(d,ids);if(!state.ok)return state;
  const offset=options.offset??[0,0,0],tilt=options.tilt??[0,0,0],
   scale=options.scale??1,falloff=options.falloff??0,twist=options.twist??0;
  if(!finite3(offset)||!finite3(tilt.map(v=>v/6))||
   !tilt.every(x=>Number.isFinite(x)&&Math.abs(x)<=180)||
   !Number.isFinite(scale)||scale<.02||scale>8||
   !Number.isInteger(falloff)||falloff<0||falloff>8||
   !Number.isFinite(twist)||Math.abs(twist)>180)return BAD('Use bounded position, rotation, scale, twist, and falloff.');
  const pivot=options.pivot??state.ids.reduce((sum,id)=>{
   const p=P(d,id);return sum.map((x,k)=>x+p[k]/state.ids.length);
  },[0,0,0]);
  if(!finite3(pivot))return BAD('The selected pivot is outside the permitted local editing range.');
  const plane=options.plane||'xz',ax=axes(plane);
  if(!['xy','xz','yz'].includes(plane))return BAD('Choose a valid mesh plane.');
  const distance=id=>planeDistance(P(d,id),pivot,ax);
  const maxRad=Math.max(.000001,...state.ids.map(distance));
  const adj=Array.from({length:state.audit.vertices},()=>[]);
  for(let i=0;i<d.indices.length;i+=3){
   const [a,b,c]=d.indices.slice(i,i+3);
   for(const [u,v] of [[a,b],[b,c],[c,a]]){adj[u].push(v);adj[v].push(u);}
  }
  const dist=new Int16Array(state.audit.vertices).fill(-1),queue=[...state.ids];
  for(const id of state.ids)dist[id]=0;
  if(falloff)for(let i=0;i<queue.length;i++){
   if(dist[queue[i]]>=falloff)continue;
   for(const v of adj[queue[i]])if(dist[v]<0){dist[v]=dist[queue[i]]+1;queue.push(v);}
  }
  const out=clone(d);
  for(const id of queue){
   const p=P(d,id),relative=p.map((x,k)=>x-pivot[k]);
   // Gradual twist: center rotates the most; outer ring retains the base
   // rotation. No new vertices are needed for pure transforms.
   const radiusRatio=Math.min(1,distance(id)/maxRad),additional=twist*(1-radiusRatio);
   const spin=[...tilt];spin[ax[2]]+=additional;
   const spun=rotate(relative.map(x=>x*scale),spin);
   const target=spun.map((x,k)=>pivot[k]+x+offset[k]);
   const blend=dist[id]===0?1:Math.pow(1-dist[id]/(falloff+1),2)*
    (3-2*(1-dist[id]/(falloff+1)));
   for(let j=0;j<3;j++)out.positions[id*3+j]=p[j]+(target[j]-p[j])*blend;
  }
  const verified=se430MeshOps.audit(out);
  if(!verified.ok)return BAD('The transform would damage mesh topology: '+verified.reason);
  return {ok:true,data:out,selectedVertices:[...state.ids],
   stats:{operation:'ring-transform',affectedVertices:queue.length,
    selectedVertices:state.ids.length,pivot,twist,falloff}};
 }
 function detail(d,ids,options={}){
  const state=init(d,ids);if(!state.ok)return state;
  if(options.action==='internal')return radialCuts(d,state.ids,options);
  if(options.action==='density')return density(d,state.ids,options);
  return BAD('Choose ring-density change or internal-ring subdivision.');
 }
 return Object.freeze({detail,transform,splitEdges});
})();
/* SE483_RING_DETAIL_KERNEL_END */