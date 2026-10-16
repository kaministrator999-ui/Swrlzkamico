// Explicit, saved sampling density. Unannotated historical parts keep their original topology.
let atelierTopologyView=false;
function atelierDetailSphere(part){
 const {u,v}=part.meshDensity,g=new THREE.SphereGeometry(1,u,v),a=g.attributes.position;
 const paint=part.surfaceStyle==='split-dye-cap'||!!part.faceSculpt,colors=[];
 const skin=new THREE.Color(part.color),accent=new THREE.Color(part.dyeAccent||'#f65f60');
 const bell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
 for(let i=0;i<a.count;i++){
  let x=a.getX(i),y=a.getY(i),z=a.getZ(i);
  if(part.surfaceStyle==='portrait-head'){
   x*=1-(part.jawTaper??.31)*THREE.MathUtils.smoothstep(-y,.12,1);
   z*=1-.08*THREE.MathUtils.smoothstep(-y,.20,.65);
   if(z>0){z+=.055*bell(x,y+.2,.52,.4);
    if(part.faceSculpt){const f=part.faceSculpt,front=THREE.MathUtils.smoothstep(z,.12,.65);
     const sockets=bell(x-.46,y-.12,.25,.18)+bell(x+.46,y-.12,.25,.18);
     const cheeks=bell(x-.48,y+.20,.24,.24)+bell(x+.48,y+.20,.24,.24);
     // Continuous bridge, nasal tip/alar planes, eye sockets and cheek transition.
     const bridge=f.nose*(bell(x,y+.10,.115,.28)+.62*bell(x,y+.30,.16,.105));
     const alar=f.nose*.18*(bell(x-.16,y+.31,.075,.075)+bell(x+.16,y+.31,.075,.075));
     const philtrum=-.012*bell(x,y+.42,.065,.08),mouth=.018*bell(x,y+.50,.32,.10);
     z+=front*(bridge+alar-f.socket*sockets+f.cheek*cheeks+philtrum+mouth);
    }
   }
  }else if(part.surfaceStyle==='tapered-muzzle'){
   const t=(x+1)*.5,taper=1-.68*t*t;y*=taper;z*=taper;
  }
  a.setXYZ(i,x,y,z);
  if(paint){const c=part.surfaceStyle==='split-dye-cap'?(x<0?skin:accent).clone():skin.clone();
   if(part.faceSculpt&&z>0){const blush=(bell(x-.54,y+.20,.24,.15)+bell(x+.54,y+.20,.24,.15))*.11;c.lerp(new THREE.Color('#e69b9e'),blush);}
   colors.push(c.r,c.g,c.b);
  }
 }
 if(paint)g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
 g.computeVertexNormals();g.computeBoundingSphere();return g;
}
function atelierDensityPreset(part,portrait=false){
 const id=part.id;
 if(['paper-plume','paper-leaf','fabric-panel'].includes(part.surfaceStyle))return null;
 if(part.kind==='sphere'){
  if(part.surfaceStyle==='portrait-head')return {u:portrait?96:64,v:portrait?64:48};
  if(/sclera|ear$|shoe-|hair-cap/.test(id))return {u:portrait?24:16,v:portrait?16:10};
  if(/iris|pupil/.test(id))return {u:portrait?20:12,v:portrait?12:8};
  return {u:portrait?16:8,v:portrait?12:6};
 }
 if(part.kind==='loft'){
  if(id==='model-0002'||id==='model-0003')return {u:portrait?36:20,v:portrait?20:12};
  if(id.includes('-leg'))return {u:portrait?48:28,v:portrait?24:14};
  if(id.startsWith('arm-'))return {u:portrait?36:20,v:portrait?20:12};
  if(id.startsWith('sock-'))return {u:portrait?24:12,v:portrait?16:10};
  if(part.surfaceStyle==='silken-lock')return {u:portrait?28:12,v:portrait?12:6};
  if(part.surfaceStyle==='hair-lock')return {u:portrait?20:8,v:portrait?10:4};
  if(part.surfaceStyle==='tailored-panel')return {u:portrait?28:12,v:portrait?8:4};
  if(/lid|brow|smile|lower-lip/.test(id))return {u:portrait?28:16,v:portrait?12:8};
  return {u:portrait?16:6,v:portrait?8:4};
 }
 return null;
}
function atelierDensityMeasured(){
 const byPart={};for(const mesh of modelRoot?.children||[]){const p=partById(mesh.userData?.atelierId);if(!mesh.isMesh||!p)continue;
  byPart[p.id]={triangles:Math.floor((mesh.geometry.index?.count??mesh.geometry.attributes.position.count)/3),group:p.group};}
 const stats=atelierGeometryStats();return {byPart,heroTriangles:stats.groups.Character?.triangles||0,totalTriangles:stats.triangles,topologyView:atelierTopologyView};
}
function atelierDensityRefresh(){
 const p=partById(selection),d=p?.meshDensity,deck=$m('DensityEditor');if(!deck)return;
 const supported=p&&(p.kind==='sphere'||p.kind==='loft')&&!['paper-plume','paper-leaf','fabric-panel'].includes(p.surfaceStyle);
 deck.hidden=!supported;
 if(supported){$m('DensityU').value=String(d?.u??(p.kind==='sphere'?16:p.segments||32));$m('DensityV').value=String(d?.v??(p.kind==='sphere'?12:p.radialSegments||8));
  $m('DensityLabelU').textContent=p.kind==='sphere'?'Around the surface':'Along the spline';$m('DensityLabelV').textContent=p.kind==='sphere'?'Vertical rings':'Around each section';}
 const face=p?.surfaceStyle==='portrait-head';$m('FaceContours').hidden=!face;
 if(face){$m('FaceNose').value=String(p.faceSculpt?.nose??.12);$m('FaceSocket').value=String(p.faceSculpt?.socket??.045);$m('FaceCheek').value=String(p.faceSculpt?.cheek??.04);}
 const measured=atelierDensityMeasured(),n=measured.byPart[selection]?.triangles;
 $m('DensityReadout').textContent='Heroine '+measured.heroTriangles.toLocaleString('en-US')+' tris · whole set '+measured.totalTriangles.toLocaleString('en-US')+' tris'+(n!==undefined?' · selected '+n.toLocaleString('en-US'):'');
 for(const mesh of modelRoot?.children||[])if(mesh.isMesh&&partById(mesh.userData?.atelierId)){mesh.material.wireframe=atelierTopologyView;}
}
function atelierDensityInstall(){
 $m('DensityApply').addEventListener('click',()=>{const p=partById(selection);if(!p)return;
  const next={...p,meshDensity:{u:Number($m('DensityU').value),v:Number($m('DensityV').value)}};
  if(p.surfaceStyle==='portrait-head')next.faceSculpt={nose:Number($m('FaceNose').value),socket:Number($m('FaceSocket').value),cheek:Number($m('FaceCheek').value)};
  if(!checkPart(next)){status('Mesh detail rejected: use whole-number samples (6–96, 4–64) and bounded facial contours.',true);return;}
  checkpoint();Object.assign(p,next);signalEdited();select(p.id);
 });
 $m('DensityPresetApply').addEventListener('click',()=>{if(!model())return;checkpoint();const high=$m('DensityPreset').value==='portrait';
  for(const p of model().parts){if(p.group!=='Character')continue;const d=atelierDensityPreset(p,high);if(d)p.meshDensity=d;
   if(p.surfaceStyle==='portrait-head')p.faceSculpt=p.faceSculpt||{nose:.12,socket:.045,cheek:.04};}
  signalEdited();status((high?'Close-up detail':'Mobile detail')+' applied to the heroine. Creature meshes retain their own detail.');
 });
 $m('TopologyView').addEventListener('change',()=>{atelierTopologyView=$m('TopologyView').checked;atelierDensityRefresh();});
}
