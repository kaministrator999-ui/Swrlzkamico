/* SE477_VERTEX_ENTRY_START */
// Native ModelAtelier scope. Reuse selected-part ownership, native vertex
// topology, 2D touch picker, shader points, and original Undo transactions.
(function se477VertexEntryInstall(){
 'use strict';
 function candidates(){
  const ids=new Set(),out=[];
  for(const mesh of (modelRoot?.children||[])){
   const id=mesh?.userData?.atelierId;
   if(!mesh?.isMesh||mesh.visible===false||typeof id!=='string'||ids.has(id)||!partById(id))continue;
   ids.add(id);out.push({id,mesh});
  }
  return out;
 }
 function refresh(){
  if(atelierComponentMode==='vertex'&&atelierComponentSupported()){
   atelierComponentRefresh();
   return true;
  }
  return false;
 }
 function activate(){
  if(atelierComponentMode!=='vertex')return {ok:false,reason:'Choose Vertex mode first.'};
  if(atelierComponentSupported()){
   refresh();
   return {ok:true,partId:selection,pointCount:atelierComponentTopology(atelierComponentMesh()).vertices.length};
  }
  const available=candidates();
  if(available.length!==1)return {
   ok:false,reason:available.length?'Tap the model part you want to edit; its vertices will appear.':
    'No editable mesh is visible. Open or create a model part first.',
   candidates:available.length
  };
  const target=available[0];
  const result=se350ModelTools.select(target.id);
  if(result?.ok===false)return {ok:false,reason:result.reason||result.error||'Cannot select mesh.'};
  // Native selection can reset component mode. Restore vertex editing only
  // when needed; do not clear a center/vertex selection on repeated taps.
  if(atelierComponentMode!=='vertex')atelierComponentModeSet('vertex');
  if(!atelierComponentSupported())return {
   ok:false,reason:'This part cannot expose editable vertices while its refinement layers are active.'
  };
  refresh();
  return {ok:true,partId:selection,pointCount:atelierComponentTopology(atelierComponentMesh()).vertices.length};
 }
 function pick(e){
  if(atelierComponentMode!=='vertex'||atelierComponentSupported()||!camera||!raycaster||!modelRoot)return false;
  const available=candidates();
  if(!available.length)return false;
  const p=point(e);
  mouse.set(p.x,p.y);raycaster.setFromCamera(mouse,camera);
  const hit=raycaster.intersectObjects(available.map(v=>v.mesh),false)[0];
  const id=hit?.object?.userData?.atelierId;
  if(!id||!partById(id))return false;
  const result=se350ModelTools.select(id);
  if(result?.ok===false)return false;
  if(atelierComponentMode!=='vertex')atelierComponentModeSet('vertex');
  refresh();
  return atelierComponentSupported();
 }
 // Only a tap in vertex mode with no active native mesh needs picking.
 // The original handler still owns picking the nearest projected vertex.
 const previousUp=atelierComponentPointerUp;
 atelierComponentPointerUp=function(event){
  const g=atelierComponentGesture;
  if(atelierComponentMode==='vertex'&&!atelierComponentSupported()&&g&&g.pointerId===event?.pointerId&&!g.moved){
   pick(event);
  }
  return previousUp.apply(this,arguments);
 };
 window.SWYRL_ENGINE_VERTEX_ENTRY_477=Object.freeze({
  activate,
  inspect:()=>{
   const supported=atelierComponentSupported(),mesh=supported?atelierComponentMesh():null;
   const topo=mesh?atelierComponentTopology(mesh):null;
   return {mode:atelierComponentMode,partId:selection||null,supported,
    availableMeshes:candidates().length,visiblePointOverlay:!!atelierComponentOverlay?.children?.some(x=>x.isPoints),
    pointCount:topo?.vertices?.length||0,selectedCount:atelierComponentIds.length};
  }
 });
})();
/* SE477_VERTEX_ENTRY_END */