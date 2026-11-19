"""§E v11.519 — QUEST BROWSER 2D ONLY.
Native Move/Rotate/Scale gizmo ray-pointer targets, tap-to-deselect,
and a display-only selection boundary toggle. Immersive WebXR untouched.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_519_QUEST_BROWSER_TRANSFORMS'
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.519',label,n,old[:120]))
 return s.replace(old,new,1)
def scope(html,start,end,fn):
 a=html.index(start);b=html.index(end,a)
 return html[:a]+fn(html[a:b])+html[b:]
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_518_QUEST_RIG_CACHE' in html
 js=(ROOT/'runtime/model_quest_browser_transform_v11_519.js').read_text('utf8')
 assert 'SE519_QUEST_BROWSER_TRANSFORM_END' in js
 # The browser Model Atelier already owns the canvas and selection lifecycle.
 # Introduce only a local adapter, after existing 2D gizmo/selection helpers.
 html=one(html,'/* ATELIER_BRIDGE_END */',js+'\n/* ATELIER_BRIDGE_END */',
          'native Model Atelier closure adapter')
 def improve_gizmo(s):
  s=one(s,"const coarse=()=>pointerType==='touch'||(!pointerType&&typeof matchMedia==='function'&&matchMedia('(pointer:coarse)').matches);",
        "const coarse=()=>pointerType==='touch'||(typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D())||(!pointerType&&typeof matchMedia==='function'&&matchMedia('(pointer:coarse)').matches);",
        'Quest controller rays use larger projection handles, not tiny mouse targets')
  radius=re.findall(r"const targetRadius=type=>[^;\n]+;",s)
  assert len(radius)==1,('v11.519 native gizmo target radius',radius)
  s=s.replace(radius[0],
    "const targetRadius=type=>typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D()?28:"+radius[0][len('const targetRadius=type=>'):],
    1)
  s=one(s,"e.target!==c||e.isPrimary===false||!primary||!ready()",
        "e.target!==c||(e.isPrimary===false&&!(typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D()))||!primary||!ready()",
        'allow Quest non-primary hand while canvas still owns press')
  s=one(s,"document.elementFromPoint(e.clientX,e.clientY)!==c)return false;",
        "document.elementFromPoint(e.clientX,e.clientY)!==c&&!(typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D()&&document.elementFromPoint(e.clientX,e.clientY)===c.parentElement))return false;",
        'tolerate Quest browser canvas-parent rounding, never overlay presses')
  return s
 html=scope(html,'/* SE431_MODEL_GIZMO_ACCESS_START */','/* SE431_MODEL_GIZMO_ACCESS_END */',improve_gizmo)
 def improve_quest(s):
  return one(s,"return !top||top===canvas;",
    "return !top||top===canvas||(typeof se512QuestBrowser2D==='function'&&se512QuestBrowser2D()&&top===canvas.parentElement);",
    'native Quest 2D viewport input ownership agrees with gizmo hit acceptance')
 html=scope(html,'/* SE467_QUEST_BROWSER_INPUT_START */','/* SE467_QUEST_BROWSER_INPUT_END */',improve_quest)
 for old,new in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_518_QUEST_RIG_CACHE',MARKER),
  ('ENGINE · MAKER v11.518','ENGINE · MAKER v11.519'),
  ('v11.518 · Quest native rig scope, selected project resume and revision-aware cache',
   'v11.519 · Quest browser gizmo drag, tap-deselect and bounds toggle'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.518'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.519'"),
  ('<title>§wyrl§ Engine · Maker v11.518</title>',
   '<title>§wyrl§ Engine · Maker v11.519</title>')
 ]:html=one(html,old,new,'release identity')
 previous=" source.engine='§wyrl§ Engine · Maker v11.518';source.version=11.518;"
 assert html.count(previous)==5,('provenance',html.count(previous))
 html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.519';source.version=11.519;")
 marker='const SE_RELEASE_NOTES=';at=html.index(marker)+len(marker)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.518']
 notes['history'].insert(0,{'version':'v11.518','changes':notes.get('changes',[])})
 notes.update(version='v11.519',date='2026-11-18',
  title='Quest 2D Browser native transform gizmos and selection display',
  changes=[
   'Quest regular 2D Browser: move, rotate and scale gizmos use larger, projection-correct controller ray targets and can be picked with either tracked controller. A native pointer drag still uses the exact original transform preview, clamp, single Undo checkpoint, cancellation and save; no new standalone gizmo pipeline.',
   'Quest Browser 2D: clicking the already selected visible mesh once again (without dragging, hitting its transform handles, or editing vertices) clears that selection. This does not affect immersive VR, desktop or multi-mesh grouping.',
   'The existing 2D viewport-control row now offers Hide bounds / Show bounds. This changes only Three.js native selection BoxHelper visibility, not authored mesh geometry, wireframes, UVs, rig weights, gizmos, project revisions or Undo.',
   'The v11.518 fix for se220RigAvailable during immersive entry and cloud project revision caching remains intact, as do current spatial WebXR menus and all model/project data.',
   'Physical Quest Browser selection, grab and bounds toggle require on-device acceptance after deployment.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
