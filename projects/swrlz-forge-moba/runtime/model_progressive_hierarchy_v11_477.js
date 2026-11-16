/* SE477_TOOL_LIST_START */
function toolList(family){
 // The flyout contains modeling OPERATIONS, never component or ring-selection
 // types. The native inspector retains controls for configuring each tool.
 if(family==='Sculpt'){
  return [
   ['extrude','Extrude'],['inset','Inset'],['subdivide','Subdivide'],
   ['splitEdge','Split edge'],['solidify','Solidify'],['deleteFaces','Delete faces'],
   ['fillHole','Fill hole'],['repairNormals','Repair normals']
  ].map(([kind,name])=>({name,kind}));
 }
 if(family==='Topology'){
  return meshOps.map(([kind,name])=>({name,kind}));
 }
 const fromNative=window.SWYRL_E_CONTEXT?.groups?.()?.[family]||[];
 return [...new Set(fromNative.filter(x=>typeof x==='string'&&x.trim()))]
  .map(name=>({name,kind:'native'}));
}
/* SE477_TOOL_LIST_END */

/* SE477_TOP_BARS_START */
function specificModes(){
 if(state.operation)return [['vertex','Vertex'],['edge','Edge'],['face','Face']];
 if(state.toolType==='manual')return meshOps.map(x=>[x[0],x[1]]);
 return [['settings','Settings']];
}
function renderTop(){
 if(!state)return;
 state.top.hidden=!state.tool;
 state.top.replaceChildren();
 if(!state.tool){renderShapes();return;}
 const label=document.createElement('strong');
 label.className='se474-top-label';label.textContent=state.tool+' · Selection';
 state.top.append(label);
 for(const [value,name]of specificModes()){
  state.top.append(makeButton(name,'mode',value,
   state.operation?state.selectionType===value:state.mode===value));
 }
 state.top.append(state.feedback);
 renderShapes();
}
function selectionShapes(){
 if(state.selectionType==='vertex')return [['single','Single vertex'],['ring','Vertex ring'],['fill','Filled vertex ring']];
 if(state.selectionType==='face')return [['single','Single face'],['region','Face region']];
 if(state.selectionType==='edge')return [['single','Single edge'],['box','Box select'],['lasso','Lasso']];
 return [];
}
function renderShapes(){
 const row=state?.shapeBar;if(!row)return;
 row.hidden=!state.operation||!state.selectionType;
 row.replaceChildren();
 if(row.hidden)return;
 const label=document.createElement('strong');label.className='se477-selection-label';
 label.textContent=state.selectionType==='vertex'?'Vertex selection':
  state.selectionType==='face'?'Face selection':'Edge selection';
 row.append(label);
 for(const [value,name]of selectionShapes()){
  row.append(makeButton(name,'shape',value,state.shape===value));
 }
}
/* SE477_TOP_BARS_END */

/* SE477_CHOOSE_TOOL_START */
function chooseTool(name,kind){
 if(previewPending()){feedback('Apply or Cancel the preview before selecting another tool.');return;}
 const operation=meshOps.some(x=>x[0]===kind);
 if(operation){
  if(!chooseContext('Topology','Manual mesh modeling'))return;
  if(!nativeOperation(kind))return feedback('This operation is not available in the native mesh editor.');
  if(!nativeMode('vertex'))return;
 }else if(kind==='native'){
  if(!chooseContext(state.family,name))return;
 }else return;
 state.tool=name;state.toolType=kind==='native'&&/manual mesh modeling/i.test(name)?'manual':kind;
 state.operation=operation;state.selectionType=operation?'vertex':'';
 state.shape=operation?'single':'';
 state.mode=operation?'vertex':'';
 state.panel.dataset.se477SelectionType=state.selectionType||'none';
 state.panel.dataset.se477SelectionShape=state.shape||'none';
 state.panel.dataset.se477Operation=operation?'true':'false';
 // The flyout otherwise overlays the second horizontal mode strip on phones.
 // Collapse it after choosing an operation; the same family button reopens it
 // without changing the active operation or viewport selection.
 state.flyoutOpen=false;
 setOpen(false);renderFlyout();renderTop();
 if(operation){
  const r=window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
  feedback(r?.ok?'Tap a visible point to select it. Other selection types are above.':
   r?.reason||'Tap a model part to reveal its vertices.');
 }else feedback('Choose a tool option in the top bar.');
}
/* SE477_CHOOSE_TOOL_END */

