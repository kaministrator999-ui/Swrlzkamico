"""§E v11.528: original WebXR project dialog, rest pose, ray gizmos,
contextual +/- toolbars, left Menu (where browser exposes it), account saves.
Adds no second XR scene, OAuth flow or model editor.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_528_IMMERSIVE_UX_ACCOUNT_REPAIR'
def one(s,a,b,reason):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.528',reason,n,a[:160]))
 return s.replace(a,b,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_527_DRAW_MENU_CLEANUP' in html
 paths=[
  ('runtime/model_vr_project_dialog_v11_528.js',
   '/* SE517_XR_PROJECT_BROWSER_END */','immersive project dialog'),
  ('runtime/model_vr_ray_controls_v11_528.js',
   '/* SE517_XR_PROJECT_BROWSER_END */','native ray/menu/parameter extensions'),
  ('runtime/model_account_project_repair_v11_528.js',
   '/* SE372_VR_PROJECTS_IN_CHAT_CLOSURE_END */','authenticated account save bridge')
 ]
 for path,anchor,reason in paths:
  script=(ROOT/path).read_text('utf8')
  html=one(html,anchor,anchor+'\n'+script,reason)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_527_DRAW_MENU_CLEANUP',MARKER),
  ('ENGINE · MAKER v11.527','ENGINE · MAKER v11.528'),
  ('v11.527 · contextual immersive Draw tools, global history only',
   'v11.528 · immersive project dialog, ray transforms, rest pose, controls and account saves'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.527'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.528'"),
  ('<title>§wyrl§ Engine · Maker v11.527</title>',
   '<title>§wyrl§ Engine · Maker v11.528</title>')
 ):html=one(html,old,new,'release identity')
 old=" source.engine='§wyrl§ Engine · Maker v11.527';source.version=11.527;"
 if html.count(old)!=5:raise AssertionError(('v11.528 provenance',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.528';source.version=11.528;")
 tag='const SE_RELEASE_NOTES=';at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.527']
 notes['history'].insert(0,{'version':'v11.527','changes':notes.get('changes',[])})
 notes.update(version='v11.528',date='2026-11-19',
  title='Immersive Projects and native interaction repairs',
  changes=[
   'Projects opens a spacious native 3D card dialog instead of the cramped operation list, with existing Device, Account and Starter project selection, navigation, Open, Refresh, Save, Clone and safe close.',
   'A posed skinned mesh that refuses immersive Push/Pull offers Set Rest Pose or Keep Pose, recording the neutral reset in the original rig history before retrying manually.',
   'Native Move/Rotate/Scale gizmo Trigger captures now follow the tracked controller ray in an appropriate plane; the existing validated group transaction, Preview, B cancel and release commit remain.',
   'Related native plus/minus modifiers are grouped into an adjacent labeled parameter toolbar; original duplicate controls are hidden only when a real pair is present.',
   'Quest left controller Menu toggles the existing tool menu when Meta Quest Browser exposes the button as gamepad input; X remains fallback if the browser reserves it.',
   'Both Chat panel and My Projects Save to account use the same authenticated, durable native cloud bridge, with stable project IDs, explicit failure messages and normalized Account project IDs for loading.',
   'No new cloud storage service, authentication token transfer, duplicate XR dispatcher, editor or renderer. Meta Quest hardware and signed-in account acceptance remain pending.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
