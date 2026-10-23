// Finish the same connected skin surface across the neck, shoulder and arm
// muscles. Head and legs have their own refiners; fingers retain their detail.
function atelierSmoothExposedSkinV1193(scene){
 const model=scene.project.modelAtelier,body=model.parts.find(part=>part.id==='girl-organic-body');
 if(!body?.topologyMesh)throw Error('Connected anatomical skin is missing.');
 if(model.anatomySmoothing?.upperBody?.version==='v11.93')return scene;
 const mesh=body.topologyMesh,original=Float64Array.from(mesh.positions),count=original.length/3,weights=new Float64Array(count),active=[];
 const smooth=(value,a,b)=>{const t=Math.max(0,Math.min(1,(value-a)/(b-a)));return t*t*(3-2*t);};
 for(let i=0;i<count;i++){
  const x=Math.abs(original[i*3]),y=original[i*3+1];
  // Strict shared boundaries leave the portrait, calf refiner and feet intact.
  if(y>=3.58||y<2.745||(y<2.75&&x<=.85))continue;
  const upper=1-smooth(y,3.50,3.58),lower=x>.85?smooth(y,2.745,2.805):smooth(y,2.75,2.84);
  const palm=x>.85?.48*(1-smooth(x,.99,1.045)):1;
  const weight=upper*lower*palm;
  if(weight>.000001){weights[i]=weight;active.push(i);}
 }
 // Face incidences give each adjacent edge the same duplicated weight on this
 // closed manifold. CSR storage avoids a Set/object allocation per skin vertex.
 const degree=new Uint32Array(count);
 for(let i=0;i<mesh.indices.length;i+=3){for(let j=0;j<3;j++){const vertex=mesh.indices[i+j];if(weights[vertex])degree[vertex]+=2;}}
 const offsets=new Uint32Array(count+1);for(let i=0;i<count;i++)offsets[i+1]=offsets[i]+degree[i];
 const neighbors=new Uint32Array(offsets[count]),cursor=offsets.slice(0,count);
 for(let i=0;i<mesh.indices.length;i+=3){const a=mesh.indices[i],b=mesh.indices[i+1],c=mesh.indices[i+2];
  if(weights[a]){neighbors[cursor[a]++]=b;neighbors[cursor[a]++]=c;}
  if(weights[b]){neighbors[cursor[b]++]=a;neighbors[cursor[b]++]=c;}
  if(weights[c]){neighbors[cursor[c]++]=a;neighbors[cursor[c]++]=b;}
 }
 const energy=positions=>{let sum=0,weight=0;for(const i of active){const start=offsets[i],end=offsets[i+1];if(start===end)continue;const p=i*3,mean=[0,0,0];for(let j=start;j<end;j++){const n=neighbors[j]*3;for(let k=0;k<3;k++)mean[k]+=positions[n+k];}for(let k=0;k<3;k++){const d=mean[k]/(end-start)-positions[p+k];sum+=d*d*weights[i];}weight+=weights[i];}return Math.sqrt(sum/Math.max(1,weight));};
 const before=energy(original);let current=original.slice(),next=original.slice();
 const step=factor=>{
  for(const i of active){const start=offsets[i],end=offsets[i+1];if(start===end)continue;const p=i*3,mean=[0,0,0];
   for(let j=start;j<end;j++){const n=neighbors[j]*3;for(let k=0;k<3;k++)mean[k]+=current[n+k];}
   const delta=[0,0,0];for(let k=0;k<3;k++)delta[k]=current[p+k]+factor*weights[i]*(mean[k]/(end-start)-current[p+k])-original[p+k];
   const distance=Math.hypot(...delta),limit=.008*weights[i],scale=distance>limit?limit/distance:1;
   for(let k=0;k<3;k++)next[p+k]=original[p+k]+delta[k]*scale;
  }
  const previous=current;current=next;next=previous;
 };
 // Positive/negative Taubin pairs remove sampling bumps without collapsing the
 // deltoid, elbow, forearm and neck volumes into thin tubes.
 for(let pass=0;pass<8;pass++){step(.48);step(-.51);}
 // Very short triangles near welded sampling seams can fold even under a
 // small displacement. Backtrack just their local movement until every face
 // keeps its original orientation, including six-decimal native quantization.
 const proposed=current.slice(),factors=new Float64Array(count);factors.fill(1);
 const normal=(positions,a,b,c)=>{const ax=positions[b]-positions[a],ay=positions[b+1]-positions[a+1],az=positions[b+2]-positions[a+2],bx=positions[c]-positions[a],by=positions[c+1]-positions[a+1],bz=positions[c+2]-positions[a+2];return [ay*bz-az*by,az*bx-ax*bz,ax*by-ay*bx];};
 for(const i of active)for(let k=0;k<3;k++)current[i*3+k]=+current[i*3+k].toFixed(6);
 for(let pass=0;pass<24;pass++){
  const constrained=new Set();
  for(let i=0;i<mesh.indices.length;i+=3){const vertices=mesh.indices.slice(i,i+3);if(!vertices.some(vertex=>weights[vertex]))continue;
   const [a,b,c]=vertices.map(vertex=>vertex*3),before=normal(original,a,b,c),after=normal(current,a,b,c),area=before.reduce((sum,v)=>sum+v*v,0),dot=before.reduce((sum,v,k)=>sum+v*after[k],0);
   if(area>1e-22&&dot<=0)for(const vertex of vertices)if(weights[vertex])constrained.add(vertex);
  }
  if(!constrained.size)break;
  for(const i of constrained){factors[i]*=.5;for(let k=0;k<3;k++)current[i*3+k]=+(original[i*3+k]+(proposed[i*3+k]-original[i*3+k])*factors[i]).toFixed(6);}
 }
 let changed=0,maxDisplacement=0;
 for(const i of active){const p=i*3,distance=Math.hypot(current[p]-original[p],current[p+1]-original[p+1],current[p+2]-original[p+2]);if(distance>.000001)changed++;maxDisplacement=Math.max(maxDisplacement,distance);for(let k=0;k<3;k++)mesh.positions[p+k]=+current[p+k].toFixed(6);}
 body.textureBinding={...body.textureBinding,normalStrength:.03};
 // These are the existing fitted garment owners. Re-extract their thin closed
 // shells from the finished anatomy so the smoothed skin cannot pierce them.
 const fitted=[
  ['girl-fitted-sleeve',[(x,y,z)=>-.16-x,(x,y,z)=>y-2.79,(x,y,z)=>3.54-y],.006],
  ['model-0003',[(x,y,z)=>y-2.80,(x,y,z)=>3.40+.35*x-y,(x,y,z)=>.31-Math.abs(x)],.009],
  ['dark-shoulder',[(x,y,z)=>y-3.34-.6*x,(x,y,z)=>.04-x,(x,y,z)=>3.65-y],.016]
 ];
 for(const [id,planes,offset] of fitted){const part=model.parts.find(p=>p.id===id);if(!part)continue;part.topologyMesh=atelierAnimeClothShell(mesh,planes,offset);part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];}
 model.anatomySmoothing={...(model.anatomySmoothing||{}),upperBody:{version:'v11.93',method:'regional volume-preserving Taubin',pairs:8,vertices:changed,maxDisplacement:+maxDisplacement.toFixed(6),laplacianBefore:+before.toFixed(8),laplacianAfter:+energy(current).toFixed(8),normalStrength:.03,orientationProtectedVertices:active.filter(i=>factors[i]<1).length,skinTopologyPreserved:true,fittedGarments:fitted.map(item=>item[0]),protectedRegions:['portrait above 3.58','legs below 2.75','finger tips and nails','feet']}};
 return scene;
}
