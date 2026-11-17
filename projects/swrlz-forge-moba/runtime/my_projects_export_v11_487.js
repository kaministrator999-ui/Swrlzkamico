/* §E v11.487 — export the selected My Projects card, never the active viewport.
   Installs in the existing trusted account host after its delete-card wrapper. */
(function se487MyProjectsExport(){
 'use strict';
 const previous=se184ProjectCard;
 const label=name=>String(name||'Untitled project').trim().slice(0,100)||'Untitled project';
 const filename=name=>{
  const stem=label(name).normalize('NFKC').replace(/[^\p{L}\p{N}_-]+/gu,'-').replace(/^-+|-+$/g,'').slice(0,90);
  return stem||'untitled-project';
 };
 function saveBlob(name,bytes){
  const blob=bytes instanceof Blob?bytes:new Blob([bytes],{type:'application/json'});
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download=name;document.body.append(link);link.click();link.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
 }
 async function selectedDocument(record,source){
  const id=String(record?.id||'');
  if(!bounded(id,160)||!['cloud','local'].includes(source))throw Error('Invalid project selection');
  let doc,raw=null,metadata=record;
  if(source==='local'){
   const row=await se175Read(id);
   if(row?.id!==id||!row.data)throw Error('This saved project is unavailable. Refresh My Projects.');
   doc=row.data;metadata=row;
  }else{
   if(!ready||!se176AccountConnected)throw Error('Sign into your account before exporting');
   const reply=await rpc('cloud.load',{projectId:id});
   if(reply?.project?.id!==id||!(reply.bytes instanceof ArrayBuffer)||reply.bytes.byteLength>MAX_RAW)
    throw Error('Could not download the selected account project');
   if(Number.isInteger(record?.revision)&&reply.project.revision!==record.revision)
    throw Error('This project was saved again on another device. Refresh My Projects before exporting.');
   raw=reply.bytes;
   doc=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(raw));
   metadata=reply.project;
  }
  if(!doc?.project||!Array.isArray(doc.scene?.actors)||!doc.editor)
   throw Error('This saved project is missing its native scene or editor data');
  return {id,doc,raw,metadata};
 }
 async function exportNative(record,source){
  const item=await selectedDocument(record,source);
  // Native export keeps full scene, UV images, materials, rigs and all history.
  // Raw account bytes are used unchanged; we do not load/switch the editor.
  const bytes=item.raw||JSON.stringify(item.doc,null,2)+'\n';
  saveBlob(filename(item.metadata?.name||record.name)+'.swyrl.json',bytes);
  return 'Exported complete saved project '+label(item.metadata?.name||record.name)+'.';
 }
 async function exportUpdate(record,source){
  const {id,doc,metadata}=await selectedDocument(record,source);
  const model=doc?.project?.modelAtelier;
  if(model?.schema!=='swyrl-model-atelier-v1'||!Array.isArray(model.parts))
   throw Error('This saved project does not contain an editable Model Studio asset. Use Export Project instead.');
  let update;
  const cloudId=source==='cloud'?id:(metadata.cloudRef?.id||null);
  const revision=source==='cloud'?metadata.revision:(metadata.cloudRef?.revision||null);
  if(doc?.assetRecord?.schema==='swrlz-asset-record-v1'){
   const assetId=doc.assetRecord.id;
   if(!bounded(assetId,160))throw Error('Saved model asset identity is missing');
   update={schema:'se-asset-update-v1',exportedAt:new Date().toISOString(),
    target:{type:'modeler',id:assetId,accountId:cloudId,baseRevision:revision},
    data:structuredClone(model)};
  }else{
   const projectId=doc.project.instanceId;
   if(!bounded(projectId,160))throw Error('Project has no stable model identity. Open and Save Project once, then export again.');
   update={schema:'se-model-project-update-v1',exportedAt:new Date().toISOString(),
    target:{projectId,accountId:cloudId,baseRevision:revision},
    model:structuredClone(model)};
  }
  window.SWYRL_ENGINE_REVISIONS_486.download(metadata?.name||record.name,update);
  return 'Exported an update package for '+label(metadata?.name||record.name)+'.';
 }
 se184ProjectCard=function(record,source){
  const card=previous(record,source);
  const actions=card.querySelector('.se184-card-actions');
  const status=card.querySelector('.se184-preview-status');
  if(!actions||!status)return card;
  for(const [caption,kind,action] of [
   ['Export Project','project',exportNative],
   ['Export Model Update','update',exportUpdate]
  ]){
   const button=document.createElement('button');
   button.type='button';button.textContent=caption;button.dataset.se487Export=kind;
   button.setAttribute('aria-label',caption+' '+label(record?.name));
   button.addEventListener('click',async()=>{
    if(button.disabled)return;
    button.disabled=true;
    status.textContent='Exporting '+label(record?.name)+' from '+(source==='cloud'?'your account':'this device')+'…';
    try{status.textContent=await action(record,source)}
    catch(error){status.textContent='Export failed: '+String(error?.message||error).slice(0,180)}
    finally{button.disabled=false}
   });
   actions.append(button);
  }
  return card;
 };
 window.SWYRL_ENGINE_MY_PROJECTS_EXPORT_487=Object.freeze({
  exportNative,exportUpdate,selectedDocument,filename
 });
})();
