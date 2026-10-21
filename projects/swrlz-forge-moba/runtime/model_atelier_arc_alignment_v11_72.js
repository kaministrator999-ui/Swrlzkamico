// §E v11.72: true object-sized rotation arcs and calibrated touch mapping.
let atelierArcLastAxis='x';
// v11.71's zoom-sized rings were too large for a selected face and used an
// affine 2D projection to infer 3D angles. Retain native scene/history.
function atelierArcVisualFocus(axis){
 for(const [key,item] of atelierArcRings){
  const active=key===axis;
  item.curve.material.opacity=active?1:.28;
  item.marks.material.opacity=active?.85:.25;
  item.bead.material.opacity=active?1:.42;
  item.bead.material.transparent=!active;
  item.hit.visible=true;
 }
}
function atelierArcCalibratedBuild(root){
 atelierArcReset();
 if(atelierMeshMode!=='rotate'||!root||!camera)return;
 const bounds=new THREE.Box3();
 for(const mesh of atelierMeshSelectedMeshes()){
  mesh.updateMatrixWorld(true);
  bounds.expandByObject(mesh);
 }
 const sphere=new THREE.Sphere();
 if(!bounds.isEmpty())bounds.getBoundingSphere(sphere);
 const dist=Math.max(.2,camera.position.distanceTo(root.position));
 const viewHeight=2*dist*Math.tan(THREE.MathUtils.degToRad(camera.fov||50)/2);
 // At least ~5% viewport height in radius for phone touch, but never
 // force the arc to span half the entire avatar when editing a small head.
 const extent=bounds.isEmpty()?.25:sphere.radius;
 const radius=atelierMeshClamp(Math.max(extent*1.18,viewHeight*.046),
  .2,Math.min(1.3,Math.max(.28,viewHeight*.11)));
 for(const [axis,color] of atelierArcAxes){
  const ring=new THREE.Group();
  ring.name='Rotation ruler '+axis.toUpperCase();
  ring.userData.atelierHelper=true;
  ring.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),new THREE.Vector3(...atelierMeshAxes[axis]));
  const phase=atelierArcPhase[axis],r=radius,points=[];
  for(let i=0;i<=96;i++)points.push(atelierArcPoint(r,phase-atelierArcLimit+2*atelierArcLimit*i/96));
  const curve=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({color,transparent:true,opacity:.98,depthTest:false,depthWrite:false}));
  curve.renderOrder=55;curve.userData.atelierHelper=true;ring.add(curve);
  const tickCoordinates=[];
  for(let deg=-120;deg<=120;deg+=15){
   const theta=phase+deg*Math.PI/180;
   const tick=deg%30===0?r*.09:r*.045;
   tickCoordinates.push(...atelierArcPoint(r-tick,theta).toArray(),
    ...atelierArcPoint(r+tick,theta).toArray());
  }
  const tickGeometry=new THREE.BufferGeometry();
  tickGeometry.setAttribute('position',new THREE.Float32BufferAttribute(tickCoordinates,3));
  const marks=new THREE.LineSegments(tickGeometry,new THREE.LineBasicMaterial({
   color,transparent:true,opacity:.86,depthTest:false,depthWrite:false
  }));
  marks.renderOrder=56;marks.userData.atelierHelper=true;ring.add(marks);
  const beadRadius=atelierMeshClamp(radius*.12,.055,.105);
  const bead=new THREE.Mesh(new THREE.SphereGeometry(beadRadius,14,11),
    new THREE.MeshBasicMaterial({color,depthTest:false,depthWrite:false}));
  bead.renderOrder=61;bead.userData.atelierHelper=true;ring.add(bead);
  // Do not use the old 0.37-world-unit transparent hit sphere: for a head
  // it overlaps other axes. Pointer selection uses 24-pixel screen distance.
  const hit=new THREE.Mesh(new THREE.SphereGeometry(beadRadius,12,10),
    new THREE.MeshBasicMaterial({color,transparent:true,opacity:0,depthTest:false,depthWrite:false}));
  hit.userData.atelierArcAxis=axis;hit.userData.atelierHelper=true;ring.add(hit);
  root.add(ring);
  atelierArcRings.set(axis,{ring,curve,marks,hit,bead,radius:r,phase,axis});
  atelierArcPosition(axis,0);
 }
 atelierArcVisualFocus(atelierMeshAxis);
 atelierArcReadout();
}
function atelierArcCalibratedPointerAngle(d,e){
 const item=atelierArcRings.get(d.axis);
 if(!item||!renderer||!camera)return null;
 const normal=new THREE.Vector3(...atelierMeshAxes[d.axis]);
 // A plane seen edge-on has no stable inverse; use a screen-space tangent
 // there instead of jumping to a distant ray-plane intersection.
 const look=camera.getWorldDirection(new THREE.Vector3());
 if(Math.abs(normal.dot(look))<.23)return null;
 const cursor=point(e);
 raycaster.setFromCamera(mouse.set(cursor.x,cursor.y),camera);
 const plane=new THREE.Plane().setFromNormalAndCoplanarPoint(normal,d.pivot);
 const hit=raycaster.ray.intersectPlane(plane,new THREE.Vector3());
 if(!hit||!Number.isFinite(hit.x+hit.y+hit.z))return null;
 item.ring.updateMatrixWorld(true);
 const local=item.ring.worldToLocal(hit);
 if(local.lengthSq()<1e-10)return null;
 return Math.atan2(local.y,local.x);
}
function atelierArcCalibratedDown(e){
 if(atelierMeshMode!=='rotate'||atelierMeshDrag||e.button!==0||!renderer)return false;
 const rect=renderer.domElement.getBoundingClientRect();
 let nearest=null;
 for(const [axis,item] of atelierArcRings){
  const world=item.hit.getWorldPosition(new THREE.Vector3());
  const p=world.project(camera);
  if(p.z<-1||p.z>1)continue;
  const cx=rect.left+(p.x+1)*rect.width/2;
  const cy=rect.top+(1-p.y)*rect.height/2;
  const distance=Math.hypot(cx-e.clientX,cy-e.clientY);
  // Pixel-based tolerance works at every camera zoom.
  const touch=e.pointerType==='touch',maxDistance=touch?28:21;
  if(distance>maxDistance)continue;
  // Prefer the chosen axis when two projected beads overlap.
  const score=distance-(axis===atelierMeshAxis?2.5:0);
  if(!nearest||score<nearest.score)nearest={axis,item,score};
 }
 if(!nearest)return false;
 const {axis,item}=nearest;
 const snapshot=atelierMeshSnapshots();
 if(!snapshot.length||!atelierMeshPivot)return false;
 atelierMeshAxis=axis;
 atelierArcVisualFocus(axis);
 const pivot=atelierMeshPivot.clone();
 const d={pointerId:e.pointerId,arc:true,axis,mode:'rotate',
  pivot,startX:e.clientX,startY:e.clientY,snapshot,amount:0};
 const startAngle=atelierArcCalibratedPointerAngle(d,e);
 d.initialAngle=startAngle??item.phase;
 const bead=item.hit.getWorldPosition(new THREE.Vector3()).project(camera);
 const next=item.ring.localToWorld(atelierArcPoint(item.radius,item.phase+.045)).project(camera);
 const tangent=new THREE.Vector2((next.x-bead.x)*rect.width/2,-(next.y-bead.y)*rect.height/2);
 d.tangent=tangent.lengthSq()>.005?tangent.clone().normalize():new THREE.Vector2(1,0);
 d.pixelsPerRad=atelierMeshClamp(tangent.length()/.045,24,600);
 atelierMeshDrag=d;
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;
 if(e.cancelable)e.preventDefault();
 atelierArcReadout(0);
 return true;
}
