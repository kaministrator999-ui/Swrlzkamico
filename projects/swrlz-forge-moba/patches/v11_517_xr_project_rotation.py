"""§E v11.517 — original QA #5 and #7.
Camera/model transform isolation and native three-stage VR project browsing.
No new XR menu, controller dispatch loop, OAuth path or project schema.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_517_XR_PROJECTS_ROTATION'
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.517',label,n,old[:120]))
 return s.replace(old,new,1)
def edit_section(html,start,end,fn):
 a=html.index(start);b=html.index(end,a)
 return html[:a]+fn(html[a:b])+html[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_516_RIG_PRECISION' in html
 project=(ROOT/'runtime/model_vr_project_library_v11_517.js').read_text('utf8')
 xr=(ROOT/'runtime/model_vr_project_browser_v11_517.js').read_text('utf8')
 assert 'SE517_PROJECT_LIBRARY_END' in project
 assert 'SE517_XR_PROJECT_BROWSER_END' in xr
 # Stay in the existing authenticated §Chat closure. Do not duplicate OAuth.
 html=one(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
  project+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
  'existing account bridge extension')
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
  xr+'\ninstallPerformanceSettings();se189InstallPerfUI();','existing XR scene extension')
 def stage(s):
  s=one(s,"function setCategory(action){",
    "function setCategory(action){\n    if(action==='projects')se517XRProjects.start();",
    'init project listing through native category')
  s=one(s,"const options=presets[category]||[];",
    "const options=category==='projects'?se517XRProjects.operations():presets[category]||[];",
    'dynamic project rows in current submenu')
  s=one(s,"let detailPage='tools',lastState=null,lastHover=null,disposed=false;",
    "let detailPage='tools',lastState=null,lastHover=null,disposed=false,lastProjectRevision=-1;",
    'project row revision state')
  s=one(s,"function update(next){\n    lastState=next||{};",
    """function update(next){
    lastState=next||{};
    if(category==='projects'&&next?.projectBrowserRevision!==lastProjectRevision){
     lastProjectRevision=next?.projectBrowserRevision??0;
     const options=se517XRProjects.operations();
     for(let i=0;i<submenuRows.length;i++){
      const item=submenuRows[i],entry=options[i];
      item.action=entry?.[0]||'';item.label=entry?.[1]||'';
      item.mesh.userData.se340Action=item.action||null;
      item.mesh.visible=!!item.action;item.paint();
     }
    }""",
    'refresh native list names without new panel or event ownership')
  s=one(s,"if(action.startsWith('save-')||action==='projects'||action==='clone-project')return 'projects';",
    "if(action.startsWith('project-')||action.startsWith('save-')||action==='projects'||action==='clone-project')return 'projects';",
    'projects choose existing left settings')
  return s
 html=edit_section(html,'/* SE445_VR_PROGRESSIVE_TOOLS_START','/* SE445_VR_PROGRESSIVE_TOOLS_END',stage)
 # The same frame state already drives the native UI. Only its revision changes
 # when a project list is fetched, selected, paged or confirmed.
 html=one(html,'mode:s.mode,selectedName:selected?.name||',
  'mode:s.mode,projectBrowserRevision:se517XRProjects.inspect().revision,selectedName:selected?.name||',
  'existing XR UI redraw on catalog change')
 html=one(html,'const bridge=se340Bridge(),native=bridge.inspect();',
  '''if(s.se517ProjectBusy){renderer.render(s.scene,s.camera);return;}
  const bridge=se340Bridge(),native=bridge.inspect();''',
  'do not trigger XR auto-exit during owned asynchronous document switch')
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_516_RIG_PRECISION',MARKER),
  ('ENGINE · MAKER v11.516','ENGINE · MAKER v11.517'),
  ('v11.516 · precise per-vertex and region rig weight editing',
   'v11.517 · native VR project browser and isolated object rotation'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.516'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.517'"),
  ('<title>§wyrl§ Engine · Maker v11.516</title>',
   '<title>§wyrl§ Engine · Maker v11.517</title>')
 ]:html=one(html,old,new,'runtime identity')
 previous=" source.engine='§wyrl§ Engine · Maker v11.516';source.version=11.516;"
 if html.count(previous)!=5:raise AssertionError(('v11.517 provenance',html.count(previous)))
 html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.517';source.version=11.517;")
 marker='const SE_RELEASE_NOTES=';at=html.index(marker)+len(marker)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.516']
 notes['history'].insert(0,{'version':'v11.516','changes':notes.get('changes',[])})
 notes.update(version='v11.517',date='2026-11-18',
  title='Immersive VR project library and object-versus-camera rotation isolation',
  changes=[
   'Issue #5: the existing native Rotate mode now requires a selected model. A rotation gesture guards the camera orbit yaw/pitch against inadvertent changes. Right-stick orbit remains a separate camera/reference-space operation whenever no model transform is active; only selected authored part TRS commits.',
   'Issue #7: the established far-right Projects category and middle 11-slot operation list now display on-device, signed-in Google and Model Atelier starter project names. Previous/Next page, row selection, Open and Cancel run through the same native hit-testing, Trigger/Grip pipeline and spatial menu.',
   'Unsaved edits require an explicit confirm action. The existing IndexedDB/Google project service creates a new independently named local recovery copy before every project switch, validates saved model documents and account access, and restores the prior project if loading fails.',
   'Successful project transitions release and reborrow the existing Model Atelier root inside the SAME active WebXR session; source/project token, display cache, hover meshes, pose view and model bounds are refreshed without a new VR renderer, login popup or second menu.',
   'Quest physical acceptance remains required for project switching, project-specific asset loading, recovery scenarios and rotation controls. Other open QA categories retain their original scope.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
