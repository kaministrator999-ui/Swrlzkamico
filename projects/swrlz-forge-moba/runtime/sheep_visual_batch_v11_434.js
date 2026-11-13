/* SE434_SHEEP_VISUAL_BATCH_START */
// Combine only unnamed opaque siblings of the same native material/state.
// Vertex attributes, triangles, lighting and the actor/pivot hierarchy survive.
const se434VisualBatch={visuals:0,groups:0,sourceMeshes:0,drawMeshes:0,triangles:0,skipped:0,errors:0};
function se434CompactVisual(root){
 if(!root?.isObject3D)return root;
 const parents=[];root.traverse(o=>{if(o.children?.length)parents.push(o);});
 const made=[],retired=new Set();
 const attributesKey=g=>Object.keys(g.attributes).sort().map(k=>{
  const a=g.attributes[k];return k+':'+a.itemSize+':'+a.normalized+':'+a.array?.constructor?.name;
 }).join('|');
 function eligible(o){
  const g=o.geometry,m=o.material;
  return o.isMesh&&!o.isSkinnedMesh&&!o.isInstancedMesh&&!o.name&&o.visible&&
   Object.keys(o.userData||{}).length===0&&g?.isBufferGeometry&&m&&!Array.isArray(m)&&
   !m.transparent&&m.opacity===1&&m.onBeforeCompile===THREE.Material.prototype.onBeforeCompile&&
   !Object.keys(g.morphAttributes||{}).length&&!g.attributes.skinIndex&&!g.attributes.skinWeight&&
   Object.values(g.attributes).every(a=>!a.isInterleavedBufferAttribute&&a.array)&&
   g.attributes.position?.itemSize===3&&g.drawRange.start===0&&
   (!Number.isFinite(g.drawRange.count)||g.drawRange.count===(g.index?.count||g.attributes.position.count));
 }
 for(const parent of parents){
  const groups=new Map();
  for(const mesh of [...parent.children]){
   if(!eligible(mesh))continue;
   if(mesh.matrixAutoUpdate)mesh.updateMatrix();
   if(mesh.matrix.determinant()<=0)continue;
   const key=[mesh.material.uuid,mesh.castShadow,mesh.receiveShadow,mesh.renderOrder,mesh.layers.mask,mesh.frustumCulled,attributesKey(mesh.geometry)].join(';');
   if(!groups.has(key))groups.set(key,[]);groups.get(key).push(mesh);
  }
  for(const members of groups.values()){
   if(members.length<2)continue;
   const clones=[];let geometry=null;
   try{
    let vertices=0,indexCount=0;
    for(const mesh of members){
     const g=mesh.geometry.clone().applyMatrix4(mesh.matrix);clones.push(g);
     vertices+=g.attributes.position.count;indexCount+=g.index?.count||g.attributes.position.count;
    }
    if(vertices===0||vertices>250000||indexCount%3){se434VisualBatch.skipped++;continue;}
    geometry=new THREE.BufferGeometry();
    for(const name of Object.keys(clones[0].attributes)){
     const first=clones[0].attributes[name],array=new first.array.constructor(vertices*first.itemSize);let offset=0;
     for(const g of clones){array.set(g.attributes[name].array,offset);offset+=g.attributes[name].array.length;}
     geometry.setAttribute(name,new THREE.BufferAttribute(array,first.itemSize,first.normalized));
    }
    const indices=vertices>65535?new Uint32Array(indexCount):new Uint16Array(indexCount);let vi=0,ii=0;
    for(const g of clones){
     const n=g.index?.count||g.attributes.position.count;
     for(let i=0;i<n;i++)indices[ii++]=vi+(g.index?g.index.getX(i):i);
     vi+=g.attributes.position.count;
    }
    geometry.setIndex(new THREE.BufferAttribute(indices,1));geometry.computeBoundingBox();geometry.computeBoundingSphere();
    const first=members[0],combined=new THREE.Mesh(geometry,first.material);
    combined.name='Native static visual batch';combined.userData.se434StaticVisual=true;
    combined.castShadow=first.castShadow;combined.receiveShadow=first.receiveShadow;
    combined.renderOrder=first.renderOrder;combined.layers.mask=first.layers.mask;combined.frustumCulled=first.frustumCulled;
    // Commit only after a complete candidate exists. Named animation pivots,
    // source actors, material identity and parent transforms remain native.
    for(const mesh of members){retired.add(mesh.geometry);parent.remove(mesh);}
    parent.add(combined);made.push(geometry);
    se434VisualBatch.groups++;se434VisualBatch.sourceMeshes+=members.length;
    se434VisualBatch.drawMeshes++;se434VisualBatch.triangles+=indexCount/3;
   }catch(error){geometry?.dispose();se434VisualBatch.errors++;}
   finally{clones.forEach(g=>g.dispose());}
  }
 }
 if(made.length){
  // Old inputs can have shared attributes. Retire them with the derived root's
  // native geometry lifecycle, never while another child still renders them.
  const retained=new Set();root.traverse(o=>{if(o.geometry)retained.add(o.geometry);});
  for(const g of retained)retired.delete(g);
  let remaining=made.length;
  for(const g of made){let disposed=false;g.addEventListener('dispose',()=>{
   if(disposed)return;disposed=true;
   if(--remaining===0){for(const old of retired)old.dispose();retired.clear();}
  });}
  se434VisualBatch.visuals++;
 }
 return root;
}
const se434PriorMakeVisual=stMakeVisual;
stMakeVisual=function(type){
 const root=se434PriorMakeVisual.apply(this,arguments);
 // Runtime buildings already have the native v11.265 batch owner. Extend
 // the same rendering benefit to editor buildings and static scenery only.
 if(['st-tree','st-rock','st-farm','st-income','st-fort','st-shop','st-pond','st-wall','st-ramp','st-totem'].includes(type)&&
    !(typeof stSession!=='undefined'&&stSession&&typeof ST_BUILDINGS!=='undefined'&&ST_BUILDINGS[type]))se434CompactVisual(root);
 return root;
};
window.SWYRL_ENGINE_SHEEP_VISUAL_BATCH_434=Object.freeze({
 diagnose:()=>({...se434VisualBatch,drawCallsAvoidedPerVisibleSet:se434VisualBatch.sourceMeshes-se434VisualBatch.drawMeshes,
  nativeGeometryAndMaterialsRetained:true,namedPivotsRetained:true,visualDetailReduced:false})
});
/* SE434_SHEEP_VISUAL_BATCH_END */
