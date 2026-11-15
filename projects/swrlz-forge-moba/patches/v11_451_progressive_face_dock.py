"""§E v11.451: contextual Face → operation → modifier dock.

Moves the existing native workshop controls; it never duplicates mesh state,
selection authority, preview allocation, apply/undo, or camera gestures.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_451_PROGRESSIVE_FACE_DOCK'
def one(html,old,new):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.451 source anchor',old[:155],n))
 return html.replace(old,new,1)

def apply(html):
 js=(ROOT/'runtime/model_face_progressive_v11_451.js').read_text(encoding='utf8')
 css=(ROOT/'runtime/model_face_progressive_v11_451.css').read_text(encoding='utf8')
 assert js.startswith('/* SE451_FACE_PROGRESSIVE_DOCK_START */')
 assert js.rstrip().endswith('/* SE451_FACE_PROGRESSIVE_DOCK_END */')
 assert css.startswith('/* SE451_FACE_PROGRESSIVE_DOCK_CSS_START */')
 assert css.rstrip().endswith('/* SE451_FACE_PROGRESSIVE_DOCK_CSS_END */')
 # Preserve the prior release marker for source-level regression tests.
 # The latest deploy marker is the ONLY top-level release marker.
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_450_CAMERA_INSET_PREVIEW',MARKER)
 # The beginner layer owns the ONLY live native workshop. Hook its installer
 # after its declaration and before Model Studio is mounted by the UI.
 html=one(html,'/* SE430_MODEL_BEGINNER_UI_END */',
     '/* SE430_MODEL_BEGINNER_UI_END */\n'+
     '/* Previous verified behavior: SWYRL_ENGINE_DEPLOY_MARKER: V11_450_CAMERA_INSET_PREVIEW */\n'+js)
 html=one(html,'</head>','<style id="se451ProgressiveFaceDock">\n'+css+'\n</style>\n</head>')
 for before,after in [
  ('ENGINE · MAKER v11.450','ENGINE · MAKER v11.451'),
  ('v11.450 · stable dock zoom and visible Inset preview','v11.451 · contextual face tool drawers'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.450'","window.SWRLZ_FORGE_BUILD={version:'v11.451'"),
  ('<title>§wyrl§ Engine · Maker v11.450</title>','<title>§wyrl§ Engine · Maker v11.451</title>')
 ]:html=one(html,before,after)
 old=" source.engine='§wyrl§ Engine · Maker v11.450';source.version=11.450;"
 assert html.count(old)==5,('v11.451 engine provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.451';source.version=11.451;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.450']
 notes['history'].insert(0,{'version':'v11.450','changes':notes.get('changes',[])})
 notes.update(version='v11.451',date='2026-11-14',
  title='Contextual Face tools with compact Inset / Extrude modifier drawers',
  changes=[
   'The existing right-side primary modeling rail now opens a second Face operations drawer, followed by a third contextual settings drawer for Inset, Extrude, Solidify and Subdivide. Other tool categories retain their original editor and inspector.',
   'The existing native Make Editable, Select Region, Preview, Apply, Cancel and amount controls are reused with their original handlers, not duplicated. Choosing Inset/Extrude arms Face selection or previews the whole planar square directly through the existing v11.450 native workshop.',
   'Only operation-specific modifiers and Preview / Apply / Cancel remain visible in the settings drawer. Conversion follows existing source protection and confirmation; the original All face tools view is one tap away.',
   'The redundant full Inspector track collapses only during this Face workflow, enlarging the 3D viewport without triggering a global resize or changing saved dock widths. On compact phones, operation and modifier drawers occupy alternate overlay stages above the existing tool rail.',
   'The non-destructive geometry preview remains source-preserving; Apply is the sole mesh commit with native Undo, and closing is blocked while a preview is pending. Existing Face/Vertex/Edge selection, camera pinch/orbit, VR menus, projects and tool state remain native.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
