"""§E v11.518 — Quest WebXR rig scope, chosen-project resume, revision cache.
Append-only hotfix for regression first observed on Quest 2 after v11.517.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_518_QUEST_RIG_CACHE'
def one(s,old,new,label):
 count=s.count(old)
 if count!=1:raise AssertionError(('v11.518',label,count,old[:110]))
 return s.replace(old,new,1)
def section(html,start,end,edit):
 a=html.index(start);b=html.index(end,a)
 return html[:a]+edit(html[a:b])+html[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_517_XR_PROJECTS_ROTATION' in html
 native=(ROOT/'runtime/model_rig_scope_access_v11_518.js').read_text('utf8')
 cache=(ROOT/'runtime/engine_cloud_revision_cache_v11_518.js').read_text('utf8')
 assert 'SE518_RIG_SCOPE_ACCESS_END' in native
 assert 'SE518_REVISION_CACHE_END' in cache
 # Native se220 variables live INSIDE Model Atelier, not in the outer WebXR
 # script. Give XR a narrow getter/setter API without moving/hiding the
 # existing 514/515/516 menu and input handlers or creating a second rig.
 html=one(html,"window.SWYRL_ENGINE_MODEL_WORKSPACE_490=se490Workspace;",
  "window.SWYRL_ENGINE_MODEL_WORKSPACE_490=se490Workspace;\n"+native,
  'native private rig bridge before Model Atelier closure returns')
 def vr(s):
  aliases="""
