"""§E v11.487 — correct exported identity/names and first account-save naming.

One new patch applied to verified v11.486; no regeneration of old patch
sources, no starter mutation, and no parallel account storage.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_487_PROJECT_EXPORT_NAMING'

def once(text,old,new,label):
    count=text.count(old)
    if count!=1:raise AssertionError(('v11.487 source anchor',label,count,old[:130]))
    return text.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS' in html
    script=(ROOT/'runtime/project_export_naming_v11_487.js').read_text('utf8')
    for token in ('se487DownloadProject','se487FetchCardProject','se487DownloadModelUpdate','se487AskProjectName'):
        assert token in script,token

    # Model Atelier's v11.3 legacy export still hardcodes Prism Jester even
    # when the active model is the owner's completely different mesh.
    name_helper="""  function se487ModelExportBase(){
    const inScratch=window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()===true;
    const projectName=String(currentProject?.projectName||currentProject?.name||'').trim();
    const modelName=String(model()?.name||'').trim();
    const legacy=name=>/^(prism jester|untitled(?: model| project)?|model atelier)$/i.test(name);
    const resolved=inScratch?(modelName||'Untitled Model'):
      (projectName&&!legacy(projectName)?projectName:
        (modelName&&!legacy(modelName)?modelName:(projectName||modelName||'Untitled Model')));
    return resolved.replace(/[\\/:*?"<>|\x00-\x1f]+/g,'-')
      .replace(/\s+/g,'-').replace(/-+/g,'-')
      .replace(/^[-.]+|[-.]+$/g,'').slice(0,90)||'Untitled-Model';
  }
"""
    html=once(html,'  function exportJSON(){if(!model())return;',
              name_helper+'  function exportJSON(){if(!model())return;',
              'model exporter filename helper')
    html=once(html,
      "window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()?'untitled-model.model.json':'prism-jester.model.json'",
      "se487ModelExportBase()+'.model.json'",
      'dynamic model JSON export filename')
    html=once(html,
      "const lines=['# §wyrl§ Model Atelier v11.3','o Prism_Jester'];",
      "const lines=['# §wyrl§ Model Atelier v11.3','o '+se487ModelExportBase().replace(/[^a-zA-Z0-9_-]/g,'_')];",
      'dynamic OBJ object header')
    html=once(html,
      "download('prism-jester.mesh.obj',lines.join('\\n')+'\\n','text/plain');",
      "download(se487ModelExportBase()+'.mesh.obj',lines.join('\\n')+'\\n','text/plain');",
      'dynamic OBJ filename')

    # Native Save Project saves named user copies. When the account is
    # connected, first-time or placeholder names require an explicit choice.
    html=once(html,
      """  if(!se371HasSavedIdentity())await se371Clone(se371NewName(se371ProjectName()));
  else await se371SaveLocal();""",
      """  if(!se371HasSavedIdentity()){
    const name=ready&&se176AccountConnected
      ?se487AskProjectName(se371NewName(se371ProjectName()))
      :se371NewName(se371ProjectName());
    if(name===null)throw Error('Save cancelled: no project name supplied');
    await se371Clone(name);
  }else{
    if(ready&&se176AccountConnected&&se487NativeProjectUnnamed()){
      const name=se487AskProjectName('');
      if(name===null)throw Error('Save cancelled: no project name supplied');
      se175StampProject(getProjectId(),name,se371SourceId());
    }
    await se371SaveLocal();
  }""",
      'first saved native project name')

    # Name prompts for standalone Model and Particle Studio account assets.
    # The current asset ID and account revision must not be regenerated.
    asset_name=""" function se487AssetUnnamed(label){
  return !label||/^(prism jester|untitled(?:\\s+(?:model|project|asset))?|new (?:model|project)|model asset|particle asset)$/i.test(String(label).trim());
 }
 function se487NameAssetForAccount(type,record,working){
  if(!se487AssetUnnamed(record.name))return true;
  if(working?.remote){
   const prior=cloudRows.find(item=>item.id===working.remote.id);
   const previous=String(prior?.name||'').replace(/^\\[(?:Model|Particle)\\]\\s*/,'').trim();
   if(previous&&!se487AssetUnnamed(previous)){
    record.name=previous;record.data.name=previous;return true;
   }
   // Do not silently rename an already-account-saved legacy project.
   return true;
  }
  const response=window.prompt('Name this '+(type==='modeler'?'model':'particle project')+' for your account','');
  if(response===null){status('Account save cancelled. No asset was overwritten.');return false;}
  const label=String(response).trim();
  if(!label||label.length>100)throw Error('Please provide an asset name (1–100 characters)');
  record.name=label;record.data.name=label;
  if(type==='modeler'){
   const source=se470Source(type);
   if(source){
    source.name=label;
    if(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.())
      window.SWYRL_ENGINE_WORKSPACES.draftEdited?.();
    else if(typeof markDirty==='function')markDirty();
   }
  }
  return true;
 }
"""
    html=once(html,
      " async function save(type,cloud){\n  if(!['modeler','particles'].includes(type)||busy)return false;",
      asset_name+" async function save(type,cloud){\n  if(!['modeler','particles'].includes(type)||busy)return false;",
      'asset account-name helper')
    html=once(html,
      """   const record=snapshot(type),working=se470Working.get(type);
   if(cloud){""",
      """   const record=snapshot(type),working=se470Working.get(type);
   if(cloud&&!se487NameAssetForAccount(type,record,working))return false;
   if(cloud){""",
      'name before asset account save')

    # Each My Projects card exports THAT exact project. No active editor
    # replacement, no default "Prism Jester", and no cross-account lookup.
    card="""  const exportProject=document.createElement('button');
  exportProject.type='button';exportProject.textContent='Export Project';
  exportProject.title='Export this exact saved project as a full native file';
  exportProject.onclick=async()=>{
    exportProject.disabled=true;result.textContent='Exporting saved project…';
    try{
      const {payload}=await se487FetchCardProject(record,source);
      const asset=payload.assetRecord?.schema==='swrlz-asset-record-v1';
      se487DownloadProject(record.name||payload.project?.projectName||payload.project?.name,payload,asset);
      result.textContent='Exported '+(asset?'studio asset':'native project')+' without changing your workspace.';
    }catch(error){result.textContent='Export failed: '+String(error?.message||error).slice(0,160);}
    finally{exportProject.disabled=false;}
  };
  const modelExportable=record.name?.includes('§E Asset · [Model]')||
      /model-atelier|modeler/i.test(String(record.kind||record.preview?.kind||record.starterId||''));
  if(modelExportable){
    const exportUpdate=document.createElement('button');
    exportUpdate.type='button';exportUpdate.textContent='Export Model Update';
    exportUpdate.title='Export an editable update package bound to this saved model';
    exportUpdate.onclick=async()=>{
      exportUpdate.disabled=true;result.textContent='Preparing model update package…';
      try{
        const {payload,record:saved}=await se487FetchCardProject(record,source);
        se487DownloadModelUpdate(record.name||payload.project?.name,payload,source,saved);
        result.textContent='Model update exported. Reopen this project to apply a modified version.';
      }catch(error){result.textContent='Export update failed: '+String(error?.message||error).slice(0,160);}
      finally{exportUpdate.disabled=false;}
    };
    actions.append(exportUpdate);
  }
"""
    html=once(html,
      '  actions.append(open,see);article.append(actions);',
      card+'  actions.prepend(open,see);actions.append(exportProject);article.append(actions);',
      'My Projects selected-card export actions')

    # Hoist project helpers into the existing authenticated host's closure,
    # after v11.486 cloud revisions and v11.371 storage wrappers.
    html=once(html,
      'window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({',
      script+'\nwindow.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({',
      'named project export and save helpers')

    for old,new,label in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS',MARKER,'marker'),
      ('ENGINE · MAKER v11.486','ENGINE · MAKER v11.487','header'),
      ('v11.486 · rolling project revisions and in-place model updates',
       'v11.487 · correct project exports and naming','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.486'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.487'",'build identity'),
      ('<title>§wyrl§ Engine · Maker v11.486</title>',
       '<title>§wyrl§ Engine · Maker v11.487</title>','page title'),
    ):html=once(html,old,new,label)
    prior=" source.engine='§wyrl§ Engine · Maker v11.486';source.version=11.486;"
    if html.count(prior)!=5:raise AssertionError(('provenance',html.count(prior)))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.487';source.version=11.487;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.486']
    notes['history'].insert(0,{'version':'v11.486','changes':notes.get('changes',[])})
    notes.update(version='v11.487',date='2026-11-17',
      title='Correct model file export names and account project naming',
      changes=[
        'Model JSON and OBJ exports use the active named model or saved project, never the original Prism Jester template filename or OBJ object header.',
        'On first account save, unnamed native projects and standalone Model/Particle assets request a user-defined name. Cancel prevents an account write.',
        'My Projects cards export that specific saved account or on-device project without loading/replacing the active editor.',
        'Model project cards can export the identity- and revision-bound update package for in-place modifications.',
        'Starter copy protection, existing account IDs/revisions, mesh and UV data, and previous eight-slot revision history are preserved.',
        'Source/build tests and browser-delivery verification are required; physical Moto and Quest acceptance is pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
