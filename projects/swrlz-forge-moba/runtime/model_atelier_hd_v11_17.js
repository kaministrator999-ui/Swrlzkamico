// Native HD finishes: deterministic geometric surfaces, saved parameters and physical materials.
const atelierHDStyles={portrait:['sphere'],eye:['sphere'],iris:['sphere'],ear:['sphere'],wrap:['sphere'],hair:['loft'],skin:['sphere','loft'],lip:['loft'],cloth:['loft'],sock:['loft'],leather:['sphere'],bow:['sphere'],paper:['loft'],leaf:['loft']};
const atelierHDSampling={portrait:[192,128],iris:[192,64],hair:[128,64],cloth:[96,40],paper:[64,32],sock:[96,64],lip:[64,24],eye:[96,64],ear:[64,48],wrap:[128,96],leather:[96,64],bow:[64,48],skin:[64,32],leaf:[24,8]};
let atelierHDDirty=true,atelierHDEnabled=false;
const atelierHDMaterials=new Map();
// Advance HD motion in seconds even when a dense frame takes longer than 80 ms.
function atelierHDFrameDelta(now,last){const elapsed=Math.max(0,(now-last)/1000);return atelierHDEnabled?elapsed:Math.min(.08,elapsed);}
function atelierHDRestoreSampling(){for(const p of model()?.parts||[]){if(['paper-plume','paper-leaf','fabric-panel'].includes(p.surfaceStyle))continue;const s=atelierHDSampling[p.hdFinish?.style];if(s)p.meshDensity={u:s[0],v:s[1]};else if(p.group==='Character'){const d=atelierDensityPreset(p,true);if(d)p.meshDensity=d;}}}
function atelierHDColorGeometry(g,colors){g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.computeVertexNormals();g.computeBoundingSphere();return g;}
function atelierHDMesh(positions,colors,indices,uv){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));if(indices)g.setIndex(indices);if(uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));return atelierHDColorGeometry(g,colors);}
function atelierHDRadius(p,t){const f=t*(p.radii.length-1),i=Math.min(p.radii.length-2,Math.floor(f)),u=f-i;
 const a=p.radii[Math.max(0,i-1)],b=p.radii[i],c=p.radii[i+1],d=p.radii[Math.min(p.radii.length-1,i+2)];
 return Math.max(.0004,.5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u));}
function atelierHDFrames(curve,n){const frames=[],front=new THREE.Vector3(0,0,1);let previous=curve.getTangent(0).normalize(),right=front.clone().cross(previous);if(right.lengthSq()<.001)right.set(1,0,0);right.normalize();
 for(let i=0;i<=n;i++){const tangent=curve.getTangent(i/n).normalize();if(i)right.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(previous,tangent));right.addScaledVector(tangent,-right.dot(tangent)).normalize();frames.push({tangent,right:right.clone(),depth:new THREE.Vector3().crossVectors(tangent,right).normalize()});previous=tangent;}return frames;}
