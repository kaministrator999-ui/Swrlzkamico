"""§E v11.373 — preserve precise left-trigger press hit into reversible sweep."""
from pathlib import Path
import json

MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_373_VR_SWEEP_TRIGGER_HANDOFF"
def once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(("v11.373 anchor",label,n))
 return s.replace(old,new,1)

def apply(html):
 # Retain the exact fresh press hit before the normal selection refresh clears
 # passive hover caches; do not add an extra mesh raycast per trigger press.
 html=once(html,
  "const start=performance.now(),hit=se340Hit(record,false);record.hit=hit;",
  "const start=performance.now(),hit=se340Hit(record,false);record.hit=hit;record.se372TriggerHit=hit;",
  "capture selection press hit")
 html=once(html,
  "if(before)se372SweepStart(record,before);",
  "if(before)se372SweepStart(record,before,record.se372TriggerHit);record.se372TriggerHit=null;",
  "deliver exact press hit")
 html=once(html,
  "function se372SweepStart(record,before){\n const s=se340XR,hit=record.hit;",
  "function se372SweepStart(record,before,hit){\n const s=se340XR;",
  "avoid stale invalidated hover")
 for old,new,label in [
  ("SWYRL_ENGINE_DEPLOY_MARKER: V11_372_MODEL_VR_PHASE1",MARKER,"marker"),
  ("ENGINE · MAKER v11.372","ENGINE · MAKER v11.373","header"),
  ("v11.372 · VR editing, reversible sweep and account save","v11.373 · reliable left-trigger mesh sweep","headline"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.372'","window.SWRLZ_FORGE_BUILD={version:'v11.373'","runtime"),
  ("<title>§wyrl§ Engine · Maker v11.372</title>","<title>§wyrl§ Engine · Maker v11.373</title>","browser title")
 ]:html=once(html,old,new,label)
 old=" source.engine='§wyrl§ Engine · Maker v11.372';source.version=11.372;"
 n=html.count(old)
 if n not in (3,5,6):raise AssertionError(("provenance count",n))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.373';source.version=11.373;")
 at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get("version")=="v11.372" for x in notes.get("history",[])):
  notes.setdefault("history",[]).insert(0,{"version":"v11.372","changes":notes.get("changes",[])})
 notes.update(version="v11.373",date="2026-11-10",
  title="Make left-trigger reversible mesh sweep start reliably",
  changes=[
   "Capture the same fresh left-trigger selection hit before the native selection invalidates hover; hand it directly to the reversible sweep initializer.",
   "A single tap remains additive selection. During a continuous hold, traversing separate pieces adds meshes, reversing that same path removes only pieces added during that hold.",
   "No additional per-frame picking, new XR renderer, or change to source mesh geometry. Grip-menu and grip-model mutual exclusion, cloud saves with revision guards, Quest Touch labels and existing modeling modes are preserved."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
