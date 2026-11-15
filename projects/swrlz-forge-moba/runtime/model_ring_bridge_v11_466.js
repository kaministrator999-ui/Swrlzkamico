/* SE466_RING_BRIDGE_START */
 let ringAnchor=null;
 function selectedRingVertices(p=partById(selection)){
  if(p?.kind!=='topologyMesh'||atelierComponentMode!=='vertex'||atelierComponentPartId!==selection)return [];
  const mesh=meshFor(),top=mesh&&atelierComponentTopology(active?.mesh===mesh?{geometry:active.original}:mesh);
  if(!top?.vertices)return [];
  return [...new Set(atelierComponentIds.map(i=>top.vertices[i]).filter(id=>Number.isInteger(id)&&id>=0&&id<p.topologyMesh.positions.length/3))];
 }
 function setRingAnchor(){
  if(active)return fail('Apply or Cancel the current geometry preview before setting a ring center.');
  if(busy())return fail('Finish the active transform or gesture first.');
  const p=partById(selection),reason=blocked(p);if(reason)return fail(reason);
  const ids=selectedRingVertices(p);
  if(ids.length!==1)return fail('Switch to Vertex mode and select exactly one vertex for the ring center.');
  ringAnchor={seed:ids[0],partId:p.id,documentToken:native().documentToken,revision:native().revision};
  publish('Ring center set at vertex '+ids[0]+'. Expand connected rings and choose Outline, Fill, or an arc.');
  return {ok:true,changed:false,seed:ids[0],message:'Ring center saved. Set radius and arc, then select.'};
 }
 function selectRing(options={}){
  if(active)return fail('Apply or Cancel the current geometry preview before changing a ring selection.');
  if(busy())return fail('Finish the active transform or sculpt gesture first.');
  const p=partById(selection),reason=blocked(p);if(reason)return fail(reason);
  if(!p||p.kind!=='topologyMesh')return fail('Convert to editable topology and select a center vertex first.');
  const state=native(),anchor=ringAnchor;
  if(!anchor||anchor.partId!==selection||anchor.documentToken!==state.documentToken||anchor.revision!==state.revision)
   return fail('Select one vertex and use Set center first. A model edit invalidates the previous center.');
  const result=se466RingKernel.ringSelect(p.topologyMesh,anchor.seed,options);
  if(!result.ok)return fail(result.reason);
  const mesh=meshFor(),top=mesh&&atelierComponentTopology(mesh);
  if(!top?.vertices)return fail('Component vertex mapping is unavailable; source selection was not changed.');
  const selectedKeys=new Set(result.vertexIds.map(i=>top.keys[i]));
  const components=top.vertices.map((vertex,i)=>selectedKeys.has(top.keys[vertex])?i:-1).filter(i=>i>=0);
  if(!components.length)return fail('No matching UI vertices were found for the selected ring.');
  atelierComponentMode='vertex';atelierComponentPartId=p.id;atelierComponentIds=components;
  atelierComponentGesture=null;atelierComponentDrag=null;refreshComponents();
  publish(components.length+' real mesh vertices selected using '+result.mode+' '+result.steps+'-step radius'+(result.arcSweep<360?' and '+result.arcSweep+'° arc':'')+'.');
  return {ok:true,changed:false,vertexIds:result.vertexIds,componentIds:components,
   message:components.length+' vertices selected. Use Move, Scale, Rotate, or refine geometry.'};
 }
/* SE466_RING_BRIDGE_END */