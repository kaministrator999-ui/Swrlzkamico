"""§E v11.493: file-signature ZIP import + explicit safe account load diagnosis."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_493_PROJECT_LOAD_DIAGNOSTICS'
def once(h,old,new,label):
 n=h.count(old)
 if n!=1:raise AssertionError(('v11.493 anchor',label,n,old[:120]))
 return h.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_492_ZIP_MODEL_UPDATES' in html
 js=(ROOT/'runtime/project_load_diagnostics_v11_493.js').read_text('utf8')
 assert 'SWYRL_ENGINE_PROJECT_LOAD_493' in js
 # Scoped to the existing authenticated host and Update Model closure.
 html=once(html,'const se491TransientRead = error =>',js+'\nconst se491TransientRead = error =>','install native helper')
 html=once(html,'const input=await se492ModelUpload.parse(file,onProgress);',
   'const input=await se493ProjectLoad.parseModel(file,onProgress);','read ZIP by signature')
 # Make the genuine loader's error visible to its selected account card.
 html=once(html,
   "  if(dirty&&!window.confirm('Load this account project and replace unsaved local changes? Save the current project first if you want to keep them.'))return;",
   "  window.SWYRL_ENGINE_PROJECT_LOAD_493.reset();\n  if(dirty&&!window.confirm('Load this account project and replace unsaved local changes? Save the current project first if you want to keep them.')){window.SWYRL_ENGINE_PROJECT_LOAD_493.failure(Error('Open cancelled to preserve unsaved changes.'));return false;}",
   'distinguish cancelled load')
 html=once(html,
   "se183LoadStep(se183Ticket,'Downloading account project');const result=await rpc('cloud.load',{projectId});",
   "se183LoadStep(se183Ticket,'Downloading account project');const result=await window.SWYRL_ENGINE_PROJECT_LOAD_493.fetchProject(projectId,stage=>se183LoadStep(se183Ticket,stage));",
   'retry only cloud load reads')
 html=once(html,
   "  }catch(error){setStatus('Account load failed: '+error.message,true);}finally{cloudBusy=false;se183FinishLoad(se183Ticket,se183Opened,se183Opened?'Account project ready':'Account project load failed');}",
   "  }catch(error){window.SWYRL_ENGINE_PROJECT_LOAD_493.failure(error);setStatus('Account load failed: '+window.SWYRL_ENGINE_PROJECT_LOAD_493.getError(),true);}finally{cloudBusy=false;se183FinishLoad(se183Ticket,se183Opened,se183Opened?'Account project ready':'Account project load failed');}",
   'surface exact cloud failure')
 html=once(html,
   "    else result.textContent='Could not open project. Your active scene was preserved.';",
   "    else result.textContent='Could not open project: '+(window.SWYRL_ENGINE_PROJECT_LOAD_493?.getError()||'see § Chat account status')+'. Your active scene was preserved.';",
   'show reason on selected card')
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_492_ZIP_MODEL_UPDATES',MARKER),
  ('ENGINE · MAKER v11.492','ENGINE · MAKER v11.493'),
  ('v11.492 · direct ZIP model updates','v11.493 · verified ZIP detection and project load errors'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.492'","window.SWRLZ_FORGE_BUILD={version:'v11.493'"),
  ('<title>§wyrl§ Engine · Maker v11.492</title>','<title>§wyrl§ Engine · Maker v11.493</title>')
 ): html=once(html,old,new,'runtime identity')
 previous=" source.engine='§wyrl§ Engine · Maker v11.492';source.version=11.492;"
 if html.count(previous)!=5:raise AssertionError(('source provenance',html.count(previous)))
 html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.493';source.version=11.493;")
 marker='const SE_RELEASE_NOTES=';start=html.index(marker)+len(marker)
 notes,length=json.JSONDecoder().raw_decode(html[start:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.492']
 notes['history'].insert(0,{'version':'v11.492','changes':notes.get('changes',[])})
 notes.update(version='v11.493',date='2026-11-17',
   title='Accurate ZIP detection and cloud project open diagnostics',
   changes=[
    'The selected Update Model file is inspected for ZIP signatures independently of its Android content-provider filename, preventing binary PK headers from being parsed as JSON.',
    'Opening a saved My Projects cloud project retries only transient read errors before any scene import, with verified server project ID and no automatic writes.',
    'The selected cloud card shows the exact underlying load error rather than a generic failure while preserving the active workspace.',
    'Cancelling an unsaved-changes warning is correctly reported as cancellation rather than project corruption.',
    'No account project revision, user mesh, UV layout, rig, animation, local project history or credentials are changed by this release.'
   ])
 return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[start+length:]
