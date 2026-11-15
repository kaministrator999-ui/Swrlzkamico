"""§E v11.453: editable Inset rim width and visible coplanar inner border.

Single native source geometry/preview, no parallel document or history system.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_453_INSET_RIM_WIDTH'
def once(s,a,b):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.453 anchor',a[:170],n))
 return s.replace(a,b,1)

def apply(html):
 js=(ROOT/'runtime/model_rim_width_v11_453.js').read_text('utf8')
 css=(ROOT/'runtime/model_rim_width_v11_453.css').read_text('utf8')
 html=once(html,'/* SE452_NATIVE_FACE_FLYOUTS_END */',
           '/* SE452_NATIVE_FACE_FLYOUTS_END */\n'+js)
 html=html.replace('</head>','<style id="se453RimWidthStyles">\n'+css+'\n</style>\n</head>',1)
 # The old EdgesGeometry omitted coplanar seam edges. Draw the verified
 # connected inner loop, owned by the disposable preview record.
 html=once(html,
  "function restore(record){\n  se450PreviewOutlineClear(record);",
  "function restore(record){\n  se450PreviewOutlineClear(record);\n  window.se453RimBorderClear?.(record);")
 html=once(html,
  "se450PreviewOutlineClear(record);\n  record.operation=operation;",
  "se450PreviewOutlineClear(record);\n  window.se453RimBorderClear?.(record);\n  record.operation=operation;")
 html=once(html,
  "record.geometry=geometry;mesh.geometry=geometry;active=record;\n  se450PreviewOutlineAdd(record);",
  "record.geometry=geometry;mesh.geometry=geometry;active=record;\n  se450PreviewOutlineAdd(record);\n  window.se453RimBorderAdd?.(record);")
 for old,new in [
   ('SWYRL_ENGINE_DEPLOY_MARKER: V11_452_NATIVE_FACE_FLYOUTS',MARKER),
   ('ENGINE · MAKER v11.452','ENGINE · MAKER v11.453'),
   ('v11.452 · three-stage contextual Face flyouts','v11.453 · visible adjustable inset rim'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.452'","window.SWRLZ_FORGE_BUILD={version:'v11.453'"),
   ('<title>§wyrl§ Engine · Maker v11.452</title>','<title>§wyrl§ Engine · Maker v11.453</title>')
 ]:html=once(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.452';source.version=11.452;"
 assert html.count(old)==5,('v11.453 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.453';source.version=11.453;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[r for r in notes.get('history',[]) if r.get('version')!='v11.452']
 notes['history'].insert(0,{'version':'v11.452','changes':notes.get('changes',[])})
 notes.update(version='v11.453',date='2026-11-14',
  title='Visible rim and direct adjustable Inset border',
  changes=[
    'Inset now draws an explicit transient loop around the coplanar inner border. The former sharp-edge-only overlay omitted these edges, making an actual rim difficult to see.',
    'During an uncommitted Inset preview, a gold viewport handle drags toward the face center for a wider rim and outward for a narrower rim, using the same native Inset amount, preview, Apply, Cancel and one-step Undo.',
    'The Face modifier controls label the rim percentage and clarify that 20% inset corresponds to about 10% face width at each edge of a square.',
    'An inline Prepare rim button recovers valid selected face triangles after explicit conversion or vertex-edit bake, with confirmation for existing vertex edits. Painted or rigged protected parts remain guarded.',
    'No permanent helper geometry, duplicate mesh editor, camera reset, input ownership swap, or fabricated depth occurs; mobile, desktop and VR source controls remain preserved.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
