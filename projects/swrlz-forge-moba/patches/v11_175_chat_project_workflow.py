"""§E v11.175: typed project creation, preserved starters and active-project context."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/chat_project_workflow_v11_175.js').read_text()
    html=once(html,'projectId:currentProject.canonicalId||currentProject.name,stationId:', 'projectId:currentProject.instanceId||currentProject.canonicalId||currentProject.name,stationId:')
    html=once(html,'function getProjectId(){if(!currentProject',js+'\nfunction getProjectId(){if(!currentProject')
    html=once(html,"if(!projectIds.has(currentProject))projectIds.set(currentProject,id());return projectIds.get(currentProject);", "if(!projectIds.has(currentProject))projectIds.set(currentProject,bounded(currentProject.instanceId,160)?currentProject.instanceId:id());return projectIds.get(currentProject);")
    html=once(html,'project:{name:summaryName(currentProject.name),kind:summaryName(currentProject.kind)},workspace,',"project:{name:summaryName(currentProject.projectName||currentProject.name),kind:summaryName(currentProject.kind),template:summaryName(currentProject.template),sourceStarterId:summaryName(currentProject.sourceStarterId||'')},starters:se175Starters(),dirty:!!dirty,...(typeof seLevels!=='undefined'&&seLevelsCurrent()?{activeLevel:{id:seLevels.active,name:summaryName(seLevelsCurrent().name)}}:{}),workspace,")
    html=once(html,"if(new TextEncoder().encode(JSON.stringify(value)).length>32768)","se175UpdateLabel();if(new TextEncoder().encode(JSON.stringify(value)).length>32768)")
    html=once(html,"'mesh.add':[['op','kind']", "'project.create':[['op','starterId','name'],[]],\n    'mesh.add':[['op','kind']")
    html=once(html,"if(ctx.mode!=='edit')throw Error('STOP_PLAY_BEFORE_EDITING');", "if(ctx.mode!=='edit')throw Error('STOP_PLAY_BEFORE_EDITING');\n  if(op.op==='project.create'&&(!bounded(op.starterId,100)||!Object.hasOwn(se175StarterKinds,op.starterId)||!bounded(op.name,100)||!op.name.trim()))throw Error('INVALID_PROJECT_CREATE');")
    html=once(html,'for(const op of taken.operations)validateOperation(op,before);',"if(taken.operations.some(op=>op?.op==='project.create')&&taken.operations.length!==1)throw Error('PROJECT_CREATE_REQUIRES_SEPARATE_BATCH');\n    for(const op of taken.operations)validateOperation(op,before);")
    html=once(html,'results.push({op:op.op,ok:true,...execute(op)});',"results.push({op:op.op,ok:true,...(op.op==='project.create'?await se175Create(op,active,before):execute(op))});")
    html=once(html,"setStatus(failed?'Some editor actions could not finish. See Chat for the receipts.':'Native editor changes applied. Undo is available.',failed);", "if(!failed&&taken.operations[0]?.op==='project.create'){revoke('New project opened. Reconnect on your next message.');setStatus('Created '+summaryName(currentProject.projectName||currentProject.name)+' · saved on this device. Chat will inspect it on your next message.');}else setStatus(failed?'Some editor actions could not finish. See Chat for the receipts.':'Native editor changes applied. Undo is available.',failed);\n    se175UpdateLabel();")
    html=once(html,'epoch++;return nativeMarkDirty.apply(this,args);','epoch++;const result=nativeMarkDirty.apply(this,args);se175ScheduleSave();return result;')
    html=once(html,"epoch++;if(!preserve)revoke('Project changed.');", "epoch++;if(!preserve&&!se175Transition)revoke('Project changed.');")
    html=once(html,'projectIds.set(currentProject,previousId);return result;', 'projectIds.set(currentProject,previousId);se175UpdateLabel();return result;')
    html=once(html,'mount();se170Install();','mount();se170Install();se175Install();')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_174_MOBILE_EDITOR_VIEWPORT','SWYRL_ENGINE_DEPLOY_MARKER: V11_175_CHAT_PROJECT_WORKFLOW'),
      ('ENGINE · MAKER v11.174','ENGINE · MAKER v11.175'),
      ('v11.174 · full-height mobile editor and clear controls','v11.175 · Chat creates independent native projects'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.174'","window.SWRLZ_FORGE_BUILD={version:'v11.175'"),
      ('<title>§wyrl§ Engine · Maker v11.174</title>','<title>§wyrl§ Engine · Maker v11.175</title>')]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key);notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Chat creates your project from a reusable starter',date='2026-10-30',changes=[
      'Ask Chat to create a named blank scene, blank model or a new project from an advertised native starter. The editor opens the independent copy.',
      'The existing workspace is saved on this device before switching; reusable starter sources are preserved. Storage failure stops creation instead of discarding your work.',
      'My Projects includes local project copies. Local native edits autosave; Save to account remains the explicit way to sync a complete project through your Google account.',
      'Chat receives the active project name, starter, current level, workspace, selection and real object counts before each request. A new project retires the old edit grant.',
      'Native project creation is a separate typed action; unsupported work reports a failure. Physical device and real-account acceptance remain separate.'
    ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
