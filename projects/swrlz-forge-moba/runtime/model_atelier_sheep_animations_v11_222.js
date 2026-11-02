// Model Atelier scope only. The sheep's editable source vertices stay neutral.
// Preview deforms displayed mesh transforms; neither scene nor history is rewritten.
const se222SheepPreview={playing:false,clip:'idle',start:0,elapsed:0};
const se222SheepRootPoint=(name)=>{
 const limb=/^(Fore|Hind) (left|right)/.exec(name);
 if(limb)return {
  point:[limb[2]==='left'?-.34:.34,limb[1]==='Fore'?1.06:1.02,limb[1]==='Fore'?.49:-.68],
  id:(limb[1]==='Fore'?2:0)+(limb[2]==='right'?1:0)};
 if(name.startsWith('Tail ·'))return {point:[0,1.22,-1],id:'tail'};
 if(/^(Face |Left ear|Right ear|Left eye|Right eye|Nose |Mouth )/.test(name))
  return {point:[0,1.64,.79],id:'head'};
 return null;
};
function se222SheepIsModel(){
 const m=model();
 return !!m&&(currentProject?.canonicalId==='sheep-model'||
  m?.sheepAnimations?.schema==='swyrl-sheep-joint-clips-v1');
}
function se222SheepStudioInstall(){
 if(!panel||document.getElementById('modelAtelierSheepStudio'))return;
 const controls=panel.querySelector('.atelier-viewport-controls');
 if(!controls)return;
 const root=document.createElement('div');
 root.id='modelAtelierSheepStudio';root.className='atelier-sheep-studio';
 const label=document.createElement('label');label.textContent='🐑 Clover motion';
 const select=document.createElement('select');select.id='modelAtelierSheepMotion';
 select.setAttribute('aria-label','Clover sheep animation clip');
 for(const [value,duration,description] of SE222_SHEEP_MOTIONS){
  const o=document.createElement('option');o.value=value;o.textContent=
   value[0].toUpperCase()+value.slice(1)+' · '+duration+'s';o.title=description;select.append(o);
 }
 const play=document.createElement('button');play.type='button';play.textContent='▶ Preview';
 play.id='modelAtelierSheepPlay';play.setAttribute('aria-pressed','false');
 select.addEventListener('change',()=>{
  se222SheepPreview.clip=select.value;se222SheepPreview.start=performance.now()/1000;
  se222SheepPreview.elapsed=0;
 });
 play.addEventListener('click',()=>{
  se222SheepPreview.playing=!se222SheepPreview.playing;
  se222SheepPreview.start=performance.now()/1000-se222SheepPreview.elapsed;
  play.textContent=se222SheepPreview.playing?'■ Stop':'▶ Preview';
  play.setAttribute('aria-pressed',String(se222SheepPreview.playing));
  if(!se222SheepPreview.playing)se222SheepPreviewReset();
 });
 label.append(select);root.append(label,play);controls.append(root);
}
function se222SheepPreviewReset(){
 if(!modelRoot||!model())return;
 for(const mesh of modelRoot.children){
  const p=mesh.userData.atelierId&&partById(mesh.userData.atelierId);
  if(!p)continue;
  mesh.position.fromArray(p.position);mesh.rotation.fromArray(p.rotation);
 }
}
function se222SheepPreviewFrame(){
 const pane=document.getElementById('modelAtelierSheepStudio');
 if(pane)pane.hidden=!se222SheepIsModel();
 if(!se222SheepIsModel()){
  se222SheepPreview.playing=false;se222SheepPreview.elapsed=0;
  return;
 }
 if(!se222SheepPreview.playing||!modelRoot||!model())return;
 const clip=se222SheepPreview.clip;
 se222SheepPreview.elapsed=performance.now()/1000-se222SheepPreview.start;
 const pose=se222SheepPose(clip,se222SheepPreview.elapsed);
 for(const mesh of modelRoot.children){
  const p=mesh.userData.atelierId&&partById(mesh.userData.atelierId);
  if(!p||!mesh.isMesh)continue;
  const joint=se222SheepRootPoint(p.name);
  if(!joint){mesh.position.fromArray(p.position);mesh.rotation.fromArray(p.rotation);continue;}
  const e=new THREE.Euler(
   (joint.id==='head'?pose.head:typeof joint.id==='number'?pose.legs[joint.id]:0),
   (joint.id==='head'?pose.headY:joint.id==='tail'?pose.tail:0),0,'XYZ');
  const origin=new THREE.Vector3(...joint.point);
  const shifted=origin.clone().sub(origin.clone().applyEuler(e));
  mesh.position.fromArray(p.position).add(shifted);
  mesh.rotation.set(p.rotation[0]+e.x,p.rotation[1]+e.y,p.rotation[2]+e.z);
 }
}
function se222SheepPreviewClose(){
 se222SheepPreview.playing=false;se222SheepPreview.elapsed=0;se222SheepPreviewReset();
 const button=document.getElementById('modelAtelierSheepPlay');
 if(button){button.textContent='▶ Preview';button.setAttribute('aria-pressed','false');}
}
