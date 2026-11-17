"""§E v11.480: expose native guarded editable-topology conversion in viewport."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_480_EDITABLE_ENTRY'

def once(html,old,new):
 count=html.count(old)
 assert count==1,('v11.480 unique patch anchor',old[:125],count)
 return html.replace(old,new,1)

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_479_RIM_VISIBLE_SIDE' in html
 js=(ROOT/'runtime/model_editable_entry_v11_480.js').read_text('utf8')
 css=(ROOT/'runtime/model_editable_entry_v11_480.css').read_text('utf8')
 assert '/* SE480_EDITABLE_ENTRY_END */' in js
 assert '/* SE480_EDITABLE_ENTRY_STYLES_END */' in css
 html=once(html,'/* SE479_RIM_VISIBILITY_END */',
  '/* SE479_RIM_VISIBILITY_END */\n'+js)
 html=once(html,
  'Convert this mesh to editable topology before selecting a rim.',
  'This mesh needs editable topology for ring selection. Use the contextual Make mesh editable control; protected textured models explain why conversion is unavailable.')
 assert '</head>' in html
 html=html.replace('</head>','<style id="se480EditableEntryStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_479_RIM_VISIBLE_SIDE',MARKER),
  ('ENGINE · MAKER v11.479','ENGINE · MAKER v11.480'),
  ('v11.479 · rim-first and visible-side vertex editing','v11.480 · accessible editable mesh conversion'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.479'","window.SWRLZ_FORGE_BUILD={version:'v11.480'"),
  ('<title>§wyrl§ Engine · Maker v11.479</title>','<title>§wyrl§ Engine · Maker v11.480</title>')
 ):html=once(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.479';source.version=11.479;"
 assert html.count(prior)==5,('v11.480 provenance',html.count(prior))
 html=html.replace(prior,
  " source.engine='§wyrl§ Engine · Maker v11.480';source.version=11.480;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[item for item in notes.get('history',[]) if item.get('version')!='v11.479']
 notes['history'].insert(0,{'version':'v11.479','changes':notes.get('changes',[])})
 notes.update(version='v11.480',date='2026-11-16',
  title='Accessible Make mesh editable action during Vertex Ring/Extrude',
  changes=[
   'The progressive Extrude and Inset interface now has a context-aware Make mesh editable action directly under the selection strips in the viewport. The older Inset-only conversion CTA is unchanged.',
   'On a convertible native primitive, the action explicitly asks for confirmation that plain UVs are regenerated, then uses the existing native convert transaction with built-in validation and Undo.',
   'The converter returns to the selected progressive component type (including Vertex Ring or Ring Fill), so the user can immediately select real editable topology without resetting modeling state.',
   'When the selected model has protected UV/paint, authored geometry, rigging or other unsupported data, the action is disabled and its native reason shown; the decorated source is not altered.',
   'The contextual action hides once a topology mesh is ready. The viewport, inspector, model parts, materials, Undo, previews and VR ownership remain unchanged.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
