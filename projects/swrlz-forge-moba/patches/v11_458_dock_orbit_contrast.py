"""§E v11.458: restore dock resizing, selected mesh contrast and true model orbit.

Only integrates with native state: the pre-existing splitter handler, renderer,
geometry/Undo owners and camera controls remain authoritative.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_458_DOCK_ORBIT_CONTRAST'

def one(src,old,new):
 n=src.count(old)
 if n!=1:raise AssertionError(('v11.458 anchor drift',old[:160],n))
 return src.replace(old,new,1)

def apply(html):
 js=(ROOT/'runtime/model_viewport_stability_v11_458.js').read_text('utf8')
 css=(ROOT/'runtime/model_viewport_stability_v11_458.css').read_text('utf8')
 assert js.startswith('/* SE458_MODEL_VIEWPORT_STABILITY_START */')
 assert js.rstrip().endswith('/* SE458_MODEL_VIEWPORT_STABILITY_END */')
 assert css.startswith('/* SE458_DOCK_AND_MODEL_CONTRAST_START */')

 # Hidden panels must stop taking the sizing budget. Existing native pointer
 # handlers stay in charge and persist exactly one drag result on pointerup.
 html=one(html,
  "if(d.left+d.right<=budget)return;\n const original=d.left+d.right;",
  """if(d.rightCollapsed){d.left=Math.max(145,Math.min(d.left,budget));return;}
 if(d.collapsed){d.right=Math.max(145,Math.min(d.right,budget));return;}
 if(d.left+d.right<=budget)return;
 const original=d.left+d.right;""")
 html=one(html,
  "return Math.max(145,Math.min(480,budget-state.model[side==='left'?'right':'left']));",
  """const other=side==='left'
  ?(state.model.rightCollapsed?0:state.model.right)
  :(state.model.collapsed?0:state.model.left);
 return Math.max(145,Math.min(480,budget-other));""")

 # Place dedicated module AFTER the already verified mesh, camera and view
 # definitions. Do not mutate source Three.js materials or create history.
 html=one(html,'/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */',
  '/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */\n'+js)
 html=one(html,'</head>','<style id="se458DockOrbitContrastStyles">\n'+css+'\n</style>\n</head>') if html.count('</head>')==1 else html.replace('</head>','<style id="se458DockOrbitContrastStyles">\n'+css+'\n</style>\n</head>',1)

 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_457_CONVERSION_NO_FACE_GATE',MARKER)
 html=one(html,'/* SE458_MODEL_VIEWPORT_STABILITY_END */',
  '/* SE458_MODEL_VIEWPORT_STABILITY_END */\n'
  '/* Historical v11.457 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_457_CONVERSION_NO_FACE_GATE */')
 for old,new in [
   ('ENGINE · MAKER v11.457','ENGINE · MAKER v11.458'),
   ('v11.457 · reliable editable cube conversion','v11.458 · stable model orbit and dock resizing'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.457'",
    "window.SWRLZ_FORGE_BUILD={version:'v11.458'"),
   ('<title>§wyrl§ Engine · Maker v11.457</title>','<title>§wyrl§ Engine · Maker v11.458</title>')
 ]:html=one(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.457';source.version=11.457;"
 assert html.count(prior)==5,('v11.458 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.458';source.version=11.458;")

 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.457']
 notes['history'].insert(0,{'version':'v11.457','changes':notes.get('changes',[])})
 notes.update(version='v11.458',date='2026-11-15',
  title='Model Studio dock resizing, clear edges and correct orbit focus',
  changes=[
   'Closing the right inspector now releases its desktop grid column instead of leaving a blank reserved track; reopening it restores the original width.',
   'The native splitter clamps ignore a collapsed opposing panel, so dragging remains effective. Pointer and keyboard handlers, persistence and ResizeObserver remain unchanged; the phone-sized drag target is wider.',
   'A selected model in Solid, Flat or Clay view gains a bounded dark angle-filtered edge overlay, with no internal quad diagonals. Preview geometry, authoring materials, saved UVs and Undo remain untouched; replaced helper geometry is disposed.',
   'After committing Inset or Extrude, the camera corrects an evidently detached orbit pivot to the selected mesh without changing the existing zoom, pitch or yaw. Ordinary close-range pans, framing tools and active previews are left alone.',
   'Existing native Face selection, guided conversion, Inset Rim/Depth Set, viewport mode switch, touch gestures and VR modeling architecture are preserved.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
