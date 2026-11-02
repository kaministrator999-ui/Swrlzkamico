// §E v11.226 Material & Texture Studio: bounded, project-native authoring.
// Material definitions/assignments are saved in project metadata; textures and
// 3D previews are derived GPU resources, never serialized into the scene actors.
const SE225_M_SCHEMA='swyrl-material-studio-v1',SE225_M_CAP=12,SE225_STROKES=160,SE225_POINTS=220;
const SE225_PATTERNS=['solid','checker','stripes','noise','brick','wood','dots','image'];
const SE225_M_PRESETS=Object.freeze({
 metal:['Brushed Steel','#a2bdd1','#69798b','stripes',.28,.88,'#000000'],
 gold:['Golden Armor','#e5ae41','#8e5521','noise',.22,.87,'#000000'],
 wood:['Oak Wood','#946038','#50311b','wood',.79,0,'#000000'],
 stone:['Weathered Stone','#89929c','#58636d','noise',.94,0,'#000000'],
 brick:['Red Masonry','#a44d43','#513d3b','brick',.92,0,'#000000'],
 fabric:['Woven Fabric','#477aa5','#234d75','checker',.94,0,'#000000'],
 leather:['Tanned Leather','#925a38','#503523','noise',.82,0,'#000000'],
 magic:['Arcane Glow','#6055c7','#cf9cff','dots',.45,.22,'#5841ff'],
 glass:['Icy Glass','#98ddeb','#cceeff','solid',.09,.04,'#000000'],
 ceramic:['Glazed Ceramic','#f2f2e9','#c9c8b6','solid',.19,.04,'#000000']
});
const se225Mat={selected:null,target:null,source:null,signature:'',actors:[],applied:new Map(),
 textures:new Map(),pendingImages:new Map(),preview:null,lastUpdate:0,paint:null,ui:null};
