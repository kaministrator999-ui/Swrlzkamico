"""§E v11.183: no redundant level rebuild; real loading stages + project UI."""
from pathlib import Path
import json

def once(s, old, new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.183 anchor',old[:155],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_project_ui_load_v11_183.js').read_text(encoding='utf-8')
    css=(root/'runtime/engine_project_ui_load_v11_183.css').read_text(encoding='utf-8')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se183ProjectUI">\n'+css+'\n</style>\n</head>',1)

    # Expose helpers before any bootstrap loader can call seLevelsEnsureUI.
    html=once(html,'const seLevelRawLoadProject=loadProject;',
      js+'\nconst seLevelRawLoadProject=loadProject;')

    # Legacy v11.141 rebuilt scene data twice: first the outer pack, then
    # the active record. Choose exactly the same active record in advance and
    # perform only one original native build. Preserve the original pack as
    # the source of record metadata, IDs, level routes and subsequent saves.
    html=once(html,
'''loadProject=function(data,...args){
 if(seLevels.playingMenu)seLevelsStopMenu();
 const internal=seLevels.loading;
 const result=seLevelRawLoadProject(data,...args);
 if(!internal){
  if(!seLevelsHydrate(data))seLevelsInitSingle(data);
  // If opening a project bundle with a different saved active level, load
  // the selected level using the native loader but without recursive wrappers.
  const chosen=seLevelsCurrent();
  if(chosen?.data?.scene&&data.project?.levelPack){
   seLevels.loading=true;
   try{seLevelRawLoadProject(structuredClone(chosen.data),{workspaceLocal:true});}
   finally{seLevels.loading=false;}
  }
 }
 seLevelsEnsureUI();seLevelsRefresh();
 return result;
};''',
'''loadProject=function(data,...args){
 if(seLevels.playingMenu)seLevelsStopMenu();
 const internal=seLevels.loading;
 const pack=!internal&&data?.project?.levelPack?.schema==='se-levels-v1'
  ?data.project.levelPack:null;
 const valid=Array.isArray(pack?.levels)?pack.levels.filter(l=>
  typeof l?.id==='string'&&l.id&&l.data?.project&&l.data?.scene):[];
 const chosen=valid.find(l=>l.id===pack?.active)||valid[0];
 const target=chosen?structuredClone(chosen.data):data;
 const options=chosen?[{...(args[0]||{}),workspaceLocal:true}]:args;
 const result=seLevelRawLoadProject(target,...options);
 if(!internal){
  if(!seLevelsHydrate(data))seLevelsInitSingle(data);
 }
 seLevelsEnsureUI();seLevelsRefresh();
 return result;
};''')

    # Level project actions keep their native input IDs, onchange and buttons,
    # but move as original nodes into a collapsed/expanded workspace panel.
    html=once(html,"bar.querySelector('#st141LevelSelect').onchange=e=>seLevelsSwitch(e.target.value);",
      "bar.querySelector('#st141LevelSelect').onchange=e=>seLevelsSwitch(e.target.value);")
    html=once(html,"  seLevels.bar=bar;\n","  seLevels.bar=bar;\n  se183InstallLevels(bar);\n")
    html=once(html,
      " if(seLevels.inspector&&(!visible||current.role!=='menu'))seLevels.inspector.hidden=true;\n}",
      " if(seLevels.inspector&&(!visible||current.role!=='menu'))seLevels.inspector.hidden=true;\n se183LevelsSync();\n}")
    html=once(html,
      " if(!seLevels.records.has(id)||seLevels.playingMenu||playing||simulating||stSession)return false;",
      " if(!seLevels.records.has(id)||seLevels.playingMenu||playing||simulating||stSession)return false;\n if(id===seLevels.active)return true;")

    # Native starter cards: await paint before heavy synchronous builders.
    # Confirm dirty-state destruction once before yielding; preserve all
    # canonical template implementations, asynchronous model imports and IDs.
    html=once(html,
      "document.querySelectorAll('[data-project-template]').forEach(b=>b.onclick=()=>createProjectFromTemplate(b.dataset.projectTemplate));",
      "document.querySelectorAll('[data-project-template]').forEach(b=>b.onclick=()=>void se183OpenStarter(b.dataset.projectTemplate));")

    # Same-account list requests within 12s reuse an in-memory result; no
    # bearer tokens or metadata are stored persistently. Manual Refresh
    # always bypasses cache; account changes invalidate it immediately.
    html=once(html,'async function se170Refresh(){','async function se170Refresh(force=false){')
    html=once(html,"    const data=await rpc('cloud.list');",
      "    const data=await se183CloudListCached(()=>rpc('cloud.list'),force);")
    html=once(html,'refresh.onclick=se170Refresh;','refresh.onclick=()=>se170Refresh(true);')
    html=once(html,'function se170Invalidate(){\n  ++se170Epoch;',
      'function se170Invalidate(){\n  se183CloudCacheClear();\n  ++se170Epoch;')
    html=once(html,'async function se176RefreshProjects(){','async function se176RefreshProjects(force=false){')
    html=once(html,"    const result=await rpc('cloud.list');",
      "    const result=await se183CloudListCached(()=>rpc('cloud.list'),force);")
    html=once(html,"document.getElementById('seChatRefresh').onclick=se176RefreshProjects;",
      "document.getElementById('seChatRefresh').onclick=()=>se176RefreshProjects(true);")

    # Local project read and recovery already use asynchronous indexedDB.
    # Expose their real lifecycle without interrupting rollback semantics.
    html=once(html,
      " se175LocalLoading=true;let recovery=null,recoveryState=null,started=false;",
      " se175LocalLoading=true;let recovery=null,recoveryState=null,started=false,opened=false;\n const se183Ticket=se183StartLoad('Opening local project');")
    html=once(html,
      "  const wanted=await se175Read(se175LocalList.value);",
      "  se183LoadStep(se183Ticket,'Reading project on this device');\n  const wanted=await se175Read(se175LocalList.value);")
    html=once(html,
      "  const before=context();recovery=se175Snapshot();",
      "  se183LoadStep(se183Ticket,'Protecting current workspace');await se183PaintNext();\n  const before=context();recovery=se175Snapshot();")
    html=once(html,
      "  revoke('Loading another local project.');started=true;\n  loadProject(structuredClone(wanted.data),{workspaceLocal:true});",
      "  se183LoadStep(se183Ticket,'Building selected 3D scene');await se183PaintNext();\n  if(JSON.stringify(context())!==JSON.stringify(before))throw Error('PROJECT_CHANGED_BEFORE_LOCAL_LOAD');\n  revoke('Loading another local project.');started=true;\n  loadProject(structuredClone(wanted.data),{workspaceLocal:true});")
    html=once(html,
      "se175UpdateLabel();se175LocalMessage('Loaded '+wanted.name+'.');",
      "se175UpdateLabel();se175LocalMessage('Loaded '+wanted.name+'.');opened=true;")
    html=once(html," }finally{se175LocalLoading=false;}",
      " }finally{se175LocalLoading=false;se183FinishLoad(se183Ticket,opened,opened?'Local project ready':'Local project load failed');}")

    # Cloud load: keep validation, recovery and auth enforcement intact.
    html=once(html,
      "  cloudBusy=true;\n  try{revoke('Loading project.');setStatus('Loading complete native project…');const result=await rpc('cloud.load',{projectId});",
      "  cloudBusy=true;let se183Opened=false;\n  const se183OriginProject=currentProject,se183OriginRevision=revision;\n  const se183Ticket=se183StartLoad('Loading saved account project');\n  try{revoke('Loading project.');setStatus('Loading complete native project…');se183LoadStep(se183Ticket,'Downloading account project');const result=await rpc('cloud.load',{projectId});\n    se183LoadStep(se183Ticket,'Validating project data');await se183PaintNext();")
    html=once(html,
      "    const recovery=window.SWYRL_ENGINE_AGENT.inspectScene();\n    try{window.SWYRL_ENGINE_AGENT.loadScene(native);",
      "    if(currentProject!==se183OriginProject||revision!==se183OriginRevision)throw Error('WORKSPACE_CHANGED_DURING_ACCOUNT_DOWNLOAD');\n    const recovery=window.SWYRL_ENGINE_AGENT.inspectScene();\n    se183LoadStep(se183Ticket,'Building selected 3D scene');await se183PaintNext();\n    if(currentProject!==se183OriginProject||revision!==se183OriginRevision)throw Error('WORKSPACE_CHANGED_BEFORE_ACCOUNT_IMPORT');\n    try{window.SWYRL_ENGINE_AGENT.loadScene(native);")
    html=once(html,
      "cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');return true;",
      "cloudRefs.set(getProjectId(),result.project);setStatus('Loaded '+summaryName(result.project.name)+' · revision '+result.project.revision+'.');se183Opened=true;return true;")
    html=once(html,
      "  }catch(error){setStatus('Account load failed: '+error.message,true);}finally{cloudBusy=false;}",
      "  }catch(error){setStatus('Account load failed: '+error.message,true);}finally{cloudBusy=false;se183FinishLoad(se183Ticket,se183Opened,se183Opened?'Account project ready':'Account project load failed');}")

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_182_PROFESSIONAL_UI','SWYRL_ENGINE_DEPLOY_MARKER: V11_183_PROJECT_UI_LOADING'),
      ('ENGINE · MAKER v11.182','ENGINE · MAKER v11.183'),
      ('v11.182 · professional editor layout and overlap audit','v11.183 · clear project controls and faster loading'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.182'","window.SWRLZ_FORGE_BUILD={version:'v11.183'"),
      ('<title>§wyrl§ Engine · Maker v11.182</title>','<title>§wyrl§ Engine · Maker v11.183</title>'),
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';pos=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Cleaner project and Sheep Tag HUD; faster and clearer project loading',
      date='2026-10-31',changes=[
        'Remove redundant actor-count floating pill that covered native editor toolbar controls; existing status bar retains scene/selection information.',
        'Replace cramped in-scene level button strip with a compact Levels toggle that expands into a proper editable, scrollable two-column control panel; retain native select/new/rename/next/menu/export handlers.',
        'Suppress editor-only hints, perspective badges and duplicate level toolbar while Sheep Tag immersive start and runtime menus are visible; retain native Start, LAN, Exit and Chat.',
        'Optimize multi-level project open: select the saved active level before calling the original native loader, eliminating a redundant second full 3D scene rebuild.',
        'Show real preparation, validation, import and completion states with elapsed time for starter, local and account project operations; paint before synchronous scene reconstruction, no fake percentage.',
        'Deduplicate account project listing requests for 12 seconds in memory, with explicit Refresh bypass and account-change invalidation.',
        'Preserve all project data, auto-save recovery, model editor, gameplay, LAN, WebXR and Chat auth behaviors. Owner Android/Quest testing remains acceptance gate.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+length:]
