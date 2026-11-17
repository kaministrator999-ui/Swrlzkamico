/* §E v11.488 — explicit account asset names and an in-place Rename Model.
   These functions live inside the existing standalone asset library closure. */
function se488GenericAssetName(name){
 const value=String(name||'').trim();
 return !value||/^(?:prism jester|untitled(?:\s+(?:model|asset|project))?|new model|model asset|particle asset|untitled)$/i.test(value);
}
function se488SetModelName(value){
 const model=se470Source('modeler');
 if(!model||model.schema!=='swyrl-model-atelier-v1')throw Error('No active editable model');
 model.name=value;
 if(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.())
  window.SWYRL_ENGINE_WORKSPACES.draftEdited?.();
 else if(typeof markDirty==='function')markDirty();
}
function se488NameAssetBeforeCloudSave(type,record,working){
 if(!se488GenericAssetName(record.name))return true;
 if(working?.remote){
  const matched=cloudRows.find(row=>row.id===working.remote.id);
  const old=String(matched?.name||'').replace(/^\[(?:Model|Particle)\]\s*/,'').trim();
  if(old&&!se488GenericAssetName(old)){record.name=old;record.data.name=old;}
  // Existing cloud assets are not unexpectedly renamed by an ordinary save.
  return true;
 }
 const response=window.prompt('Name this '+(type==='modeler'?'model':'particle project')+' before saving to your account','');
 if(response===null){status('Save cancelled. Your account asset is unchanged.');return false;}
 const name=String(response).trim();
 if(!name||name.length>100)throw Error('Enter a name of 1–100 characters');
 record.name=name;record.data.name=name;
 if(type==='modeler')se488SetModelName(name);
 return true;
}
function se488RenameActiveModel(){
 if(mode()!=='modeler')throw Error('Open Model Studio first');
 const current=se470Source('modeler');
 if(!current)throw Error('No editable model is open');
 const previous=String(current.name||'').trim();
 const answer=window.prompt('Name this model',se488GenericAssetName(previous)?'':previous.slice(0,100));
 if(answer===null)return;
 const name=String(answer).trim();
 if(!name||name.length>100)throw Error('Enter a name of 1–100 characters');
 se488SetModelName(name);
 status('Model named '+name+'. Save to account to update its existing saved revision.');
}
function se488InstallNameAction(bar){
 if(!bar||bar.querySelector('[data-se488-name]'))return;
 const button=document.createElement('button');button.type='button';button.textContent='Name Model';
 button.dataset.se488Name='1';button.title='Set or change this model name without creating another project';
 button.onclick=()=>{
  try{se488RenameActiveModel()}
  catch(error){status('Rename failed: '+String(error?.message||error).slice(0,140),true);}
 };
 bar.insertBefore(button,bar.querySelector('#se468AssetStatus'));
}
