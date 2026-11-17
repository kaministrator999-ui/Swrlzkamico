/* SE479_RIM_KERNEL_START */
// View-projected rim selection. The tapped vertex belongs to the rim,
// never becomes the center unless the explicit center tool is enabled.
const se479ProjectedRim=(()=>{
 'use strict';
 function choose(points,edges,seed,center,mode){
  if(!Array.isArray(points)||!Number.isInteger(seed)||seed<0||seed>=points.length||
     !Array.isArray(center)||center.length!==2||!['outline','fill'].includes(mode))
   return {ok:false,reason:'Choose a valid vertex on the mesh rim.'};
  const graph=Array.from({length:points.length},()=>[]);
  for(const pair of edges){
   if(!Array.isArray(pair)||pair.length!==2)continue;
   const [a,b]=pair;
   if(Number.isInteger(a)&&Number.isInteger(b)&&a!==b&&a>=0&&b>=0&&
      a<points.length&&b<points.length){graph[a].push(b);graph[b].push(a);}
  }
  const seen=new Set([seed]),queue=[seed];
  for(let i=0;i<queue.length;i++){
   for(const other of graph[queue[i]])if(!seen.has(other)){
    seen.add(other);queue.push(other);
   }
  }
  const distance=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
  const finite=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
  if(!finite(points[seed])||!finite(center))return {ok:false,reason:'Rim projection is unavailable.'};
  const radius=distance(points[seed],center);
  const lengths=graph[seed].filter(i=>finite(points[i]))
   .map(i=>distance(points[i],points[seed])).filter(x=>x>1e-7).sort((a,b)=>a-b);
  const spacing=lengths.length?lengths[Math.floor(lengths.length/2)]:0;
  const tolerance=Math.max(.006,Math.min(.09,spacing>0?spacing*.38:.09,Math.max(.014,radius*.30)));
  const slots=[];
  for(const i of queue){
   if(!finite(points[i]))continue;
   const radial=distance(points[i],center);
   if(mode==='outline'?Math.abs(radial-radius)<=tolerance:
       radial<=radius+tolerance)slots.push(i);
  }
  if(!slots.includes(seed))slots.push(seed);
  slots.sort((a,b)=>a-b);
  return {ok:true,vertexSlots:slots,radius,tolerance,seed,mode,
   connectedVertices:queue.length};
 }
 return Object.freeze({choose});
})();
/* SE479_RIM_KERNEL_END */
/* SE479_RIM_VISIBILITY_START */
(function se479RimVisibility(){
 'use strict';
 const workshop=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const progressive=()=>window.SWYRL_ENGINE_PROGRESSIVE_TOOLS_474?.inspect?.();
 const ringShape=()=>{
  const state=progressive();
  return state?.operation&&state.selectionType==='vertex'&&['ring','fill'].includes(state.shape)
   ?state.shape:null;
 };
 let centerMode=false,frontOnly=true,selectionStyle='material-vertices';
 let shapeBar=null,shapeObserver=null,viewMenu=null,viewControls=null;
 const originalChoose=atelierComponentChoose;
 const originalOverlayBuild=atelierComponentOverlayBuild;
 const originalRegionPick=atelierComponentRegionPick;
 function showStatus(message,error=false){if(typeof status==='function')status(message,error);}
 function isVisible(mesh,slot){
  if(!frontOnly)return true;
  const top=mesh&&atelierComponentTopology(mesh);
  const vertex=top?.vertices?.[slot],attr=mesh?.geometry?.attributes?.position;
  if(!Number.isInteger(vertex)||!attr||!camera)return false;
  mesh.updateMatrixWorld(true);
  camera.updateMatrixWorld(true);
  const target=new THREE.Vector3().fromBufferAttribute(attr,vertex).applyMatrix4(mesh.matrixWorld);
  const projected=target.clone().project(camera);
  if(!Number.isFinite(projected.x)||!Number.isFinite(projected.y)||
     !Number.isFinite(projected.z)||Math.abs(projected.x)>1.04||
     Math.abs(projected.y)>1.04||projected.z>1.001||projected.z< -1.001)return false;
  const origin=camera.isOrthographicCamera?
   new THREE.Vector3(projected.x,projected.y,-1).unproject(camera):
   camera.getWorldPosition(new THREE.Vector3());
  const delta=target.clone().sub(origin),length=delta.length();
  if(length<1e-7)return true;
  const ray=new THREE.Raycaster(origin,delta.multiplyScalar(1/length),0,length+.05);
  const hit=ray.intersectObject(mesh,false)[0];
  const geometry=mesh.geometry;
  if(!geometry.boundingSphere)geometry.computeBoundingSphere();
  const tolerance=Math.max(.0002,(geometry.boundingSphere?.radius||1)*.0035);
  if(hit&&hit.distance+tolerance<length)return false;
  // Ray hits at exact shared triangle corners can miss an occluding face.
  // A second sample a fraction of a pixel toward the object's projected
  // center distinguishes a hidden back corner from a visible front corner.
  // Compare CAMERA DEPTH (not ray distance) because the sample is offset.
  const center=new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()).project(camera);
  const inward=new THREE.Vector2(
   projected.x*.995+center.x*.005,
   projected.y*.995+center.y*.005
  );
  const probe=new THREE.Raycaster();
  probe.setFromCamera(inward,camera);
  const near=probe.intersectObject(mesh,false)[0];
  if(!near)return !!hit; // don't invent visibility where both rays miss
  const view=camera.matrixWorldInverse;
  const depth=-target.clone().applyMatrix4(view).z;
  const foreground=-near.point.clone().applyMatrix4(view).z;
  return foreground+tolerance>=depth;
 }
 function trimToVisible(){
  if(!frontOnly||atelierComponentMode!=='vertex'||!atelierComponentIds.length)return;
  const mesh=atelierComponentMesh();
  if(!mesh)return;
  const next=atelierComponentIds.filter(slot=>isVisible(mesh,slot));
  if(next.length===atelierComponentIds.length)return;
  atelierComponentIds=next;
  atelierComponentRefresh();
 }
 // Existing native selected and unselected dots use depthTest=false.
 // Respect material depth for ALL of them when visible-side selection is on.
 atelierComponentOverlayBuild=function(...args){
  const result=originalOverlayBuild.apply(this,args);
  if(atelierComponentMode==='vertex'&&atelierComponentOverlay){
   for(const child of atelierComponentOverlay.children){
    if(!child.isPoints)continue;
    child.material.depthTest=!!frontOnly;
    child.material.depthWrite=false;
    child.material.needsUpdate=true;
   }
  }
  return result;
 };
 atelierComponentRegionPick=function(points,tool){
  const result=originalRegionPick.apply(this,arguments);
  if(!frontOnly||atelierComponentMode!=='vertex')return result;
  const mesh=atelierComponentMesh();
  return mesh?result.filter(slot=>isVisible(mesh,slot)):[];
 };
 function options(){
  const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh);
  return {mesh,top,part:partById(selection)};
 }
 function selectRim(slot){
  const shape=ringShape();
  if(!shape)return {ok:false,reason:'Select Vertex Ring or Filled Vertex Ring.'};
  if(workshop()?.inspect?.()?.preview?.active)
   return {ok:false,reason:'Apply or Cancel the height preview before changing the rim.'};
  const {mesh,top,part}=options();
  if(!Number.isInteger(slot)||slot<0||slot>=(top?.vertices?.length||0))
   return {ok:false,reason:'Tap a real vertex on the desired rim.'};
  if(!mesh||part?.kind!=='topologyMesh'||!atelierComponentSupported())
   return {ok:false,reason:'Convert this mesh to editable topology before selecting a rim.'};
  if(frontOnly&&!isVisible(mesh,slot))
   return {ok:false,reason:'That vertex is behind the material. Turn off Visible Side Only to select through the mesh.'};
  mesh.updateMatrixWorld(true);camera.updateMatrixWorld(true);
  const centerWorld=new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
  const screenCenter=centerWorld.project(camera),projected=[];
  const attr=mesh.geometry.attributes.position;
  for(const id of top.vertices){
   const v=new THREE.Vector3().fromBufferAttribute(attr,id)
    .applyMatrix4(mesh.matrixWorld).project(camera);
   projected.push([v.x,v.y]);
  }
  const lookup=new Map(top.vertices.map((vertex,i)=>[vertex,i]));
  const edges=top.edges.map(pair=>pair.map(vertex=>lookup.get(vertex)))
   .filter(pair=>pair.every(Number.isInteger));
  const calculated=se479ProjectedRim.choose(projected,edges,slot,
   [screenCenter.x,screenCenter.y],shape==='ring'?'outline':'fill');
  if(!calculated.ok)return calculated;
  // A projection alone can overlap the opposite surface. Ray visibility is
  // authoritative for group selection, not merely for rendering the dots.
  const ids=frontOnly?calculated.vertexSlots.filter(i=>isVisible(mesh,i)):
   calculated.vertexSlots;
  if(!ids.includes(slot))ids.push(slot);
  ids.sort((a,b)=>a-b);
  if(!ids.length)return {ok:false,reason:'No visible vertices intersect this rim.'};
  atelierComponentMode='vertex';atelierComponentPartId=selection;
  atelierComponentIds=ids;atelierComponentGesture=null;atelierComponentDrag=null;
  atelierComponentRefresh();
  const message=(shape==='ring'?'Rim':'Filled rim')+' · '+ids.length+
   ' actual selected vertices · touched point is on the rim.';
  showStatus(message);
  window.SWYRL_ENGINE_RING_HEIGHT_478?.sync?.();
  return {ok:true,vertexSlots:[...ids],seed:slot,mode:shape,radius:calculated.radius,
   selectedCount:ids.length,highlighted:true,message};
 }
 function setCenterMode(value){
  if(workshop()?.inspect?.()?.preview?.active)return false;
  centerMode=!!value;
  refreshToggle();
  showStatus(centerMode?'Set Ring Center ON · tap a vertex to define the center.':
   'Rim-first ON · tap a vertex on the desired rim.');
  return true;
 }
 atelierComponentChoose=function(slot){
  if(ringShape()&&atelierComponentMode==='vertex'&&Number.isInteger(slot)){
   const result=centerMode?
    window.SWYRL_ENGINE_RING_HIGHLIGHT_478?.selectCenter?.(slot):selectRim(slot);
   if(result?.ok){
    if(frontOnly&&centerMode)trimToVisible();
   }else showStatus(result?.reason||result?.error||'Could not select the rim.',true);
   return;
  }
  return originalChoose.apply(this,arguments);
 };
 function setFrontOnly(value){
  if(workshop()?.inspect?.()?.preview?.active)return false;
  frontOnly=!!value;
  trimToVisible();
  if(atelierComponentMode==='vertex'&&atelierComponentSupported())
   atelierComponentRefresh();
  refreshToggle();refreshViewControls();
  showStatus(frontOnly?'Visible Side Only · back vertices are hidden and excluded from new selections.':
   'All sides · back vertices can be viewed and selected.');
  return true;
 }
 function refreshToggle(){
  const row=document.getElementById('se477SelectionShapes');
  if(!row||!ringShape())return;
  let button=row.querySelector('#se479CenterToggle');
  if(!button){
   button=document.createElement('button');button.type='button';
   button.id='se479CenterToggle';
   button.className='se479-center-toggle';
   button.addEventListener('pointerdown',e=>e.stopPropagation());
   button.addEventListener('click',e=>{
    e.stopPropagation();setCenterMode(!centerMode);
   });
   row.append(button);
  }
  const label=centerMode?'Set Ring Center: ON':'Set Ring Center: OFF';
  if(button.textContent!==label)button.textContent=label;
  button.title=centerMode?'Tap a vertex to set the center.':'Tap a vertex on the rim; center mode is disabled.';
  button.setAttribute('aria-pressed',String(centerMode));
  button.setAttribute('aria-label','Set vertex ring center mode');
 }
 function refreshViewControls(){
  if(!viewControls?.isConnected)return;
  const toggle=viewControls.querySelector('#se479VisibleSideOnly');
  if(toggle)toggle.checked=frontOnly;
  const button=viewControls.querySelector('#se479MaterialVertices');
  if(button)button.setAttribute('aria-pressed',String(
   atelierComponentMode==='vertex'&&
   window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode==='shaded'));
 }
 function materialVertices(){
  const state=workshop()?.inspect?.();
  if(state?.preview?.active){showStatus('Apply or Cancel the preview before changing view mode.',true);return false;}
  if(!state?.selection?.partId){showStatus('Select a model mesh first.',true);return false;}
  const view=window.SWYRL_ENGINE_MODEL_VIEW;
  if(!view?.setMode?.('shaded')){showStatus('Material view is not available.',true);return false;}
  if(workshop()?.inspect?.()?.selection?.mode!=='vertex'){
   const result=workshop()?.setComponentMode?.('vertex');
   if(!result?.ok)return false;
  }
  const active=window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
  if(active?.ok===false){showStatus(active.reason,true);return false;}
  frontOnly=true;selectionStyle='material-vertices';
  trimToVisible();atelierComponentRefresh();
  refreshViewControls();
  if(viewMenu)viewMenu.hidden=true;
  const trigger=document.getElementById('se455ViewButton');
  if(trigger)trigger.setAttribute('aria-expanded','false');
  showStatus('Material + Vertices · Visible Side Only. Tap only the front surface; toggle to select through.');
  return true;
 }
 function attachUI(){
  const bar=document.getElementById('se477SelectionShapes');
  if(bar&&bar!==shapeBar){
   shapeObserver?.disconnect();shapeBar=bar;
   shapeObserver=new MutationObserver(refreshToggle);
   shapeObserver.observe(bar,{childList:true});
  }
  refreshToggle();
  const menu=document.getElementById('se455ViewMenu');
  if(!menu||menu===viewMenu&&viewControls?.isConnected)return;
  viewMenu=menu;
  const div=document.createElement('div');div.id='se479MaterialVertexControls';
  div.className='se479-material-vertex-controls';
  const button=document.createElement('button');button.id='se479MaterialVertices';button.type='button';
  button.textContent='Material + Vertices';
  button.title='Keep actual materials visible and show editable mesh vertices.';
  button.addEventListener('click',e=>{e.stopPropagation();materialVertices();});
  const label=document.createElement('label');label.htmlFor='se479VisibleSideOnly';
  const checkbox=document.createElement('input');checkbox.type='checkbox';
  checkbox.id='se479VisibleSideOnly';checkbox.checked=frontOnly;
  checkbox.addEventListener('change',()=>setFrontOnly(checkbox.checked));
  label.append(checkbox,document.createTextNode(' Visible Side Only'));
  const note=document.createElement('small');
  note.textContent='On: selectable front surface only. Off: select through the mesh.';
  div.append(button,label,note);
  const header=[...menu.querySelectorAll('.se455-menu-heading')]
   .find(el=>el.textContent.trim()==='Camera');
  if(header)menu.insertBefore(div,header);else menu.append(div);
  viewControls=div;refreshViewControls();
 }
 const observer=new MutationObserver(()=>attachUI());
 function mount(){
  attachUI();
  const host=document.getElementById('modelAtelierPanel')||document.body;
  if(host)observer.observe(host,{subtree:true,childList:true});
 }
 if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',mount,{once:true});
 else mount();
 window.addEventListener('swrlz:model-workshop-change',()=>{
  // Camera depth updates every render. Selected vertices stay identified in
  // source topology; no geometry, UV or history step is created here.
  refreshViewControls();
 });
 window.SWYRL_ENGINE_RIM_VISIBILITY_479=Object.freeze({
  selectRim,setCenterMode,setFrontOnly,materialVertices,
  inspect:()=>({centerMode,frontOnly,selectionStyle,
   shape:ringShape(),selectedCount:atelierComponentMode==='vertex'?atelierComponentIds.length:0,
   selectedSlots:atelierComponentMode==='vertex'?[...atelierComponentIds]:[],
   selectedVisible:atelierComponentMode==='vertex'?
    atelierComponentIds.filter(id=>isVisible(atelierComponentMesh(),id)).length:0,
   material:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode||null}),
  isVisibleSlot:slot=>isVisible(atelierComponentMesh(),slot),
  vertexLocalPosition:slot=>{
   const mesh=atelierComponentMesh(),top=mesh&&atelierComponentTopology(mesh);
   const vertex=top?.vertices?.[slot],attr=mesh?.geometry?.attributes?.position;
   return Number.isInteger(vertex)&&attr?[
    attr.getX(vertex),attr.getY(vertex),attr.getZ(vertex)]:null;
  },
  sync:()=>{attachUI();refreshViewControls();}
 });
})();
/* SE479_RIM_VISIBILITY_END */
