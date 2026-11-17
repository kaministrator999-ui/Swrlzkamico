"""§E v11.482: geometric circular vertex rings, draggable height, focused vertex inspector."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_482_GEOMETRIC_RING_HEIGHT'

def once(html,old,new):
 n=html.count(old)
 assert n==1,('v11.482 source anchor',old[:150],n)
 return html.replace(old,new,1)

def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_481_TEXTURED_EDITABLE_COPY' in html
 circle=(ROOT/'runtime/model_geometric_ring_v11_482.js').read_text('utf8')
 layout=(ROOT/'runtime/model_ring_height_layout_v11_482.js').read_text('utf8')
 css=(ROOT/'runtime/model_ring_height_layout_v11_482.css').read_text('utf8')
 assert '/* SE482_GEOMETRIC_RING_END */' in circle
 assert '/* SE482_RING_HEIGHT_LAYOUT_END */' in layout
 assert '/* SE482_RING_HEIGHT_LAYOUT_STYLES_END */' in css
 html=once(html,'/* SE481_TEXTURED_EDITABLE_COPY_END */',
  '/* SE481_TEXTURED_EDITABLE_COPY_END */\n'+circle+'\n'+layout)
 # Replace the old projected radial distance with object-local geometric
 # distance. The EXISTING visible-only ray test and highlighted IDs still own
 # the final selection; no new mesh, material, Undo, or selection controller.
 html=once(html,
  """  const calculated=se479ProjectedRim.choose(projected,edges,slot,
   [screenCenter.x,screenCenter.y],shape==='ring'?'outline':'fill');""",
  """  const calculated=se482GeometricRing.choose(top,mesh.geometry,slot,{
   kind:'rim',mode:shape==='ring'?'outline':'fill',
   plane:panel?.querySelector('#se466RingPlane')?.value||'xz'
  });""")
 html=once(html,
  """  atelierComponentMode='vertex';atelierComponentPartId=selection;
  atelierComponentIds=ids;atelierComponentGesture=null;atelierComponentDrag=null;
  atelierComponentRefresh();""",
  """  atelierComponentMode='vertex';atelierComponentPartId=selection;
  atelierComponentIds=ids;atelierComponentGesture=null;atelierComponentDrag=null;
  se482GeometricRing.noteRim(slot);
  atelierComponentRefresh();""")
 # Center mode also uses an actual Euclidean circle rather than the old
 # graph edge-step boundary. Keep its native anchor for compatibility.
 html=once(html,
  """  const result=workshop()?.selectRing?.(options(mode));""",
  """  const result=se482GeometricRing.selectCenter(slot,options(mode));""")
 # Preserve existing history-capable slider; change only viewport positioning
 # and hide Face controls when operating on vertices.
 html=html.replace('</head>',
  '<style id="se482GeometricRingHeightStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in (
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_481_TEXTURED_EDITABLE_COPY',MARKER),
  ('ENGINE · MAKER v11.481','ENGINE · MAKER v11.482'),
  ('v11.481 · texture-preserving editable working copies','v11.482 · geometric rings and draggable height'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.481'","window.SWRLZ_FORGE_BUILD={version:'v11.482'"),
  ('<title>§wyrl§ Engine · Maker v11.481</title>','<title>§wyrl§ Engine · Maker v11.482</title>')
 ):html=once(html,old,new)
 old=" source.engine='§wyrl§ Engine · Maker v11.481';source.version=11.481;"
 assert html.count(old)==5
 html=html.replace(old,
  " source.engine='§wyrl§ Engine · Maker v11.482';source.version=11.482;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,size=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.481']
 notes['history'].insert(0,{'version':'v11.481','changes':notes.get('changes',[])})
 notes.update(version='v11.482',date='2026-11-16',
  title='True geometric circle selection, draggable Ring Height, vertex-first tools',
  changes=[
   'Vertex Ring follows an actual constant-radius circle measured in the chosen local mesh plane, not an arbitrary graph-step path. Filled Ring selects the geometric interior while the existing visibility picker filters hidden back surfaces.',
   'Tapping a vertex on a rim uses its distance from the mesh center; the explicit Set Ring Center mode creates a Euclidean-radius circle around the chosen vertex.',
   'Circle band width is adjustable for irregular ring geometry. Native vertex selections include UV seam variants and keep the original painted material visible.',
   'Ring Height is a compact, touch-sized, keyboard-accessible draggable viewport panel; preview, Cancel, Apply and the original native Undo transaction remain unchanged.',
   'The right inspector hides inactive Face tools when working in Vertex mode, opens the applicable vertex circle options and retains Face tools when switched to Face mode.',
   'Browser regression verifies correct circular geometry on the painted mesh, selected vertex highlights, Ring Height preview and actual selected-vertex movement without changing UV coordinates.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
