/* §E v11.496: unified Model / Rigging / Animation mini-studios.
   Existing renderer, camera, model, rig and animation data stay authoritative. */
const se496MiniStudios=(()=>{
 'use strict';
 const modes=['model','rig','animate'];let active='model';
 const $=id=>panel?.querySelector('#'+id);
 const rig=()=>se220RigAvailable()?se220Rig():null;
 const selectedBone=()=>rig()?.bones.find(b=>b.id===se220Joint)||null;
 function refreshFields(){
  const r=rig(),b=selectedBone(),e=r?.envelopes?.find(x=>x.bone===b?.id);
  for(let i=0;i<3;i++){const el=$('se496Rest'+i);if(el){el.disabled=!b;el.value=b?String(b.rest[i]):'';}}
  const input=$('se496Strength');if(input){input.disabled=!e;input.value=e?String(e.strength):'0';}
  const value=$('se496StrengthValue');if(value)value.textContent=e?Math.round(e.strength*100)+'%':'Root';
  const count=$('se496BoneCount');if(count)count.textContent=r?r.bones.length+' bones · computed skin weights':'No valid skeleton';
  const add=$('se496AddBone');if(add)add.disabled=!r||r.schema!=='swyrl-cloth-skin-v1'||r.bones.length>=48;
 }
 function publishRig(message){
  se220Playing=false;renderParts();se220RigBind();se220RigRefresh();
  se220RigTouched(message);refreshFields();update();
 }
 function createRig(){
  if(rig()){status('This model already has a valid rig.');return;}
  if(model()?.rigging){status('Existing rig data is invalid; refusing to overwrite.',true);return;}
  const m=model(),part=partById(selection)||m?.parts?.[0];
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData?.atelierId===part?.id);
  if(!mesh){status('Select a visible mesh to rig.',true);return;}
  mesh.updateWorldMatrix(true,false);
  const bounds=new THREE.Box3().setFromObject(mesh);
  if(bounds.isEmpty()){status('No geometry available to rig.',true);return;}
  const size=bounds.getSize(new THREE.Vector3()),center=bounds.getCenter(new THREE.Vector3());
  if(![...size.toArray(),...center.toArray()].every(Number.isFinite)||
   Math.max(...size.toArray())>35||[...bounds.min.toArray(),...bounds.max.toArray()].some(n=>Math.abs(n)>=19)){
   status('Scale and recenter the selected mesh before rigging.',true);return;
  }
  const low=bounds.min.y,high=bounds.max.y,mid=(low+high)/2,h=Math.max(.12,high-low);
  const rad=[Math.min(9,Math.max(.12,size.x*.65)),Math.min(9,Math.max(.2,h*.48)),Math.min(9,Math.max(.12,size.z*.65))];
  const timeline=[{time:0,pose:{}},{time:2,pose:{}}];
  const data={schema:'swyrl-cloth-skin-v1',algorithm:'linear-blend-4',targetPartId:part.id,
   bones:[{id:'root',label:'Root',parent:null,rest:[center.x,low,center.z]},
    {id:'lower',label:'Lower',parent:'root',rest:[center.x,mid,center.z]},
    {id:'upper',label:'Upper',parent:'lower',rest:[center.x,high,center.z]}],
   envelopes:[{bone:'lower',center:[center.x,(low+mid)/2,center.z],radii:rad.slice(),strength:.72},
    {bone:'upper',center:[center.x,(mid+high)/2,center.z],radii:rad.slice(),strength:.90}],
   duration:2,loop:true,pose:{},timeline:structuredClone(timeline),activeClip:'idle',
   clips:{idle:{label:'Idle',duration:2,loop:true,timeline:structuredClone(timeline)}}};
  if(!se220RigValidate(data)){status('Skeleton failed validation; mesh unchanged.',true);return;}
  m.rigging=data;se220Joint='lower';se220Time=0;
  publishRig('Editable three-bone armature created. Save Project to retain it.');
 }
 function addBone(){
  const r=rig(),parent=selectedBone();if(!r||r.schema!=='swyrl-cloth-skin-v1'||!parent||r.bones.length>=48)return;
  const letter=[...'abcdefghijklmnopqrstuvwxyz'].find(a=>!r.bones.some(b=>b.id==='joint'+a));
  if(!letter){status('Bone limit reached.',true);return;}
  const id='joint'+letter,rest=parent.rest.slice();rest[1]=Math.min(19.8,rest[1]+.18);
  r.bones.push({id,label:'Joint '+letter.toUpperCase(),parent:parent.id,rest});
  r.envelopes.push({bone:id,center:rest.slice(),radii:[.55,.55,.55],strength:.55});
  if(!se220RigValidate(r)){r.bones.pop();r.envelopes.pop();status('Joint rejected by rig validation.',true);return;}
  se220Joint=id;publishRig('Child joint added.');
 }
 function changeRest(axis,value){
  const r=rig(),b=selectedBone(),v=Number(value);
  if(!r||r.schema!=='swyrl-cloth-skin-v1'||!b||!Number.isFinite(v)||Math.abs(v)>=19.9){refreshFields();return;}
  const previous=b.rest[axis];if(previous===v)return;
  const e=r.envelopes.find(x=>x.bone===b.id);b.rest[axis]=v;if(e)e.center[axis]+=v-previous;
  if(!se220RigValidate(r)){
   b.rest[axis]=previous;if(e)e.center[axis]-=v-previous;
   status('Joint placement exceeds supported bounds.',true);refreshFields();return;
  }
  publishRig('Bone rest position updated.');
 }
 function changeStrength(value){
  const e=rig()?.envelopes?.find(x=>x.bone===selectedBone()?.id),v=Number(value);
  if(!e||!Number.isFinite(v)||v<0||v>1)return;
  e.strength=v;publishRig('Bone influence updated and skin rebound.');
 }
 function install(){
  if(!panel||$('se496ModeTabs'))return;
  const head=panel.querySelector('.atelier-head'),scene=panel.querySelector('.atelier-scene');
  if(!head||!scene)return;
  const tabs=document.createElement('nav');tabs.id='se496ModeTabs';tabs.setAttribute('aria-label','Model workspace mode');
  for(const [mode,label] of [['model','Model'],['rig','Rigging'],['animate','Animation']]){
   const button=document.createElement('button');button.type='button';button.dataset.studio=mode;button.textContent=label;
   button.addEventListener('click',()=>setMode(mode));tabs.append(button);
  }
  head.querySelector('.atelier-actions')?.before(tabs);
  const setup=document.createElement('section');setup.id='se496RigSetup';
  setup.innerHTML='<strong id="se496EmptyTitle"></strong><p id="se496EmptyMessage"></p><button type="button" id="se496CreateRig">Create editable three-bone rig</button><button type="button" id="se496GoRig">Open Rigging</button>';
  scene.append(setup);
  $('se496CreateRig').addEventListener('click',createRig);
  $('se496GoRig').addEventListener('click',()=>setMode('rig'));
  const native=se220R('Studio'),body=native?.querySelector('.atelier-rig-body');
  if(body&&!$('se496BoneAuthoring')){
   const editor=document.createElement('section');editor.id='se496BoneAuthoring';
   editor.innerHTML='<strong>Skeleton authoring</strong><small id="se496BoneCount"></small><button type="button" id="se496AddBone">Add child to selected joint</button><div class="se496-rest"><label>Rest X<input id="se496Rest0" type="number" step=".05"></label><label>Rest Y<input id="se496Rest1" type="number" step=".05"></label><label>Rest Z<input id="se496Rest2" type="number" step=".05"></label></div><label>Bone influence <span id="se496StrengthValue"></span><input id="se496Strength" type="range" min="0" max="1" step=".05"></label><small>Uses bounded automatic skin envelopes. Source mesh and UVs remain unchanged.</small>';
   body.querySelector('.atelier-rig-axes')?.before(editor);
   $('se496AddBone').addEventListener('click',addBone);
   for(let i=0;i<3;i++)$('se496Rest'+i).addEventListener('change',e=>changeRest(i,e.target.value));
   $('se496Strength').addEventListener('change',e=>changeStrength(e.target.value));
   se220R('Joint')?.addEventListener('change',()=>queueMicrotask(refreshFields));
  }
 }
 function update(){
  if(!panel||panel.hidden)return;
  panel.dataset.se496Studio=active;
  for(const button of $('se496ModeTabs')?.querySelectorAll('button')||[]){
   const chosen=button.dataset.studio===active;
   button.setAttribute('aria-pressed',String(chosen));button.tabIndex=chosen?0:-1;
  }
  const valid=!!rig(),native=se220R('Studio');
  if(native){native.hidden=active==='model'||!valid;if(valid&&active!=='model')native.open=true;}
  const setup=$('se496RigSetup');
  if(setup){
   setup.hidden=active==='model'||valid;
   $('se496EmptyTitle').textContent=active==='rig'?'Start Rigging':'No animation armature';
   $('se496EmptyMessage').textContent=active==='rig'?
    'Create an editable rig for the selected mesh. The model and camera stay loaded.':
    'Create or load a skeleton in Rigging before editing animation clips.';
   $('se496CreateRig').hidden=active!=='rig';$('se496GoRig').hidden=active!=='animate';
  }
  if(se220BoneOverlay)se220BoneOverlay.visible=valid&&active==='rig';
  refreshFields();
 }
 function setMode(next,persist=true){
  if(!modes.includes(next)||!panel||panel.hidden||!model())return false;
  if(active==='animate'&&next!=='animate')se220Playing=false;
  active=next;install();se220RigRefresh();update();
  if(persist)window.SWYRL_ENGINE_MODEL_WORKSPACE_490?.persist?.();
  return true;
 }
 const previousOpen=open;
 open=function(...args){
  const result=previousOpen.apply(this,args);
  if(result===false)return result;
  install();
  const saved=model()?.editorWorkspace?.studioMode;
  setMode(modes.includes(saved)?saved:'model',false);
  return result;
 };
 const previousRefresh=se220RigRefresh;
 se220RigRefresh=function(...args){
  const result=previousRefresh.apply(this,args);if($('se496ModeTabs'))update();return result;
 };
 return Object.freeze({mode:()=>active,set:setMode,refresh:update,createRig});
})();
window.SWYRL_ENGINE_MINI_STUDIOS_496=se496MiniStudios;
