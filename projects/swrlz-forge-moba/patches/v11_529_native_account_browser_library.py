"""§E v11.529 — one native full-project cloud save and clean browser My Projects.

Append-only patch. No new Google auth or cloud datastore. In model studio,
v11.488 deliberately redirects saveCloud() to asset saving; the *project*
buttons must bypass that path through the preserved v11.371 native project
save facade with revision validation. Keep standalone asset saving unchanged.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_529_NATIVE_ACCOUNT_BROWSER_LIBRARY'
def one(html,old,new,reason):
 count=html.count(old)
 if count!=1:raise AssertionError(('v11.529',reason,count,old[:130]))
 return html.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_528_IMMERSIVE_UX_ACCOUNT_REPAIR' in html
 account=(ROOT/'runtime/project_account_save_v11_529.js').read_text('utf8')
 ui=(ROOT/'runtime/project_library_browser_ui_v11_529.js').read_text('utf8')
 css=(ROOT/'runtime/project_library_browser_ui_v11_529.css').read_text('utf8')
 for token in ('se371PreviousSaveCloud()','se488EnsureProjectNameForAccount',
               'se529SaveNativeProjectToAccount','se529ProjectSaveResult'):
  assert token in account,token
 for token in ('se529PolishLibrary','se184ProjectCard=function',
               'se529-card-more','se529LibraryHero','se529Advanced'):
  assert token in ui,token
 # Both account and My Projects implementations MUST execute in the original
 # authenticated Chat-host closure, with access to its existing private RPC,
 # stable account identity, project guard and local snapshot functions.
 anchor='/* SE528_ACCOUNT_PROJECT_REPAIR_END */'
 html=one(html,anchor,anchor+'\n'+account+'\n'+ui,
          'project-account bridge and native browser gallery')
 html=one(html,'</head>','<style id="se529NativeProjectLibrary">\n'+css+
    '\n</style>\n</head>','scoped responsive CSS')
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_528_IMMERSIVE_UX_ACCOUNT_REPAIR',MARKER),
  ('ENGINE · MAKER v11.528','ENGINE · MAKER v11.529'),
  ('v11.528 · immersive project dialog, ray transforms, rest pose, controls and account saves',
   'v11.529 · native account-save routing and professional browser My Projects'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.528'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.529'"),
  ('<title>§wyrl§ Engine · Maker v11.528</title>',
   '<title>§wyrl§ Engine · Maker v11.529</title>')
 ):html=one(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.528';source.version=11.528;"
 if html.count(old)!=5:raise AssertionError(('v11.529 source provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.529';source.version=11.529;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.528']
 notes['history'].insert(0,{'version':'v11.528','changes':notes.get('changes',[])})
 notes.update(version='v11.529',date='2026-11-19',
  title='Complete native cloud-project saves and unified My Projects browser library',
  changes=[
   'Save to Account from §wyrlz Chat, browser My Projects and immersive VR saves the complete independent project through the original v11.371 version-checked native cloud RPC, never the separate Model Studio asset save route.',
   'The result must show durable cloud revision evidence. Account failures remain failures with readable source errors; local saves are never mislabeled account success.',
   'Independent starter identity and project naming are preserved before cloud save; the standalone Model/Particle asset library remains unchanged.',
   'Browser My Projects has one responsive top action bar (Save to Account, Save on Device, Refresh), a connected-account indicator and accurate local/cloud project counts.',
   'The original on-device and account project card galleries retain Open, Preview, default project, and their original event handlers. Delete, Export Project, Export Model Update and Update Model move into per-card More actions without duplicated primary rows.',
   'Advanced tools retain native Revision History, Clone, export/update and local-list controls in a collapsible panel. Repeated save/refresh/sign-in controls are hidden only within the browser My Projects tab.',
   'New UI and cloud-save routing are scoped to browser My Projects and the existing authenticated project bridge. Immersive WebXR native menu, model geometry, textures, UVs, rig and project history stay unchanged.',
   'Authenticated cloud write/reopen and owner screenshot verification still require user acceptance.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
