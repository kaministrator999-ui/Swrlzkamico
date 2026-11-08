/* SE345_MODEL_VR_DISPLAY_MODES_START */
// Display modes operate on borrowed runtime materials only, never the source
// model schema. Restore exact references on mode change, rebuild and VR exit.
const SE345_DISPLAY_OPTIONS=['textured','solid','wireframe','xray','normals'];
function se345DisplayMaterial(mode){
 const s=se340XR;
 if(!s.displayMaterials)s.displayMaterials=new Map();
 if(s.displayMaterials.has(mode))return s.displayMaterials.get(mode);
 let mat=null;
 if(mode==='solid')mat=new THREE.MeshStandardMaterial({color:0xb6bbc6,roughness:.78,metalness:.06,side:THREE.DoubleSide});
 if(mode==='wireframe')mat=new THREE.MeshBasicMaterial({color:0x83f6e8,wireframe:true,side:THREE.DoubleSide,depthWrite:false});
 if(mode==='xray')mat=new THREE.MeshBasicMaterial({color:0x9dcaff,transparent:true,opacity:.24,depthWrite:false,side:THREE.DoubleSide});
 if(mode==='normals')mat=new THREE.MeshNormalMaterial({side:THREE.DoubleSide});
 if(!mat)return null;
 se340Own(mat);s.displayMaterials.set(mode,mat);return mat;
}
function se345SyncDisplay(){
 const s=se340XR;if(!s.scene)return;
 if(!s.displayOriginals)s.displayOriginals=new Map();
 const keep=new Set(),entries=s.cachedEntries||s.frameEntries||[];
 for(const entry of entries){
  const mesh=entry?.mesh;
  if(!mesh?.isMesh)continue;
  keep.add(mesh);
  if(!s.displayOriginals.has(mesh))s.displayOriginals.set(mesh,mesh.material);
  const original=s.displayOriginals.get(mesh);
  const target=s.displayMode==='textured'?original:se345DisplayMaterial(s.displayMode);
  if(target&&mesh.material!==target)mesh.material=target;
 }
 for(const [mesh,original] of [...s.displayOriginals]){
  if(!keep.has(mesh)){mesh.material=original;s.displayOriginals.delete(mesh);}
 }
}
function se345SetDisplay(mode){
 if(!SE345_DISPLAY_OPTIONS.includes(mode))return false;
 const s=se340XR;
 s.displayMode=mode;se345SyncDisplay();
 se340Notice('Model display: '+mode+'. Original materials are retained and restored when VR closes.');
 return true;
}
function se345RestoreDisplay(){
 const s=se340XR;
 for(const [mesh,material] of s.displayOriginals||[])mesh.material=material;
 s.displayOriginals?.clear();s.displayMaterials?.clear();s.displayMode='textured';
}
/* SE345_MODEL_VR_DISPLAY_MODES_END */