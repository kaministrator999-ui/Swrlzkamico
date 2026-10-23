// Reference-directed portrait finishing, applied after the preserved v11.91 sculpt.
// The welded skin keeps its original indices; all facial additions remain editable.
function atelierFestivalRefineFace(project){
 const m=project.project.modelAtelier,parts=m.parts,round=v=>+v.toFixed(6),blend=(v,a,b)=>THREE.MathUtils.smoothstep(v,a,b);
 const lift=y=>.045*Math.exp(-(((y-3.775)/.115)**2))+.013*Math.exp(-(((y-3.747)/.027)**2));
 const body=parts.find(p=>p.id==='girl-organic-body');
 for(let i=0;i<body.topologyMesh.positions.length;i+=3){
  const a=body.topologyMesh.positions,x=a[i],y=a[i+1],z=a[i+2];if(y<3.58||y>4.20)continue;
  const front=Math.max(blend(z,.08,.19),blend(Math.abs(x),.085,.145)*blend(y,3.75,3.88)),cheek=Math.exp(-(((y-3.985)/.065)**2)),jaw=Math.exp(-(((y-3.87)/.055)**2)),chin=Math.exp(-(((y-3.79)/.045)**2));
  a[i]=round(x*(1+front*(.038*cheek+.065*jaw+.60*chin)));
  a[i+1]=round(y+front*lift(y));
  a[i+2]=round(z+front*(.009*cheek*Math.exp(-(((Math.abs(x)-.17)/.085)**2))+.004*chin));
 }
 for(const p of parts.filter(p=>p.organicSurface?.region==='lip'))for(let i=1;i<p.topologyMesh.positions.length;i+=3)p.topologyMesh.positions[i]=round(p.topologyMesh.positions[i]+lift(p.topologyMesh.positions[i]));
 const surface=(x,y)=>{let originalY=y;for(let j=0;j<5;j++)originalY=y-lift(originalY);return atelierAnimeFaceZ(x,originalY)+.009*Math.exp(-(((y-3.985)/.065)**2+((Math.abs(x)-.17)/.085)**2));};
 const mesh=(id,name,data,color,region)=>({id,name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material:region==='eye'?'gloss':'silk',group:'Character',organicSurface:{species:'anime',region},topologyMesh:data});
 const replace=(id,name,data,color,region)=>{let p=parts.find(p=>p.id===id);const next=mesh(id,name,data,color,region);if(p)Object.assign(p,next);else{p=next;parts.push(p);}return p;};
 const eyePoint=(s,x,y,depth=0)=>{const angle=s*Math.PI*8/180,c=Math.cos(angle),sn=Math.sin(angle),X=s*.12+c*x-sn*y,Y=4.071+sn*x+c*y;return [X,Y,surface(X,Y)+depth];};
 const dome=s=>{const positions=[],uvs=[],indices=[],cols=80,rows=40;
  for(let i=0;i<=rows;i++){const phi=i/rows*Math.PI,r=Math.sin(phi);for(let j=0;j<=cols;j++){const theta=j/cols*Math.PI*2,v=Math.sin(theta),x=Math.cos(theta)*r*.096,y=v*r*(v>0?.054:.045)*Math.pow(Math.abs(v),.38),p=eyePoint(s,x,y,.002+Math.cos(phi)*.016);positions.push(...p.map(round));uvs.push(j/cols,i/rows);if(i<rows&&j<cols){const a=i*(cols+1)+j,b=a+cols+1;indices.push(a,b,a+1,a+1,b,b+1);}}}
  return atelierAnimalWeld({positions,uvs,indices});};
 for(const s of [-1,1]){
  const label=s<0?'left':'right';replace(label+'-sclera',label+' eye · almond white with softly raised outer corner',dome(s),'#fff6eb','eye');
  // Existing radial iris UVs and layered catchlights are retained and fitted to
  // the wider almond aperture; they do not turn into flat painted eye decals.
  for(const p of parts.filter(p=>p.id===label+'-iris'||p.id.startsWith(label+'-eye-catch')||p.id==='girl-pupil-'+label)){
   for(let i=0;i<p.topologyMesh.positions.length;i+=3){const a=p.topologyMesh.positions,x=a[i],y=a[i+1],z=a[i+2],dx=x-s*.12,dy=y-4.067;a[i]=round(s*.12+dx*1.07);a[i+1]=round(4.071+dy*1.06);a[i+2]=round(z+surface(a[i],a[i+1])-atelierAnimeFaceZ(x,y)+.0015);}
   if(p.id.endsWith('-iris'))p.name=label+' eye · warm amber radial iris';
  }
  const eyePath=(coordinates,depth)=>coordinates.map(([x,y])=>eyePoint(s,s*x,y,depth));
  const upper=eyePath([[-.094,-.003],[-.062,.043],[-.015,.059],[.044,.044],[.095,.006],[.113,.021]],.008);
  const lower=eyePath([[-.094,-.003],[-.052,-.034],[.005,-.046],[.063,-.028],[.095,.006]],.0055);
  replace(label+'-upper-lid',label+' eye · tapered swept upper liner',atelierAnimeStrand(upper,[.0007,.0032,.0042,.0046,.0023,.00015],72,12,.63),'#30212c','lid');
  replace(label+'-lower-lid',label+' eye · delicate rose lower waterline',atelierAnimeStrand(lower,[.0003,.0014,.0018,.0011,.0002],64,10,.65),'#b98489','lid');
  const browPath=eyePath([[-.075,.102],[-.036,.120],[.012,.126],[.057,.115],[.089,.098]],.009);
  replace(label+'-brow',label+' brow · slim lifted arch with tapered outer end',atelierAnimeStrand(browPath,[.0013,.0040,.0044,.0026,.0002],64,12,.42),'#503337','brow');
  for(let l=0;l<3;l++){
   const x=.066+l*.012,y=.035-l*.006,path=eyePath([[x,y],[x+.013,y+.009],[x+.027,y+.018-l*.003]],.009);
   replace(label+'-lash-'+l,label+' eye · fine outer lash '+(l+1),atelierAnimeStrand(path,[.0018,.00125,.0001],22,7,.5),'#30212c','lid');
  }
 }
 // Replace the old parallel fringe strips and highlights with individually
 // tapered, asymmetric broad locks. Buns and companion-held braid roots remain.
 const remove=new Set(parts.filter(p=>/^hair-(front|back|nape)-/.test(p.id)||p.id.startsWith('girl-fiber-')||p.id.startsWith('hair-grip-')).map(p=>p.id));
 m.parts=parts.filter(p=>!remove.has(p.id));
 const addLock=(id,name,path,radii,color,flatten=.32,highlight=true)=>{
  const p=mesh(id,name,atelierAnimeStrand(path,radii,64,16,flatten),color,'hair');m.parts.push(p);
  if(highlight){const h=path.map((a,i)=>[a[0],a[1]+.001,a[2]+Math.max(.001,radii[Math.min(i,radii.length-1)]*flatten*.9)]),c='#'+new THREE.Color(color).lerp(new THREE.Color('#fff0dd'),.20).getHexString();m.parts.push(mesh(id+'-silk',name+' · tapered silk ridge',atelierAnimeStrand(h,[.0003,.0014,.0016,.0001],48,7,.45),c,'hair'));}
 };
 const cyan=['#1aaaba','#22b9c9','#27bfd0','#35c6d2','#168d9f','#24b0bf'],coral=['#e9584c','#f56b58','#ee5b4c','#ff7c63','#d94a42','#f16b54'];
 // A dyed knot stays at each original assembly socket. The exaggerated dark
 // ring/grip silhouette is replaced by broad upward locks, not a new owner.
 for(const s of [-1,1]){
  const bun=m.parts.find(p=>p.id==='hair-bun-'+s);
  bun.color=s<0?'#1ba9bd':'#e95b4c';delete bun.textureBinding;
  const palette=s<0?cyan:coral;
  for(let j=0;j<3;j++){
   const f=j/2,path=s<0?
    [[-.035-j*.011,4.448-.009*j,.13],[-.119-j*.015,4.386,.285+j*.025],[-.176-j*.017,4.298,.339+j*.025],[-.076-j*.036,4.224-j*.012,.347+j*.022],[.073-j*.078,4.205-j*.008,.319]]:
    [[-.030+j*.012,4.459-.009*j,.15],[.076+j*.026,4.410-.008*j,.296+j*.024],[.198+j*.025,4.321-.012*j,.366+j*.025],[.288+j*.011,4.226-.022*j,.320+j*.022],[.264+j*.019,4.181-.027*j,.259]];
   addLock('girl-reference-fringe-'+s+'-'+j,(s<0?'Cyan under-sweep':'Coral overlapping sweep')+' · broad sculpted bang '+(j+1),path,[.010,.075-j*.009,.084-j*.009,.047-j*.006,.0003],palette[j],.23,true);
  }
  // Short graded rear layers stay behind the cheeks; the front has one long,
  // delicate face-framing lock on each side rather than two thick curtains.
  for(let j=0;j<4;j++){
   const f=j/3,x=s*(.11+.15*f),path=[[s*.07,4.36,-.12],[x,4.25,-.19],[s*(.21+.045*f),4.06,-.10],[s*(.23+.045*f),3.94+.035*f,.015],[s*(.18+.055*f),3.91+.035*f,.07]];
   addLock('girl-reference-nape-'+s+'-'+j,(s<0?'Cyan':'Coral')+' bob · graded rear lock '+(j+1),path,[.012,.045,.038,.025,.0003],palette[(j+2)%palette.length],.42,j%2===0);
  }
  // Five pointed, flattened leaves fan upward from a shared tied root. Their
  // closed cross-sections provide real silhouette and volume from every view.
  for(let j=0;j<5;j++){
   const f=j/4,path=[[s*.335,4.298,-.11+j*.035],[s*(.405+.025*f),4.435,-.10+j*.04],[s*(.505+.12*f),4.61-.020*j,-.12+j*.055],[s*(.55+.19*f),4.78-.055*j,-.06+j*.055],[s*(.45+.36*f),4.91-.10*j,.015+j*.045]];
   addLock('girl-reference-ponytail-'+s+'-'+j,(s<0?'Cyan':'Coral')+' ponytail · upward pointed silk tuft '+(j+1),path,[.025,.075,.13-.012*f,.078-.008*f,.0003],palette[(j+1)%palette.length],.38,true);
  }
 }
 addLock('girl-reference-cyan-tendril','Cyan hair · long thin curled cheek-framing tendril',[[-.19,4.30,.265],[-.255,4.18,.276],[-.269,4.035,.264],[-.272,3.89,.242],[-.233,3.807,.255],[-.165,3.792,.281]],[.012,.018,.015,.011,.007,.0002],'#23b9cd',.34);
 addLock('girl-reference-coral-temple','Coral hair · slim long temple lock',[[.235,4.31,.264],[.266,4.17,.265],[.272,4.025,.227],[.273,3.88,.19],[.235,3.758,.192],[.202,3.73,.23]],[.012,.020,.016,.011,.006,.0002],'#ee6454',.33);
 // Keep group membership valid when former fringe IDs were replaced.
 for(const g of m.meshGroups||[])g.members=g.members.filter(id=>m.parts.some(p=>p.id===id));
 m.meshGroups=(m.meshGroups||[]).filter(g=>g.members.length>1);
 const newHair=m.parts.filter(p=>p.id.startsWith('girl-reference-')).map(p=>p.id);for(let i=0;i<newHair.length;i+=28)m.meshGroups.push({id:'girl-reference-hair-group-'+i,name:'Reference hair layers '+(i/28+1),members:newHair.slice(i,i+28)});
 m.referenceProfile={...(m.referenceProfile||{}),version:'v11.92',face:{eyeShape:'upturned almond',eyeCantDegrees:8,brow:'slim raised arch',cheeks:'softly full',chin:'small rounded taper'},hair:{part:'asymmetric swept coral and cyan',silhouette:'layered short bob with upward tied ponytail tufts',cheekLock:'long curved cyan tendril'},source:'owner-provided festival character image'};
 return project;
}
