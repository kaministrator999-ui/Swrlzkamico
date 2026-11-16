"""§E v11.470: repair live UV positioning and make Model Studio account saves explicit/idempotent."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_470_UV_MODEL_SAVE'

def once(s,old,new,tag):
    count=s.count(old)
    if count!=1:
        raise AssertionError(('v11.470 anchor',tag,count,old[:120]))
    return s.replace(old,new,1)

def apply(html):
    for token in ('SWYRL_ENGINE_DEPLOY_MARKER: V11_469_UV_SHAPE_FIT',
                  'SE469_UV_SHAPE_FIT_START','SE468_STANDALONE_STUDIO_ASSETS_START',
                  'function se336SlideSet(offset)', 'function se371Run(mode)',
                  'function se184RenderCloudProjects(rows)'):
        assert token in html,token

    # Imported PNG repositioning: use the native material right away, not only
    # the later "dirty" document rebuild. Narrow UI button scoping avoids
    # overwriting disabled Apply/Cancel on the newer UV fitting controls.
    html=once(html,
        """  part.uvPaintOffset=next;
  signalEdited();
  se336SlideNotify();""",
        """  part.uvPaintOffset=next;
  se336SlidePreview(part);
  signalEdited();
  se336SlideNotify();""",'UV nudge material preview')
    html=once(html,
        """    for(const material of materials)if(material?.map?.isTexture)
      material.map.offset.set(offset[0],offset[1]);""",
        """    for(const material of materials)if(material?.map?.isTexture){
      material.map.offset.set(offset[0],offset[1]);
      material.map.updateMatrix();
    }""",'UV material updateMatrix')
    html=once(html,
        """function se336SlideNudge(direction) {
  if(!se336SlideState().enabled)return;""",
        """function se336SlideNudge(direction) {
  if(!se336SlideState().available)return;
  if(!se336SlideState().enabled)se336SlideToggle();""",'UV nudge activation')
    html=once(html,
        """  for (const button of root.querySelectorAll('button'))
    button.disabled = !target || (button.id === 'se336UVRemove' && !target.part.uvPaintPNG);""",
        """  for (const button of root.querySelectorAll('.se336-uv-actions button'))
    button.disabled = !target || (button.id === 'se336UVRemove' && !target.part.uvPaintPNG);
  // The nested UV Preview and Shape-fit own their own Apply/Cancel disabled state.""",
        'UV status buttons')
    html=once(html,
        """      part.uvPaintPNG = png;
      signalEdited();
      select(id);""",
        """      part.uvPaintPNG = png;
      signalEdited();
      select(id);
      se336SlideNotify();
      se356UVPreviewSchedule();""",
        'UV import updates controls')

    # Native modeler Save Project must never clone the active Game project.
    # Route it to the explicitly requested standalone account asset operation.
    html=once(html,
        """async function se371Run(mode){
 if(se371ActionBusy)return;""",
        """async function se371Run(mode){
 if(window.SWYRL_ENGINE_WORKSPACES?.modelerActive?.()){
  if(mode==='save'){
   const api=window.SWYRL_ENGINE_ASSET_LIBRARY;
   if(!api?.save){se371Display('Model asset library is unavailable.',true);return;}
   await api.save('modeler',true);
  }
  return;
 }
 if(se371ActionBusy)return;""",'model Save Project explicit account')
    html=once(html,
        """ for(const [label,mode] of [['Save Project','save'],['Clone Project','clone']]){
  const button=document.createElement('button');""",
        """ for(const [label,mode] of (scope==='model'
   ?[['Save to account','save']]
   :[['Save Project','save'],['Clone Project','clone']])){
  const button=document.createElement('button');""",
        'model Save button explicit destination')

    # Explicit account asset writes reuse one working model identity and cloud
    # revision. Local draft recovery and manual local saves remain separate.
    html=once(html,
        """ const cloudRefs=new Map(),localCache=new Map();""",
        """ const cloudRefs=new Map(),localCache=new Map();
 const se470Working=new Map();
 const se470Source=type=>type==='modeler'
  ?(window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()
    ?window.SWYRL_ENGINE_WORKSPACES.scratchModel():currentProject?.modelAtelier)
  :null;
 function se470MarkLoaded(type,record,remote=null){
  se470Working.set(type,{source:se470Source(type),id:record.id,remote});
 }
 function se470ModelAsset(name){return typeof name==='string'&&name.startsWith('§E Asset · [Model] ');}
 function se470VisibleCloud(list){
  const sorted=[...(Array.isArray(list)?list:[])].sort((a,b)=>
   String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))||
   (Number(b.revision)||0)-(Number(a.revision)||0));
  const seen=new Set();
  return sorted.filter(item=>{
   if(!se470ModelAsset(item?.name))return true;
   const key=item.name.toLowerCase();
   if(seen.has(key))return false;
   seen.add(key);return true;
  });
 }""",'stable asset identity helpers')
    html=once(html,
        """ function snapshot(type){
  const data=type==='modeler'?modelData():particleData();
  const name=clean(data.name||data.title||LABEL[type]+' asset');
  return {schema:'swrlz-asset-record-v1',type,id:crypto.randomUUID(),name,updatedAt:new Date().toISOString(),data};
 }""",
        """ function snapshot(type){
  const data=type==='modeler'?modelData():particleData();
  const name=clean(data.name||data.title||LABEL[type]+' asset');
  const source=se470Source(type),old=se470Working.get(type);
  const id=old&&(type==='particles'||old.source===source)?old.id:crypto.randomUUID();
  if(!old||old.id!==id)se470Working.set(type,{source,id,remote:null});
  return {schema:'swrlz-asset-record-v1',type,id,name,updatedAt:new Date().toISOString(),data};
 }""",'reuse snapshot identity')
    html=once(html,
        """  status('Loaded '+record.name+' into '+LABEL[type]+' Studio. Game project unchanged.');""",
        """  se470MarkLoaded(type,record);
  status('Loaded '+record.name+' into '+LABEL[type]+' Studio. Game project unchanged.');""",
        'remember loaded model identity')
    html=once(html,
        """  cloudRows=projects.filter(x=>typeof x.name==='string'&&x.name.startsWith('§E Asset · '))
   .map(x=>({id:x.id,name:x.name.slice('§E Asset · '.length),revision:x.revision,
    type:x.name.includes('[Model]')?'modeler':x.name.includes('[Particle]')?'particles':null}))
   .filter(x=>x.type);""",
        """  cloudRows=se470VisibleCloud(projects.filter(x=>
   typeof x.name==='string'&&x.name.startsWith('§E Asset · ')))
   .map(x=>({id:x.id,name:x.name.slice('§E Asset · '.length),revision:x.revision,
    type:x.name.includes('[Model]')?'modeler':x.name.includes('[Particle]')?'particles':null}))
   .filter(x=>x.type);""",
        'no legacy duplicate cloud asset cards')
    # Disable unexpected account auto-loading; account data is intentionally opened by user.
    start="""  // Restore only into an empty standalone draft, never overwrite edits or
  // load a game project. Account metadata does not carry editable geometry.
  const type=mode(),autoKey=userKey+':'+type;"""
    stop="""  }
 }
 async function save(type,cloud){"""
    start_at=html.index(start)
    stop_at=html.index(stop,start_at)+len("  }\n")
    html=html[:start_at]+"""  // Account list is metadata only. A blank studio remains blank until the user
  // explicitly selects a saved asset; no implicit account loads occur.
"""+html[stop_at:]
    save_start=html.index(" async function save(type,cloud){", start_at)
    save_end=html.index(" async function loadSelection(){",save_start)
    save_replacement=""" async function save(type,cloud){
  if(!['modeler','particles'].includes(type)||busy)return false;
  busy=true;refresh();
  try{
   if(cloud&&(!connected||!api()?.save))throw Error('Connect your Google account in the Chat panel before saving.');
   const record=snapshot(type),working=se470Working.get(type);
   if(cloud){
    const payload=new TextEncoder().encode(JSON.stringify(envelope(record)));
    if(payload.byteLength>MAX)throw Error('Asset exceeds the 8 MiB account limit.');
    const remote=working?.remote||null;
    const result=await api().save(payload.buffer,
     '§E Asset · ['+(type==='modeler'?'Model':'Particle')+'] '+record.name,
     remote?.id||null,remote?.revision||0);
    if(result.durable!==true||!result.project?.id||
       !Number.isInteger(result.project.revision)||result.project.revision<1)
     throw Error('Account did not confirm durable versioned storage.');
    const link={id:result.project.id,revision:result.project.revision};
    cloudRefs.set(record.id,link);
    se470Working.set(type,{source:se470Source(type),id:record.id,remote:link});
    status('Saved '+record.name+' to your account · revision '+link.revision+'.');
    await listCloud();
   }else{
    const rows=read(type);
    persist(type,[record,...rows.filter(row=>row.id!==record.id)].slice(0,30));
    status('Saved '+record.name+' on this device (separate from account).');
   }
   return true;
  }catch(error){status('Save failed: '+error.message,true);return false;}
  finally{busy=false;refresh();}
 }
 async function loadAccountAsset(type,id){
  if(!connected||busy||!api()?.load)throw Error('Connect your Google account before loading.');
  if(!['modeler','particles'].includes(type)||!/^[a-zA-Z0-9_-]{1,128}$/.test(id))
   throw Error('Invalid model asset selection.');
  busy=true;refresh();
  try{
   const result=await api().load(id);
   if(!(result.bytes instanceof ArrayBuffer)||result.bytes.byteLength>MAX)
    throw Error('Invalid asset download.');
   const record=decode(JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(result.bytes)),type);
   load(type,record);
   const metadata=cloudRows.find(x=>x.id===id);
   const revision=metadata?.revision||result.project?.revision;
   se470Working.set(type,{source:se470Source(type),id:record.id,
    remote:Number.isInteger(revision)&&revision>=1?{id,revision}:null});
   status('Loaded '+record.name+' from account. Changes are local until Save to account.');
   return true;
  }finally{busy=false;refresh();}
 }
"""
    html=html[:save_start]+save_replacement+html[save_end:]
    html=once(html,
        """    load(type,record);
    persist(type,[record,...read(type).filter(x=>x.id!==record.id)].slice(0,30));""",
        """    load(type,record);
    const remote=cloudRows.find(x=>x.id===value.slice(6));
    se470Working.set(type,{source:se470Source(type),id:record.id,
     remote:Number.isInteger(remote?.revision)&&remote.revision>=1?
      {id:value.slice(6),revision:remote.revision}:null});""",
        'no automatic local copy during cloud load')
    html=once(html,
        """  window.addEventListener('swrlz:project-loaded',refresh);""",
        """  window.addEventListener('swrlz:project-loaded',refresh);
  window.addEventListener('swrlz:model-blank',()=>{se470Working.delete('modeler');refresh();});""",
        'reset model identity on new blank')
    html=once(html,
        """window.SWYRL_ENGINE_ASSET_LIBRARY=Object.freeze({refresh,save,loadSelection,read,inspect:""",
        """window.SWYRL_ENGINE_ASSET_LIBRARY=Object.freeze({refresh,save,loadSelection,
  loadAccountAsset,read,inspect:""",
        'account model open API')
    html=once(html,
        """  scratch=blank();
  preferScratch=true;
  draftChanged=true;flushDraft();""",
        """  scratch=blank();
  window.dispatchEvent(new Event('swrlz:model-blank'));
  preferScratch=true;
  draftChanged=true;flushDraft();""",
        'new blank identity reset')
    html=once(html,
        """  save:(bytes,name)=>{
   if(!(bytes instanceof ArrayBuffer)||bytes.byteLength>8*1024*1024||typeof name!=='string'||!name.startsWith('§E Asset · '))return Promise.reject(Error('INVALID_ASSET_SAVE'));
   return rpc('cloud.save',{bytes,name,expectedRevision:0},[bytes]);
  },""",
        """  save:(bytes,name,projectId=null,expectedRevision=0)=>{
   if(!(bytes instanceof ArrayBuffer)||bytes.byteLength>8*1024*1024||typeof name!=='string'||!name.startsWith('§E Asset · ')||
     (projectId!==null&&!/^[a-zA-Z0-9_-]{1,128}$/.test(projectId))||
     !Number.isInteger(expectedRevision)||expectedRevision<0)return Promise.reject(Error('INVALID_ASSET_SAVE'));
   return rpc('cloud.save',{bytes,name,expectedRevision,...(projectId?{projectId}:{})},[bytes]);
  },""",
        'versioned account updates')

    # My Projects: model assets appear only once, via the explicit account
    # save path. Device drafts remain retrievable via the local recovery control.
    html=once(html,
        """ const rows=(Array.isArray(records)?records:[]).filter(p=>p&&bounded(p.id,160)).slice(0,1000);""",
        """ const rows=(Array.isArray(records)?records:[]).filter(p=>p&&bounded(p.id,160)&&
  !(['blank-model','model-atelier','wolf-model','sheep-model','festival-girl-saved'].includes(p.starterId)||
   p.preview?.kind==='model-atelier')).slice(0,1000);""",
        'hide model drafts from My Projects gallery')
    html=once(html,
        """ for(const p of (Array.isArray(rows)?rows:[]).slice(0,1000)){""",
        """ const saved=se470SavedCloudProjects(rows);
 for(const p of saved.slice(0,1000)){""",
        'collapse legacy cloud model duplicates')
    html=once(html,
        """ const title=document.createElement('strong');title.textContent=summaryName(record?.name)||'Untitled project';""",
        """ const title=document.createElement('strong');
 title.textContent=summaryName(record?.name?.replace(/^§E Asset · \\[Model\\] /,''))||'Untitled project';""",
        'clean model account card title')
    html=once(html,
        """    const ok=await loadCloud(id);""",
        """    const ok=typeof record?.name==='string'&&record.name.startsWith('§E Asset · [Model] ')
     ?(window.SWYRL_ENGINE_WORKSPACES?.change('modeler')!==false&&
        await window.SWYRL_ENGINE_ASSET_LIBRARY?.loadAccountAsset?.('modeler',id))
     :await loadCloud(id);""",
        'open model account asset in modeler')
    html=once(html,
        """function se184RenderCloudProjects(rows){""",
        """function se470SavedCloudProjects(rows){
 const all=Array.isArray(rows)?rows:[];
 const ordered=[...all].sort((a,b)=>
  String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))||
  (Number(b.revision)||0)-(Number(a.revision)||0));
 const seen=new Set();
 return ordered.filter(item=>{
  if(typeof item?.name!=='string'||!item.name.startsWith('§E Asset · [Model] '))return true;
  const key=item.name.toLowerCase();
  if(seen.has(key))return false;
  seen.add(key);return true;
 });
}
function se184RenderCloudProjects(rows){""",
        'cloud model saved-project filtering')
    html=once(html,
        """    if(!data.projects.length){se170Message('No account projects saved yet. Save a project using § Chat to see it here.');return;}
    se170Message(data.projects.length+' saved project'+(data.projects.length===1?'':'s')+' · Choose Load to open one.');""",
        """    const visible=se470SavedCloudProjects(data.projects);
    if(!visible.length){se170Message('No account projects saved yet. Use Save to account in the appropriate studio.');return;}
    se170Message(visible.length+' saved project'+(visible.length===1?'':'s')+' · Choose Load to open one.');""",
        'account gallery count')

    html=once(html,
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_469_UV_SHAPE_FIT',MARKER,'version marker')
    for old,new in [
        ('ENGINE · MAKER v11.469','ENGINE · MAKER v11.470'),
        ('v11.469 · UV stretch diagnostic and shape-fit','v11.470 · UV placement and explicit model saves'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.469'","window.SWRLZ_FORGE_BUILD={version:'v11.470'"),
        ('<title>§wyrl§ Engine · Maker v11.469</title>',
         '<title>§wyrl§ Engine · Maker v11.470</title>')
    ]:html=once(html,old,new,old[:32])
    prior=" source.engine='§wyrl§ Engine · Maker v11.469';source.version=11.469;"
    assert html.count(prior)==5,('v11.470 provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.470';source.version=11.470;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.469']
    notes['history'].insert(0,{'version':'v11.469','changes':notes.get('changes',[])})
    notes.update(version='v11.470',date='2026-11-15',title='UV image position and manually saved model account projects',changes=[
        'After UV PNG import, UV Slide nudges update the selected mesh texture immediately, and shape-fit Preview/Apply/Cancel keep their own disabled-state ownership.',
        'Model Studio Save to account writes a standalone model asset explicitly, never clones or saves the unrelated active game project.',
        'Repeated saves reuse the same model asset identity and cloud revision rather than creating new local and account project records.',
        'My Projects displays account-saved model assets once, de-duplicating legacy same-named cloud assets without deleting them. Local scratch drafts remain in separate recovery storage.',
        'Opening a saved model from My Projects routes it into the standalone modeler rather than replacing Game Studio.',
        'User-authored account models no longer auto-load into an empty draft without selection; local draft recovery remains unchanged.',
        'Existing game project history, materials, model geometry, particle effects, and native Undo are preserved.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\\/')+html[at+width:]