/* SE477_SPECIFIC_SELECTION_START */
function setNativePicker(tool){
 const control=state.panel.querySelector('[data-component-tool="'+tool+'"]');
 if(control)control.click();
}
function selectSpecific(type){
 if(!state?.tool)return;
 if(previewPending()){feedback('Apply or Cancel the preview before changing selection type.');return;}
 if(!state.operation){
  state.mode=type;setOpen(type==='settings');renderTop();return;
 }
 if(!['vertex','edge','face'].includes(type))return;
 if(!nativeMode(type))return;
 state.selectionType=type;state.mode=type;state.shape='single';
 state.panel.dataset.se477SelectionType=type;
 state.panel.dataset.se477SelectionShape='single';
 if(type==='vertex'){
  const r=window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
  feedback(r?.ok?'Vertices visible. Tap a point, or select a vertex ring below.':
   r?.reason||'Tap a mesh to reveal vertices.');
 }else if(type==='face'){
  feedback('Tap a face. Face Inset and Extrude use the native Preview and Apply controls.');
 }else{
  feedback('Tap an edge. Native Inset/Extrude requires faces; edge editing is selection only.');
 }
 setNativePicker('tap');setOpen(type==='face');renderTop();
}
function selectShape(shape){
 if(!state?.operation||!state.selectionType)return;
 if(previewPending()){feedback('Apply or Cancel the preview before switching selection shapes.');return;}
 const allowed=selectionShapes().map(([value])=>value);
 if(!allowed.includes(shape))return;
 state.shape=shape;state.panel.dataset.se477SelectionShape=shape;
 const type=state.selectionType;
 if(type==='vertex'){
  if(!nativeMode('vertex'))return;
  const result=window.SWYRL_ENGINE_VERTEX_ENTRY_477?.activate?.();
  setNativePicker('tap');
  if(shape==='single'){
   feedback(result?.ok?'Tap individual vertices. Inset requires a face; Extrude uses a face or valid boundary ring.':
    result?.reason||'Tap a mesh, then select vertices.');
  }else{
   // Native ring selection is topology-only. It uses one selected center
   // vertex and will not invent a ring on a UV-only primitive.
   const details=state.panel.querySelector('#se466RingControls');
   if(details)details.open=true;
   if(result?.ok!==false)selectRing(shape==='fill'?'fill':'outline');
   else feedback(result?.reason||'Choose an editable topology mesh to use ring modes.');
  }
 }else if(type==='face'){
  setNativePicker('tap');
  if(shape==='region'){
   const s=inspected(),face=s?.selection?.faceIds?.[0],part=s?.selection?.partId;
   if(Number.isInteger(face)){
    const result=workshop()?.selectRegion?.(face,part);
    if(result?.ok===false)feedback(result.reason||result.error||'Cannot expand region.');
   }else feedback('Tap a face first, then choose Face region.');
  }else feedback('Tap one face. Use the native Preview / Apply controls for this operation.');
 }else if(type==='edge'){
  setNativePicker(shape==='box'?'box':shape==='lasso'?'lasso':'tap');
  feedback('Select edges. Standard Inset/Extrude geometry requires Face mode.');
 }
 setOpen(type==='face'||type==='vertex'&&shape!=='single');
 renderShapes();
}
/* SE477_SPECIFIC_SELECTION_END */