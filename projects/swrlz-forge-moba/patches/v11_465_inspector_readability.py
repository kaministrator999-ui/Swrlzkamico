"""§E v11.465 — native inspector readability without width/geometry rewrites."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_465_INSPECTOR_READABILITY'
def one(html,old,new):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.465 source anchor drift',old[:150],n))
 return html.replace(old,new,1)
def apply(html):
 js=(ROOT/'runtime/model_inspector_readability_v11_465.js').read_text('utf8')
 css=(ROOT/'runtime/model_inspector_readability_v11_465.css').read_text('utf8')
 assert js.startswith('/* SE465_NARROW_INSPECTOR_START */')
 assert js.rstrip().endswith('/* SE465_NARROW_INSPECTOR_END */')
 assert css.startswith('/* SE465_NARROW_INSPECTOR_STYLES_START */')
 # Source bridge lives in same ModelAtelier closure as v11.464; the original
 # inspector, Expand/Dock handlers, drag grips and selection events survive.
 html=one(html,'/* SE464_MODEL_VISUAL_POLISH_END */',
  '/* SE464_MODEL_VISUAL_POLISH_END */\n'+js)
 html=html.replace('</head>',
  '<style id="se465InspectorReadabilityStyles">\n'+css+'\n</style>\n</head>',1)
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_464_MODEL_VISUAL_INSPECTOR',MARKER)
 html=one(html,'/* SE465_NARROW_INSPECTOR_END */',
  '/* SE465_NARROW_INSPECTOR_END */\n'
  '/* Historical v11.464 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_464_MODEL_VISUAL_INSPECTOR */')
 for old,new in [
  ('ENGINE · MAKER v11.464','ENGINE · MAKER v11.465'),
  ('v11.464 · modeling depth and inspector focus','v11.465 · readable mobile inspector'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.464'","window.SWRLZ_FORGE_BUILD={version:'v11.465'"),
  ('<title>§wyrl§ Engine · Maker v11.464</title>','<title>§wyrl§ Engine · Maker v11.465</title>')
 ]:html=one(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.464';source.version=11.464;"
 assert html.count(old)==5,('v11.465 provenance count',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.465';source.version=11.465;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.464']
 notes['history'].insert(0,{'version':'v11.464','changes':notes.get('changes',[])})
 notes.update(version='v11.465',date='2026-11-15',
  title='Readable mobile inspector and reliable Expand/Dock track',
  changes=[
   'The existing right inspector no longer breaks tool names into individual letters: label wrapping respects word boundaries in docked and expanded layouts.',
   'At very narrow manually dragged widths, tool content temporarily condenses into a clear Expand prompt while its original DOM elements and native events remain mounted. Dragging wider or tapping Expand restores full controls.',
   'The Expand overlay now releases the actual native right-hand dock grid column on coarse pointer/mobile desktop-style layouts; Dock restores saved widths and the existing drag handles unchanged.',
   'Mesh selection, Undo/Redo, inset preview, all seven view modes, X-Ray, UVs, camera orbit, VR and project state remain owned by their existing native systems.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
