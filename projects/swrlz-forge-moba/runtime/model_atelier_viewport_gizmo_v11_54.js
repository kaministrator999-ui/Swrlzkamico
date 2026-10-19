// §E v11.54: touch-accessible viewport rotation/scale handles.
// Extends native grouped vertex records, reuses atelierGroupEdit's exact
// world/object/surface-space evaluation, and never edits base data mid-drag.
let atelierViewportGizmoDrag=null;
const atelierViewportGizmoMode=()=>$m('GroupViewportMode')?.value||'translate';
function atelierViewportGizmoDelta(mode,axis,pivot,start,end,snapDegrees=0){
 if(!['rotate','scale'].includes(mode)||!['x','y','z'].includes(axis)||
    !Array.isArray(pivot)||!Array.isArray(start)||!Array.isArray(end)||
    [...pivot,...start,...end,snapDegrees].some(v=>!Number.isFinite(v))||
    snapDegrees<0||snapDegrees>45)return null;
 const offset=[start[0]-pivot[0],start[1]-pivot[1]],
   moved=[end[0]-pivot[0],end[1]-pivot[1]];
 const a=Math.hypot(...offset),d=Math.hypot(...moved);
 if(a<9||d<2)return null;
 const key={x:0,y:1,z:2}[axis];
 if(mode==='rotate'){
  const cross=offset[0]*moved[1]-offset[1]*moved[0];
  const dot=offset[0]*moved[0]+offset[1]*moved[1];
  let degrees=THREE.MathUtils.radToDeg(Math.atan2(cross,dot));
  if(snapDegrees)degrees=Math.round(degrees/snapDegrees)*snapDegrees;
  const vec=[0,0,0];vec[key]=Math.max(-180,Math.min(180,degrees));
  return vec;
 }
 const scale=Math.max(.1,Math.min(3,d/a)),vec=[1,1,1];vec[key]=scale;
 return vec;
}
function atelierViewportGizmoDecorate(group){
 const mode=atelierViewportGizmoMode();
 if(mode==='rotate'){
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.16,.012,8,48),
   new THREE.MeshBasicMaterial({color:0xffaa40,depthTest:false,transparent:true,opacity:.95}));
  ring.quaternion.copy(camera.quaternion);
  ring.renderOrder=32;ring.userData.atelierHelper=true;group.add(ring);
 }else if(mode==='scale'){
  const handle=new THREE.Mesh(new THREE.BoxGeometry(.055,.055,.055),
   new THREE.MeshBasicMaterial({color:0xffaa40,depthTest:false}));
  handle.position.set(.16,0,0);handle.renderOrder=32;
  handle.userData.atelierHelper=true;group.add(handle);
 }
}
function atelierViewportGizmoPointerDown(e){
 const mode=atelierViewportGizmoMode();
 if(mode==='translate'||e.button!==0||!atelierSculptVertexMode||
    !atelierSculptGizmo||!atelierSculptOverlayMesh)return false;
 const p=partById(selection);
 if(!p||p.refinementLayers?.some(l=>l.enabled)){
  status('Disable refinement layers before editing source vertex handles.',true);return true;
 }
 const mesh=atelierSculptOverlayMesh,indices=atelierSculptExpandedIndices(mesh.geometry,atelierSculptVertexIDs);
 if(!indices.length||indices.length>256){status('Rotate/scale supports 1–256 selected native vertices.',true);return true;}
 const rect=renderer.domElement.getBoundingClientRect();
 const proj=atelierSculptGizmo.position.clone().project(camera);
 const pivot=[rect.left+(proj.x+1)*rect.width*.5,rect.top+(1-proj.y)*rect.height*.5];
 const start=[e.clientX,e.clientY];
 const radial=Math.hypot(start[0]-pivot[0],start[1]-pivot[1]);
 if(radial>54||radial<9)return false;
 const g=mesh.geometry.attributes.position;
 atelierViewportGizmoDrag={
  mode,axis:$m('GroupViewportAxis').value,space:$m('GroupSpace').value,
  partId:selection,mesh,indices,pivot,start,pointerId:e.pointerId,moves:null,
  original:indices.map(i=>[g.getX(i),g.getY(i),g.getZ(i)])
 };
 renderer.domElement.setPointerCapture?.(e.pointerId);
 return true;
}
function atelierViewportGizmoPointerMove(e){
 const d=atelierViewportGizmoDrag;if(!d||e.pointerId!==d.pointerId)return false;
 const pos=d.mesh.geometry.attributes.position;
 // Prevent incremental drift: restore base before evaluating each frame.
 for(let i=0;i<d.indices.length;i++)pos.setXYZ(d.indices[i],...d.original[i]);
 const vec=atelierViewportGizmoDelta(d.mode,d.axis,d.pivot,d.start,
  [e.clientX,e.clientY],Number($m('GroupViewportAngleSnap').value));
 const candidate=vec?atelierGroupEdit(d.mesh,d.indices,d.mode,d.space,vec,
  Number($m('SculptBrushSnap').value)):null;
 d.moves=candidate?.moves||null;
 if(candidate)for(let i=0;i<d.indices.length;i++){
  const p=d.original[i],move=candidate.moves[i];
  pos.setXYZ(d.indices[i],p[0]+move[0],p[1]+move[1],p[2]+move[2]);
 }
 pos.needsUpdate=true;d.mesh.geometry.computeVertexNormals();
 d.mesh.geometry.computeBoundingSphere();d.mesh.geometry.computeBoundingBox();
 return true;
}
function atelierViewportGizmoPointerUp(e){
 const d=atelierViewportGizmoDrag;if(!d||e?.pointerId!==d.pointerId)return false;
 atelierViewportGizmoDrag=null;
 const p=partById(d.partId);
 if(!p||!d.moves||d.moves.every(m=>m.every(v=>Math.abs(v)<1e-7))){
  renderParts();return true;
 }
 const record={indices:d.indices,moves:d.moves,resolution:atelierSculptResolution(p)};
 const next={...p,sculptVertexEdits:[...(p.sculptVertexEdits||[]),record]};
 if(!checkPart(next)){renderParts();status('Viewport gizmo transform exceeds native edit bounds.',true);return true;}
 checkpoint();p.sculptVertexEdits=next.sculptVertexEdits;
 const partId=p.id;signalEdited();select(partId);
 status('Saved '+d.mode+' on '+d.indices.length+' native vertices in '+d.space+
  ' space. Undo/JSON/OBJ retain it.');
 return true;
}
function atelierViewportGizmoCancel(){
 if(!atelierViewportGizmoDrag)return false;
 atelierViewportGizmoDrag=null;renderParts();return true;
}
function atelierViewportGizmoInstall(){
 for(const id of ['GroupViewportMode','GroupViewportAxis']){
  $m(id)?.addEventListener('change',()=>{atelierSculptOverlayRefresh();atelierSculptEnsureGizmoTouchable();});
 }
}
