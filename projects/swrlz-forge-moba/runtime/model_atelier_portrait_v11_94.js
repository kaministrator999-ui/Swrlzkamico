// Refine the existing welded portrait. The nose remains connected skin and the
// hair sockets stay fixed while the face becomes subtly narrower.
function atelierPortraitV1194(scene){
 const model=scene.project.modelAtelier,parts=model.parts,body=parts.find(p=>p.id==='girl-organic-body');
 if(!body?.topologyMesh)throw Error('Connected portrait skin is required.');
 const mesh=body.topologyMesh,round=v=>+v.toFixed(6),smooth=(v,a,b)=>THREE.MathUtils.smoothstep(v,a,b),widthScale=.95;
 const original=Float64Array.from(mesh.positions),contracted=original.slice(),count=original.length/3,weights=new Float64Array(count),active=[];
 // A smooth depth contraction removes the long hard bridge while preserving a
 // small rounded tip. Its depth derivative stays positive; there is no clipped
 // plane, added primitive or seam across the bridge/cheek transition.
 for(let i=0;i<count;i++){
  const p=i*3,x=original[p],y=original[p+1],z=original[p+2];
  if(y<3.945||y>4.16||Math.abs(x)>.105||z<.26)continue;
  const front=smooth(z,.26,.292),edge=smooth(y,3.945,3.970)*(1-smooth(y,4.12,4.16)),across=Math.exp(0-(x/.061)**4);
  const bridge=.68*Math.exp(0-((y-4.055)/.060)**2),tip=.30*Math.exp(0-((y-3.990)/.035)**2),relief=Math.max(0,z-atelierAnimeFaceZ(x,y));
  contracted[p+2]=z-relief*Math.min(.76,bridge+tip)*front*edge*across;
  const weight=front*edge*Math.exp(0-(x/.073)**4-((y-4.025)/.10)**4);
  if(weight>.00001){weights[i]=weight;active.push(i);}
 }
 // Unlike the preceding whole-face pass, this finish allows the nose itself
 // to relax. Volume-preserving pairs soften the nasal root, tip and underside.
 const neighbors=new Map();
 for(let f=0;f<mesh.indices.length;f+=3){const [a,b,c]=mesh.indices.slice(f,f+3);for(const [i,j,k] of [[a,b,c],[b,c,a],[c,a,b]])if(weights[i]){if(!neighbors.has(i))neighbors.set(i,new Set());neighbors.get(i).add(j).add(k);}}
 const energy=positions=>{let sum=0,total=0;for(const [i,adjacent] of neighbors){const p=i*3,mean=[0,0,0];for(const j of adjacent)for(let k=0;k<3;k++)mean[k]+=positions[j*3+k]/adjacent.size;for(let k=0;k<3;k++)sum+=(mean[k]-positions[p+k])**2*weights[i];total+=weights[i];}return Math.sqrt(sum/Math.max(1,total));};
 const before=energy(contracted);let current=contracted.slice();
 for(let pass=0;pass<10;pass++)for(const factor of [.42,-.43]){
  const previous=current.slice();for(const [i,adjacent] of neighbors){const p=i*3,mean=[0,0,0];for(const j of adjacent)for(let k=0;k<3;k++)mean[k]+=previous[j*3+k]/adjacent.size;
   const delta=mean.map((v,k)=>(v-previous[p+k])*factor*weights[i]);
   for(let k=0;k<3;k++)current[p+k]=contracted[p+k]+THREE.MathUtils.clamp(previous[p+k]+delta[k]-contracted[p+k],-.004*weights[i],.004*weights[i]);
  }
 }
 // Protect short field-sampling faces from a quantized local smoothing fold.
 const proposed=current.slice(),factors=new Float64Array(count);factors.fill(1);
 const normal=(a,b,c,data)=>{const u=[0,1,2].map(k=>data[b*3+k]-data[a*3+k]),v=[0,1,2].map(k=>data[c*3+k]-data[a*3+k]);return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];};
 for(const i of active)for(let k=0;k<3;k++)current[i*3+k]=round(current[i*3+k]);
 for(let pass=0;pass<24;pass++){
  const constrained=new Set();for(let f=0;f<mesh.indices.length;f+=3){const ids=mesh.indices.slice(f,f+3);if(!ids.some(i=>weights[i]))continue;const a=normal(...ids,contracted),b=normal(...ids,current),area=a.reduce((s,v)=>s+v*v,0),dot=a.reduce((s,v,k)=>s+v*b[k],0);if(area>1e-22&&dot<=0)for(const i of ids)if(weights[i])constrained.add(i);}
  if(!constrained.size)break;for(const i of constrained){factors[i]*=.5;for(let k=0;k<3;k++)current[i*3+k]=round(contracted[i*3+k]+(proposed[i*3+k]-contracted[i*3+k])*factors[i]);}
 }
 // A second, smaller finish rounds the residual alar/tip underside. Keep
 // the preceding validated portrait as the local fallback for tiny rim faces.
 const softReference=current.slice(),tipWeights=new Float64Array(count);
 for(const i of active){const p=i*3,x=current[p],y=current[p+1],w=weights[i]*Math.exp(0-(x/.071)**4-((y-3.991)/.043)**4);tipWeights[i]=w;current[p+2]-=Math.min(.007,Math.max(0,current[p+2]-atelierAnimeFaceZ(x,y))*.23)*w;}
 const tipBase=current.slice();
 for(let pass=0;pass<4;pass++){
  const previous=current.slice();for(const [i,adjacent] of neighbors){const p=i*3,mean=[0,0,0];for(const j of adjacent)for(let k=0;k<3;k++)mean[k]+=previous[j*3+k]/adjacent.size;
   for(let k=0;k<3;k++)current[p+k]=tipBase[p+k]+THREE.MathUtils.clamp(previous[p+k]+.35*tipWeights[i]*(mean[k]-previous[p+k])-tipBase[p+k],-.004*tipWeights[i],.004*tipWeights[i]);
  }
 }
 const tipProposed=current.slice(),tipFactors=new Float64Array(count);tipFactors.fill(1);
 for(const i of active)for(let k=0;k<3;k++)current[i*3+k]=round(current[i*3+k]);
 for(let pass=0;pass<32;pass++){
  const constrained=new Set();for(let f=0;f<mesh.indices.length;f+=3){const ids=mesh.indices.slice(f,f+3);if(!ids.some(i=>weights[i]))continue;const next=normal(...ids,current);for(const reference of [original,softReference]){const prior=normal(...ids,reference),area=prior.reduce((s,v)=>s+v*v,0),dot=prior.reduce((s,v,k)=>s+v*next[k],0);if(area>1e-22&&dot<=0)for(const i of ids)if(weights[i])constrained.add(i);}}
  if(!constrained.size)break;for(const i of constrained){tipFactors[i]*=.5;for(let k=0;k<3;k++)current[i*3+k]=round(softReference[i*3+k]+(tipProposed[i*3+k]-softReference[i*3+k])*tipFactors[i]);}
 }
 const noseAfter=energy(current);let noseVertices=0,maxDepthReduction=0,bridgeReliefBefore=0,bridgeReliefAfter=0,tipReliefBefore=0,tipReliefAfter=0;
 for(let i=0;i<count;i++){
  const p=i*3,y=current[p+1],factor=1-(1-widthScale)*smooth(y,3.70,3.91);
  mesh.positions[p]=round(current[p]*factor);mesh.positions[p+1]=round(current[p+1]);mesh.positions[p+2]=round(current[p+2]);
  if(weights[i]){noseVertices++;maxDepthReduction=Math.max(maxDepthReduction,original[p+2]-current[p+2]);}
  if(Math.abs(original[p])<.018&&original[p+2]>.29){
   const prior=Math.max(0,original[p+2]-atelierAnimeFaceZ(original[p],original[p+1])),next=Math.max(0,current[p+2]-atelierAnimeFaceZ(current[p],current[p+1]));
   if(original[p+1]>=4.025&&original[p+1]<=4.10){bridgeReliefBefore=Math.max(bridgeReliefBefore,prior);bridgeReliefAfter=Math.max(bridgeReliefAfter,next);}
   if(original[p+1]>=3.975&&original[p+1]<=4.015){tipReliefBefore=Math.max(tipReliefBefore,prior);tipReliefAfter=Math.max(tipReliefAfter,next);}
  }
 }
 // Apply that same head deformation in world coordinates to every facial
 // overlay and attached lock. Bun/grip owners and companion meshes are exact.
 const attached=[];
 for(const part of parts){
  if(part===body||part.group!=='Character'||/^hair-(bun|grip)-/.test(part.id))continue;
  const region=part.organicSurface?.region,isHair=['hair','splitHair'].includes(region),isFace=['eye','iris','lid','brow','lip'].includes(region)||/^(left|right)-earring$|^portrait-curl-/.test(part.id);
  if(!isHair&&!isFace)continue;
  const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale)),inverse=matrix.clone().invert(),a=part.topologyMesh.positions;
  for(let i=0;i<a.length;i+=3){const v=new THREE.Vector3().fromArray(a,i).applyMatrix4(matrix);let weight=smooth(v.y,3.70,3.91);
   // The upward tuft root is pinned to the unchanged hair socket; the rest of
   // the lock blends back to the narrower cap without pulling its piñata.
   if(isHair){const rootDistance=Math.hypot((Math.abs(v.x)-.34)/.080,(v.y-4.275)/.095,(v.z+.065)/.13);weight*=smooth(rootDistance,.35,1.8);}
   v.x*=1-(1-widthScale)*weight;v.applyMatrix4(inverse);a[i]=round(v.x);a[i+1]=round(v.y);a[i+2]=round(v.z);
  }
  attached.push(part.id);
 }
 if(model.portraitRefinement){model.portraitRefinement.version='v11.94';if(model.portraitRefinement.eyeCorners)for(const eye of Object.values(model.portraitRefinement.eyeCorners)){for(const key of ['inner','outer'])eye[key][0]*=widthScale;eye.slopeDegrees=round(Math.atan2(eye.outer[1]-eye.inner[1],Math.abs(eye.outer[0]-eye.inner[0]))*180/Math.PI);}}
 model.portraitRefinementV1194={version:'v11.94',changedParts:[body.id,...attached],head:{widthScale,neckBlend:[3.70,3.91],attachedParts:attached,fixedHairOwners:parts.filter(p=>/^hair-(bun|grip)-/.test(p.id)).map(p=>p.id),companionSocketsPreserved:true},nose:{method:'smooth bridge-depth contraction and nasal Taubin finish',bridgeContraction:.68,tipContraction:.30,tipReliefFinish:.23,smoothingPairs:10,tipFairingPasses:4,noseVertices,maxDepthReduction:round(maxDepthReduction),bridgeReliefBefore:round(bridgeReliefBefore),bridgeReliefAfter:round(bridgeReliefAfter),tipReliefBefore:round(tipReliefBefore),tipReliefAfter:round(tipReliefAfter),laplacianBefore:round(before),laplacianAfter:round(noseAfter),orientationProtectedVertices:active.filter(i=>factors[i]<1||tipFactors[i]<1).length,connectedTopologyPreserved:true}};
 if(model.referenceProfile){model.referenceProfile.version='v11.94';model.referenceProfile.face={...model.referenceProfile.face,headWidth:'subtly narrower oval',nose:'small smooth rounded nose with soft bridge'};}
 return scene;
}
