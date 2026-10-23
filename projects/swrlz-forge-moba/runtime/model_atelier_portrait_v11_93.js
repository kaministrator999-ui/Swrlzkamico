// A continuous portrait pass over the original connected skin. The previous
// front/side max-mask is deliberately not accumulated into the new jaw.
function atelierPortraitRefinementV1193(scene,baselineBodyPositions){
 const model=scene.project.modelAtelier,parts=model.parts,skin=parts.find(p=>p.id==='girl-organic-body'),data=skin.topologyMesh;
 const round=value=>+value.toFixed(6),smooth=(value,a,b)=>THREE.MathUtils.smoothstep(value,a,b);
 if(!baselineBodyPositions||baselineBodyPositions.length!==data.positions.length)throw Error('Original portrait skin is required');
 const chinLift=y=>{const u=THREE.MathUtils.clamp((y-3.748)/.10,0,1);return .055*Math.exp(0-((y-3.79)/.13)**2)-.027*Math.sin(Math.PI*u)**2*(1-u);};
 const eyeSlope=Math.tan(14*Math.PI/180),orbitAngle=8*Math.PI/180;
 const reshape=(x,y,z)=>{
  if(y<3.58||y>4.30)return [x,y,z];
  const face=smooth(z,-.005,.17),side=smooth(Math.abs(x),.075,.17)*smooth(y,3.72,3.91),mask=(face+side-face*side)*smooth(y,3.64,3.73);
  const cheek=Math.exp(0-((y-3.985)/.085)**2),jaw=Math.exp(0-((y-3.88)/.085)**2),chin=Math.exp(0-((y-3.79)/.065)**2);
  let X=x*(1+mask*(.035*cheek+.065*jaw+.38*chin)),Y=y+mask*chinLift(y),Z=z+mask*(.008*cheek*Math.exp(0-((Math.abs(x)-.17)/.095)**2)+.003*chin);
  // Turn the actual orbital skin as well as the overlay eye. The centre bridge
  // is anchored and the blend is smooth, so the two sockets cannot form a seam.
  const sign=X<0?-1:1,u=sign*X-.12,v=Y-4.067;
  const w=Math.exp(0-(u/.14)**2-(v/.105)**2)*smooth(Math.abs(X),.015,.045)*smooth(Z,.13,.25)*smooth(Y,3.93,4.015)*(1-smooth(Y,4.20,4.29));
  const a=orbitAngle*w,c=Math.cos(a),s=Math.sin(a);
  X=sign*(.12+c*u-s*v);Y=4.067+s*u+c*v;
  return [X,Y,Z];
 };
 for(let i=0;i<data.positions.length;i+=3){const p=baselineBodyPositions.slice(i,i+3);if(p[1]>=3.58)for(const [k,v] of reshape(...p).entries())data.positions[i+k]=round(v);}
 // A small volume-preserving finish removes field sampling ridges on the
 // cheeks/jaw while anchoring eyes, lips, nostrils and ear bowls.
 const active=new Float32Array(data.positions.length/3),neighbors=new Map();
 for(let i=0;i<active.length;i++){
  const x=data.positions[i*3],y=data.positions[i*3+1],z=data.positions[i*3+2];
  let w=smooth(y,3.68,3.82)*(1-smooth(y,4.20,4.31));
  const nose=Math.exp(0-((x/.075)**2+((y-4.0)/.095)**2))*smooth(z,.25,.32);
  const eye=Math.exp(0-(((Math.abs(x)-.12)/.12)**2+((y-4.067)/.09)**2))*smooth(z,.15,.25);
  const mouth=Math.exp(0-((x/.085)**2+((y-3.925)/.055)**2))*smooth(z,.22,.29);
  const ear=smooth(Math.abs(x),.23,.28)*(1-smooth(Math.abs(y-4.015),.07,.13));
  active[i]=w*(1-.95*nose)*(1-.85*eye)*(1-.85*mouth)*(1-.9*ear);
 }
 for(let f=0;f<data.indices.length;f+=3){const a=data.indices[f],b=data.indices[f+1],c=data.indices[f+2];for(const [u,v,w] of [[a,b,c],[b,c,a],[c,a,b]])if(active[u]>.001){if(!neighbors.has(u))neighbors.set(u,new Set());neighbors.get(u).add(v).add(w);}}
 for(let pass=0;pass<2;pass++)for(const factor of [.27,-.28]){
  const previous=data.positions.slice();
  for(const [i,adjacent] of neighbors){const mean=[0,0,0];for(const j of adjacent)for(let k=0;k<3;k++)mean[k]+=previous[j*3+k]/adjacent.size;
   for(let k=0;k<3;k++)data.positions[i*3+k]=round(previous[i*3+k]+THREE.MathUtils.clamp((mean[k]-previous[i*3+k])*factor*active[i],-.002,.002));}
 }
 const oldLift=y=>.045*Math.exp(0-((y-3.775)/.115)**2)+.013*Math.exp(0-((y-3.747)/.027)**2);
 for(const p of parts.filter(p=>p.organicSurface?.region==='lip'))for(let i=0;i<p.topologyMesh.positions.length;i+=3){const a=p.topologyMesh.positions;let y=a[i+1];for(let j=0;j<8;j++)y=a[i+1]-oldLift(y);a.splice(i,3,...reshape(a[i],y,a[i+2]).map(round));}
 const faceZ=(x,y)=>{
  let bx=x,by=y;
  for(let j=0;j<6;j++){const p=reshape(bx,by,atelierAnimeFaceZ(bx,by));bx+=x-p[0];by+=y-p[1];}
  return reshape(bx,by,atelierAnimeFaceZ(bx,by))[2];
 };
 const onEye=(side,u,v,depth=0)=>{const x=side*(.12+u),y=4.067+eyeSlope*u+v;return [x,y,faceZ(x,y)+depth];};
 const place=(id,name,mesh,color,region,texture=false)=>{
  const old=parts.find(p=>p.id===id);if(!old)throw Error('Portrait part missing: '+id);
  Object.assign(old,{name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material:['eye','iris'].includes(region)?'gloss':'silk',organicSurface:{species:'anime',region},topologyMesh:mesh});
  if(!texture)delete old.textureBinding;return old;
 };
 const lens=(side,center,radii,depth,thickness,almond=false)=>{
  const positions=[],uvs=[],indices=[],rows=40,cols=72;
  for(let i=0;i<=rows;i++){const phi=i/rows*Math.PI,r=Math.sin(phi),z=Math.cos(phi);
   for(let j=0;j<=cols;j++){const angle=j/cols*Math.PI*2,s=Math.sin(angle),u=Math.cos(angle)*r*radii[0],v=s*r*(almond?(s>=0?radii[1]:radii[2]):radii[1])*(almond?Math.pow(Math.abs(s),.28):1),p=onEye(side,center[0]+u,center[1]+v,depth+z*thickness);positions.push(...p.map(round));uvs.push(.5+u/(radii[0]*2),.5+v/(radii[1]*2));if(i<rows&&j<cols){const a=i*(cols+1)+j,b=a+cols+1;indices.push(a,b,a+1,a+1,b,b+1);}}
  }
  if(side<0)for(let i=0;i<indices.length;i+=3){const b=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=b;}
  return atelierAnimalWeld({positions,uvs,indices});
 };
 const corners={};
 for(const side of [-1,1]){
  const label=side<0?'left':'right';
  place(label+'-sclera',label+' eye · rising almond aperture',lens(side,[0,0],[.092,.046,.036],.003,.011,true),'#fff7ef','eye');
  place(label+'-iris',label+' eye · shallow amber cornea',lens(side,[.001,.003],[.0385,.0405],.0145,.003),'#ffffff','iris',true);
  place('girl-pupil-'+label,label+' eye · rounded shallow dark pupil',lens(side,[.001,.004],[.017,.0195],.019,.00085),'#241421','eye');
  place(label+'-eye-catch',label+' eye · upper catchlight',lens(side,[-.009,.016],[.0042,.0052],.0205,.0004),'#fffdf5','eye');
  const second=parts.find(p=>p.id===label+'-eye-catch2');if(second)place(label+'-eye-catch2',label+' eye · secondary catchlight',lens(side,[.009,-.009],[.002,.0023],.0203,.0003),'#f8ffff','eye');
  const path=(xy,d)=>xy.map(([u,v])=>onEye(side,u,v,d));
  const upper=path([[-.092,0],[-.063,.033],[-.016,.046],[.042,.036],[.092,0],[.112,.012]],.009);
  const lower=path([[-.092,0],[-.057,-.026],[0,-.036],[.06,-.025],[.092,0]],.0065);
  place(label+'-upper-lid',label+' eye · rising upper lid and tapered outer wing',atelierAnimeStrand(upper,[.0008,.0038,.0048,.0060,.0030,.00015],80,12,.65),'#30202b','lid');
  place(label+'-lower-lid',label+' eye · soft rising waterline',atelierAnimeStrand(lower,[.0003,.0012,.0016,.0011,.0002],64,10,.55),'#bc8a90','lid');
  place(label+'-brow',label+' brow · fitted softly lifted arch',atelierAnimeStrand(path([[-.075,.084],[-.035,.102],[.015,.108],[.06,.095],[.089,.075]],.0075),[.0014,.0036,.0040,.0025,.0002],64,12,.45),'#59373a','brow');
  for(let j=0;j<3;j++)place(label+'-lash-'+j,label+' eye · tapered outward upper lash '+(j+1),atelierAnimeStrand(path([[.058+j*.011,.029-j*.007],[.075+j*.012,.042-j*.005],[.09+j*.012,.046-j*.004]],.010),[.0025,.0018,.0001],24,8,.55),'#30202b','lid');
  const inner=onEye(side,-.092,0),outer=onEye(side,.092,0);corners[label]={inner,outer,rise:round(outer[1]-inner[1]),slopeDegrees:14};
 }
 model.portraitRefinement={version:'v11.93',skin:'continuous smooth cheek, jaw and rounded chin',connectedIndicesPreserved:true,eyeCorners:corners,pupils:'rounded shallow corneal lenses',localSkinFinish:{passes:2,method:'anchored Taubin',maximumStep:.002}};
 if(model.referenceProfile){model.referenceProfile.version='v11.93';model.referenceProfile.face={...model.referenceProfile.face,eyeShape:'low inner corner rising to outer corner',eyeCantDegrees:14,cheeks:'continuous soft cheek-to-jaw transition',chin:'small smooth rounded chin'};}
 return scene;
}
