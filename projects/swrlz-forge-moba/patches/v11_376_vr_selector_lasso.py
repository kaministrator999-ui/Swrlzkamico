"""§E v11.376 — dedicated XR Selector tool, retained trigger sweep, Left Grip area lasso."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_376_VR_SELECTOR_LASSO'
def once(s,a,b,label):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.376 source anchor',label,n,a[:105]))
 return s.replace(a,b,1)
def apply(html):
 helper=(ROOT/'runtime/model_vr_selector_lasso_v11_376.js').read_text('utf8')
 assert 'SE376_VR_SELECTOR_LASSO_START' in helper
 html=once(html,'/* SE372_MODEL_VR_PHASE1_END */',
  helper+'\n/* SE372_MODEL_VR_PHASE1_END */','shared native XR gesture selectors')
 # Let the existing menu Grip interception run first. Only while the Selector
 # panel has Lasso armed does the left workspace Grip draw a loop instead.
 html=once(html,
  "if(se372MenuDragStart(record,pose))return true;\n if(s.mode==='two-hand'){",
  "if(se372MenuDragStart(record,pose))return true;\n if(se376ShouldLasso(record,purpose))return se376LassoBegin(record,purpose);\n if(s.mode==='two-hand'){",
  'reserve Left Grip lasso when selected')
 html=once(html,
  "if(!g||!['view','menu','group','two-hand','extrude'].includes(g.kind))return false;",
  "if(!g||!['view','menu','selection-lasso','group','two-hand','extrude'].includes(g.kind))return false;",
  'accept lasso on Grip release')
 html=once(html,
  "if(g.kind==='menu'){se372MenuDragFinish(g,true);se340Notice('VR menu placed.');se340Publish();return true;}",
  "if(g.kind==='menu'){se372MenuDragFinish(g,true);se340Notice('VR menu placed.');se340Publish();return true;}\n  if(g.kind==='selection-lasso')return se376LassoCommit(g);",
  'commit lasso selection on Left Grip release')
 html=once(html,
  "if(g.kind==='menu')se372MenuDragFinish(g,false);se372GuideStop(g);s.se372Sweep=null;",
  "if(g.kind==='menu')se372MenuDragFinish(g,false);se376LassoDispose(g);se372GuideStop(g);s.se372Sweep=null;",
  'B/tracking loss discard unfinished selection')
 html=once(html,
  "if(g.kind==='menu'){se372MenuDragUpdate(g,pose);return;}",
  "if(g.kind==='menu'){se372MenuDragUpdate(g,pose);return;}\n if(g.kind==='selection-lasso'){se376LassoUpdate(g);return;}",
  'trace visible selection path each tracked frame')
 html=once(html,
  "function se372Dispose(){\n const s=se340XR;se374Dispose();",
  "function se372Dispose(){\n const s=se340XR;se376LassoDispose(s.gesture);se374Dispose();",
  'destroy transient lasso on XR exit')
 html=once(html,
  "if(action==='exit'){void se340ModelXRExit();return true;}",
  "if(se376PanelMode(action))return true;\n  if(action==='exit'){void se340ModelXRExit();return true;}",
  'selector modes in original model XR menu actions')
 html=once(html,
  "s.se372Gizmo=null;s.se372Sweep=null;s.se372ProjectBusy=false;",
  "s.se372Gizmo=null;s.se372Sweep=null;s.se372ProjectBusy=false;s.se376SelectionMode='sweep';",
  'default retains original sweep selection')
 html=once(html,
  "page:s.page,viewMode:s.viewMode,displayMode:s.displayMode,aimHand:s.aimHand,",
  "page:s.page,selectionMode:s.se376SelectionMode||'sweep',viewMode:s.viewMode,displayMode:s.displayMode,aimHand:s.aimHand,",
  'update menu selected mode indicator')
 html=once(html,
  "controllerHint:'Left grip moves view · Right grip edits · Both grips in Two-hand mode · B cancels'};",
  "controllerHint:s.page==='selector'&&s.se376SelectionMode!=='sweep'?'Left Grip draws a selection lasso · release selects · B cancels':\n    'Left grip moves view · Right grip edits · Both grips in Two-hand mode · B cancels'};",
  'contextual VR selector hint')
 # Add one discoverable Selector tab rather than replacing user-established tools.
 html=once(html,
  "  projects:[\n   ['save-account','Save to account']",
  """  selector:[
   ['selector-sweep','Swipe · trigger'],['selector-lasso-front','Lasso · front'],['selector-lasso-through','Lasso · through'],
   ['selection-clear','Clear selection'],['undo','Undo'],['redo','Redo'],
   ['move','Move selected'],['rotate','Rotate selected'],['scale','Scale selected'],
   ['mesh','Mesh tools'],['projects','Projects'],['help','Guide']
  ],
  projects:[
   ['save-account','Save to account']""",
  'dedicated selector modes')
 html=once(html,
  "const details={projects:'Save and manage this project',inspect:",
  "const details={selector:'Select overlapping model parts',"+
  "'selector-sweep':'Hold left trigger to add; retrace to remove',"+
  "'selector-lasso-front':'Left Grip · nearby-depth meshes',"+
  "'selector-lasso-through':'Left Grip · all depths in loop',"+
  "projects:'Save and manage this project',inspect:",
  'selector mode explanations')
 html=once(html,
  "const pageTitles={projects:['My projects'",
  "const pageTitles={selector:['Selector','SWEEP · FRONT LASSO · THROUGH LASSO'],projects:['My projects'",
  'menu heading for selector')
 html=once(html,
  "[['tools','Tools'],['sculpt','Sculpt'],['draw','Draw'],['views','Display'],['projects','Projects'],['help','Guide']].forEach",
  "[['tools','Tools'],['selector','Select'],['sculpt','Sculpt'],['draw','Draw'],['views','Display'],['projects','Projects'],['help','Guide']].forEach",
  'add selector to navigation')
 html=once(html,
  "surface('Model Studio · navigation '+label,.097,.041,330,123,.016)",
  "surface('Model Studio · navigation '+label,.083,.041,330,123,.016)",
  'fit seven tab widths without overlaps')
 html=once(html,
  "item.home=new T.Vector3((i-2.5)*.103,.198,.016)",
  "item.home=new T.Vector3((i-3)*.086,.198,.016)",
  'fit seven tab positions')
 html=once(html,
  "geometry(item.role==='nav'?.101:.212,item.role==='nav'?.053:.080)",
  "geometry(item.role==='nav'?.087:.212,item.role==='nav'?.053:.080)",
  'fit menu tab glow')
 html=once(html,
  "return ['inspect','move','rotate','scale','sculpt','draw','lasso','extrude','two-hand'].includes(id)?",
  "return id.startsWith('selector-')?state.selectionMode===id.slice(9):"+
  "['inspect','move','rotate','scale','sculpt','draw','lasso','extrude','two-hand'].includes(id)?",
  'show currently selected selector sub-mode')
 # Leave all existing controller models and placements untouched; update only
 # their contextual Left Grip label when a lasso mode is explicitly armed.
 html=once(html,
  "if(action==='stroke')return mode==='draw'?",
  "if(action==='pan'&&s.page==='selector'&&['lasso-front','lasso-through'].includes(s.se376SelectionMode))return 'Draw selection lasso';\n if(action==='stroke')return mode==='draw'?",
  'accurate context-sensitive left grip label')
 # This distinct model selector is not the older sculpt Lasso surface mask.
 for before,after,label in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_375_CHAT_TURNAROUND_BLOCKOUT',MARKER,'release marker'),
  ('ENGINE · MAKER v11.375','ENGINE · MAKER v11.376','heading'),
  ('v11.375 · image-guided editable 3D blockout','v11.376 · VR selector and area lasso','headline'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.375'","window.SWRLZ_FORGE_BUILD={version:'v11.376'",'build stamp'),
  ('<title>§wyrl§ Engine · Maker v11.375</title>','<title>§wyrl§ Engine · Maker v11.376</title>','title')
 ]:html=once(html,before,after,label)
 previous=" source.engine='§wyrl§ Engine · Maker v11.375';source.version=11.375;"
 n=html.count(previous)
 if n not in (3,5,6):raise AssertionError(('v11.376 provenance count',n))
 html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.376';source.version=11.376;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get('version')=='v11.375' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.375','changes':notes.get('changes',[])})
 notes.update(version='v11.376',date='2026-11-10',
  title='Quest 2 VR Selector with separate trigger sweep and left-grip lasso modes',
  changes=[
   'Adds a first-level Selector tab with Sweep, Front Lasso and Through Lasso modes; controller labels change with the selected tool.',
   'Original left-trigger tap and reversible hold-sweep remain available. In a lasso mode, Left Grip draws an outline in the model workspace; releasing Grip selects mesh parts inside its projected area, including overlapping geometry.',
   'Front Lasso uses a bounded depth band to avoid selecting everything behind the outlined cluster; Through Lasso includes all depths. Earlier selections are retained and the 32-part limit is respected.',
   'Gripping the floating VR menu retains priority over lasso drawing; outside the Selector lasso mode, Left Grip still moves the workspace. B cancels without changing selection.',
   'Lasso has a lightweight visible preview line and performs mesh selection only when Grip is released; existing Undo/Redo, controller models, UV textures, saved projects and account/starter safeguards remain intact.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
