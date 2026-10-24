// Fit the existing complete skirt to the actual waist and upper hip. Only the
// upper costume moves; the lower flare, knee heights and anatomy stay exact.
function atelierFittedSkirtV1195(scene){
 const model=scene.project.modelAtelier,round=v=>+v.toFixed(6),anchorY=2.4,
  profile=[
   [2.40,1,1],[2.50,.95,.95],[2.60,.90,.85],[2.65,.85,.80],
   [2.70,.86,.79],[2.80,.81,.80],[2.90,.75,.78],[3.00,.80,.80],[3.08,.80,.80]
  ];
 // Monotone cubic interpolation keeps the anchored lower flare C1 continuous
 // and avoids a hard belt line or a kink between waist and hip samples.
 const slope=(index,column)=>{
  if(index===0||index===profile.length-1)return 0;
  const a=profile[index-1],b=profile[index],c=profile[index+1],h0=b[0]-a[0],h1=c[0]-b[0],d0=(b[column]-a[column])/h0,d1=(c[column]-b[column])/h1;
  if(d0*d1<=0)return 0;
  const w0=2*h1+h0,w1=h1+2*h0;return (w0+w1)/(w0/d0+w1/d1);
 };
 const ratio=(y,column)=>{
  if(y<=anchorY)return 1;if(y>=profile.at(-1)[0])return profile.at(-1)[column];
  let i=0;while(i<profile.length-2&&profile[i+1][0]<y)i++;
  const a=profile[i],b=profile[i+1],h=b[0]-a[0],t=(y-a[0])/h,t2=t*t,t3=t2*t;
  return (2*t3-3*t2+1)*a[column]+(t3-2*t2+t)*h*slope(i,column)+(-2*t3+3*t2)*b[column]+(t3-t2)*h*slope(i+1,column);
 };
 const owned=new Set(model.kneeSkirtRefinement?.affectedParts||[]),affectedParts=[],waistRatios=[];
 const components=data=>{
  const count=data.positions.length/3,parent=Array.from({length:count},(_,i)=>i),find=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;};
  for(let i=0;i<data.indices.length;i+=3){const a=find(data.indices[i]),b=find(data.indices[i+1]),c=find(data.indices[i+2]);parent[b]=a;parent[c]=a;}
  const result=new Map();for(let i=0;i<count;i++){const root=find(i);if(!result.has(root))result.set(root,[]);result.get(root).push(i);}return [...result.values()];
 };
 const oldEnvelope=[
  [1.55,.675,.365],[2,.635,.345],[2.25,.595,.325],
  [2.5,.555,.305],[2.65,.510,.285],[2.8,.390,.245],[2.99,.325,.205]
 ];
 const nominal=y=>{
  let i=0;while(i<oldEnvelope.length-2&&oldEnvelope[i+1][0]<y)i++;
  const a=oldEnvelope[i],b=oldEnvelope[i+1],t=Math.max(0,Math.min(1,(y-a[0])/(b[0]-a[0])));
  return [a[1]+(b[1]-a[1])*t+.025,a[2]+(b[2]-a[2])*t+.025];
 };
 for(const part of model.parts){
  const jewel=/^waist-star-\d+$/.test(part.id);if(!owned.has(part.id)&&!jewel)continue;
  const data=part.topologyMesh,positions=data.positions,aggregate=part.id==='girl-tailoring-stitches';
  let selected=null;
  if(aggregate){
   selected=new Set();for(const group of components(data)){
    let meanY=0;for(const index of group)meanY+=positions[index*3+1]/group.length;
    // This aggregate also contains original bodice stitching. Those stitches
    // belong to the unchanged bodice rather than the skirt below the waist.
    if(meanY<=2.925)for(const index of group)selected.add(index);
   }
  }
  const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale)),inverse=matrix.clone().invert();
  let changed=false;
  for(let i=0;i<positions.length;i+=3){
   if(selected&&!selected.has(i/3))continue;
   const point=new THREE.Vector3(positions[i],positions[i+1],positions[i+2]).applyMatrix4(matrix),y=point.y;if(y<=anchorY)continue;
   const sx=ratio(y,1),sz=ratio(y,2),originalX=point.x,originalZ=point.z;point.x*=sx;
   if(jewel){
    // The old five-piece jewel was left floating at Z=.31. Bend the same
    // native jewel gently over the fitted front instead of leaving that gap.
    const r=nominal(y),rx=r[0]*sx,rz=r[1]*sz,q=Math.max(-.985,Math.min(.985,point.x/rx));
    point.z=rz*Math.sqrt(1-q*q)+.014+(point.z-.31);
   }else{
    point.z*=sz;
    // The upper right side panel begins slightly below Y2.79. Extend the two
    // existing front side edges across that tiny angular opening as they draw
    // into the waist; piping/inset relief follows the identical sector map.
    if(/^skirt-(?:panel|piping|inset)-[01](?:-|$)/.test(part.id)&&y>2.74){
     const r=nominal(y),rx=r[0]-.025+(/-0(?:-|$)/.test(part.id)?.012:.014),rz=r[1]-.025+(/-0(?:-|$)/.test(part.id)?.012:.014),
      x=originalX/rx,z=originalZ/rz,theta=Math.atan2(x,z),edge=Math.max(0,Math.min(1,(Math.abs(theta)-1.20)/.37)),h=Math.max(0,Math.min(1,(y-2.74)/.05)),
      angle=theta+Math.sign(theta)*.12*edge*h*h*(3-2*h),reach=Math.hypot(x,z);
     point.x=rx*sx*reach*Math.sin(angle);point.z=rz*sz*reach*Math.cos(angle);
    }
   }
   const local=point.applyMatrix4(inverse);positions[i]=round(local.x);positions[i+2]=round(local.z);
   // Ordinary panels keep local Y exact. Rotated jewel arms need a local-Y
   // correction under the inverse transform to retain their original world Y.
   if(jewel)positions[i+1]=round(local.y);
   changed=true;
  }
  if(changed){part.tailoring={...(part.tailoring||{}),revision:'fitted-waist-v11.95',waistFit:'close waist and smooth upper hip flare'};affectedParts.push(part.id);}
 }
 for(const y of [2.65,2.8,2.9])waistRatios.push({y,width:round(ratio(y,1)),depth:round(ratio(y,2))});
 model.festivalDress={...model.festivalDress,revision:'fitted-waist-v11.95',style:'fitted waist with overlapping full festival armor skirt'};
 model.skirtFitV1195={version:'v11.95',revision:'v11.95',anchorY,affectedParts,profile,waistRatios,scope:'waist and upper hip costume only',preserved:'anatomy, lower flare at and below Y2.4, knee heights, native topology and transforms'};
 return scene;
}
