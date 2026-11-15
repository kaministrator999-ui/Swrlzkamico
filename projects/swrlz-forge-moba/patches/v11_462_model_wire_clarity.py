"""§E v11.462: readable clean topology wire, optional triangles, mobile viewport budget."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_462_WIRE_CLARITY_MOBILE'
def one(s,a,b):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.462 anchor drift',a[:140],n))
 return s.replace(a,b,1)
def apply(html):
 js=(ROOT/'runtime/model_wire_clarity_v11_462.js').read_text('utf-8')
 css=(ROOT/'runtime/model_wire_clarity_v11_462.css').read_text('utf-8')
 assert js.startswith('/* SE462_MODEL_WIRE_CLARITY_START */')
 assert js.rstrip().endswith('/* SE462_MODEL_WIRE_CLARITY_END */')
 assert css.startswith('/* SE462_VIEW_AND_DOCK_STYLES_START */')
 # Source-owned view extension within original ModelAtelier closure.
 html=one(html,'/* SE461_HARD_SURFACE_ORBIT_END */',
  '/* SE461_HARD_SURFACE_ORBIT_END */\n'+js)
 html=html.replace('</head>',
  '<style id="se462ViewAndDockStyles">\n'+css+'\n</style>\n</head>',1)
 # Existing native splitter budget had reserved just 190px for the viewport.
 # On a desktop-style mobile layout give it 35% (240-330px) instead.
 html=one(html,'return {width,rail,budget:Math.max(290,Math.floor(width-rail-190))};',
  'return {width,rail,budget:Math.max(290,Math.floor(width-rail-'
  'Math.max(240,Math.min(330,Math.round(width*.35)))))};')
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_461_MODEL_EDGES_ORBIT_DOCK',MARKER)
 html=one(html,'/* SE462_MODEL_WIRE_CLARITY_END */',
  '/* SE462_MODEL_WIRE_CLARITY_END */\n'
  '/* Historical v11.461 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_461_MODEL_EDGES_ORBIT_DOCK */')
 for a,b in [
  ('ENGINE · MAKER v11.461','ENGINE · MAKER v11.462'),
  ('v11.461 · hard-edge rims, model orbit and touch resize','v11.462 · clean wire edges and mobile viewport'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.461'","window.SWRLZ_FORGE_BUILD={version:'v11.462'"),
  ('<title>§wyrl§ Engine · Maker v11.461</title>','<title>§wyrl§ Engine · Maker v11.462</title>')
 ]:html=one(html,a,b)
 old=" source.engine='§wyrl§ Engine · Maker v11.461';source.version=11.461;"
 assert html.count(old)==5,('v11.462 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.462';source.version=11.462;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.461']
 notes['history'].insert(0,{'version':'v11.461','changes':notes.get('changes',[])})
 notes.update(version='v11.462',date='2026-11-15',
  title='Clean wireframe geometry and phone-friendly model viewport',
  changes=[
   'Wireframe defaults to clean angle-filtered mesh edges rather than the triangulation lattice. Show triangulation and Show hidden edges are optional, non-serialized display diagnostics.',
   'Shaded Wire and Solid/Flat/Clay have brighter geometry edges and stronger selected-object edge contrast; display materials are disposable and do not change saved meshes.',
   'Material view uses crisp planar shading on bounded editable hard-surface topology, so an inset cavity is not visually smoothed closed. Original authored materials remain intact.',
   'Mobile desktop-style dock resizing now reserves a larger central 3D viewport while leaving the existing native drag handles, collapse state, touch capture and Undo unaffected.',
   'The earlier orbit, working View commands, two-stage Inset/Extrude, UI docking, UVs and VR tools remain available.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
