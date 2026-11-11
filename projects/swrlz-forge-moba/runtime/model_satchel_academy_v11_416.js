/* SE416_SATCHEL_ACADEMY_START
 * v11.416 · Seven guided steps, real model inspection, non-editable 3D ghosts,
 * source-owned tool highlights and separate, bounded recovery checkpoints.
 * Save to account uses the existing project serialization; no new backend.
 */
(function se415SatchelAcademy(){
 'use strict';
 const LESSON='satchel-001',MAX_SNAPSHOTS=7,MAX_SNAPSHOT_BYTES=280000,MAX_TOTAL_BYTES=950000;
 let ghostEnabled=false,ghost=null,ghostFor=-1,highlight=null,flatPanel=null;
 const api=()=>window.SWYRL_ENGINE_TUTORIAL_412;
 const current=()=>api()?.status?.();
 const active=()=>current()?.active===true&&currentProject?.se412Tutorial===LESSON;
 const parts=()=>currentProject?.modelAtelier?.parts||[];
 const storedKey=()=> 'se415:satchel:checkpoints:'+String(currentProject?.instanceId||'');
 const $=(sel,root=document)=>root.querySelector(sel);
 const note=message=>{const el=$('#se412Note');if(el)el.textContent=message;};
 const bytes=value=>JSON.stringify(value).length;
 const clone=value=>structuredClone(value);
 const finite3=a=>Array.isArray(a)&&a.length===3&&a.every(v=>Number.isFinite(v));
 function modelReady(){return active()&&currentProject?.kind==='model-atelier'&&Array.isArray(parts());}
 function isBox(p){return p?.kind==='box'&&finite3(p.scale)&&finite3(p.position)&&
  p.scale.every(v=>v>.005)&&(!Array.isArray(p.rotation)||p.rotation.every(v=>Math.abs(v)<.25));}
 function structure(){
  const boxes=parts().filter(isBox);
  const floor=boxes.find(p=>p.scale[0]>=.85&&p.scale[2]>=.35&&p.scale[1]<=.23);
  if(!floor)return {boxes,floor:null,walls:[],wallIds:new Set(),flap:null,straps:[]};
  const wallYs=p=>p.position[1]>floor.position[1]+.18&&p.position[1]<floor.position[1]+1.6;
  const x=boxes.filter(p=>p!==floor&&wallYs(p)&&p.scale[0]<.25&&p.scale[1]>.42&&p.scale[2]>.3
   &&Math.abs(p.position[0]-floor.position[0])>=floor.scale[0]*.34);
  const z=boxes.filter(p=>p!==floor&&wallYs(p)&&p.scale[2]<.25&&p.scale[1]>.42&&p.scale[0]>.62
   &&Math.abs(p.position[2]-floor.position[2])>=floor.scale[2]*.25);
  const left=x.find(p=>p.position[0]<floor.position[0]),right=x.find(p=>p.position[0]>floor.position[0]);
  const front=z.find(p=>p.position[2]>=floor.position[2]),back=z.find(p=>p.position[2]<floor.position[2]);
  const walls=[left,right,front,back].filter(Boolean),wallIds=new Set(walls.map(p=>p.id));
  const roof=boxes.some(p=>p!==floor&&!wallIds.has(p.id)&&p.scale[0]>.7&&p.scale[2]>.32
   &&p.scale[1]<.24&&p.position[1]>floor.position[1]+.5
   &&Math.abs(p.position[2]-floor.position[2])<floor.scale[2]*.3);
  const flap=boxes.find(p=>p!==floor&&!wallIds.has(p.id)&&p.scale[0]>=floor.scale[0]*.5
   &&p.scale[1]<.27&&p.position[1]>floor.position[1]+.42
   &&p.position[2]>=floor.position[2]+floor.scale[2]*.2);
  const straps=boxes.filter(p=>p!==floor&&!wallIds.has(p.id)&&p!==flap&&
   p.scale.filter(dim=>dim<.24).length>=2&&p.position[1]>floor.position[1]+.36);
  return {boxes,floor,walls,wallIds,flap,straps,roof};
 }
 function inspect(index){
  if(!modelReady()||!Number.isInteger(index)||index<0||index>6)return {ok:false,message:'Open your independent Apprentice Satchel project first.'};
  const all=parts(),s=structure(),boxCount=s.boxes.length;
  if(index===0){
   if(all.some(p=>p.kind==='box'&&finite3(p.scale)&&p.scale[0]>=1.2&&p.scale[1]>=.85&&p.scale[2]>=.35))
    return {ok:true,message:'Your body blockout has usable width, height, and depth.'};
   if(s.floor&&s.walls.length===4)return {ok:true,message:'You have already progressed beyond the blockout to an open-top body.'};
   return {ok:false,message:'Enlarge the practice cube: width ≥1.2, height ≥0.85, depth ≥0.35, before reshaping it into a floor.'};
  }
  if(index===1){
   if(!s.floor)return {ok:false,message:'First make a thin box floor (height about 0.1). The current model has no detectable floor slab.'};
   if(s.walls.length<4)return {ok:false,message:'Detected '+s.walls.length+'/4 surrounding thin walls. Add the missing left/right/front/back wall boxes; keep the center empty.'};
   if(s.roof)return {ok:null,message:'Four walls detected, but another slab may cover the top. Inspect from above to verify the opening, then mark manually.'};
   return {ok:true,message:'A thin floor and four surrounding wall boxes form an open top. Visually inspect wall joins for gaps.'};
  }
  if(index===2){
   if(!s.floor||s.walls.length<4)return {ok:false,message:'Finish the floor and surrounding walls before checking the flap.'};
   if(s.flap)return {ok:true,message:'Separate thin flap-like mesh detected above the front opening. Check that its free end actually covers the pouch.'};
   return {ok:false,message:'Create a separate wide, thin box above the opening toward the front and name it Flap.'};
  }
  if(index===3){
   if(s.straps.length>=3){
    const heights=s.straps.map(p=>p.position[1]),span=Math.max(...heights)-Math.min(...heights);
    if(span>.16)return {ok:true,message:'Multiple narrow elevated strap segments detected at different heights. Inspect both attachment ends.'};
   }
   const otherGeometry=all.some(p=>p.kind!=='box');
   return {ok:otherGeometry?null:false,message:otherGeometry
    ?'The strap may use custom geometry that a box-based inspection cannot evaluate. Inspect attachment at both ends, then mark complete yourself.'
    :'Build at least three narrow strap segments at varied heights and bring the ends to the two side walls.'};
  }
  if(index===4){
   const metal=all.filter(p=>p.material==='metal');
   const detail=all.filter(p=>!s.wallIds.has(p.id)&&p!==s.floor&&p!==s.flap&&
    p.scale&&Math.max(...p.scale)<.38);
   if(metal.length&&detail.length>=2)return {ok:true,message:'A metal piece and multiple small details were detected. Inspect attachment, seams and clasp alignment.'};
   return {ok:false,message:'Detected '+metal.length+' metal parts and '+detail.length+' small details. Make a metallic clasp plus at least one small loop, seam or stitch.'};
  }
  if(index===5){
   const leather=all.some(p=>['matte','silk'].includes(p.material)&&
    /^#[0-9a-f]{6}$/i.test(p.color||'')&&p.color.toLowerCase()!=='#ffffff');
   const metal=all.some(p=>p.material==='metal');
   return {ok:leather&&metal,message:leather&&metal
    ?'Leather-like matte material and contrasting metal are present on editable parts.'
    :'Assign matte/silk colored leather to a pouch piece and metallic material to a clasp. VR learners can use the quest Materials controls.'};
  }
  return {ok:null,message:'Rotate through front, side, back and top. Use native Save Project, then Save to Account if you want to reopen this progress on another device. Model saving cannot be proven from shape alone.'};
 }
 function syncProgress(done){
  if(!active())return;
  const now=Date.now(),arr=[...new Set(done)].filter(v=>Number.isInteger(v)&&v>=0&&v<7).sort((a,b)=>a-b);
  currentProject.se415TutorialState={schema:'se415-quest-progress-v1',lesson:LESSON,done:arr,updatedAt:now};
  try{localStorage.setItem('se412:satchel:progress:'+currentProject.instanceId+':updatedAt',String(now));}catch(_){}
 }
 function snapshotMeta(){if(!active())return null;const v=currentProject.se415TutorialState;
  return v&&v.schema==='se415-quest-progress-v1'?clone(v):null;}
 function snapshots(){
  if(!active())return [];
  try{const value=JSON.parse(localStorage.getItem(storedKey())||'[]');
   if(!Array.isArray(value))return [];
   return value.filter(v=>v?.lesson===LESSON&&v?.projectId===currentProject.instanceId&&Array.isArray(v.parts)).slice(-MAX_SNAPSHOTS);
  }catch(_){return [];}
 }
 function saveCheckpoint(){
  if(!modelReady())return {ok:false,message:'Open your tutorial project before saving a checkpoint.'};
  if(window.SWYRL_E_SATCHEL_NATIVE_416?.busy?.())return {ok:false,message:'Finish or cancel the current VR modeling gesture first.'};
  const stamp=current()?.current||0,copy=clone(parts()),done=api().steps().filter(r=>r.done).map(r=>r.index);
  if(!window.SWYRL_E_SATCHEL_NATIVE_416?.validate?.(copy))return {ok:false,message:'Model parts could not be validated. Native model unchanged.'};
  const record={schema:1,lesson:LESSON,projectId:currentProject.instanceId,step:stamp,
   title:api().steps()[stamp]?.title||'Lesson checkpoint',savedAt:Date.now(),parts:copy,done};
  if(bytes(record)>MAX_SNAPSHOT_BYTES)return {ok:false,message:'This model is too large for lightweight local tutorial checkpoints. Use native Save Project instead.'};
  let records=snapshots().filter(r=>r.step!==stamp);records.push(record);
  while(records.length>MAX_SNAPSHOTS||bytes(records)>MAX_TOTAL_BYTES)records.shift();
  try{localStorage.setItem(storedKey(),JSON.stringify(records));}
  catch(error){return {ok:false,message:'Checkpoint storage is full. Use Save Project; no geometry was changed.'};}
  return {ok:true,message:'Checkpoint saved: step '+(stamp+1)+' ('+records.length+' locally stored). Save to Account separately to sync your editable project and quest checkoffs.'};
 }
 function restoreCheckpoint(options={}){
  if(!modelReady())return {ok:false,message:'Open your saved tutorial project first.'};
  const records=snapshots(),record=records[records.length-1];
  if(!record)return {ok:false,message:'No saved checkpoint on this device.'};
  if(!options.confirmed)return {ok:false,requiresConfirmation:true,
   message:'Restore step '+(record.step+1)+' checkpoint? This replaces the current editable parts. Native Undo can reverse this restore.'};
  const copy=clone(record.parts);
  const restored=window.SWYRL_E_SATCHEL_NATIVE_416?.restore?.(copy);
  if(!restored?.ok)return restored||{ok:false,message:'Native checkpoint bridge unavailable.'};
  api().applyProgress(record.done);
  api().choose(record.step);
  refreshGhost();
  return {ok:true,message:'Restored checkpoint from step '+(record.step+1)+'. Native Undo is available. Use Save Project to keep the recovered model.'};
 }
 function clearHighlight(){
  if(highlight?.element)highlight.element.classList.remove('se415-show-target');
  highlight=null;
  try{se340XR?.ui?.highlightTutorialAction?.(null);}catch(_){}
 }
 function selectedAction(index){
  const refs=window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.references(index)||[];
  return refs.find(r=>r.vr)?.vr||null;
 }
 function showMe(index,vr=false){
  if(!active())return {ok:false,message:'Open the Apprentice Satchel lesson first.'};
  clearHighlight();
  const refs=window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.references(index)||[];
  if(vr){
   const s=se340XR,action=selectedAction(index);
   if(!s?.ui||!action)return {ok:false,message:'This is an inspector-only step. In VR use the Materials row in the quest window.'};
   const page=action==='create-box'?'create':action==='save-local'?'projects':action==='cameras'?'views':'tools';
   s.page=page;s.paletteVisible=true;s.helpVisible=false;
   se340SyncUI();s.ui.highlightTutorialAction?.(action);
   highlight={vr:true,index,action};
   return {ok:true,message:'The '+action+' button is highlighted on the existing VR tool panel. Point at it with your controller.'};
  }
  for(const ref of refs){
   const element=document.querySelector(ref.flat||'');
   if(element){
    element.classList.add('se415-show-target');
    element.scrollIntoView?.({behavior:'smooth',block:'nearest',inline:'nearest'});
    highlight={index,element,key:ref.key};
    return {ok:true,message:'Highlighted '+ref.name+' in the actual Model Studio controls. This is the real button/field—not the lesson preview.'};
   }
  }
  return {ok:false,message:'The required control is not visible. Select a mesh to reveal its inspector, then choose the matching button shown in the lesson.'};
 }
 function makeGhostPart(group,shape,position,rotation=[0,0,0]){
  const geometry=new THREE.BoxGeometry(...shape);
  const material=new THREE.MeshBasicMaterial({color:'#75edce',transparent:true,opacity:.21,
   depthWrite:false,depthTest:true,wireframe:true,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(geometry,material);
  mesh.position.set(...position);mesh.rotation.set(...rotation);
  mesh.userData.editorOnly=true;mesh.name='Tutorial ghost · visual guide only';
  mesh.raycast=()=>{};group.add(mesh);
 }
 function disposeGhost(){
  if(!ghost)return;
  ghost.removeFromParent();
  ghost.traverse(obj=>{if(obj.isMesh){obj.geometry?.dispose();obj.material?.dispose();}});
  ghost=null;ghostFor=-1;
 }
 function refreshGhost(){
  disposeGhost();
  const modelRoot=window.SWYRL_E_SATCHEL_NATIVE_416?.root?.();
  if(!ghostEnabled||!modelReady()||!modelRoot||typeof THREE==='undefined'||!modelRoot.isObject3D)return;
  const index=current()?.current||0,group=new THREE.Group();
  group.name='Tutorial ghost guides · not editable';group.userData.editorOnly=true;
  const add=(size,xyz,rot)=>makeGhostPart(group,size,xyz,rot);
  if(index===0)add([1.4,1.0,.65],[0,1.5,0]);
  if(index===1){
   add([1.4,.10,.65],[0,1.09,0]);
   add([1.4,.76,.07],[0,1.52,.30]);add([1.4,.76,.07],[0,1.52,-.30]);
   add([.07,.76,.54],[-.66,1.52,0]);add([.07,.76,.54],[.66,1.52,0]);
  }
  if(index===2)add([1.35,.07,.47],[0,1.99,.22],[-.28,0,0]);
  if(index===3){
   for(let i=0;i<5;i++){const t=i/4,x=(t-.5)*1.4,y=2.12+Math.sin(t*Math.PI)*.54;
    add([.09,.34,.08],[x,y,0],[0,0,(t-.5)*.85]);}
  }
  if(index===4){add([.2,.16,.07],[0,1.83,.36]);add([.07,.11,.07],[.31,1.69,.35]);}
  if(!group.children.length){group.clear();return;}
  ghost=group;ghostFor=index;modelRoot.add(group);
 }
 function renderFlat(panel,index){
  if(!panel||!active())return;
  flatPanel=panel;
  let host=panel.querySelector('#se415Coach');
  if(!host){
   host=document.createElement('section');host.id='se415Coach';host.setAttribute('aria-label','Interactive satchel tutor');
   const title=document.createElement('strong');title.textContent='INTERACTIVE COACH';host.append(title);
   const row=document.createElement('div');row.className='se415-coach-actions';host.append(row);
   for(const [id,label,handler] of [
    ['show','Show Me',()=>{const result=showMe(current()?.current||0,false);note(result.message);}],
    ['ghost','Ghost guide',()=>{ghostEnabled=!ghostEnabled;refreshGhost();renderFlat(panel,current()?.current||0);
     note(ghostEnabled?'Transparent target geometry shown—build the real mesh yourself.':'Ghost guide hidden.');}],
    ['checkpoint','Save checkpoint',()=>note(saveCheckpoint().message)],
    ['restore','Restore checkpoint',()=>{
      const result=restoreCheckpoint();if(result.requiresConfirmation){
       if(!window.confirm(result.message))return;
       const final=restoreCheckpoint({confirmed:true});note(final.message);
      }else note(result.message);
    }]
   ]){
    const b=document.createElement('button');b.type='button';b.id='se415-'+id;b.textContent=label;
    b.addEventListener('click',handler);row.append(b);
   }
   const small=document.createElement('p');small.className='se415-help';
   small.textContent='Show Me highlights the native tool. Ghosts are non-editable examples. Checkpoints stay on this device; use Save to Account to sync the project and completed objectives.';
   host.append(small);
   const anchor=panel.querySelector('#se413Examples')||panel.querySelector('#se412Note');
   anchor?.before(host);
  }
  $('#se415-ghost',host)?.setAttribute('aria-pressed',String(ghostEnabled));
  const last=snapshots().at(-1);
  $('#se415-restore',host).disabled=!last;
  if(ghostEnabled&&ghostFor!==index)refreshGhost();
  if(highlight&&!highlight.vr&&highlight.index!==index)clearHighlight();
 }
 function onRenderParts(){
  if(ghostEnabled&&active())refreshGhost();else if(ghost)disposeGhost();
 }
 function inspectAPI(){return {active:active(),ghost:ghostEnabled,ghostMeshes:ghost?.children.length||0,
  highlighted:highlight?.key||highlight?.action||null,checkpoints:snapshots().length,
  cloudProgress:!!snapshotMeta(),progress:current()?.progress||0};}
 const baseSnapshot=se175Snapshot;
 se175Snapshot=function(...args){const row=baseSnapshot.apply(this,args);
  const meta=snapshotMeta();if(meta&&row?.data?.project)row.data.project.se415TutorialState=meta;
  return row;};
 const baseProjectData=projectData;
 projectData=function(...args){const data=baseProjectData.apply(this,args);
  const meta=snapshotMeta();if(meta&&data?.project)data.project.se415TutorialState=meta;
  return data;};
 window.SWYRL_E_SATCHEL_ACADEMY_416=Object.freeze({
  verify:inspect,renderFlat,progressUpdate:syncProgress,saveCheckpoint,restoreCheckpoint,
  showMe,setGhost(value){ghostEnabled=!!value;refreshGhost();return ghostEnabled;},
  ghost:()=>ghostEnabled,refreshGhost,onNativeRender:onRenderParts,clearHighlight,snapshotMeta,inspect:inspectAPI
 });
})();
 /* SE416_SATCHEL_ACADEMY_END */