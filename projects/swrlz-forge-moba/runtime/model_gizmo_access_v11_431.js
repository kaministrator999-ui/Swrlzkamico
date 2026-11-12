/* SE431_MODEL_GIZMO_ACCESS_START */
// Native editor helpers only. Picking returns the original handle so the
// established snapshot, preview, pointer capture and history paths stay intact.
const se431GizmoAccess=(()=>{
 const roots=new WeakMap(),canvases=new WeakSet(),colors=new WeakMap();
 let pointerType='',hoverAxis=null;
 const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
 const canvas=()=>renderer?.domElement;
 const borrowed=()=>typeof se340ModelBridge!=='undefined'&&se340ModelBridge.isBorrowed();
 const coarse=()=>pointerType==='touch'||(!pointerType&&typeof matchMedia==='function'&&matchMedia('(pointer:coarse)').matches);
 const targetRadius=type=>type==='touch'?22:type==='pen'?18:12;
 const visible=o=>{for(let n=o;n;n=n.parent)if(n.visible===false)return false;return true;};
 function rect(){const r=canvas()?.getBoundingClientRect();return r&&r.width>0&&r.height>0?{left:r.left||0,top:r.top||0,width:r.width,height:r.height}:null;}
 function ready(){return !!camera&&!!atelierMeshGizmo&&visible(atelierMeshGizmo)&&!borrowed();}
 function project(world,r){
  const local=world.clone().applyMatrix4(camera.matrixWorldInverse);
  if(!Number.isFinite(local.z)||local.z>=-camera.near)return null;
  const p=world.clone().project(camera);
  if(![p.x,p.y,p.z].every(Number.isFinite)||p.z<-1||p.z>1)return null;
  return {x:r.left+(p.x+1)*r.width/2,y:r.top+(1-p.y)*r.height/2,z:p.z,
   inside:Math.abs(p.x)<=1&&Math.abs(p.y)<=1};
 }
 function unitsAt(root,r){
  camera.updateMatrixWorld(true);
  const depth=-root.getWorldPosition(new THREE.Vector3()).applyMatrix4(camera.matrixWorldInverse).z;
  if(!(depth>camera.near))return 0;
  return camera.isOrthographicCamera?(camera.top-camera.bottom)/(camera.zoom||1)/r.height:
   2*depth*Math.tan(THREE.MathUtils.degToRad(camera.fov||44)/2)/(camera.zoom||1)/r.height;
 }
 function adopt(root){
  if(!root||roots.has(root))return;
  const handles=root.children.filter(o=>o.userData.meshGizmoAxis),span=Math.max(0,...handles.map(h=>h.position.length()));
  const rows=root.children.filter(o=>o.isMesh&&o.userData.atelierHelper&&!o.userData.atelierArcAxis).map(o=>({object:o,position:o.position.clone(),scale:o.scale.clone()}));
  roots.set(root,{span,rows});root.userData.se431GizmoAccess=true;
 }
 function paint(axis){
  const g=atelierMeshGizmo;if(!g)return;
  g.traverse(o=>{
   const key=o.userData.meshGizmoAxis||o.userData.atelierArcAxis;
   if(!key||!o.material||Array.isArray(o.material)||!o.material.color)return;
   if(!colors.has(o.material))colors.set(o.material,o.material.color.clone());
   o.material.color.copy(colors.get(o.material));
   if(key===axis)o.material.color.lerp(new THREE.Color(0xffffff),.55);
  });
  for(const [key,item]of atelierArcRings){
   if(!visible(item.ring))continue;
   for(const o of [item.wideTrack,item.bead,item.marks]){
    if(!o?.material?.color)continue;
    if(!colors.has(o.material))colors.set(o.material,o.material.color.clone());
    o.material.color.copy(colors.get(o.material));
    if(key===axis)o.material.color.lerp(new THREE.Color(0xffffff),.42);
   }
  }
 }
 function refresh(){
  if(!ready())return;
  const g=atelierMeshGizmo,r=rect();if(!r)return;
  adopt(g);const data=roots.get(g),unit=unitsAt(g,r);if(!unit)return;
  const touch=coarse(),spanPixels=touch?clamp(Math.min(r.width,r.height)*.25,60,90):76;
  const factor=data.span?unit*spanPixels/data.span:1;
  for(const row of data.rows){
   const o=row.object;o.position.copy(row.position).multiplyScalar(factor);
   if(o.userData.meshGizmoAxis){
    const radius=o.geometry.boundingSphere?.radius||((o.geometry.computeBoundingSphere(),o.geometry.boundingSphere?.radius)||.1);
    o.scale.setScalar(unit*(touch?10:8)/Math.max(radius,.00001));
   }else o.scale.copy(row.scale).multiplyScalar(factor);
  }
  if(atelierComponentMode==='mesh'&&atelierMeshMode==='rotate'){
   const radiusPixels=touch?clamp(Math.min(r.width,r.height)*.27,64,96):86;
   for(const item of atelierArcRings.values()){
    if(item.ring.parent!==g)continue;
    item.ring.scale.setScalar(unit*radiusPixels/item.radius);
    for(const o of [item.bead,item.hit]){
     const radius=o.geometry.parameters?.radius||.08;
     o.scale.setScalar(unit*(touch?11:9)/(radius*item.ring.scale.x));
    }
   }
  }
  g.updateMatrixWorld(true);
  const active=atelierComponentDrag?.axis||atelierMeshDrag?.axis||hoverAxis;
  paint(active);install();
 }
 function pointerAllowed(e){
  const c=canvas(),r=rect();
  const primary=e&&(e.button===undefined||e.button===0||e.type==='pointermove'&&e.button===-1&&e.buttons===0);
  if(!e||!c||!r||e.target!==c||e.isPrimary===false||!primary||!ready())return false;
  if(e.clientX<r.left||e.clientX>r.left+r.width||e.clientY<r.top||e.clientY>r.top+r.height)return false;
  // Real menus own their press, including transparent padded portions. A
  // captured drag is handled by native Move/Up, without re-running this gate.
  if(typeof document!=='undefined'&&typeof document.elementFromPoint==='function'&&document.elementFromPoint(e.clientX,e.clientY)!==c)return false;
  return true;
 }
 function segment(px,py,a,b){
  const dx=b.x-a.x,dy=b.y-a.y,n=dx*dx+dy*dy;
  const t=n?clamp(((px-a.x)*dx+(py-a.y)*dy)/n,0,1):0;
  return {distance:Math.hypot(px-a.x-dx*t,py-a.y-dy*t),t};
 }
 function beats(next,previous){
  if(!previous)return true;
  if(Math.abs(next.distance-previous.distance)>.25)return next.distance<previous.distance;
  if(next.axis===atelierMeshAxis&&previous.axis!==atelierMeshAxis)return true;
  if(previous.axis===atelierMeshAxis&&next.axis!==atelierMeshAxis)return false;
  if(next.kind==='uniform'&&previous.kind!=='uniform')return true;
  if(previous.kind==='uniform'&&next.kind!=='uniform')return false;
  return next.depth<previous.depth;
 }
 function handleRows(){
  const r=rect();if(!ready()||!r)return [];
  camera.updateMatrixWorld(true);atelierMeshGizmo.updateMatrixWorld(true);
  const rows=[];
  for(const o of atelierMeshGizmo.children){
   const axis=o.userData.meshGizmoAxis;if(!axis||!visible(o)||axis==='all'&&atelierMeshMode!=='scale')continue;
   const p=project(o.getWorldPosition(new THREE.Vector3()),r);if(!p?.inside)continue;
   rows.push({object:o,axis,kind:axis==='all'?'uniform':'axis',point:[p.x,p.y],depth:p.z,visualRadiusPx:coarse()?10:8});
  }
  return rows;
 }
 function arcRows(){
  const r=rect();if(!ready()||!r||atelierComponentMode!=='mesh'||atelierMeshMode!=='rotate')return [];
  camera.updateMatrixWorld(true);const rows=[];
  for(const [axis,item]of atelierArcRings){
   if(!visible(item.ring)||item.ring.parent!==atelierMeshGizmo)continue;
   item.ring.updateMatrixWorld(true);const samples=[];
   for(let i=0;i<=64;i++){
    const offset=-atelierArcLimit+2*atelierArcLimit*i/64;
    const p=project(item.ring.localToWorld(atelierArcPoint(item.radius,item.phase+offset)),r);
    samples.push(p?{point:[p.x,p.y],offset,depth:p.z,inside:p.inside}:null);
   }
   const representative=samples.find((p,i)=>p?.inside&&i>=24)||samples.find(p=>p?.inside);
   if(representative)rows.push({axis,kind:'arc',point:representative.point,depth:representative.depth,item,samples});
  }
  return rows;
 }
 function pickArc(e){
  if(!pointerAllowed(e)||atelierComponentMode!=='mesh'||atelierMeshMode!=='rotate')return null;
  pointerType=e.pointerType||'mouse';refresh();let best=null;const radius=targetRadius(pointerType);
  for(const row of arcRows())for(let i=1;i<row.samples.length;i++){
   const a=row.samples[i-1],b=row.samples[i];if(!a||!b||!a.inside&&!b.inside)continue;
   const d=segment(e.clientX,e.clientY,{x:a.point[0],y:a.point[1]},{x:b.point[0],y:b.point[1]});
   if(d.distance>radius)continue;
   const next={axis:row.axis,item:row.item,offset:a.offset+(b.offset-a.offset)*d.t,score:d.distance,distance:d.distance,depth:a.depth+(b.depth-a.depth)*d.t};
   if(beats(next,best))best=next;
  }
  return best;
 }
 function pick(e){
  if(!pointerAllowed(e))return null;
  pointerType=e.pointerType||'mouse';refresh();let best=null;const radius=targetRadius(pointerType),r=rect();
  const pivot=project(atelierMeshGizmo.getWorldPosition(new THREE.Vector3()),r);
  for(const row of handleRows()){
   let distance=Math.hypot(e.clientX-row.point[0],e.clientY-row.point[1]);
   if(distance>radius&&row.kind==='axis'&&pivot){
    // The outer shaft is also operable. Keep its smaller target away from
    // the pivot so ordinary mesh/component selection is not swallowed.
    const a={x:pivot.x+(row.point[0]-pivot.x)*.48,y:pivot.y+(row.point[1]-pivot.y)*.48};
    const b={x:row.point[0],y:row.point[1]};const along=segment(e.clientX,e.clientY,a,b).distance;
    if(along<=Math.min(radius,coarse()?11:6))distance=along+radius*.4;
   }
   if(distance>radius)continue;
   const next={...row,distance};if(beats(next,best))best=next;
  }
  return best?{object:best.object,axis:best.axis,distancePx:best.distance}:null;
 }
 function inspect(){
  refresh();const r=rect(),p=ready()&&r?project(atelierMeshGizmo.getWorldPosition(new THREE.Vector3()),r):null;
  const axis=handleRows().map(({object,...row})=>({...row,radiusPx:targetRadius(coarse()?'touch':'mouse')}));
  const arcs=arcRows().map(({item,...row})=>({...row,radiusPx:targetRadius(coarse()?'touch':'mouse')}));
  return {ready:ready(),mode:atelierMeshMode,componentMode:atelierComponentMode,dragging:!!(atelierMeshDrag||atelierComponentDrag),
   activeAxis:atelierComponentDrag?.axis||atelierMeshDrag?.axis||hoverAxis,pivot:p?[p.x,p.y]:null,
   touchRadius:22,mouseRadius:12,handles:[...axis,...arcs]};
 }
 function install(){
  const c=canvas();if(!c||canvases.has(c)||!c.addEventListener)return;canvases.add(c);
  c.addEventListener('pointermove',e=>{
   if(atelierMeshDrag||atelierComponentDrag||e.pointerType==='touch')return;
   const hit=atelierMeshMode==='rotate'&&atelierComponentMode==='mesh'?pickArc(e):pick(e),next=hit?.axis||null;
   if(next!==hoverAxis){hoverAxis=next;paint(next);if(!borrowed()&&typeof atelierMeshPaintModeImmediately==='function')atelierMeshPaintModeImmediately();}
  });
  c.addEventListener('pointerleave',()=>{if(!atelierMeshDrag&&!atelierComponentDrag){hoverAxis=null;paint(null);}});
  c.addEventListener('pointerdown',e=>{pointerType=e.pointerType||'mouse';refresh();});
 }
 const meshBuild=atelierMeshGizmoBuild;
 atelierMeshGizmoBuild=function(){const result=meshBuild.apply(this,arguments);adopt(atelierMeshGizmo);refresh();return result;};
 const componentBuild=atelierComponentGizmoBuild;
 atelierComponentGizmoBuild=function(){const result=componentBuild.apply(this,arguments);adopt(atelierMeshGizmo);refresh();return result;};
 atelierArcPickOnScreen=pickArc;
 return Object.freeze({refresh,pick,inspect});
})();
/* SE431_MODEL_GIZMO_ACCESS_END */
