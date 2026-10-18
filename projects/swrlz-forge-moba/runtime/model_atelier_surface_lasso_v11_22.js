// §E Surface Lasso Slice D: non-destructive, surface-attached polygonal
// boundaries with separately editable PIN controls and regional deformation.
// This is NOT local topology refinement; no new triangles are created here.
const atelierLassoMaxRegions=8,atelierLassoMaxPins=32;
let atelierLassoArm=null,atelierLassoPending=[],atelierLassoActive=null;
let atelierLassoOverlay=null,atelierLassoDrag=null,atelierLassoTempPin=null;
function atelierLassoValid(part){
 const regions=part.sculptLassos;
 if(regions===undefined)return true;
 if(!Array.isArray(regions)||regions.length>atelierLassoMaxRegions)return false;
 const ids=new Set();
 return regions.every(r=>{
   if(!r||typeof r!=='object'||Array.isArray(r)||
     !['id','name','pins','axis','feather','morph','enabled','resolution'].every(k=>Object.hasOwn(r,k))
     ||Object.keys(r).length!==7||typeof r.id!=='string'||r.id.length>48||ids.has(r.id)
     ||typeof r.name!=='string'||r.name.length>90||!Array.isArray(r.pins)
     ||r.pins.length<3||r.pins.length>atelierLassoMaxPins)return false;
   ids.add(r.id);
   if(!Array.isArray(r.axis)||r.axis.length!==3||!r.axis.every(Number.isFinite)
      ||Math.abs(Math.hypot(...r.axis)-1)>.02)return false;
   if(!Array.isArray(r.resolution)||r.resolution.length!==2||
      !r.resolution.every(v=>Number.isInteger(v)&&v>=0&&v<=512))return false;
   if(!Number.isFinite(r.feather)||r.feather<0||r.feather>.3
     ||!Number.isFinite(r.morph)||Math.abs(r.morph)>.35||typeof r.enabled!=='boolean')return false;
   return r.pins.every(pin=>{
     if(!pin||typeof pin!=='object'||Object.keys(pin).sort().join('|')!=='bary|point|tri')return false;
     return Array.isArray(pin.point)&&pin.point.length===3&&pin.point.every(v=>Number.isFinite(v)&&Math.abs(v)<=4)
      &&Number.isInteger(pin.tri)&&pin.tri>=0&&pin.tri<=600000
      &&Array.isArray(pin.bary)&&pin.bary.length===3&&pin.bary.every(v=>Number.isFinite(v)&&v>=-.0001&&v<=1.0001)
      &&Math.abs(pin.bary.reduce((a,b)=>a+b,0)-1)<.005;
   });
 });
}
function atelierLassoProjection(r){
 const [u,v]=atelierSurfaceTangent(r.axis);
 const origin=new THREE.Vector3(...r.pins[0].point);
 const poly=r.pins.map(p=>{
   const delta=new THREE.Vector3(...p.point).sub(origin);
   return [delta.dot(u),delta.dot(v)];
 });
 return {origin,u,v,poly};
}
function atelierLassoPolygonValid(r){
 const {poly}=atelierLassoProjection(r),n=poly.length;
 let area=0;for(let i=0;i<n;i++){const p=poly[i],q=poly[(i+1)%n];area+=p[0]*q[1]-q[0]*p[1];}
 if(Math.abs(area)<.00004)return false;
 function intersects(a,b,c,d){
   const cross=(p,q,r)=>(q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]);
   const x=cross(a,b,c),y=cross(a,b,d),z=cross(c,d,a),w=cross(c,d,b);
   return x*y<-.0000001&&z*w<-.0000001;
 }
 for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
   if(i===j||(i+1)%n===j||(j+1)%n===i)continue;
   if(intersects(poly[i],poly[(i+1)%n],poly[j],poly[(j+1)%n]))return false;
 }
 return true;
}
function atelierLassoInside(pt,poly){
 let inside=false;
 for(let i=0,j=poly.length-1;i<poly.length;j=i++){
   const a=poly[i],b=poly[j];
   if((a[1]>pt[1])!==(b[1]>pt[1])
      &&pt[0]<(b[0]-a[0])*(pt[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
 }
 return inside;
}
function atelierLassoEdgeDistance(pt,poly){
 let best=Infinity;
 for(let i=0;i<poly.length;i++){
   const a=poly[i],b=poly[(i+1)%poly.length],dx=b[0]-a[0],dy=b[1]-a[1];
   const t=THREE.MathUtils.clamp(((pt[0]-a[0])*dx+(pt[1]-a[1])*dy)/(dx*dx+dy*dy+1e-12),0,1);
   best=Math.min(best,Math.hypot(pt[0]-a[0]-dx*t,pt[1]-a[1]-dy*t));
 }
 return best;
}
function atelierLassoApply(geometry,part){
 const regions=part?.sculptLassos;
 if(!regions?.length)return geometry;
 const a=geometry.attributes.position,n=geometry.attributes.normal;
 for(const r of regions){
   if(!r.enabled||!r.morph||!atelierLassoPolygonValid(r))continue;
   const res=atelierSculptResolution(part);
   if(res[0]!==r.resolution[0]||res[1]!==r.resolution[1])continue;
   const {origin,u,v,poly}=atelierLassoProjection(r),axis=new THREE.Vector3(...r.axis);
   for(let i=0;i<a.count;i++){
     if(n&&new THREE.Vector3(n.getX(i),n.getY(i),n.getZ(i)).dot(axis)<-.12)continue;
     const point=new THREE.Vector3(a.getX(i),a.getY(i),a.getZ(i)).sub(origin);
     const p=[point.dot(u),point.dot(v)];
     if(!atelierLassoInside(p,poly))continue;
     const d=atelierLassoEdgeDistance(p,poly);
     const t=r.feather?THREE.MathUtils.smoothstep(d,0,r.feather):1;
     a.setXYZ(i,a.getX(i)+axis.x*r.morph*t,
       a.getY(i)+axis.y*r.morph*t,a.getZ(i)+axis.z*r.morph*t);
   }
 }
 a.needsUpdate=true;return geometry;
}
function atelierLassoPart(){return partById(selection);}
function atelierLassoRegion(){
 const part=atelierLassoPart();
 return part?.sculptLassos?.find(r=>r.id===atelierLassoActive)||null;
}
function atelierLassoPinFromHit(hit){
 const obj=hit?.object;
 if(!obj?.isMesh||obj.userData.atelierId!==selection||hit.faceIndex==null)return null;
 const g=obj.geometry,p=g.attributes.position,idx=g.index,tri=hit.faceIndex;
 const vertex=k=>idx?idx.getX(tri*3+k):tri*3+k;
 const x=new THREE.Vector3().fromBufferAttribute(p,vertex(0));
 const y=new THREE.Vector3().fromBufferAttribute(p,vertex(1));
 const z=new THREE.Vector3().fromBufferAttribute(p,vertex(2));
 const local=obj.worldToLocal(hit.point.clone());
 const bary=new THREE.Vector3();
 THREE.Triangle.getBarycoord(local,x,y,z,bary);
 if(!Number.isFinite(bary.x))return null;
 return {point:local.toArray(),tri,bary:[bary.x,bary.y,bary.z]};
}
function atelierLassoOverlayClear(){
 const g=atelierLassoOverlay;if(!g)return;
 g.parent?.remove(g);
 g.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 atelierLassoOverlay=null;
}
function atelierLassoOverlayRefresh(){
 atelierLassoOverlayClear();
 if(!world||!modelRoot)return;
 const p=atelierLassoPart(),mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===p?.id);
 if(!mesh)return;
 mesh.updateMatrixWorld(true);
 const group=new THREE.Group();group.name='Boundary lasso pins and region';
 const active=atelierLassoRegion(),polygons=[];
 if(active)polygons.push({pins:active.pins,color:0xffd66b,id:active.id});
 if(atelierLassoPending.length)polygons.push({pins:atelierLassoPending,color:0x56f2cf,id:'draft'});
 for(const region of polygons){
   const vertices=[];
   for(let i=0;i<region.pins.length;i++){
     const p=region.id===active?.id&&atelierLassoTempPin?.index===i?
       atelierLassoTempPin.pin:region.pins[i];
     const v=mesh.localToWorld(new THREE.Vector3(...p.point));
     vertices.push(v.x,v.y,v.z);
   }
   if(vertices.length>=6){
     const lineGeo=new THREE.BufferGeometry();
     lineGeo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
     const line=new THREE.LineLoop(lineGeo,new THREE.LineBasicMaterial({
       color:region.color,depthTest:false,linewidth:2
     }));
     line.renderOrder=29;group.add(line);
   }
   const pinsGeo=new THREE.BufferGeometry();
   pinsGeo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
   const dots=new THREE.Points(pinsGeo,new THREE.PointsMaterial({
     color:region.color,size:13,sizeAttenuation:false,depthTest:false
   }));
   dots.userData.atelierLassoPins=region.id==='draft'?null:region.id;
   dots.renderOrder=31;group.add(dots);
 }
 world.add(group);atelierLassoOverlay=group;
}
function atelierLassoRefresh(){
 const p=atelierLassoPart(),select=$m('LassoRegion');
 if(!select)return;
 if(!p){atelierLassoPending=[];atelierLassoActive=null;atelierLassoArm=null;}
 const regions=p?.sculptLassos||[];
 if(!regions.some(r=>r.id===atelierLassoActive))atelierLassoActive=regions[0]?.id||null;
 select.replaceChildren();
 for(const r of regions){
   const opt=document.createElement('option');opt.value=r.id;opt.textContent=r.name;
   select.append(opt);
 }
 if(atelierLassoActive)select.value=atelierLassoActive;
 const r=atelierLassoRegion();
 const pins=$m('LassoPinIndex');pins.replaceChildren();
 for(let i=0;i<(r?.pins.length||0);i++){
   const o=document.createElement('option');o.value=String(i);o.textContent='📌 Boundary pin '+(i+1);
   pins.append(o);
 }
 $m('LassoFeather').value=String(r?.feather??.04);
 $m('LassoMorph').value=String(r?.morph??0);
 $m('LassoInfo').textContent=regions.length+' saved lasso regions · '
   +(atelierLassoPending.length?'Draft: '+atelierLassoPending.length+' pins · ':'')
   +(atelierLassoArm?'Tap mesh to '+(atelierLassoArm==='draft'?'add draft boundary pins':'insert boundary pin')+'.':
   'Boundary pins are yellow; move them by dragging on the source mesh.');
 atelierLassoOverlayRefresh();
}
function atelierLassoPick(hit){
 if(!atelierLassoArm)return false;
 const part=atelierLassoPart(),pin=atelierLassoPinFromHit(hit);
 if(!part||!pin){status('Tap the selected mesh surface to attach a lasso pin.',true);return true;}
 if(atelierLassoArm==='draft'){
   if(atelierLassoPending.length>=atelierLassoMaxPins){status('Maximum 32 boundary pins.',true);return true;}
   atelierLassoPending.push(pin);
 }else if(atelierLassoArm==='insert'){
   const r=atelierLassoRegion();if(!r)return true;
   if(r.pins.length>=atelierLassoMaxPins){status('Maximum 32 boundary pins.',true);return true;}
   const idx=Number($m('LassoPinIndex').value),next={...r,pins:r.pins.slice()};
   next.pins.splice(idx+1,0,pin);
   if(!atelierLassoValid({sculptLassos:[next]})||!atelierLassoPolygonValid(next)){
     status('Pin would cross/degenerate the polygon; try another point.',true);return true;
   }
   checkpoint();r.pins=next.pins;atelierLassoArm=null;signalEdited();
 }
 atelierLassoRefresh();return true;
}
function atelierLassoPointFromEvent(e,mesh){
 const box=renderer.domElement.getBoundingClientRect();
 const x=(e.clientX-box.left)/box.width*2-1,y=-((e.clientY-box.top)/box.height*2-1);
 raycaster.setFromCamera(new THREE.Vector2(x,y),camera);
 const h=raycaster.intersectObject(mesh,false)[0];
 return atelierLassoPinFromHit(h);
}
function atelierLassoPointerDown(e){
 if(e.button!==0||!atelierLassoOverlay||!atelierLassoActive||atelierLassoArm)return false;
 const r=atelierLassoRegion();if(!r)return false;
 const box=renderer.domElement.getBoundingClientRect();
 const pos=new THREE.Vector2((e.clientX-box.left)/box.width*2-1,-((e.clientY-box.top)/box.height*2-1));
 raycaster.setFromCamera(pos,camera);raycaster.params.Points.threshold=.06;
 const points=atelierLassoOverlay.children.find(o=>o.isPoints&&o.userData.atelierLassoPins===r.id);
 const hit=points&&raycaster.intersectObject(points,false)[0];
 if(!hit)return false;
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
 if(!mesh)return false;
 atelierLassoDrag={id:e.pointerId,regionId:r.id,index:hit.index,mesh,last:null};
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;return true;
}
function atelierLassoPointerMove(e){
 if(!atelierLassoDrag||atelierLassoDrag.id!==e.pointerId)return false;
 const pin=atelierLassoPointFromEvent(e,atelierLassoDrag.mesh);
 if(pin){
   atelierLassoDrag.last=pin;
   atelierLassoTempPin={index:atelierLassoDrag.index,pin};
   atelierLassoOverlayRefresh();
 }
 return true;
}
function atelierLassoPointerUp(e){
 const drag=atelierLassoDrag;if(!drag||drag.id!==e.pointerId)return false;
 atelierLassoDrag=null;atelierLassoTempPin=null;
 const r=atelierLassoRegion();
 if(r&&r.id===drag.regionId&&drag.last){
   const next={...r,pins:r.pins.slice()};next.pins[drag.index]=drag.last;
   if(atelierLassoValid({sculptLassos:[next]})&&atelierLassoPolygonValid(next)){
     checkpoint();r.pins=next.pins;signalEdited();
     status('Boundary pin moved along the actual mesh; local region updated. Undo available.');
   }else status('Invalid or crossing pin drag: region left unchanged.',true);
 }
 atelierLassoRefresh();return true;
}
function atelierLassoInstall(){
 const id=n=>$m('Lasso'+n);
 id('Start').addEventListener('click',()=>{
   if(!atelierLassoPart()){status('Select a mesh before drawing a lasso.',true);return;}
   atelierLassoPending=[];atelierLassoArm='draft';atelierLassoRefresh();
   status('Tap at least 3 surface positions, then press Finish polygon.');
 });
 id('Finish').addEventListener('click',()=>{
   const p=atelierLassoPart(),pins=atelierLassoPending;
   if(!p||pins.length<3){status('Draw at least 3 boundary pins before finishing.',true);return;}
   if((p.sculptLassos?.length||0)>=atelierLassoMaxRegions){status('Maximum 8 regions per mesh.',true);return;}
   const first=atelierLassoOverlay?.children?.find(o=>o.isPoints),mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   const input=id('Name').value.trim().slice(0,90)||'Region '+((p.sculptLassos?.length||0)+1);
   const n=new THREE.Vector3().subVectors(new THREE.Vector3(...pins[1].point),new THREE.Vector3(...pins[0].point))
     .cross(new THREE.Vector3().subVectors(new THREE.Vector3(...pins[2].point),new THREE.Vector3(...pins[0].point))).normalize();
   if(n.length()<.9){status('Lasso pins are collinear. Add area before finishing.',true);return;}
   if(mesh){const towards=mesh.worldToLocal(camera.position.clone()).sub(new THREE.Vector3(...pins[0].point));if(n.dot(towards)<0)n.negate();}
   const region={id:'lasso-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7),
     name:input,pins:pins.map(x=>structuredClone(x)),axis:n.toArray(),
     feather:.04,morph:0,enabled:true,resolution:atelierSculptResolution(p)};
   if(!atelierLassoValid({sculptLassos:[region]})||!atelierLassoPolygonValid(region)){
     status('Lasso boundary crossed itself or is too narrow. Move/add pins.',true);return;
   }
   checkpoint();p.sculptLassos=[...(p.sculptLassos||[]),region];
   atelierLassoActive=region.id;atelierLassoPending=[];atelierLassoArm=null;
   signalEdited();atelierLassoRefresh();
   status('Created a non-destructive surface lasso with '+region.pins.length+' editable boundary pins.');
 });
 id('Cancel').addEventListener('click',()=>{
   atelierLassoPending=[];atelierLassoArm=null;atelierLassoRefresh();
 });
 id('Region').addEventListener('change',e=>{atelierLassoActive=e.target.value;atelierLassoRefresh();});
 id('InsertPin').addEventListener('click',()=>{
   if(!atelierLassoRegion()){status('Choose or draw a region first.',true);return;}
   atelierLassoArm='insert';atelierLassoRefresh();
 });
 id('DeletePin').addEventListener('click',()=>{
   const r=atelierLassoRegion();if(!r||r.pins.length<=3)return;
   const index=Number(id('PinIndex').value),next={...r,pins:r.pins.filter((_,i)=>i!==index)};
   if(!atelierLassoPolygonValid(next)){status('Pin removal would break the boundary.',true);return;}
   checkpoint();r.pins=next.pins;signalEdited();atelierLassoRefresh();
 });
 id('DeleteRegion').addEventListener('click',()=>{
   const p=atelierLassoPart(),r=atelierLassoRegion();if(!p||!r)return;
   checkpoint();p.sculptLassos=p.sculptLassos.filter(v=>v.id!==r.id);
   atelierLassoActive=null;signalEdited();atelierLassoRefresh();
 });
 id('ApplyMorph').addEventListener('click',()=>{
   const p=atelierLassoPart(),r=atelierLassoRegion();if(!p||!r)return;
   const morph=Number(id('Morph').value),feather=Number(id('Feather').value);
   if(!Number.isFinite(morph)||Math.abs(morph)>.35||!Number.isFinite(feather)||feather<0||feather>.3){
      status('Region depth must be ±0.35 and feather 0–0.30.',true);return;
   }
   const next={...r,morph,feather};
   if(!atelierLassoValid({sculptLassos:[next]})){status('Invalid lasso morph.',true);return;}
   checkpoint();Object.assign(r,{morph,feather});const key=p.id;signalEdited();select(key);
   status('Saved surface-lasso displacement; moving pins will recompute the affected region.');
 });
 id('Toggle').addEventListener('click',()=>{
   const p=atelierLassoPart(),r=atelierLassoRegion();if(!p||!r)return;
   checkpoint();r.enabled=!r.enabled;const key=p.id;signalEdited();select(key);
 });
}
