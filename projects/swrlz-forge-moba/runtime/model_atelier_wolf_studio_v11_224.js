// §E v11.224 · native wolf SkinnedMesh armature, editable bones, clip studio.
// Runs only for newly loaded wolf starters carrying wolfRig. No extra renderer.
let se224WolfBones=null,se224WolfSkeleton=null,se224WolfHelper=null;
const se224WolfPreview={playing:false,clip:'idle',start:0,elapsed:0};
const se224WolfCurrent=()=>model()?.wolfRig;
const se224WolfActive=()=>se224WolfRigValid(se224WolfCurrent());
function se224WolfRigMesh(part){
 if(!se224WolfActive())return se220RigMesh(part);
 const g=atelierSculptApply(geometry(part),part),mat=material(part),pos=g.getAttribute('position');
 if(!pos)return new THREE.Mesh(g,mat);
 const rig=se224WolfCurrent(),indexById=Object.fromEntries(rig.bones.map((b,i)=>[b.id,i]));
 const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),
  new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale));
 const v=new THREE.Vector3(),ids=[],weights=[];
 for(let i=0;i<pos.count;i++){
  v.fromBufferAttribute(pos,i).applyMatrix4(matrix);
  const inf=se224WolfVertexWeights([v.x,v.y,v.z],rig,part,indexById);
  ids.push(...inf.indexes);weights.push(...inf.weights);
 }
 g.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(ids,4));
 g.setAttribute('skinWeight',new THREE.Float32BufferAttribute(weights,4));
 const mesh=new THREE.SkinnedMesh(g,mat);mesh.normalizeSkinWeights();return mesh;
}
function se224WolfRigBind(){
 se224WolfBones=null;se224WolfSkeleton=null;se224WolfHelper=null;
 if(!se224WolfActive()||!modelRoot)return;
 const rig=se224WolfCurrent(),map={};
 for(const b of rig.bones){
  const bone=new THREE.Bone();bone.name=b.id;
  const par=b.parent?rig.bones.find(x=>x.id===b.parent):null,origin=par?par.rest:[0,0,0];
  bone.position.set(...b.rest.map((v,i)=>v-origin[i]));
  if(par)map[par.id].add(bone);else modelRoot.add(bone);
  map[b.id]=bone;
 }
 modelRoot.updateMatrixWorld(true);
 const skeleton=new THREE.Skeleton(rig.bones.map(b=>map[b.id]));
 skeleton.calculateInverses();
 for(const mesh of modelRoot.children){
  if(!mesh.isSkinnedMesh)continue;
  mesh.updateMatrixWorld(true);
  mesh.bind(skeleton,mesh.matrixWorld.clone());mesh.frustumCulled=false;
 }
 se224WolfBones=map;se224WolfSkeleton=skeleton;
 const helper=new THREE.SkeletonHelper(map.wolf_root);
 helper.material.depthTest=false;helper.material.transparent=true;
 helper.material.opacity=.8;helper.material.color.set('#ffca73');
 helper.renderOrder=180;helper.visible=!!document.getElementById('modelAtelierWolfBones')?.checked;
 helper.userData.atelierHelper=true;modelRoot.add(helper);
 se224WolfHelper=helper;
 se224WolfApplyPose(rig.pose);
}
function se224WolfApplyPose(rotations,bob=0){
 if(!se224WolfBones||!se224WolfSkeleton||!se224WolfActive())return;
 const rig=se224WolfCurrent();
 for(const b of rig.bones){
  const angles=rotations?.[b.id]||[0,0,0];
  se224WolfBones[b.id]?.rotation.set(...angles);
 }
 const root=se224WolfBones.wolf_root,base=rig.bones[0].rest;
 root.position.set(base[0],base[1]+bob,base[2]);
 root.updateMatrixWorld(true);se224WolfSkeleton.update();
}
function se224WolfIsModel(){
 return se224WolfActive()&&(
  currentProject?.canonicalId==='wolf-model'||model()?.wolfAnimations?.schema==='swyrl-wolf-joint-clips-v1');
}
function se224WolfStudioInstall(){
 if(!panel||document.getElementById('modelAtelierWolfStudio'))return;
 const controls=panel.querySelector('.atelier-viewport-controls');if(!controls)return;
 const ui=document.createElement('details');ui.id='modelAtelierWolfStudio';
 ui.className='atelier-wolf-studio';
 ui.innerHTML=`<summary>🐺 Astra · Wolf Rig & Motion</summary>
  <div class="atelier-wolf-panel">
   <label>Wolf animation <select id="modelAtelierWolfClip" aria-label="Wolf animation"></select></label>
   <div class="atelier-wolf-actions">
    <button type="button" id="modelAtelierWolfPlay">▶ Preview</button>
    <button type="button" id="modelAtelierWolfReset">Reset pose</button>
   </div>
   <label>Playhead <output id="modelAtelierWolfTimeValue">0.00s</output>
    <input id="modelAtelierWolfTime" type="range" min="0" max="2.8" step=".02" value="0"></label>
   <label>Bone <select id="modelAtelierWolfBone" aria-label="Wolf armature bone"></select></label>
   <div class="atelier-wolf-axes">
    <label>Bend / X <output id="modelAtelierWolfXValue">0°</output>
     <input id="modelAtelierWolfX" type="range" min="-1.4" max="1.4" step=".02" value="0"></label>
    <label>Twist / Y <output id="modelAtelierWolfYValue">0°</output>
     <input id="modelAtelierWolfY" type="range" min="-1.4" max="1.4" step=".02" value="0"></label>
    <label>Roll / Z <output id="modelAtelierWolfZValue">0°</output>
     <input id="modelAtelierWolfZ" type="range" min="-1.4" max="1.4" step=".02" value="0"></label>
   </div>
   <label class="atelier-wolf-check"><input id="modelAtelierWolfBones" type="checkbox"> Show 14-bone skeleton</label>
   <button type="button" id="modelAtelierWolfSaveKey">Save pose at playhead</button>
   <small>Head, jaw, spine, tail and four two-joint legs. Keys are saved to model JSON.</small>
  </div>`;
 controls.append(ui);
 const by=id=>document.getElementById('modelAtelierWolf'+id);
 const clipSelect=by('Clip'),boneSelect=by('Bone');
 const rig=se224WolfRigSpec();
 for(const [name,duration] of SE224_WOLF_MOTIONS){
  const option=document.createElement('option');option.value=name;
  option.textContent=name[0].toUpperCase()+name.slice(1)+' · '+duration+'s';clipSelect.add(option);
 }
 for(const b of rig.bones){
  const option=document.createElement('option');option.value=b.id;option.textContent=b.id.replaceAll('_',' ');
  boneSelect.add(option);
 }
 let boneId='wolf_head';boneSelect.value=boneId;
 const sliderUpdate=()=>{
  const angles=se224WolfCurrent()?.pose?.[boneId]||[0,0,0];
  for(const [i,axis] of ['X','Y','Z'].entries()){
   by(axis).value=angles[i];by(axis+'Value').textContent=Math.round(angles[i]*180/Math.PI)+'°';
  }
 };
 boneSelect.addEventListener('change',()=>{boneId=boneSelect.value;sliderUpdate();});
 for(const [i,axis] of ['X','Y','Z'].entries()){
  by(axis).addEventListener('input',e=>{
   if(!se224WolfIsModel())return;
   se224WolfPreview.playing=false;by('Play').textContent='▶ Preview';
   const pose=se224WolfCurrent().pose;
   pose[boneId]=pose[boneId]||[0,0,0];pose[boneId][i]=Number(e.target.value);
   se224WolfApplyPose(pose);sliderUpdate();
  });
  by(axis).addEventListener('change',()=>{if(se224WolfIsModel()){markDirty();status('Wolf bone pose changed. Save a key to animate it.');}});
 }
 const changeClip=()=>{
  const c=model()?.wolfAnimations?.clips?.find(c=>c.name===clipSelect.value);
  by('Time').max=String(c?.duration||2.8);
  by('Time').value='0';se224WolfPreview.elapsed=0;
  const sample=c?.keys?.[0];if(sample&&se224WolfIsModel()){
   se224WolfCurrent().pose=structuredClone(sample.rotations);
   se224WolfApplyPose(sample.rotations,sample.bodyBob);sliderUpdate();
  }
 };
 clipSelect.addEventListener('change',()=>{se224WolfPreview.playing=false;by('Play').textContent='▶ Preview';changeClip();});
 by('Time').addEventListener('input',()=>{
  if(!se224WolfIsModel())return;
  se224WolfPreview.playing=false;by('Play').textContent='▶ Preview';
  se224WolfPreview.elapsed=Number(by('Time').value);
  const clip=model().wolfAnimations.clips.find(c=>c.name===clipSelect.value);
  const sample=se224WolfSampleClip(clip,se224WolfPreview.elapsed);
  if(sample){se224WolfCurrent().pose=structuredClone(sample.rotations);
   se224WolfApplyPose(sample.rotations,sample.bodyBob);sliderUpdate();}
  by('TimeValue').textContent=se224WolfPreview.elapsed.toFixed(2)+'s';
 });
 by('Play').addEventListener('click',()=>{
  if(!se224WolfIsModel())return;
  se224WolfPreview.playing=!se224WolfPreview.playing;
  se224WolfPreview.start=performance.now()/1000-se224WolfPreview.elapsed;
  by('Play').textContent=se224WolfPreview.playing?'■ Stop':'▶ Preview';
  if(!se224WolfPreview.playing)se224WolfApplyPose(se224WolfCurrent().pose);
 });
 by('Reset').addEventListener('click',()=>{
  if(!se224WolfIsModel())return;
  se224WolfPreview.playing=false;by('Play').textContent='▶ Preview';
  const pose=se224WolfRigSpec().pose;
  se224WolfCurrent().pose=pose;se224WolfApplyPose(pose);sliderUpdate();
  markDirty();status('Wolf armature returned to neutral pose.');
 });
 by('Bones').addEventListener('change',e=>{
  if(se224WolfHelper)se224WolfHelper.visible=e.target.checked;
 });
 by('SaveKey').addEventListener('click',()=>{
  if(!se224WolfIsModel())return;
  const clip=model()?.wolfAnimations?.clips?.find(c=>c.name===clipSelect.value);
  if(!clip)return;
  const t=+se224WolfPreview.elapsed.toFixed(4);
  const index=clip.keys.findIndex(k=>Math.abs(k.time-t)<.015);
  if(index<0&&clip.keys.length>=64){status('Max 64 wolf keys per clip.',true);return;}
  const key={time:t,rotations:structuredClone(se224WolfCurrent().pose),bodyBob:0};
  if(index<0)clip.keys.push(key);else clip.keys[index]=key;
  clip.keys.sort((a,b)=>a.time-b.time);markDirty();
  status('Saved '+boneId+' pose into wolf '+clip.name+' at '+t.toFixed(2)+'s.');
 });
 changeClip();
}
function se224WolfPreviewFrame(){
 const ui=document.getElementById('modelAtelierWolfStudio');
 if(ui)ui.hidden=!se224WolfIsModel();
 if(!se224WolfIsModel()){
  se224WolfPreview.playing=false;return;
 }
 if(!se224WolfPreview.playing||!se224WolfSkeleton)return;
 const clip=model().wolfAnimations?.clips?.find(c=>c.name===document.getElementById('modelAtelierWolfClip')?.value);
 if(!clip)return;
 se224WolfPreview.elapsed=(performance.now()/1000-se224WolfPreview.start)%clip.duration;
 const sample=se224WolfSampleClip(clip,se224WolfPreview.elapsed);
 if(sample)se224WolfApplyPose(sample.rotations,sample.bodyBob);
 const time=document.getElementById('modelAtelierWolfTime');
 if(time)time.value=String(se224WolfPreview.elapsed);
 const label=document.getElementById('modelAtelierWolfTimeValue');
 if(label)label.textContent=se224WolfPreview.elapsed.toFixed(2)+'s';
}
function se224WolfPreviewClose(){
 se224WolfPreview.playing=false;se224WolfPreview.elapsed=0;se224WolfBones=null;
 se224WolfSkeleton=null;se224WolfHelper=null;
 const b=document.getElementById('modelAtelierWolfPlay');if(b)b.textContent='▶ Preview';
}

window.SWYRL_ENGINE_WOLF_RIG=Object.freeze({status:()=>({
 available:se224WolfIsModel(),bones:se224WolfCurrent()?.bones?.length||0,
 skinned:!!se224WolfSkeleton,
 skinnedMeshes:modelRoot?.children?.filter(m=>m.isSkinnedMesh)?.length||0,
 headX:se224WolfBones?.wolf_head?.rotation.x||0,
 jawX:se224WolfBones?.wolf_jaw?.rotation.x||0,
 foreLegX:se224WolfBones?.wolf_fore_l?.rotation.x||0,
 clips:model()?.wolfAnimations?.clips?.length||0,
 playing:se224WolfPreview.playing
})});
