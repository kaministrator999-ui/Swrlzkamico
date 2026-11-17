/* §E v11.489 — native weighted cloth rig for user-uploaded single-mesh models.
   Runs in Model Atelier's existing closure. Explicit weights are bound to the
   original topology, while all unrigged and hand-rig projects remain unchanged. */
function se489ValidateClothRig(rig){
 if(!rig||rig.schema!=='swyrl-cloth-skin-v1'||rig.algorithm!=='linear-blend-4'||
    !Array.isArray(rig.bones)||rig.bones.length<2||rig.bones.length>32||
    !Number.isFinite(rig.duration)||rig.duration<.2||rig.duration>30||
    typeof rig.loop!=='boolean')return false;
 const ids=new Set();
 for(const b of rig.bones){
  if(!b||typeof b.id!=='string'||!/^[a-z_]{2,32}$/.test(b.id)||
     ids.has(b.id)||typeof b.label!=='string'||b.label.length>55||
     !Array.isArray(b.rest)||b.rest.length!==3||
     !b.rest.every(x=>Number.isFinite(x)&&Math.abs(x)<20)||
     (b.parent!==null&&!ids.has(b.parent)))return false;
  ids.add(b.id);
 }
 const poseValid=p=>p&&typeof p==='object'&&!Array.isArray(p)&&
  Object.keys(p).length<=rig.bones.length&&Object.entries(p).every(([id,v])=>
   ids.has(id)&&Array.isArray(v)&&v.length===3&&v.every(x=>Number.isFinite(x)&&Math.abs(x)<=2.8));
 const timelineValid=(timeline,duration)=>Array.isArray(timeline)&&timeline.length<=32&&
  timeline.every((f,i)=>f&&Number.isFinite(f.time)&&f.time>=0&&
   f.time<=duration&&(i===0||f.time>timeline[i-1].time)&&poseValid(f.pose));
 if(!poseValid(rig.pose)||!timelineValid(rig.timeline,rig.duration))return false;
 if(!Array.isArray(rig.clips)||!rig.clips.length||rig.clips.length>12)return false;
 const names=new Set();
 for(const c of rig.clips){
  if(!c||typeof c.name!=='string'||!c.name.trim()||c.name.length>80||
     names.has(c.name)||!Number.isFinite(c.duration)||c.duration<.2||c.duration>30||
     typeof c.loop!=='boolean'||!timelineValid(c.timeline,c.duration))return false;
  names.add(c.name);
 }
 return names.has(rig.activeClip);
}
function se489ExplicitInfluences(part,index,rig){
 const raw=part?.skinning,vertices=part?.topologyMesh?.positions?.length/3;
 if(raw?.schema!=='swyrl-explicit-skin-v1'||!Number.isInteger(vertices)||
    raw.indices?.length!==vertices*4||raw.weights?.length!==vertices*4||
    index<0||index>=vertices)return {indices:[0,0,0,0],weights:[1,0,0,0]};
 const at=index*4,ii=[],ww=[];let total=0;
 for(let n=0;n<4;n++){
  const j=raw.indices[at+n],w=raw.weights[at+n];
  if(!Number.isInteger(j)||j<0||j>=rig.bones.length||!Number.isFinite(w)||w<0)
   return {indices:[0,0,0,0],weights:[1,0,0,0]};
  ii.push(j);ww.push(w);total+=w;
 }
 if(total<.0001)return {indices:[0,0,0,0],weights:[1,0,0,0]};
 return {indices:ii,weights:ww.map(w=>w/total)};
}
function se489ClothRigClip(rig,name){
 const clip=rig.clips?.find(c=>c.name===name);
 if(!clip||!se489ValidateClothRig(rig))return false;
 se220Playing=false;rig.activeClip=clip.name;rig.duration=clip.duration;
 rig.loop=clip.loop;rig.timeline=structuredClone(clip.timeline);
 rig.pose=structuredClone(clip.timeline[0]?.pose||{});
 se220Time=0;se220RigPose(rig.pose);
 se220RigRefresh();
 return true;
}
function se489RigInstallUI(rigUI){
 if(rigUI.querySelector('#se489ClothRigClips'))return;
 const label=document.createElement('label');label.id='se489ClothRigClips';label.hidden=true;
 label.textContent='Hat animation · ';
 const select=document.createElement('select');select.id='se489ClothClip';
 select.setAttribute('aria-label','Select cloth animation clip');
 select.addEventListener('change',()=>{
  const r=se220Rig();
  if(r?.schema==='swyrl-cloth-skin-v1'&&se489ClothRigClip(r,select.value))
   status('Loaded '+select.value+'. Play or edit its skeletal keys.');
 });
 label.append(select);
 rigUI.querySelector('.atelier-rig-body')?.prepend(label);
 const oldButtons=[...rigUI.querySelectorAll('#modelAtelierRigOpen,#modelAtelierRigFist,#modelAtelierRigPoint,#modelAtelierRigPinch')];
 for(const b of oldButtons)b.dataset.se489HandPreset='1';
}
function se489ClothRigRefresh(){
 const rig=se220Rig(),active=rig?.schema==='swyrl-cloth-skin-v1'&&se489ValidateClothRig(rig);
 const label=document.getElementById('se489ClothRigClips'),select=document.getElementById('se489ClothClip');
 if(label)label.hidden=!active;
 for(const b of document.querySelectorAll('#modelAtelierRigStudio [data-se489-hand-preset]'))
  b.hidden=!!active;
 if(!active||!select)return;
 if(select.options.length!==rig.clips.length||
    rig.clips.some((c,i)=>select.options[i]?.value!==c.name)){
  select.replaceChildren(...rig.clips.map(c=>{
   const o=document.createElement('option');o.value=c.name;o.textContent=c.name;return o;
  }));
 }
 select.value=rig.activeClip;
 const hint=document.querySelector('#modelAtelierRigStudio .atelier-rig-body small:last-child');
 if(hint)hint.textContent='Weighted cloth rig · '+rig.bones.length+
   ' bones. Select a clip, pose joints, save keys, then Save Project.';
}
function se489ClothRigTouched(){
 const rig=se220Rig();
 if(rig?.schema!=='swyrl-cloth-skin-v1'||!se489ValidateClothRig(rig))return;
 const active=rig.clips.find(c=>c.name===rig.activeClip);
 if(active){active.duration=rig.duration;active.loop=rig.loop;
  active.timeline=structuredClone(rig.timeline);}
}
