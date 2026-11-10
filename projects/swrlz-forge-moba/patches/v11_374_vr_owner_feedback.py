"""§E v11.374 — real headset feedback: usable drag, visible grouping/reticle and project menu."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_374_QUEST_VR_FEEDBACK'
def once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.374 source anchor',label,n,old[:95]))
 return s.replace(old,new,1)

def span(s,start,end,replacement,label):
 if s.count(start)!=1:raise AssertionError(('v11.374 start',label,s.count(start)))
 a=s.index(start);b=s.find(end,a+len(start))
 if b<0:raise AssertionError(('v11.374 end',label))
 return s[:a]+replacement+s[b:]

def apply(html):
 helper=(ROOT/'runtime/model_vr_feedback_v11_374.js').read_text('utf8')
 assert 'SE374_MODEL_VR_OWNER_FEEDBACK_START' in helper
 html=once(html,'/* SE372_MODEL_VR_PHASE1_END */',helper+'\n/* SE372_MODEL_VR_PHASE1_END */','scoped shared XR helpers')
 # Physically held Grip now grabs the ray-hit spot on the floating panel.
 # This supports wrist-directed dragging with the same Raycast as selection;
 # it is not a head-following HUD.
 html=once(html,
  "s.gesture={kind:'menu',record,hand:pose,start:s.ui.root.position.clone(),\n  initial:s.ui.root.position.clone(),initialRotation:s.ui.root.quaternion.clone()};",
  "s.gesture={kind:'menu',record,hand:pose,start:s.ui.root.position.clone(),\n  initial:s.ui.root.position.clone(),initialRotation:s.ui.root.quaternion.clone()};se374MenuRayGripStart(s.gesture,hit);",
  'start anchored window drag at ray hit')
 html=once(html,
  "function se372MenuDragUpdate(g,pose){\n se340XR.ui.root.position.copy(g.start)",
  "function se372MenuDragUpdate(g,pose){\n if(se374MenuRayGripUpdate(g))return;\n se340XR.ui.root.position.copy(g.start)",
  'follow target ray instead of tiny physical grip delta')
 # Make axis targets a little more forgiving when casting a Quest pointer.
 html=once(html,'new THREE.TorusGeometry(.105,.004,6,56)',
  'new THREE.TorusGeometry(.105,.008,8,56)','pointer-friendly ring volume')
 # One gizmo contact path is shared by the Grip axis selector and the
 # visible ray reticle; ignore hidden/inactive axis handles.
 html=span(html,"function se372GizmoHit(record){","function se372GizmoFrame(s){",
  "function se372GizmoHit(record){return se374GizmoContact(record)?.axis||null;}\n",
  'share gizmo ray contact')
 html=once(html,
  " const entries=se340PartEntries().filter(e=>e.mesh?.visible!==false);\n if(!precise){",
  " const gizmo=se374GizmoContact(record,cast);if(gizmo)return finish(gizmo);\n const entries=se340PartEntries().filter(e=>e.mesh?.visible!==false);\n if(!precise){",
  'surface picker recognizes transformation handles')
 html=once(html,
  "if(hit?.ui){if(hit.action&&se340XR.ui.press(hit.target)!==false)se340ModelXRAction(hit.action,record);return;}\n if(se340XR.gesture)return;",
  "if(hit?.ui){if(hit.action&&se340XR.ui.press(hit.target)!==false)se340ModelXRAction(hit.action,record);return;}\n if(hit?.gizmo)return; // Gizmo grip starts a constrained transform; trigger must not select geometry behind it.\n if(se340XR.gesture)return;",
  'gizmo pointer never selects behind the handle')
 html=once(html,
  "record.dot.visible=!!(hit?.id||hit?.ui)&&!!hit.point;",
  "record.dot.visible=!!(hit?.id||hit?.ui||hit?.gizmo)&&!!hit.point;",
  'show cursor reticle when pointing at gizmo')
 html=once(html,
  "record.ray.material.color.setHex(hit?.ui?0xe1bbff:hit?.id?0x80f0c4:0xbda0ff);",
  "record.ray.material.color.setHex(hit?.ui?0xe1bbff:hit?.gizmo?0xffd28a:hit?.id?0x80f0c4:0xbda0ff);",
  'differentiate gizmo ray hover')
 html=once(html,
  "s.selectedOutline.box.union(se340PartBox(entry.mesh));}\n s.hoverOutline.visible=",
  "s.selectedOutline.box.union(se340PartBox(entry.mesh));}se374GroupBoundary(s,selectedIds);\n s.hoverOutline.visible=",
  'one distinct expanding multi-mesh selection boundary')
 html=once(html,
  "function se372Dispose(){\n const s=se340XR;",
  "function se372Dispose(){\n const s=se340XR;se374Dispose();",
  'dispose transient group helper on XR exit')
 # Put project saving in an explicit, always-visible top-level menu tab.
 html=once(html,
  "  sculpt:[\n   ['sculpt-push','Push']",
  """  projects:[
   ['save-account','Save to account'],['save-local','Save project'],['clone-project','Clone project'],
   ['menu-reset','Reset menu'],['menu-hide','Hide menu'],['studio','More tools'],
   ['help','Controller guide'],['tools','Model tools'],['exit','Exit VR']
  ],
  sculpt:[
   ['sculpt-push','Push']""",
  'first-level projects menu page')
 html=once(html,
  "const details={inspect:'View without editing'",
  "const details={projects:'Save and manage this project',inspect:'View without editing'",
  'description for projects navigation')
 html=once(html,
  "const pageTitles={tools:['Quick tools'",
  "const pageTitles={projects:['My projects','SAVE · ACCOUNT · CLONE'],tools:['Quick tools'",
  'visible project page label')
 html=once(html,
  "[['tools','Tools'],['sculpt','Sculpt'],['draw','Draw'],['views','Display'],['help','Guide']].forEach",
  "[['tools','Tools'],['sculpt','Sculpt'],['draw','Draw'],['views','Display'],['projects','Projects'],['help','Guide']].forEach",
  'projects tab beside original menu navigation')
 html=once(html,
  "surface('Model Studio · navigation '+label,.11,.041,330,123,.016)",
  "surface('Model Studio · navigation '+label,.097,.041,330,123,.016)",
  'six nav tabs without overlaps')
 html=once(html,
  "item.home=new T.Vector3((i-2)*.121,.198,.016)",
  "item.home=new T.Vector3((i-2.5)*.103,.198,.016)",
  'six-tab spacing within original menu plate')
 html=once(html,
  "geometry(item.role==='nav'?.123:.212,item.role==='nav'?.053:.080)",
  "geometry(item.role==='nav'?.101:.212,item.role==='nav'?.053:.080)",
  'nav hover glow respects new tab width')
 html=once(html,
  "if(action==='mesh'||action==='studio'){se340CancelGesture();s.page=action;",
  "if(action==='mesh'||action==='studio'||action==='projects'){se340CancelGesture();s.page=action;",
  'projects page action without changing current model mode')
 # Prior versioned source/release metadata remains intact.
 for before,after,label in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_373_VR_SWEEP_TRIGGER_HANDOFF',MARKER,'release marker'),
  ('ENGINE · MAKER v11.373','ENGINE · MAKER v11.374','header'),
  ('v11.373 · reliable left-trigger mesh sweep','v11.374 · VR gesture, selection and project menu usability','headline'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.373'","window.SWRLZ_FORGE_BUILD={version:'v11.374'",'build version'),
  ('<title>§wyrl§ Engine · Maker v11.373</title>','<title>§wyrl§ Engine · Maker v11.374</title>','browser title')
 ]:html=once(html,before,after,label)
 old=" source.engine='§wyrl§ Engine · Maker v11.373';source.version=11.373;"
 count=html.count(old)
 if count not in (3,5,6):raise AssertionError(('v11.374 provenance count',count))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.374';source.version=11.374;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get('version')=='v11.373' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.373','changes':notes.get('changes',[])})
 notes.update(version='v11.374',date='2026-11-10',
  title='Quest 2 VR menu, multi-selection bounds and visible transform targeting',
  changes=[
   'Move the floating VR panel by holding Grip on the ray-hit point: wrist-directed ray movement positions the full window, and it stays in its world workspace until manually dragged again.',
   'A high-contrast shared boundary box visibly expands around all selected meshes; a single selected mesh keeps its original selection outline.',
   'Controller ray pointer now shows a reticle when targeting an active Move, Rotate or Scale handle; hidden handles remain non-selectable and transforms remain grip-only.',
   'Projects appears as a distinct top-level VR menu tab with Save to account, Save project and Clone project visible, retaining the existing authenticated account revision and starter protections.',
   'Preserve the original Quest Touch controller bodies, dynamic labels, X-menu toggle, Undo/Redo and single physical XR frame loop.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
