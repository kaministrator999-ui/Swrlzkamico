"""§E v11.461: source-owned rim normals, true orbit pivot, touch-reachable dock.

Modify only display presentation, native camera gesture entry points and
the existing splitter hit area. Preserve the saved indexed topology,
UVs, source materials, native transactions and Undo/Redo lineage.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_461_MODEL_EDGES_ORBIT_DOCK'
def one(src,old,new):
 n=src.count(old)
 if n!=1:raise AssertionError(('v11.461 anchor drift',old[:165],n))
 return src.replace(old,new,1)
def apply(html):
 js=(ROOT/'runtime/model_hard_surface_orbit_v11_461.js').read_text('utf8')
 css=(ROOT/'runtime/model_touch_dock_v11_461.css').read_text('utf8')
 assert js.startswith('/* SE461_HARD_SURFACE_ORBIT_START */')
 assert js.rstrip().endswith('/* SE461_HARD_SURFACE_ORBIT_END */')
 assert css.startswith('/* SE461_TOUCH_DOCK_BOUNDS_START */')
 # Place the supplement INSIDE the existing native ModelAtelier scope, not
 # in a separate global script that cannot see the renderer and modelRoot.
 html=one(html,'/* SE460_NATIVE_VIEW_COMMANDS_END */',
  '/* SE460_NATIVE_VIEW_COMMANDS_END */\n'+js)
 # Source-welded topology averages normals across square inset rims. On
 # bounded, low-poly editable hard surfaces use per-triangle lighting
 # ONLY in display shaders. Native geometry.indices and vertex IDs unchanged.
 html=one(html,
  "color,metalness:0,roughness:.89,flatShading:mode==='flat',",
  "color,metalness:0,roughness:.89,flatShading:mode==='flat'||se461LowPolyEditable(part,mesh),")
 # The user expects a ONE-finger orbit around the edited object, not a
 # turn-in-place from the old fixed target y=2.35/2.8. Call once per actual
 # orbit gesture, never from a gizmo, two-finger pan, preview Apply or Undo.
 html=one(html,
  "function se447CameraOrbitApply(gesture,x,y){",
  "function se447CameraOrbitApply(gesture,x,y){\n"
  " if(!gesture.se461PivotAligned){se461AlignOrbitPivot();gesture.se461PivotAligned=true;}")
 html=one(html,
  "if(pressed.moved){const touch=e.pointerType==='touch',invertTouch=touch&&se433CameraPrefs.inverted;",
  "if(pressed.moved){if(!pressed.se461PivotAligned){se461AlignOrbitPivot();pressed.se461PivotAligned=true;}"
  "const touch=e.pointerType==='touch',invertTouch=touch&&se433CameraPrefs.inverted;")
 html=html.replace('</head>',
  '<style id="se461TouchDockBoundsStyles">\n'+css+'\n</style>\n</head>',1)
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_460_NATIVE_VIEW_MENU',MARKER)
 html=one(html,'/* SE461_HARD_SURFACE_ORBIT_END */',
   '/* SE461_HARD_SURFACE_ORBIT_END */\n'
   '/* Historical v11.460 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_460_NATIVE_VIEW_MENU */')
 for a,b in [
   ('ENGINE · MAKER v11.460','ENGINE · MAKER v11.461'),
   ('v11.460 · working Display and Camera views','v11.461 · hard-edge rims, model orbit and touch resize'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.460'","window.SWRLZ_FORGE_BUILD={version:'v11.461'"),
   ('<title>§wyrl§ Engine · Maker v11.460</title>','<title>§wyrl§ Engine · Maker v11.461</title>')
 ]:html=one(html,a,b)
 old=" source.engine='§wyrl§ Engine · Maker v11.460';source.version=11.460;"
 assert html.count(old)==5,('v11.461 provenance',html.count(old))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.461';source.version=11.461;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.460']
 notes['history'].insert(0,{'version':'v11.460','changes':notes.get('changes',[])})
 notes.update(version='v11.461',date='2026-11-15',
   title='Readable hard-surface rims, object-centered orbit and mobile splitters',
   changes=[
    'Bounded low-poly editable topology now uses correct planar face lighting in Solid and Shaded Wire. Flat remains available and smoothed curved primitives keep their original normals. Saved mesh vertices, face IDs, UVs and Undo are unchanged.',
    'Hard-surface silhouette and angle-filtered inset edges remain visible in Solid, Flat and Clay even when the cube is not currently selected; Shaded Wire retains its own native edge guide.',
    'A new one-finger orbit centers on the selected mesh, or the whole model when nothing is selected, only once when actual drag movement begins. It preserves yaw, pitch and zoom; two-finger pinch and pan, model editing gestures, and intentional tool previews remain unaffected.',
    'The right dock splitter hit area now sits entirely on the tool-rail side of the inspector boundary, where touch events cannot be intercepted by the inspector. Both handles use wider hit targets and retain the original native pointer and keyboard resizing handlers.',
    'v11.459 startup safeguards, v11.460 working Display/Camera controls, guided cube conversion, two-stage Inset/Extrude, save/UV, VR and modeling history remain under their native owners.'
   ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
