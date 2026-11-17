"""§E v11.494: authenticated model-update stages and verified in-memory auto-reopen."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_494_MODEL_UPDATE_LIFECYCLE'
def once(html,old,new,label):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.494',label,n,old[:140]))
 return html.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_493_PROJECT_LOAD_DIAGNOSTICS' in html
 helpers=(ROOT/'runtime/model_update_account_workflow_v11_494.js').read_text('utf8')
 style=(ROOT/'runtime/model_update_account_workflow_v11_494.css').read_text('utf8')
 assert 'se494TrustedLoadCache' in helpers
 assert '</head>' in html
 html=html.replace('</head>','<style id="se494-model-update">'+style+'</style>\\n</head>',1)
 # Install in the established authenticated host, outside the nested card IIFE.
 html=once(html,
  'const se184CloudPreviews=new Map();',
  helpers+'\nconst se184CloudPreviews=new Map();',
  'helpers in authenticated closure')
 # Native loader verifies the exact same saved account bytes and link through
 # its existing path, but accepts a single trusted post-CAS in-memory result.
 html=once(html,
  "se183LoadStep(se183Ticket,'Downloading account project');const result=await window.SWYRL_ENGINE_PROJECT_LOAD_493.fetchProject(projectId,stage=>se183LoadStep(se183Ticket,stage));",
  "se183LoadStep(se183Ticket,'Downloading account project');const verified=se494TrustedLoadCache.get(projectId)||null;const result=verified||await window.SWYRL_ENGINE_PROJECT_LOAD_493.fetchProject(projectId,stage=>se183LoadStep(se183Ticket,stage));se494TrustedLoadCache.delete(projectId);",
  'use proven project only after acknowledged CAS')
 html=once(html,
  'async function updateSelectedModel(record,source,chosen,onProgress=()=>{}){',
  'async function updateSelectedModel(record,source,chosen,onProgress=()=>{},card=null,onStage=()=>{}){',
  'update callbacks')
 html=once(html,
  "  onProgress('Reading selected model or ZIP archive…');\n  const input=await se493ProjectLoad.parseModel(file,onProgress);\n  onProgress('Checking the currently saved project revision…');",
  "  onStage(0,'Opening ZIP or model JSON');\n  onProgress('Reading selected model or ZIP archive…');\n  await se494NextPaint();\n  const input=await se493ProjectLoad.parseModel(file,onProgress);\n  onStage(1,'Downloading account revision');\n  onProgress('Checking the currently saved project revision…');\n  await se494NextPaint();",
  'visible steps before read')
 html=once(html,
  "  onProgress('Validating mesh identity, topology, UVs and rig…');\n  const changed=sourceModel(input,doc,metadata,source);",
  "  onStage(2,'Checking mesh ID, UV and rig');\n  onProgress('Validating mesh identity, topology, UVs and rig…');\n  await se494NextPaint();\n  const changed=sourceModel(input,doc,metadata,source);",
  'explicit model validation stage')
 html=once(html,
  "  const next=structuredClone(doc);\n  next.project.modelAtelier=changed;",
  "  onStage(3,'Preserving previous revision');\n  await se494NextPaint();\n  const next=structuredClone(doc);\n  next.project.modelAtelier=changed;",
  'save preparation')
 html=once(html,
  "   const archived=(await revisions.prepare(doc,next,version,max)).payload;\n   const bytes=new TextEncoder().encode(JSON.stringify(archived));",
  "   onProgress('Archiving previous project revision (may require compression)…');\n   const archived=(await revisions.prepare(doc,next,version,max)).payload;\n   await se494NextPaint();\n   const bytes=new TextEncoder().encode(JSON.stringify(archived));",
  'responsive revision archiving')
 html=once(html,
  "   onProgress('Saving '+String(metadata.name||record.name)+' · expected revision '+version+'…');\n   let reply;",
  "   onStage(4,'Sending confirmed revision '+(version+1));\n   onProgress('Saving '+String(metadata.name||record.name)+' · expected revision '+version+'…');\n   await se494NextPaint();\n   // Keep an exact copy for the canonical loader before transfer detaches bytes.\n   const verifiedSnapshot=bytes.slice().buffer;\n   let reply;",
  'save and retain exact bytes')
 html=once(html,
  """   let refreshed=true;
   try{await se170Refresh();}
   catch{refreshed=false;}
   return 'Updated '+String(metadata.name||record.name)+' to revision '+reply.project.revision+
    (refreshed?'. If this project is open, reload it before saving more edits.':
      '. The save succeeded, but the project list could not refresh. Do NOT submit the same update again; reopen My Projects later.');""",
  """   // Do not re-fetch the list or download the just-uploaded 10+ MB scene.
   // Native loadCloud still enforces the dirty-scene confirmation and is
   // responsible for account links and rollback if the renderer rejects it.
   if(card)se494AfterCloudSave(card,record,reply);
   onStage(5,'Opening confirmed saved revision');
   let opened=false,openIssue='';
   try{opened=await se494OpenConfirmedCloud(id,reply.project,verifiedSnapshot,onProgress);}
   catch(error){openIssue=String(error?.message||error).slice(0,170);}
   return opened?'Updated and opened '+String(metadata.name||record.name)+' · revision '+reply.project.revision+'.':
    'Saved '+String(metadata.name||record.name)+' · revision '+reply.project.revision+
    ', but automatic open was not completed: '+(openIssue||'select Open project to retry.')+' No save retry is needed.';""",
  'confirmed write then in-memory canonical reopen')
 html=once(html,
  """  await se175Store([{...metadata,data:next,updatedAt:new Date().toISOString()}]);
  await revisions.recordLocal(id,next);
  await se175RefreshLocal();
  return 'Updated the same on-device project. Its previous model remains in local revision history.';""",
  """  onStage(4,'Saving local revision');
  await se175Store([{...metadata,data:next,updatedAt:new Date().toISOString()}]);
  await revisions.recordLocal(id,next);
  onStage(5,'Opening updated local scene');
  let opened=false,openIssue='';
  try{opened=await se494OpenConfirmedLocal(id,next,onProgress);}
  catch(error){openIssue=String(error?.message||error).slice(0,170);}
  if(!opened){await se175RefreshLocal().catch(()=>{});}
  return opened?'Updated and opened the same on-device project. Previous version preserved in local history.':
   'Saved updated local model, but automatic open was not completed. '+(openIssue||'Open project to retry.') ;""",
  'local update and auto-open')
 start=html.index('  let se491RetryFile=null;',html.index('se184ProjectCard=function(record,source){',html.index('function se491TransientRead') if 'function se491TransientRead' in html else 0))
 end=html.index('  actions.append(button);',start)
 old=html[start:end]
 assert old.count('button.onclick=async()=>')==1,old[:100]
 updated="""  let se491RetryFile=null;
  button.onclick=async()=>{
   if(button.disabled)return;
   button.disabled=true;
   const ui=se494UpdateSteps(card,status,button);
   let file=se491RetryFile;
   try{
    if(!file){
     ui.note('Choose a .swyrl.json or ZIP model update…');
     await se494NextPaint();
     file=await selectFile();
    }
    if(!file){ui.done('No changes made.',true);return;}
    const answer=await updateSelectedModel(record,source,file,
     message=>ui.note(message),card,(step,detail)=>ui.stage(step,detail));
    se491RetryFile=null;button.textContent='Update Model';
    ui.done(answer,true);
   }catch(error){
    const recoverable=error?.se491Recoverable===true;
    se491RetryFile=recoverable?file:null;
    button.textContent=recoverable?'Retry Update':'Update Model';
    ui.done('Update failed: '+msg(error),false);
   }finally{button.disabled=false;}
  };
