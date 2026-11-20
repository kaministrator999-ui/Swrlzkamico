"""§E v11.531 — native Quest menu, gizmo and account project corrective patch."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_530_QUEST_GIZMO_CONTROLLER_MENU'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_531_QUEST_MENU_GIZMO_ACCOUNT'
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.531',label,n,a[:90]))
 return s.replace(a,b,1)
def apply(html):
 assert OLD in html
 runtime=(ROOT/'runtime/model_vr_quest_interactions_v11_531.js').read_text('utf8')
 html=one(html,'/* SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END */',
  '/* SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END */\n'+runtime,
  'install corrective XR layer after v530')
 start=html.index('/* SE517_PROJECT_LIBRARY_START')
 end=html.index('/* SE517_PROJECT_LIBRARY_END',start)
 block=html[start:end]
 block=one(block,'  se175Transition=true;\n  try{',
  "  // loadCloud owns its own transition; never pre-lock the account loader.\n  se175Transition=source!=='cloud';\n  try{",'cloud transition')
 block=one(block,'}catch(error){online=false;}',
  "}catch(error){throw Error('Account project list failed: '+String(error?.message||error).slice(0,160));}",
  'visible account list failure')
 html=html[:start]+block+html[end:]
 for before,after in [
  (OLD,MARKER),
  ('ENGINE · MAKER v11.530','ENGINE · MAKER v11.531'),
  ('v11.530 · continuous immersive gizmos and left-hand tool console',
   'v11.531 · stable Quest menu, held-axis gizmos and cloud project open'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.530'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.531'"),
  ('<title>§wyrl§ Engine · Maker v11.530</title>',
   '<title>§wyrl§ Engine · Maker v11.531</title>')
 ]:html=one(html,before,after,'release identity')
 before=" source.engine='§wyrl§ Engine · Maker v11.530';source.version=11.530;"
 assert html.count(before)==5,('v531 provenance',html.count(before))
 html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.531';source.version=11.531;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.530']
 notes['history'].insert(0,{'version':'v11.530','changes':notes.get('changes',[])})
 notes.update(version='v11.531',date='2026-11-20',
  title='Quest VR menu stabilization, held-axis gizmo and account project load',
  changes=[
   'Immersive menu follows left controller translation without rotating with wrist pitch/roll; it remains upright and faces the headset.',
   'Existing native tool tiers are reflowed into adjacent panels, with Sculpt parameter controls beneath the modifier panel and no extra banner.',
   'Holding Trigger on a native X/Y/Z arrow continuously moves the selected mesh along that axis in either direction until release commits or B cancels.',
   'Cloud project load no longer takes the parent transition lock before invoking the account loader; account listing errors remain visible. Recovery copy remains.',
   'No new XR scene, cloud credentials, project data format or model-history authority.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
