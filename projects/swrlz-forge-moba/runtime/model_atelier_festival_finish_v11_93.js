// Keep the actual hair-attached piñatas as the dominant silhouette. The new
// compact locks and angular wrap stay native meshes, not painted substitutes.
function atelierFestivalFinishV1193(scene,originalGripParts=[]){
 const model=scene.project.modelAtelier,parts=model.parts,round=v=>+v.toFixed(6),clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
 const byId=id=>parts.find(part=>part.id===id);
 const interpolate=(rows,t,column=1)=>{let i=0;while(i<rows.length-2&&rows[i+1][0]<t)i++;const a=rows[i],b=rows[i+1],f=clamp((t-a[0])/(b[0]-a[0]));return a[column]+(b[column]-a[column])*f;};
 const hairBefore={};
 for(const part of parts){
  if(!part.id.startsWith('girl-reference-ponytail-'))continue;
  const side=part.id.includes('ponytail--1-')?-1:1,root=[side*.335,4.298,-.055],data=part.topologyMesh;
  let oldReach=0,newReach=0;
  for(let i=0;i<data.positions.length;i+=3){const p=data.positions.slice(i,i+3);oldReach=Math.max(oldReach,Math.hypot(p[0]-root[0],p[1]-root[1]));const next=[root[0]+(p[0]-root[0])*.58,root[1]+(p[1]-root[1])*.58,root[2]+(p[2]-root[2])*.68];data.positions.splice(i,3,...next.map(round));newReach=Math.max(newReach,Math.hypot(next[0]-root[0],next[1]-root[1]));}
  part.name=part.name.replace('upward pointed silk tuft','compact tied silk lock');part.referenceFinish={revision:'v11.93',radialScale:.58};hairBefore[part.id]={oldReach:round(oldReach),newReach:round(newReach)};
 }
 // Braid sections held by the companions were removed during the previous
 // hair pass. Restore the same native geometry without touching socket owners.
 const restored=[];
 for(const id of ['hair-grip--1','hair-grip-1']){
  const source=originalGripParts.find(part=>part.id===id);
  if(!source)throw Error('Missing original piñata braid connector '+id);
  const old=parts.findIndex(part=>part.id===id);if(old>=0)parts.splice(old,1);
  parts.push(structuredClone(source));restored.push(id);
 }
 // Describe each preserved cloth surface by its own UV rows. This lets all
 // matching trim follow the same shape change while its UVs/indices stay exact.
 const plans={
  0:{center:[[0,0],[.28,-.20],[.62,-.46],[1,-.70]],width:[[0,.16],[.27,.30],[.64,.21],[1,.006]],hem:1.7952,skew:.035},
  1:{center:[[0,.1802],[.30,.36],[.62,.56],[1,.86]],width:[[0,.12],[.24,.205],[.46,.215],[.69,.125],[1,.005]],hem:1.51,skew:-.055},
  2:{center:[[0,.0848],[.34,.15],[.68,.27],[1,.385]],width:[[0,.17],[.25,.19],[.55,.155],[.78,.075],[1,.005]],hem:2.115,skew:-.09},
  3:{center:[[0,-.12836],[.30,-.185],[.65,-.23],[1,-.23]],width:[[0,.15137],[.25,.18],[.60,.105],[1,.005]],hem:1.72,skew:.035}
 };
 const surfaces=new Map(),samples=[];
 for(const [key,plan] of Object.entries(plans)){
  const index=+key,part=byId('skirt-panel-'+index),data=part.topologyMesh,groups=new Map();
  for(let i=0;i<data.positions.length/3;i++){const t=round(data.uvs[i*2+1]);let row=groups.get(t);if(!row){row={t,minX:Infinity,maxX:-Infinity,sumY:0,sumZ:0,count:0};groups.set(t,row);}row.minX=Math.min(row.minX,data.positions[i*3]);row.maxX=Math.max(row.maxX,data.positions[i*3]);row.sumY+=data.positions[i*3+1];row.sumZ+=data.positions[i*3+2];row.count++;if(i%10===0)samples.push({index,p:data.positions.slice(i*3,i*3+3)});}
  const rows=[...groups.values()].sort((a,b)=>a.t-b.t).map(row=>[row.t,(row.minX+row.maxX)/2,Math.max(.004,(row.maxX-row.minX)/2),row.sumY/row.count,row.sumZ/row.count]);
  const top=rows[0][3];
  const parameter=y=>{let best=Infinity,value=0;for(let i=0;i<rows.length-1;i++){const a=rows[i],b=rows[i+1],f=clamp((y-a[3])/(b[3]-a[3])),candidate=a[3]+(b[3]-a[3])*f,dist=Math.abs(y-candidate);if(dist<best){best=dist;value=a[0]+(b[0]-a[0])*f;}}return value;};
  const warp=(p,t=parameter(p[1]))=>{const oldX=interpolate(rows,t,1),oldWidth=interpolate(rows,t,2),oldY=interpolate(rows,t,3),oldZ=interpolate(rows,t,4),q=clamp((p[0]-oldX)/oldWidth,-1.4,1.4),targetX=interpolate(plan.center,t),targetWidth=interpolate(plan.width,t),targetY=top+(plan.hem-top)*t;return [targetX+q*targetWidth,targetY+(p[1]-oldY)+plan.skew*q*t,oldZ+(p[2]-oldZ)*.82];};
  surfaces.set(index,{warp,rows,plan});
 }
 for(const index of [4,5,6]){const part=byId('skirt-panel-'+index);if(part)for(let i=0;i<part.topologyMesh.positions.length;i+=30)samples.push({index,p:part.topologyMesh.positions.slice(i,i+3)});}
 const pendants=new Map();
 for(const cord of parts.filter(p=>p.id.startsWith('light-cord-'))){const index=cord.id.includes('--1-')?0:1,d=cord.topologyMesh.positions;let high=-Infinity;for(let i=1;i<d.length;i+=3)high=Math.max(high,d[i]);const anchor=[0,0,0];let count=0;for(let i=0;i<d.length;i+=3)if(d[i+1]>high-.002){for(let k=0;k<3;k++)anchor[k]+=d[i+k];count++;}for(let k=0;k<3;k++)anchor[k]/=count;const target=surfaces.get(index).warp(anchor);pendants.set(cord.id.slice('light-cord'.length),target.map((v,k)=>v-anchor[k]));}
 const ownerFor=p=>{let distance=Infinity,owner=0;for(const sample of samples){const d=(p[0]-sample.p[0])**2+(p[1]-sample.p[1])**2+(p[2]-sample.p[2])**2;if(d<distance){distance=d;owner=sample.index;}}return owner;};
 const affected=[];
 for(const part of parts){
  const match=part.id.match(/^skirt-(?:panel|piping|inset)-(\d+)/),index=match?+match[1]:null;
  const special=part.id==='girl-dress-inset-pleat-seams'?3:part.id==='girl-dress-gold-tail-tassel'?1:/^girl-dress-(pastel-bauble|bauble-loop)-/.test(part.id)?2:/^light(?:-cord)?-/.test(part.id)?(part.id.includes('--1-')?0:1):null;
  const aggregate=['girl-tailoring-stitches','girl-dress-brocade-diamonds','girl-dress-running-stitches'].includes(part.id);
  if(!surfaces.has(index)&&special===null&&!aggregate)continue;
  const data=part.topologyMesh,isBauble=/^girl-dress-pastel-bauble-|^light-(?!cord)/.test(part.id);
  const pendantKey=part.id.startsWith('light-cord-')?part.id.slice('light-cord'.length):part.id.startsWith('light-')?part.id.slice('light'.length):null;
  if(pendantKey&&pendants.has(pendantKey)){const delta=pendants.get(pendantKey);for(let i=0;i<data.positions.length;i++)data.positions[i]=round(data.positions[i]+delta[i%3]);}
  else if(isBauble){
   const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let i=0;i<data.positions.length;i++){lo[i%3]=Math.min(lo[i%3],data.positions[i]);hi[i%3]=Math.max(hi[i%3],data.positions[i]);}const center=lo.map((v,i)=>(v+hi[i])/2),target=surfaces.get(special).warp(center);
   for(let i=0;i<data.positions.length;i++)data.positions[i]=round(data.positions[i]+target[i%3]-center[i%3]);
  }else{
   for(let i=0;i<data.positions.length;i+=3){const p=data.positions.slice(i,i+3);if(aggregate&&p[1]>2.925)continue;const own=index!==null?index:special!==null?special:ownerFor(p);if(!surfaces.has(own))continue;const t=part.id==='skirt-panel-'+index?data.uvs[i/3*2+1]:undefined;data.positions.splice(i,3,...surfaces.get(own).warp(p,t).map(round));}
  }
  part.tailoring={...(part.tailoring||{}),silhouette:'angular asymmetric wrap',revision:'festival-reference-v11.93'};affected.push(part.id);
 }
 // These are decorative skirt surfaces; the anatomical body and every piñata
 // component remain exactly as supplied by the existing model owner.
 model.festivalDress={...model.festivalDress,revision:'festival-reference-v11.93',style:'long angular overlapping festival wrap',silhouettePanels:[0,1,2,3],finishParts:affected};
 model.referenceProfile={...model.referenceProfile,hair:{...model.referenceProfile?.hair,silhouette:'compact tied locks beneath hair-attached piñatas',compactScale:.58,restoredGripParts:restored}};
 model.festivalFinish={revision:'v11.93',hairScale:.58,hairReach:hairBefore,restoredGripParts:restored,angularDressPanels:[0,1,2,3],matchedTrimParts:affected};
 return scene;
}