const se225MHex=v=>typeof v==='string'&&/^#[0-9a-fA-F]{6}$/.test(v);
const se225MClamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function se225MaterialDefault(kind='metal'){
 const p=SE225_M_PRESETS[kind]||SE225_M_PRESETS.metal;
 return {id:uid(),name:p[0],baseColor:p[1],accentColor:p[2],
  pattern:p[3],roughness:p[4],metalness:p[5],emissive:p[6],
  glow:kind==='magic'?1.3:0,opacity:kind==='glass'?.72:1,
  scale:kind==='metal'?12:8,seed:7,tiling:1,strokes:[],imageData:''};
}
function se225ValidateMaterial(value){
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('Material must be an object.');
 // Imported and persisted material data must be complete. Never invent IDs
 // for malformed source records or silently supply missing PBR properties.
 const v=value;
 if(typeof v.id!=='string'||!/^[a-zA-Z0-9_-]{2,70}$/.test(v.id))throw Error('Invalid material ID.');
 if(typeof v.name!=='string'||!v.name.trim()||v.name.length>65)throw Error('Material name must be 1–65 characters.');
 if(!SE225_PATTERNS.includes(v.pattern))throw Error('Unknown texture pattern.');
 for(const key of ['baseColor','accentColor','emissive'])if(!se225MHex(v[key]))throw Error('Invalid '+key+' color.');
 for(const [key,a,b] of [['roughness',0,1],['metalness',0,1],['glow',0,3],
  ['opacity',.1,1],['scale',1,24],['tiling',.25,8],['seed',1,9999]]){
  if(typeof v[key]!=='number'||!Number.isFinite(v[key])||v[key]<a||v[key]>b)throw Error(key+' outside '+a+'–'+b);
 }
 if(!Array.isArray(v.strokes)||v.strokes.length>SE225_STROKES)throw Error('Too many paint strokes.');
 const strokes=v.strokes.map(s=>{
  if(!s||!se225MHex(s.color)||typeof s.width!=='number'||!Number.isFinite(s.width)||s.width<.003||s.width>.25||
    !Array.isArray(s.points)||s.points.length<1||s.points.length>SE225_POINTS)throw Error('Invalid painted stroke.');
  const points=s.points.map(pt=>{
   if(!Array.isArray(pt)||pt.length!==2||!pt.every(x=>typeof x==='number'&&Number.isFinite(x)&&x>=0&&x<=1))throw Error('Invalid paint coordinates.');
   return [pt[0],pt[1]];
  });
  return {color:s.color.toLowerCase(),width:s.width,points};
 });
 if(typeof v.imageData!=='string'||v.imageData.length>360000||
  (v.imageData&&!/^data:image\/png;base64,[a-zA-Z0-9+/=]+$/.test(v.imageData)))
  throw Error('Imported texture must be a bounded PNG image.');
 return {id:v.id,name:v.name,pattern:v.pattern,
  baseColor:v.baseColor.toLowerCase(),accentColor:v.accentColor.toLowerCase(),
  roughness:v.roughness,metalness:v.metalness,emissive:v.emissive.toLowerCase(),
  glow:v.glow,opacity:v.opacity,scale:v.scale,tiling:v.tiling,seed:Math.round(v.seed),
  strokes,imageData:v.imageData};
}
function se225ValidateLibrary(source){
 if(!source||source.schema!==SE225_M_SCHEMA||!Array.isArray(source.materials)||
  source.materials.length>SE225_M_CAP||!Array.isArray(source.assignments)||source.assignments.length>256)
  throw Error('Expected Material Studio v1 JSON (up to 12 materials).');
 const materials=source.materials.map(se225ValidateMaterial);
 if(new Set(materials.map(m=>m.id)).size!==materials.length)throw Error('Duplicate material IDs.');
 const allowed=new Set(materials.map(m=>m.id)),ids=new Set();
 const assignments=source.assignments.map(a=>{
  if(!a||typeof a.actorId!=='string'||!/^[a-zA-Z0-9_-]{1,90}$/.test(a.actorId)||
     !allowed.has(a.materialId)||ids.has(a.actorId))throw Error('Invalid actor assignment.');
  ids.add(a.actorId);return {actorId:a.actorId,materialId:a.materialId};
 });
 return {schema:SE225_M_SCHEMA,materials,assignments};
}
const se225Verified=new WeakSet(),se225Empty=Object.freeze({schema:SE225_M_SCHEMA,materials:[],assignments:[]});
function se225MaterialData(create=false){
 if(!currentProject||typeof currentProject!=='object')return null;
 if(!currentProject.materialStudio){
  if(!create)return se225Empty;
  currentProject.materialStudio={schema:SE225_M_SCHEMA,materials:[],assignments:[]};
 }
 const data=currentProject.materialStudio;
 if(!data||typeof data!=='object')return null;
 if(!se225Verified.has(data)){
  try{se225ValidateLibrary(data);se225Verified.add(data);}catch{return null;}
 }
 return data;
}
function se225MaterialList(){return (se225MaterialData()?.materials||[]).map(x=>structuredClone(x));}
function se225MaterialGet(id){return se225MaterialData()?.materials.find(x=>x.id===id)||null;}
function se225MaterialChange(label,fn,repair=false){
 if(playing||simulating){toast('Stop Play or Simulate before editing materials.');return false;}
 const source=se225MaterialData();
 if(!source&&!repair){toast('Invalid material data. Import a valid library to repair.');return false;}
 try{
  const draft=structuredClone(source||se225Empty),result=fn(draft);
  const validated=se225ValidateLibrary(draft);
  beginTransaction(label);currentProject.materialStudio=validated;commitTransaction(label);
  se225Mat.signature='';se225MaterialUIRefresh();
  return result;
 }catch(error){toast('Material rejected: '+String(error?.message||error).slice(0,100));return false;}
}
function se225MaterialCreate(kind='metal'){
 const created=se225MaterialChange('Create material',lib=>{
  if(lib.materials.length>=SE225_M_CAP)throw Error('12 material maximum.');
  const value=se225MaterialDefault(kind);
  lib.materials.push(value);return structuredClone(value);
 });
 if(created){se225Mat.selected=created.id;se225MaterialUIRefresh();}
 return created;
}
function se225MaterialEdit(id,changes){
 return se225MaterialChange('Edit material',lib=>{
  const i=lib.materials.findIndex(x=>x.id===id);
  if(i<0)throw Error('Material no longer exists.');
  const value=se225ValidateMaterial({...lib.materials[i],...changes,id});
  lib.materials[i]=value;return structuredClone(value);
 });
}
function se225MaterialDuplicate(id){
 const source=se225MaterialGet(id);if(!source)return false;
 const next=se225MaterialChange('Duplicate material',lib=>{
  if(lib.materials.length>=SE225_M_CAP)throw Error('12 material maximum.');
  const copy=se225ValidateMaterial({...structuredClone(source),id:uid(),name:(source.name+' copy').slice(0,65)});
  lib.materials.push(copy);return structuredClone(copy);
 });
 if(next){se225Mat.selected=next.id;se225MaterialUIRefresh();}
 return next;
}
function se225MaterialDelete(id){
 const ok=se225MaterialChange('Delete material',lib=>{
  lib.materials=lib.materials.filter(x=>x.id!==id);
  lib.assignments=lib.assignments.filter(x=>x.materialId!==id);
  return true;
 });
 if(ok){se225Mat.selected=se225MaterialData().materials[0]?.id||null;se225MaterialUIRefresh();}
 return ok;
}
function se225MaterialAssign(actorId,materialId){
 if(!actors.some(a=>a.userData?.id===actorId)||!se225MaterialGet(materialId))return false;
 return se225MaterialChange('Assign material to actor',lib=>{
  lib.assignments=lib.assignments.filter(x=>x.actorId!==actorId);
  lib.assignments.push({actorId,materialId});return true;
 });
}
function se225MaterialUnassign(actorId){
 return se225MaterialChange('Restore original actor material',lib=>{
  lib.assignments=lib.assignments.filter(x=>x.actorId!==actorId);return true;
 });
}
function se225MaterialImport(value){
 let model;
 try{model=se225ValidateLibrary(value);}catch(error){toast('Material import rejected: '+error.message);return false;}
 // Material libraries are portable; actor IDs belong to another project.
 return se225MaterialChange('Import material library',draft=>{
  draft.materials=model.materials;draft.assignments=[];return true;
 },true);
}
function se225MRandom(seed){let value=seed|0;return ()=>{value=(Math.imul(value,1664525)+1013904223)|0;return (value>>>0)/4294967296;};}
function se225MaterialCanvas(def){
 const canvas=document.createElement('canvas');canvas.width=256;canvas.height=256;
 const ctx=canvas.getContext('2d',{willReadFrequently:false}),n=256;
 ctx.fillStyle=def.baseColor;ctx.fillRect(0,0,n,n);
 const count=def.scale,rnd=se225MRandom(def.seed);
 ctx.fillStyle=def.accentColor;
 if(def.pattern==='checker'){
  const d=n/count;
  for(let y=0;y<count;y++)for(let x=0;x<count;x++)if((x+y)%2===0)ctx.fillRect(x*d,y*d,d,d);
 }else if(def.pattern==='stripes'){
  const d=n/count;
  for(let i=0;i<count;i+=2)ctx.fillRect(i*d,0,d,n);
 }else if(def.pattern==='brick'){
  const rows=Math.max(2,Math.round(count*.62)),h=n/rows,w=n/Math.max(2,Math.round(count*.6));
  ctx.lineWidth=Math.max(1,n/(count*35));ctx.strokeStyle=def.accentColor;
  for(let y=0;y<=rows;y++){ctx.beginPath();ctx.moveTo(0,y*h);ctx.lineTo(n,y*h);ctx.stroke();}
  for(let y=0;y<rows;y++)for(let x=-1;x<=n/w+1;x++){
   const px=(x+(y%2)*.5)*w;
   ctx.beginPath();ctx.moveTo(px,y*h);ctx.lineTo(px,(y+1)*h);ctx.stroke();
  }
 }else if(def.pattern==='noise'){
  ctx.globalAlpha=.08;
  for(let i=0;i<5500;i++){
   ctx.fillStyle=rnd()>.44?def.accentColor:def.baseColor;
   const radius=.4+rnd()*3.5;ctx.fillRect(rnd()*n,rnd()*n,radius,radius);
  }
  ctx.globalAlpha=1;
 }else if(def.pattern==='wood'){
  ctx.lineWidth=1.1;
  for(let j=0;j<Math.round(count*4);j++){
   const x=(j/Math.max(1,count*4))*n+(rnd()-.5)*8;
   ctx.globalAlpha=.2+rnd()*.45;
   ctx.strokeStyle=def.accentColor;ctx.beginPath();ctx.moveTo(x,0);
   for(let y=0;y<=n;y+=8)ctx.lineTo(x+Math.sin(y*.05+j*2)*3,y);
   ctx.stroke();
  }
  ctx.globalAlpha=1;
 }else if(def.pattern==='dots'){
  for(let j=0;j<count*count;j++){
   const col=j%count,row=Math.floor(j/count),step=n/count;
   ctx.beginPath();ctx.arc((col+.5)*step,(row+.5)*step,Math.max(1,step*.22),0,Math.PI*2);ctx.fill();
  }
 }
 const paint=()=>{
  for(const stroke of def.strokes){
   ctx.beginPath();ctx.strokeStyle=stroke.color;ctx.fillStyle=stroke.color;
   ctx.lineWidth=stroke.width*n;ctx.lineCap='round';ctx.lineJoin='round';
   for(let i=0;i<stroke.points.length;i++){
    const [u,v]=stroke.points[i];
    if(i===0)ctx.moveTo(u*n,v*n);else ctx.lineTo(u*n,v*n);
   }
   if(stroke.points.length===1){const [u,v]=stroke.points[0];ctx.beginPath();ctx.arc(u*n,v*n,ctx.lineWidth*.5,0,Math.PI*2);ctx.fill();}
   else ctx.stroke();
  }
 };
 if(def.pattern==='image'&&def.imageData){
  const img=new Image();
  // Imported image is the base layer; paint goes on top after decoding.
  // An older in-flight load must never change the newer selected texture.
  img.onload=()=>{
   if(se225Mat.textures.get(def.id)?.canvas!==canvas)return;
   ctx.drawImage(img,0,0,n,n);paint();se225MaterialInvalidateCanvas(def.id);
  };
  img.onerror=()=>{console.warn('§E texture PNG could not be decoded');};
  img.src=def.imageData;
 }else paint();
 return canvas;
}
function se225MaterialInvalidateCanvas(id){
 const rec=se225Mat.textures.get(id);
 if(rec){rec.texture.needsUpdate=true;}
 if(se225Mat.selected===id)se225MaterialUIPreview();
}
function se225MaterialTexture(def){
 const fingerprint=JSON.stringify(def);
 const previous=se225Mat.textures.get(def.id);
 if(previous?.fingerprint===fingerprint)return previous;
 if(previous){previous.texture.dispose();se225Mat.textures.delete(def.id);}
 const canvas=se225MaterialCanvas(def);
 const texture=new THREE.CanvasTexture(canvas);
 texture.colorSpace=THREE.SRGBColorSpace;texture.wrapS=THREE.RepeatWrapping;texture.wrapT=THREE.RepeatWrapping;
 texture.repeat.set(def.tiling,def.tiling);
 const record={canvas,texture,fingerprint};se225Mat.textures.set(def.id,record);return record;
}
function se225MakeSurface(def,original){
 const source=original?.isMeshStandardMaterial||original?.isMeshPhysicalMaterial ? original:null;
 const material=source?source.clone():new THREE.MeshStandardMaterial({side:original?.side??THREE.FrontSide});
 // The bitmap owns its base color; prevent the shader from tinting it twice.
 material.color.set('#ffffff');material.roughness=def.roughness;material.metalness=def.metalness;
 material.emissive.set(def.emissive);material.emissiveIntensity=def.glow;
 material.opacity=def.opacity;material.transparent=def.opacity<1;
 material.map=se225MaterialTexture(def).texture;material.needsUpdate=true;
 return material;
}
function se225RestoreMaterials(){
 for(const [mesh,old] of se225Mat.applied){
  if(mesh.material===old.applied){mesh.material=old.base;}
  else if(Array.isArray(mesh.material)&&mesh.material.length===old.applied.length&&
     mesh.material.every((m,i)=>m===old.applied[i]))mesh.material=old.base;
  const applied=Array.isArray(old.applied)?old.applied:[old.applied];
  for(const m of applied)m.dispose();
 }
 se225Mat.applied.clear();
 if(se225Mat.preview){se225Mat.preview.geometry.dispose();se225Mat.preview.material.dispose();
  se225Mat.preview.removeFromParent();se225Mat.preview=null;}
 for(const rec of se225Mat.textures.values())rec.texture.dispose();
 se225Mat.textures.clear();
}
function se225MaterialActorsChanged(){
 const ids=actors||[];
 if(se225Mat.actors.length!==ids.length)return true;
 return ids.some((a,i)=>a!==se225Mat.actors[i]);
}
function se225MaterialSync(force=false){
 const data=se225MaterialData();
 // Authoring edits replace this metadata object atomically. Compare its
 // identity rather than repeatedly JSON.stringify large imported PNG data on
 // each Quest/Android frame (the actor list is checked separately).
 const signature=data;
 const changed=force||currentProject!==se225Mat.source||signature!==se225Mat.signature||se225MaterialActorsChanged();
 if(!changed)return;
 se225RestoreMaterials();se225Mat.source=currentProject;se225Mat.signature=signature;
 se225Mat.actors=[...actors];
 if(!data)return;
 const byId=new Map(data.materials.map(m=>[m.id,m]));
 for(const a of data.assignments){
  const actor=actors.find(x=>x.userData?.id===a.actorId),def=byId.get(a.materialId);
  if(!actor||!def)continue;
  actor.traverse(mesh=>{
   if(!mesh.isMesh||mesh.userData?.editorOnly||mesh.userData?.atelierHelper||!mesh.material)return;
   const base=mesh.material;
   const applied=Array.isArray(base)?base.map(m=>se225MakeSurface(def,m)):se225MakeSurface(def,base);
   se225Mat.applied.set(mesh,{base,applied});mesh.material=applied;
  });
 }
}
function se225MaterialPreviewSphere(){
 const selected=se225MaterialGet(se225Mat.selected);if(!selected||!scene||!camera)return;
 if(!se225Mat.preview){
  const geometry=new THREE.SphereGeometry(.72,28,20);
  const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0xffffff,roughness:.4}));
  mesh.name='Material Studio · sample sphere';mesh.userData.editorOnly=true;
  mesh.frustumCulled=false;scene.add(mesh);se225Mat.preview=mesh;
 }
 const old=se225Mat.preview.material;
 se225Mat.preview.material=se225MakeSurface(selected,old);old.dispose();
}
function se225MaterialFrame(dt,t){
 if(!scene||!currentProject)return;
 const now=performance.now();
 if(now-se225Mat.lastUpdate>=240){
  se225Mat.lastUpdate=now;se225MaterialSync();
 }
 const active=window.SWYRL_ENGINE_STUDIOS?.active?.()==='materials';
 if(!active){
  if(se225Mat.preview){se225Mat.preview.geometry.dispose();se225Mat.preview.material.dispose();
   se225Mat.preview.removeFromParent();se225Mat.preview=null;}
  return;
 }
 if(!se225Mat.preview||se225Mat.preview.userData.se225MaterialId!==se225Mat.selected){
  if(se225Mat.preview){
   se225Mat.preview.geometry.dispose();se225Mat.preview.material.dispose();
   se225Mat.preview.removeFromParent();se225Mat.preview=null;
  }
  se225MaterialPreviewSphere();
  if(se225Mat.preview)se225Mat.preview.userData.se225MaterialId=se225Mat.selected;
 }
 if(se225Mat.preview){
  camera.updateMatrixWorld(true);
  const world=camera.localToWorld(new THREE.Vector3(1.6,-.05,-3.6));
  se225Mat.preview.position.copy(world);
  se225Mat.preview.rotation.y+=Math.min(dt,.05)*.35;
 }
}
function se225MaterialExport(){
 const model=se225MaterialData();if(!model)return false;
 return {schema:SE225_M_SCHEMA,materials:structuredClone(model.materials),assignments:[]};
}
window.SWYRL_ENGINE_MATERIALS=Object.freeze({
 schema:SE225_M_SCHEMA,presets:()=>Object.keys(SE225_M_PRESETS),
 list:se225MaterialList,create:se225MaterialCreate,edit:se225MaterialEdit,
 duplicate:se225MaterialDuplicate,remove:se225MaterialDelete,
 assign:se225MaterialAssign,unassign:se225MaterialUnassign,
 export:se225MaterialExport,import:se225MaterialImport,
 inspect:()=>({materials:se225MaterialList().length,assignments:se225MaterialData()?.assignments.length||0,
  active:window.SWYRL_ENGINE_STUDIOS?.active?.()==='materials',cap:SE225_M_CAP})
});
