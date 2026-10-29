// §E v11.71: three-axis curved rotation ruler, with a visible sliding bead.
// Uses only helper geometry. Native transform, history and exports stay intact.
const atelierArcSnapKey='swyrlz-atelier-rotate-arc-snap-v1';
const atelierArcAxes=[['x',0xff7585],['y',0x6af1ad],['z',0x75b5ff]];
const atelierArcLimit=120*Math.PI/180;
const atelierArcPhase={x:0,y:-Math.PI/3,z:Math.PI/3};
let atelierArcRings=new Map(),atelierArcLast=0;
let atelierArcSnap=(()=>{
 try{const n=Number(localStorage.getItem(atelierArcSnapKey));return [0,5,15].includes(n)?n:0;}
 catch(_){return 0;}
})();
function atelierArcPoint(r,theta){return new THREE.Vector3(r*Math.cos(theta),r*Math.sin(theta),0);}
function atelierArcReset(){
 atelierArcRings.clear();
}
function atelierArcBuild(root){
 atelierArcReset();
 if(atelierMeshMode!=='rotate'||!root)return;
 const radius=atelierMeshClamp(orbit.distance*.085,.68,1.35);
 for(const [axis,color] of atelierArcAxes){
  const ring=new THREE.Group();
  ring.name='Rotation arc '+axis.toUpperCase();
  ring.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(...atelierMeshAxes[axis]));
  const phase=atelierArcPhase[axis],points=[];
  const r=radius+({x:0,y:.055,z:.11}[axis]);
  for(let i=0;i<=96;i++)
   points.push(atelierArcPoint(r,phase-atelierArcLimit+2*atelierArcLimit*i/96));
  const curve=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),
   new THREE.LineBasicMaterial({color,depthTest:false,depthWrite:false,transparent:true,opacity:.9}));
  curve.renderOrder=55;curve.userData.atelierHelper=true;ring.add(curve);
  // Graduated ruler: short marks every 15 degrees, longer marks every 30.
  const ticks=[];
  for(let deg=-120;deg<=120;deg+=15){
   const angle=phase+deg*Math.PI/180;
   const inside=atelierArcPoint(r-(deg%30===0?.07:.035),angle);
   const outside=atelierArcPoint(r+(deg%30===0?.07:.035),angle);
   ticks.push(...inside.toArray(),...outside.toArray());
  }
  const ticksGeometry=new THREE.BufferGeometry();
  ticksGeometry.setAttribute('position',new THREE.Float32BufferAttribute(ticks,3));
  const marks=new THREE.LineSegments(ticksGeometry,new THREE.LineBasicMaterial({
   color:0xe5ffff,depthTest:false,depthWrite:false,transparent:true,opacity:.85
  }));
  marks.renderOrder=56;marks.userData.atelierHelper=true;ring.add(marks);
  const bead=new THREE.Mesh(new THREE.SphereGeometry(.095,14,10),
    new THREE.MeshBasicMaterial({color:0xffe1a4,depthTest:false,depthWrite:false}));
  bead.renderOrder=60;bead.userData.atelierHelper=true;ring.add(bead);
  // Enlarged invisible hit surface makes the bead operable by touch.
  const hit=new THREE.Mesh(new THREE.SphereGeometry(.37,12,10),
    new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:0,depthTest:false,depthWrite:false}));
  hit.userData.atelierArcAxis=axis;
  hit.userData.atelierHelper=true;hit.renderOrder=61;ring.add(hit);
  root.add(ring);
  atelierArcRings.set(axis,{ring,hit,bead,radius:r,phase,axis});
  atelierArcPosition(axis,0);
 }
 atelierArcReadout();
}
function atelierArcPosition(axis,angle){
 const item=atelierArcRings.get(axis);
 if(!item)return;
 const at=atelierArcPoint(item.radius,item.phase+atelierMeshClamp(angle,-atelierArcLimit,atelierArcLimit));
 item.bead.position.copy(at);
 item.hit.position.copy(at);
 item.ring.updateMatrixWorld(true);
}
function atelierArcReadout(amount=atelierArcLast){
 const row=atelierMeshStrip?.querySelector('[data-arc-ruler]');
 if(!row)return;
 row.hidden=atelierMeshMode!=='rotate';
 if(row.hidden)return;
 const output=row.querySelector('[data-arc-degrees]');
 if(output)output.textContent=(amount>=0?'+':'')+(amount*180/Math.PI).toFixed(1)+'°';
 const axis=row.querySelector('[data-arc-axis]');
 if(axis)axis.textContent=atelierMeshAxis.toUpperCase();
 const button=row.querySelector('[data-arc-snap]');
 if(button){
  button.textContent=atelierArcSnap?'Snap '+atelierArcSnap+'°':'Snap off';
  button.setAttribute('aria-pressed',String(atelierArcSnap>0));
 }
}
function atelierArcInstall(strip){
 if(strip.querySelector('[data-arc-ruler]'))return;
 const row=document.createElement('div');
 row.className='amq-arc-ruler';
 row.dataset.arcRuler='1';
 row.hidden=true;
 row.innerHTML='<span>⤾ Rotation arc <b data-arc-axis>X</b></span>'+
   '<output data-arc-degrees>+0.0°</output>'+
   '<button type="button" data-arc-snap title="Cycle angle snapping: off, 5°, 15°">Snap off</button>';
 const precision=strip.querySelector('[data-mesh-precision]');
 if(precision)precision.insertAdjacentElement('afterend',row);
 else strip.append(row);
 row.querySelector('[data-arc-snap]').addEventListener('click',e=>{
  e.stopPropagation();
  atelierArcSnap=atelierArcSnap===0?5:atelierArcSnap===5?15:0;
  try{localStorage.setItem(atelierArcSnapKey,String(atelierArcSnap))}catch(_){}
  atelierArcReadout();
 });
 atelierArcReadout();
}
// Invert the projected XY basis of a 3D ring to find where the finger is
// on its ellipse. When viewed almost edge-on, use the projected tangent.
function atelierArcPointerAngle(d,e){
 const item=atelierArcRings.get(d.axis);
 if(!item||!renderer||!camera)return null;
 const rect=renderer.domElement.getBoundingClientRect();
 const screen=v=>{
  const p=v.clone().project(camera);
  return new THREE.Vector2(rect.left+(p.x+1)*rect.width/2,rect.top+(1-p.y)*rect.height/2);
 };
 const center=screen(d.pivot);
 const ux=item.ring.localToWorld(new THREE.Vector3(item.radius,0,0));
 const uy=item.ring.localToWorld(new THREE.Vector3(0,item.radius,0));
 const u=screen(ux).sub(center),v=screen(uy).sub(center);
 const det=u.x*v.y-u.y*v.x;
 if(Math.abs(det)<100)return null;
 const px=e.clientX-center.x,py=e.clientY-center.y;
 const cos=(px*v.y-py*v.x)/det;
 const sin=(u.x*py-u.y*px)/det;
 return Math.atan2(sin,cos);
}
function atelierArcDown(e){
 if(atelierMeshMode!=='rotate'||atelierMeshDrag||e.button!==0||!renderer)return false;
 const p=point(e);mouse.set(p.x,p.y);raycaster.setFromCamera(mouse,camera);
 const hit=raycaster.intersectObjects([...atelierArcRings.values()].map(x=>x.hit),false)[0];
 if(!hit)return false;
 const axis=hit.object.userData.atelierArcAxis;
 const item=atelierArcRings.get(axis),snapshot=atelierMeshSnapshots();
 if(!item||!snapshot.length||!atelierMeshPivot)return false;
 atelierMeshAxis=axis;
 const pivot=atelierMeshPivot.clone();
 const d={pointerId:e.pointerId,arc:true,axis,mode:'rotate',pivot,
  startX:e.clientX,startY:e.clientY,snapshot,amount:0};
 const first=atelierArcPointerAngle(d,e);
 d.initialAngle=first??item.phase;
 const start=item.hit.getWorldPosition(new THREE.Vector3()).project(camera);
 const tangent=item.ring.localToWorld(atelierArcPoint(item.radius,item.phase+.025)).project(camera);
 const rect=renderer.domElement.getBoundingClientRect();
 const tangentVec=new THREE.Vector2((tangent.x-start.x)*rect.width/2,-(tangent.y-start.y)*rect.height/2);
 d.tangent=tangentVec.lengthSq()>.01?tangentVec.clone().normalize():new THREE.Vector2(1,0);
 d.pixelsPerRad=atelierMeshClamp(tangentVec.length()/.025,25,600);
 atelierMeshDrag=d;
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;
 if(e.cancelable)e.preventDefault();
 atelierArcReadout(0);
 return true;
}
function atelierArcMove(e){
 const d=atelierMeshDrag;
 if(!d?.arc||d.pointerId!==e.pointerId)return false;
 if(e.cancelable)e.preventDefault();
 const current=atelierArcPointerAngle(d,e);
 let raw;
 if(current!==null){
  raw=current-d.initialAngle;
  while(raw>Math.PI)raw-=2*Math.PI;
  while(raw< -Math.PI)raw+=2*Math.PI;
 }else{
  const dx=e.clientX-d.startX,dy=e.clientY-d.startY;
  raw=(dx*d.tangent.x+dy*d.tangent.y)/d.pixelsPerRad;
 }
 let amount=atelierMeshClamp(raw*atelierMeshSensitivity('rotate'),-atelierArcLimit,atelierArcLimit);
 if(atelierArcSnap){
  const step=atelierArcSnap*Math.PI/180;
  amount=atelierMeshClamp(Math.round(amount/step)*step,-atelierArcLimit,atelierArcLimit);
 }
 d.amount=amount;
 atelierArcPosition(d.axis,amount);
 const next=atelierMeshCandidates(d.snapshot,d.pivot,'rotate',d.axis,amount);
 atelierMeshLiveDragPreview(next);
 atelierArcReadout(amount);
 return true;
}
function atelierArcUp(e){
 const d=atelierMeshDrag;
 if(!d?.arc||d.pointerId!==e.pointerId)return false;
 atelierMeshDrag=null;
 atelierArcLast=d.amount;
 if(Math.abs(d.amount)<1e-6){
  atelierMeshRestoreLiveTransforms(d.snapshot);
  atelierMeshToolbarRefresh();
 }else{
  atelierMeshCommit(d.snapshot,d.pivot,'rotate',d.axis,d.amount);
 }
 atelierArcReadout(atelierArcLast);
 return true;
}
