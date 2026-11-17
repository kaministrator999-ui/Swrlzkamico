/* §E v11.486 — standalone Model/Particle asset in-place update and revision UI.
   Same account asset ID, verified expected revision, no starter replacement. */
const se486AssetRev=window.SWYRL_ENGINE_REVISIONS_486;
function se486ActiveAsset(){
 const type=mode();
 if(!type)throw Error('Open Model Studio or Particle Studio first');
 const working=se470Working.get(type);
 if(!working?.id)throw Error('Save or load this asset before using its revision controls');
 return {type,working,record:snapshot(type)};
}
function se486AssetExport(){
 const {type,working,record}=se486ActiveAsset(),remote=working.remote;
 se486AssetRev.download(record.name,{schema:'se-asset-update-v1',
  target:{type,id:working.id,accountId:remote?.id||null,baseRevision:remote?.revision||null},
  data:record.data,exportedAt:new Date().toISOString()});
 status('Exported '+record.name+' for an update to this same asset.');
}
async function se486AssetUpdate(){
 const {type,working,record}=se486ActiveAsset(),remote=working.remote;
 const file=await se486AssetRev.choose();if(!file)return;
 if(file.size>32*1024*1024)throw Error('Update file exceeds 32 MiB');
 const doc=JSON.parse(await file.text());
 if(doc?.schema!=='se-asset-update-v1'||doc.target?.type!==type||
    doc.target?.id!==working.id||doc.target?.accountId!==(remote?.id||null)||
    doc.target?.baseRevision!==(remote?.revision||null))
   throw Error('Update belongs to a different asset or an older account revision');
 const expected=type==='modeler'?'swyrl-model-atelier-v1':'swyrl-particle-studio-v1';
 const array=type==='modeler'?'parts':'emitters';
 if(doc.data?.schema!==expected||!Array.isArray(doc.data[array])||doc.data[array].length>5000)
  throw Error('Invalid edited studio asset');
 if(!confirm('Update '+record.name+' in place? Its current save will be retained in revision history.'))return;
 const changed={...record,data:structuredClone(doc.data)};
 try{
  load(type,changed);
  if(await save(type,!!remote)!==true)throw Error('Updated editor, but the save was not confirmed');
  status('Updated '+record.name+' in place · new revision saved.');
 }catch(error){
  try{load(type,record)}catch{}
  throw error;
 }
}
async function se486AssetHistory(){
 const {type,working,record}=se486ActiveAsset(),remote=working.remote;
 let items=[],cloud=false;
 if(remote?.id&&connected&&api()?.load){
  const reply=await api().load(remote.id);
  if(reply.project?.id!==remote.id||reply.project?.revision!==remote.revision)
   throw Error('Account asset changed. Reload its latest revision first.');
  const doc=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(reply.bytes));
  items=[...se486AssetRev.history(doc),{number:remote.revision,savedAt:'Current account asset',current:true}];
  cloud=true;
 }else{
  const stored=await se486AssetRev.readLocal('asset-'+working.id);
  items=[...(stored?.entries||[]),...(stored?.latest?[{...stored.latest,current:true}]:[])];
 }
 if(!items.length)throw Error('Save this asset first to start revision history');
 se486AssetRev.present((cloud?'Account':'On-device')+' · '+record.name,items,async item=>{
  const old=await se486AssetRev.unpack(item),restored=decode(old,type);
  if(restored.id!==working.id)throw Error('Revision belongs to a different asset');
  try{
   load(type,restored);
   if(await save(type,cloud)!==true)throw Error('Restored editor, but saving the new revision failed');
   status('Restored revision '+item.number+' as a new revision of '+record.name+'.');
  }catch(error){try{load(type,record)}catch{}throw error}
 });
}
function se486AssetAction(label,fn){
 Promise.resolve().then(fn).catch(error=>status(label+': '+String(error?.message||error).slice(0,170),true));
}
function se486InstallAssetActions(bar){
 if(!bar||bar.querySelector('[data-se486-asset]'))return;
 const controls=[['Export Update','export',se486AssetExport],
  ['Update This Project','update',se486AssetUpdate],
  ['Revision History','history',se486AssetHistory]];
 for(const [label,key,fn] of controls){
  const b=document.createElement('button');b.type='button';b.dataset.se486Asset=key;
  b.textContent=label;b.title=label+' for the active '+(mode()==='modeler'?'model':'studio')+' asset';
  b.onclick=()=>se486AssetAction(label,fn);
  bar.insertBefore(b,bar.querySelector('#se468AssetStatus'));
 }
}
