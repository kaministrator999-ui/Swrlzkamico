// V11_20_LOCAL_VERTEX_SPHERE_BRUSH
// Opt-in, native-project-backed geometric sculpting; never imports OBJ files.
// A picked center/normal drives a finite-radius vertex group. Each stroke is
// recorded in its part and deterministically replayed after procedural rebuild.
const atelierSculptMaxStrokes=32;
const atelierSculptModes=['smooth','soft','flat','sharp'];
const atelierSculptOperations=['push','smooth','flatten','inflate','pinch','translate'];
const atelierSculptMaxVertexEdits=64;
function atelierSculptVertexValid(p){
 const edits=p.sculptVertexEdits;
 if(edits===undefined)return true;
 if(!Array.isArray(edits)||edits.length>atelierSculptMaxVertexEdits)return false;
 return edits.every(e=>e&&typeof e==='object'&&!Array.isArray(e)
   &&(['delta|indices|resolution','indices|moves|resolution'].includes(Object.keys(e).sort().join('|')))
   &&Array.isArray(e.indices)&&e.indices.length>0&&e.indices.length<=256
   &&new Set(e.indices).size===e.indices.length
   &&e.indices.every(i=>Number.isInteger(i)&&i>=0&&i<=300000)
   &&((Array.isArray(e.delta)&&e.delta.length===3&&e.delta.every(v=>Number.isFinite(v)&&Math.abs(v)<=.5))||
      (Array.isArray(e.moves)&&e.moves.length===e.indices.length&&e.moves.every(a=>
        Array.isArray(a)&&a.length===3&&a.every(v=>Number.isFinite(v)&&Math.abs(v)<=.5))))
   &&Array.isArray(e.resolution)&&e.resolution.length===2
   &&e.resolution.every(v=>Number.isInteger(v)&&v>=0&&v<=512));
}
function atelierSculptResolution(p){
 const d=p.meshDensity;return d?[d.u,d.v]:[0,0];
}

