// §E v11.23 local topology refinement. Deterministically rebuilds crack-free
// triangle edges from a saved named lasso. Original mesh topology is immutable;
// disabling/removing a layer restores the original on the next render.
const atelierRefineMaxLayers=3,atelierRefineMaxTriangles=180000;
function atelierRefineValid(p){
 const layers=p.refinementLayers;
 if(layers===undefined)return true;
 if(!Array.isArray(layers)||layers.length>atelierRefineMaxLayers)return false;
 const ids=new Set();
 return layers.every(layer=>{
   if(!layer||typeof layer!=='object'||Array.isArray(layer)||
      Object.keys(layer).some(k=>!['enabled','id','level','regionId','locked'].includes(k))
      ||!['enabled','id','level','regionId'].every(k=>Object.prototype.hasOwnProperty.call(layer,k))
      ||(layer.locked!==undefined&&typeof layer.locked!=='boolean')
      ||typeof layer.id!=='string'||layer.id.length>60||ids.has(layer.id)
      ||typeof layer.regionId!=='string'||layer.regionId.length>60
      ||!Number.isInteger(layer.level)||layer.level<1||layer.level>2
      ||typeof layer.enabled!=='boolean')return false;
   ids.add(layer.id);
   return (p.sculptLassos||[]).some(r=>r.id===layer.regionId);
 });
}
// Structural lock blocks deletion/reordering of this layer, independently
// from user-controlled show/hide. Its referenced surface lasso is a separate
// editable object: locking detail does NOT implicitly lock that lasso.
function atelierRefineLayerLocked(layer){return layer?.locked===true;}
function atelierRefineCanMove(layers,index,target){
 return Array.isArray(layers)&&Number.isInteger(index)&&
   Number.isInteger(target)&&index>=0&&target>=0&&
   index<layers.length&&target<layers.length&&Math.abs(target-index)===1&&
   !atelierRefineLayerLocked(layers[index])&&!atelierRefineLayerLocked(layers[target]);
}
// Duplicate is a copy of saved density instructions, NOT an extra live
// subdivision operation until the owner enables it. Distinct ID and original
// layer stay untouched. Caller commits only if native part validation passes.
function atelierRefineDuplicateCandidate(p,index,newId){
 const all=p?.refinementLayers;
 if(!Array.isArray(all)||!Number.isInteger(index)||index<0||index>=all.length||
    all.length>=atelierRefineMaxLayers||typeof newId!=='string'||
    newId.length<1||newId.length>60||all.some(l=>l.id===newId))
   return {ok:false,reason:'Invalid layer, duplicate ID or three-layer limit'};
 const selected=all[index];
 const duplicated={id:newId,regionId:selected.regionId,
   level:selected.level,enabled:false,locked:false};
 const layers=all.slice();
 layers.splice(index+1,0,duplicated);
 return atelierRefineValid({...p,refinementLayers:layers})?
   {ok:true,layers,index:index+1}:
   {ok:false,reason:'Duplicate fails native refinement schema validation'};
}
function atelierRefineCount(g){
 return Math.floor((g.index?.count||g.attributes.position.count)/3);
}
function atelierRefineEstimate(g,part,layers=part.refinementLayers||[]){
 let triangles=atelierRefineCount(g);
 // Conservative bound; target area usually much smaller. Never blindly
 // execute a full-scene 4x subdivision if an object is near mobile limits.
 for(const l of layers)if(l.enabled)triangles*=4**l.level;
 return {original:atelierRefineCount(g),upperBound:Math.floor(triangles),
   withinCap:triangles<=atelierRefineMaxTriangles};
}
function atelierRefineOne(g,region,part){
 if(g.morphAttributes?.position?.length||g.groups.length>1)return null;
 const a=g.attributes.position,idx=g.index,triangles=atelierRefineCount(g);
 if(!triangles||triangles>atelierRefineMaxTriangles)return null;
 const uv=g.attributes.uv,normal=g.attributes.normal,color=g.attributes.color;
 const fields={position:3};
 if(uv)fields.uv=uv.itemSize;
 if(normal)fields.normal=normal.itemSize;
 if(color)fields.color=color.itemSize;
 const point=(vertex,attribute,n)=>Array.from({length:n},(_,k)=>attribute.getComponent(vertex,k));
 const triIDs=new Uint32Array(triangles*3);
 for(let i=0;i<triIDs.length;i++)triIDs[i]=idx?idx.getX(i):i;
 const positions=Array.from({length:a.count},(_,i)=>point(i,a,3));
 const mask=atelierLassoCompiledRegionMask(part,region),axis=new THREE.Vector3(...region.axis);
 // Weld opposite UV seams by rounded POSITION when deciding shared edges.
 // Attribute midpoints remain per-face to preserve distinct UVs/material.
 const keys=positions.map(p=>p.map(v=>Math.round(v*1e5)).join(','));
 const edge=(i,j)=>keys[i]<keys[j]?keys[i]+'|'+keys[j]:keys[j]+'|'+keys[i];
 const faceSelected=new Uint8Array(triangles),splitEdges=new Set();
 let selected=0;
 for(let t=0;t<triangles;t++){
   const [a,b,c]=triIDs.slice(t*3,t*3+3);
   const center=[0,1,2].map(k=>(positions[a][k]+positions[b][k]+positions[c][k])/3);
   const N=g.attributes.normal;
   if(N){
     const norm=new THREE.Vector3(
       (N.getX(a)+N.getX(b)+N.getX(c))/3,
       (N.getY(a)+N.getY(b)+N.getY(c))/3,
       (N.getZ(a)+N.getZ(b)+N.getZ(c))/3);
     if(norm.dot(axis)<-.12)continue;
   }
   if(!mask.contains(center))continue;
   faceSelected[t]=1;selected++;
   splitEdges.add(edge(a,b));splitEdges.add(edge(b,c));splitEdges.add(edge(c,a));
 }
 if(!selected)return null;
 const out=Object.fromEntries(Object.keys(fields).map(k=>[k,[]]));
 const getAttribute=(k)=>g.attributes[k];
 const origin=i=>Object.fromEntries(Object.keys(fields).map(k=>[k,point(i,getAttribute(k),fields[k])]));
 const midpoint=(i,j)=>Object.fromEntries(Object.keys(fields).map(k=>{
   const attr=getAttribute(k),n=fields[k];
   return [k,Array.from({length:n},(_,a)=>(attr.getComponent(i,a)+attr.getComponent(j,a))*.5)];
 }));
 const emit=(a,b,c)=>{for(const v of [a,b,c])for(const k of Object.keys(fields))out[k].push(...v[k]);};
 // Conforming fan triangulation: selected faces split all three edges and
 // produce four triangles; their neighbors split only the shared edges.
 // Every edge midpoint matches on both sides, so no T-junctions/cracks.
 for(let t=0;t<triangles;t++){
   const a=triIDs[t*3],b=triIDs[t*3+1],c=triIDs[t*3+2];
   const A=origin(a),B=origin(b),C=origin(c);
   const ab=splitEdges.has(edge(a,b)),bc=splitEdges.has(edge(b,c)),ca=splitEdges.has(edge(c,a));
   if(!ab&&!bc&&!ca){emit(A,B,C);continue;}
   const AB=ab?midpoint(a,b):null,BC=bc?midpoint(b,c):null,CA=ca?midpoint(c,a):null;
   if(ab&&bc&&ca){
     emit(A,AB,CA);emit(AB,B,BC);emit(CA,BC,C);emit(AB,BC,CA);
   }else{
     const polygon=[A,...(ab?[AB]:[]),B,...(bc?[BC]:[]),C,...(ca?[CA]:[])];
     for(let i=1;i<polygon.length-1;i++)emit(polygon[0],polygon[i],polygon[i+1]);
   }
   if(out.position.length/9>atelierRefineMaxTriangles)return null;
 }
 if(out.position.length/9>atelierRefineMaxTriangles)return null;
 const result=new THREE.BufferGeometry();
 for(const [name,values]of Object.entries(out))result.setAttribute(name,new THREE.Float32BufferAttribute(values,fields[name]));
 result.userData.refinedTriangles=out.position.length/9;
 result.userData.selectedOriginalTriangles=selected;
 // Existing normals are interpolated, retaining smooth shading across new
 // edges instead of generating faceted normals on nonindexed geometry.
 return result;
}
function atelierRefineApply(g,part){
 const layers=part.refinementLayers||[];
 if(!layers.some(l=>l.enabled))return g;
 let current=g;
 for(const layer of layers){
   if(!layer.enabled)continue;
   const r=part.sculptLassos?.find(r=>r.id===layer.regionId);
   if(!r||!atelierLassoPolygonValid(r))continue;
   for(let i=0;i<layer.level;i++){
     const next=atelierRefineOne(current,r,part);
     if(!next)break;
     if(current!==g)current.dispose();
     current=next;
   }
 }
 if(current!==g)g.dispose();
 return current;
}
// A read-only preview uses the EXACT local triangulation routine used by
// Apply. Count generated BufferGeometry vertex slots separately from welded
// source points; never present them as unique mesh vertices.
function atelierRefineCandidate(mesh,region,level,part){
 if(!mesh?.geometry||!region||!atelierLassoPolygonValid(region)||
    (region.selectionOp&&!part)||
    !Number.isInteger(level)||level<1||level>2)return {ok:false,reason:'Invalid mesh, boundary or density level'};
 const base=mesh.geometry,before=atelierRefineCount(base);
 if(before>atelierRefineMaxTriangles)return {ok:false,reason:'Base exceeds local mobile triangle cap'};
 let current=base.clone(),grown=false,affected=0;
 try{
   for(let i=0;i<level;i++){
     const next=atelierRefineOne(current,region,part);
     if(!next)break;
     current.dispose();current=next;grown=true;
     affected+=next.userData.selectedOriginalTriangles||0;
   }
   const after=atelierRefineCount(current);
   return {ok:grown&&after>before&&after<=atelierRefineMaxTriangles,
     before,after,delta:after-before,vertices:current.attributes.position.count,
     affected,cap:atelierRefineMaxTriangles};
 }finally{current.dispose();}
}
function atelierRefineRefresh(){
 const p=partById(selection),panel=$m('RefineTools');
 if(!panel)return;
 panel.hidden=!p;
 const r=atelierLassoRegion();
 const source=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===p?.id);
 const all=p?.refinementLayers||[];
 const options=$m('RefineLayer');options.replaceChildren();
 for(let i=0;i<all.length;i++){
   const el=document.createElement('option');
   el.value=String(i);el.textContent=(i+1)+': '+(all[i].enabled?'● ':'○ ')+
     (atelierRefineLayerLocked(all[i])?'🔒 ':'')+all[i].regionId+' ×'+(4**all[i].level);
   options.append(el);
 }
 const original=source?atelierRefineCount(source.geometry):0;
 $m('RefineStats').textContent='Current visible mesh: '+original.toLocaleString()+' triangles · '+
   all.length+' saved refinement layers · '+all.filter(atelierRefineLayerLocked).length+
   ' structurally locked · Region: '+(r?.name||'none')+
   '. The editor caps topology at '+atelierRefineMaxTriangles.toLocaleString()+' triangles per mesh.';
 const budget=$m('RefineBudget');
 if(budget)budget.textContent='Preview next local density before applying; no geometry is changed by preview.';
}
function atelierRefineInstall(){
 const id=s=>$m('Refine'+s);
 id('Preview').addEventListener('click',()=>{
   const p=partById(selection),r=atelierLassoRegion(),level=Number(id('Level').value);
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===p?.id);
   const result=atelierRefineCandidate(mesh,r,level,p),output=id('Budget');
   if(!result.ok){
     output.textContent='Cannot preview or safely refine: '+(result.reason||
       'no affected triangles or per-object cap exceeded')+'. Original untouched.';
     return;
   }
   output.textContent='Measured local preview · '+result.before.toLocaleString()+' → '+
     result.after.toLocaleString()+' triangles (+'+result.delta.toLocaleString()+
     '); '+result.vertices.toLocaleString()+' evaluated vertex slots; '+
     result.cap.toLocaleString()+' triangle cap. No model change.';
 });
 id('Add').addEventListener('click',()=>{
   const p=partById(selection),r=atelierLassoRegion();
   if(!p||!r){status('Create/select a surface lasso region before refining.',true);return;}
   if((p.refinementLayers?.length||0)>=atelierRefineMaxLayers){status('Maximum three refinement layers per object.',true);return;}
   const level=Number(id('Level').value);
   const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
   if(!mesh||!Number.isInteger(level)||level<1||level>2)return;
   // Use the same measured local geometry result for Preview and Apply;
   // a pessimistic whole-head 4x estimate would reject valid tiny regions.
   const projected=atelierRefineCandidate(mesh,r,level,p);
   if(!projected.ok){
     status('No local triangles could be safely refined inside this region. Reduce level, region size or base density.',true);return;
   }
   const layer={id:'detail-'+Date.now().toString(36),regionId:r.id,level,enabled:true,locked:false};
   const next={...p,refinementLayers:[...(p.refinementLayers||[]),layer]};
   if(!checkPart(next)){status('Refinement rejected by native validation.',true);return;}
   checkpoint();p.refinementLayers=next.refinementLayers;
   signalEdited();select(p.id);
   status('Added reversible local refinement: '+projected.before.toLocaleString()+' → '+
     projected.after.toLocaleString()+' evaluated triangles. Source mesh preserved; Undo/JSON/OBJ supported.');
 });
 id('Remove').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value);
   if(!p?.refinementLayers?.[i])return;
   if(atelierRefineLayerLocked(p.refinementLayers[i])){
     status('Unlock this detail layer before removing it.',true);return;
   }
   checkpoint();p.refinementLayers.splice(i,1);signalEdited();select(p.id);
 });
 id('Toggle').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value);
   if(!p?.refinementLayers?.[i])return;
   checkpoint();p.refinementLayers[i].enabled=!p.refinementLayers[i].enabled;
   signalEdited();select(p.id);id('Layer').value=String(i);
 });
 id('Up').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value);
   if(!p?.refinementLayers?.[i]||i===0)return;
   if(!atelierRefineCanMove(p.refinementLayers,i,i-1)){
     status('Unlock both detail layers before changing their order.',true);return;
   }
   checkpoint();[p.refinementLayers[i-1],p.refinementLayers[i]]=[p.refinementLayers[i],p.refinementLayers[i-1]];
   signalEdited();select(p.id);id('Layer').value=String(i-1);
 });
 id('Down').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value);
   if(!p?.refinementLayers?.[i]||i>=p.refinementLayers.length-1)return;
   if(!atelierRefineCanMove(p.refinementLayers,i,i+1)){
     status('Unlock both detail layers before changing their order.',true);return;
   }
   checkpoint();[p.refinementLayers[i],p.refinementLayers[i+1]]=[p.refinementLayers[i+1],p.refinementLayers[i]];
   signalEdited();select(p.id);id('Layer').value=String(i+1);
 });
 id('Lock').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value),layer=p?.refinementLayers?.[i];
   if(!layer)return;
   checkpoint();layer.locked=!atelierRefineLayerLocked(layer);
   const wasLocked=layer.locked;
   signalEdited();select(p.id);id('Layer').value=String(i);
   status(wasLocked?'Detail layer structurally locked; visibility remains independent.':
     'Detail layer unlocked for reordering and removal.');
 });
 id('Duplicate').addEventListener('click',()=>{
   const p=partById(selection),i=Number(id('Layer').value);
   const newId='detail-copy-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7);
   const candidate=atelierRefineDuplicateCandidate(p,i,newId);
   if(!candidate.ok){status('Cannot duplicate layer: '+candidate.reason,true);return;}
   if(!checkPart({...p,refinementLayers:candidate.layers})){
     status('Duplicate rejected by native part validation.',true);return;
   }
   checkpoint();p.refinementLayers=candidate.layers;
   signalEdited();select(p.id);id('Layer').value=String(candidate.index);
   status('Created a disabled, unlocked detail duplicate. Enable only after checking the triangle budget.');
 });
}
