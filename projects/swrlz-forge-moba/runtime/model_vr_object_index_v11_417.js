/* SE417_MODEL_VR_OBJECT_INDEX_START */
// The VR index reads native part records; no parallel selection state or saved-data mutations.
const SE417_INDEX_PAGE_SIZE=9;
function se417IndexPageCount(total){return Math.max(1,Math.ceil(Math.max(0,total)/SE417_INDEX_PAGE_SIZE));}
function se417IndexAction(action,record=null){
 const s=se340XR;
 if(!s.session||!s.scene||!se340VisibleSession())return false;
 if(action==='objects'){
  if(s.gesture)se340CancelGesture('Preview canceled before opening Object Index.');
  s.page='objects';s.helpVisible=false;
  s.se417IndexPage=Math.min(s.se417IndexPage||0,se417IndexPageCount(se340PartEntries().length)-1);
  se340Notice('Object Index · trigger selects one part · Multi toggles additional parts.');
 }else if(action==='index-add'){
  s.se417IndexMulti=!s.se417IndexMulti;
  se340Notice(s.se417IndexMulti?'Multi on · tap part names to add or remove (maximum 32).':'Single on · tap a name to select only that part.');
 }else if(action==='index-prev'||action==='index-next'){
  const pages=se417IndexPageCount(se340PartEntries().length);
  s.se417IndexPage=THREE.MathUtils.clamp((s.se417IndexPage||0)+(action==='index-next'?1:-1),0,pages-1);
  se340Notice('Objects · page '+(s.se417IndexPage+1)+' of '+pages);
 }else if(action.startsWith('index-part-')){
  if(s.page!=='objects')return false;
  const offset=Number(action.slice('index-part-'.length)),entries=se340PartEntries();
  const begin=(s.se417IndexPage||0)*SE417_INDEX_PAGE_SIZE;
  if(!Number.isSafeInteger(offset)||offset<begin||offset>=begin+SE417_INDEX_PAGE_SIZE||offset>=entries.length)return false;
  const item=entries[offset];
  if(!item||!item.id)return false;
  if(s.gesture){se340Notice('Finish or cancel the active tool before changing selection.',true);return false;}
  const result=se350Tools().select(item.id,{additive:!!s.se417IndexMulti});
  if(result?.ok===false){se350Result(result,'Select '+item.name,record);return false;}
  se350Invalidate();
  const count=se350Tools().selection().ids.length;
  s.lastAction=(s.se417IndexMulti?'Toggled ':'Selected ')+item.name;
  se340Notice(s.lastAction+' · '+count+' selected');
  if(record)se340Pulse(record,.25,25);
 }else return false;
 se340SyncUI();se340Publish();return true;
}
function se417IndexState(s,entries,ids){
 if(s.page!=='objects')return {indexEntries:[],indexSelected:[],indexTotal:0,indexPage:0,indexMulti:!!s.se417IndexMulti};
 const pages=se417IndexPageCount(entries.length);
 s.se417IndexPage=THREE.MathUtils.clamp(s.se417IndexPage||0,0,pages-1);
 const start=s.se417IndexPage*SE417_INDEX_PAGE_SIZE;
 return {indexEntries:entries.slice(start,start+SE417_INDEX_PAGE_SIZE).map(e=>({id:e.id,name:e.name})),
  indexSelected:[...ids],indexTotal:entries.length,indexPage:s.se417IndexPage,indexMulti:!!s.se417IndexMulti};
}
// Backface-expanded geometry shells outline each selected mesh individually.
function se417UpdateHighlights(s,entries,ids){
 if(!s.scene)return;
 if(!s.se416Shells)s.se416Shells=new Map();
 const shells=s.se416Shells;
 if(!ids.size){for(const item of shells.values())item.shell.removeFromParent();shells.clear();return;}
 if(!s.se416ShellMaterial){
  s.se416ShellMaterial=new THREE.MeshBasicMaterial({color:0x8fffe1,side:THREE.BackSide,
   transparent:true,opacity:.94,depthTest:true,depthWrite:false,toneMapped:false});
 }
 const keep=new Set();
 for(const item of entries){
  const mesh=item.mesh;
  if(!ids.has(item.id)||!mesh?.isMesh||!mesh.geometry||!mesh.parent||mesh.visible===false)continue;
  keep.add(item.id);
  let current=shells.get(item.id);
  if(current&&(current.mesh!==mesh||current.shell.parent!==mesh.parent||current.shell.geometry!==mesh.geometry)){
   current.shell.removeFromParent();shells.delete(item.id);current=null;
  }
  if(!current){
   const shell=mesh.isSkinnedMesh?new THREE.SkinnedMesh(mesh.geometry,s.se416ShellMaterial):
    new THREE.Mesh(mesh.geometry,s.se416ShellMaterial);
   if(mesh.isSkinnedMesh&&mesh.skeleton){
    shell.bindMode=mesh.bindMode;shell.bind(mesh.skeleton,mesh.bindMatrix);
    shell.bindMatrixInverse.copy(mesh.bindMatrixInverse);
   }
   shell.name='Model VR · selected silhouette · '+String(item.name||'part');
   shell.userData.editorOnly=true;shell.userData.atelierHelper=true;shell.userData.se416SelectedSilhouette=true;
   shell.renderOrder=Number(mesh.renderOrder||0)+1;shell.frustumCulled=mesh.frustumCulled;
   mesh.parent.add(shell);
   current={mesh,shell};shells.set(item.id,current);
  }
  const shell=current.shell,scale=mesh.scale;
  shell.position.copy(mesh.position);shell.quaternion.copy(mesh.quaternion);
  const sphere=mesh.geometry.boundingSphere;
  const localRadius=(sphere?.radius||.1)*Math.max(Math.abs(scale.x),Math.abs(scale.y),Math.abs(scale.z),.0001);
  const amount=THREE.MathUtils.clamp(.0035/Math.max(.001,localRadius),.015,.065);
  shell.scale.copy(scale).multiplyScalar(1+amount);
  if(sphere?.center){
   const center=sphere.center.clone().multiply(scale).applyQuaternion(mesh.quaternion);
   shell.position.addScaledVector(center,-amount);
  }
  if(mesh.isSkinnedMesh){
   if(shell.skeleton!==mesh.skeleton&&mesh.skeleton)shell.bind(mesh.skeleton,mesh.bindMatrix);
   shell.bindMatrixInverse.copy(mesh.bindMatrixInverse);
  }
  if(mesh.morphTargetInfluences)shell.morphTargetInfluences=mesh.morphTargetInfluences;
  shell.visible=true;
 }
 for(const [id,item] of shells)if(!keep.has(id)){item.shell.removeFromParent();shells.delete(id);}
}
function se417DisposeHighlights(s){
 if(s.se416Shells){for(const item of s.se416Shells.values())item.shell.removeFromParent();s.se416Shells.clear();}
 s.se416Shells=null;s.se416ShellMaterial?.dispose?.();s.se416ShellMaterial=null;
 s.se417IndexPage=0;s.se417IndexMulti=false;
}
/* SE417_MODEL_VR_OBJECT_INDEX_END */