const atelierSculptClamp=(v,low,high)=>Math.min(high,Math.max(low,v));
function atelierSculptValid(p){
 const strokes=p.sculptBrushes;
 if(!atelierSculptVertexValid(p)||!atelierLassoValid(p)||!atelierRefineValid(p))return false;
 if(strokes===undefined)return true;
 if(!Array.isArray(strokes)||strokes.length>atelierSculptMaxStrokes)return false;
 return strokes.every(s=>{
   if(!s||typeof s!=='object'||Array.isArray(s)
     ||Object.keys(s).some(k=>!['axis','center','falloff','half','level','pitch','plateau','radius','snap','strength','taper','yaw',
       'surfaceMode','selectionRadius','offsetU','offsetV','operation','mirrorX','cameraLocal','falloffCurve'].includes(k))
     ||!['axis','center','falloff','half','level','pitch','plateau','radius','snap','strength','taper','yaw']
       .every(k=>Object.prototype.hasOwnProperty.call(s,k)))return false;
   const vec=v=>Array.isArray(v)&&v.length===3&&v.every(x=>Number.isFinite(x)&&Math.abs(x)<=4);
   if(!vec(s.center)||!vec(s.axis))return false;
   const n=Math.hypot(...s.axis);
   return n>.99&&n<1.01
      &&Number.isFinite(s.radius)&&s.radius>=.03&&s.radius<=2.5
      &&Number.isFinite(s.strength)&&Math.abs(s.strength)<=.5
      &&typeof s.half==='boolean'
      &&atelierSculptModes.includes(s.falloff)
       &&(s.falloffCurve===undefined||(typeof atelierSculptCurveValid==='function'&&atelierSculptCurveValid(s.falloffCurve)))
      &&Number.isFinite(s.yaw)&&Math.abs(s.yaw)<=Math.PI
      &&Number.isFinite(s.pitch)&&Math.abs(s.pitch)<=Math.PI
      &&Number.isFinite(s.snap)&&s.snap>=0&&s.snap<=.1
      &&Number.isFinite(s.plateau)&&s.plateau>=0&&s.plateau<=1
      &&Number.isFinite(s.taper)&&s.taper>=0&&s.taper<=1
      &&typeof s.level==='boolean'
      &&(s.operation===undefined||atelierSculptOperations.includes(s.operation))
      &&(s.mirrorX===undefined||typeof s.mirrorX==='boolean')
      &&(s.surfaceMode===undefined||atelierSurfaceModes.includes(s.surfaceMode))
      &&((s.surfaceMode==='occluded'||s.surfaceMode==='visible-geodesic')?(Array.isArray(s.cameraLocal)&&s.cameraLocal.length===3&&s.cameraLocal.every(x=>Number.isFinite(x)&&Math.abs(x)<=600)):s.cameraLocal===undefined)
      &&(s.selectionRadius===undefined||(Number.isFinite(s.selectionRadius)&&s.selectionRadius>=.03&&s.selectionRadius<=2.5))
      &&[s.offsetU??0,s.offsetV??0].every(v=>Number.isFinite(v)&&Math.abs(v)<=.5);
 });
}
function atelierSculptFalloff(normalizedDistance,mode,plateau=0,taper=.5){
 if(normalizedDistance<=plateau)return 1;
 if(normalizedDistance>=1)return 0;
 const x=(normalizedDistance-plateau)/(1-plateau);
 if(mode==='flat')return x<.92?1:Math.max(0,(1-x)/.08);
 if(mode==='sharp')return Math.pow(1-x,2+8*taper);
 const expo=.55+4.8*taper; // smaller -> broad fade, larger -> concentrated edge drop
 if(mode==='soft'){
   const k=1.5+6*taper;
   const g=(Math.exp(-k*x*x)-Math.exp(-k))/(1-Math.exp(-k));
   return Math.pow(Math.max(0,g),.55+2*taper);
 }
 return Math.pow(1-x*x,expo);
}
function atelierSculptApply(geometry,part){
 if(!geometry?.attributes?.position||(!part?.sculptBrushes?.length&&!part?.sculptVertexEdits?.length&&!part?.sculptLassos?.some(r=>r.enabled&&r.morph)&&!part?.refinementLayers?.some(l=>l.enabled)))return geometry;
 let a=geometry.attributes.position;
 atelierLassoApply(geometry,part);
 // Position samples in a UV sphere are duplicated at the seam. Use the SAME
 // position-dependent influence for identical vertices so the seam stays shut.
 for(const s of part.sculptBrushes||[]){
   if(!atelierSculptValid({sculptBrushes:[s]}))continue;
   if((s.operation&&s.operation!=='push')||s.mirrorX){
     atelierSculptApplyOperator(geometry,s);continue;
   }
   const origin=new THREE.Vector3(...s.center);
   const axis=new THREE.Vector3(...s.axis).applyEuler(new THREE.Euler(s.pitch,s.yaw,0,'YXZ')).normalize();
   const delta=new THREE.Vector3(),move=new THREE.Vector3(),r=s.radius;
   const selected=s.surfaceMode?atelierSurfaceWeights(geometry,s):null;
   const originPoint=selected?.origin||origin;
   for(let i=0;i<a.count;i++){
     const x=a.getX(i),y=a.getY(i),z=a.getZ(i);
     delta.set(x-originPoint.x,y-originPoint.y,z-originPoint.z);
     const radial=delta.length();
     const distance=(s.surfaceMode==='connected'||s.surfaceMode==='visible-geodesic')?selected.dist[i]:radial;
     if(distance>=r||(selected&&selected.dist[i]>selected.radius))continue;
     let weight=(typeof atelierSculptCurveWeight==='function')?
       atelierSculptCurveWeight(distance/r,s):
       atelierSculptFalloff(distance/r,s.falloff,s.plateau,s.taper);
     // Rotatable HALF-sphere restricts the influenced group to the chosen
     // side of the brush. Fade through the plane instead of a hard seam.
     if(s.half)weight*=THREE.MathUtils.smoothstep(delta.dot(axis),-r*.18,0);
     // Preserve topology/relief or level affected vertices toward one
     // shared brush-aligned plane at center + signed desired depth.
     const signed=delta.dot(axis);
     let amount=weight*(s.level?s.strength-signed:s.strength);
     if(s.snap>0)amount=Math.round(amount/s.snap)*s.snap; // snap the MOVE, not base mesh
     move.copy(axis).multiplyScalar(amount);
     a.setXYZ(i,x+move.x,y+move.y,z+move.z);
   }
 }
 // Explicit index edits are stored in native project data, not transient GPU
 // buffers. They are resolution-bound: changing sampling never silently
 // reassigns an edit to an unrelated face vertex.
 for(const edit of part.sculptVertexEdits||[]){
   const res=atelierSculptResolution(part);
   if(edit.resolution[0]!==res[0]||edit.resolution[1]!==res[1])continue;
   edit.indices.forEach((i,k)=>{
     if(i>=a.count)return;
     const delta=edit.moves?.[k]||edit.delta;
     a.setXYZ(i,a.getX(i)+delta[0],a.getY(i)+delta[1],a.getZ(i)+delta[2]);
   });
 }
 a.needsUpdate=true;
 geometry=atelierRefineApply(geometry,part);
 a=geometry.attributes.position;
 // Preserve interpolated normals on refined meshes to avoid faceted seams;
 // existing native meshes retain their legacy recompute behavior.
 if(!geometry.userData.refinedTriangles)geometry.computeVertexNormals();
 geometry.computeBoundingSphere();
 geometry.computeBoundingBox();
 return geometry;
}
let atelierSculptArmed=false,atelierSculptHit=null;
function atelierSculptRefresh(){
 const p=partById(selection),deck=$m('SculptBrush');
 if(!deck)return;
 deck.hidden=!p;
 if(atelierSculptHit?.partId!==selection)atelierSculptHit=null;
 if(!p)atelierSculptArmed=false;
 if(p){const d=atelierSculptResolution(p);$m('SculptBrushGridU').value=d[0]||64;$m('SculptBrushGridV').value=d[1]||48;}
 const hint=$m('SculptBrushInfo');
 if(hint)hint.textContent=(atelierSculptHit?'Picked surface on '+p.name+'. ':'')
   +(p?.sculptBrushes?.length||0)+' saved strokes. '
   +(atelierSculptArmed?'Tap the mesh to select the brush center.':'Orbit freely; arm to pick a point.');
 const arm=$m('SculptBrushPick');
 if(arm)arm.textContent=atelierSculptArmed?'Cancel picking':'Pick center on mesh';
 atelierLassoRefresh();
 atelierRefineRefresh();
 atelierSculptDensityRefresh();
 const remove=$m('SculptBrushUndoStroke');
 if(remove)remove.disabled=!(p?.sculptBrushes?.length);
}
function atelierSculptPick(hit){
 if(!atelierSculptArmed)return false;
 if(!hit?.object?.isMesh||hit.object.userData.atelierId!==selection){
   status('Sculpt picking: tap the selected mesh. Drag to orbit normally.',true);
   return true;
 }
 const local=hit.object.worldToLocal(hit.point.clone());
 // Raycaster face.normal uses the native triangle's part-local orientation.
 // A two-sided surface may have an inverted triangle; orient toward the view.
 const normal=hit.face?.normal?.clone()||new THREE.Vector3(0,0,1);
 const cameraLocal=hit.object.worldToLocal(camera.position.clone());
 if(normal.dot(cameraLocal.sub(local))<0)normal.negate();
 normal.normalize();
 atelierSculptHit={partId:selection,center:local.toArray(),axis:normal.toArray()};
 for(let i=0;i<3;i++){
   $m('SculptBrushCenter'+i).value=local.getComponent(i).toFixed(4);
   $m('SculptBrushAxis'+i).value=normal.getComponent(i).toFixed(4);
 }
 atelierSculptArmed=false;
 atelierSculptRefresh();
 atelierSurfacePreviewRefresh();
 status('Surface brush point selected. Adjust front/connected/through targeting and preview the vertex footprint before Apply.');
 return true;
}
function atelierSculptForm(){
 const p=partById(selection);
 if(!p)return null;
 const xyz=stem=>[0,1,2].map(i=>Number($m('SculptBrush'+stem+i).value));
 const center=xyz('Center'),axis=xyz('Axis');
 const len=Math.hypot(...axis);
 const amount=Number($m('SculptBrushAmount').value);
 const action=$m('SculptBrushMode').value;
 const operation=['extrude','intrude'].includes(action)?'push':action;
 const s={
  center,axis:axis.map(v=>v/len),
  radius:Number($m('SculptBrushRadius').value),
  strength:(action==='intrude'?-1:1)*amount,
  operation,mirrorX:$m('SculptBrushMirrorX').checked,
  half:$m('SculptBrushHalf').checked,
  falloff:$m('SculptBrushFalloff').value,
  plateau:Number($m('SculptBrushPlateau').value),
  taper:Number($m('SculptBrushTaper').value),
  level:$m('SculptBrushLevel').checked,
  yaw:Number($m('SculptBrushYaw').value)*Math.PI/180,
  pitch:Number($m('SculptBrushPitch').value)*Math.PI/180,
  snap:Number($m('SculptBrushSnap').value),
  surfaceMode:$m('SculptBrushSurfaceMode').value,
  selectionRadius:Number($m('SculptBrushSelectRadius').value),
  offsetU:Number($m('SculptBrushOffsetU').value),
  offsetV:Number($m('SculptBrushOffsetV').value)
 };
 if($m('SculptBrushCurveEnabled')?.checked){
  const knots=atelierSculptCurveInput();if(!knots)return null;
  s.falloffCurve=knots;
 }
 if($m('SculptBrushRadiusUnits')?.value==='screen'){
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
  if(!mesh||!renderer?.domElement)return null;
  const at=new THREE.Vector3(...s.center);
  const influence=atelierBrushLocalRadiusFromPixels(mesh,camera,renderer.domElement,
     at,Number($m('SculptBrushRadiusScreen').value));
  const selectRadius=atelierBrushLocalRadiusFromPixels(mesh,camera,renderer.domElement,
     at,Number($m('SculptBrushSelectRadiusScreen').value));
  if(influence===null||selectRadius===null)return null;
  s.radius=influence;s.selectionRadius=selectRadius;
 }
 if(s.surfaceMode==='occluded'||s.surfaceMode==='visible-geodesic'){
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
  if(!mesh)return null;
  const g=mesh.geometry;
  if(Math.floor((g.index?.count||g.attributes.position.count)/3)>atelierOcclusionMaxTriangles||
     g.attributes.position.count>atelierOcclusionMaxVertices)return null;
  // Store the eye in object-local space so Undo and JSON restore replay
  // the exact same selection after the viewport changes.
  s.cameraLocal=mesh.worldToLocal(camera.position.clone()).toArray();
 }
 if(!Number.isFinite(len)||len<1e-5||!atelierSculptValid({sculptBrushes:[s]}))return null;
 return s;
}
function atelierSculptInstall(){
 $m('SculptBrushPick').addEventListener('click',()=>{
   if(!partById(selection)){status('Select a mesh to sculpt first.',true);return;}
   atelierSculptArmed=!atelierSculptArmed;
   atelierSculptRefresh();
 });
 $m('SculptBrushApply').addEventListener('click',()=>{
   const p=partById(selection),s=atelierSculptForm();if(!p)return;
   if(!s){const reason=typeof atelierBrushPixelLastReason==='string'?atelierBrushPixelLastReason:'';status('Brush rejected: '+(reason||'invalid radius, occlusion budget, center or mesh'),true);return;}
   if((p.sculptBrushes?.length??0)>=atelierSculptMaxStrokes){
     status('Maximum '+atelierSculptMaxStrokes+' strokes for one mesh. Use Undo or remove strokes.',true);return;
   }
   const next={...p,sculptBrushes:[...(p.sculptBrushes||[]),s]};
   if(!checkPart(next)){status('Sculpt geometry data rejected by native validation.',true);return;}
   checkpoint();p.sculptBrushes=next.sculptBrushes;const id=p.id;
   signalEdited();select(id);
   atelierSurfacePreviewClear();
   status('Saved '+(s.operation==='push'?(s.strength<0?'intrusion':'extrusion'):
     s.operation)+(s.mirrorX?' with mirrored X editing':'')+
     ' as a local, undoable vertex stroke. Save JSON to keep it.');
 });
 atelierSculptVertexInstall();
 atelierSculptDensityInstall();
 atelierSculptSurfaceInstall();
 atelierBrushSizingRefresh();
 if(typeof atelierSculptCurveInstall==='function')atelierSculptCurveInstall();
 atelierLassoInstall();
 atelierGroupInstall();
 if(typeof atelierViewportGizmoInstall==='function')atelierViewportGizmoInstall();
 atelierRefineInstall();
 $m('SculptBrushUndoStroke').addEventListener('click',()=>{
   const p=partById(selection);if(!p?.sculptBrushes?.length)return;
   checkpoint();p.sculptBrushes=p.sculptBrushes.slice(0,-1);
   signalEdited();select(p.id);status('Last sculpt stroke removed; full-model Undo can restore it.');
 });
}

