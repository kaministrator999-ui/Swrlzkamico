// §E v11.73 — immediate gizmo tool switching and touch-friendly arc picking.
// Render the newly selected tool immediately, not on the next camera event.
let atelierModePaintCount=0;
function atelierMeshPaintModeImmediately(){
 if(!renderer||!world||!camera||!modelRoot)return;
 atelierMeshGizmo?.updateMatrixWorld(true);
 camera.updateMatrixWorld(true);
 renderer.render(world,camera);
 atelierModePaintCount++;
}
function atelierArcThickenRulers(){
 if(atelierMeshMode!=='rotate')return;
 for(const [axis,item] of atelierArcRings){
  if(item.wideTrack)return;
  const points=[];
  for(let i=0;i<=96;i++)
   points.push(atelierArcPoint(item.radius,item.phase-atelierArcLimit+2*atelierArcLimit*i/96));
  const tube=new THREE.Mesh(
   new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),96,
    atelierMeshClamp(item.radius*.048,.025,.046),5,false),
   new THREE.MeshBasicMaterial({color:atelierArcAxes.find(a=>a[0]===axis)[1],
    transparent:true,opacity:axis===atelierMeshAxis?.96:.28,
    depthTest:false,depthWrite:false}));
  tube.userData.atelierHelper=true;
  tube.renderOrder=54;
  item.ring.add(tube);
  item.wideTrack=tube;
  item.curve.visible=false; // Prevent competing hairline strokes.
  item.bead.scale.setScalar(1.75); // Visible grip, independent of hit testing.
 }
 atelierArcVisualFocus(atelierMeshAxis);
}
// Project samples from each world-axis arc onto the actual canvas. The user
// may now touch anywhere on the ring, not solely at the small draggable bead.
// Never choose an axis from a distant tap elsewhere on the character.
function atelierArcPickOnScreen(e){
 if(!renderer||!camera||atelierMeshMode!=='rotate')return null;
 const rect=renderer.domElement.getBoundingClientRect();
 const threshold=e.pointerType==='touch'?37:25;
 let candidate=null;
 for(const [axis,item] of atelierArcRings){
  item.ring.updateMatrixWorld(true);
  for(let k=0;k<=48;k++){
   const offset=-atelierArcLimit+2*atelierArcLimit*k/48;
   const projected=item.ring.localToWorld(atelierArcPoint(item.radius,item.phase+offset)).project(camera);
   if(projected.z<-1||projected.z>1)continue;
   const x=rect.left+(projected.x+1)*rect.width/2;
   const y=rect.top+(1-projected.y)*rect.height/2;
   const distance=Math.hypot(e.clientX-x,e.clientY-y);
   if(distance>threshold)continue;
   const priority=axis===atelierMeshAxis?12:0;
   const score=distance-priority;
   if(!candidate||score<candidate.score)
    candidate={axis,item,score,offset};
  }
 }
 return candidate;
}
function atelierArcEasyDown(e){
 if(atelierMeshMode!=='rotate'||atelierMeshDrag||e.button!==0||!renderer||!atelierMeshPivot)return false;
 const picked=atelierArcPickOnScreen(e);
 if(!picked)return false;
 const {axis,item,offset}=picked;
 const snap=atelierMeshSnapshots();
 if(!snap.length)return false;
 atelierMeshAxis=axis;
 atelierArcVisualFocus(axis);
 const pivot=atelierMeshPivot.clone();
 // Move the thumb to where the finger touched the arc before drag begins.
 atelierArcPosition(axis,offset);
 const rect=renderer.domElement.getBoundingClientRect();
 const d={pointerId:e.pointerId,arc:true,axis,mode:'rotate',
  pivot,startX:e.clientX,startY:e.clientY,snapshot:snap,amount:0,
  arcStartOffset:offset};
 const initial=atelierArcCalibratedPointerAngle(d,e);
 d.initialAngle=initial??item.phase+offset;
 const start=item.hit.getWorldPosition(new THREE.Vector3()).project(camera);
 const next=item.ring.localToWorld(atelierArcPoint(item.radius,item.phase+offset+.045)).project(camera);
 const tangent=new THREE.Vector2((next.x-start.x)*rect.width/2,-(next.y-start.y)*rect.height/2);
 d.tangent=tangent.lengthSq()>.005?tangent.clone().normalize():new THREE.Vector2(1,0);
 d.pixelsPerRad=atelierMeshClamp(tangent.length()/.045,24,600);
 atelierMeshDrag=d;
 try{renderer.domElement.setPointerCapture?.(e.pointerId)}catch(_){}
 pressed=null;
 if(e.cancelable)e.preventDefault();
 atelierArcReadout(0);
 atelierMeshPaintModeImmediately();
 return true;
}
