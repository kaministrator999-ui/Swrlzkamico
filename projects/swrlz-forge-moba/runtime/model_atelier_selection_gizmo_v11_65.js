// §E v11.65 — selection-first mesh transform controls.
// All edits use native part transforms and checkpoint(); vertex points reuse native overlay.
let atelierMeshIds=[],atelierMeshAdding=false,atelierMeshMode='move',atelierMeshAxis='x';
let atelierMeshStrip=null,atelierMeshPivot=null,atelierMeshGizmo=null,atelierMeshDrag=null;
let atelierMeshDensityOpen=false,atelierMeshHidden=false,atelierMeshDensityShownPart=null;
const atelierMeshAxes={x:[1,0,0],y:[0,1,0],z:[0,0,1]};
const atelierMeshClamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));
const atelierMeshFinite=a=>a.every(Number.isFinite);
function atelierMeshSelected(id){
 if(!id){atelierMeshIds=[];atelierMeshAdding=false;return;}
 if(!atelierMeshAdding){atelierMeshIds=[id];return;}
 if(atelierMeshIds.includes(id))atelierMeshIds=atelierMeshIds.filter(x=>x!==id);
 else if(atelierMeshIds.length<32)atelierMeshIds.push(id);
 else status('Group limit: 32 meshes.',true);
 if(!atelierMeshIds.length)atelierMeshIds=[id];
}
function atelierMeshActiveIds(){
 const valid=new Set(model()?.parts.map(p=>p.id)||[]);
 atelierMeshIds=atelierMeshIds.filter(id=>valid.has(id));
 if(!atelierMeshIds.length&&partById(selection))atelierMeshIds=[selection];
 return atelierMeshIds;
}
function atelierMeshSelectedMeshes(){
 const ids=new Set(atelierMeshActiveIds());
 return (modelRoot?.children||[]).filter(o=>o.isMesh&&ids.has(o.userData.atelierId));
}
function atelierMeshCenter(meshes){
 if(!meshes.length)return null;
 const box=new THREE.Box3();
 for(const mesh of meshes){mesh.updateMatrixWorld(true);box.expandByObject(mesh);}
 return box.isEmpty()?null:box.getCenter(new THREE.Vector3());
}
function atelierMeshGizmoClear(){
 if(!atelierMeshGizmo)return;
 atelierMeshGizmo.parent?.remove(atelierMeshGizmo);
 atelierMeshGizmo.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 atelierMeshGizmo=null;
}
function atelierMeshGizmoBuild(){
 atelierMeshGizmoClear();
 if(!world||!modelRoot||!camera||!partById(selection))return;
 const meshes=atelierMeshSelectedMeshes(),pivot=atelierMeshCenter(meshes);
 if(!pivot)return;
 atelierMeshPivot=pivot;
 const root=new THREE.Group();root.position.copy(pivot);root.name='Selected mesh transforms';
 const span=atelierMeshClamp(orbit.distance*.065,.24,1.0);
 for(const [axis,color] of [['x',0xff666b],['y',0x6cf2a8],['z',0x6baaff]]){
  const direction=new THREE.Vector3(...atelierMeshAxes[axis]);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.009,.009,span*.8,8),
      new THREE.MeshBasicMaterial({color,depthTest:false,transparent:true,opacity:.95}));
  stem.position.copy(direction.clone().multiplyScalar(span*.48));
  stem.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction);
  stem.renderOrder=35;stem.userData.atelierHelper=true;root.add(stem);
  const handle=new THREE.Mesh(new THREE.SphereGeometry(Math.max(.07,span*.15),12,10),
      new THREE.MeshBasicMaterial({color,depthTest:false}));
  handle.position.copy(direction.clone().multiplyScalar(span));
  handle.userData.meshGizmoAxis=axis;handle.userData.atelierHelper=true;handle.renderOrder=38;
  root.add(handle);
 }
 if(atelierMeshMode==='scale'){
  const h=new THREE.Mesh(new THREE.BoxGeometry(span*.19,span*.19,span*.19),
      new THREE.MeshBasicMaterial({color:0xffd67e,depthTest:false}));
  h.userData.meshGizmoAxis='all';h.userData.atelierHelper=true;h.renderOrder=39;root.add(h);
 }
 world.add(root);
 atelierMeshGizmo=root;
 for(const mesh of meshes){
  const outline=new THREE.BoxHelper(mesh,0xf3cf86);
  outline.userData.atelierHelper=true;outline.material.depthTest=false;
  outline.renderOrder=32;root.add(outline);
  // BoxHelper is built in world coordinates, but this root is at pivot.
  outline.position.sub(pivot);
 }
}
function atelierMeshToolbarPosition(){
 if(!atelierMeshStrip||atelierMeshStrip.hidden||!atelierMeshPivot||!camera||!stage)return;
 const projection=atelierMeshPivot.clone().project(camera);
 if(!atelierMeshFinite([projection.x,projection.y,projection.z])||projection.z>=1){
  atelierMeshStrip.style.visibility='hidden';return;
 }
 atelierMeshStrip.style.visibility='visible';
 const width=stage.clientWidth,height=stage.clientHeight;
 const x=(projection.x+1)*width/2+18, y=(1-projection.y)*height/2+22;
 const w=atelierMeshStrip.offsetWidth||290,h=atelierMeshStrip.offsetHeight||130;
 atelierMeshStrip.style.left=Math.round(atelierMeshClamp(x,5,Math.max(5,width-w-6)))+'px';
 atelierMeshStrip.style.top=Math.round(atelierMeshClamp(y,50,Math.max(50,height-h-8)))+'px';
}
function atelierMeshToolbarRefresh(){
 if(!atelierMeshStrip)return;
 const ids=atelierMeshActiveIds(),part=partById(selection),active=!!part&&!!modelRoot;
 atelierMeshStrip.hidden=!active||atelierMeshHidden;
 const name=atelierMeshStrip.querySelector('[data-mesh-name]');
 if(name)name.textContent=(ids.length>1?ids.length+' meshes grouped · ':'')+(part?.name||'');
 for(const b of atelierMeshStrip.querySelectorAll('[data-mode]'))b.setAttribute('aria-pressed',String(atelierMeshMode===b.dataset.mode));
 for(const b of atelierMeshStrip.querySelectorAll('[data-axis]'))b.setAttribute('aria-pressed',String(atelierMeshAxis===b.dataset.axis));
 const add=atelierMeshStrip.querySelector('[data-mesh-group]');
 if(add){add.setAttribute('aria-pressed',String(atelierMeshAdding));add.textContent=atelierMeshAdding?'✓ Finish group':'＋ Add mesh';}
 const join=atelierMeshStrip.querySelector('[data-mesh-join]');
 if(join)join.disabled=ids.length<2;
 const toggle=atelierMeshStrip.querySelector('[data-mesh-vertices]');
 if(toggle){toggle.setAttribute('aria-pressed',String(atelierSculptVertexMode));toggle.textContent=atelierSculptVertexMode?'● Hide vertices':'● Show vertices';}
 const density=atelierMeshStrip.querySelector('[data-mesh-density]');
 if(density)density.hidden=!atelierMeshDensityOpen;
 if(active){
  const g=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
  const count=g?.geometry?.attributes?.position?.count||0;
  const note=atelierMeshStrip.querySelector('[data-mesh-count]');
  if(note)note.textContent=count.toLocaleString()+' real vertex slots';
  if(density){
   const eligible=['sphere','loft','faceSheet','box','cone','cylinder'].includes(part.kind);
   density.querySelector('fieldset').disabled=!eligible;
   const u=density.querySelector('[data-mesh-u]'),v=density.querySelector('[data-mesh-v]');
   const fallback=part.kind==='faceSheet'?[part.faceSheet?.gridU||48,part.faceSheet?.gridV||20]:
     ['box','cone','cylinder'].includes(part.kind)?[16,12]:[64,48];
   if(atelierMeshDensityShownPart!==selection){
    u.value=String(part.meshDensity?.u||fallback[0]);
    v.value=String(part.meshDensity?.v||fallback[1]);
    atelierMeshDensityShownPart=selection;
   }
   density.querySelector('[data-mesh-density-note]').textContent=eligible?
     'U/V change actual mesh points. Applying clears indexed vertex edits. Undo available.':
     'Custom topology: use native Topology refinement; uniform U/V resampling is unavailable.';
  }
 }
 atelierMeshGizmoBuild();
 atelierMeshToolbarPosition();
}
function atelierMeshPrimitiveDensityGeometry(part){
 const d=part.meshDensity;if(!d||!['box','cone','cylinder'].includes(part.kind))return null;
 const {u,v}=d;
 if(!Number.isInteger(u)||!Number.isInteger(v)||u<4||u>64||v<2||v>64||u*v>2048)return null;
 if(part.kind==='box')return new THREE.BoxGeometry(1,1,1,u,v,u);
 if(part.kind==='cone')return new THREE.ConeGeometry(.5,1,u,v);
 return new THREE.CylinderGeometry(.5,.5,1,u,v);
}
function atelierMeshPrimitiveDensityValid(part){
 if(!['box','cone','cylinder'].includes(part.kind)||part.meshDensity===undefined)return true;
 const d=part.meshDensity;
 return !!d&&!Array.isArray(d)&&Object.keys(d).sort().join('|')==='u|v'&&
  Number.isInteger(d.u)&&Number.isInteger(d.v)&&d.u>=4&&d.u<=64&&d.v>=2&&d.v<=64&&d.u*d.v<=2048;
}
function atelierMeshSetDensity(deltaU=0,deltaV=0,apply=false){
 const p=partById(selection);
 if(!p)return;
 const box=atelierMeshStrip.querySelector('[data-mesh-density]');
 const ui=box.querySelector('[data-mesh-u]'),vi=box.querySelector('[data-mesh-v]');
 const u=Number(ui.value)+deltaU,v=Number(vi.value)+deltaV;
 const native=['sphere','loft'].includes(p.kind),face=p.kind==='faceSheet';
 const minU=native?16:face?8:4,maxU=native?256:face?128:64;
 const minV=native?12:face?4:2,maxV=native?192:face?128:64;
 const cap=native?42000:face?16384:2048;
 if(!Number.isInteger(u)||!Number.isInteger(v)||u<minU||u>maxU||v<minV||v>maxV||u*v>cap){
  status('Grid bounds: U '+minU+'–'+maxU+', V '+minV+'–'+maxV+', budget '+cap+'.',true);return;
 }
 ui.value=String(u);vi.value=String(v);
 if(!apply)return;
 if(p.sculptVertexEdits?.length&&!confirm('Resampling clears source-indexed vertex edits. Continue?'))return;
 if(native){
  $m('SculptBrushGridU').value=u;$m('SculptBrushGridV').value=v;
  atelierSculptVertexResolutionApply();
 }else if(face){
  $m('FaceSheetGridU').value=u;$m('FaceSheetGridV').value=v;
  $m('FaceSheetApply').click();
 }else{
  const next={...p,meshDensity:{u,v},sculptVertexEdits:undefined};
  if(!checkPart(next)){status('Native mesh validation rejected this density.',true);return;}
  const g=atelierMeshPrimitiveDensityGeometry(next);
  if(!g){status('Cannot create that mesh grid.',true);return;}
  g.dispose();
  checkpoint();p.meshDensity={u,v};delete p.sculptVertexEdits;
  const id=p.id;signalEdited();select(id);
 }
 atelierMeshToolbarRefresh();
 status('Mesh U/V grid updated. Real vertices regenerated; use Undo to restore the previous mesh.');
}
function atelierMeshSnapshots(){
 return atelierMeshActiveIds().map(id=>partById(id)).filter(Boolean).map(p=>({
  id:p.id,position:[...p.position],rotation:[...p.rotation],scale:[...p.scale]
 }));
}
function atelierMeshCandidates(snapshot,pivot,mode,axis,amount){
 const axisIndex={x:0,y:1,z:2}[axis],q=mode==='rotate'?
   new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(...atelierMeshAxes[axis]),amount):null;
 return snapshot.map(before=>{
  const pos=new THREE.Vector3(...before.position),rot=new THREE.Euler(...before.rotation,'XYZ'),scale=[...before.scale];
  if(mode==='move')pos.setComponent(axisIndex,pos.getComponent(axisIndex)+amount);
  if(mode==='rotate'){
   pos.sub(pivot).applyQuaternion(q).add(pivot);
   rot.setFromQuaternion(q.multiply(new THREE.Quaternion().setFromEuler(rot)),'XYZ');
   // Avoid mutating shared axis quaternion for subsequent grouped objects.
   q.setFromAxisAngle(new THREE.Vector3(...atelierMeshAxes[axis]),amount);
  }
  if(mode==='scale'){
   const ax=axis==='all'?[0,1,2]:[axisIndex];
   for(const a of ax){scale[a]*=amount;pos.setComponent(a,pivot.getComponent(a)+(pos.getComponent(a)-pivot.getComponent(a))*amount);}
  }
  return {id:before.id,position:pos.toArray(),rotation:[rot.x,rot.y,rot.z],scale};
 });
}
function atelierMeshCommit(snap,pivot,mode,axis,amount){
 if(!snap.length||!Number.isFinite(amount)||mode==='scale'&&amount<=0)return false;
 if(!['move','rotate','scale'].includes(mode)||!(axis in atelierMeshAxes||axis==='all'&&mode==='scale'))return false;
 const next=atelierMeshCandidates(snap,pivot,mode,axis,amount);
 if(next.some(t=>{const p=partById(t.id);return !p||!checkPart({...p,...t});})){
  status('Transform exceeds valid native position/rotation/scale bounds.',true);renderParts();return false;
 }
 if(next.every((t,i)=>['position','rotation','scale'].every(k=>t[k].every((v,j)=>Math.abs(v-snap[i][k][j])<1e-7))))return false;
 checkpoint();
 for(const t of next){const p=partById(t.id);p.position=t.position;p.rotation=t.rotation;p.scale=t.scale;}
 signalEdited();atelierMeshToolbarRefresh();
 status('Saved '+next.length+' mesh '+mode+' transform(s). Undo/JSON/OBJ supported.');
 return true;
}
function atelierMeshNudge(direction){
 const snap=atelierMeshSnapshots(),pivot=atelierMeshCenter(atelierMeshSelectedMeshes());
 if(!snap.length||!pivot)return;
 const amount=atelierMeshMode==='move'?direction*.1:
  atelierMeshMode==='rotate'?direction*Math.PI/36:Math.pow(1.1,direction);
 atelierMeshCommit(snap,pivot,atelierMeshMode,atelierMeshAxis,amount);
}
function atelierMeshGizmoDown(e){
 if(atelierMeshDrag)return true;
 if(e.button!==0||!atelierMeshGizmo||!renderer||!atelierMeshActiveIds().length)return false;
 const q=point(e);mouse.set(q.x,q.y);raycaster.setFromCamera(mouse,camera);
 const handles=atelierMeshGizmo.children.filter(x=>x.userData.meshGizmoAxis);
 const hit=raycaster.intersectObjects(handles,false)[0];
 if(!hit)return false;
 const axis=hit.object.userData.meshGizmoAxis;
 const snap=atelierMeshSnapshots();
 if(!snap.length)return false;
 atelierMeshAxis=axis;
 const pivot=atelierMeshPivot.clone(),p0=pivot.clone().project(camera),tip=pivot.clone().add(
  new THREE.Vector3(...(atelierMeshAxes[axis]||[1,1,0])).multiplyScalar(.5)).project(camera);
 const rect=renderer.domElement.getBoundingClientRect();
 const dir=new THREE.Vector2((tip.x-p0.x)*rect.width/2,-(tip.y-p0.y)*rect.height/2);
 if(dir.lengthSq()<16)dir.set(1,0);else dir.normalize();
 atelierMeshDrag={pointerId:e.pointerId,startX:e.clientX,startY:e.clientY,axis,pivot,mode:atelierMeshMode,
  direction:dir,snapshot:snap,amount:atelierMeshMode==='scale'?1:0};
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;atelierMeshToolbarRefresh();
 return true;
}
function atelierMeshGizmoMove(e){
 const d=atelierMeshDrag;if(!d||e.pointerId!==d.pointerId)return false;
 const pixels=(e.clientX-d.startX)*d.direction.x+(e.clientY-d.startY)*d.direction.y;
 const amount=d.mode==='move'?atelierMeshClamp(pixels*.007*orbit.distance,-25,25):
  d.mode==='rotate'?atelierMeshClamp(pixels*.009,-Math.PI,Math.PI):
  atelierMeshClamp(Math.exp(pixels*.009),.1,3);
 d.amount=amount;
 const values=atelierMeshCandidates(d.snapshot,d.pivot,d.mode,d.axis,amount);
 for(const t of values){
  const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===t.id);
  if(!mesh)continue;
  mesh.position.set(...t.position);mesh.rotation.set(...t.rotation);mesh.scale.set(...t.scale);
 }
 return true;
}
function atelierMeshGizmoUp(e){
 const d=atelierMeshDrag;if(!d||e.pointerId!==d.pointerId)return false;
 atelierMeshDrag=null;
 if(Math.abs(d.mode==='scale'?d.amount-1:d.amount)<1e-6){renderParts();return true;}
 atelierMeshCommit(d.snapshot,d.pivot,d.mode,d.axis,d.amount);
 return true;
}
function atelierMeshGizmoCancel(){
 if(!atelierMeshDrag)return false;
 atelierMeshDrag=null;renderParts();return true;
}
function atelierMeshJoin(){
 const ids=atelierMeshActiveIds();if(ids.length<2)return;
 if(!confirm('Join '+ids.length+' meshes as ONE editable topology mesh? Original parts and individual materials become one mesh. Undo can restore them.'))return;
 const chosen=atelierMeshSelectedMeshes();if(chosen.length!==ids.length){status('Not all selected meshes are rendered.',true);return;}
 const pivot=atelierMeshCenter(chosen),positions=[],uvs=[],indices=[];
 let base=0;
 for(const mesh of chosen){
  mesh.updateMatrixWorld(true);
  const g=mesh.geometry,pos=g.getAttribute('position'),uv=g.getAttribute('uv'),idx=g.getIndex();
  const triangles=(idx?.count||pos.count)/3;
  if(!Number.isInteger(triangles)||base+pos.count>9000||indices.length+triangles*3>48000){
   status('Join exceeds safe 9,000 vertex / 16,000 triangle topology budget. Group transforms remain available.',true);return;
  }
  for(let j=0;j<pos.count;j++){
   const v=new THREE.Vector3().fromBufferAttribute(pos,j).applyMatrix4(mesh.matrixWorld).sub(pivot);
   positions.push(...v.toArray());uvs.push(uv?uv.getX(j):0,uv?uv.getY(j):0);
  }
  for(let j=0;j<triangles*3;j++)indices.push(base+(idx?idx.getX(j):j));
  base+=pos.count;
 }
 const parent=partById(ids[0]);
 const merged={id:'atelier-join-'+Date.now().toString(36),name:'Joined · '+ids.length+' meshes',
  group:'Custom',kind:'topologyMesh',position:pivot.toArray(),rotation:[0,0,0],scale:[1,1,1],
  color:parent.color,material:parent.material,topologyMesh:{positions,uvs,indices}};
 if(!checkPart(merged)){status('Join failed topology or native validation. No edits made.',true);return;}
 checkpoint();
 model().parts=model().parts.filter(p=>!ids.includes(p.id));
 model().parts.push(merged);
 atelierMeshAdding=false;atelierMeshIds=[merged.id];selection=merged.id;
 signalEdited();select(merged.id);
 status('Joined '+ids.length+' meshes into one editable topology mesh. Undo restores originals.');
}
function atelierMeshControlsInstall(panel){
 if(panel.dataset.meshToolsInstalled==='1')return;
 const viewport=panel.querySelector('#modelAtelierViewport');
 if(!viewport)return;
 panel.dataset.meshToolsInstalled='1';
 const strip=document.createElement('div');
 strip.id='modelAtelierMeshQuickStrip';strip.className='atelier-mesh-quickstrip';strip.hidden=true;
 strip.setAttribute('role','group');strip.setAttribute('aria-label','Selected mesh transform and vertex controls');
 strip.innerHTML=
  '<div class="amq-head"><strong>✣ Mesh tools</strong><span data-mesh-name></span><button type="button" data-mesh-hide aria-label="Hide floating mesh controls">×</button></div>'+
  '<div class="amq-line"><button type="button" data-mode="move">↔ Move</button><button type="button" data-mode="rotate">⟳ Rotate</button><button type="button" data-mode="scale">⤢ Scale</button></div>'+
  '<div class="amq-line"><button type="button" data-axis="x">X</button><button type="button" data-axis="y">Y</button><button type="button" data-axis="z">Z</button><button type="button" data-mesh-minus aria-label="Decrease selected axis transform">−</button><button type="button" data-mesh-plus aria-label="Increase selected axis transform">＋</button></div>'+
  '<div class="amq-line"><button type="button" data-mesh-group>＋ Add mesh</button><button type="button" data-mesh-join>Join selected</button></div>'+
  '<div class="amq-line"><button type="button" data-mesh-vertices>● Show vertices</button><button type="button" data-mesh-density-toggle>▦ Grid U/V</button></div>'+
  '<div class="amq-count" data-mesh-count></div>'+
  '<div data-mesh-density hidden><fieldset><legend>Actual vertex grid density</legend>'+
  '<label>U / columns <input type="number" data-mesh-u step="1" min="2" max="256"></label>'+
  '<label>V / rows <input type="number" data-mesh-v step="1" min="2" max="192"></label>'+
  '<div class="amq-line"><button type="button" data-mesh-u-minus>U−</button><button type="button" data-mesh-u-plus>U＋</button>'+
  '<button type="button" data-mesh-v-minus>V−</button><button type="button" data-mesh-v-plus>V＋</button>'+
  '<button type="button" data-mesh-apply>Apply</button></div></fieldset>'+
  '<small data-mesh-density-note></small></div>';
 viewport.append(strip);atelierMeshStrip=strip;
 const viewButtons=panel.querySelector('.atelier-viewport-controls');
 if(viewButtons){
  const open=document.createElement('button');open.type='button';open.id='modelAtelierMeshToolsOpen';
  open.textContent='✣ Mesh tools';open.addEventListener('click',()=>{
   atelierMeshHidden=false;atelierMeshToolbarRefresh();
   if(!partById(selection))status('Select a mesh in the viewport to open Mesh tools.');
  });viewButtons.append(open);
 }
 strip.addEventListener('pointerdown',e=>e.stopPropagation());
 strip.addEventListener('click',e=>{
  const btn=e.target.closest('button');if(!btn)return;
  if(btn.dataset.mode){atelierMeshMode=btn.dataset.mode;atelierMeshAxis='x';}
  else if(btn.dataset.axis){atelierMeshAxis=btn.dataset.axis;}
  else if(btn.hasAttribute('data-mesh-minus'))atelierMeshNudge(-1);
  else if(btn.hasAttribute('data-mesh-plus'))atelierMeshNudge(1);
  else if(btn.hasAttribute('data-mesh-group')){atelierMeshAdding=!atelierMeshAdding;status(atelierMeshAdding?'Tap additional meshes in the viewport to add/remove from group.':'Group selection finished.');}
  else if(btn.hasAttribute('data-mesh-join'))atelierMeshJoin();
  else if(btn.hasAttribute('data-mesh-vertices'))$m('SculptBrushVertexToggle')?.click();
  else if(btn.hasAttribute('data-mesh-density-toggle'))atelierMeshDensityOpen=!atelierMeshDensityOpen;
  else if(btn.hasAttribute('data-mesh-u-minus'))atelierMeshSetDensity(-1,0);
  else if(btn.hasAttribute('data-mesh-u-plus'))atelierMeshSetDensity(1,0);
  else if(btn.hasAttribute('data-mesh-v-minus'))atelierMeshSetDensity(0,-1);
  else if(btn.hasAttribute('data-mesh-v-plus'))atelierMeshSetDensity(0,1);
  else if(btn.hasAttribute('data-mesh-apply'))atelierMeshSetDensity(0,0,true);
  else if(btn.hasAttribute('data-mesh-hide'))atelierMeshHidden=true;
  atelierMeshToolbarRefresh();
 });
 // Native part-list multi-selection (desktop Ctrl/Shift, or mobile selection list).
 const list=$m('Parts');list.multiple=true;
 list.addEventListener('change',e=>{
  const ids=[...list.selectedOptions].map(o=>o.value).filter(partById);
  if(!ids.length)return;
  atelierMeshIds=ids.slice(0,32);selection=atelierMeshIds.at(-1);
  atelierMeshAdding=false;renderParts();refreshInspector();atelierMeshToolbarRefresh();
  e.stopImmediatePropagation();
 },true);
}
function atelierMeshListSync(list){
 const ids=new Set(atelierMeshActiveIds());
 for(const opt of list.options)opt.selected=ids.has(opt.value);
}
