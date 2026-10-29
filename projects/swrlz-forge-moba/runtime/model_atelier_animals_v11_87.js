// Native organic volume tool. Smooth fields are resampled into one welded,
// editable indexed surface: construction volumes never become visible parts.
function atelierAnimalSurface(field,bounds,step=.045){
 const [lo,hi]=bounds,n=lo.map((a,i)=>Math.ceil((hi[i]-a)/step)+1),spacing=lo.map((a,i)=>(hi[i]-a)/(n[i]-1)),size=n[0]*n[1]*n[2],values=new Float32Array(size);
 const index=(x,y,z)=>x+n[0]*(y+n[1]*z),point=id=>{const x=id%n[0],y=Math.floor(id/n[0])%n[1],z=Math.floor(id/(n[0]*n[1]));return [lo[0]+x*spacing[0],lo[1]+y*spacing[1],lo[2]+z*spacing[2]];};
 for(let i=0;i<size;i++)values[i]=field(...point(i));
 const positions=[],uvs=[],indices=[],edges=new Map(),tetra=[[0,5,1,6],[0,1,2,6],[0,2,3,6],[0,3,7,6],[0,7,4,6],[0,4,5,6]],offsets=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]];
 const vertex=(a,b)=>{const key=a<b?a+':'+b:b+':'+a;if(edges.has(key))return edges.get(key);const pa=point(a),pb=point(b),t=values[a]/(values[a]-values[b]),p=pa.map((v,i)=>v+(pb[i]-v)*t),id=positions.length/3;positions.push(...p);uvs.push((p[2]-lo[2])/(hi[2]-lo[2]),(p[1]-lo[1])/(hi[1]-lo[1]));edges.set(key,id);return id;};
 const face=(a,b,c)=>{if(a===b||b===c||c===a)return;const p=positions.slice(a*3,a*3+3),q=positions.slice(b*3,b*3+3),r=positions.slice(c*3,c*3+3),u=q.map((v,i)=>v-p[i]),v=r.map((v,i)=>v-p[i]),normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],length=Math.hypot(...normal);if(length<1e-12)return;const mid=p.map((v,i)=>(v+q[i]+r[i])/3),e=.001;const gradient=mid.map((_,i)=>{const a=mid.slice(),b=mid.slice();a[i]+=e;b[i]-=e;return field(...a)-field(...b);});if(normal.reduce((s,v,i)=>s+v*gradient[i],0)<0)indices.push(a,c,b);else indices.push(a,b,c);};
 for(let z=0;z<n[2]-1;z++)for(let y=0;y<n[1]-1;y++)for(let x=0;x<n[0]-1;x++){
  const cube=offsets.map(([a,b,c])=>index(x+a,y+b,z+c));if(cube.every(i=>values[i]>=0)||cube.every(i=>values[i]<0))continue;
  for(const t of tetra){const inside=t.map(i=>cube[i]).filter(i=>values[i]<0),outside=t.map(i=>cube[i]).filter(i=>values[i]>=0);if(!inside.length||!outside.length)continue;
   if(inside.length===1)face(...outside.map(i=>vertex(inside[0],i)));else if(outside.length===1)face(...inside.map(i=>vertex(outside[0],i)));else{const [a,b]=inside,[c,d]=outside,ac=vertex(a,c),ad=vertex(a,d),bc=vertex(b,c),bd=vertex(b,d);face(ac,ad,bc);face(ad,bd,bc);}
  }
 }
 return {positions:positions.map(v=>+v.toFixed(6)),uvs:uvs.map(v=>+v.toFixed(6)),indices};
}
function atelierAnimalWeld(data){
 const positions=[],uvs=[],indices=[],vertices=new Map(),remap=[],seen=new Set();
 for(let i=0;i<data.positions.length;i+=3){const p=data.positions.slice(i,i+3).map(v=>+v.toFixed(6)),key=p.join(',');let id=vertices.get(key);if(id===undefined){id=positions.length/3;vertices.set(key,id);positions.push(...p);uvs.push(...data.uvs.slice(i/3*2,i/3*2+2));}remap.push(id);}
 for(let i=0;i<data.indices.length;i+=3){const t=data.indices.slice(i,i+3).map(j=>remap[j]);if(new Set(t).size<3)continue;const key=t.slice().sort((a,b)=>a-b).join(',');if(seen.has(key))continue;seen.add(key);indices.push(...t);}
 return {positions,uvs,indices};
}
function atelierAnimalUV(data,region){
 if(!['wool','coat','tail'].includes(region))return data;
 const p=data.positions,zs=p.filter((_,i)=>i%3===2),lo=Math.min(...zs),hi=Math.max(...zs);
 data.uvs=[];for(let i=0;i<p.length;i+=3)data.uvs.push(+((Math.atan2(p[i],p[i+1]-1.2)+Math.PI)/(2*Math.PI)).toFixed(6),+((p[i+2]-lo)/Math.max(.001,hi-lo)).toFixed(6));
 return data;
}
function atelierAnimalBuild(species){
 if(!['sheep','wolf'].includes(species))throw Error('Choose sheep or wolf.');
 const sheep=species==='sheep',parts=[],mass=[],smin=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
 const ellipsoid=(x,y,z,c,r)=>{const p=[x-c[0],y-c[1],z-c[2]],k0=Math.hypot(...p.map((v,i)=>v/r[i])),k1=Math.hypot(...p.map((v,i)=>v/(r[i]*r[i])));return k1?k0*(k0-1)/k1:-Math.min(...r);};
 const addMass=(c,r,k=.16)=>mass.push({c,r,k});
 const add=(name,data,color,region,atlas='fur',normal=.16)=>{const p={id:species+'-'+parts.length,name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material:region==='eye'?'gloss':'matte',group:region,topologyMesh:atelierAnimalUV(atelierAnimalWeld(data),region),organicSurface:{species,region}};if(atlas)p.textureBinding={set:'wildwood-4k',tile:atlas,normalStrength:normal};parts.push(p);return p;};
 const volume=(name,c,r,color,region,atlas='fur',detail=.024)=>add(name,atelierAnimalSurface((x,y,z)=>ellipsoid(x,y,z,c,r),[c.map((v,i)=>v-r[i]-.04),c.map((v,i)=>v+r[i]+.04)],detail),color,region,atlas);
 const tube=(name,points,radii,color,region,atlas='fur',detail=.018)=>{const cs=points.map(p=>new THREE.Vector3(...p)),curve=new THREE.CatmullRomCurve3(cs),samples=Array.from({length:32},(_,i)=>{const t=i/31,p=curve.getPoint(t),f=t*(radii.length-1),a=Math.min(radii.length-2,Math.floor(f)),r=radii[a]+(radii[a+1]-radii[a])*(f-a);return {p,r};}),bound=new THREE.Box3().setFromPoints(cs).expandByScalar(Math.max(...radii)+.04);return add(name,atelierAnimalSurface((x,y,z)=>Math.min(...samples.map(s=>Math.hypot(x-s.p.x,y-s.p.y,z-s.p.z)-s.r)),[bound.min.toArray(),bound.max.toArray()],detail),color,region,atlas);};
 if(sheep){
  addMass([0,1.18,-.14],[.55,.57,.91],.24);addMass([0,1.43,.55],[.39,.49,.48],.22);addMass([0,1.69,.83],[.28,.38,.3],.22);
 }else{
  addMass([0,1.18,-.05],[.33,.4,.99],.25);addMass([0,1.33,.50],[.4,.49,.44],.24);addMass([0,1.39,.80],[.33,.45,.36],.24);addMass([0,1.66,1.01],[.29,.34,.35],.20);addMass([0,1.56,1.36],[.19,.18,.42],.13);
 }
 for(const side of [-1,1]){
  if(sheep){addMass([side*.34,1.02,-.68],[.25,.42,.31],.18);addMass([side*.33,1.02,.49],[.21,.4,.26],.17);}
  else{addMass([side*.25,1.02,-.70],[.28,.40,.34],.2);addMass([side*.29,1.06,.46],[.18,.46,.22],.17);}
 }
 const baseField=(x,y,z)=>{let d=10;for(const m of mass)d=smin(d,ellipsoid(x,y,z,m.c,m.r),m.k);if(sheep){const curl=Math.sin(19*x+Math.sin(8*z))*Math.sin(17*y+Math.sin(9*x))*Math.sin(18*z+Math.sin(9*y));d-=.024*curl+.004*Math.sin(x*23+y*19+z*21);}else{d-=.002*Math.sin(19*z+Math.sin(9*y))*Math.sin(17*x+8*y);const waist=Math.exp(-(((z+.28)/.35)**2+((y-.92)/.25)**2));d+=.035*waist;}return d;};
 add(sheep?'Fleece · continuous shoulders, barrel and haunches':'Wolf · fused ribs, shoulder blades, neck, skull and muzzle',atelierAnimalSurface(baseField,[[-.95,.43,-1.3],[.95,sheep?2.16:2.2,1.94]],sheep?.032:.035),'#ffffff',sheep?'wool':'coat',sheep?'ivory':'fur',sheep?.32:.12);
 if(sheep){
  const head=(x,y,z)=>{let d=smin(ellipsoid(x,y,z,[0,1.75,1.10],[.24,.30,.27]),ellipsoid(x,y,z,[0,1.50,1.32],[.17,.21,.22]),.12);d=smin(d,ellipsoid(x,y,z,[0,1.61,1.39],[.095,.22,.13]),.075);d=smin(d,ellipsoid(x,y,z,[0,1.36,1.36],[.13,.075,.17]),.07);d+=.032*Math.exp(-(((Math.abs(x)-.15)/.07)**2+((y-1.57)/.13)**2+((z-1.34)/.15)**2));return d;};
  add('Face · tapered cheekbones and downturned ovine muzzle',atelierAnimalSurface(head,[[-.32,1.20,.77],[.32,2.07,1.65]],.022),'#c2afa0','face','leather',.4);
 }
 for(const side of [-1,1])for(const front of [false,true]){
  const x=side*(sheep?.34:.29),z=front?.49:-.68,label=(front?'Fore':'Hind')+(side<0?' left':' right');
  const points=front?[[x,1.1,z],[x,.72,z+.015],[x,.38,z+.06],[x,.16,z+.12]]:[[x,1.08,z],[x,.72,z+.19],[x,.39,z-.08],[x,.15,z+.02]];
  tube(label+' · muscle, knee, tendon and fetlock',points,sheep?[.115,.085,.057,.07]:[.14,.10,.055,.075],sheep?'#a8998b':'#c8c0ae','legs',sheep?'leather':'fur',.016);
  if(sheep)for(const toe of [-1,1])volume(label+' · split hoof '+toe,[x+toe*.039,.095,z+(front?.18:.09)],[.036,.085,.11],'#393532','hoof','leather',.012);
  else{
   volume(label+' · weight-bearing paw',[x,.10,z+(front?.17:.09)],[.112,.09,.18],'#b0a99a','paws','fur',.015);
   for(const toe of [-1.5,-.5,.5,1.5]){volume(label+' · articulated toe '+toe,[x+toe*.055,.078,z+(front?.29:.21)],[.041,.065,.075],'#c2b9a7','paws','fur',.012);tube(label+' · claw '+toe,[[x+toe*.055,.08,z+(front?.335:.255)],[x+toe*.055,.055,z+(front?.40:.32)]],[.016,.003],'#282a29','claws',null,.009);}
  }
 }
 // Curved, closed leaf ears with asymmetric tip and a recessed inner pinna.
 for(const side of [-1,1]){
  const ear=(inner=false)=>{const pos=[],uv=[],idx=[],rows=28,cols=24;for(let i=0;i<=rows;i++){const t=i/rows,width=Math.pow(Math.sin(Math.PI*t),.72)*(sheep?.13:.14)*(inner?.67:1),cx=side*(sheep?.19+.52*t:.19+.09*t),cy=sheep?1.87-.13*t+Math.sin(t*Math.PI)*.04:1.87+.32*t,cz=sheep?1.06-.06*t:1.02-.12*t;for(let j=0;j<=cols;j++){const a=2*Math.PI*j/cols,thickness=(inner?.004:.029)*Math.pow(Math.sin(Math.PI*t),.7);pos.push(cx+(sheep?0:width*Math.cos(a)),cy+(sheep?width*Math.cos(a):.01*Math.cos(a)),cz+thickness*Math.sin(a)-(inner?-.026:0));uv.push(j/cols,t);if(i<rows&&j<cols){const k=i*(cols+1)+j;idx.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}}}return{positions:pos,uvs:uv,indices:idx};};
  add((side<0?'Left':'Right')+' ear · curved outer helix',ear(),'#ffffff','ears',sheep?'ivory':'fur',.5);add((side<0?'Left':'Right')+' ear · recessed pinna',ear(true),sheep?'#b99691':'#8c7772','innerEar','leather',.3);
  const ex=side*(sheep?.205:.20),ey=sheep?1.80:1.77,ez=sheep?1.245:1.15;
  volume((side<0?'Left':'Right')+' eye · almond socket',[ex,ey,ez],[.044,.049,.055],'#24211e','eye',null,.008);
  volume((side<0?'Left':'Right')+' eye · amber iris',[ex+side*.014,ey+.003,ez+.040],[.030,.032,.020],sheep?'#ac8e48':'#d69e35','eye','amber',.006);
  volume((side<0?'Left':'Right')+' eye · '+(sheep?'horizontal':'round')+' pupil',[ex+side*.016,ey+.003,ez+.056],[sheep?.026:.015,sheep?.007:.024,.007],'#0b1011','eye',null,.005);
  volume((side<0?'Left':'Right')+' eye · corneal catchlight',[ex+side*.007,ey+.023,ez+.063],[.006,.008,.004],'#fbf3da','eye',null,.004);
  tube((side<0?'Left':'Right')+' eye · upper brow and eyelid',[[ex-side*.045,ey+.025,ez+.027],[ex,ey+.079,ez+.035],[ex+side*.045,ey+.03,ez+.025]],[.018,.022,.014],sheep?'#a89989':'#5d615b','lid','fur',.008);
 }
 if(sheep){
  volume('Nose · divided ovine leather',[0,1.40,1.50],[.115,.065,.065],'#534640','nose','leather',.01);
  tube('Mouth · subtle split lip',[[-.12,1.365,1.47],[0,1.337,1.51],[.12,1.365,1.47]],[.009,.011,.009],'#473a34','mouth',null,.008);
  tube('Tail · short curled fleece',[[0,1.29,-.99],[.06,1.09,-1.18],[.03,.91,-1.13]],[.12,.11,.045],'#e8dfcd','wool','ivory',.018);
 }else{
  volume('Nose · canine nasal leather',[0,1.58,1.707],[.163,.103,.09],'#242b2b','nose','leather',.011);
  for(const side of [-1,1]){volume('Nostril · sculpted inset '+side,[side*.094,1.595,1.773],[.031,.021,.015],'#080e10','nose',null,.006);tube('Lip · tapered mouth line '+side,[[0,1.485,1.73],[side*.13,1.455,1.53],[side*.205,1.47,1.24]],[.009,.012,.007],'#292b2a','mouth',null,.009);}
  tube('Tail · low flowing brush',[[0,1.30,-.90],[.07,1.13,-1.31],[.17,.77,-1.61],[.22,.39,-1.58],[.18,.23,-1.37]],[.19,.23,.22,.14,.018],'#ffffff','tail','fur',.026);
 }
 return {schema:'swyrl-model-atelier-v1',name:sheep?'Clover · Meadow Sheep':'Fen · Wildwood Wolf',parts,meshGroups:[...new Set(parts.map(p=>p.group))].map((g,i)=>({id:species+'-assembly-'+i,name:g,members:parts.filter(p=>p.group===g).map(p=>p.id)})).filter(g=>g.members.length>=2),poseFrames:[],poseNeutral:null,editedAt:'local'};
}
