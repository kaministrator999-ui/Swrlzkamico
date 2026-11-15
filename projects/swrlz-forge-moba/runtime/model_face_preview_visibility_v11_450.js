/* SE450_FACE_PREVIEW_VISIBILITY_START */
// One transient edge overlay belongs exclusively to a native preview record.
// The underlying mesh geometry, history and face selection remain owned by
// se430ModelWorkshop. No preview markup becomes project/source data.
function se450PreviewOutlineClear(record){
 const lines=record?.se450Outline;
 if(!lines)return;
 lines.parent?.remove(lines);
 lines.geometry?.dispose?.();lines.material?.dispose?.();
 record.se450Outline=null;
}
function se450PreviewOutlineAdd(record){
 se450PreviewOutlineClear(record);
 const geo=record?.geometry,mesh=record?.mesh;
 const count=(geo?.getIndex?.()?.count||geo?.getAttribute?.('position')?.count||0)/3;
 if(!mesh||!geo||count<=0||count>8000||typeof THREE.EdgesGeometry!=='function')return;
 let edges=null,material=null;
 try{
  edges=new THREE.EdgesGeometry(geo,10);
  material=new THREE.LineBasicMaterial({color:0x74ffcf,depthTest:false,depthWrite:false,transparent:true,opacity:.97});
  const lines=new THREE.LineSegments(edges,material);
  lines.name='Inset / Extrude preview edges';
  lines.renderOrder=180;
  lines.userData.atelierHelper=true;lines.userData.se450Transient=true;
  mesh.add(lines);record.se450Outline=lines;
 }catch(_){edges?.dispose?.();material?.dispose?.();}
}
/* SE450_FACE_PREVIEW_VISIBILITY_END */
