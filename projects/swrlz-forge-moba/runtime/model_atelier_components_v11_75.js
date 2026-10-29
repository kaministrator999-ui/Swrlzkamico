// §E v11.75 — unified native component editing, mobile-first.
// Component edits are sparse sculptVertexEdits: existing native JSON, history,
// renderer, OBJ export and source integrity, no new destructive mesh format.
let atelierComponentMode='mesh',atelierComponentTool='tap',atelierComponentMulti=false;
let atelierComponentIds=[],atelierComponentPartId=null,atelierComponentOverlay=null;
let atelierComponentGesture=null,atelierComponentDrag=null,atelierComponentPivot=null;
const atelierComponentMax=192,atelierComponentMaxSlots=2048;
const atelierComponentTopologyCache=new WeakMap();
function atelierComponentMesh(){
 return modelRoot?.children.find(m=>m.isMesh&&m.userData.atelierId===selection)||null;
}
function atelierComponentSupported(){
 const p=partById(selection),mesh=atelierComponentMesh();
 if(!p||!mesh?.geometry?.attributes?.position)return false;
 if(p.refinementLayers?.some(l=>l.enabled))return false;
 return true;
}
function atelierComponentTriangles(g){
 const idx=g.index,pos=g.attributes.position,triangles=[];
 const count=idx?idx.count:pos.count;
 for(let i=0;i+2<count;i+=3){
  const t=idx?[idx.getX(i),idx.getX(i+1),idx.getX(i+2)]:[i,i+1,i+2];
  if(t.every(x=>x<pos.count))triangles.push(t);
 }
 return triangles;
}
function atelierComponentTopology(mesh){
 const g=mesh.geometry;
 const cached=atelierComponentTopologyCache.get(g);if(cached)return cached;
 const p=g.attributes.position,tri=atelierComponentTriangles(g);
 const keys=[],groups=new Map();
 for(let i=0;i<p.count;i++){
  const key=[p.getX(i),p.getY(i),p.getZ(i)].map(v=>Math.round(v*100000)).join(',');
  keys[i]=key;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(i);
 }
 const representative=new Map(),vertices=[],edges=[],edgeSeen=new Set(),edgeLookup=new Map();
 for(let i=0;i<keys.length;i++)if(!representative.has(keys[i])){
  representative.set(keys[i],i);vertices.push(i);
 }
 for(const t of tri)for(let k=0;k<3;k++){
  const a=representative.get(keys[t[k]]),b=representative.get(keys[t[(k+1)%3]]);
  if(a===b)continue;
  const key=[Math.min(a,b),Math.max(a,b)].join(':');
  if(!edgeSeen.has(key)){edgeLookup.set(key,edges.length);edges.push([a,b]);edgeSeen.add(key);}
 }
 const result={vertices,edges,edgeLookup,tri,groups,keys,representative};
 atelierComponentTopologyCache.set(g,result);
 return result;
}
function atelierComponentTopologyForActive(){
 const mesh=atelierComponentMesh();if(!mesh)return null;
 return {mesh,topology:atelierComponentTopology(mesh)};
}
function atelierComponentIndices(topology,mode=atelierComponentMode,ids=atelierComponentIds){
 const selected=new Set();
 for(const id of ids){
  if(mode==='vertex'){
   const key=topology.keys[id];
   for(const i of topology.groups.get(key)||[])selected.add(i);
  }else if(mode==='edge'){
   const e=topology.edges[id];if(!e)continue;
   for(const vertex of e)for(const i of topology.groups.get(topology.keys[vertex])||[])selected.add(i);
  }else if(mode==='face'){
   const t=topology.tri[id];if(!t)continue;
   for(const vertex of t)for(const i of topology.groups.get(topology.keys[vertex])||[])selected.add(i);
  }
 }
 return [...selected].sort((a,b)=>a-b);
}
function atelierComponentProject(mesh,index){
 const p=mesh.geometry.attributes.position;
 const v=new THREE.Vector3().fromBufferAttribute(p,index);
 return mesh.localToWorld(v).project(camera);
}
function atelierComponentScreen(mesh,index){
 const v=atelierComponentProject(mesh,index),r=renderer.domElement.getBoundingClientRect();
 return {x:r.left+(1+v.x)*r.width*.5,y:r.top+(1-v.y)*r.height*.5,z:v.z};
}
function atelierComponentOverlayClear(){
 if(!atelierComponentOverlay)return;
 atelierComponentOverlay.parent?.remove(atelierComponentOverlay);
 atelierComponentOverlay.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 atelierComponentOverlay=null;
}
function atelierComponentOverlayBuild(){
 atelierComponentOverlayClear();
 if(atelierComponentMode==='mesh'||!atelierComponentSupported())return;
 const mesh=atelierComponentMesh(),top=atelierComponentTopology(mesh),g=mesh.geometry;
 mesh.updateMatrixWorld(true);
 const root=new THREE.Group();root.name='Component selection overlay';
 root.userData.atelierHelper=true;world.add(root);
 const selected=new Set(atelierComponentIds);
 const colors={vertex:0x56e9e7,edge:0x69bbff,face:0xe3b6ff};
 if(atelierComponentMode==='vertex'){
  const make=(ids,color,size)=>{
   if(!ids.length)return;
   const positions=[];
   for(const i of ids){
    const v=new THREE.Vector3().fromBufferAttribute(g.attributes.position,i).applyMatrix4(mesh.matrixWorld);
    positions.push(v.x,v.y,v.z);
   }
   const geo=new THREE.BufferGeometry();
   geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
   const point=new THREE.Points(geo,new THREE.PointsMaterial({
    color,size,sizeAttenuation:false,depthTest:false,transparent:true,opacity:.97}));
   point.renderOrder=90;point.userData.atelierHelper=true;root.add(point);
  };
  make(top.vertices.filter((_,i)=>i%Math.max(1,Math.ceil(top.vertices.length/6000))===0&&!selected.has(i)),
    colors.vertex,5);
  make([...selected].map(i=>top.vertices[i]).filter(x=>x!==undefined),0xffd776,11);
 }else if(atelierComponentMode==='edge'){
  const build=(ids,color,width)=>{
   const a=[];
   for(const i of ids){
    const e=top.edges[i];if(!e)continue;
    for(const j of e){
     const v=new THREE.Vector3().fromBufferAttribute(g.attributes.position,j).applyMatrix4(mesh.matrixWorld);
     a.push(v.x,v.y,v.z);
    }
   }
   const geometry=new THREE.BufferGeometry();
   geometry.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
   const line=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color,
    depthTest:false,transparent:true,opacity:.92,linewidth:width}));
   line.renderOrder=90;line.userData.atelierHelper=true;root.add(line);
  };
  const stride=Math.max(1,Math.ceil(top.edges.length/6000));
  build(top.edges.map((_,i)=>i).filter(i=>i%stride===0&&!selected.has(i)),colors.edge,1);
  build([...selected],0xffdb84,2);
 }else{
  const draw=(ids,color,opacity)=>{
   const a=[];
   for(const i of ids){
    const t=top.tri[i];if(!t)continue;
    for(const j of t){
     const v=new THREE.Vector3().fromBufferAttribute(g.attributes.position,j).applyMatrix4(mesh.matrixWorld);
     a.push(v.x,v.y,v.z);
    }
   }
   if(!a.length)return;
   const geo=new THREE.BufferGeometry();
   geo.setAttribute('position',new THREE.Float32BufferAttribute(a,3));
   const m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({
    color,transparent:true,opacity,depthTest:false,depthWrite:false,side:THREE.DoubleSide}));
   m.renderOrder=91;m.userData.atelierHelper=true;root.add(m);
  };
  const stride=Math.max(1,Math.ceil(top.tri.length/4000));
  draw(top.tri.map((_,i)=>i).filter(i=>i%stride===0&&!selected.has(i)),colors.face,.065);
  draw([...selected],0xffd36c,.37);
 }
 atelierComponentOverlay=root;
}
function atelierComponentSelectedPivot(){
 const view=atelierComponentTopologyForActive();
 if(!view||!atelierComponentIds.length)return null;
 const {mesh,topology}=view,ids=atelierComponentIndices(topology);
 if(!ids.length)return null;
 mesh.updateMatrixWorld(true);
 const v=new THREE.Vector3(),center=new THREE.Vector3();
 for(const id of ids)center.add(v.fromBufferAttribute(mesh.geometry.attributes.position,id)
  .applyMatrix4(mesh.matrixWorld));
 return center.divideScalar(ids.length);
}
function atelierComponentGizmoBuild(){
 atelierMeshGizmoClear();
 if(!atelierComponentIds.length||!atelierComponentSupported())return;
 const pivot=atelierComponentSelectedPivot();if(!pivot)return;
 atelierComponentPivot=pivot;
 const root=new THREE.Group();root.name='Selected component transforms';root.position.copy(pivot);
 const span=atelierMeshClamp(orbit.distance*.065,.24,.8);
 for(const [axis,color] of [['x',0xff6b7a],['y',0x65f0aa],['z',0x68b9ff]]){
  const direction=new THREE.Vector3(...atelierMeshAxes[axis]);
  const stem=new THREE.Mesh(new THREE.CylinderGeometry(.014,.014,span*.78,8),
   new THREE.MeshBasicMaterial({color,depthTest:false,depthWrite:false}));
  stem.position.copy(direction.clone().multiplyScalar(span*.42));
  stem.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction);
  stem.userData.atelierHelper=true;root.add(stem);
  const handle=new THREE.Mesh(new THREE.SphereGeometry(Math.max(.09,span*.16),12,10),
   new THREE.MeshBasicMaterial({color,depthTest:false}));
  handle.position.copy(direction.clone().multiplyScalar(span));
  handle.userData.meshGizmoAxis=axis;handle.userData.atelierHelper=true;
  root.add(handle);
 }
 if(atelierMeshMode==='scale'){
  const handle=new THREE.Mesh(new THREE.BoxGeometry(.17,.17,.17),
   new THREE.MeshBasicMaterial({color:0xffe28b,depthTest:false}));
  handle.userData.meshGizmoAxis='all';handle.userData.atelierHelper=true;root.add(handle);
 }
 world.add(root);atelierMeshGizmo=root;atelierMeshPivot=pivot;
}
function atelierComponentRefresh(){
 if(atelierComponentMode==='mesh'){atelierComponentOverlayClear();return;}
 if(atelierComponentPartId!==selection){
  atelierComponentIds=[];atelierComponentPartId=selection;
 }
 atelierComponentOverlayBuild();
 atelierComponentGizmoBuild();
 atelierComponentUIRefresh();
 if(renderer&&world&&camera)renderer.render(world,camera);
}
function atelierComponentModeSet(next){
 if(!['mesh','vertex','edge','face'].includes(next))return;
 atelierComponentMode=next;atelierComponentIds=[];atelierComponentPartId=selection;
 atelierComponentGesture=null;atelierComponentDrag=null;
 atelierComponentOverlayClear();atelierMeshGizmoClear();
 if(next==='mesh'){atelierMeshToolbarRefresh();}
 else{atelierComponentRefresh();}
 atelierComponentUIRefresh();
 if(renderer&&world&&camera)renderer.render(world,camera);
}
function atelierComponentUIRefresh(){
 const bar=panel?.querySelector('[data-component-controls]');if(!bar)return;
 for(const b of bar.querySelectorAll('[data-component-mode]'))
  b.setAttribute('aria-pressed',String(b.dataset.componentMode===atelierComponentMode));
 for(const b of bar.querySelectorAll('[data-component-tool]'))
  b.setAttribute('aria-pressed',String(b.dataset.componentTool===atelierComponentTool));
 const multi=bar.querySelector('[data-component-multi]');
 if(multi){multi.setAttribute('aria-pressed',String(atelierComponentMulti));
  multi.textContent=atelierComponentMulti?'✓ Multi':'＋ Multi';}
 const count=bar.querySelector('[data-component-count]');
 if(count)count.textContent=atelierComponentMode==='mesh'?'Object mode':
  atelierComponentIds.length+' '+atelierComponentMode+(atelierComponentIds.length===1?'':'s');
 const disabled=atelierComponentMode==='mesh';
 for(const b of bar.querySelectorAll('[data-component-tool],[data-component-multi],[data-component-clear],[data-component-nudge]'))
  b.disabled=disabled;
}
function atelierComponentChoose(id){
 if(id==null){if(!atelierComponentMulti)atelierComponentIds=[];}
 else if(atelierComponentMulti){
  if(atelierComponentIds.includes(id))atelierComponentIds=atelierComponentIds.filter(x=>x!==id);
  else if(atelierComponentIds.length<atelierComponentMax)atelierComponentIds.push(id);
  else status('Maximum of '+atelierComponentMax+' selected components.',true);
 }else atelierComponentIds=[id];
 atelierComponentRefresh();
}
function atelierComponentHit(e){
 const view=atelierComponentTopologyForActive();if(!view)return null;
 const {mesh,topology:top}=view;
 mouse.set(point(e).x,point(e).y);raycaster.setFromCamera(mouse,camera);
 // Raycast against the selected native part first. Searching all 73k edges
 // of the head on every phone tap would freeze the editor.
 const hit=raycaster.intersectObject(mesh,false)[0],triangle=top.tri[hit?.faceIndex];
 if(!triangle)return null;
 if(atelierComponentMode==='face')return hit.faceIndex;
 const tol=e.pointerType==='touch'?31:22;
 if(atelierComponentMode==='vertex'){
  let best=null;
  for(const id of triangle){
   const key=top.keys[id],representative=top.representative.get(key);
   const point=atelierComponentScreen(mesh,representative);
   const dist=Math.hypot(e.clientX-point.x,e.clientY-point.y);
   const index=top.vertices.indexOf(representative);
   if(index>=0&&dist<=tol&&(!best||dist<best.dist))best={index,dist};
  }
  return best?.index??null;
 }
 let best=null;
 for(let i=0;i<3;i++){
  const j=triangle[(i+1)%3],k=triangle[i];
  const repA=top.representative.get(top.keys[k]),repB=top.representative.get(top.keys[j]);
  if(repA===repB)continue;
  const key=[Math.min(repA,repB),Math.max(repA,repB)].join(':');
  const index=top.edgeLookup.get(key);if(index===undefined)continue;
  const from=atelierComponentScreen(mesh,repA),to=atelierComponentScreen(mesh,repB);
  const vx=to.x-from.x,vy=to.y-from.y,length=vx*vx+vy*vy||1;
  const t=atelierMeshClamp(((e.clientX-from.x)*vx+(e.clientY-from.y)*vy)/length,0,1);
  const dist=Math.hypot(e.clientX-from.x-t*vx,e.clientY-from.y-t*vy);
  if(dist<=tol&&(!best||dist<best.dist))best={index,dist};
 }
 return best?.index??null;
}
function atelierComponentRegionPick(points,tool){
 const view=atelierComponentTopologyForActive();if(!view||!points.length)return [];
 const {mesh,topology:top}=view,rect=renderer.domElement.getBoundingClientRect();
 const extent={left:Math.min(...points.map(p=>p.x)),right:Math.max(...points.map(p=>p.x)),
  top:Math.min(...points.map(p=>p.y)),bottom:Math.max(...points.map(p=>p.y))};
 const inside=p=>{
  if(tool==='box')return p.x>=extent.left&&p.x<=extent.right&&p.y>=extent.top&&p.y<=extent.bottom;
  let yes=false;
  for(let i=0,j=points.length-1;i<points.length;j=i++){
   const a=points[i],b=points[j];
   if((a.y>p.y)!==(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)yes=!yes;
  }
  return yes;
 };
 const candidate=atelierComponentMode==='vertex'?top.vertices:
  atelierComponentMode==='edge'?top.edges:top.tri;
 const selected=[];
 const stride=Math.max(1,Math.ceil(candidate.length/16000));
 mesh.updateMatrixWorld(true);
 for(let i=0;i<candidate.length;i+=stride){
  const item=candidate[i],vertices=typeof item==='number'?[item]:item;
  const samples=vertices.map(id=>atelierComponentScreen(mesh,id));
  const center={x:samples.reduce((a,p)=>a+p.x,0)/samples.length,
   y:samples.reduce((a,p)=>a+p.y,0)/samples.length};
  if(inside(center))selected.push(i);
  if(selected.length>=atelierComponentMax)break;
 }
 return selected;
}
function atelierComponentPointerDown(e){
 if(atelierComponentMode==='mesh'||e.button!==0)return false;
 if(atelierComponentGizmoDown(e))return true;
 atelierComponentGesture={pointerId:e.pointerId,startX:e.clientX,startY:e.clientY,
  points:[{x:e.clientX,y:e.clientY}],moved:false};
 try{renderer.domElement.setPointerCapture(e.pointerId)}catch(_){}
 if(e.cancelable)e.preventDefault();
 return true;
}
function atelierComponentPointerMove(e){
 if(atelierComponentDrag)return atelierComponentGizmoMove(e);
 const d=atelierComponentGesture;
 if(!d||d.pointerId!==e.pointerId)return false;
 if(Math.hypot(e.clientX-d.startX,e.clientY-d.startY)>5)d.moved=true;
 if(d.moved&&atelierComponentTool!=='tap'){
  d.points.push({x:e.clientX,y:e.clientY});
  if(d.points.length>300)d.points.shift();
 }
 if(e.cancelable)e.preventDefault();
 return true;
}
function atelierComponentPointerUp(e){
 if(atelierComponentDrag)return atelierComponentGizmoUp(e);
 const d=atelierComponentGesture;
 if(!d||d.pointerId!==e.pointerId)return false;
 atelierComponentGesture=null;
 if(atelierComponentTool==='tap'){
  if(!d.moved)atelierComponentChoose(atelierComponentHit(e));
  // A swiping gesture in tap mode still orbits the view.
  else{orbit.yaw-=(e.clientX-d.startX)*.008;
   orbit.pitch=atelierMeshClamp(orbit.pitch+(e.clientY-d.startY)*.006,-.85,1.1);
   cameraUpdate();}
 }else{
  const chosen=atelierComponentRegionPick(d.points,atelierComponentTool);
  atelierComponentIds=atelierComponentMulti?[...new Set([...atelierComponentIds,...chosen])].slice(0,atelierComponentMax):chosen;
  atelierComponentRefresh();
 }
 if(e.cancelable)e.preventDefault();
 return true;
}
function atelierComponentCancel(){
 if(atelierComponentDrag){atelierComponentDrag=null;renderParts();}
 atelierComponentGesture=null;
}
function atelierComponentSnapshot(){
 const view=atelierComponentTopologyForActive();if(!view)return null;
 const {mesh,topology}=view;
 const ids=atelierComponentIndices(topology);
 if(!ids.length||ids.length>atelierComponentMaxSlots)return null;
 const a=mesh.geometry.attributes.position;
 return {mesh,partId:selection,ids,pivot:atelierComponentSelectedPivot(),
  base:ids.map(i=>[a.getX(i),a.getY(i),a.getZ(i)])};
}
function atelierComponentAmountFromPixels(pixels,mode,axis){
 const speed=atelierMeshSensitivity(mode);
 if(mode==='move')return atelierMeshClamp(pixels*.0009*Math.min(orbit.distance,8)*speed,-.5,.5);
 if(mode==='rotate')return atelierMeshClamp(pixels*.009*speed,-Math.PI,Math.PI);
 return atelierMeshClamp(Math.exp(pixels*.009*speed),.2,3);
}
function atelierComponentCandidate(d,amount){
 const {mesh,base,ids,pivot,axis,mode}=d;
 const inverse=mesh.matrixWorld.clone().invert(),q=new THREE.Quaternion();
 if(mode==='rotate')q.setFromAxisAngle(new THREE.Vector3(...atelierMeshAxes[axis]),amount);
 const factor=mode==='scale'?amount:1;
 const translate=new THREE.Vector3(...(atelierMeshAxes[axis]||[0,0,0]));
 const result=[];
 for(const original of base){
  const worldPoint=new THREE.Vector3(...original).applyMatrix4(mesh.matrixWorld);
  if(mode==='move')worldPoint.addScaledVector(translate,amount);
  else if(mode==='rotate')worldPoint.sub(pivot).applyQuaternion(q).add(pivot);
  else if(mode==='scale'){
   worldPoint.sub(pivot);
   if(axis==='all')worldPoint.multiplyScalar(factor);
   else worldPoint.setComponent({x:0,y:1,z:2}[axis],
    worldPoint.getComponent({x:0,y:1,z:2}[axis])*factor);
   worldPoint.add(pivot);
  }
  const local=worldPoint.applyMatrix4(inverse);
  result.push([local.x,local.y,local.z]);
 }
 return result;
}
function atelierComponentPreview(d,amount){
 const neutral=d.mode==='scale'?1:0;
 const within=rows=>rows.every((v,k)=>v.every((x,i)=>
  Number.isFinite(x)&&Math.abs(x-d.base[k][i])<=.499));
 let next=atelierComponentCandidate(d,amount);
 if(!within(next)){
  let lo=0,hi=1;
  for(let i=0;i<11;i++){
   const fraction=(lo+hi)*.5;
   const candidate=neutral+(amount-neutral)*fraction;
   if(within(atelierComponentCandidate(d,candidate)))lo=fraction;else hi=fraction;
  }
  amount=neutral+(amount-neutral)*lo;
  next=atelierComponentCandidate(d,amount);
 }
 d.amount=amount;
 const a=d.mesh.geometry.attributes.position;
 for(let k=0;k<d.ids.length;k++)a.setXYZ(d.ids[k],...next[k]);
 a.needsUpdate=true;
 // Do not recompute whole-mesh normals and bounds on EVERY Android pointer
 // event. The final native geometry rebuild computes the correct values once.
 if(atelierMeshGizmo){
  if(d.mode==='move'){
   const axis=atelierMeshAxes[d.axis];
   atelierMeshGizmo.position.copy(d.pivot).add(
    new THREE.Vector3(...axis).multiplyScalar(amount));
  }
  atelierMeshGizmo.updateMatrixWorld(true);
 }
 if(renderer&&world&&camera)renderer.render(world,camera);
}
function atelierComponentCommit(d){
 const p=partById(d.partId);if(!p)return false;
 const a=d.mesh.geometry.attributes.position;
 const rows=d.ids.map((index,k)=>({
  index,delta:[a.getX(index)-d.base[k][0],a.getY(index)-d.base[k][1],
   a.getZ(index)-d.base[k][2]]})).filter(row=>row.delta.some(v=>Math.abs(v)>1e-7));
 if(!rows.length){atelierComponentRefresh();return false;}
 if(rows.some(r=>r.delta.some(v=>!Number.isFinite(v)||Math.abs(v)>.5))){
  status('Component edit exceeds safe ±0.5 local units; reduce sensitivity or use smaller steps.',true);
  renderParts();return false;
 }
 const chunks=[];
 for(let i=0;i<rows.length;i+=256){
  const chunk=rows.slice(i,i+256);
  chunks.push({indices:chunk.map(r=>r.index),moves:chunk.map(r=>r.delta),
   resolution:atelierSculptResolution(p)});
 }
 const prev=p.sculptVertexEdits||[];
 if(prev.length+chunks.length>atelierSculptMaxVertexEdits){
  status('Vertex edit history budget reached; save/export, or undo earlier edits.',true);
  renderParts();return false;
 }
 const next={...p,sculptVertexEdits:[...prev,...chunks]};
 if(!checkPart(next)){status('Native vertex data validation rejected the edit.',true);renderParts();return false;}
 checkpoint();p.sculptVertexEdits=next.sculptVertexEdits;
 signalEdited();atelierComponentRefresh();
 status('Saved '+rows.length+' '+atelierComponentMode+' vertex slots. Native Undo / JSON / OBJ supported.');
 return true;
}
function atelierComponentGizmoDown(e){
 if(atelierComponentMode==='mesh')return false;
 if(atelierComponentDrag||!atelierMeshGizmo||!atelierComponentIds.length)return false;
 mouse.set(point(e).x,point(e).y);raycaster.setFromCamera(mouse,camera);
 const hit=raycaster.intersectObjects(atelierMeshGizmo.children.filter(o=>o.userData.meshGizmoAxis),false)[0];
 if(!hit)return false;
 const snapshot=atelierComponentSnapshot();
 if(!snapshot){status('Select fewer component slots (maximum '+atelierComponentMaxSlots+').',true);return true;}
 const axis=hit.object.userData.meshGizmoAxis,pivot=snapshot.pivot.clone();
 const p0=pivot.clone().project(camera);
 const tip=pivot.clone().add(new THREE.Vector3(...(atelierMeshAxes[axis]||[1,1,0])).multiplyScalar(.5)).project(camera);
 const rect=renderer.domElement.getBoundingClientRect();
 const dir=new THREE.Vector2((tip.x-p0.x)*rect.width/2,-(tip.y-p0.y)*rect.height/2);
 if(dir.lengthSq()<16)dir.set(1,0);else dir.normalize();
 atelierComponentDrag={...snapshot,pointerId:e.pointerId,axis,mode:atelierMeshMode,
  startX:e.clientX,startY:e.clientY,direction:dir,amount:atelierMeshMode==='scale'?1:0};
 try{renderer.domElement.setPointerCapture(e.pointerId)}catch(_){}
 pressed=null;if(e.cancelable)e.preventDefault();return true;
}
function atelierComponentGizmoMove(e){
 const d=atelierComponentDrag;
 if(!d||d.pointerId!==e.pointerId)return false;
 const pixels=(e.clientX-d.startX)*d.direction.x+(e.clientY-d.startY)*d.direction.y;
 atelierComponentPreview(d,atelierComponentAmountFromPixels(pixels,d.mode,d.axis));
 if(e.cancelable)e.preventDefault();return true;
}
function atelierComponentGizmoUp(e){
 const d=atelierComponentDrag;if(!d||d.pointerId!==e.pointerId)return false;
 atelierComponentDrag=null;
 atelierComponentCommit(d);
 if(e.cancelable)e.preventDefault();return true;
}
function atelierComponentNudge(sign){
 const d=atelierComponentSnapshot();if(!d)return;
 d.axis=atelierMeshAxis;d.mode=atelierMeshMode;
 const speed=atelierMeshSensitivity(d.mode),amount=d.mode==='move'?sign*.025*speed:
  d.mode==='rotate'?sign*Math.PI/90*speed:Math.pow(1.025,sign*speed);
 atelierComponentPreview(d,amount);
 atelierComponentCommit(d);
}
function atelierComponentInstall(){
 if(panel.querySelector('[data-component-controls]'))return;
 const parent=panel.querySelector('.atelier-viewport-controls')||panel.querySelector('#modelAtelierViewport');
 if(!parent)return;
 const row=document.createElement('div');row.className='atelier-component-dock';
 row.dataset.componentControls='1';
 row.innerHTML='<div class="atelier-component-modes" aria-label="Mesh component mode">'+
  '<button data-component-mode="mesh" aria-pressed="true">Mesh</button>'+
  '<button data-component-mode="vertex">● Vertex</button>'+
  '<button data-component-mode="edge">╱ Edge</button>'+
  '<button data-component-mode="face">▱ Face</button></div>'+
  '<div class="atelier-component-tools">'+
  '<button data-component-multi aria-pressed="false">＋ Multi</button>'+
  '<button data-component-tool="tap" aria-pressed="true">Tap</button>'+
  '<button data-component-tool="box">▭ Box</button>'+
  '<button data-component-tool="lasso">⌁ Lasso</button>'+
  '<button data-component-clear>Clear</button>'+
  '<button data-component-nudge="-1">−</button><button data-component-nudge="1">＋</button>'+
  '<output data-component-count aria-live="polite">Object mode</output></div>';
 parent.append(row);
 row.addEventListener('pointerdown',e=>e.stopPropagation());
 row.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.componentMode)atelierComponentModeSet(b.dataset.componentMode);
  else if(b.dataset.componentTool){atelierComponentTool=b.dataset.componentTool;atelierComponentUIRefresh();}
  else if(b.hasAttribute('data-component-multi')){atelierComponentMulti=!atelierComponentMulti;atelierComponentUIRefresh();}
  else if(b.hasAttribute('data-component-clear')){atelierComponentIds=[];atelierComponentRefresh();}
  else if(b.dataset.componentNudge)atelierComponentNudge(Number(b.dataset.componentNudge));
 });
 atelierComponentUIRefresh();
}
