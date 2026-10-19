// §E Surface Lasso Slice D: non-destructive, surface-attached polygonal
// boundaries with separately editable PIN controls and regional deformation.
// This is NOT local topology refinement; no new triangles are created here.
const atelierLassoMaxRegions=8,atelierLassoMaxPins=32;
let atelierLassoArm=null,atelierLassoPending=[],atelierLassoActive=null;
let atelierLassoOverlay=null,atelierLassoDrag=null,atelierLassoTempPin=null,atelierLassoSelectedPin=0;
let atelierLassoFreehand=null; // transient, never persisted
function atelierLassoTraceAdd(pin){
 if(!pin||!Array.isArray(pin.point)||pin.point.length!==3)return false;
 const last=atelierLassoPending[atelierLassoPending.length-1];
 if(last&&Math.hypot(...pin.point.map((v,i)=>v-last.point[i]))<.017)return false;
 if(atelierLassoPending.length>=atelierLassoMaxPins)return false;
 atelierLassoPending.push(pin);return true;
}
function atelierLassoValid(part){
 const regions=part.sculptLassos;
 if(regions===undefined)return true;
 if(!Array.isArray(regions)||regions.length>atelierLassoMaxRegions)return false;
 const ids=new Set();

 const basic=regions.every(r=>{
   if(!r||typeof r!=='object'||Array.isArray(r)||
     !['id','name','pins','axis','feather','morph','enabled','resolution'].every(k=>Object.hasOwn(r,k))
     ||Object.keys(r).some(k=>!['id','name','pins','axis','feather','morph','enabled','resolution',
        'selectionOp','operandRegionId','boundaryCurve','paintDabs'].includes(k))
     ||(r.boundaryCurve!==undefined&&(!Number.isFinite(r.boundaryCurve)||
       r.boundaryCurve<0||r.boundaryCurve>1))
     ||((r.selectionOp===undefined)!==(r.operandRegionId===undefined))
     ||(r.selectionOp!==undefined&&!['add','subtract','intersect'].includes(r.selectionOp))
     ||typeof r.id!=='string'||r.id.length>48||ids.has(r.id)
     ||typeof r.name!=='string'||r.name.length>90||!Array.isArray(r.pins)
     ||r.pins.length<3||r.pins.length>atelierLassoMaxPins||
      (r.paintDabs!==undefined&&
       (typeof atelierPaintDabsValid!=='function'||!atelierPaintDabsValid(r.paintDabs))))return false;
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
 if(!basic)return false;
 const byId=new Map(regions.map(r=>[r.id,r]));
 // Deliberately single-level composition: no dependency cycles or implicit
 // forward references. Layers remain native-editable polygons themselves.
 return regions.every(r=>{
   if(!r.selectionOp)return true;
   const rhs=byId.get(r.operandRegionId);
   if(!rhs||rhs===r||rhs.selectionOp||rhs.id===r.id)return false;
   if(r.resolution.some((v,i)=>v!==rhs.resolution[i]))return false;
   const a=new THREE.Vector3(...r.axis),b=new THREE.Vector3(...rhs.axis);
   return a.dot(b)>.75;
 });
}
// Chaikin-style bounded corner interpolation keeps the 3–32 original
// surface-attached control pins untouched; extra points are evaluated-only
// footprint samples, never new native mesh vertices or editable 📌 pins.
function atelierLassoCurvePoints(poly,amount=0){
 if(!Number.isFinite(amount)||amount<=0)return poly;
 const t=Math.min(1,Math.max(0,amount))*.25;
 let result=poly;
 for(let pass=0;pass<2;pass++){
   const next=[];
   for(let i=0;i<result.length;i++){
     const a=result[i],b=result[(i+1)%result.length];
     next.push([(1-t)*a[0]+t*b[0],(1-t)*a[1]+t*b[1]]);
     next.push([t*a[0]+(1-t)*b[0],t*a[1]+(1-t)*b[1]]);
   }
   result=next;
 }
 return result;
}
function atelierLassoProjection(r){
 const [u,v]=atelierSurfaceTangent(r.axis);
 const origin=new THREE.Vector3(...r.pins[0].point);
 const poly=r.pins.map(p=>{
   const delta=new THREE.Vector3(...p.point).sub(origin);
   return [delta.dot(u),delta.dot(v)];
 });
 return {origin,u,v,poly:atelierLassoCurvePoints(poly,r.boundaryCurve||0)};
}
function atelierLassoPolygonValid(r){
 if(r.boundaryCurve&&!atelierLassoPolygonValid({...r,boundaryCurve:0}))return false;
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
// Boolean selection operates on current mesh sample points. No fake
// cutout polygon is generated; each named boundary keeps its own attachment
// triangles, pins, resolution and edit history.
function atelierLassoCompiledRegionMask(part,region){
 const lhs=atelierLassoProjection(region),operation=region.selectionOp;
 const operand=operation?part?.sculptLassos?.find(r=>r.id===region.operandRegionId):null;
 if(operation&&(!operand||operand.selectionOp))return {contains:()=>false,distance:()=>Infinity};
 const rhs=operand?atelierLassoProjection(operand):null;
 const project=(v,frame)=>{
   const point=new THREE.Vector3(...v).sub(frame.origin);
   return [point.dot(frame.u),point.dot(frame.v)];
 };
 return {
   contains(v){
     const rawA=atelierLassoInside(project(v,lhs),lhs.poly);
     const a=typeof atelierPaintMaskContains==='function'?atelierPaintMaskContains(v,rawA,region.paintDabs):rawA;
     if(!rhs)return a;
     const rawB=atelierLassoInside(project(v,rhs),rhs.poly);
     const b=typeof atelierPaintMaskContains==='function'?atelierPaintMaskContains(v,rawB,operand.paintDabs):rawB;
     return operation==='add'?(a||b):operation==='subtract'?(a&&!b):(a&&b);
   },
   distance(v){
     const a=atelierLassoEdgeDistance(project(v,lhs),lhs.poly);
     if(typeof atelierPaintMaskEdgeDistance!=='function')return rhs?Math.min(a,atelierLassoEdgeDistance(project(v,rhs),rhs.poly)):a;
     return Math.min(a,atelierPaintMaskEdgeDistance(v,region.paintDabs||[]),
      rhs?Math.min(atelierLassoEdgeDistance(project(v,rhs),rhs.poly),atelierPaintMaskEdgeDistance(v,operand.paintDabs||[])):Infinity);
   }
 };
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
   const mask=atelierLassoCompiledRegionMask(part,r),axis=new THREE.Vector3(...r.axis);
   for(let i=0;i<a.count;i++){
     if(n&&new THREE.Vector3(n.getX(i),n.getY(i),n.getZ(i)).dot(axis)<-.12)continue;
     const point=[a.getX(i),a.getY(i),a.getZ(i)];
     if(!mask.contains(point))continue;
     const d=mask.distance(point);
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
// Numeric pin controls are projected onto the selected mesh triangles;
// entering an XYZ coordinate never creates a disconnected floating region.
function atelierLassoProjectXYZ(mesh,coordinates){
 const src=new THREE.Vector3(...coordinates),g=mesh?.geometry;
 if(!g||coordinates.some(v=>!Number.isFinite(v)||Math.abs(v)>4))return null;
 const a=g.attributes.position,index=g.index,n=(index?index.count:a.count)/3;
 const triangle=new THREE.Triangle(),u=new THREE.Vector3(),v=new THREE.Vector3(),w=new THREE.Vector3();
 const closest=new THREE.Vector3(),bary=new THREE.Vector3();
 let min=Infinity,out=null;
 for(let k=0;k<n;k++){
   const vi=i=>index?index.getX(3*k+i):3*k+i;
   u.fromBufferAttribute(a,vi(0));v.fromBufferAttribute(a,vi(1));w.fromBufferAttribute(a,vi(2));
   triangle.set(u,v,w).closestPointToPoint(src,closest);
   const d=src.distanceToSquared(closest);
   if(d>=min)continue;
   THREE.Triangle.getBarycoord(closest,u,v,w,bary);
   if(!Number.isFinite(bary.x))continue;
   min=d;out={point:closest.toArray(),tri:k,bary:[bary.x,bary.y,bary.z]};
 }
 return min<=.45*.45?out:null;
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
     // Smooth evaluated boundary follows the SAME tangent-plane footprint
     // as sculpt/refinement selection. Source control glyphs stay pinned to
     // real triangles; no interpolated point is promoted into native topology.
     let wire=vertices;
     if(region.id===active?.id&&active.boundaryCurve){
       const basis=atelierLassoProjection(active);
       wire=[];
       for(const xy of basis.poly){
         const p=mesh.localToWorld(basis.origin.clone().addScaledVector(basis.u,xy[0])
           .addScaledVector(basis.v,xy[1]));
         wire.push(p.x,p.y,p.z);
       }
     }
     const lineGeo=new THREE.BufferGeometry();
     lineGeo.setAttribute('position',new THREE.Float32BufferAttribute(wire,3));
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
 if(r?.pins.length){
   atelierLassoSelectedPin=Math.min(atelierLassoSelectedPin,r.pins.length-1);
   pins.value=String(atelierLassoSelectedPin);
   for(let i=0;i<3;i++)$m('LassoPinXYZ'+i).value=r.pins[atelierLassoSelectedPin].point[i].toFixed(4);
 }
 $m('LassoFeather').value=String(r?.feather??.04);
 $m('LassoMorph').value=String(r?.morph??0);
 if($m('LassoCurve'))$m('LassoCurve').value=String(r?.boundaryCurve||0);
 const booleanWith=$m('LassoBooleanWith'),validOperand=regions.filter(x=>x.id!==r?.id&&!x.selectionOp);
 if(booleanWith){
   booleanWith.replaceChildren();
   for(const item of validOperand){
     const o=document.createElement('option');o.value=item.id;
     o.textContent=item.name;booleanWith.append(o);
   }
   if(r?.operandRegionId&&validOperand.some(x=>x.id===r.operandRegionId))
     booleanWith.value=r.operandRegionId;
 }
 if($m('LassoBooleanOp'))$m('LassoBooleanOp').value=r?.selectionOp||'none';
 const paintStatus=$m('LassoPaintInfo');
 if(paintStatus)paintStatus.textContent=(r?.paintDabs?.length||0)+' saved additive/subtractive surface selection dabs.';
 if($m('LassoPaintArm'))$m('LassoPaintArm').textContent=(typeof atelierPaintArmed!=='undefined'&&atelierPaintArmed)?'Cancel paint mode':'Paint selected region by dragging';
 $m('LassoInfo').textContent=regions.length+' saved lasso regions · '
   +(atelierLassoPending.length?'Draft: '+atelierLassoPending.length+' pins · ':'')
   +(atelierLassoArm==='freehand'?'Drag over the selected mesh to trace up to 32 boundary pins.':
    atelierLassoArm?'Tap mesh to '+(atelierLassoArm==='draft'?'add draft boundary pins':'insert boundary pin')+'.':
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
 if(e.button!==0)return false;
 if(typeof atelierPaintArmed!=='undefined'&&atelierPaintArmed)return atelierPaintStart(e);
 if(atelierLassoArm==='freehand'){
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   if(!mesh)return false;
   const pin=atelierLassoPointFromEvent(e,mesh);
   if(!pin){status('Begin tracing on the selected mesh surface.',true);return true;}
   atelierLassoPending=[pin];
   atelierLassoFreehand={id:e.pointerId,mesh,lastX:e.clientX,lastY:e.clientY};
   renderer.domElement.setPointerCapture?.(e.pointerId);
   pressed=null;atelierLassoOverlayRefresh();return true;
 }
 if(!atelierLassoOverlay||!atelierLassoActive||atelierLassoArm)return false;
 const r=atelierLassoRegion();if(!r)return false;
 const box=renderer.domElement.getBoundingClientRect();
 const pos=new THREE.Vector2((e.clientX-box.left)/box.width*2-1,-((e.clientY-box.top)/box.height*2-1));
 raycaster.setFromCamera(pos,camera);raycaster.params.Points.threshold=.06;
 const points=atelierLassoOverlay.children.find(o=>o.isPoints&&o.userData.atelierLassoPins===r.id);
 const hit=points&&raycaster.intersectObject(points,false)[0];
 if(!hit)return false;
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
 if(!mesh)return false;
 atelierLassoSelectedPin=hit.index;
 atelierLassoDrag={id:e.pointerId,regionId:r.id,index:hit.index,mesh,last:null};
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;return true;
}
function atelierLassoPointerMove(e){
 if(typeof atelierPaintMove==='function'&&atelierPaintMove(e))return true;
 if(atelierLassoFreehand?.id===e.pointerId){
   const trace=atelierLassoFreehand;
   if(Math.hypot(e.clientX-trace.lastX,e.clientY-trace.lastY)<7)return true;
   trace.lastX=e.clientX;trace.lastY=e.clientY;
   const pin=atelierLassoPointFromEvent(e,trace.mesh);
   if(atelierLassoTraceAdd(pin))atelierLassoOverlayRefresh();
   return true;
 }
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
 if(typeof atelierPaintFinish==='function'&&atelierPaintFinish(e))return true;
 if(atelierLassoFreehand?.id===e.pointerId){
   atelierLassoTraceAdd(atelierLassoPointFromEvent(e,atelierLassoFreehand.mesh));
   atelierLassoFreehand=null;atelierLassoArm=null;
   const count=atelierLassoPending.length;
   atelierLassoRefresh();
   status(count>=3?
     'Freehand trace captured '+count+' surface pins. Review, then Finish polygon (or Cancel).':
     'Only '+count+' points captured; trace a longer loop or Cancel.',count<3);
   return true;
 }
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
function atelierLassoPointerCancel(e){
 if(typeof atelierPaintFinish==='function'&&atelierPaintFinish(e,true))return true;
 if(atelierLassoFreehand?.id!==e.pointerId)return false;
 atelierLassoFreehand=null;atelierLassoArm=null;atelierLassoPending=[];
 atelierLassoRefresh();status('Freehand trace cancelled without changing mesh.');
 return true;
}
// A group boundary edit changes only region-control pins, never source
// vertices or triangles. It reprojects every proposed pin before committing
// a single atomic native Undo transaction.
function atelierLassoGroupCandidate(region,mesh,raw,delta){
 if(!region||!mesh||typeof raw!=='string'||!/^\d+(?:\s*,\s*\d+)*$/.test(raw.trim())||
    !Array.isArray(delta)||delta.length!==3||!delta.every(v=>Number.isFinite(v)&&Math.abs(v)<=.15))
   return {ok:false,reason:'Use 1–8 one-based pin indices and finite XYZ delta ≤0.15'};
 const indices=[...new Set(raw.split(',').map(v=>Number(v.trim())-1))];
 if(!indices.length||indices.length>8||indices.some(i=>!Number.isInteger(i)||i<0||i>=region.pins.length))
   return {ok:false,reason:'One-based pin numbers must exist, with at most eight unique pins'};
 const pins=region.pins.slice();
 for(const i of indices){
   const source=region.pins[i].point,xyz=source.map((v,j)=>v+delta[j]);
   const projected=atelierLassoProjectXYZ(mesh,xyz);
   if(!projected)return {ok:false,reason:'One or more moved pins could not reattach to the original mesh'};
   pins[i]=projected;
 }
 const updated={...region,pins};
 if(!atelierLassoValid({sculptLassos:[updated]})||!atelierLassoPolygonValid(updated))
   return {ok:false,reason:'The grouped motion would cross or collapse the boundary'};
 return {ok:true,pins,indices};
}
// Push just one chosen boundary edge, not the entire selection area.
// Positive values follow polygon winding's outward tangent-plane normal;
// negative values pull only that edge inward. Endpoint reattachment is atomic.
function atelierLassoSegmentCandidate(region,mesh,index,amount){
 if(!region||!mesh||!Number.isInteger(index)||index<0||
    index>=region.pins.length||!Number.isFinite(amount)||
    Math.abs(amount)>.15||Math.abs(amount)<.0001)
   return {ok:false,reason:'Choose an existing segment and a signed amount of 0.0001–0.15'};
 const basis=atelierLassoProjection({...region,boundaryCurve:0}),poly=basis.poly,n=poly.length;
 const a=poly[index],b=poly[(index+1)%n];
 const dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);
 if(length<1e-5)return {ok:false,reason:'Selected segment is degenerate'};
 let area=0;
 for(let i=0;i<n;i++){
   const p=poly[i],q=poly[(i+1)%n];area+=p[0]*q[1]-q[0]*p[1];
 }
 if(Math.abs(area)<.00004)return {ok:false,reason:'Boundary has no stable winding'};
 const sign=Math.sign(area),normalU=sign*dy/length,normalV=-sign*dx/length;
 const motion=basis.u.clone().multiplyScalar(normalU*amount)
   .addScaledVector(basis.v,normalV*amount);
 const next=(index+1)%n;
 const result=atelierLassoGroupCandidate(region,mesh,
   String(index+1)+','+String(next+1),motion.toArray());
 return result.ok?{...result,segment:index,outward:amount>0}:result;
}
function atelierLassoInstall(){
 if(typeof atelierPaintInstall==='function')atelierPaintInstall();
 const id=n=>$m('Lasso'+n);
 id('PinIndex').addEventListener('change',e=>{
   atelierLassoSelectedPin=Number(e.target.value);
   const p=atelierLassoRegion()?.pins[atelierLassoSelectedPin];
   if(p)for(let i=0;i<3;i++)id('PinXYZ'+i).value=p.point[i].toFixed(4);
 });
 const numericPin=()=>{
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   return atelierLassoProjectXYZ(mesh,[0,1,2].map(i=>Number(id('PinXYZ'+i).value)));
 };
 id('AddXYZ').addEventListener('click',()=>{
   const pin=numericPin();
   if(!pin){status('XYZ must be near the selected mesh surface.',true);return;}
   if(atelierLassoArm==='draft'){
     if(atelierLassoPending.length>=atelierLassoMaxPins)return;
     atelierLassoPending.push(pin);atelierLassoRefresh();return;
   }
   const r=atelierLassoRegion();if(!r||r.pins.length>=atelierLassoMaxPins){
     status('Start a draft lasso or choose an existing region.',true);return;
   }
   const next={...r,pins:r.pins.slice()};next.pins.splice(atelierLassoSelectedPin+1,0,pin);
   if(!atelierLassoPolygonValid(next)){status('Adding this pin would cross the boundary.',true);return;}
   checkpoint();r.pins=next.pins;atelierLassoSelectedPin++;
   signalEdited();atelierLassoRefresh();
 });
 id('MoveXYZ').addEventListener('click',()=>{
   const r=atelierLassoRegion(),pin=numericPin();if(!r||!pin)return;
   const next={...r,pins:r.pins.slice()};next.pins[atelierLassoSelectedPin]=pin;
   if(!atelierLassoPolygonValid(next)){status('Pin move would collapse/cross the boundary.',true);return;}
   checkpoint();r.pins=next.pins;signalEdited();atelierLassoRefresh();
 });
 id('SegmentMove').addEventListener('click',()=>{
   const r=atelierLassoRegion(),p=atelierLassoPart();
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   const index=Number(id('PinIndex').value),amount=Number(id('SegmentAmount').value);
   const candidate=atelierLassoSegmentCandidate(r,mesh,index,amount);
   if(!candidate.ok){
     status('Segment adjustment rejected: '+candidate.reason,true);return;
   }
   checkpoint();r.pins=candidate.pins;
   const key=p.id;signalEdited();select(key);
   status('Surface-reprojected boundary segment '+(index+1)+' moved '+
     (candidate.outward?'outward':'inward')+' in one native Undo transaction. Other controls unchanged.');
 });
 id('GroupMove').addEventListener('click',()=>{
   const r=atelierLassoRegion(),mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   const raw=id('GroupPins').value;
   const delta=[0,1,2].map(k=>Number(id('GroupDelta'+k).value));
   const result=atelierLassoGroupCandidate(r,mesh,raw,delta);
   if(!result.ok){status('Pin group rejected: '+result.reason,true);return;}
   checkpoint();r.pins=result.pins;
   const key=selection;signalEdited();select(key);
   status('Moved '+result.indices.length+' boundary pins on their mesh surface in one undoable transaction; source topology unchanged.');
 });
 id('Start').addEventListener('click',()=>{
   if(!atelierLassoPart()){status('Select a mesh before drawing a lasso.',true);return;}
   atelierLassoFreehand=null;atelierLassoPending=[];atelierLassoArm='draft';atelierLassoRefresh();
   status('Tap at least 3 surface positions, then press Finish polygon.');
 });
 id('StartFreehand').addEventListener('click',()=>{
   if(!atelierLassoPart()){status('Select a mesh before tracing a lasso.',true);return;}
   atelierLassoFreehand=null;atelierLassoPending=[];atelierLassoArm='freehand';
   atelierLassoRefresh();
   status('Drag one finger or mouse over the mesh. Release, inspect boundary pins, then Finish polygon.');
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
   atelierLassoFreehand=null;atelierLassoPending=[];atelierLassoArm=null;atelierLassoRefresh();
 });
 id('Region').addEventListener('change',e=>{atelierLassoActive=e.target.value;atelierLassoRefresh();});
 id('CurveApply').addEventListener('click',()=>{
   const p=atelierLassoPart(),r=atelierLassoRegion();
   if(!p||!r)return;
   const amount=Number(id('Curve').value);
   if(!Number.isFinite(amount)||amount<0||amount>1){
     status('Curve interpolation must be between 0 (corners) and 1 (rounded).',true);return;
   }
   const updated={...r};
   if(amount===0)delete updated.boundaryCurve;
   else updated.boundaryCurve=amount;
   const next=p.sculptLassos.map(x=>x.id===r.id?updated:x);
   if(!atelierLassoValid({...p,sculptLassos:next})||
       !atelierLassoPolygonValid(updated)||!checkPart({...p,sculptLassos:next})){
     status('Smoothed boundary would self-intersect or fail native validation. No changes made.',true);return;
   }
   if((r.boundaryCurve||0)===amount)return;
   checkpoint();p.sculptLassos=next;
   signalEdited();select(p.id);atelierLassoActive=r.id;atelierLassoRefresh();
   status(amount?'Saved curve strength '+amount.toFixed(2)+'. Original surface pins stay unchanged.':
     'Restored exact straight-edge polygon boundary.');
 });
 id('BooleanApply').addEventListener('click',()=>{
   const p=atelierLassoPart(),r=atelierLassoRegion();if(!p||!r)return;
   const op=id('BooleanOp').value,operand=id('BooleanWith').value;
   if(!['none','add','subtract','intersect'].includes(op)){
     status('Unsupported Boolean lasso operation.',true);return;
   }
   const next={...r};delete next.selectionOp;delete next.operandRegionId;
   if(op!=='none'){next.selectionOp=op;next.operandRegionId=operand;}
   const regions=p.sculptLassos.map(x=>x.id===r.id?next:x);
   if(!atelierLassoValid({...p,sculptLassos:regions})||
       !checkPart({...p,sculptLassos:regions})){
     status('Boolean selection rejected: use another independent region with compatible orientation and source resolution.',true);
     atelierLassoRefresh();return;
   }
   checkpoint();p.sculptLassos=regions;
   const key=p.id;signalEdited();select(key);atelierLassoActive=r.id;
   atelierLassoRefresh();
   status(op==='none'?'Region restored to its original boundary selection.':
     'Saved '+op+' Boolean region mask. Sculpt and local refinement both evaluate it; pins and original mesh remain editable.');
 });
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
   if(p.refinementLayers?.some(layer=>layer.regionId===r.id)){
     status('Remove saved refinement layers using this region before deleting its boundary.',true);return;
   }
   if(p.sculptLassos.some(x=>x.operandRegionId===r.id)){
     status('This region is referenced by a Boolean selection. Clear dependent operation before deletion.',true);return;
   }
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
