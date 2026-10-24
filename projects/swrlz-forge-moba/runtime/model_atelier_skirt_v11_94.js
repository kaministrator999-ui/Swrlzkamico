// Re-tailor the nine existing armor/cloth panels into a complete overlapping
// festival skirt. Native part identities, UVs and indexed topology are retained.
function atelierKneeSkirtV1194(scene){
 const model=scene.project.modelAtelier,parts=model.parts,round=v=>+v.toFixed(6),clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
 const plans=[
  {id:'skirt-panel-0',angle:-.92,span:.65,hem:1.73,layer:.012},
  {id:'skirt-panel-1',angle:.92,span:.65,hem:1.71,layer:.014},
  {id:'skirt-panel-2',angle:.30,span:.63,hem:1.78,layer:.025},
  {id:'skirt-panel-3',angle:-.30,span:.63,hem:1.69,layer:.032},
  {id:'skirt-panel-4',angle:-2.50,span:.85,hem:1.76,layer:.012,direction:-1},
  {id:'skirt-panel-5',angle:2.50,span:.85,hem:1.72,layer:.016,direction:-1},
  {id:'skirt-panel-6',angle:Math.PI,span:.72,hem:1.80,layer:.028,direction:-1},
  {id:'skirt-side-left',angle:-Math.PI/2,span:.68,hem:1.75,layer:.002,axis:2},
  {id:'skirt-side-right',angle:Math.PI/2,span:.68,hem:1.74,layer:.004,axis:2,direction:-1}
 ];
 const byId=new Map(parts.map(part=>[part.id,part])),surfaces=new Map(),samples=[];
 const mix=(a,b,t)=>a+(b-a)*t,sub=(a,b)=>a.map((v,k)=>v-b[k]),dot=(a,b)=>a.reduce((s,v,k)=>s+v*b[k],0);
 const normal=(a,b)=>{const n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],l=Math.hypot(...n)||1;return n.map(v=>v/l);};
 const envelope=[
  [1.55,.675,.365],[2,.635,.345],[2.25,.595,.325],
  [2.5,.555,.305],[2.65,.510,.285],[2.8,.390,.245],[2.99,.325,.205]
 ];
 const radius=y=>{let i=0;while(i<envelope.length-2&&envelope[i+1][0]<y)i++;const a=envelope[i],b=envelope[i+1],t=clamp((y-a[0])/(b[0]-a[0]));return [mix(a[1],b[1],t),mix(a[2],b[2],t)];};
 for(const plan of plans){
  const part=byId.get(plan.id);if(!part)throw Error('Missing existing skirt panel '+plan.id);
  const data=part.topologyMesh,groups=new Map();
  for(let i=0;i<data.positions.length/3;i++){
   const t=round(data.uvs[i*2+1]);if(!groups.has(t))groups.set(t,[]);
   groups.get(t).push({u:data.uvs[i*2],p:data.positions.slice(i*3,i*3+3)});
   if(i%16===0)samples.push({id:plan.id,p:data.positions.slice(i*3,i*3+3)});
  }
  const rows=[...groups].sort((a,b)=>a[0]-b[0]).map(([t,row])=>({t,row:row.sort((a,b)=>a.u-b.u)}));
  const atRow=(row,u)=>{let j=clamp(Math.floor(u*(row.length-1)),0,row.length-2),a=row[j],b=row[j+1],f=(u-a.u)/(b.u-a.u);return a.p.map((v,k)=>mix(v,b.p[k],f));};
  const oldAt=(u,t)=>{let j=clamp(Math.floor(t*(rows.length-1)),0,rows.length-2),a=rows[j],b=rows[j+1],f=(t-a.t)/(b.t-a.t),lo=atRow(a.row,u),hi=atRow(b.row,u);return lo.map((v,k)=>mix(v,hi[k],f));};
  const top=rows[0].row.reduce((s,v)=>s+v.p[1],0)/rows[0].row.length,bottom=rows.at(-1).row.reduce((s,v)=>s+v.p[1],0)/rows.at(-1).row.length;
  const targetAt=(u,t)=>{
   const q=u*2-1,theta=plan.angle+(plan.direction||1)*q*plan.span,
    y=mix(top,plan.hem,t)+.115*Math.abs(q)**1.35*t**5,
    r=radius(y),pleat=.0025*Math.cos(u*Math.PI*8)*Math.sin(t*Math.PI);
   return [(r[0]+plan.layer+pleat)*Math.sin(theta),y,(r[1]+plan.layer+pleat)*Math.cos(theta)];
  };
  const inverse=p=>{
   const axis=plan.axis||0;let t=clamp((top-p[1])/(top-bottom)),u=.5;
   for(let iteration=0;iteration<7;iteration++){
    const center=oldAt(u,t),h=.0002,du=sub(oldAt(u+h,t),center).map(v=>v/h),dt=sub(oldAt(u,t+h),center).map(v=>v/h),d=sub(p,center),det=du[axis]*dt[1]-du[1]*dt[axis];
    if(Math.abs(det)<1e-9)break;
    u=clamp(u+(d[axis]*dt[1]-d[1]*dt[axis])/det,-.055,1.055);
    t=clamp(t+(du[axis]*d[1]-du[1]*d[axis])/det,-.025,1.025);
   }
   return [u,t];
  };
  const warp=(p,u,t)=>{
   if(u===undefined)[u,t]=inverse(p);
   const old=oldAt(u,t),next=targetAt(u,t),h=.0002,
    oldN=normal(sub(oldAt(u+h,t),old),sub(oldAt(u,t+h),old)),
    nextN=normal(sub(targetAt(u+h,t),next),sub(targetAt(u,t+h),next)),offset=dot(sub(p,old),oldN);
   return next.map((v,k)=>v+nextN[k]*offset);
  };
  surfaces.set(plan.id,{data,oldAt,targetAt,inverse,warp,plan});
 }
 const closestOwner=p=>{let best=Infinity,id=null;for(const sample of samples){const d=dot(sub(p,sample.p),sub(p,sample.p));if(d<best){best=d;id=sample.id;}}return id;};
 const affected=[],hemBounds={};
 // Pendants translate rigidly with their cord's attachment point so their
 // round geometry and the shared cord/bauble join cannot stretch or tear.
 const pendants=new Map();
 for(const part of parts.filter(p=>p.id.startsWith('light-cord-'))){
  const ps=part.topologyMesh.positions,high=Math.max(...ps.filter((v,i)=>i%3===1)),anchor=[0,0,0];let count=0;
  for(let i=0;i<ps.length;i+=3)if(ps[i+1]>high-.002){for(let k=0;k<3;k++)anchor[k]+=ps[i+k];count++;}
  for(let k=0;k<3;k++)anchor[k]/=count;
  const surface=surfaces.get('skirt-panel-'+(part.id.includes('--1-')?0:1)),target=surface.warp(anchor),delta=sub(target,anchor),key=part.id.slice('light-cord'.length),orb=byId.get('light'+key);
  const minimum=Math.min(...ps.filter((v,i)=>i%3===1),...(orb?.topologyMesh.positions||[]).filter((v,i)=>i%3===1));delta[1]+=Math.max(0,1.525-minimum-delta[1]);pendants.set(key,delta);
 }
 const components=data=>{
  const count=data.positions.length/3,parent=Array.from({length:count},(_,i)=>i),find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;};
  for(let i=0;i<data.indices.length;i+=3){const a=find(data.indices[i]),b=find(data.indices[i+1]),c=find(data.indices[i+2]);parent[b]=a;parent[c]=a;}
  const groups=new Map();for(let i=0;i<count;i++){const root=find(i);if(!groups.has(root))groups.set(root,[]);groups.get(root).push(i);}return [...groups.values()];
 };
 for(const part of parts){
  const match=part.id.match(/^skirt-(?:panel|piping|inset)-(\d+)/),owner=match?'skirt-panel-'+match[1]:surfaces.has(part.id)?part.id:null,
   special=part.id==='girl-dress-inset-pleat-seams'?'skirt-panel-3':part.id==='girl-dress-gold-tail-tassel'?'skirt-panel-1':/^girl-dress-(pastel-bauble|bauble-loop)-/.test(part.id)?'skirt-panel-2':null,
   aggregate=['girl-tailoring-stitches','girl-dress-brocade-diamonds','girl-dress-running-stitches'].includes(part.id),
   pendantKey=part.id.startsWith('light-cord-')?part.id.slice('light-cord'.length):part.id.startsWith('light-')?part.id.slice('light'.length):null;
  if(!owner&&!special&&!aggregate&&!pendants.has(pendantKey))continue;
  const data=part.topologyMesh,positions=data.positions;
  if(pendants.has(pendantKey)){
   const delta=pendants.get(pendantKey);for(let i=0;i<positions.length;i++)positions[i]=round(positions[i]+delta[i%3]);
  }else if(part.id===owner){
   const surface=surfaces.get(owner);for(let i=0;i<positions.length;i+=3)positions.splice(i,3,...surface.targetAt(data.uvs[i/3*2],data.uvs[i/3*2+1]).map(round));
  }else if(aggregate){
   for(const vertices of components(data)){
    const center=[0,0,0];for(const index of vertices)for(let k=0;k<3;k++)center[k]+=positions[index*3+k]/vertices.length;
    if(center[1]>2.925)continue;
    const surface=surfaces.get(closestOwner(center));
    for(const index of vertices){const p=positions.slice(index*3,index*3+3);positions.splice(index*3,3,...surface.warp(p).map(round));}
   }
  }else if(/^girl-dress-pastel-bauble-/.test(part.id)||part.id==='girl-dress-gold-tail-tassel'){
   const center=[0,0,0];for(let i=0;i<positions.length;i++)center[i%3]+=positions[i]/(positions.length/3);
   const delta=sub(surfaces.get(special).warp(center),center);for(let i=0;i<positions.length;i++)positions[i]=round(positions[i]+delta[i%3]);
  }else{
   const surface=surfaces.get(owner||special);for(let i=0;i<positions.length;i+=3)positions.splice(i,3,...surface.warp(positions.slice(i,i+3)).map(round));
  }
  let minY=Infinity,maxY=-Infinity;for(let i=1;i<positions.length;i+=3){minY=Math.min(minY,positions[i]);maxY=Math.max(maxY,positions[i]);}
  // Trims retain their relief, while even dangling tassels stay above the knee.
  if(minY<1.525){const rise=1.525-minY;for(let i=1;i<positions.length;i+=3)positions[i]=round(positions[i]+rise);maxY+=rise;minY=1.525;}
  hemBounds[part.id]={minY:round(minY),maxY:round(maxY)};
  part.tailoring={...(part.tailoring||{}),silhouette:'overlapping full festival skirt',revision:'knee-armor-v11.94'};affected.push(part.id);
 }
 model.festivalDress={...model.festivalDress,revision:'knee-armor-v11.94',style:'complete overlapping festival armor skirt',silhouettePanels:plans.map(p=>p.id),finishParts:affected};
 model.kneeSkirtRefinement={revision:'v11.94',kneeY:1.52,coverage:'overlapping full skirt',panelIds:plans.map(p=>p.id),affectedParts:affected,hemBounds};
 return scene;
}
