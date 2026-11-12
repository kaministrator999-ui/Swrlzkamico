/* SE430_MODEL_WORKSHOP_BRIDGE_START */
// Native component topology tools. A preview replaces only an owned derived
// BufferGeometry; descriptors, selection intent and Undo remain authoritative.
const se430ModelWorkshop=(()=>{
 const clone=value=>structuredClone(value),ops=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals'];
 const ordinary=new Set(['id','name','kind','group','position','rotation','scale','color','material','meshDensity','topologyMesh','runtimeLOD']);
 let active=null,message='',notifying=false,refreshQueued=false;
 const auditCache=new WeakMap(),regionCache=new WeakMap(),disposed=new WeakSet();
 const fail=reason=>{message=reason;return {ok:false,reason,error:reason};};
 const native=()=>se340ModelBridge.inspect();
 const borrowed=()=>!!se340ModelBridge.isBorrowed?.();
 function refreshComponents(){
  if(borrowed())atelierComponentUIRefresh();
  else atelierComponentRefresh();
 }
 function renderPreview(){if(!borrowed()&&renderer&&world&&camera)renderer.render(world,camera);}
 function meshFor(id=selection){return modelRoot?.children.find(o=>o.isMesh&&o.userData?.atelierId===id)||null;}
 function blocked(p=partById(selection),mesh=meshFor()){
  if(!native().open||!modelRoot||!model())return 'Open a Model Studio project first.';
  if(!p||!mesh)return 'Select one mesh in the viewport or parts list.';
  if((atelierMeshIds||[]).filter(id=>partById(id)).length>1)return 'Choose one mesh; topology tools edit one object at a time.';
  if(mesh.isSkinnedMesh||mesh.geometry?.getAttribute?.('skinIndex')||Object.keys(mesh.geometry?.morphAttributes||{}).length)
   return 'This mesh is skinned or animated. Use an independent unrigged mesh for topology changes.';
  if(Object.keys(p).some(key=>!ordinary.has(key)))return 'This mesh has authored deformation, paint, texture, rig or procedural data. Keep that source intact; use a plain independent mesh.';
  if(!checkPart(p))return 'The selected native part is invalid; no geometry will be changed.';
  return '';
 }
 function busy(){
  return !!native().gesture||!!se350ModelTools.inspect().gesture||!!se350ModelSurface.inspect().active||
   !!se390ModelCreate.inspect().pending||!!se410ModelAccessory.inspect().pending||
   !!atelierMeshDrag||!!atelierComponentDrag||!!atelierComponentGesture||!!atelierSculptDrag;
 }
 function sourceVersion(){const state=native();return state.documentToken+':'+state.revision;}
 function audit(data){
  const version=sourceVersion(),cached=auditCache.get(data);
  if(cached?.version===version)return cached.result;
  const result=atelierTopologyAudit(data);auditCache.set(data,{version,result});return result;
 }
 function faceIds(p=partById(selection)){
  return p?.kind==='topologyMesh'&&atelierComponentMode==='face'&&atelierComponentPartId===selection?
   [...new Set(atelierComponentIds)].filter(id=>Number.isInteger(id)&&id>=0&&id<p.topologyMesh.indices.length/3).sort((a,b)=>a-b):[];
 }
 function region(p,ids){
  const data=p.topologyMesh,key=ids.join(','),version=sourceVersion();
  if(regionCache.get(data)?.version!==version)regionCache.set(data,{version,regions:new Map()});
  const cache=regionCache.get(data).regions;if(!cache.has(key)){
   if(cache.size>12)cache.clear();cache.set(key,se430MeshOps.region(data,ids));
  }
  return cache.get(key);
 }
 function selectedEdge(p){
  if(atelierComponentMode!=='edge'||atelierComponentPartId!==selection||atelierComponentIds.length!==1)return null;
  const mesh=meshFor(),top=mesh&&atelierComponentTopology(active?.mesh===mesh?{geometry:active.original}:mesh),pair=top?.edges?.[atelierComponentIds[0]];
  if(!pair)return null;
  // Component edges are physical endpoints. Only a unique indexed pair can
  // map safely to the old exact-index splitter without breaking UV seams.
  if(pair.some(id=>(top.groups.get(top.keys[id])||[]).length!==1))return null;
  for(let f=0;f<p.topologyMesh.indices.length/3;f++){
   const tri=p.topologyMesh.indices.slice(f*3,f*3+3);
   for(let edgeSlot=0;edgeSlot<3;edgeSlot++){
    const a=tri[edgeSlot],b=tri[(edgeSlot+1)%3];
    if((a===pair[0]&&b===pair[1])||(a===pair[1]&&b===pair[0]))return {faceIndex:f,edgeSlot};
   }
  }
  return null;
 }
 function boundaryVertex(p){
  if(atelierComponentPartId!==selection||!atelierComponentIds.length)return null;
  const mesh=meshFor(),top=mesh&&atelierComponentTopology(active?.mesh===mesh?{geometry:active.original}:mesh);if(!top)return null;
  const vertices=atelierComponentMode==='vertex'?atelierComponentIds.map(i=>top.vertices[i]):
   atelierComponentMode==='edge'?atelierComponentIds.flatMap(i=>top.edges[i]||[]):[];
  const exposed=new Set();for(const edges of audit(p.topologyMesh).edges.values())if(edges.length===1){exposed.add(edges[0].from);exposed.add(edges[0].to);}
  return vertices.find(id=>exposed.has(id))??null;
 }
 function availability(){
  const p=partById(selection),reason=blocked(p),result=Object.fromEntries(ops.map(op=>[op,{available:false,reason}]));
  const convert={available:false,reason:reason||'Conversion is for a plain primitive. This mesh is already editable topology.'};
  if(reason)return {operations:result,convert};
  convert.available=['box','sphere','cylinder','cone'].includes(p.kind);
  if(convert.available)convert.reason='Creates welded editable topology and regenerates plain UV coordinates. Convert only when you are ready to edit faces.';
  if(p.kind!=='topologyMesh'){
   for(const op of ops)result[op].reason='Convert this plain primitive to editable topology first.';
   return {operations:result,convert};
  }
  const a=audit(p.topologyMesh),integrity=!a.ok||a.zeroAreaFaces||a.nonManifoldEdges;
  if(integrity){for(const op of ops)result[op].reason='Repair invalid, degenerate or nonmanifold geometry in the advanced topology inspector first.';return {operations:result,convert};}
  const ids=faceIds(p),r=ids.length?region(p,ids):null;
  for(const op of ['inset','extrude','solidify'])result[op]={available:!!r?.ok,reason:r?.reason||'Switch to Faces and select a connected planar region.'};
  if(r?.ok){
   if(!r.convex)for(const op of ['inset','extrude','solidify'])result[op]={available:false,reason:'This operation needs a convex planar region. Choose a simpler patch.'};
   if(r.convex){
    result.inset.reason='Create an inner face and a connected border.';
    const closed=r.boundary.every((id,i)=>{const next=r.boundary[(i+1)%r.boundary.length],key=id<next?id+':'+next:next+':'+id;return a.edges.get(key)?.length===2;});
    result.extrude={available:closed,reason:closed?'Extend this connected region outwards or use a negative depth to push inward.':'An open outer edge cannot use region Extrude. Solidify a complete planar surface instead.'};
    const plane=r.convex&&ids.length===a.faces&&a.boundaryEdges===r.boundary.length;
    result.solidify={available:plane,reason:plane?'Give this complete open planar surface closed thickness.':'Solidify needs the entire convex planar open mesh. A closed object uses face Inset and Extrude.'};
   }
  }
  result.deleteFaces={available:ids.length>0&&ids.length<a.faces,reason:ids.length===a.faces?'Use Delete object to remove an entire mesh.':ids.length?'Remove the selected triangles, leaving an open boundary.':'Switch to Faces and select the triangles to delete.'};
  result.splitEdge={available:!!selectedEdge(p),reason:'Select one edge on welded indexed topology. This is a midpoint split, not a full edge loop.'};
  result.subdivide={available:ids.length>0,reason:ids.length?'Refine triangles near the selected region; adjacent triangles are stitched. This is triangle refinement, not quad subdivision.':'Switch to Faces and select the region to refine.'};
  result.fillHole={available:boundaryVertex(p)!==null,reason:'Select a vertex or edge on one simple planar boundary ring. Only that verified ring is capped.'};
  result.repairNormals={available:a.oppositeWindingErrors>0,reason:a.oppositeWindingErrors?'Repair inconsistent shared-edge winding; it does not guess an outward direction.':'Shared-edge winding is already consistent.'};
  if(a.oppositeWindingErrors)for(const op of ops)if(op!=='repairNormals')result[op]={available:false,reason:'Repair inconsistent winding before changing this topology.'};
  return {operations:result,convert};
 }
 function current(record,strict=false){
  const state=native();return state.open&&model()===record.document&&model()?.parts===record.parts&&modelRoot===record.root&&
   partById(record.part.id)===record.part&&selection===record.part.id&&record.mesh.parent===record.root&&record.mesh.userData.atelierId===record.part.id&&
   state.documentToken===record.documentToken&&state.revision===record.revision&&record.mesh.geometry===record.geometry&&
   atelierComponentMode===record.mode&&JSON.stringify(atelierComponentIds)===record.componentIds&&JSON.stringify(atelierMeshIds)===record.objectIds&&
   (!strict||JSON.stringify(model())===record.fingerprint);
 }
 function dispose(g){if(!g||disposed.has(g))return;disposed.add(g);g.dispose();}
 function restore(record){
  // Restore only the exact geometry still owned by this preview. Never replace
  // another mesh, a newer geometry or data from a different loaded document.
  const owned=record.mesh.geometry===record.geometry&&record.mesh.parent===record.root;
  const same=model()===record.document&&modelRoot===record.root&&partById(record.part.id)===record.part;
  if(owned&&same){record.mesh.geometry=record.original;dispose(record.geometry);return true;}
  if(!owned)dispose(record.geometry);
  // A replaced document/projection owns disposal of its attached geometry.
  // The detached original is no longer referenced by a native mesh.
  if(record.mesh.geometry!==record.original)dispose(record.original);
  return false;
 }
 function inspect(){
  const objectIds=[...se350ModelTools.selection().ids];
  if(active&&!current(active))cancel('The document, selection or projection changed; preview canceled.');
  const p=partById(selection),mesh=meshFor(),t=p?.topologyMesh;
  return {selection:{partId:p?.id||null,name:p?.name||'',mode:atelierComponentMode,objectIds,objectCount:objectIds.length,ids:[...atelierComponentIds],faceIds:faceIds(p),
    vertexCount:t?t.positions.length/3:mesh?.geometry?.attributes?.position?.count||0,triangleCount:t?t.indices.length/3:(mesh?.geometry?.index?.count||mesh?.geometry?.attributes?.position?.count||0)/3},
   preview:active?{active:true,operation:active.operation,stats:clone(active.stats),selectedFaces:[...active.selectedFaces]}:{active:false,operation:null,stats:null,selectedFaces:[]},
   ...availability(),message};
 }
 function publish(text,error=false){
  if(text!==undefined)message=text;status(message,error);
  if(!notifying&&typeof window?.dispatchEvent==='function'&&typeof CustomEvent==='function'){
   notifying=true;try{window.dispatchEvent(new CustomEvent('swrlz:model-workshop-change',{detail:inspect()}));}finally{notifying=false;}
  }
 }
 function cancel(reason='Preview canceled. Source geometry and Undo are unchanged.',internal=false){
  const record=active;if(!record)return {ok:true,changed:false,cancelled:false};active=null;
  const restored=restore(record);
  if(restored&&!internal){refreshComponents();renderPreview();}
  if(!internal)publish(reason);else message=reason;
  return {ok:true,changed:false,cancelled:true};
 }
 function setComponentMode(mode){
  if(!['mesh','vertex','edge','face'].includes(mode))return fail('Choose Object, Vertex, Edge or Face mode.');
  cancel(undefined,true);
  if(borrowed()){
   atelierComponentMode=mode;atelierComponentIds=[];atelierComponentPartId=selection;
   atelierComponentGesture=null;atelierComponentDrag=null;atelierComponentOverlayClear();atelierMeshGizmoClear();atelierComponentUIRefresh();
  }else atelierComponentModeSet(mode);
  publish(mode==='mesh'?'Object mode: select and transform complete meshes.':'Select '+mode+' components in the viewport.');return {ok:true,changed:false};
 }
 function selectRegion(seedTriangle,partId=selection){
  if(active)return fail('Apply or cancel the current preview before changing its face selection.');
  if(busy())return fail('Finish the active transform or creation preview first.');
  if(typeof partId!=='string'||!partById(partId))return fail('Select an existing native mesh.');
  if(selection!==partId||(atelierMeshIds||[]).length!==1){const selected=se350ModelTools.select(partId);if(!selected?.ok)return selected;}
  const p=partById(partId),reason=blocked(p);if(reason)return fail(reason);
  if(p.kind!=='topologyMesh')return fail('Convert this plain primitive to editable topology before selecting a region.');
  const result=se430MeshOps.region(p.topologyMesh,[seedTriangle],{expand:true});if(!result.ok)return fail(result.reason);
  atelierComponentMode='face';atelierComponentPartId=partId;atelierComponentIds=[...result.triangleIds];
  atelierComponentGesture=null;atelierComponentDrag=null;refreshComponents();
  publish(result.triangleIds.length+' connected coplanar triangles selected. Inset creates an inner face; Extrude adds connected depth.');
  return {ok:true,changed:false,faceIds:[...result.triangleIds],normal:[...result.normal]};
 }
 function convert(){
  if(active)return fail('Apply or cancel this preview before converting another mesh.');
  if(busy())return fail('Finish the current gesture or creation preview first.');
  const p=partById(selection),availabilityState=availability();if(!availabilityState.convert.available)return fail(availabilityState.convert.reason);
  let source,result;try{source=atelierCourierBaseGeometry(p);result=se430MeshOps.convert(source);}
  catch{return fail('The primitive geometry could not be converted safely. No edit was applied.');}
  finally{source?.dispose?.();}
  if(!result?.ok)return fail(result?.reason||'Plain primitive conversion failed.');
  const candidate={...p,kind:'topologyMesh',topologyMesh:clone(result.data)};delete candidate.meshDensity;delete candidate.runtimeLOD;
  if(!checkPart(candidate))return fail('Converted geometry failed native source validation.');
  checkpoint();p.kind='topologyMesh';p.topologyMesh=candidate.topologyMesh;delete p.meshDensity;delete p.runtimeLOD;
  atelierComponentMode='face';atelierComponentIds=[];atelierComponentPartId=p.id;atelierMeshIds=[p.id];signalEdited();refreshComponents();
  publish('Primitive converted to welded editable topology. Plain UV coordinates were regenerated. Pick a face region; Undo restores the primitive.');
  return {ok:true,changed:true,id:p.id,stats:clone(result.stats)};
 }
 function create(kind='box'){
  if(active)return fail('Apply or cancel the pending topology preview before creating another object.');
  if(!['box','sphere','cylinder','cone'].includes(kind))return fail('Choose Cube, Sphere, Cylinder or Cone.');
  if(busy())return fail('Finish the current gesture or creation preview first.');
  const previous=partById(selection),position=previous?[Math.min(99,previous.position[0]+.8),previous.position[1],previous.position[2]]:[0,1,0];
  const labels={box:'Cube',sphere:'Sphere',cylinder:'Cylinder',cone:'Cone'};
  const draft=se390ModelCreate.draft(kind,{position,scale:[.6,.6,.6],name:labels[kind],color:'#b6a2dd',material:'matte'});
  if(!draft?.ok)return draft;const result=se390ModelCreate.commit(draft,draft.documentToken);if(!result?.ok){se390ModelCreate.cancel(draft);return result;}
  atelierComponentMode='mesh';atelierComponentIds=[];atelierComponentPartId=result.id;refreshComponents();
  publish(labels[kind]+' created as editable native geometry. Move, rotate or scale it; Convert enables face construction.');return result;
 }
 function candidate(operation,p,params){
  const ids=faceIds(p),amount=params.amount;
  if(operation==='inset')return se430MeshOps.inset(p.topologyMesh,ids,{fraction:amount??.2});
  if(operation==='extrude')return se430MeshOps.extrude(p.topologyMesh,ids,{depth:amount??.15});
  if(operation==='deleteFaces')return se430MeshOps.deleteFaces(p.topologyMesh,ids);
  if(operation==='solidify')return se430MeshOps.solidify(p.topologyMesh,ids,{thickness:amount??.1});
  if(operation==='splitEdge'){const edge=selectedEdge(p);return edge?atelierTopologyEditCandidate(p,'split-edge',edge.faceIndex,edge.edgeSlot):fail('Select one welded edge first.');}
  if(operation==='fillHole'){const vertex=boundaryVertex(p);return vertex!==null?atelierBoundaryCapCandidate(p,vertex):fail('Select a vertex or edge on the boundary ring.');}
  if(operation==='repairNormals')return atelierTopologyReorientCandidate(p);
  if(operation==='subdivide'){
   const vertices=[...new Set(ids.flatMap(f=>p.topologyMesh.indices.slice(f*3,f*3+3)))],points=vertices.map(id=>p.topologyMesh.positions.slice(id*3,id*3+3));
   const center=[0,1,2].map(k=>points.reduce((sum,pt)=>sum+pt[k],0)/points.length),radius=Math.max(.05,...points.map(pt=>Math.hypot(...pt.map((n,k)=>n-center[k]))+.001));
   return atelierAdaptiveRefineCandidate(p,center,radius,amount??.25);
  }
  return fail('This topology operation is not implemented.');
 }
 function preview(operation,params={}){
  if(!ops.includes(operation)||!params||typeof params!=='object'||Array.isArray(params)||Object.keys(params).some(k=>k!=='amount')||
   Object.hasOwn(params,'amount')&&(typeof params.amount!=='number'||!Number.isFinite(params.amount)))return fail('Choose a supported topology operation and a finite local amount.');
  if(active&&!current(active,true)){cancel('The source changed; preview canceled.');return fail('The source changed. Select the current mesh again.');}
  if(busy())return fail('Finish the current transform, sculpt stroke or creation preview first.');
  const available=availability().operations[operation];if(!available.available)return fail(available.reason);
  const p=partById(selection);let result;try{result=candidate(operation,p,params);}catch{return fail('The geometry candidate could not be constructed safely.');}
  if(!result?.ok)return fail(result?.reason||'The selected operation could not produce valid geometry.');
  const data=clone(result.data),next={...p,topologyMesh:data};delete next.runtimeLOD;
  const checked=atelierTopologyAudit(data);
  if(!checkPart(next)||!checked.ok||checked.zeroAreaFaces||checked.nonManifoldEdges||checked.oppositeWindingErrors)return fail('The candidate failed native topology validation. No edit was applied.');
  if(JSON.stringify(data)===JSON.stringify(p.topologyMesh))return fail('This operation does not change the selected geometry.');
  let geometry;
  try{geometry=atelierTopologyGeometry(next);}catch{return fail('The native preview geometry could not be allocated. No edit was applied.');}
  if(!geometry?.isBufferGeometry){geometry?.dispose?.();return fail('The native preview geometry is unavailable. No edit was applied.');}
  geometry.addEventListener('dispose',()=>disposed.add(geometry));
  const old=active,previousGeometry=old?.geometry,mesh=meshFor(),state=native();
  const record=old||{document:model(),parts:model().parts,part:p,root:modelRoot,mesh,original:mesh.geometry,
   documentToken:state.documentToken,revision:state.revision,fingerprint:JSON.stringify(model()),mode:atelierComponentMode,componentIds:JSON.stringify(atelierComponentIds),objectIds:JSON.stringify(atelierMeshIds)};
  record.operation=operation;record.data=data;record.stats={verticesBefore:p.topologyMesh.positions.length/3,verticesAfter:data.positions.length/3,facesBefore:p.topologyMesh.indices.length/3,facesAfter:data.indices.length/3,...clone(result.stats||{})};
  record.selectedFaces=Array.isArray(result.selectedFaces)?[...result.selectedFaces]:[];
  record.geometry=geometry;mesh.geometry=geometry;active=record;
  // Keep a single allocation while sliders update the same pending preview.
  if(previousGeometry)dispose(previousGeometry);
  atelierComponentOverlayClear();atelierMeshGizmoClear();
  renderPreview();
  publish('Preview '+operation+' · '+record.stats.facesBefore+' → '+record.stats.facesAfter+' triangles. Apply commits one Undo step; Cancel keeps the source.');
  return {ok:true,changed:false,operation,stats:clone(record.stats)};
 }
 function apply(){
  const record=active;if(!record)return fail('Preview an operation before applying it.');
  if(!current(record,true)){cancel('The document or selection changed; nothing applied.');return fail('The preview is stale. No edit was applied.');}
  if(busy())return fail('Finish the active gesture before applying this topology preview.');
  const candidatePart={...record.part,topologyMesh:clone(record.data)};delete candidatePart.runtimeLOD;
  const checked=atelierTopologyAudit(candidatePart.topologyMesh);
  if(!checkPart(candidatePart)||!checked.ok||checked.zeroAreaFaces||checked.nonManifoldEdges||checked.oppositeWindingErrors)return fail('The preview no longer passes native topology validation.');
  active=null;restore(record);checkpoint();record.part.topologyMesh=candidatePart.topologyMesh;delete record.part.runtimeLOD;
  selection=record.part.id;atelierMeshIds=[selection];signalEdited();atelierComponentPartId=selection;
  atelierComponentMode=record.selectedFaces.length?'face':record.mode;atelierComponentIds=[...record.selectedFaces];refreshComponents();
  publish('Applied '+record.operation+' to native geometry. Undo restores the previous mesh; the resulting face region remains selected.');
  return {ok:true,changed:true,id:selection,selectedFaces:[...record.selectedFaces],stats:clone(record.stats)};
 }
 const priorRender=renderParts;
 renderParts=function(...args){if(active)cancel('Projection rebuilt; topology preview canceled.',true);return priorRender.apply(this,args);};
 const priorClose=close;
 close=function(...args){cancel('Model Studio closed; topology preview canceled.',true);return priorClose.apply(this,args);};
 const priorHistory=historyStep;
 historyStep=function(...args){if(active){cancel('Preview canceled. Press Undo or Redo again to change committed history.');return;}return priorHistory.apply(this,args);};
 const priorSelect=select;
 select=function(...args){if(active)cancel('Selection changed; topology preview canceled.',true);return priorSelect.apply(this,args);};
 const priorPointer=pointerDown;
 pointerDown=function(event,...args){if(active){if(event?.cancelable)event.preventDefault();publish('Apply or Cancel the topology preview before editing the viewport.');return;}return priorPointer.call(this,event,...args);};
 const priorComponentUIRefresh=atelierComponentUIRefresh;
 atelierComponentUIRefresh=function(...args){
  const result=priorComponentUIRefresh.apply(this,args);
  if(!refreshQueued&&!notifying&&typeof queueMicrotask==='function'){
   refreshQueued=true;queueMicrotask(()=>{
    refreshQueued=false;if(notifying||typeof window?.dispatchEvent!=='function'||typeof CustomEvent!=='function')return;
    notifying=true;try{window.dispatchEvent(new CustomEvent('swrlz:model-workshop-change',{detail:inspect()}));}finally{notifying=false;}
   });
  }
  return result;
 };
 return Object.freeze({inspect,create,convert,selectRegion,setComponentMode,preview,apply,cancel});
})();
/* SE430_MODEL_WORKSHOP_BRIDGE_END */
