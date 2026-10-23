// Native organic anatomy refinement. Reference-informed seated canid proportions,
// blended muscle/tendon/paw fields and closed curved pinnae; no imported mesh.
function atelierLivingClose(data){
 const mesh=atelierAnimalWeld(data),edges=new Map();for(let i=0;i<mesh.indices.length;i+=3){const t=mesh.indices.slice(i,i+3);for(let j=0;j<3;j++){const a=t[j],b=t[(j+1)%3],key=a<b?a+':'+b:b+':'+a,e=edges.get(key);if(e)e.count++;else edges.set(key,{a,b,count:1});}}
 const boundary=[...edges.values()].filter(e=>e.count===1);for(const first of boundary){if(first.used)continue;const loop=[first],vertices=[first.a];let edge=first;while(edge.b!==first.a&&loop.length<12){const next=boundary.find(e=>!e.used&&!loop.includes(e)&&e.a===edge.b);if(!next)break;vertices.push(edge.b);loop.push(next);edge=next;}if(edge.b===first.a){for(let i=1;i<vertices.length-1;i++)mesh.indices.push(vertices[0],vertices[i+1],vertices[i]);for(const e of loop)e.used=true;}}return mesh;
}
function atelierLivingSweep(part,flatten=1,ripple=0){
 const curve=new THREE.CatmullRomCurve3(part.path.map(p=>new THREE.Vector3(...p)),false,'centripetal'),rows=64,cols=32,positions=[],uvs=[],indices=[];
 for(let i=0;i<=rows;i++){const t=i/rows,p=curve.getPoint(t),tan=curve.getTangent(t).normalize();let right=new THREE.Vector3(0,0,1).cross(tan);if(right.lengthSq()<.0001)right=new THREE.Vector3(1,0,0).cross(tan);right.normalize();const up=new THREE.Vector3().crossVectors(tan,right).normalize(),f=t*(part.radii.length-1),a=Math.min(part.radii.length-2,Math.floor(f)),k=f-a,s=k*k*(3-2*k),radius=part.radii[a]*(1-s)+part.radii[a+1]*s;
  for(let j=0;j<=cols;j++){const theta=j/cols*Math.PI*2,r=radius*(1+ripple*Math.sin(theta*5+t*8)*Math.sin(Math.PI*t)),v=p.clone().addScaledVector(right,Math.cos(theta)*r).addScaledVector(up,Math.sin(theta)*r*flatten);v.z+=.014*Math.sin(Math.PI*t)*Math.cos(theta)**2;positions.push(...v.toArray().map(v=>+v.toFixed(6)));uvs.push(+(j/cols).toFixed(6),+t.toFixed(6));if(i<rows&&j<cols){const q=i*(cols+1)+j;indices.push(q,q+1,q+cols+1,q+1,q+cols+2,q+cols+1);}}
 }
 for(const end of [0,rows]){const center=positions.length/3;positions.push(...curve.getPoint(end/rows).toArray().map(v=>+v.toFixed(6)));uvs.push(.5,end/rows);for(let j=0;j<cols;j++){const a=end*(cols+1)+j,b=a+1;indices.push(...(end?[center,a,b]:[center,b,a]));}}
 return atelierLivingClose({positions,uvs,indices});
}
const atelierLivingCourierBase=atelierRefineCourierProject;
atelierRefineCourierProject=function(original=COMET_COURIER_PROJECT){
 const project=atelierLivingCourierBase(original),model=project.project.modelAtelier,parts=model.parts;
 const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
 const ell=(x,y,z,c,r)=>{const dx=x-c[0],dy=y-c[1],dz=z-c[2],a=Math.hypot(dx/r[0],dy/r[1],dz/r[2]),b=Math.hypot(dx/(r[0]*r[0]),dy/(r[1]*r[1]),dz/(r[2]*r[2]));return b?a*(a-1)/b:-Math.min(...r);};
 const combine=(masses,k=.08)=>(x,y,z)=>{let d=10;for(const [c,r] of masses)d=smooth(d,ell(x,y,z,c,r),k);return d;};
 const capsule=(x,y,z,a,b,ra,rb)=>{const dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2],t=THREE.MathUtils.clamp(((x-a[0])*dx+(y-a[1])*dy+(z-a[2])*dz)/(dx*dx+dy*dy+dz*dz),0,1);return Math.hypot(x-a[0]-dx*t,y-a[1]-dy*t,z-a[2]-dz*t)-(ra*(1-t)+rb*t);};
 const mesh=(part,field,bounds,step,region)=>{part.kind='topologyMesh';part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];delete part.path;delete part.radii;delete part.meshDensity;delete part.hdFinish;part.topologyMesh=atelierLivingClose(atelierAnimalSurface(field,bounds,step));part.organicSurface={species:'courier',region};return part;};
 const body=parts.find(p=>p.id==='model-seed'),bodyField=combine([[[0,1.39,-.15],[.43,.54,.72]],[[0,1.78,.25],[.34,.40,.33]],[[0,2.04,.31],[.285,.32,.28]],[[-.29,1.59,.18],[.20,.33,.28]],[[.29,1.59,.18],[.20,.33,.28]],[[-.34,1.01,-.59],[.29,.41,.32]],[[.34,1.01,-.59],[.29,.41,.32]]],.14);
 body.name='Astra · scapulae, ribcage, tucked belly and seated pelvis';mesh(body,(x,y,z)=>bodyField(x,y,z)+.038*Math.exp(-(((z+.05)/.29)**2+((y-1.04)/.21)**2))-.006*Math.sin(z*16+y*8)*Math.sin(x*13),[[-.73,.50,-1.03],[.73,2.43,.78]],.033,'body');
 const skull=parts.find(p=>p.organicSurface?.region==='face'),head=combine([[[0,2.43,.43],[.415,.35,.355]],[[-.26,2.32,.56],[.18,.20,.22]],[[.26,2.32,.56],[.18,.20,.22]],[[0,2.22,.57],[.27,.13,.26]]],.085);
 skull.name='Astra · brow stop, cheekbones, orbital wells and jaw';mesh(skull,(x,y,z)=>{let d=head(x,y,z);for(const side of [-1,1])d=Math.max(d,-ell(x,y,z,[side*.245,2.48,.818],[.145,.094,.077]));return d;},[[-.53,2.04,.01],[.53,2.85,.91]],.018,'face');
 const muzzle=parts.find(p=>p.organicSurface?.region==='muzzle'),muzzleField=combine([[[0,2.34,.76],[.185,.145,.29]],[[0,2.265,.91],[.245,.105,.205]],[[0,2.19,.83],[.18,.065,.22]]],.065);
 muzzle.name='Astra · tapered nasal bridge, whisker pads and lower jaw';mesh(muzzle,(x,y,z)=>muzzleField(x,y,z)+.008*Math.exp(-((x/.017)**2+((y-2.20)/.055)**2+((z-1.03)/.13)**2)),[[-.32,2.10,.40],[.32,2.53,1.16]],.016,'muzzle');
 const bib=parts.find(p=>p.name==='Fox · proud breast'),bibField=combine([[[0,1.93,.43],[.32,.30,.31]],[[0,1.63,.49],[.31,.34,.28]],[[0,1.30,.45],[.16,.19,.19]]],.12);
 bib.name='Astra · tapered throat and flowing ivory chest ruff';mesh(bib,(x,y,z)=>Math.max(bibField(x,y,z),ell(x,y,z,[0,1.73,.34],[.4,.56,.41]))-.003*Math.sin(x*31+z*7)*Math.sin(y*23),[[-.43,1.04,.06],[.43,2.28,.88]],.025,'bib');
 // Each limb is one continuous anatomical surface, including all four toes.
 const removed=new Set(parts.filter(p=>/^Astra · sculpted (foreleg|hock)|^(Paw|Toe|Claw) ·/.test(p.name)).map(p=>p.id));
 const additions=[];
 for(const side of [-1,1])for(const front of [false,true]){
  const label=(front?'Fore':'Hind')+(side<0?' left':' right'),x=side*(front?.35:.41),z=front?.65:-.57;
  const points=front?[[side*.29,1.72,.27],[side*.33,1.13,.40],[side*.36,.37,.53],[x,.18,.63]]:[[side*.34,1.18,-.61],[side*.48,.75,-.43],[side*.43,.41,-.79],[x,.18,-.62]];
  const radii=front?[.18,.115,.065,.085]:[.19,.145,.065,.09],masses=[[[x,.125,z],[.165,.115,.21]]];for(const toe of [-1.5,-.5,.5,1.5])masses.push([[x+toe*.073,.095,z+.15-(Math.abs(toe)-.5)*.025],[.052,.074,.105]]);
  const paw=combine(masses,.035),field=(px,py,pz)=>{let d=paw(px,py,pz);for(let i=0;i<3;i++)d=smooth(d,capsule(px,py,pz,points[i],points[i+1],radii[i],radii[i+1]),.055);return d;};
  const p={id:'astra-living-'+(front?'fore':'hind')+'-'+side,name:'Astra · '+label+' elbow/hock, tendon and four-toed paw',color:'#ffffff',material:'silk',group:'Custom',textureBinding:{set:'astra-4k',tile:'fur',normalStrength:.36}};
  mesh(p,field,[[x-.34,.005,front?.03:-1.04],[x+.34,front?1.95:1.42,front?1.02:-.18]],front?.022:.023,'limb');additions.push(p);
  for(const toe of [-1.5,-.5,.5,1.5]){const cx=x+toe*.073,cz=z+.225-(Math.abs(toe)-.5)*.025,claw={id:p.id+'-claw-'+toe,name:label+' · curved claw '+toe,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color:'#b4a17c',material:'gloss',group:'Custom',organicSurface:{species:'courier',region:'claw'}};claw.topologyMesh=atelierLivingSweep({path:[[cx,.105,cz],[cx,.078,cz+.052],[cx,.046,cz+.075]],radii:[.018,.012,.001]},.72);additions.push(claw);}
 }
 const gearIds=new Set(model.meshGroups.find(g=>g.name==='Couriers travelling gear').members),tailIds=new Set(model.meshGroups.find(g=>g.name==='Comet tail and stardust').members);
 for(const part of parts){
  if(gearIds.has(part.id)||tailIds.has(part.id)||removed.has(part.id)||part.kind==='topologyMesh')continue;
  if(part.kind==='loft'){
   const ear=part.name.startsWith('Ear ·'),inner=part.name.includes('velvet');
   if(ear){part.path=part.path.map(p=>[p[0],p[1]*.88,p[2]]);part.radii=part.radii.map((r,i)=>i===0?r*.96:r);}
   if(part.name.startsWith('Face · expressive brow')){part.textureBinding.tile='fur';part.radii=part.radii.map(r=>r*.78);}
   const data=atelierLivingSweep(part,ear?(inner?.22:.55):1,ear?.025:.055);part.kind='topologyMesh';part.topologyMesh=data;delete part.path;delete part.radii;delete part.meshDensity;delete part.hdFinish;part.organicSurface={species:'courier',region:ear?'ear':'ruff'};
  }else if(part.kind==='sphere'){
   const g=new THREE.SphereGeometry(1,48,32),a=g.attributes.position;
   for(let i=0;i<a.count;i++){let x=a.getX(i),y=a.getY(i),z=a.getZ(i);if(part.name.includes('dark almond')){y*=.74+.26*Math.abs(x);z*=.8;}if(part.name.startsWith('Nose ·'))x*=.79+.18*(y+1)/2;a.setXYZ(i,x,y,z);}
   part.kind='topologyMesh';part.topologyMesh=atelierLivingClose({positions:Array.from(a.array).map(v=>+v.toFixed(6)),uvs:Array.from(g.attributes.uv.array).map(v=>+v.toFixed(6)),indices:Array.from(g.index.array)});delete part.meshDensity;delete part.hdFinish;part.organicSurface={species:'courier',region:part.name.startsWith('Eye ·')?'eye':'nose'};g.dispose();
   if(part.name.includes('vertical pupil')){part.name=part.name.replace('vertical pupil','canine pupil');part.scale=[.027,.037,.01];}
   if(part.name.includes('amber iris'))part.scale=[.057,.073,.020];
  }
 }
 const nostrils=[];for(const side of [-1,1]){const p={id:'astra-living-nostril-'+side,name:'Astra · recessed nostril '+side,color:'#09151b',material:'gloss',group:'Custom'};mesh(p,(x,y,z)=>ell(x,y,z,[side*.052,2.326,1.145],[.024,.014,.012]),[[side*.052-.032,2.304,1.125],[side*.052+.032,2.348,1.165]],.005,'nose');nostrils.push(p);}
 model.parts=[...parts.filter(p=>!removed.has(p.id)),...additions,...nostrils];model.meshGroups.find(g=>g.name==='Face, ears and cheek ruff').members.push(...nostrils.map(p=>p.id));for(const group of model.meshGroups)group.members=group.members.filter(id=>!removed.has(id));
 for(const p of additions){const front=p.name.startsWith('Astra · Fore')||p.name.startsWith('Fore');model.meshGroups.find(g=>g.name===(front?'Forelegs and paws':'Haunches and hind paws')).members.push(p.id);}
 model.name='Astra · Living Comet Courier';model.editedAt='local';project.engine='§wyrl§ Engine · Maker v11.89';project.project.name=model.name;return project;
};