(function se518NativeRigClosure(){
 const se518RigAPI=()=>window.SWYRL_ENGINE_MODEL_RIG_ACCESS_518;
 const se220RigAvailable=()=>se518RigAPI().available();
 const se220Rig=()=>se518RigAPI().rig();
 const se220R=id=>se518RigAPI().element(id);
 const se220RigJointUI=()=>se518RigAPI().jointUI();
 const se220RigPose=pose=>se518RigAPI().pose(pose);
 const se220RigRemember=()=>se518RigAPI().remember();
 const se220RigTouched=msg=>se518RigAPI().touched(msg);
 const se220RigValidate=rig=>se518RigAPI().validate(rig);
 const partById=id=>se518RigAPI().part(id);
 const checkpoint=()=>se518RigAPI().checkpoint();
"""
  # Replace only the private variable names with live accessors. Never copy
  # stale initial bone/root data: every model switch can create a new rig.
  for old,replacement in [
   ('se220Bones','se518RigAPI().bones'),('se220Skeleton','se518RigAPI().skeleton'),
   ('modelRoot','se518RigAPI().root'),('se220Joint','se518RigAPI().joint'),
   ('se220Playing','se518RigAPI().playing'),
   ('se220PoseHistory','se518RigAPI().poseHistory')]:
   s=re.sub(r'\b'+old+r'\b',replacement,s)
  return aliases+s+'\n})();\n'
 html=section(html,'/* SE514_NATIVE_XR_RIG_START','/* SE514_NATIVE_XR_RIG_END */',lambda s:vr(s))
 # Embed the version-checked account cache within the existing verified
 # account closure, after previous credential-free §E project helpers.
 html=one(html,'/* SE517_PROJECT_LIBRARY_END */',
  '/* SE517_PROJECT_LIBRARY_END */\n'+cache,'account project cache in trusted project-service scope')
 def bridge(s):
  return one(s,'return (await loadCloud(id))===true;',
   'return (await se518CloudCache.load(id))===true;','first-paint resume uses verified cache')
 html=section(html,'/* SE476_ACCOUNT_BRIDGE_START','/* SE476_ACCOUNT_BRIDGE_END */',bridge)
 def xrproject(s):
  return one(s,'const loaded=await loadCloud(key);',
   'const loaded=await se518CloudCache.load(key);','VR project switch can reuse cached account content')
 html=section(html,'/* SE517_PROJECT_LIBRARY_START','/* SE517_PROJECT_LIBRARY_END */',xrproject)
 # My Projects must preserve the EXPLICIT user-picked default. Merely
 # refreshing a list never changes the preference; only real change events.
 html=one(html,"cloudList.addEventListener('change',se176UpdateLoadButton);",
  """cloudList.addEventListener('change',()=>{
     se176UpdateLoadButton();
     const match=/^(local|cloud):(.{1,160})$/.exec(cloudList.value||'');
     if(match)window.SWYRL_ENGINE_SAVED_DEFAULT?.set?.(match[1],match[2]);
    });""",'remember selected My Projects picker item across sessions')
 html=one(html,'    await loadCloud();\n    await se176RefreshProjects();',
  """    const loaded=await se518CloudCache.load(choice.slice(6));
    if(!loaded)setStatus('Account project could not be loaded; current workspace preserved.',true);
    await se176RefreshProjects();""",'picker cloud load reuses verified cache')
 # Earlier project card revisions may inline a differently named loader;
 # the authenticated startup and My Projects selected-project handler are
 # the stable v11.518 integration points. Do not patch an absent card call.
 if html.count('const ok=await loadCloud(id);')==1:
  html=one(html,'const ok=await loadCloud(id);',
   'const ok=await window.SWYRL_ENGINE_CLOUD_CACHE_518.load(id);',
   'optional legacy My Projects card')
 html=one(html,
  """    const choice=defaults();
    if(choice)void openSelected(choice);""",
  """    const choice=chosenRow()||defaults();
    if(choice)void openSelected(choice);""",
  'honor manually selected startup gate item before automatic fallback')
 html=one(html,
  """   $('se476Remember').checked=!!chosen&&pref?.source===chosen.source&&pref?.id===chosen.id;
   });""",
  """   if(chosen)window.SWYRL_ENGINE_SAVED_DEFAULT?.set?.(chosen.source,chosen.id);
   $('se476Remember').checked=!!chosen&&
    window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.()?.source===chosen.source&&
    window.SWYRL_ENGINE_SAVED_DEFAULT?.read?.()?.id===chosen.id;
   });""",
  'startup project selection is the project to restore next time')
 # On a successful cached cloud read, local loader stamps a local session ID.
 # The cache changes that back to the remote ID after authorized validation.
 # Previous start app and selected studio continue to govern camera restore.
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_517_XR_PROJECTS_ROTATION',MARKER),
  ('ENGINE · MAKER v11.517','ENGINE · MAKER v11.518'),
  ('v11.517 · native VR project browser and isolated object rotation',
   'v11.518 · Quest native rig scope, selected project resume and revision-aware cache'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.517'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.518'"),
  ('<title>§wyrl§ Engine · Maker v11.517</title>',
   '<title>§wyrl§ Engine · Maker v11.518</title>')
 ]:html=one(html,old,new,'version identity')
 before=" source.engine='§wyrl§ Engine · Maker v11.517';source.version=11.517;"
 assert html.count(before)==5,('native provenance',html.count(before))
 html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.518';source.version=11.518;")
 marker='const SE_RELEASE_NOTES=';at=html.index(marker)+len(marker)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.517']
 notes['history'].insert(0,{'version':'v11.517','changes':notes.get('changes',[])})
 notes.update(version='v11.518',date='2026-11-18',
  title='Quest immersive VR startup recovery and versioned account project cache',
  changes=[
   'Fix the reproducible Quest Model VR start failure se220RigAvailable is not defined: the existing native rig extension can now access valid rig state through a scope-safe Model Atelier bridge, not unrelated top-level identifiers. Rigging actions, controller labels and three-stage WebXR menus remain original.',
   'The My Projects selection and startup project picker now preserve the user-selected device/account project as the next session default instead of silently falling back to an unrelated starter or overwriting the choice during account synchronization.',
   'Authenticated cloud project loads first fetch lightweight account revision metadata; when an IndexedDB copy for that exact remote project ID and revision exists, open that verified local copy with the existing guarded native loader. Otherwise download updated account data normally and remember the new local mirror.',
   'Original on-device project saves, Google session verification, source revisions, conflict protection, selection state, and independent starter cloning remain intact. Never cache Google secrets in localStorage; do not trust an account project cache with missing or stale revision.',
   'Physical Quest 2 testing is still required for immersive entry, selected project persistence, first-download/cache-hit behavior and signed-in revision changes.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
