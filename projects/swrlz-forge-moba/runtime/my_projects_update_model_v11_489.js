/* §E v11.489 — selected-card "Update Model" for My Projects.
   Updates only a saved model asset, NEVER loads a new scene or creates a
   project; exact account CAS protects against newer edits on another device. */
(function se489MyProjectUpdate(){
 'use strict';
 const previous=se184ProjectCard;
 const NAME=window.SWYRL_ENGINE_MY_PROJECTS_EXPORT_487;
 const revisions=window.SWYRL_ENGINE_REVISIONS_486;
 const LIMIT=32*1024*1024;
 const msg=error=>String(error?.message||error).slice(0,190);
 const safeId=id=>typeof id==='string'&&id.length>0&&id.length<=160;
 function supported(model){
  if(!model||model.schema!=='swyrl-model-atelier-v1'||
   !Array.isArray(model.parts)||model.parts.length<1||model.parts.length>5000)return false;
  const ids=new Set();
  for(const part of model.parts){
   if(!part||!safeId(part.id)||ids.has(part.id)||typeof part.kind!=='string')return false;
   ids.add(part.id);
   if(part.topologyMesh){
    const m=part.topologyMesh;
    if(!Array.isArray(m.positions)||m.positions.length%3!==0||m.positions.length>1500000||
       !Array.isArray(m.indices)||m.indices.length%3!==0||m.indices.length>6000000||
       !Array.isArray(m.uvs)||m.uvs.length!==m.positions.length/3*2)return false;
    if(!m.positions.every(n=>Number.isFinite(n)&&Math.abs(n)<1e5)||
       !m.uvs.every(n=>Number.isFinite(n)&&Math.abs(n)<1e5))return false;
    const count=m.positions.length/3;
    if(!m.indices.every(n=>Number.isInteger(n)&&n>=0&&n<count))return false;
    if(part.skinning){
     const skin=part.skinning;
     if(skin.schema!=='swyrl-explicit-skin-v1'||
        !Array.isArray(skin.indices)||!Array.isArray(skin.weights)||
        skin.indices.length!==count*4||skin.weights.length!==count*4||
        !skin.indices.every(n=>Number.isInteger(n)&&n>=0&&n<48)||
        !skin.weights.every(n=>Number.isFinite(n)&&n>=0&&n<=1))return false;
    }
   }
  }
  const rig=model.rigging;
  if(rig!=null){
   if(rig.schema==='swyrl-cloth-skin-v1'){
    if(!window.SWYRL_ENGINE_CLOTH_RIG_489?.validate(rig)||
       !ids.has(rig.targetPartId))return false;
   }else if(rig.schema==='swyrl-hand-skin-v1'){
    if(typeof se220RigValidate!=='function'||!se220RigValidate(rig))return false;
   }else return false;
  }
  return true;
 }
 function sameModel(oldModel,nextModel){
  const prior=new Set(oldModel.parts.map(p=>p.id));
  return nextModel.parts.some(part=>prior.has(part.id));
 }
 function sourceModel(input,active,record,source){
  const asset=active.assetRecord?.schema==='swrlz-asset-record-v1';
  const nativeId=active.project?.instanceId||null;
  const current=active.project?.modelAtelier;
  const storedRevision=source==='cloud'?record.revision:record?.cloudRef?.revision||null;
  const accountId=source==='cloud'?record.id:record?.cloudRef?.id||null;
  let candidate,original=null;
  if(input?.schema==='se-model-project-update-v1'){
   if(asset||input.target?.projectId!==nativeId||
      input.target?.accountId!==accountId||
      input.target?.baseRevision!==storedRevision)
    throw Error('Update package belongs to another project or revision. Export again from this card.');
   candidate=input.model;
  }else if(input?.schema==='se-asset-update-v1'){
   if(!asset||input.target?.type!=='modeler'||
      input.target?.id!==active.assetRecord.id||
      input.target?.accountId!==accountId||
      input.target?.baseRevision!==storedRevision)
    throw Error('Asset update belongs to another model or revision. Export again from this card.');
   candidate=input.data;
  }else if(input?.project?.modelAtelier){
   candidate=input.project.modelAtelier;original=input.project;
   if(input.assetRecord?.id&&input.assetRecord.id!==active.assetRecord?.id)
    throw Error('The file is an export of a different saved asset.');
   if(input.project.instanceId&&input.project.instanceId!==nativeId)
    throw Error('The native project ID differs from this saved project.');
   if(original.canonicalId&&active.project.canonicalId&&
      original.canonicalId!==active.project.canonicalId)
    throw Error('The native project starter identity differs from this saved project.');
   if(!input.project.instanceId && !sameModel(current,candidate))
    throw Error('Unidentified export has no common mesh ID with this saved model.');
  }else if(input?.schema==='swyrl-model-atelier-v1'&&input.model){
   // Portable model-only export. Allowed only when at least one part ID
   // belongs to this explicitly selected saved project.
   candidate=input.model;
   if(!sameModel(current,candidate))
    throw Error('This model JSON does not share the selected project mesh ID.');
  }else throw Error('Unsupported update file. Use Export Model Update or a native .swyrl.json file.');
  if(!supported(candidate)||!sameModel(current,candidate))
   throw Error('Invalid model, rig, UV topology, or no matching original mesh ID.');
  return structuredClone(candidate);
 }
 async function selectFile(){
  return await new Promise(resolve=>{
   const input=document.createElement('input');
   input.type='file';input.accept='.json,.swyrl,application/json';input.hidden=true;
   document.body.append(input);
   const finish=file=>{input.remove();resolve(file)};
   input.addEventListener('change',()=>finish(input.files?.[0]||null),{once:true});
   input.addEventListener('cancel',()=>finish(null),{once:true});
   input.click();
  });
 }
 async function updateSelectedModel(record,source,chosen){
  if(!safeId(record?.id))throw Error('No saved project selected');
  if(source==='cloud'&&(!ready||!se176AccountConnected))throw Error('Sign into the same account first');
  const file=chosen||await selectFile();
  if(!file)return 'No changes made.';
  if(file.size>LIMIT)throw Error('Update file exceeds 32 MiB');
  const input=JSON.parse(await file.text());
  const {id,doc,metadata}=await NAME.selectedDocument(record,source);
  const current=doc.project?.modelAtelier;
  if(!supported(current))throw Error('The selected project is not a valid saved Model Studio project');
  const changed=sourceModel(input,doc,metadata,source);
  if(!confirm('Update the model in '+String(metadata.name||record.name)+
    ' (revision '+(metadata.revision||'local')+')?\n\nOnly the model data changes; the project ID, scene and revision history are retained.'))return 'Update cancelled.';
  const next=structuredClone(doc);
  next.project.modelAtelier=changed;
  // Mirror the modified model into the matching editable active level.
  // Leave unrelated game levels, scene actors, and project metadata alone.
  const levels=next.project.levelPack;
  if(levels?.schema==='se-levels-v1'&&Array.isArray(levels.levels)){
   const active=levels.levels.find(level=>level.id===levels.active);
   const embedded=active?.data?.project?.modelAtelier;
   if(active?.data?.project?.kind==='model-atelier'&&
      embedded?.schema==='swyrl-model-atelier-v1'&&
      Array.isArray(embedded.parts)&&sameModel(embedded,changed)){
    active.data.project.modelAtelier=structuredClone(changed);
   }
  }
  if(source==='cloud'){
   const isAsset=doc.assetRecord?.schema==='swrlz-asset-record-v1';
   const max=isAsset?8*1024*1024:MAX_RAW;
   const version=metadata.revision;
   if(!Number.isInteger(version)||version<1)throw Error('Cloud revision unavailable');
   const archived=(await revisions.prepare(doc,next,version,max)).payload;
   const bytes=new TextEncoder().encode(JSON.stringify(archived));
   if(bytes.byteLength>max)throw Error('Revised model exceeds account asset size limit');
   const reply=await rpc('cloud.save',{
    bytes:bytes.buffer,name:metadata.name||record.name,
    projectId:id,expectedRevision:version
   },[bytes.buffer]);
   if(reply?.durable!==true||reply.project?.id!==id||reply.project.revision!==version+1)
    throw Error('Account did not confirm the same-project revision. Refresh before retrying.');
   // Do not alter an open editor or its cached expected revision behind its back.
   await se170Refresh();
   return 'Updated '+String(metadata.name||record.name)+' to revision '+reply.project.revision+
    '. If this project is open, reload it before saving more edits.';
  }
  if(doc.project?.instanceId&&doc.project.instanceId!==id)
    throw Error('Local project identity is inconsistent. No update was written.');
  const history=await revisions.readLocal(id).catch(()=>null);
  if(!history)await revisions.recordLocal(id,doc);
  await se175Store([{...metadata,data:next,updatedAt:new Date().toISOString()}]);
  await revisions.recordLocal(id,next);
  await se175RefreshLocal();
  return 'Updated the same on-device project. Its previous model remains in local revision history.';
 }
 se184ProjectCard=function(record,source){
  const card=previous(record,source);
  const actions=card.querySelector('.se184-card-actions');
  const status=card.querySelector('.se184-preview-status');
  if(!actions||!status)return card;
  const button=document.createElement('button');
  button.type='button';button.textContent='Update Model';
  button.dataset.se489Update='model';
  button.title='Upload a modified model into this same saved project and create a new revision';
  button.setAttribute('aria-label','Update model in '+String(record.name||'saved project'));
  button.onclick=async()=>{
   if(button.disabled)return;
   button.disabled=true;status.textContent='Checking selected project…';
   try{status.textContent=await updateSelectedModel(record,source)}
   catch(error){status.textContent='Update failed: '+msg(error);}
   finally{button.disabled=false}
  };
  actions.append(button);
  return card;
 };
 window.SWYRL_ENGINE_MY_PROJECTS_UPDATE_489=Object.freeze({
  updateSelectedModel,validateModel:supported,prepareSource:sourceModel
 });
})();