// Vertex map and pickable, locally edited point groups. These are *editor
// overlays* and never become part of the source mesh, OBJ or exported model.
let atelierSculptVertexMode=false,atelierSculptVertexIDs=[],atelierSculptLastVertexPart=null,atelierSculptOverlay=null,
  atelierSculptGizmo=null,atelierSculptDrag=null,atelierSculptOverlayMesh=null;
function atelierSculptOverlayClear(){
 if(atelierSculptOverlay){
   atelierSculptOverlay.parent?.remove(atelierSculptOverlay);
   atelierSculptOverlay.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 }
 atelierSculptOverlay=null;atelierSculptGizmo=null;atelierSculptOverlayMesh=null;
}
function atelierSculptExpandedIndices(geometry,ids){
 const a=geometry.attributes.position;
 const keys=new Set(ids.filter(i=>i>=0&&i<a.count).map(i=>
   [a.getX(i),a.getY(i),a.getZ(i)].map(n=>Math.round(n*100000)).join(',')));
 const out=[];
 for(let i=0;i<a.count;i++){
   const k=[a.getX(i),a.getY(i),a.getZ(i)].map(n=>Math.round(n*100000)).join(',');
   if(keys.has(k))out.push(i);
 }
 return out;
}
function atelierSculptCentroid(mesh,ids){
 const pos=mesh.geometry.attributes.position,v=new THREE.Vector3();
 for(const i of ids)v.add(new THREE.Vector3().fromBufferAttribute(pos,i));
 v.multiplyScalar(1/ids.length);
 return mesh.localToWorld(v);
}
function atelierSculptOverlayRefresh(){
 atelierSculptOverlayClear();
 if(atelierSculptLastVertexPart!==selection){
   atelierSculptVertexIDs=[];atelierSculptLastVertexPart=selection;
 }
 if(!atelierSculptVertexMode||!modelRoot||!world)return;
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
 if(!mesh)return;
 mesh.updateMatrixWorld(true);
 atelierSculptOverlayMesh=mesh;
 const src=mesh.geometry.attributes.position,count=src.count,root=new THREE.Group();
 root.name='Sculpt vertex map overlay';
 atelierSculptOverlay=root;world.add(root);
 const stride=Math.max(1,Math.ceil(count/5000));
 const verts=[],sourceIDs=[];
 for(let i=0;i<count;i+=stride){
   const worldPos=mesh.localToWorld(new THREE.Vector3().fromBufferAttribute(src,i));
   verts.push(worldPos.x,worldPos.y,worldPos.z);sourceIDs.push(i);
 }
 const g=new THREE.BufferGeometry();
 g.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
 const points=new THREE.Points(g,new THREE.PointsMaterial({
   color:0x5ff2fa,size:4,sizeAttenuation:false,depthTest:true,transparent:true,opacity:.68
 }));
 points.renderOrder=20;points.userData.sculptVertexIDs=sourceIDs;root.add(points);
 atelierSculptOverlay.userData.vertexPoints=points;
 const selected=atelierSculptVertexIDs.filter(i=>i>=0&&i<count).slice(0,128);
 if(selected.length){
   const expanded=atelierSculptExpandedIndices(mesh.geometry,selected);
   const marked=[];
   for(const i of expanded){
     const q=mesh.localToWorld(new THREE.Vector3().fromBufferAttribute(src,i));
     marked.push(q.x,q.y,q.z);
   }
   const mg=new THREE.BufferGeometry();
   mg.setAttribute('position',new THREE.Float32BufferAttribute(marked,3));
   const dots=new THREE.Points(mg,new THREE.PointsMaterial({
     color:0xffd14a,size:8,sizeAttenuation:false,depthTest:false
   }));
   dots.renderOrder=25;root.add(dots);
   const pivot=atelierSculptCentroid(mesh,expanded);
   const gizmo=new THREE.Group();
   gizmo.name='Sculpt drag gizmo';
   const axes=new THREE.AxesHelper(.16);gizmo.add(axes);
   const handle=new THREE.Mesh(new THREE.SphereGeometry(.026,12,8),
     new THREE.MeshBasicMaterial({color:0xffd14a,depthTest:false}));
   handle.renderOrder=30;gizmo.add(handle);
   gizmo.position.copy(pivot);if(typeof atelierViewportGizmoDecorate==='function')atelierViewportGizmoDecorate(gizmo);root.add(gizmo);atelierSculptGizmo=gizmo;
 }
 const hint=$m('SculptBrushVertexInfo');
 if(hint){
   hint.textContent=count+' source vertices, '+sourceIDs.length+
     ' displayed; '+selected.length+' points selected. Tap dots to select; drag yellow gizmo to move.';
   if(atelierSculptGizmo){
     const projected=atelierSculptGizmo.position.clone().project(camera);
     const rect=renderer.domElement.getBoundingClientRect();
     hint.dataset.gizmoX=String(rect.left+(projected.x+1)*rect.width/2);
     hint.dataset.gizmoY=String(rect.top+(1-projected.y)*rect.height/2);
   }else{
     delete hint.dataset.gizmoX;delete hint.dataset.gizmoY;
   }
 }
}
// Keep selected vertex gizmos outside the floating render toolbar on mobile.
function atelierSculptAutoFrameGizmo(){
 if(!atelierSculptGizmo||!camera||!renderer)return false;
 const bar=$m('ViewportModes');
 if(!bar)return false;
 const canvas=renderer.domElement.getBoundingClientRect();
 const bounds=bar.getBoundingClientRect();
 const projected=atelierSculptGizmo.position.clone().project(camera);
 const x=canvas.left+(projected.x+1)*canvas.width/2;
 const y=canvas.top+(1-projected.y)*canvas.height/2;
 const minimum=Math.max(canvas.top+35,bounds.bottom+42);
 if(!Number.isFinite(x)||!Number.isFinite(y)||y>=minimum||minimum>canvas.bottom-90)return false;
 atelierCameraPanByPixels(0,Math.min(180,minimum-y+6));
 return true;
}
function atelierSculptEnsureGizmoTouchable(){
 for(let attempt=0;attempt<4;attempt++){
   if(!atelierSculptAutoFrameGizmo())break;
   atelierSculptOverlayRefresh();
 }
}
function atelierSculptVertexPick(e){
 if(!atelierSculptVertexMode||!atelierSculptOverlay?.userData.vertexPoints)return false;
 const q=point(e);mouse.set(q.x,q.y);raycaster.setFromCamera(mouse,camera);
 raycaster.params.Points.threshold=.034;
 const hits=raycaster.intersectObject(atelierSculptOverlay.userData.vertexPoints,false);
 const id=hits[0]?.object?.userData?.sculptVertexIDs?.[hits[0].index];
 if(id===undefined){status('Tap one of the cyan mapped vertex points.',true);return true;}
 if(!$m('SculptBrushMulti').checked)atelierSculptVertexIDs=[id];
 else if(atelierSculptVertexIDs.includes(id))atelierSculptVertexIDs=atelierSculptVertexIDs.filter(x=>x!==id);
 else if(atelierSculptVertexIDs.length<128)atelierSculptVertexIDs.push(id);
 else {status('Select a maximum of 128 control points per group.',true);return true;}
 atelierSculptOverlayRefresh();
 atelierSculptEnsureGizmoTouchable();
 atelierSculptRefresh();
 return true;
}
function atelierSculptOnPointerDown(e){
 if(typeof atelierViewportGizmoPointerDown==='function'&&atelierViewportGizmoPointerDown(e))return true;
 if(typeof atelierViewportGizmoMode==='function'&&atelierViewportGizmoMode()!=='translate')return false;
 if(!atelierSculptVertexMode||!atelierSculptGizmo||!atelierSculptOverlayMesh||e.button!==0)return false;
 const pos=point(e),projected=atelierSculptGizmo.position.clone().project(camera);
 const r=renderer.domElement.getBoundingClientRect();
 const px=(projected.x-pos.x)*r.width/2,py=(projected.y-pos.y)*r.height/2;
 if(Math.hypot(px,py)>25)return false;
 const mesh=atelierSculptOverlayMesh;
 const indices=atelierSculptExpandedIndices(mesh.geometry,atelierSculptVertexIDs);
 if(!indices.length)return false;
 const plane=new THREE.Plane().setFromNormalAndCoplanarPoint(
   camera.getWorldDirection(new THREE.Vector3()),atelierSculptGizmo.position);
 const startRay=raycaster;mouse.set(pos.x,pos.y);startRay.setFromCamera(mouse,camera);
 const hit=startRay.ray.intersectPlane(plane,new THREE.Vector3());
 if(!hit)return false;
 const p=mesh.geometry.attributes.position,base=indices.map(i=>[p.getX(i),p.getY(i),p.getZ(i)]);
 atelierSculptDrag={mesh,indices,base,plane,hit,origin:atelierSculptGizmo.position.clone(),
   delta:[0,0,0],partId:selection};
 renderer.domElement.setPointerCapture?.(e.pointerId);
 return true;
}
function atelierSculptOnPointerMove(e){
 if(typeof atelierViewportGizmoPointerMove==='function'&&atelierViewportGizmoPointerMove(e))return true;
 const drag=atelierSculptDrag;if(!drag)return false;
 const q=point(e);mouse.set(q.x,q.y);raycaster.setFromCamera(mouse,camera);
 const to=raycaster.ray.intersectPlane(drag.plane,new THREE.Vector3());
 if(!to)return true;
 const worldDelta=to.sub(drag.hit),inverse=drag.mesh.matrixWorld.clone().invert();
 const zero=new THREE.Vector3(0,0,0).applyMatrix4(inverse);
 const local=worldDelta.clone().applyMatrix4(inverse).sub(zero);
 const axis=$m('SculptBrushVertexAxis').value;
 if(axis!=='free'){
   const n=axis==='x'?0:axis==='y'?1:2;
   for(let i=0;i<3;i++)if(i!==n)local.setComponent(i,0);
 }
 const snap=Number($m('SculptBrushSnap').value);
 const delta=[0,1,2].map(i=>atelierSculptClamp(snap>0?
    Math.round(local.getComponent(i)/snap)*snap:local.getComponent(i),-.5,.5));
 drag.delta=delta;
 const pos=drag.mesh.geometry.attributes.position;
 for(let i=0;i<drag.indices.length;i++){
   const b=drag.base[i];
   pos.setXYZ(drag.indices[i],b[0]+delta[0],b[1]+delta[1],b[2]+delta[2]);
 }
 pos.needsUpdate=true;drag.mesh.geometry.computeVertexNormals();
 drag.mesh.geometry.computeBoundingSphere();
 drag.mesh.geometry.computeBoundingBox();
 const pivotLocal=drag.mesh.worldToLocal(drag.origin.clone()).add(new THREE.Vector3(...delta));
 atelierSculptGizmo.position.copy(drag.mesh.localToWorld(pivotLocal));
 return true;
}
function atelierSculptOnPointerUp(e){
 if(typeof atelierViewportGizmoPointerUp==='function'&&atelierViewportGizmoPointerUp(e))return true;
 const drag=atelierSculptDrag;if(!drag)return false;
 atelierSculptDrag=null;
 const p=partById(drag.partId),delta=drag.delta;
 if(!p||!delta.some(x=>Math.abs(x)>1e-7)){
   renderParts();return true;
 }
 if((p.sculptVertexEdits?.length||0)>=atelierSculptMaxVertexEdits){
   status('Vertex edit history full; remove edits or export JSON.',true);
   renderParts();return true;
 }
 const edit={indices:drag.indices,delta,resolution:atelierSculptResolution(p)};
 const next={...p,sculptVertexEdits:[...(p.sculptVertexEdits||[]),edit]};
 if(!checkPart(next)){status('Vertex move rejected.',true);renderParts();return true;}
 checkpoint();p.sculptVertexEdits=next.sculptVertexEdits;
 const id=p.id;signalEdited();select(id);
 status('Saved '+drag.indices.length+' moved vertices. Gizmo edit retained in native JSON and OBJ export.');
 return true;
}
function atelierSculptVertexResolutionApply(){
 const p=partById(selection);
 if(!p||!['sphere','loft'].includes(p.kind)){status('Sampling grid supported on sphere and loft meshes.',true);return;}
 const u=Number($m('SculptBrushGridU').value),v=Number($m('SculptBrushGridV').value);
 if(!Number.isInteger(u)||!Number.isInteger(v)||u<16||u>256||v<12||v>192||u*v>42000){
   status('Grid count requires U 16–256, V 12–192, and ≤42,000 samples.',true);return;
 }
 const next={...p,meshDensity:{u,v},sculptVertexEdits:undefined};
 if(!checkPart(next)){status('Sampling grid rejected by native mesh validation.',true);return;}
 checkpoint();p.meshDensity={u,v};
 delete p.sculptVertexEdits;
 atelierSculptVertexIDs=[];const id=p.id;signalEdited();select(id);
 status('Vertex map re-sampled to '+u+' × '+v+'. Old indexed vertex edits were cleared; radial brush strokes remain.');
}
function atelierSculptVertexInstall(){
 $m('SculptBrushIndicesApply').addEventListener('click',()=>{
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   if(!mesh){status('Select a mesh before choosing vertex indices.',true);return;}
   const raw=String($m('SculptBrushIndices').value).trim();
   if(!/^\d+(?:\s*,\s*\d+)*$/.test(raw)){status('Enter 1–128 comma-separated vertex indices.',true);return;}
   const ids=[...new Set(raw.split(',').map(x=>Number(x.trim())))];
   if(ids.length<1||ids.length>128||ids.some(i=>i<0||i>=mesh.geometry.attributes.position.count)){
     status('Vertex indices must exist in the currently sampled mesh (up to 128).',true);return;
   }
   atelierSculptVertexMode=true;
   atelierSculptVertexIDs=ids;
   atelierSculptLastVertexPart=selection;
   $m('SculptBrushVertexToggle').textContent='Hide vertex map';
   atelierSculptOverlayRefresh();
   atelierSculptEnsureGizmoTouchable();
   atelierSculptRefresh();
   status('Mapped and selected '+ids.length+' control points. The gizmo is framed below the camera toolbar for touch/drag.');
 });
 $m('SculptBrushVertexToggle').addEventListener('click',()=>{
   atelierSculptVertexMode=!atelierSculptVertexMode;
   atelierSculptVertexIDs=[];
   $m('SculptBrushVertexToggle').textContent=atelierSculptVertexMode?'Hide vertex map':'Show vertex map';
   atelierSculptOverlayRefresh();atelierSculptRefresh();
 });
 $m('SculptBrushVertexClear').addEventListener('click',()=>{
   atelierSculptVertexIDs=[];atelierSculptOverlayRefresh();atelierSculptRefresh();
 });
 $m('SculptBrushGridApply').addEventListener('click',atelierSculptVertexResolutionApply);
 $m('SculptBrushVertexUndo').addEventListener('click',()=>{
   const p=partById(selection);if(!p?.sculptVertexEdits?.length)return;
   checkpoint();p.sculptVertexEdits=p.sculptVertexEdits.slice(0,-1);
   const id=p.id;signalEdited();select(id);
   status('Last vertex-group move removed. Undo can restore it.');
 });
}
