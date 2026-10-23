// Remap the existing continuous skin cross-sections. No replacement leg meshes,
// changed topology, hidden joint overlays or disconnected calf primitives.
function atelierSmoothLegsV1193(scene){
 const model=scene.project.modelAtelier,body=model.parts.find(p=>p.id==='girl-organic-body'),data=body.topologyMesh;
 const source=data.positions.slice(),round=v=>+v.toFixed(6),smooth=(v,a,b)=>{const t=Math.max(0,Math.min(1,(v-a)/(b-a)));return t*t*(3-2*t);};
 // y, lateral half-width, front skin, back skin. The upper calf reaches its
 // fullness below the knee and then tapers continuously into the ankle.
 const target=[
  [.35,.058,.104,-.008],[.50,.068,.094,-.027],[.70,.086,.096,-.062],
  [.90,.101,.100,-.101],[1.10,.113,.107,-.126],[1.25,.113,.116,-.125],
  [1.40,.105,.129,-.101],[1.52,.102,.136,-.080],[1.65,.108,.139,-.073],
  [1.80,.124,.142,-.088],[2.00,.143,.145,-.113],[2.20,.154,.148,-.132],
  [2.42,.176,.151,-.146]
 ];
 // Use the current skin's own centerline, preserving the authored stance and
 // side-to-side symmetry rather than straightening the legs into cylinders.
 const original=target.map(([y])=>{
  let loX=Infinity,hiX=-Infinity,loZ=Infinity,hiZ=-Infinity;
  for(let i=0;i<source.length;i+=3){const x=source[i],py=source[i+1],z=source[i+2];if(x<.065||x>.85||Math.abs(py-y)>.019)continue;loX=Math.min(loX,x);hiX=Math.max(hiX,x);loZ=Math.min(loZ,z);hiZ=Math.max(hiZ,z);}
  if(!Number.isFinite(loX)||hiX-loX<.015||hiZ-loZ<.015)throw Error('Native calf section is unavailable at '+y);
  return [y,(loX+hiX)/2,(loZ+hiZ)/2,(hiX-loX)/2,(hiZ-loZ)/2];
 });
 // Shape-preserving Hermite interpolation gives every section a shared C1
 // tangent. There is no linear-band shoulder at the knee or calf anchors.
 const section=(rows,y,k)=>{
  let i=0;while(i<rows.length-2&&rows[i+1][0]<y)i++;
  const a=rows[i],b=rows[i+1],h=b[0]-a[0],t=Math.max(0,Math.min(1,(y-a[0])/h));
  const slope=j=>{
   if(j===0)return (rows[1][k]-rows[0][k])/(rows[1][0]-rows[0][0]);
   if(j===rows.length-1)return (rows[j][k]-rows[j-1][k])/(rows[j][0]-rows[j-1][0]);
   const l=(rows[j][k]-rows[j-1][k])/(rows[j][0]-rows[j-1][0]),r=(rows[j+1][k]-rows[j][k])/(rows[j+1][0]-rows[j][0]);return l*r<=0?0:2*l*r/(l+r);
  };
  return (2*t*t*t-3*t*t+1)*a[k]+(t*t*t-2*t*t+t)*h*slope(i)+(-2*t*t*t+3*t*t)*b[k]+(t*t*t-t*t)*h*slope(i+1);
 };
 let changed=0;
 for(let i=0;i<source.length;i+=3){
  const x=source[i],y=source[i+1],z=source[i+2],side=x<0?-1:1;
  if(y<=.39||y>=2.42||Math.abs(x)<.065||Math.abs(x)>.85)continue;
  const weight=smooth(y,.39,.59)*(1-smooth(y,2.22,2.42))*smooth(Math.abs(x),.065,.15);if(weight<=0)continue;
  const cx=section(original,y,1),cz=section(original,y,2),rx=Math.max(.02,section(original,y,3)),rz=Math.max(.02,section(original,y,4));
  const angle=Math.atan2((z-cz)/rz,(Math.abs(x)-cx)/rx),front=section(target,y,2),back=section(target,y,3),mid=(front+back)/2;
  const nextX=side*(cx+Math.cos(angle)*section(target,y,1)),nextZ=mid+Math.sin(angle)*(front-back)/2;
  data.positions[i]=round(x+(nextX-x)*weight);data.positions[i+2]=round(z+(nextZ-z)*weight);changed++;
 }
 model.legRefinement={revision:'smooth-muscle-flow-v11.93',method:'continuous-native-cross-section-remap',changedVertices:changed,profile:'smooth thigh to knee, full upper calf and tapered ankle',feetPreservedBelowY:.39,pelvisPreservedAboveY:2.42,bodyIndicesPreserved:true,sections:target.map(([y,radius,front,back])=>({y,lateralRadius:radius,front,back}))};
 return scene;
}
