/* §E v11.489 — general purpose single-cloth skinning and editable clip selector.
   Reuses v11.220 THREE.SkinnedMesh / native Rig · Pose · Animate UI.
   No replacement of neutral mesh, UV positions, part IDs or material. */
const se489PriorRigValidate=se220RigValidate;
function se489ClothRigValidate(r){
 if(!r||r.schema!=='swyrl-cloth-skin-v1'||r.algorithm!=='linear-blend-4')return false;
 if(!Array.isArray(r.bones)||r.bones.length<3||r.bones.length>48||
    !Array.isArray(r.envelopes)||r.envelopes.length>64||!r.envelopes.length)return false;
 const ids=new Set();
 for(const b of r.bones){
  if(!b||typeof b.id!=='string'||!/^[a-z_]{2,32}$/.test(b.id)||ids.has(b.id)||
    typeof b.label!=='string'||b.label.length>72||
    !Array.isArray(b.rest)||b.rest.length!==3||
    !b.rest.every(n=>Number.isFinite(n)&&Math.abs(n)<20)||
    (b.parent!==null&&!ids.has(b.parent)))return false;
  ids.add(b.id);
 }
 if(!ids.has('root')||r.bones[0].id!=='root'||
    typeof r.targetPartId!=='string'||r.targetPartId.length>100)return false;
 for(const a of r.envelopes)if(!a||!ids.has(a.bone)||
   !Array.isArray(a.center)||!Array.isArray(a.radii)||
   a.center.length!==3||a.radii.length!==3||
   !a.center.every(n=>Number.isFinite(n)&&Math.abs(n)<20)||
   !a.radii.every(n=>Number.isFinite(n)&&n>.005&&n<=10)||
   !Number.isFinite(a.strength)||a.strength<0||a.strength>1)return false;
 const validPose=p=>p&&typeof p==='object'&&!Array.isArray(p)&&Object.keys(p).length<=ids.size&&
  Object.entries(p).every(([id,rotation])=>ids.has(id)&&Array.isArray(rotation)&&
   rotation.length===3&&rotation.every(n=>Number.isFinite(n)&&Math.abs(n)<=2.8));
 const validTimeline=(timeline,duration)=>Array.isArray(timeline)&&timeline.length>=2&&
  timeline.length<=32&&timeline.every((key,i)=>key&&Number.isFinite(key.time)&&
   key.time>=0&&key.time<=duration&&validPose(key.pose)&&
   (i===0||key.time>timeline[i-1].time))&&
  timeline[0].time===0&&Math.abs(timeline.at(-1).time-duration)<.0001;
 if(!Number.isFinite(r.duration)||r.duration<.3||r.duration>30||
   typeof r.loop!=='boolean'||!validPose(r.pose)||
   !validTimeline(r.timeline,r.duration))return false;
 if(!r.clips||typeof r.clips!=='object'||Array.isArray(r.clips)||
  Object.keys(r.clips).length<1||Object.keys(r.clips).length>8||
  !Object.hasOwn(r.clips,r.activeClip))return false;
 for(const [name,c] of Object.entries(r.clips)){
  if(!/^[a-z][a-z0-9_-]{1,29}$/.test(name)||
   typeof c?.label!=='string'||c.label.length>65||
   !Number.isFinite(c.duration)||c.duration<.3||c.duration>30||
   typeof c.loop!=='boolean'||!validTimeline(c.timeline,c.duration))return false;
 }
 return true;
}
se220RigValidate=function(rig){
 return rig?.schema==='swyrl-cloth-skin-v1'
   ?se489ClothRigValidate(rig):se489PriorRigValidate(rig);
};
function se489ClothSkinWeights(pt,rig){
 const source=[['root',1]],idIndex=Object.fromEntries(rig.bones.map((b,i)=>[b.id,i]));
 const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);};
 for(const e of rig.envelopes){
  const d=Math.hypot(...pt.map((n,i)=>(n-e.center[i])/e.radii[i]));
  const w=(1-smooth(d))*e.strength;
  if(w<1e-6)continue;
  for(const entry of source)entry[1]*=1-w;
  const prior=source.find(entry=>entry[0]===e.bone);
  if(prior)prior[1]+=w;else source.push([e.bone,w]);
 }
 const four=source.filter(x=>x[1]>1e-6).sort((a,b)=>b[1]-a[1]).slice(0,4);
 const total=four.reduce((sum,x)=>sum+x[1],0)||1;
 const indices=four.map(x=>idIndex[x[0]]),weights=four.map(x=>x[1]/total);
 while(indices.length<4){indices.push(0);weights.push(0);}
 return {indices,weights};
}
const se489PriorRigWeights=se220RigWeights;
se220RigWeights=function(point,rig){
 return rig?.schema==='swyrl-cloth-skin-v1'
  ?se489ClothSkinWeights(point,rig):se489PriorRigWeights(point,rig);
};
function se489IsClothRig(){return se220Rig()?.schema==='swyrl-cloth-skin-v1'&&se220RigAvailable();}
function se489SaveCurrentClip(){
 if(!se489IsClothRig())return;
 const r=se220Rig(),clip=r.clips[r.activeClip];
 if(!clip)return;
 clip.duration=r.duration;clip.loop=r.loop;
 clip.timeline=structuredClone(r.timeline);
}
function se489SelectClip(name){
 const rig=se220Rig();
 if(!se489IsClothRig()||!Object.hasOwn(rig.clips,name))return;
 se489SaveCurrentClip();se220Playing=false;
 rig.activeClip=name;
 const clip=rig.clips[name];
 rig.duration=clip.duration;rig.loop=clip.loop;rig.timeline=structuredClone(clip.timeline);
 rig.pose=structuredClone(clip.timeline[0].pose);
 se220Time=0;se220RigPose(rig.pose);se220RigRefresh();
 se220RigTouched('Selected '+clip.label+' animation. Edit bones or timeline; save your project when ready.');
}
const se489PriorRigTouched=se220RigTouched;
se220RigTouched=function(...args){
 if(se489IsClothRig())se489SaveCurrentClip();
 return se489PriorRigTouched.apply(this,args);
};
const se489PriorRigInstall=se220RigControlsInstall;
se220RigControlsInstall=function(...args){
 const result=se489PriorRigInstall.apply(this,args);
 const host=se220R('Studio'),body=host?.querySelector('.atelier-rig-body');
 if(!body||host.querySelector('[data-se489-clip]'))return result;
 const section=document.createElement('div');
 section.dataset.se489Clip='1';section.className='se489-clip-selector';
 const label=document.createElement('label');label.textContent='Animation clip';
 const select=document.createElement('select');select.id='se489ClothClip';
 select.setAttribute('aria-label','Cloth animation clip');
 select.addEventListener('change',()=>se489SelectClip(select.value));
 label.append(select);section.append(label);
 const hint=document.createElement('small');
 hint.textContent='Weighted cloth rig: face, brows, speaking mouth, brim and flexible tip. Keyframes are editable using the controls below.';
 section.append(hint);
 body.insertBefore(section,body.querySelector('.atelier-rig-axes'));
 return result;
};
const se489PriorRigRefresh=se220RigRefresh;
se220RigRefresh=function(...args){
 const result=se489PriorRigRefresh.apply(this,args);
 const host=se220R('Studio'),panel=host?.querySelector('[data-se489-clip]');
 if(!panel)return result;
 const cloth=se489IsClothRig();panel.hidden=!cloth;
 const presets=host.querySelector('.atelier-rig-actions');
 if(presets)presets.hidden=cloth;
 const helper=host.querySelector('.atelier-rig-body>small:last-child');
 if(helper)helper.textContent=cloth?
  '11 hierarchical cloth bones · computed four-influence skinning · source mesh and UVs untouched.':
  '17 hierarchical bones · four-influence mesh skinning. Save Project or JSON to keep poses and clip.';
 if(!cloth)return result;
 const select=host.querySelector('#se489ClothClip'),rig=se220Rig();
 const old=select.value;
 select.replaceChildren(...Object.entries(rig.clips).map(([name,clip])=>{
  const el=document.createElement('option');el.value=name;el.textContent=clip.label;return el;
 }));
 select.value=Object.hasOwn(rig.clips,rig.activeClip)?rig.activeClip:old;
 return result;
};
window.SWYRL_ENGINE_CLOTH_RIG_489=Object.freeze({
 validate:se489ClothRigValidate,weights:se489ClothSkinWeights,
 selectClip:se489SelectClip,status:()=>({active:se489IsClothRig(),
  clip:se220Rig()?.activeClip||null,bones:se220Rig()?.bones?.length||0,
  keyframes:se220Rig()?.timeline?.length||0})
});
