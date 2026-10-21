// §E v11.76 — desktop transforms, visible wire vertices and close inspection.
// All preferences are viewport-only; geometry, saved model, groups and history
// remain owned by existing Model Atelier.
let atelierDesktopDrag=null,atelierDesktopWirePoints=null,atelierDesktopWireDots=true,
    atelierDesktopWireFocus=true;
const atelierDesktopLockSupported=()=>!!renderer?.domElement?.requestPointerLock;
function atelierDesktopBegin(e,kind='object'){
 if(e.pointerType!=='mouse'||e.button!==0||!renderer?.domElement)return;
 atelierDesktopDrag={id:e.pointerId,x:e.clientX,y:e.clientY,
   totalX:0,totalY:0,kind};
 if(!atelierDesktopLockSupported())return;
 try{
  const lock=renderer.domElement.requestPointerLock({unadjustedMovement:false});
  if(lock?.catch)lock.catch(()=>{});
 }catch(_){}
}
function atelierDesktopVirtual(e){
 const d=atelierDesktopDrag;
 if(!d||e.pointerId!==d.id||document.pointerLockElement!==renderer?.domElement)
  return e;
 d.totalX+=(Number.isFinite(e.movementX)?e.movementX:0);
 d.totalY+=(Number.isFinite(e.movementY)?e.movementY:0);
 return {pointerId:e.pointerId,pointerType:e.pointerType,button:e.button,
   clientX:d.x+d.totalX,clientY:d.y+d.totalY,cancelable:e.cancelable,
   preventDefault:()=>e.preventDefault()};
}
function atelierDesktopEnd(){
 atelierDesktopDrag=null;
 if(document.pointerLockElement===renderer?.domElement)
  try{document.exitPointerLock()}catch(_){}
}
function atelierDesktopValidTransform(snap,pivot,mode,axis,amount){
 if(!Number.isFinite(amount)||mode==='scale'&&amount<=0)return false;
 const result=atelierMeshCandidates(snap,pivot,mode,axis,amount);
 return result.every(t=>{
  const p=partById(t.id);
  return !!p&&checkPart({...p,...t});
 });
}
function atelierDesktopBoundedAmount(d,raw){
 const neutral=d.mode==='scale'?1:0;
 if(atelierDesktopValidTransform(d.snapshot,d.pivot,d.mode,d.axis,raw))return raw;
 if(!atelierDesktopValidTransform(d.snapshot,d.pivot,d.mode,d.axis,neutral))
  return neutral;
 // Binary-search only between the original and requested amount. The target
 // remains at the geometry's maximum VALID size/position, not an arbitrary 3×.
 let lo=0,hi=1;
 for(let i=0;i<23;i++){
  const mid=(lo+hi)*.5;
  const amount=neutral+(raw-neutral)*mid;
  if(atelierDesktopValidTransform(d.snapshot,d.pivot,d.mode,d.axis,amount))lo=mid;
  else hi=mid;
 }
 return neutral+(raw-neutral)*lo;
}
function atelierDesktopMeshMotion(e){
 const d=atelierMeshDrag;if(!d||d.pointerId!==e.pointerId||d.arc)return false;
 const pixels=(e.clientX-d.startX)*d.direction.x+(e.clientY-d.startY)*d.direction.y;
 const speed=atelierMeshSensitivity(d.mode);
 const raw=d.mode==='move'?pixels*.0009*Math.min(orbit.distance,8)*speed:
  d.mode==='rotate'?pixels*.009*speed:
  Math.exp(atelierMeshClamp(pixels*.009*speed,-12,12));
 const amount=atelierDesktopBoundedAmount(d,raw);
 d.amount=amount;
 const next=atelierMeshCandidates(d.snapshot,d.pivot,d.mode,d.axis,amount);
 atelierMeshLiveDragPreview(next);
 if(e.cancelable)e.preventDefault();
 return true;
}
function atelierDesktopWireRefresh(){
 if(atelierDesktopWirePoints){
  atelierDesktopWirePoints.parent?.remove(atelierDesktopWirePoints);
  atelierDesktopWirePoints.geometry?.dispose();
  atelierDesktopWirePoints.material?.dispose();
  atelierDesktopWirePoints=null;
 }
 if(atelierViewGlobal!=='wireframe'&&atelierViewOverrides.size===0)return;
 if(!modelRoot)return;
 const wireMeshes=modelRoot.children.filter(o=>o.isMesh&&partById(o.userData.atelierId)&&
  atelierViewModeFor(partById(o.userData.atelierId))==='wireframe');
 for(const mesh of wireMeshes){
  if(!mesh.material?.isMeshBasicMaterial||!mesh.material.wireframe)continue;
  const active=mesh.userData.atelierId===selection;
  mesh.material.color.set(active?'#56e6ed':'#55748f');
  mesh.material.transparent=true;
  mesh.material.opacity=active?.95:(atelierDesktopWireFocus?.12:.34);
  mesh.material.depthWrite=false;
  mesh.material.needsUpdate=true;
 }
 if(!atelierDesktopWireDots||!selection||typeof atelierComponentMode!=='undefined'&&atelierComponentMode!=='mesh')return;
 const mesh=wireMeshes.find(m=>m.userData.atelierId===selection);
 if(!mesh?.geometry?.attributes.position)return;
 // Draw actual geometry vertices, not triangles. Sampling avoids a 25,000-dot
 // cloud on the anatomical head; density and geometry are untouched.
 const p=mesh.geometry.attributes.position,stride=Math.max(1,Math.ceil(p.count/2000));
 const xyz=[],seen=new Set();
 for(let i=0;i<p.count;i+=stride){
  const x=p.getX(i),y=p.getY(i),z=p.getZ(i);
  const key=[x,y,z].map(v=>Math.round(v*10000)).join(':');
  if(seen.has(key))continue;
  seen.add(key);xyz.push(x,y,z);
 }
 if(!xyz.length)return;
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));
 const dots=new THREE.Points(geo,new THREE.PointsMaterial({
  color:'#ffdc83',size:5,sizeAttenuation:false,transparent:true,opacity:1,
  depthTest:false,depthWrite:false}));
 dots.userData.atelierHelper=true;dots.renderOrder=64;
 mesh.add(dots);
 atelierDesktopWirePoints=dots;
}
function atelierDesktopWireInstall(panel){
 const advanced=panel.querySelector('.atelier-top-advanced');
 if(!advanced||advanced.querySelector('[data-desktop-wire-options]'))return;
 const bar=document.createElement('div');
 bar.className='atelier-desktop-wire-options';
 bar.dataset.desktopWireOptions='1';
 bar.innerHTML='<label><input type="checkbox" data-desktop-wire-focus checked> Focus selected wire</label>'+
  '<label><input type="checkbox" data-desktop-wire-dots checked> Vertex points</label>'+
  '<small>Dim surrounding wire meshes; dots mark actual selected-mesh vertices.</small>';
 advanced.append(bar);
 const focus=bar.querySelector('[data-desktop-wire-focus]'),
       points=bar.querySelector('[data-desktop-wire-dots]');
 focus.checked=atelierDesktopWireFocus;points.checked=atelierDesktopWireDots;
 focus.addEventListener('change',()=>{atelierDesktopWireFocus=focus.checked;atelierDesktopWireRefresh();});
 points.addEventListener('change',()=>{atelierDesktopWireDots=points.checked;atelierDesktopWireRefresh();});
}
function atelierDesktopWireModeAfterRender(){
 queueMicrotask(atelierDesktopWireRefresh);
}
function atelierDesktopCloseRestore(){
 atelierDesktopEnd();
 atelierDesktopWirePoints=null;
}
