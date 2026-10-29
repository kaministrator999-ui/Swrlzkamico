// Editable native surfaces: fused cranium/pinna roots, muscle transitions and
// closed curved fur locks. All 37 original courier gear/tail parts stay exact.
const atelierFurredBase=atelierRefineCourierProject;
atelierRefineCourierProject=function(original=COMET_COURIER_PROJECT){
 const project=atelierFurredBase(original),model=project.project.modelAtelier;
 const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
 const ell=(x,y,z,c,r)=>{const dx=x-c[0],dy=y-c[1],dz=z-c[2],a=Math.hypot(dx/r[0],dy/r[1],dz/r[2]),b=Math.hypot(dx/r[0]**2,dy/r[1]**2,dz/r[2]**2);return b?a*(a-1)/b:-Math.min(...r);};
 const masses=(items,k)=>(x,y,z)=>items.reduce((d,[c,r])=>smooth(d,ell(x,y,z,c,r),k),10);
 const sculpt=(p,field,bounds,step)=>{p.topologyMesh=atelierLivingClose(atelierAnimalSurface(field,bounds,step));};
 const body=model.parts.find(p=>p.id==='model-seed');body.name='Astra · flowing shoulder muscles, ribcage and tucked waist';
 const torso=masses([[[0,1.40,-.18],[.425,.53,.69]],[[0,1.78,.25],[.33,.39,.32]],[[0,2.04,.31],[.28,.31,.27]],[[-.29,1.53,.24],[.21,.35,.275]],[[.29,1.53,.24],[.21,.35,.275]],[[-.34,1.00,-.59],[.29,.39,.31]],[[.34,1.00,-.59],[.29,.39,.31]]],.16);
 sculpt(body,(x,y,z)=>torso(x,y,z)+.04*Math.exp(-(((z+.02)/.31)**2+((y-1.03)/.20)**2)),[[-.74,.49,-1.04],[.74,2.43,.80]],.029);
 const skull=model.parts.find(p=>p.organicSurface?.region==='face');skull.name='Astra · continuous skull and rooted cupped ears';
 const head=masses([[[0,2.43,.43],[.415,.35,.355]],[[-.26,2.32,.56],[.18,.20,.22]],[[.26,2.32,.56],[.18,.20,.22]],[[0,2.22,.57],[.27,.13,.26]]],.085);
 const ear=(x,y,z,side)=>{const t=THREE.MathUtils.clamp((y-2.53)/.70,0,1),cx=side*(.27+.18*t),cz=.36-.09*t,w=.175*(1-t)**.65+.006,d=.079*(1-t)**.55+.006;return Math.max((Math.hypot((x-cx)/w,(z-cz)/d)-1)*Math.min(w,d),2.50-y,y-3.23);};
 sculpt(skull,(x,y,z)=>{let d=head(x,y,z);for(const s of [-1,1]){d=smooth(d,ear(x,y,z,s),.06);d=Math.max(d,-ell(x,y,z,[s*.245,2.48,.818],[.145,.094,.077]));}return d;},[[-.63,2.04,.01],[.63,3.27,.92]],.019);
 const removed=new Set(model.parts.filter(p=>p.name.startsWith('Ear · outer')).map(p=>p.id));model.parts=model.parts.filter(p=>!removed.has(p.id));for(const g of model.meshGroups)g.members=g.members.filter(id=>!removed.has(id));
 // Thin front liners follow the pinnae instead of hanging independently.
 for(const p of model.parts.filter(p=>p.name.startsWith('Ear · velvet'))){const side=p.position[0]<0?-1:1;p.position=[0,0,0];p.scale=[1,1,1];p.topologyMesh=atelierLivingSweep({path:[[side*.29,2.67,.421],[side*.36,2.90,.391],[side*.435,3.15,.299]],radii:[.102,.072,.001]},.12);p.name='Ear · inset velvet '+side;}
 // Surface-area sampling gives an even coat; each lock is a watertight curved
 // teardrop, sunk into its parent pelt. No cards, imported mesh or sphere tufts.
 let seed=1190;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;},fur=[];
 for(const source of model.parts.filter(p=>p.id==='model-seed'||p.organicSurface?.region==='bib'||/^astra-living-(fore|hind)-/.test(p.id)&&!p.id.includes('claw'))){
  const data=source.topologyMesh,g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(data.positions,3));g.setIndex(data.indices);g.computeVertexNormals();const normals=g.attributes.normal,areas=[],tri=[];let area=0;const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
  for(let i=0;i<data.indices.length;i+=3){a.fromArray(data.positions,data.indices[i]*3);b.fromArray(data.positions,data.indices[i+1]*3);c.fromArray(data.positions,data.indices[i+2]*3);const ar=b.clone().sub(a).cross(c.clone().sub(a)).length()/2;area+=ar;areas.push(area);tri.push(i);}
  const count=source===body?580:source.organicSurface.region==='bib'?220:75,positions=[],uvs=[],indices=[];let locks=0;
  for(let attempt=0;attempt<count*8&&locks<count;attempt++){const r=random()*area;let low=0,high=areas.length-1;while(low<high){const mid=(low+high)>>1;if(areas[mid]<r)low=mid+1;else high=mid;}const i=tri[low],ids=data.indices.slice(i,i+3),u=Math.sqrt(random()),v=random(),weights=[1-u,u*(1-v),u*v],p=new THREE.Vector3(),n=new THREE.Vector3();for(let k=0;k<3;k++){p.addScaledVector(new THREE.Vector3().fromArray(data.positions,ids[k]*3),weights[k]);n.addScaledVector(new THREE.Vector3().fromBufferAttribute(normals,ids[k]),weights[k]);}n.normalize();
   if(p.y<.29)continue;if(source===body&&p.z>.34&&p.y>1.12)continue;
   // Leave harness, cape and compass readable; ivory bib keeps its own coat.
   if(source===body&&Math.abs(p.x)>.28&&p.y>1.02&&p.y<1.94&&p.z<.25&&p.z>-.68)continue;
   if(source.organicSurface.region==='bib'&&(p.y>1.82||p.y>1.38&&Math.abs(p.x)<.27))continue;
   const flow=new THREE.Vector3(0,-1,-.45).addScaledVector(n,n.y+.45*n.z).normalize();if(flow.lengthSq()<.1)flow.set(0,0,-1);const right=new THREE.Vector3().crossVectors(flow,n).normalize(),length=(source===body?.09:.065)*( .7+random()*.8),width=length*(.20+random()*.12),base=positions.length/3,rows=5,cols=6;
   for(let row=0;row<=rows;row++){const t=row/rows,center=p.clone().addScaledVector(n,-.009+.024*Math.sin(Math.PI*t)).addScaledVector(flow,length*t),radius=width*Math.sin((t*.92+.08)*Math.PI/2)*(1-t)+.0007;for(let j=0;j<cols;j++){const angle=j/cols*Math.PI*2,q=center.clone().addScaledVector(right,Math.cos(angle)*radius).addScaledVector(n,Math.sin(angle)*radius*.32);positions.push(...q.toArray().map(v=>+v.toFixed(6)));uvs.push(+(j/cols).toFixed(6),+t.toFixed(6));if(row<rows){const q=base+row*cols+j,next=base+row*cols+(j+1)%cols;indices.push(q,next,q+cols,next,next+cols,q+cols);}}}
   for(const row of [0,rows]){const center=positions.length/3;const start=base+row*cols;const q=new THREE.Vector3();for(let j=0;j<cols;j++)q.add(new THREE.Vector3().fromArray(positions,(start+j)*3));q.multiplyScalar(1/cols);positions.push(...q.toArray().map(v=>+v.toFixed(6)));uvs.push(.5,row/rows);for(let j=0;j<cols;j++)indices.push(...(row?[center,start+j,start+(j+1)%cols]:[center,start+(j+1)%cols,start+j]));}locks++;
  }
  for(let i=0;i<indices.length;i+=3){const b=indices[i+1];indices[i+1]=indices[i+2];indices[i+2]=b;}
  const part={id:'astra-fur-'+source.id,name:'Astra · layered 3D '+(source.organicSurface.region==='bib'?'ivory chest ruff':source===body?'body coat':source.name.replace('Astra · ','')),kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color:'#ffffff',material:'silk',group:'Custom',textureBinding:structuredClone(source.textureBinding),organicSurface:{species:'courier',region:'fur3d'},topologyMesh:{positions,uvs,indices}};fur.push(part);g.dispose();
 }
 model.parts.push(...fur);model.meshGroups.push({id:'astra-fur-coat',name:'Layered 3D fur coat',members:fur.map(p=>p.id)});model.name='Astra · Furred Comet Courier';project.project.name=model.name;project.engine='§wyrl§ Engine · Maker v11.90';return project;
};
