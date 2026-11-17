/* §E v11.498 — mode isolation, schema-correct controls and articulated bone handles.
   Works inside the EXISTING ModelAtelier closure; never mutates source topology/UVs. */
const se498RigPolish=(()=>{
 'use strict';
 const $=selector=>panel?.querySelector(selector);
 const masked=new Map();
 const legacyUI=[
  '#se320ModelTransform','#modelAtelierViewportModes','#se474SpecificModes',
  '#se474ToolFlyout','#seAtelierModes','#se452FaceOperations','#se452FaceModifiers',
  '#modelAtelierMeshQuickStrip','#modelAtelierToolRail','#se251ModelLibrary',
  '#se251-split-model-left','#se251-split-model-right',
  '.atelier-inspector','.atelier-viewbar','#se430SelectionContext',
  '.se320-selection-tools'
 ];
 let visual=null, observer=null, observedPanel=null, pending=false, hovered=null;
 const canvases=new WeakSet();
 const worldPoint=new THREE.Vector3(),parentPoint=new THREE.Vector3();
 const inverse=new THREE.Matrix4(), axis=new THREE.Vector3(0,1,0);
 function mode(){return panel?.dataset.se496Studio||'model';}
 function rig(){return se220RigAvailable()?se220Rig():null;}
 function live(){return panel&&!panel.hidden&&['rig','animate'].includes(mode());}
 function maskUI(){
  const hide=!!live();
  if(!hide){
   for(const [el,previous] of masked){
    if(!el.isConnected)continue;
    if(previous.value)el.style.setProperty('display',previous.value,previous.priority);
    else el.style.removeProperty('display');
   }
   masked.clear();return;
  }
  for(const selector of legacyUI){
   for(const el of panel.querySelectorAll(selector)){
    if(el.closest('#modelAtelierRigStudio')||el.closest('#se496ModeTabs'))continue;
    if(!masked.has(el))masked.set(el,{
     value:el.style.getPropertyValue('display'),
     priority:el.style.getPropertyPriority('display')});
    el.style.setProperty('display','none','important');
   }
  }
 }
 function schemaUI(){
  const native=se220R('Studio');if(!native)return;
  const r=rig(),hand=r?.schema==='swyrl-hand-skin-v1';
  native.dataset.se498RigKind=hand?'hand':r?'object':'none';
  for(const node of native.querySelectorAll('.atelier-gesture-library,.atelier-thumb-kinematics')){
   node.hidden=!hand;
  }
  const axes=native.querySelector('.atelier-rig-axes');
  if(axes){
   const labels=axes.querySelectorAll('label');
   if(!hand&&labels.length===3){
    ['Rotation X','Rotation Y','Rotation Z'].forEach((title,i)=>{
     const span=labels[i].querySelector('span');
     let first=labels[i].firstChild;
     if(first?.nodeType===Node.TEXT_NODE)first.textContent=title+' ';
    });
   }else if(hand&&labels.length===3){
    ['Curl / X','Twist / Y','Spread / Z'].forEach((title,i)=>{
     const first=labels[i].firstChild;
     if(first?.nodeType===Node.TEXT_NODE)first.textContent=title+' ';
    });
   }
  }
  const checkbox=se220R('ShowBones');
  if(checkbox){
   const label=checkbox.closest('label');
   const text=label&&[...label.childNodes].find(n=>n.nodeType===Node.TEXT_NODE);
   if(text)text.textContent=' Show joints in Animation';
  }
  const summary=native.querySelector(':scope > summary');
  if(summary){
   const title=mode()==='rig'?'Rigging · Skeleton':mode()==='animate'?'Animation · Clips':'Rig · Pose · Animate';
   if(summary.textContent!==title)summary.textContent=title;
  }
  const author=$('#se496BoneAuthoring');
  if(author){
   const hint=author.querySelector('small:last-child');
   if(hint&&hint.textContent!=='Select a joint on the model or in the list. Rest transforms and automatic influences affect this rig only.')
    hint.textContent='Select a joint on the model or in the list. Rest transforms and automatic influences affect this rig only.';
  }
  const small=native.querySelector('.atelier-rig-body > small:last-child');
  if(small&&r){
   const label=r.bones.length+' hierarchical joints · four-influence GPU skinning · source mesh and UVs unchanged.';
   if(small.textContent!==label)small.textContent=label;
  }
 }
 function helpers(){
  if(!modelRoot)return;
  const isolate=!!live();
  // Restore visibility, don't destroy the native box/gizmos or change their settings.
  const sceneHelpers=[...modelRoot.children,...(world?.children||[])];
  if(typeof atelierMeshGizmo!=='undefined'&&atelierMeshGizmo)sceneHelpers.push(atelierMeshGizmo);
  for(const object of new Set(sceneHelpers)){
   if(object===modelRoot||object===world)continue;
   if(object===visual?.group||object===se220BoneOverlay)continue;
   if(!object.userData?.atelierHelper&&object!==atelierMeshGizmo)continue;
   if(isolate&&!object.userData.se498Hidden){
    object.userData.se498Hidden={visible:object.visible};
    object.visible=false;
   }else if(!isolate&&object.userData.se498Hidden){
    object.visible=object.userData.se498Hidden.visible;
    delete object.userData.se498Hidden;
   }
  }
  if(se220BoneOverlay)se220BoneOverlay.visible=false; // replace SkeletonHelper lines
 }
 function disposeVisual(){
  if(!visual)return;
  if(visual.group?.parent)visual.group.parent.remove(visual.group);
  visual.group.traverse(object=>{
   if(object.isMesh){object.geometry?.dispose();object.material?.dispose();}
  });
  visual=null;hovered=null;
 }
 function buildVisual(){
  disposeVisual();
  const r=rig();
  if(!r||!modelRoot||!se220Bones)return;
  const group=new THREE.Group();
  group.name='§E Rig Controls';
  group.userData.atelierHelper=true;
  const count=r.bones.length;const items=[];
  for(let i=0;i<count;i++){
   const spec=r.bones[i],bone=se220Bones[spec.id];
   if(!bone)continue;
   const joint=new THREE.Mesh(
    new THREE.SphereGeometry(1,12,9),
    new THREE.MeshBasicMaterial({color:0x73dbe9,transparent:true,opacity:.95,depthTest:false,depthWrite:false})
   );
   joint.name='Joint · '+spec.label;
   joint.userData.se498BoneId=spec.id;
   joint.renderOrder=450;joint.frustumCulled=false;
   group.add(joint);
   let shaft=null;
   if(spec.parent&&se220Bones[spec.parent]){
    shaft=new THREE.Mesh(
     new THREE.CylinderGeometry(.50,.86,1,9,1),
     new THREE.MeshBasicMaterial({color:0x509cbd,transparent:true,opacity:.8,depthTest:false,depthWrite:false})
    );
    shaft.name='Bone · '+spec.label;
    shaft.userData.se498BoneId=spec.id;
    shaft.renderOrder=449;shaft.frustumCulled=false;group.add(shaft);
   }
   items.push({spec,bone,joint,shaft,parent:spec.parent?se220Bones[spec.parent]:null});
  }
  modelRoot.add(group);
  visual={group,items,r};
  updateVisual();
 }
 function updateVisual(){
  if(!visual||!modelRoot)return;
  const show=!!live()&&(mode()==='rig'||!!se220R('ShowBones')?.checked);
  visual.group.visible=show;
  if(!show)return;
  modelRoot.updateMatrixWorld(true);
  inverse.copy(modelRoot.matrixWorld).invert();
  const r=rig();if(!r||r!==visual.r){visual.group.visible=false;return;}
  for(const item of visual.items){
   const point=item.bone.getWorldPosition(worldPoint).applyMatrix4(inverse);
   const chosen=se220Joint===item.spec.id,over=hovered===item.spec.id,root=!item.spec.parent;
   const size=chosen?.092:over?.080:root?.07:.055;
   item.joint.position.copy(point);item.joint.scale.setScalar(size);
   item.joint.material.color.setHex(chosen?0xff6ec7:over?0x9dffd9:root?0xffd878:0x7ecde7);
   if(item.shaft&&item.parent){
    const from=item.parent.getWorldPosition(parentPoint).applyMatrix4(inverse);
    const dir=point.clone().sub(from),len=dir.length();
    item.shaft.position.copy(from).addScaledVector(dir,.5);
    item.shaft.quaternion.setFromUnitVectors(axis,len>1e-5?dir.clone().divideScalar(len):axis);
    item.shaft.scale.set(chosen?.070:.052,Math.max(len,.00001),chosen?.070:.052);
    item.shaft.visible=len>1e-5;
    item.shaft.material.color.setHex(chosen?0xee65b8:over?0x7ae7c9:0x528ab6);
   }
  }
 }
 function picker(event){
  if(!visual||!visual.group.visible||!renderer||!camera||event.button!==0)return;
  const rect=renderer.domElement.getBoundingClientRect();
  if(rect.width<=0||rect.height<=0)return;
  const xy=new THREE.Vector2(2*(event.clientX-rect.left)/rect.width-1,1-2*(event.clientY-rect.top)/rect.height);
  const caster=new THREE.Raycaster();caster.setFromCamera(xy,camera);
  const meshes=visual.group.children.filter(x=>x.isMesh&&x.visible);
  const hit=caster.intersectObjects(meshes,false)[0]?.object;
  if(!hit?.userData.se498BoneId)return;
  se220Joint=hit.userData.se498BoneId;
  const joint=se220R('Joint');if(joint)joint.value=se220Joint;
  se220RigJointUI();
  se496MiniStudios.refresh();
  updateVisual();
  event.preventDefault();event.stopImmediatePropagation();
  status('Selected '+(rig()?.bones.find(b=>b.id===se220Joint)?.label||se220Joint)+' joint. Edit it in the rig panel.');
 }
 function installPicker(){
  if(!renderer?.domElement||canvases.has(renderer.domElement))return;
  canvases.add(renderer.domElement);
  renderer.domElement.addEventListener('pointerdown',picker,true);
 }
 function sync(){
  if(!panel)return;
  maskUI();schemaUI();helpers();
  installPicker();updateVisual();
 }
 function schedule(){
  if(pending)return;
  pending=true;
  queueMicrotask(()=>{pending=false;sync();});
 }
 function observe(){
  if(!panel||observedPanel===panel)return;
  observer?.disconnect();observedPanel=panel;
  observer=new MutationObserver(schedule);
  observer.observe(panel,{attributes:true,attributeFilter:['data-se496-studio'],
   childList:true,subtree:true});
 }
 const prevBind=se220RigBind;
 se220RigBind=function(...args){
  // Old skeleton helpers are recreated by the original binder; release the
  // previous helper when replacing a live rig without a full scene rebuild.
  const old=se220BoneOverlay;
  if(old?.parent){
   old.parent.remove(old);old.geometry?.dispose();old.material?.dispose();
  }
  disposeVisual();
  const out=prevBind.apply(this,args);
  buildVisual();helpers();return out;
 };
 const prevPose=se220RigPose;
 se220RigPose=function(...args){
  const result=prevPose.apply(this,args);updateVisual();return result;
 };
 const prevFrame=se220RigFrame;
 se220RigFrame=function(...args){
  const result=prevFrame.apply(this,args);updateVisual();return result;
 };
 const prevOpen=open;
 open=function(...args){
  const result=prevOpen.apply(this,args);
  if(result!==false){observe();installPicker();schedule();}
  return result;
 };
 const prevClose=close;
 close=function(...args){
  maskUI(); // restore native mode if needed when reentering
  disposeVisual();
  const out=prevClose.apply(this,args);
  return out;
 };
 const prevRefresh=se220RigRefresh;
 se220RigRefresh=function(...args){
  const result=prevRefresh.apply(this,args);schedule();return result;
 };
 return Object.freeze({refresh:sync,mode,visual:()=>({
  installed:!!visual,bones:visual?.items.length||0,visible:!!visual?.group.visible,
  legacyHidden:masked.size,rigSchema:rig()?.schema||null
 })});
})();
window.SWYRL_ENGINE_RIG_POLISH_498=se498RigPolish;
