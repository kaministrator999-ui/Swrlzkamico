/* SE481_TEXTURED_EDITABLE_COPY_START */
// ModelAtelier closure-owned, UV-faithful topology working copy.
// Keeps the original authored model part in the project, hidden but recoverable.
const se481TexturedEditable=(()=>{
 'use strict';
 const MAX_VERTICES=9000,MAX_FACES=16000;
 const native=()=>window.SWYRL_ENGINE_MODEL_WORKSHOP;
 const fail=reason=>({ok:false,reason,error:reason});
 const sourceKeys=['uvPaintPNG','uvPaintOffset','uvPaintRepeat','uvPaintMaxSize',
  'uvPaintSourceW','uvPaintSourceH','uvPaintSourceBytes'];
 function selected(){
  const p=partById(selection);
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData?.atelierId===selection);
  return {p,mesh};
 }
 function bounds(g){
  const pos=g?.getAttribute?.('position'),uv=g?.getAttribute?.('uv');
  const count=g?.index?.count||pos?.count||0,faces=count/3;
  if(!pos||!uv||pos.itemSize!==3||uv.itemSize!==2||pos.count!==uv.count)
   return fail('This mesh needs complete existing UV coordinates to preserve its texture.');
  if(count<3||count%3||faces>MAX_FACES)return fail(
   'The selected mesh has '+Math.floor(faces)+' triangles; UV-preserving editable copies currently support at most '+MAX_FACES+'. Original unchanged.');
  if(pos.count>180000)return fail('This source exceeds the safe geometry inspection limit.');
  if(g.getAttribute('skinIndex')||g.getAttribute('skinWeight')||
    g.getAttribute('color')||Object.keys(g.morphAttributes||{}).length)
   return fail('Rigged, morphed or vertex-painted geometry needs a separate baking workflow; original unchanged.');
  if((g.groups||[]).length>1)return fail('Multi-material geometry needs a per-material UV-preserving topology workflow.');
  return {ok:true,vertices:pos.count,faces};
 }
 function getStatus(){
  const {p,mesh}=selected();
  const linked=p?.se481SourceId?partById(p.se481SourceId):null;
  const partner=p?.se481WorkId?partById(p.se481WorkId):null;
  if(linked||partner)return {
   available:false,working:!!linked,paired:true,sourceId:linked?.id||p.id,
   copyId:linked?p.id:partner.id,
   reason:'Editable source and working copy are already linked.'
  };
  if(!p||!mesh)return {available:false,reason:'Select one model part.'};
  if(native()?.inspect?.()?.preview?.active)return {available:false,reason:'Apply or Cancel the current preview first.'};
  if((atelierMeshIds||[]).filter(id=>partById(id)).length>1)
   return {available:false,reason:'Select one mesh, not a multi-object group.'};
  if(p.kind==='topologyMesh')return {available:false,reason:'This part is already editable topology.'};
  if(!p.uvPaintPNG)return {available:false,reason:'This selected part has no painted UV texture.'};
  if(p.refinementLayers?.some(x=>x.enabled))
   return {available:false,reason:'Active procedural refinement must be baked separately before preserving its UV geometry.'};
  const g=mesh.geometry,valid=bounds(g);
  return valid.ok?{available:true,hasPaint:true,reason:'Preserve original texture, positions, UVs and material in an editable working copy.',faces:valid.faces,vertices:valid.vertices}:{
   available:false,hasPaint:true,reason:valid.reason};
 }
 function build(g){
  const allowed=bounds(g);if(!allowed.ok)return allowed;
  const pos=g.getAttribute('position'),uv=g.getAttribute('uv'),ix=g.getIndex();
  const map=new Map(),positions=[],uvs=[],indices=[];
  for(let k=0;k<allowed.faces*3;k+=3){
   const triangle=[];
   for(let j=0;j<3;j++){
    const i=ix?ix.getX(k+j):k+j;
    if(!Number.isInteger(i)||i<0||i>=pos.count)return fail('Mesh indices are invalid; original unchanged.');
    const values=[pos.getX(i),pos.getY(i),pos.getZ(i),uv.getX(i),uv.getY(i)];
    if(values.some((v,axis)=>!Number.isFinite(v)||Math.abs(v)>(axis<3?100:20)))
     return fail('Nonfinite or unsupported source UV/position values; original unchanged.');
    // Exact float attribute values are the identity. Equal positions with
    // DIFFERENT UVs must remain split so the painted atlas does not smear.
    const key=values.join(',');
    let id=map.get(key);
    if(id===undefined){
     id=positions.length/3;map.set(key,id);
     if(id>=MAX_VERTICES)return fail('UV seams need more than '+MAX_VERTICES+
       ' editable vertices. The original textured mesh was kept intact.');
     positions.push(...values.slice(0,3));uvs.push(...values.slice(3));
    }
    triangle.push(id);
   }
   if(new Set(triangle).size<3)return fail('The source contains a degenerate UV/topology triangle; no copy created.');
   indices.push(...triangle);
  }
  const data={positions,uvs,indices};
  const audit=se430MeshOps.audit(data);
  if(!audit.ok)return fail(audit.reason||'The native topology validator rejected the source.');
  return {ok:true,data,faces:allowed.faces,vertices:positions.length/3,
   originalUVsPreserved:true,atlasSeamsPreserved:true};
 }
 function uniqueId(){
  let id;
  do{id='uv-edit-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8);}
  while(partById(id));
  return id;
 }
 function prepare(){
  const state=getStatus();
  if(!state.available)return fail(state.reason||'No safe UV-preserving copy available.');
  const {p,mesh}=selected();
  const initial=p,initialId=p.id,document=model(),root=modelRoot;
  if(!document||document.parts.length>=MODEL_ATELIER_LIMIT)
   return fail('Model parts limit reached; cannot retain the original and an editable copy.');
  const derived=build(mesh.geometry);
  if(!derived.ok)return derived;
  if(selection!==initialId||model()!==document||partById(initialId)!==initial||
     modelRoot!==root||native()?.inspect?.()?.preview?.active)
   return fail('The source changed during conversion; no project edit was made.');
  const id=uniqueId();
  const copy={id,name:(p.name||'Mesh').slice(0,80)+' · Editable',
   group:p.group||'Editable UV mesh',kind:'topologyMesh',
   topologyMesh:derived.data,
   position:[...p.position],rotation:[...p.rotation],scale:[...p.scale],
   color:p.color,material:p.material,se481SourceId:p.id};
  for(const key of sourceKeys)if(Object.prototype.hasOwnProperty.call(p,key))
   copy[key]=structuredClone(p[key]);
  if(!checkPart(copy))return fail('Native saved-model validation rejected the UV-preserving copy; original unchanged.');
  // Native Undo owns this transaction. The original part is retained in the
  // saved document but hidden to prevent z-fighting/raycast double selection.
  checkpoint();
  p.se481SourceHidden=true;p.se481WorkId=id;
  document.parts.push(copy);
  selection=id;atelierMeshIds=[id];atelierMeshAdding=false;
  atelierComponentMode='vertex';atelierComponentPartId=id;atelierComponentIds=[];
  atelierComponentGesture=null;atelierComponentDrag=null;
  signalEdited();
  atelierComponentRefresh();
  refreshSwitch();
  status('UV-preserving editable copy ready: '+derived.vertices+
   ' vertices, '+derived.faces+' triangles. Texture and UV Slide retained. Original hidden and recoverable.');
  return {ok:true,changed:true,copyId:id,sourceId:p.id,
   vertices:derived.vertices,faces:derived.faces,
   originalUVsPreserved:true,originalSourceRetained:true};
 }
 function switchSource(){
  const p=partById(selection);
  if(!p)return fail('Select the source or its editable copy first.');
  const src=p.se481SourceId?partById(p.se481SourceId):p.se481WorkId?p:null;
  const copy=p.se481SourceId?p:p.se481WorkId?partById(p.se481WorkId):null;
  if(!src||!copy)return fail('This part is not linked to an editable copy.');
  if(native()?.inspect?.()?.preview?.active)
   return fail('Apply or Cancel the geometry preview before switching.');
  const showOriginal=selection===copy.id;
  checkpoint();
  src.se481SourceHidden=!showOriginal;
  copy.se481WorkHidden=showOriginal;
  const id=showOriginal?src.id:copy.id;
  selection=id;atelierMeshIds=[id];atelierMeshAdding=false;
  atelierComponentMode=showOriginal?'mesh':'vertex';
  atelierComponentIds=[];atelierComponentPartId=id;
  atelierComponentGesture=null;atelierComponentDrag=null;
  signalEdited();atelierComponentRefresh();refreshSwitch();
  status(showOriginal?
    'Original textured source visible; editable copy preserved. Tap Return to editable copy to resume.':
    'Editable copy visible with original UVs and texture; source remains preserved.');
  return {ok:true,visible:showOriginal?'source':'editable',sourceId:src.id,copyId:copy.id};
 }
 const baseRender=renderParts;
 renderParts=function(...args){
  const result=baseRender.apply(this,args);
  if(!modelRoot)return result;
  for(const child of modelRoot.children){
   if(!child.isMesh)continue;
   const part=partById(child.userData?.atelierId);
   if(part?.se481SourceHidden||part?.se481WorkHidden)child.visible=false;
  }
  return result;
 };
 let observed=null;
 function refreshSwitch(){
  const row=document.getElementById('se477SelectionShapes');
  if(!row||row.hidden)return;
  const part=partById(selection),copy=!!part?.se481SourceId,source=!!part?.se481WorkId;
  let btn=row.querySelector('#se481OriginalSourceToggle');
  if(!copy&&!source){btn?.remove();return;}
  if(!btn){
   btn=document.createElement('button');btn.type='button';btn.id='se481OriginalSourceToggle';
   btn.className='se481-source-toggle';
   btn.addEventListener('pointerdown',e=>e.stopPropagation());
   btn.addEventListener('click',e=>{
    e.stopPropagation();const r=switchSource();
    if(!r.ok)status(r.reason,true);
   });
   row.append(btn);
  }
  const label=copy?'Show original model':'Return to editable copy';
  if(btn.textContent!==label)btn.textContent=label;
  btn.title='Switch between the preserved original model and its UV-faithful editable copy.';
 }
 function attach(){
  const row=document.getElementById('se477SelectionShapes');
  if(row&&observed!==row){
   observed=row;
   new MutationObserver(refreshSwitch).observe(row,{childList:true});
  }
  refreshSwitch();
 }
 if(document.readyState==='loading')
  document.addEventListener('DOMContentLoaded',attach,{once:true});
 else attach();
 window.addEventListener('swrlz:model-workshop-change',attach);
 function inspectFidelity(){
  const p=partById(selection);
  const src=p?.se481SourceId?partById(p.se481SourceId):p;
  const copy=src?.se481WorkId?partById(src.se481WorkId):p?.se481SourceId?p:null;
  const a=src&&modelRoot?.children.find(m=>m.isMesh&&m.userData?.atelierId===src.id);
  const b=copy&&modelRoot?.children.find(m=>m.isMesh&&m.userData?.atelierId===copy.id);
  if(!a||!b)return {ok:false,reason:'No paired rendered source and working copy.'};
  const ga=a.geometry,gb=b.geometry;
  const pa=ga.getAttribute('position'),pb=gb.getAttribute('position');
  const ua=ga.getAttribute('uv'),ub=gb.getAttribute('uv');
  const count=ga.index?.count||pa.count;
  if(count!==(gb.index?.count||pb.count))
   return {ok:false,reason:'Triangle count changed',sourceCorners:count};
  let uvDifferences=0,positionDifferences=0;
  for(let k=0;k<count;k++){
   const ia=ga.index?ga.index.getX(k):k,ib=gb.index?gb.index.getX(k):k;
   for(let j=0;j<2;j++)if(Math.abs(
    (j?ua.getY(ia):ua.getX(ia))-(j?ub.getY(ib):ub.getX(ib)))>1e-6)uvDifferences++;
   for(let j=0;j<3;j++)if(Math.abs(
    pa.getComponent(ia,j)-pb.getComponent(ib,j))>1e-6)positionDifferences++;
  }
  const sourceMat=Array.isArray(a.material)?a.material[0]:a.material;
  const copyMat=Array.isArray(b.material)?b.material[0]:b.material;
  const matchingPaint=!!src.uvPaintPNG&&src.uvPaintPNG===copy.uvPaintPNG;
  const sourceMap=sourceMat?.map,copyMap=copyMat?.map;
  return {ok:!uvDifferences&&!positionDifferences&&matchingPaint&&!!sourceMap&&!!copyMap,
   triangleCorners:count,uvDifferences,positionDifferences,matchingPaint,
   sourceHasMap:!!sourceMap,copyHasMap:!!copyMap,
   sourceHidden:!a.visible,copyVisible:b.visible,
   sameUVOffset:JSON.stringify(src.uvPaintOffset||[0,0])===JSON.stringify(copy.uvPaintOffset||[0,0]),
   sameUVRepeat:JSON.stringify(src.uvPaintRepeat||[1,1])===JSON.stringify(copy.uvPaintRepeat||[1,1])};
 }
 window.SWYRL_ENGINE_TEXTURED_TOPOLOGY_481=Object.freeze({
  inspect:getStatus,prepare,switchSource,build,inspectFidelity,
  refresh:attach,
  inspectSource:()=>{
   const p=partById(selection);
   const src=p?.se481SourceId?partById(p.se481SourceId):p;
   const copy=src?.se481WorkId?partById(src.se481WorkId):p?.se481SourceId?p:null;
   return {selectedId:selection,sourceId:src?.id||null,copyId:copy?.id||null,
    sourceHidden:!!src?.se481SourceHidden,copyHidden:!!copy?.se481WorkHidden,
    sourceTexture:src?.uvPaintPNG||null,copyTexture:copy?.uvPaintPNG||null,
    sourceUVSettings:src?[src.uvPaintOffset,src.uvPaintRepeat]:null,
    copyUVSettings:copy?[copy.uvPaintOffset,copy.uvPaintRepeat]:null,
    sourceKind:src?.kind||null,copyKind:copy?.kind||null,
    copyTopology:copy?.topologyMesh?{
     vertices:copy.topologyMesh.positions.length/3,
     faces:copy.topologyMesh.indices.length/3,
     uvs:copy.topologyMesh.uvs.length/2
    }:null};
  }
 });
})();
 /* SE481_TEXTURED_EDITABLE_COPY_END */
