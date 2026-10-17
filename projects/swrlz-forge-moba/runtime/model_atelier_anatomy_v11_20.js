// A closed head built from anatomical horizontal sections, independent of sphere positions.
// Rows: height, half-width, facial-mask depth, posterior skull depth in head space.
function atelierHeadSection(sections,y,k){
 let i=0;while(i<sections.length-2&&sections[i+1][0]<y)i++;
 const a=sections[i],b=sections[i+1],h=b[0]-a[0],t=THREE.MathUtils.clamp((y-a[0])/h,0,1),d=(b[k]-a[k])/h;
 const slope=j=>{if(j===0)return (sections[1][k]-sections[0][k])/(sections[1][0]-sections[0][0]);if(j===sections.length-1)return (sections[j][k]-sections[j-1][k])/(sections[j][0]-sections[j-1][0]);const l=(sections[j][k]-sections[j-1][k])/(sections[j][0]-sections[j-1][0]),r=(sections[j+1][k]-sections[j][k])/(sections[j+1][0]-sections[j][0]);return l*r<=0?0:2*l*r/(l+r);};
 const m0=slope(i),m1=slope(i+1);return (2*t*t*t-3*t*t+1)*a[k]+(t*t*t-2*t*t+t)*h*m0+(-2*t*t*t+3*t*t)*b[k]+(t*t*t-t*t)*h*m1;
}
function atelierAnatomicalHead(p){
 const f=p.headAnatomy,rows=p.meshDensity?.v||128,cols=p.meshDensity?.u||192,positions=[],colors=[],uv=[],indices=[],base=new THREE.Color(p.color),sections=f.sections;
 const bell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
 for(let i=0;i<=rows;i++){
  const v=i/rows,y=THREE.MathUtils.lerp(sections[0][0],sections.at(-1)[0],v),w=atelierHeadSection(sections,y,1),front=atelierHeadSection(sections,y,2),back=atelierHeadSection(sections,y,3);
  for(let j=0;j<=cols;j++){
   const a=j/cols*Math.PI*2,s=Math.sin(a),c=Math.cos(a),x=w*s*(1-((p.jawTaper??.32)-.32)*THREE.MathUtils.smoothstep(-y,.1,.81));let z;
   if(c>=0){
    // A flatter facial mask rolls onto the zygomatic/temporal side plane.
    const power=2+f.facePlane*1.6,side=Math.pow(Math.max(0,1-Math.pow(Math.abs(s),power)),1/power);
    const center=(front+back)/2;z=center+(front-center)*side;
    const mask=THREE.MathUtils.smoothstep(c,0,.55),socket=bell(x-.42,y-.035,.25,.12)+bell(x+.42,y-.035,.25,.12);
    const cheek=bell(x-.59,y+.13,.19,.14)+bell(x+.59,y+.13,.19,.14);
    const bridge=bell(x,y+.11,.095,.20),tip=bell(x,y+.28,.10,.072),ala=bell(x-.115,y+.30,.055,.05)+bell(x+.115,y+.30,.055,.05);
    z+=mask*(-.055*(.5+(p.faceSculpt?.socket??.045)/.09)*socket+.035*(.5+(p.faceSculpt?.cheek??.06)/.12)*cheek+f.noseProjection*(.5+.5*(p.portraitFinish?.noseDefinition??.65)/.65)*(.8+5*(p.faceSculpt?.nose??.04))*(.60*bridge+tip+.20*ala)+.020*bell(x,y+.43,.24,.09)-.014*bell(x,y+.61,.17,.055));
   }else z=(front+back)/2+(front-back)/2*c;
   const col=base.clone(),warm=p.portraitFinish?.warmth??.7;
   if(c>0){const blush=bell(x-.52,y+.14,.23,.17)+bell(x+.52,y+.14,.23,.17);col.lerp(new THREE.Color('#df8990'),warm*.15*blush*c);col.lerp(new THREE.Color('#c78e89'),.10*(bell(x-.08,y+.31,.025,.018)+bell(x+.08,y+.31,.025,.018)));}
   const chinY=y+((p.portraitFinish?.chinLift??.16)-.16)*THREE.MathUtils.smoothstep(-y,.2,.81);
   positions.push(x,chinY,z);colors.push(col.r,col.g,col.b);uv.push(j/cols,v);
   if(i<rows&&j<cols){const n=i*(cols+1)+j,b=n+cols+1;if(i!==0)indices.push(n,n+1,b);if(i!==rows-1)indices.push(n+1,b+1,b);}
  }
 }
 const g=atelierHDMesh(positions,colors,indices,uv),norm=g.attributes.normal;
 for(let i=0;i<=rows;i++){const a=i*(cols+1),b=a+cols,n=new THREE.Vector3().fromBufferAttribute(norm,a).add(new THREE.Vector3().fromBufferAttribute(norm,b)).normalize();if(n.lengthSq()<.1)n.set(0,i===0?-1:1,0);norm.setXYZ(a,n.x,n.y,n.z);norm.setXYZ(b,n.x,n.y,n.z);}
 return g;
}
function atelierHeadAnatomyValid(p){
 const f=p.headAnatomy;if(f===undefined)return true;
 if(p.kind!=='sphere'||p.surfaceStyle!=='portrait-head'||p.hdFinish?.style!=='portrait'||!f||typeof f!=='object'||Array.isArray(f)||Object.keys(f).length!==3||!Number.isFinite(f.facePlane)||f.facePlane<0||f.facePlane>1||!Number.isFinite(f.noseProjection)||f.noseProjection<0||f.noseProjection>.3||!Array.isArray(f.sections)||f.sections.length<7||f.sections.length>32)return false;
 return f.sections.every((s,i)=>Array.isArray(s)&&s.length===4&&s.every(Number.isFinite)&&s[0]>=-1.2&&s[0]<=1.2&&(i===0||s[0]-f.sections[i-1][0]>=.015)&&s[1]>=0&&s[1]<=1.5&&s[2]>=0&&s[2]<=1.5&&s[3]<=1.5&&s[3]>=-1.5&&s[2]>=s[3]&&(i!==0&&i!==f.sections.length-1||s[1]===0&&s[2]===s[3]));
}
function atelierHeadAnatomyRefresh(){
 const p=partById(selection),deck=$m('HeadAnatomy');const option=[...($m('Kind')?.options||[])].find(o=>o.value==='sphere');if(option){option.value='sphere';option.textContent=p?.headAnatomy?'Anatomical head':'Sphere';}deck.hidden=!(p?.surfaceStyle==='portrait-head'&&p.hdFinish?.style==='portrait');if(deck.hidden)return;
 $m('HeadSections').value=JSON.stringify(p.headAnatomy?.sections||[[-.81,0,.70,.70],[-.75,.20,.82,.56],[-.60,.44,.89,.05],[-.38,.66,.91,-.55],[-.12,.84,.91,-.74],[.08,.88,.91,-.88],[.30,.83,.94,-.97],[.55,.83,.88,-1.02],[.76,.72,.69,-.88],[.93,.40,.36,-.47],[1,0,0,0]]);
 $m('HeadPlane').value=p.headAnatomy?.facePlane??.65;$m('HeadNose').value=p.headAnatomy?.noseProjection??.13;
}
function atelierHeadAnatomyInstall(){
 $m('HeadAnatomyApply').addEventListener('click',()=>{const p=partById(selection);let sections;try{sections=JSON.parse($m('HeadSections').value);}catch{status('Head sections must be valid JSON.',true);return;}
 const next={...p,headAnatomy:{sections,facePlane:Number($m('HeadPlane').value),noseProjection:Number($m('HeadNose').value)}};
 if(!checkPart(next)){status('Head anatomy rejected: use ordered, bounded sections with closed poles.',true);return;}
 checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Anatomical head sections saved. Refit facial contours after reshaping.');});
}