function atelierHDSweep(p){
 const style=p.hdFinish.style,strength=p.hdFinish.relief,curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal');
 const n=p.meshDensity?.u||64,rings=p.meshDensity?.v||32,frames=atelierHDFrames(curve,n),positions=[],colors=[],indices=[],uv=[],base=new THREE.Color(p.color);
 for(let i=0;i<=n;i++){const t=i/n,center=curve.getPoint(t),f=frames[i],radius=atelierHDRadius(p,t);
  for(let j=0;j<=rings;j++){const a=j/rings*Math.PI*2,s=Math.sin(a),c=Math.cos(a);let r=radius,depth=1,shade=1;
   if(style==='hair'){depth=.30;const groove=Math.cos(a*20+.25*Math.sin(t*8));r*=1+.018*strength*groove;shade=.82+.20*Math.pow(Math.max(0,s),3)+.015*groove+.07*t;}
   if(style==='skin'){r*=1+.025*strength*Math.cos(a*2)*Math.sin(t*Math.PI);shade=.97+.035*Math.sin(a);}
   if(style==='lip'){depth=1.6;r*=.92+.08*Math.sin(t*Math.PI);shade=.90+.12*Math.max(0,s);}
   if(style==='sock'){const folds=Math.sin(t*Math.PI*7+.5*Math.sin(a*3))*.045*Math.sin(Math.PI*t);r*=1+strength*(folds+.009*Math.cos(a*24));shade=.96+.025*Math.cos(a*24)+folds*.7;}
   const v=center.clone().addScaledVector(f.right,c*r).addScaledVector(f.depth,s*r*depth);positions.push(v.x,v.y,v.z);uv.push(j/rings,t);
   const col=base.clone().multiplyScalar(shade);if(style==='hair')col.lerp(new THREE.Color('#17263d'),.12*(1-t));colors.push(col.r,col.g,col.b);
   if(i<n&&j<rings){const k=i*(rings+1)+j,b=k+rings+1;indices.push(k,k+1,b,b,k+1,b+1);}
  }
 }
 // Smooth the duplicated seam normals without welding the UV seam.
 const g=atelierHDMesh(positions,colors,indices,uv),norm=g.attributes.normal;
 for(let i=0;i<=n;i++){const a=i*(rings+1),b=a+rings,v=new THREE.Vector3().fromBufferAttribute(norm,a).add(new THREE.Vector3().fromBufferAttribute(norm,b)).normalize();norm.setXYZ(a,v.x,v.y,v.z);norm.setXYZ(b,v.x,v.y,v.z);}return g;
}
function atelierHDIris(p){
 const n=Math.max(64,p.meshDensity?.u||192),rows=Math.max(16,p.meshDensity?.v||48),positions=[],colors=[],indices=[],uv=[],strength=p.hdFinish.relief;
 const dark=new THREE.Color('#32243d'),amber=new THREE.Color('#f4b956'),rose=new THREE.Color('#ad4c6b');
 for(let i=0;i<=rows;i++){const r=i/rows;for(let j=0;j<=n;j++){const a=j/n*Math.PI*2,x=r*Math.cos(a),y=r*Math.sin(a),fiber=.5+.5*Math.sin(a*83+Math.sin(a*29)*2+r*10);
   positions.push(x,y,.30*(1-r*r)+.015*strength*Math.sin(a*83)*Math.sin(r*Math.PI));uv.push((x+1)/2,(y+1)/2);
   const c=r<.37?new THREE.Color('#17152a'):rose.clone().lerp(amber,THREE.MathUtils.smoothstep(-y,-.45,.55));
   if(r>=.37){c.multiplyScalar(.81+.19*fiber);c.lerp(dark,THREE.MathUtils.smoothstep(r,.82,1));c.lerp(amber,.22*Math.exp(-Math.pow((r-.42)/.07,2)));}
   colors.push(c.r,c.g,c.b);if(i<rows&&j<n){const k=i*(n+1)+j,b=k+n+1;indices.push(k,b,k+1,k+1,b,b+1);}
  }}return atelierHDMesh(positions,colors,indices,uv);
}
function atelierHDSphere(p){
 const style=p.hdFinish.style,strength=p.hdFinish.relief,g=style==='portrait'?atelierDetailSphere({...p,meshDensity:p.meshDensity||{u:192,v:128}}):new THREE.SphereGeometry(1,p.meshDensity?.u||64,p.meshDensity?.v||48),pos=g.attributes.position,colors=[],base=new THREE.Color(p.color);
 const bell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
 for(let i=0;i<pos.count;i++){let x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i),col=base.clone();
  if(p.surfaceStyle==='tapered-muzzle'){const t=(x+1)/2,k=1-.68*t*t;y*=k;z*=k;}
  if(style==='portrait'&&z>0){const front=THREE.MathUtils.smoothstep(z,.2,.7),rim=bell(x-.44,y-.29,.28,.065)+bell(x+.44,y-.29,.28,.065);
   z+=front*strength*(.025*rim-.023*(bell(x-.08,y+.29,.035,.035)+bell(x+.08,y+.29,.035,.035))+.018*bell(x,y+.58,.28,.14));
   const blush=(bell(x-.51,y+.19,.23,.16)+bell(x+.51,y+.19,.23,.16))*.20*front;
   col.lerp(new THREE.Color('#e68f93'),blush);col.lerp(new THREE.Color('#d99a96'),.11*rim*front);
  }
  if(style==='eye'){y*=Math.pow(Math.max(.001,1-Math.pow(Math.abs(x),1.45)),.26);y+=.075*x;col.lerp(new THREE.Color('#d7aeb1'),.28*Math.pow(Math.abs(x),4)+.09*Math.max(0,y));}
  if(style==='ear'&&z>0){const r=Math.hypot(x*.88,y);z-=strength*.36*Math.exp(-Math.pow((r-.35)/.30,2));z+=strength*.12*Math.exp(-Math.pow((r-.78)/.13,2));col.lerp(new THREE.Color('#ce8790'),.38*Math.exp(-Math.pow((r-.35)/.30,2)));}
  if(style==='leather'){if(y<-.45)y=-1+.55*Math.pow((y+1)/.55,2);const welt=Math.exp(-Math.pow((y+.43)/.035,2));x*=1+.04*strength*welt;z*=1+.04*strength*welt;col.multiplyScalar(.88+.13*Math.max(0,y));col.lerp(new THREE.Color('#1e6a75'),welt*.7);}
  if(style==='bow'){const pinch=.22+.78*Math.pow(Math.abs(x),.52);y*=pinch;z*=pinch*(1+.12*strength*Math.cos(x*16));col.multiplyScalar(.89+.10*Math.cos(x*16));}
  if(style==='wrap'){const a=Math.atan2(z,x),weave=Math.cos(a*32+y*36)*Math.cos(y*48-a*8),r=1+.012*strength*weave;x*=r;y*=r;z*=r;col.multiplyScalar(.91+.07*weave);}
  if(style==='skin'){col.multiplyScalar(.97+.035*y);}
  pos.setXYZ(i,x,y,z);colors.push(col.r,col.g,col.b);
 }return atelierHDColorGeometry(g,colors);
}
function atelierHDCloth(p){
 const n=p.meshDensity?.u||96,cols=p.meshDensity?.v||40,strength=p.hdFinish.relief,curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),positions=[],colors=[],indices=[],uv=[],base=new THREE.Color(p.color),gold=new THREE.Color('#e4c47b');
 for(let i=0;i<=n;i++){const t=i/n,q=curve.getPoint(t),w=atelierHDRadius(p,t),sgn=q.z<0?-1:1,tangent=curve.getTangent(t).normalize(),across=new THREE.Vector3(0,0,1).cross(tangent).normalize(),front=new THREE.Vector3().crossVectors(tangent,across).normalize();
  for(let j=0;j<=cols;j++){const u=j/cols*2-1,edge=Math.exp(-Math.pow((Math.abs(u)-.91)/.022,2)),stitch=Math.pow(.5+.5*Math.cos(t*Math.PI*72),8)*edge;
   const scroll=Math.exp(-Math.pow((Math.abs(u)-(.68+.10*Math.sin(t*28)))/.025,2))*Math.sin(Math.PI*t),weave=Math.sin(u*Math.PI*17.5)*Math.sin(t*Math.PI*54);
   const fold=(p.panelPleat??.008)*Math.cos(u*Math.PI*3)*Math.sin(t*Math.PI),relief=strength*(stitch*.003+scroll*.0018+weave*.0006),camber=(p.panelCamber??.035)*u*u;
   if(p.surfaceStyle==='fabric-panel'){const v=q.clone().addScaledVector(across,u*w).addScaledVector(front,sgn*(fold-camber+relief));positions.push(v.x,v.y,v.z);}
   else if(p.panelAxis==='depth')positions.push(q.x+Math.sign(q.x)*(fold-camber+relief),q.y,q.z+u*w);else positions.push(q.x+u*w,q.y,q.z+sgn*(fold-camber+relief));
   const c=base.clone().multiplyScalar(.95+.03*Math.cos(u*Math.PI*3)+.012*weave);c.lerp(gold,Math.min(.9,edge*.85+scroll*.46)*strength);colors.push(c.r,c.g,c.b);uv.push(j/cols,t);
   if(i<n&&j<cols){const k=i*(cols+1)+j,b=k+cols+1;indices.push(k,b,k+1,k+1,b,b+1);}
  }}return atelierHDMesh(positions,colors,indices,uv);
}
function atelierHDPaper(p){
 const curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),rings=40,facets=14,frames=atelierHDFrames(curve,rings),positions=[],colors=[],indices=[],uv=[],strength=p.hdFinish.relief;
 const hsl=new THREE.Color(p.color).getHSL({},THREE.SRGBColorSpace);
 const palette=[[0,-.03],[.025,.015],[-.012,-.095],[.045,.045],[-.008,-.015]].map(([dh,dl])=>new THREE.Color().setHSL((hsl.h+dh+1)%1,Math.min(.98,hsl.s+.03),THREE.MathUtils.clamp(hsl.l+dl,.15,.78),THREE.SRGBColorSpace));
 // A continuous core closes gaps beneath the independently creased overlapping paper leaves.
 for(let i=0;i<=rings;i++){const t=i/rings,q=curve.getPoint(t),f=frames[i],r=atelierHDRadius(p,t)*.96;for(let j=0;j<=facets;j++){const a=j/facets*Math.PI*2,v=q.clone().addScaledVector(f.right,Math.cos(a)*r).addScaledVector(f.depth,Math.sin(a)*r);positions.push(v.x,v.y,v.z);const c=new THREE.Color(palette[i%5]).multiplyScalar(.78);colors.push(c.r,c.g,c.b);uv.push(j/facets,t);if(i<rings&&j<facets){const k=i*(facets+1)+j,b=k+facets+1;indices.push(k,k+1,b,b,k+1,b+1);}}}
 const rows=6,cols=4;
 for(let i=0;i<rings;i++)for(let j=0;j<facets;j++){
  const t=(i+.2)/rings,center=curve.getPoint(t),f=frames[i],a=(j+(i%2)*.5)*Math.PI*2/facets,normal=f.right.clone().multiplyScalar(Math.cos(a)).addScaledVector(f.depth,Math.sin(a)),across=f.right.clone().multiplyScalar(-Math.sin(a)).addScaledVector(f.depth,Math.cos(a)),r=atelierHDRadius(p,t),width=r*.52,span=.16+.07*Math.sin(t*Math.PI),base=positions.length/3,col=new THREE.Color(palette[(i+j*3)%5]);
  for(let k=0;k<=rows;k++)for(let h=0;h<=cols;h++){const v=k/rows,u=h/cols*2-1,tear=k===rows?.013*Math.sin(j*7+i*3+h*4):0,crease=.018*(1-Math.abs(u))+.004*strength*Math.sin(u*20+v*9),bend=.028*Math.sin(v*Math.PI)+.040*v*v;
   const q=center.clone().addScaledVector(normal,r+.015+bend+crease).addScaledVector(across,u*width*.5*(1-.10*v)).addScaledVector(f.tangent,(v-.20)*span+tear);positions.push(q.x,q.y,q.z);const c=col.clone().multiplyScalar(.92+.06*u+.022*Math.sin(u*20+v*9));colors.push(c.r,c.g,c.b);uv.push(h/cols,v);
   if(k<rows&&h<cols){const n=base+k*(cols+1)+h,b=n+cols+1;indices.push(n,b,n+1,n+1,b,b+1);}
  }
  const edges=[];for(let h=0;h<cols;h++)edges.push([base+rows*(cols+1)+h,base+rows*(cols+1)+h+1]);for(let k=0;k<rows;k++){edges.push([base+k*(cols+1),base+(k+1)*(cols+1)]);edges.push([base+k*(cols+1)+cols,base+(k+1)*(cols+1)+cols]);}
  for(const [a,b]of edges){const start=positions.length/3,A=new THREE.Vector3().fromArray(positions,a*3),B=new THREE.Vector3().fromArray(positions,b*3),c=col.clone().multiplyScalar(.72);for(const q of [A,B,B.clone().addScaledVector(normal,-.0032),A.clone().addScaledVector(normal,-.0032)]){positions.push(q.x,q.y,q.z);colors.push(c.r,c.g,c.b);}uv.push(0,0,1,0,1,1,0,1);indices.push(start,start+1,start+2,start,start+2,start+3);}
 }
 return atelierHDMesh(positions,colors,indices,uv);
}
function atelierHDGeometry(p){
 if(!p.hdFinish)return null;const s=p.hdFinish.style;
 if(s==='iris')return atelierHDIris(p);if(p.kind==='sphere')return atelierHDSphere(p);
 if(s==='paper')return atelierHDPaper(p);if(s==='cloth')return atelierHDCloth(p);
 if(s==='leaf'){const g=atelierReferenceLeaf(p),a=g.attributes.position;for(let i=0;i<a.count;i++)a.setZ(i,a.getZ(i)+.006*p.hdFinish.relief*Math.sin(i*2.3));g.computeVertexNormals();return g;}
 return atelierHDSweep(p);
}
function material(part){
 if(!part.hdFinish)return atelierPreviousMaterial(part);const s=part.hdFinish.style;
 const key=s+'|'+part.color+'|'+part.material;if(atelierHDMaterials.has(key))return atelierHDMaterials.get(key);
 if(atelierHDMaterials.size>=256)for(const [k,m]of atelierHDMaterials){if(!modelRoot?.children.some(o=>o.material===m)){m.dispose();atelierHDMaterials.delete(k);break;}}
 const rough=s==='iris'?.16:s==='leather'?.24:s==='hair'?.38:s==='paper'||s==='leaf'?.84:.55;
 const m=part.material==='emissive'?new THREE.MeshBasicMaterial({color:'#ffffff',vertexColors:true,side:THREE.DoubleSide}):new THREE.MeshPhysicalMaterial({color:'#ffffff',vertexColors:true,side:THREE.DoubleSide,roughness:part.material==='gloss'?Math.min(.25,rough):part.material==='matte'?Math.max(.82,rough):part.material==='metal'?.28:rough,metalness:part.material==='metal'?.65:0,clearcoat:s==='iris'?.9:s==='leather'?.55:s==='hair'?.12:0,clearcoatRoughness:.2,anisotropy:s==='hair'?.55:0,anisotropyRotation:Math.PI/2,sheen:['hair','cloth','sock','bow'].includes(s)?.55:.08,sheenRoughness:.65,sheenColor:new THREE.Color(part.color)});
 m.userData.atelierHDMaterial=true;atelierHDMaterials.set(key,m);return m;
}
function atelierHDRefresh(){
 const p=partById(selection),deck=$m('HDEditor');if(!deck)return;
 const panelPick=$m('HDTrimPanel');if(panelPick){const old=panelPick.value;panelPick.replaceChildren();for(const q of model()?.parts||[])if(q.hdFinish?.style==='cloth'){const op=document.createElement('option');op.value=q.id;op.textContent=q.name;panelPick.append(op);}if([...panelPick.options].some(o=>o.value===old))panelPick.value=old;}deck.hidden=!p||!['sphere','loft'].includes(p.kind);
 if(p){$m('HDStyle').value=p.hdFinish?.style||'none';$m('HDRelief').value=String(p.hdFinish?.relief??.7);}
 const hd=!!model()?.parts.some(p=>p.hdFinish);atelierHDEnabled=hd;atelierHDDirty=true;if(renderer){renderer.toneMapping=hd?THREE.ACESFilmicToneMapping:THREE.NoToneMapping;renderer.toneMappingExposure=1.05;}
 for(const o of world?.children||[]){if(o.isHemisphereLight)o.intensity=hd?1.1:2.1;if(o.isDirectionalLight&&o.position.x===-7)o.intensity=hd?1.7:2.3;if(o.isDirectionalLight&&o.position.x===-1)o.intensity=hd?1.2:1.45;}
}
// Fit an editable spline to sampled cloth vertices in the same component's rest space.
function atelierHDFitTrim(part,panel,u,start,radius){
 if(!part||part.kind!=='loft'||!panel||panel.hdFinish?.style!=='cloth'||part.id===panel.id||part.group!==panel.group||![u,start,radius].every(Number.isFinite)||Math.abs(u)>1||start<0||start>.4||radius<.0005||radius>.02)return null;
 const g=atelierHDCloth(panel),pos=g.attributes.position,norm=g.attributes.normal,n=panel.meshDensity?.u||96,cols=panel.meshDensity?.v||40,column=Math.round((u+1)*cols/2),first=Math.round(start*n),segments=Math.min(32,n-first);
 const matrix=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale)),relative=matrix(part).invert().multiply(matrix(panel)),normalMatrix=new THREE.Matrix3().getNormalMatrix(relative),path=[];
 for(let i=0;i<=segments;i++){const row=first+Math.round((n-first)*i/segments),at=row*(cols+1)+column,q=new THREE.Vector3().fromBufferAttribute(pos,at),out=panel.panelAxis==='depth'?new THREE.Vector3(Math.sign(q.x)||1,0,0):new THREE.Vector3(0,0,Math.sign(q.z)||1),normal=new THREE.Vector3().fromBufferAttribute(norm,at);if(normal.dot(out)<0)normal.negate();q.applyMatrix4(relative);normal.applyMatrix3(normalMatrix).normalize();q.addScaledVector(normal,radius*.45);path.push(q.toArray());}
 g.dispose();return {...part,path,radii:path.map(()=>radius)};
}
function atelierHDInstall(){
 const apply=matching=>{const p=partById(selection);if(!p)return;if(matching&&p.kind!=='loft'){status('Matching-surface application is available for spline meshes.');return;}
  const style=$m('HDStyle').value,relief=Number($m('HDRelief').value),sampling=atelierHDSampling[style];
  const parts=matching?model().parts.filter(q=>q.kind===p.kind&&q.surfaceStyle===p.surfaceStyle&&q.group===p.group):[p];
  const changes=parts.map(q=>{const n={...q,hdFinish:style==='none'?undefined:{style,relief}};if(sampling&&$m('HDSampling').checked&&!['paper-plume','paper-leaf','fabric-panel'].includes(q.surfaceStyle))n.meshDensity={u:sampling[0],v:sampling[1]};return n;});
  if(changes.some(q=>!checkPart(q))){status('Surface finish rejected: select a compatible mesh and relief from 0 to 1.',true);return;}
  checkpoint();parts.forEach((q,i)=>Object.assign(q,changes[i]));signalEdited();select(p.id);status('HD surface applied to '+parts.length+' editable meshes.');
 };
 $m('HDFitTrim').addEventListener('click',()=>{const p=partById(selection),next=atelierHDFitTrim(p,partById($m('HDTrimPanel').value),Number($m('HDTrimU').value),Number($m('HDTrimStart').value),Number($m('HDTrimRadius').value));if(!next||!checkPart(next)){status('Trim fit rejected: choose a separate cloth panel in the same group and valid edge, start and radius values.',true);return;}checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Trim fitted to the actual cloth surface. The saved spline remains independently editable.');});
 $m('HDApply').addEventListener('click',()=>apply(false));$m('HDMatch').addEventListener('click',()=>apply(true));
 $m('RenderPNG').addEventListener('click',()=>{if(!renderer||!camera)return;const size=renderer.getSize(new THREE.Vector2()),ratio=renderer.getPixelRatio(),scale=2048/Math.max(size.x,size.y),helpers=[];
  world.traverse(o=>{if(o.userData?.atelierHelper||o.type==='GridHelper'){helpers.push([o,o.visible]);o.visible=false;}});
  renderer.setPixelRatio(1);renderer.setSize(Math.round(size.x*scale),Math.round(size.y*scale),false);renderer.render(world,camera);
  renderer.domElement.toBlob(blob=>{helpers.forEach(([o,v])=>o.visible=v);renderer?.setPixelRatio(ratio);renderer?.setSize(size.x,size.y,false);atelierHDDirty=true;if(!blob)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='character-studio-2048.png';a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);status('Studio render exported at 2048 pixels.');},'image/png');
 });
}
