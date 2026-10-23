// Native welded anime sculpt. Construction fields never become visible parts.
function atelierAnimeGirlBody(){
 const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
 const ell=(x,y,z,c,r)=>{const dx=x-c[0],dy=y-c[1],dz=z-c[2],a=Math.hypot(dx/r[0],dy/r[1],dz/r[2]),b=Math.hypot(dx/r[0]**2,dy/r[1]**2,dz/r[2]**2);return b?a*(a-1)/b:-Math.min(...r);};
 const section=(rows,y,k)=>{let i=0;while(i<rows.length-2&&rows[i+1][0]<y)i++;const a=rows[i],b=rows[i+1],h=b[0]-a[0],t=THREE.MathUtils.clamp((y-a[0])/h,0,1),slope=j=>{if(j===0)return (rows[1][k]-rows[0][k])/(rows[1][0]-rows[0][0]);if(j===rows.length-1)return (rows[j][k]-rows[j-1][k])/(rows[j][0]-rows[j-1][0]);const l=(rows[j][k]-rows[j-1][k])/(rows[j][0]-rows[j-1][0]),r=(rows[j+1][k]-rows[j][k])/(rows[j+1][0]-rows[j][0]);return l*r<=0?0:2*l*r/(l+r);};return (2*t*t*t-3*t*t+1)*a[k]+(t*t*t-2*t*t+t)*h*slope(i)+(-2*t*t*t+3*t*t)*b[k]+(t*t*t-t*t)*h*slope(i+1);};
 const headRows=[[3.748,.006,.208,.208],[3.78,.045,.24,.095],[3.84,.105,.271,-.025],[3.93,.18,.292,-.11],[4.025,.243,.298,-.172],[4.12,.253,.298,-.2],[4.23,.251,.28,-.211],[4.34,.207,.23,-.19],[4.42,.11,.12,-.11],[4.455,.001,.008,.008]];
 const trunkRows=[[2.40,.13,.13,-.13],[2.55,.285,.17,-.16],[2.72,.29,.18,-.17],[2.9,.24,.155,-.16],[3.08,.193,.14,-.15],[3.25,.246,.185,-.15],[3.39,.278,.17,-.145],[3.47,.245,.13,-.12],[3.52,.13,.095,-.09]];
 const cross=(rows,x,y,z,power=2)=>{const w=section(rows,y,1),front=section(rows,y,2),back=section(rows,y,3),mid=(front+back)/2,depth=(front-back)/2,q=z>mid?power:2;return Math.max((Math.pow(Math.abs(x/w)**q+Math.abs((z-mid)/Math.max(.001,depth))**q,1/q)-1)*Math.min(w,Math.max(.001,depth)),rows[0][0]-y,y-rows.at(-1)[0]);};
 const capsules=(points,radii,flatten=1)=>{const rows=points.map((p,i)=>[p[1],p[0],p[2],radii[i]]).sort((a,b)=>a[0]-b[0]);return(x,y,z)=>{const t=THREE.MathUtils.clamp(y,rows[0][0],rows.at(-1)[0]),cx=section(rows,t,1),cz=section(rows,t,2),r=section(rows,t,3),e=.001,lo=Math.max(rows[0][0],t-e),hi=Math.min(rows.at(-1)[0],t+e),slope=(section(rows,hi,1)-section(rows,lo,1))/Math.max(.0001,hi-lo);return Math.hypot((x-cx)/Math.sqrt(1+slope*slope),(z-cz)/flatten,y-t)-r;};};
 const arms=[],legs=[],hands=[];
 for(const side of [-1,1]){
  arms.push(capsules([[side*.22,3.45,0],[side*.36,3.37,0],[side*.57,3.15,.015],[side*.67,3.06,.027],[side*.80,2.93,.05],[side*.914,2.80,.079]],[.10,.108,.073,.078,.065,.047],.86));
  legs.push(capsules([[side*.235,2.60,-.005],[side*.29,2.26,.005],[side*.39,1.79,.026],[side*.444,1.52,.046],[side*.525,1.12,-.01],[side*.60,.75,.012],[side*.64,.39,.045],[side*.64,.15,.12]],[.167,.153,.123,.096,.113,.089,.059,.067],.92));
  const fingerFields=[];for(let f=0;f<4;f++){const root=[side*(.94+f*.027),2.718+f*.013,.083],tip=[side*(1.016+f*.027),2.607+f*.018,.11];fingerFields.push(capsules([root,[side*(.987+f*.027),2.664+f*.015,.099],tip],[.018,.016,.0135],.9));}
  fingerFields.push(capsules([[side*.917,2.78,.10],[side*.945,2.735,.145],[side*.977,2.705,.15]],[.022,.015,.01]));
  hands.push((x,y,z)=>{let d=ell(x,y,z,[side*.967,2.765,.085],[.073,.086,.034]);for(const f of fingerFields)d=smooth(d,f(x,y,z),.016);return d;});
 }
 const field=(x,y,z)=>{let d=10;
  if(y>2.28&&y<3.67&&Math.abs(x)<.52)d=cross(trunkRows,x,y,z,2.3);
  if(y>3.36&&y<4.01&&Math.abs(x)<.23){d=smooth(d,ell(x,y,z,[0,3.685,.012],[.097,.275,.084]),.065);d=smooth(d,ell(x,y,z,[0,3.45,-.008],[.25,.085,.13]),.045);}
  if(y>3.69&&Math.abs(x)<.37){let h=cross(headRows,x,y,z,3.25);h=smooth(h,ell(x,y,z,[0,4.035,.302],[.026,.068,.036]),.022);h=smooth(h,ell(x,y,z,[0,3.984,.337],[.033,.025,.039]),.018);for(const s of [-1,1]){h=smooth(h,ell(x,y,z,[s*.027,3.975,.326],[.021,.015,.022]),.012);h=smooth(h,ell(x,y,z,[s*.273,4.008,.027],[.046,.078,.033]),.034);h=Math.max(h,-ell(x,y,z,[s*.297,4.014,.050],[.020,.046,.018]));const angle=s*Math.PI/30,c=Math.cos(angle),sn=Math.sin(angle),dx=x-s*.12,dy=y-4.067;h=Math.max(h,-ell(s*.12+c*dx+sn*dy,4.067-sn*dx+c*dy,z,[s*.118,4.067,.302],[.092,.056,.041]));}h=Math.max(h,-ell(x,y,z,[0,3.9,.306],[.055,.009,.025]));d=smooth(d,h,.042);}
  if(y<2.78&&Math.abs(x)>.06){for(const f of legs)d=smooth(d,f(x,y,z),.045);for(const side of [-1,1]){d=smooth(d,ell(x,y,z,[side*.64,.135,.16],[.111,.09,.205]),.04);d=smooth(d,ell(x,y,z,[side*.519,1.15,-.066],[.108,.27,.08]),.03);}}
  if(y>2.47&&y<3.59&&Math.abs(x)>.18){for(const f of arms)d=smooth(d,f(x,y,z),.04);if(y<2.92&&Math.abs(x)>.83)for(const f of hands)d=smooth(d,f(x,y,z),.025);}
  return d;
 };
 let data=atelierLivingClose(atelierAnimalSurface(field,[[-1.18,.025,-.27],[1.18,4.48,.44]],.015));
 // Conforming edge refinement adds face/finger density without splitting the
 // continuous body into disconnected head, wrist or ankle pieces.
 for(let pass=0;pass<2;pass++){
  const {positions,indices}=data,split=new Map();
  const middle=(a,b)=>{const key=a<b?a+':'+b:b+':'+a;if(split.has(key))return split.get(key);const p=[0,1,2].map(k=>(positions[a*3+k]+positions[b*3+k])/2),detail=p[1]>3.76?.007:Math.abs(p[0])>.88&&p[1]>2.52&&p[1]<2.91?.0045:1,dist=Math.hypot(...[0,1,2].map(k=>positions[a*3+k]-positions[b*3+k]));if(dist<detail)return null;for(let j=0;j<3;j++){const e=.0005,g=p.map((_,k)=>{const a=p.slice(),b=p.slice();a[k]+=e;b[k]-=e;return (field(...a)-field(...b))/(2*e);}),n=g.reduce((s,v)=>s+v*v,0);if(n<.0001)break;const d=THREE.MathUtils.clamp(field(...p),-.015,.015);for(let k=0;k<3;k++)p[k]-=g[k]*d/n;}const id=positions.length/3;positions.push(...p.map(v=>+v.toFixed(6)));split.set(key,id);return id;};
  for(let i=0;i<indices.length;i+=3)for(let e=0;e<3;e++)middle(indices[i+e],indices[i+(e+1)%3]);const next=[];
  const get=(a,b)=>split.get(a<b?a+':'+b:b+':'+a);
  for(let i=0;i<indices.length;i+=3){const [a,b,c]=indices.slice(i,i+3),ab=get(a,b),bc=get(b,c),ca=get(c,a),mask=(ab!==undefined?1:0)+(bc!==undefined?2:0)+(ca!==undefined?4:0);
   if(mask===0)next.push(a,b,c);if(mask===1)next.push(a,ab,c,ab,b,c);if(mask===2)next.push(a,b,bc,a,bc,c);if(mask===4)next.push(a,b,ca,b,c,ca);if(mask===3)next.push(a,ab,c,ab,bc,c,ab,b,bc);if(mask===5)next.push(a,ab,ca,ab,b,c,ab,c,ca);if(mask===6)next.push(a,b,ca,b,bc,ca,bc,c,ca);if(mask===7)next.push(a,ab,ca,ab,b,bc,ca,bc,c,ab,bc,ca);
  }data={positions,indices:next,uvs:[]};
 }
 // All original tetrahedron vertices and new detail vertices must lie on
 // the same analytic skin, otherwise subdivision amplifies interpolation noise.
 for(let i=0;i<data.positions.length;i+=3){const p=data.positions.slice(i,i+3);for(let j=0;j<3;j++){const e=.0004,g=p.map((_,k)=>{const a=p.slice(),b=p.slice();a[k]+=e;b[k]-=e;return (field(...a)-field(...b))/(2*e);}),n=g.reduce((s,v)=>s+v*v,0);if(n<.0001)break;const d=THREE.MathUtils.clamp(field(...p),-.008,.008);for(let k=0;k<3;k++)p[k]-=g[k]*d/n;}for(let k=0;k<3;k++)data.positions[i+k]=+p[k].toFixed(6);}
 // Anime finishing pass: retain the nasal bridge and alar planes with a
 // smaller, softer tip. This is a bounded surface deformation, not a sphere.
 for(let i=0;i<data.positions.length;i+=3){const x=data.positions[i],y=data.positions[i+1],z=data.positions[i+2];if(y<3.91||y>4.10||z<.292||Math.abs(x)>.10)continue;const w=Math.exp(-((x/.065)**2+((y-3.985)/.06)**2))*THREE.MathUtils.smoothstep(z,.292,.34);data.positions[i]=+(x*(1-.45*w)).toFixed(6);data.positions[i+2]=+(z-.018*w).toFixed(6);}
 data.uvs=[];for(let i=0;i<data.positions.length;i+=3){const [x,y,z]=data.positions.slice(i,i+3);data.uvs.push(+((Math.atan2(x,z-.015)+Math.PI)/(2*Math.PI)).toFixed(6),+(y>3.75?(y-3.75)/.73:y/3.75).toFixed(6));}
 return atelierLivingClose(data);
}
function atelierAnimeFaceZ(x,y){const rows=[[3.748,.006,.208,.208],[3.78,.045,.24,.095],[3.84,.105,.271,-.025],[3.93,.18,.292,-.11],[4.025,.243,.298,-.172],[4.12,.253,.298,-.2],[4.23,.251,.28,-.211],[4.34,.207,.23,-.19],[4.42,.11,.12,-.11],[4.455,.001,.008,.008]],w=atelierHeadSection(rows,y,1),front=atelierHeadSection(rows,y,2),back=atelierHeadSection(rows,y,3),mid=(front+back)/2;return mid+(front-mid)*Math.pow(Math.max(0,1-Math.pow(Math.abs(x/w),3.25)),1/3.25);}
function atelierAnimeStrand(path,radii,rows=36,cols=8,flatten=1){
 const curve=new THREE.CatmullRomCurve3(path.map(p=>new THREE.Vector3(...p))),positions=[],uvs=[],indices=[];
 for(let i=0;i<=rows;i++){const t=i/rows,p=curve.getPoint(t),tangent=curve.getTangent(t),right=new THREE.Vector3(0,0,1).cross(tangent).normalize(),up=new THREE.Vector3().crossVectors(tangent,right).normalize(),a=Math.min(radii.length-2,Math.floor(t*(radii.length-1))),f=t*(radii.length-1)-a,r=THREE.MathUtils.lerp(radii[a],radii[a+1],f*f*(3-2*f));for(let j=0;j<cols;j++){const theta=j/cols*Math.PI*2,v=p.clone().addScaledVector(right,Math.cos(theta)*r).addScaledVector(up,Math.sin(theta)*r*flatten);positions.push(...v.toArray().map(v=>+v.toFixed(6)));uvs.push(j/cols,t);if(i<rows){const a=i*cols+j,b=i*cols+(j+1)%cols;indices.push(a,b,a+cols,b,b+cols,a+cols);}}}
 for(const end of [0,rows]){const k=positions.length/3;positions.push(...curve.getPoint(end/rows).toArray().map(v=>+v.toFixed(6)));uvs.push(.5,end/rows);for(let j=0;j<cols;j++)indices.push(...(end?[k,end*cols+j,end*cols+(j+1)%cols]:[k,end*cols+(j+1)%cols,end*cols+j]));}for(let i=0;i<indices.length;i+=3){const b=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=b;}return {positions,uvs:uvs.map(v=>+v.toFixed(6)),indices};
}
// Native fitted-cloth shell: clip the actual body/garment surface and add
// a thin closed lining. Every sleeve point follows anatomy rather than a tube.
function atelierAnimeClothShell(data,planes,offset=.005){
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));g.setIndex(data.indices);g.computeVertexNormals();const normals=g.attributes.normal,positions=[],uvs=[],indices=[];
 for(let f=0;f<data.indices.length;f+=3){const ids=data.indices.slice(f,f+3);if(planes.some(plane=>ids.every(i=>plane(...data.positions.slice(i*3,i*3+3))<0)))continue;let polygon=ids.map(i=>[...data.positions.slice(i*3,i*3+3),...data.uvs.slice(i*2,i*2+2),normals.getX(i),normals.getY(i),normals.getZ(i)]);
  for(const plane of planes){const clipped=[];for(let j=0;j<polygon.length;j++){const a=polygon[j],b=polygon[(j+1)%polygon.length],da=plane(a[0],a[1],a[2]),db=plane(b[0],b[1],b[2]);if(da>=0)clipped.push(a);if((da>=0)!==(db>=0)){const t=da/(da-db);clipped.push(a.map((v,k)=>v+(b[k]-v)*t));}}polygon=clipped;if(!polygon.length)break;}
  if(polygon.length<3)continue;const base=positions.length/3;for(const p of polygon){const n=new THREE.Vector3(p[5],p[6],p[7]).normalize();positions.push(p[0]+n.x*offset,p[1]+n.y*offset,p[2]+n.z*offset);uvs.push(p[3],p[4]);}for(let j=1;j<polygon.length-1;j++)indices.push(base,base+j,base+j+1);
 }
 g.dispose();const patch=atelierAnimalWeld({positions,uvs,indices}),count=patch.positions.length/3,edges=new Map();for(let i=0;i<patch.indices.length;i+=3)for(let j=0;j<3;j++){const a=patch.indices[i+j],b=patch.indices[i+(j+1)%3],key=a<b?a+':'+b:b+':'+a,e=edges.get(key);if(e)e.count++;else edges.set(key,{a,b,count:1});}
 // A very close lining closes all hems, including clipped curved boundaries.
 const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.Float32BufferAttribute(patch.positions,3));pg.setIndex(patch.indices);pg.computeVertexNormals();const n=pg.attributes.normal,outer=patch.positions.slice(),uv=patch.uvs.slice(),idx=patch.indices.slice();for(let i=0;i<count;i++){patch.positions.push(+(outer[i*3]-n.getX(i)*.002).toFixed(6),+(outer[i*3+1]-n.getY(i)*.002).toFixed(6),+(outer[i*3+2]-n.getZ(i)*.002).toFixed(6));patch.uvs.push(...uv.slice(i*2,i*2+2));}for(let i=0;i<idx.length;i+=3)patch.indices.push(idx[i]+count,idx[i+2]+count,idx[i+1]+count);for(const {a,b,count:c} of edges.values())if(c===1)patch.indices.push(b,a,a+count,b,a+count,b+count);pg.dispose();return atelierLivingClose(patch);
}
function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){
 const project=structuredClone(original),m=project.project.modelAtelier,source=m.parts,remove=new Set(source.filter(p=>['model-0001','model-0002','left-ear','right-ear','palm-left','palm-right','arm-left','arm-right','smile','lower-lip','atelier-v118-left-leg','atelier-v118-right-leg'].includes(p.id)||/^(finger-|thumb-)/.test(p.id)||p.name.startsWith('Mouth opening')||p.name.startsWith('Upper teeth')).map(p=>p.id));
 const base=(id,name,data,color,region,tile='cloth')=>({id,name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material:region==='eye'?'gloss':'silk',group:'Character',organicSurface:{species:'anime',region},textureBinding:{set:'festival-4k',tile,normalStrength:region==='skin'?.09:region==='hair'?.26:.2},topologyMesh:data});
 const body=base('girl-organic-body','Festival · welded face, ears, neck, torso, arms, ten fingers, calves and feet',atelierAnimeGirlBody(),'#ffffff','skin','fur'),parts=[body];
 for(const p of source){if(remove.has(p.id))continue;
  // Eyes sit inside the new orbital wells; a dark pupil is now separate.
  if(p.id.endsWith('-sclera')){p.position[2]=.299;p.scale=[.088,.050,.026];}
  if(p.id.endsWith('-iris')){p.position[1]=4.067;p.position[2]=atelierAnimeFaceZ(p.position[0],4.067)+.024;p.rotation=[0,Math.sign(p.position[0])*.12,0];p.scale=[.038,.043,.015];p.color='#ffffff';}
  if(p.id.includes('eye-catch'))p.position[2]=atelierAnimeFaceZ(p.position[0],p.position[1])+.041;
  if(p.path&&(/brow|lash/.test(p.id)))p.path=p.path.map(([x,y,z])=>[x,y,atelierAnimeFaceZ(x,y)+.004]);
  let bake=p;
  if(p.id.startsWith('hair-'))bake={...p,meshDensity:p.kind==='sphere'?{u:80,v:48}:{u:80,v:24}};
  else if(p.id.endsWith('-iris'))bake={...p,meshDensity:{u:80,v:56}};
  else if(p.id.endsWith('-sclera'))bake={...p,meshDensity:{u:64,v:40}};
  else if(p.kind==='loft'&&p.group==='Character'&&Math.max(...p.radii)<.022)bake={...p,meshDensity:{u:64,v:10}};
  const smoothLock=p.id.startsWith('hair-')&&p.kind==='loft'?atelierAnimeStrand(p.path,p.radii,80,24,.30):null;
  const g=smoothLock?null:geometry(bake),a=g?.attributes.position,u=g?.attributes.uv;
  const region=p.id.startsWith('hair-')?'hair':p.id.includes('iris')||p.id.includes('sclera')||p.id.includes('eye-catch')?'eye':p.id.includes('shoe')?'leather':p.group==='Character'?'cloth':'paper';
  const data=smoothLock||{positions:Array.from(a.array).map(v=>+v.toFixed(6)),uvs:u?Array.from(u.array).map(v=>+v.toFixed(6)):Array(a.count*2).fill(0),indices:g.index?Array.from(g.index.array):Array.from({length:a.count},(_,i)=>i)};g?.dispose();
  if(p.id.endsWith('-iris')){data.uvs=[];for(let i=0;i<data.positions.length;i+=3)data.uvs.push(+((data.positions[i]+1)/2).toFixed(6),+((data.positions[i+1]+1)/2).toFixed(6));}
  if(p.id.endsWith('-sclera')){for(let i=0;i<data.positions.length;i+=3){const x=p.position[0]+data.positions[i]*p.scale[0],y=p.position[1]+data.positions[i+1]*p.scale[1],z=atelierAnimeFaceZ(x,y)+data.positions[i+2]*(data.positions[i+2]>0?.024:.034);data.positions.splice(i,3,+x.toFixed(6),+y.toFixed(6),+z.toFixed(6));}p.position=[0,0,0];p.scale=[1,1,1];p.rotation=[0,0,0];}
  const next=base(p.id,p.name,data,p.color,region,region==='hair'?'comet':region==='eye'?'amber':region==='leather'?'leather':p.material==='metal'?'brass':'cloth');next.position=p.position;next.rotation=p.rotation;next.scale=p.scale;next.group=p.group;next.material=p.material;
  if(p.id.endsWith('-sclera')||p.id.includes('eye-catch')||p.id.includes('lash')||p.id.includes('brow')||region==='paper')delete next.textureBinding;
  if(p.id.endsWith('-iris'))next.organicSurface.region='iris';if(p.id==='hair-cap')next.organicSurface.region='splitHair';parts.push(next);
 }
 for(const side of [-1,1]){const label=side<0?'left':'right',eyeZ=atelierAnimeFaceZ(side*.12,4.067)+.04;parts.push(base('girl-pupil-'+label,'Eye · '+label+' deep anime pupil',atelierLivingClose(atelierAnimalSurface((x,y,z)=>{const r=Math.hypot((x-side*.12)/.016,(y-4.068)/.026,(z-eyeZ)/.006);return (r-1)*.006;},[[side*.12-.021,4.035,eyeZ-.009],[side*.12+.021,4.102,eyeZ+.009]],.003)),'#1e1026','eye','amber'));
  const upper=[[side*.035,4.067,.300],[side*.078,4.11,.315],[side*.14,4.113,.311],[side*.204,4.082,.285],[side*.221,4.096,.274]],lower=[[side*.037,4.059,.303],[side*.12,4.019,.316],[side*.202,4.061,.285]];
  for(const [suffix,path,radii,color] of [['upper-lid',upper,[.001,.0038,.0048,.0032,.0004],'#2b202d'],['lower-lid',lower,[.0006,.0019,.0005],'#bf858a']]){const part=parts.find(p=>p.id===label+'-'+suffix);part.topologyMesh=atelierAnimeStrand(path.map(([x,y,z])=>[x,y,atelierAnimeFaceZ(x,y)+(suffix==='upper-lid'?.006:.003)]),radii,64,12);part.position=[0,0,0];part.scale=[1,1,1];part.rotation=[0,0,0];part.color=color;part.organicSurface.region='lid';}
  const lipPath=[[-.054,3.901,.299],[-.022,3.909,.312],[0,3.906,.317],[.022,3.91,.312],[.054,3.905,.299]];
  if(side===-1){parts.push(base('girl-cupid-lip','Face · sculpted cupid bow and lip roll',atelierAnimeStrand(lipPath,[.0007,.0034,.0026,.0034,.0007],64,16,.65),'#bd6678','lip','fur'));parts.push(base('girl-lower-lip','Face · soft smiling lower lip',atelierAnimeStrand([[-.053,3.899,.30],[0,3.886,.314],[.053,3.903,.30]],[.0006,.005,.0006],64,16,.65),'#dd8c98','lip','fur'));parts.push(base('girl-smile','Face · recessed smile interior',atelierAnimeStrand([[-.047,3.9,.30],[0,3.898,.308],[.047,3.904,.30]],[.0006,.0055,.0006],64,12,.35),'#632c43','lip','leather'));}
 }
 // Shaped nail plates and fine knuckle folds complete both hands.
 for(const side of [-1,1])for(let finger=0;finger<5;finger++){
  const thumb=finger===4,center=thumb?[side*.966,2.717,.165]:[side*(1.006+finger*.027),2.623+finger*.018,.125],width=thumb?.007:.006,length=thumb?.012:.0125,depth=.0016;
  const nail=base('girl-nail-'+side+'-'+finger,(side<0?'Left':'Right')+' hand · curved '+(thumb?'thumb':'finger '+(finger+1))+' nail plate',atelierLivingClose(atelierAnimalSurface((x,y,z)=>(Math.sqrt((x/width)**4+(y/length)**4+(z/depth)**2)-1)*depth,[[-width-.002,-length-.002,-depth-.001],[width+.002,length+.002,depth+.001]],.0018)),side<0?'#263140':'#f7dedd','nail','fur');nail.position=center;nail.rotation=[0,0,side*.6];nail.material='gloss';parts.push(nail);
  if(side>0&&!thumb){const x=side*(.99+finger*.027),y=2.658+finger*.015;parts.push(base('girl-knuckle-'+finger,'Hand · fine knuckle crease '+finger,atelierAnimeStrand([[x-.004,y-.003,.118],[x,y,.122],[x+.004,y+.003,.118]],[.0002,.00045,.0002],12,6),'#e4b7ba','skin','fur'));}
 }
 // Opaque fitted sleeve follows the original arm gesture; the body remains
 // continuous beneath it. Original asymmetrical bodice and underskirt remain.
 parts.push(base('girl-fitted-sleeve','Costume · anatomy-fitted black sleeve and closed lining',atelierAnimeClothShell(body.topologyMesh,[(x,y,z)=>-.16-x,(x,y,z)=>y-2.79,(x,y,z)=>3.54-y],.006),'#202634','cloth','cloth'));
 const shirt=parts.find(p=>p.id==='model-0003'),yoke=parts.find(p=>p.id==='dark-shoulder'),worldData=structuredClone(shirt.topologyMesh),matrix=new THREE.Matrix4().compose(new THREE.Vector3(...shirt.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...shirt.rotation)),new THREE.Vector3(...shirt.scale));for(let i=0;i<worldData.positions.length;i+=3){const p=new THREE.Vector3().fromArray(worldData.positions,i).applyMatrix4(matrix);for(let k=0;k<3;k++)worldData.positions[i+k]=+p.getComponent(k).toFixed(6);}shirt.topologyMesh=atelierAnimeClothShell(body.topologyMesh,[(x,y,z)=>y-2.80,(x,y,z)=>3.40+.35*x-y,(x,y,z)=>.31-Math.abs(x)],.009);shirt.position=[0,0,0];shirt.rotation=[0,0,0];shirt.scale=[1,1,1];yoke.topologyMesh=atelierAnimeClothShell(body.topologyMesh,[(x,y,z)=>y-3.34-.6*x,(x,y,z)=>.04-x,(x,y,z)=>3.65-y],.016);yoke.position=[0,0,0];yoke.rotation=[0,0,0];yoke.scale=[1,1,1];yoke.name='Costume · fitted asymmetric shoulder yoke';yoke.textureBinding={set:'festival-4k',tile:'cloth',normalStrength:.2};

 // Real tapered hair filaments layer across the original shaped color locks.
 for(const lock of source.filter(p=>/^hair-(front|back)-/.test(p.id)))for(let strand=0;strand<3;strand++){
  const path=lock.path.map((v,i)=>[v[0]+(strand-1)*.009,v[1]-.002*strand,v[2]+.009+Math.sin(i/(lock.path.length-1)*Math.PI)*.019]);const color=new THREE.Color(lock.color).lerp(new THREE.Color('#e7ffff'),.12+strand*.04).getHexString();parts.push(base('girl-fiber-'+lock.id+'-'+strand,'Hair · silky layered strand '+lock.id+' '+strand,atelierAnimeStrand(path,[.00045,.0016,.00025],40,6,.7),'#'+color,'hair','comet'));
 }
 // Tailoring: tiny raised lock stitches on the existing panel borders.
 const stitch={positions:[],uvs:[],indices:[]};for(const seam of source.filter(p=>/^(skirt-piping-|bodice-stitch-0)/.test(p.id))){const curve=new THREE.CatmullRomCurve3(seam.path.map(p=>new THREE.Vector3(...p)));for(let j=1;j<27;j++){const t=j/28,p=curve.getPoint(t),tangent=curve.getTangent(t),cross=new THREE.Vector3(0,0,1).cross(tangent).normalize().multiplyScalar(.004),a=p.clone().sub(cross),b=p.clone().add(cross);a.z+=.002;b.z+=.002;const data=atelierAnimeStrand([a.toArray(),p.clone().add(new THREE.Vector3(0,0,.003)).toArray(),b.toArray()],[.00055,.0007,.00055],6,6),offset=stitch.positions.length/3;stitch.positions.push(...data.positions);stitch.uvs.push(...data.uvs);stitch.indices.push(...data.indices.map(i=>i+offset));}}
 parts.push(base('girl-tailoring-stitches','Costume · individually modeled raised lock stitches',stitch,'#cbe9d7','cloth','cloth'));
 // Cant each complete eye assembly six degrees toward its outer upper corner.
 // Bake world-space vertices, then conform depth back to the same facial plane.
 for(const p of parts){const match=p.id.match(/^(left|right)-(sclera|iris|eye-catch2?|upper-lid|lower-lid|brow|lash-\d+)$/)||p.id.match(/^girl-pupil-(left|right)$/);if(!match)continue;const side=match[1]==='left'?-1:1,angle=side*Math.PI/30,c=Math.cos(angle),sn=Math.sin(angle),matrix=new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));for(let i=0;i<p.topologyMesh.positions.length;i+=3){const v=new THREE.Vector3().fromArray(p.topologyMesh.positions,i).applyMatrix4(matrix),dx=v.x-side*.12,dy=v.y-4.067,x=side*.12+c*dx-sn*dy,y=4.067+sn*dx+c*dy,z=v.z+atelierAnimeFaceZ(x,y)-atelierAnimeFaceZ(v.x,v.y);p.topologyMesh.positions.splice(i,3,+x.toFixed(6),+y.toFixed(6),+z.toFixed(6));}p.position=[0,0,0];p.rotation=[0,0,0];p.scale=[1,1,1];}
 for(const p of parts)if(p.id.startsWith('girl-fiber-')){delete p.textureBinding;p.color='#'+new THREE.Color(p.color).lerp(new THREE.Color(p.id.includes('--1-')?'#24b3c5':'#ed6058'),.8).getHexString();}
 m.parts=parts;m.poseFrames=[];m.poseNeutral=null;m.name='Prism · Organic Anime Festival';m.artDirection='Continuous welded anime anatomy with attached ears, ten articulated fingers, knee/shin/calf/Achilles forms, detailed eyes/lids/lips, layered split-color hair filaments, fitted asymmetric festival costume and real lock stitches. Original paper-ferret and bunny companions retained.';m.editedAt='local';m.assemblies.time=4;m.assemblies.autoplay=false;
 m.meshGroups=[];for(const group of ['Anatomy','Face and eyes','Hair','Costume','Companions']){const selected=parts.filter(p=>group==='Anatomy'?p.id===body.id:group==='Face and eyes'?['eye','iris','lid','lip'].includes(p.organicSurface.region):group==='Hair'?['hair','splitHair'].includes(p.organicSurface.region):group==='Companions'?p.group!=='Character':p.id!==body.id&&!['eye','iris','lid','lip','hair','splitHair'].includes(p.organicSurface.region)&&p.group==='Character');for(let i=0;i<selected.length;i+=30)if(selected.slice(i,i+30).length>=2)m.meshGroups.push({id:'girl-group-'+group.replaceAll(' ','-')+'-'+i,name:group+(i?' '+(i/30+1):''),members:selected.slice(i,i+30).map(p=>p.id)});}
 project.project.name=m.name;project.project.canonicalId='organic-anime-girl';project.project.template='model-atelier';project.engine='§wyrl§ Engine · Maker v11.91';return project;
}
