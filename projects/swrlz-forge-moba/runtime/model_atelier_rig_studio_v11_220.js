// §E v11.220 · Native Model Atelier Rigging / Posing / Animation Studio.
// GPU SkinnedMesh LBS (not part translation posing), authored bone keyframes,
// and a compact touch-friendly panel. Only projects carrying a valid rig use it.
let se220Bones=null,se220Skeleton=null,se220BoneOverlay=null,se220Playing=false;
let se220PlayBegin=0,se220Time=0,se220Joint='index_mcp',se220PoseHistory=[];
const se220Rig=()=>model()?.rigging;
function se220RigAvailable(){
 const r=se220Rig();return !!r&&se220RigValidate(r);
}
function se220RigMesh(part){
 const g=atelierSculptApply(geometry(part),part),mat=material(part);
 if(!se220RigAvailable())return new THREE.Mesh(g,mat);
 const rig=se220Rig(),pos=g.getAttribute('position');
 if(!pos)return new THREE.Mesh(g,mat);
 const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation));
 const transform=new THREE.Matrix4().compose(
  new THREE.Vector3(...part.position),q,new THREE.Vector3(...part.scale));
 const vertex=new THREE.Vector3(),indices=[],weights=[];
 for(let i=0;i<pos.count;i++){
  vertex.fromBufferAttribute(pos,i).applyMatrix4(transform);
  const inf=se220RigWeights([vertex.x,vertex.y,vertex.z],rig);
  indices.push(...inf.indices);weights.push(...inf.weights);
 }
 g.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(indices,4));
 g.setAttribute('skinWeight',new THREE.Float32BufferAttribute(weights,4));
 const mesh=new THREE.SkinnedMesh(g,mat);
 mesh.normalizeSkinWeights();
 return mesh;
}
function se220RigBind(){
 se220Bones=null;se220Skeleton=null;se220BoneOverlay=null;
 if(!modelRoot||!se220RigAvailable())return;
 const rig=se220Rig(),map={};
 for(const spec of rig.bones){
  const bone=new THREE.Bone();bone.name=spec.id;map[spec.id]=bone;
  const parent=spec.parent?rig.bones.find(x=>x.id===spec.parent):null;
  const origin=parent?parent.rest:[0,0,0];
  bone.position.set(spec.rest[0]-origin[0],spec.rest[1]-origin[1],spec.rest[2]-origin[2]);
  if(parent)map[parent.id].add(bone);else modelRoot.add(bone);
 }
 modelRoot.updateMatrixWorld(true);
 const bones=rig.bones.map(spec=>map[spec.id]);
 const skeleton=new THREE.Skeleton(bones);
 skeleton.calculateInverses();
 for(const mesh of modelRoot.children){
  if(!mesh.isSkinnedMesh)continue;
  mesh.updateMatrixWorld(true);
  mesh.bind(skeleton,mesh.matrixWorld.clone());
  mesh.frustumCulled=false; // posed tips may leave neutral bounds
 }
 se220Skeleton=skeleton;se220Bones=map;
 const root=bones[0],overlay=new THREE.SkeletonHelper(root);
 overlay.material.depthTest=false;overlay.material.transparent=true;
 overlay.material.opacity=.78;overlay.material.color.set('#4be2fa');
 overlay.renderOrder=180;overlay.visible=!!$m('RigShowBones')?.checked;
 overlay.userData.atelierHelper=true;modelRoot.add(overlay);
 se220BoneOverlay=overlay;
 se220RigPose(rig.pose);
}
function se220RigPose(pose){
 if(!se220Bones||!se220RigAvailable())return;
 for(const b of se220Rig().bones){
  const v=pose?.[b.id]||[0,0,0];
  se220Bones[b.id]?.rotation.set(...v);
 }
 se220Skeleton?.bones[0]?.updateMatrixWorld(true);
 se220Skeleton?.update();
}
function se220RigRemember(){
 if(!se220RigAvailable())return;
 se220PoseHistory.push(JSON.stringify({pose:se220Rig().pose,timeline:se220Rig().timeline}));
 if(se220PoseHistory.length>30)se220PoseHistory.shift();
}
function se220RigTouched(message){
 const m=model();if(m)m.editedAt='local';
 if(typeof markDirty==='function')markDirty();
 if(message)status(message);
}
const se220R=id=>$m('Rig'+id);
function se220RigJointUI(){
 const rig=se220Rig(),joint=rig?.pose?.[se220Joint]||[0,0,0];
 for(let i=0;i<3;i++){
  const input=se220R(['X','Y','Z'][i]),label=se220R(['XValue','YValue','ZValue'][i]);
  if(input)input.value=String(joint[i]||0);
  if(label)label.textContent=Math.round((joint[i]||0)*180/Math.PI)+'°';
 }
}
function se220RigRefresh(){
 const panelRig=se220R('Studio');
 if(!panelRig)return;
 const active=se220RigAvailable();
 panelRig.hidden=!active;
 const old=$m('PoseDeck');if(old)old.hidden=active;
 if(!active){se220Playing=false;return;}
 const rig=se220Rig(),joint=se220R('Joint');
 if(!rig.bones.some(x=>x.id===se220Joint))se220Joint=rig.bones[2].id;
 if(joint){
  const chosen=joint.value;
  joint.replaceChildren(...rig.bones.map(b=>{
   const o=document.createElement('option');o.value=b.id;o.textContent=b.label;return o;
  }));
  joint.value=rig.bones.some(b=>b.id===chosen)?chosen:se220Joint;
  se220Joint=joint.value;
 }
 const time=se220R('Time');
 if(time){time.max=String(rig.duration);time.value=String(se220Clamp(se220Time,0,rig.duration));}
 const length=se220R('Length');if(length)length.value=String(rig.duration);
 const loop=se220R('Loop');if(loop)loop.checked=rig.loop;
 se220RigJointUI();se220RigTimeLabel();
}
function se220RigTimeLabel(){
 const readout=se220R('TimeValue');
 if(readout)readout.textContent=se220Time.toFixed(2)+' s / '+(se220Rig()?.duration||0).toFixed(2)+' s';
 const keys=se220R('KeyList');
 if(keys)keys.textContent=(se220Rig()?.timeline||[]).map(k=>k.time.toFixed(2)).join(' · ')+' s';
}
function se220RigControlsInstall(){
 const host=panel?.querySelector('.atelier-scene');
 if(!host||se220R('Studio'))return;
 const rigUI=document.createElement('details');
 rigUI.id='modelAtelierRigStudio';rigUI.className='atelier-rig-studio';
 rigUI.hidden=true;
 rigUI.innerHTML=`
 <summary>🦴 Rig · Pose · Animate</summary>
 <div class="atelier-rig-body">
  <label>Joint <select id="modelAtelierRigJoint" aria-label="Select skeleton joint"></select></label>
  <div class="atelier-rig-axes">
   <label>Curl / X <span id="modelAtelierRigXValue">0°</span><input type="range" id="modelAtelierRigX" min="-1.4" max="1.4" step=".02" value="0"></label>
   <label>Twist / Y <span id="modelAtelierRigYValue">0°</span><input type="range" id="modelAtelierRigY" min="-1.4" max="1.4" step=".02" value="0"></label>
   <label>Spread / Z <span id="modelAtelierRigZValue">0°</span><input type="range" id="modelAtelierRigZ" min="-1.4" max="1.4" step=".02" value="0"></label>
  </div>
  <div class="atelier-rig-actions">
   <button type="button" id="modelAtelierRigOpen">Open</button>
   <button type="button" id="modelAtelierRigFist">Fist</button>
   <button type="button" id="modelAtelierRigPoint">Point</button>
   <button type="button" id="modelAtelierRigPinch">Pinch</button>
  </div>
  <label class="atelier-rig-check"><input type="checkbox" id="modelAtelierRigShowBones"> Show skeleton pivots</label>
  <div class="atelier-rig-timeline">
   <label>Time <span id="modelAtelierRigTimeValue">0.00 s</span>
    <input id="modelAtelierRigTime" type="range" min="0" max="1.5" step=".05" value="0">
   </label>
   <label>Clip length (seconds) <input id="modelAtelierRigLength" type="number" min=".5" max="10" step=".5" value="1.5"></label>
   <label class="atelier-rig-check"><input type="checkbox" id="modelAtelierRigLoop" checked> Loop</label>
  </div>
  <div class="atelier-rig-actions">
   <button type="button" id="modelAtelierRigKey">Save key</button>
   <button type="button" id="modelAtelierRigDeleteKey">Delete key</button>
   <button type="button" id="modelAtelierRigPlay">▶ Play</button>
   <button type="button" id="modelAtelierRigStop">■ Stop</button>
  </div>
  <button type="button" id="modelAtelierRigUndo" class="atelier-rig-undo">Undo pose edit</button>
  <small>Key times: <span id="modelAtelierRigKeyList">0 · .75 · 1.5 s</span></small>
  <small>17 hierarchical bones · four-influence mesh skinning. Save Project or JSON to keep poses and clip.</small>
 </div>`;
 host.append(rigUI);
 const joint=se220R('Joint');
 joint.addEventListener('change',e=>{se220Joint=e.target.value;se220RigJointUI();});
 for(const [i,axis] of ['X','Y','Z'].entries()){
  const slider=se220R(axis);let changed=false;
  slider.addEventListener('pointerdown',()=>{changed=false;});
  slider.addEventListener('input',()=>{
   const rig=se220Rig();if(!se220RigAvailable())return;
   if(!changed){se220RigRemember();changed=true;}
   const current=rig.pose[se220Joint]?.slice()||[0,0,0];
   current[i]=Number(slider.value);
   rig.pose[se220Joint]=current;se220RigPose(rig.pose);se220RigJointUI();
  });
  slider.addEventListener('change',()=>{changed=false;se220RigTouched('Rig bone rotation updated. Save a timeline key to animate this pose.');});
 }
 for(const kind of ['Open','Fist','Point','Pinch']){
  se220R(kind).addEventListener('click',()=>{
   if(!se220RigAvailable())return;
   se220Playing=false;se220RigRemember();
   se220Rig().pose=se220RigPreset(se220Rig(),kind.toLowerCase());
   se220RigPose(se220Rig().pose);se220RigJointUI();
   se220RigTouched(kind+' hand pose applied to actual weighted skin.');
  });
 }
 se220R('ShowBones').addEventListener('change',e=>{
  if(se220BoneOverlay)se220BoneOverlay.visible=e.target.checked;
 });
 se220R('Time').addEventListener('input',e=>{
  if(!se220RigAvailable())return;
  se220Playing=false;se220Time=Number(e.target.value);
  se220Rig().pose=se220RigInterpolate(se220Rig(),se220Time);
  se220RigPose(se220Rig().pose);se220RigJointUI();se220RigTimeLabel();
 });
 se220R('Length').addEventListener('change',e=>{
  if(!se220RigAvailable())return;
  const r=se220Rig(),value=Number(e.target.value);
  if(!Number.isFinite(value)||value<.5||value>10){e.target.value=r.duration;return;}
  se220RigRemember();r.duration=value;r.timeline=r.timeline.filter(k=>k.time<=value);
  se220Time=Math.min(se220Time,value);se220R('Time').max=String(value);
  se220RigTimeLabel();se220RigTouched('Clip duration updated.');
 });
 se220R('Loop').addEventListener('change',e=>{
  if(!se220RigAvailable())return;
  se220Rig().loop=e.target.checked;se220RigTouched();
 });
 se220R('Key').addEventListener('click',()=>{
  if(!se220RigAvailable())return;
  const rig=se220Rig(),at=+se220Time.toFixed(2);
  const exist=rig.timeline.findIndex(k=>Math.abs(k.time-at)<.02);
  if(exist<0&&rig.timeline.length>=32){status('Maximum 32 keyframes.',true);return;}
  se220RigRemember();
  const key={time:at,pose:structuredClone(rig.pose)};
  if(exist>=0)rig.timeline[exist]=key;else rig.timeline.push(key);
  rig.timeline.sort((a,b)=>a.time-b.time);se220RigTimeLabel();
  se220RigTouched('Skeletal pose key saved at '+at.toFixed(2)+' s.');
 });
 se220R('DeleteKey').addEventListener('click',()=>{
  if(!se220RigAvailable())return;
  const rig=se220Rig(),i=rig.timeline.findIndex(k=>Math.abs(k.time-se220Time)<.025);
  if(i<0){status('Move the playhead to a saved key before deleting it.');return;}
  se220RigRemember();rig.timeline.splice(i,1);se220RigTimeLabel();se220RigTouched('Deleted keyframe.');
 });
 se220R('Play').addEventListener('click',()=>{
  if(!se220RigAvailable()||se220Rig().timeline.length<2){status('Add at least two skeletal keys to play.',true);return;}
  se220Playing=true;se220PlayBegin=performance.now()-se220Time*1000;
  status('Playing native weighted hand rig · pose keyframes interpolate in the viewport.');
 });
 se220R('Stop').addEventListener('click',()=>{
  se220Playing=false;se220RigPose(se220Rig()?.pose);
  status('Playback stopped. Joint sliders remain editable.');
 });
 se220R('Undo').addEventListener('click',()=>{
  if(!se220RigAvailable()||!se220PoseHistory.length)return;
  se220Playing=false;
  const old=JSON.parse(se220PoseHistory.pop());
  Object.assign(se220Rig(),old);se220RigPose(se220Rig().pose);
  se220RigRefresh();se220RigTouched('Undo skeletal pose edit.');
 });
 window.SWYRL_ENGINE_RIG_STUDIO=Object.freeze({status:()=>({
  available:se220RigAvailable(),bones:se220Rig()?.bones?.length||0,
  keys:se220Rig()?.timeline?.length||0,playing:se220Playing,
  skinned:!!se220Skeleton
 })});
}
function se220RigFrame(){
 if(!se220Playing||!se220RigAvailable()||!se220Skeleton)return;
 const r=se220Rig(),elapsed=(performance.now()-se220PlayBegin)/1000;
 if(elapsed>=r.duration&&!r.loop){se220Playing=false;se220Time=r.duration;}
 else se220Time=elapsed%r.duration;
 se220RigPose(se220RigInterpolate(r,se220Time));
 if(se220R('Time'))se220R('Time').value=String(se220Time);
 se220RigTimeLabel();
}
function se220RigClose(){
 se220Playing=false;se220Bones=null;se220Skeleton=null;
 se220BoneOverlay=null;se220PoseHistory=[];se220Time=0;
}