"""
 html=html[:start]+updated+html[end:]
 # Inform Android picker about ZIPs; old wording survives earlier patch.
 html=once(html,"status.textContent='Select the extracted .swyrl.json model file…';","status.textContent='Choose ZIP or native model JSON…';","remove stale extraction hint") if "status.textContent='Select the extracted .swyrl.json model file…';" in html else html
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_493_PROJECT_LOAD_DIAGNOSTICS',MARKER),
  ('ENGINE · MAKER v11.493','ENGINE · MAKER v11.494'),
  ('v11.493 · verified ZIP detection and project load errors','v11.494 · staged model updates and immediate reopen'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.493'","window.SWRLZ_FORGE_BUILD={version:'v11.494'"),
  ('<title>§wyrl§ Engine · Maker v11.493</title>','<title>§wyrl§ Engine · Maker v11.494</title>')
 ):html=once(html,old,new,'release identity')
 prev=" source.engine='§wyrl§ Engine · Maker v11.493';source.version=11.493;"
 assert html.count(prev)==5,('provenance',html.count(prev))
 html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.494';source.version=11.494;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,length=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.493']
 notes['history'].insert(0,{'version':'v11.493','changes':notes.get('changes',[])})
 notes.update(version='v11.494',date='2026-11-17',title='Model update progress and verified immediate project reopen',
  changes=[
   'My Projects model update displays large active stage cues for ZIP read, saved project read, mesh validation, revision archiving, cloud commit and native scene opening, including elapsed time and explicit failure handling.',
   'After an account revision is durably confirmed, the existing authenticated canonical cloud loader opens the exact saved bytes already in memory, avoiding an unnecessary second download.',
   'The redundant account-project list refresh is removed from the success critical path. Account list cache is invalidated; the project card revision updates immediately.',
   'Opening a saved update uses the normal scene recovery, cloud link persistence and dirty-workspace confirmation. A save remains successful even if editor open is cancelled or fails.',
   'Local project updates also open the new scene after storing it and recording a revision. No scene is changed before the save is confirmed.',
   'Rigging, UVs, existing scene architecture, revision history, user project IDs and permission checks are retained.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
