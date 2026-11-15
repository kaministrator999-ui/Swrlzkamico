"""§E v11.457 — remove both remaining conversion-before-face UI gates.

Patch only the already-assembled v11.456 HTML. Source history is immutable:
native se430 convert guards, structured document, UV, Undo and geometry
preview ownership remain unchanged. The right-side legacy converter is also
made usable without a face and its label reflects that behavior.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_457_CONVERSION_NO_FACE_GATE"

def once(html,old,new):
 count=html.count(old)
 if count!=1:raise AssertionError(("v11.457 anchor",old[:180],count))
 return html.replace(old,new,1)

def apply(html):
 html=once(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_456_GUIDED_PRIMITIVE_CONVERSION",MARKER)
 html=once(html,"/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */",
  "/* SE456_GUIDED_PRIMITIVE_CONVERSION_END */\n"+
  "/* Historical v11.456 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_456_GUIDED_PRIMITIVE_CONVERSION */")

 # Native Face mode is allowed to have a selected part with objectCount==0:
 # the mesh selection list is separate from the active editable component.
 # The native bridge already refuses multi-object selections (>1).
 html=once(html,
  "const single=!!selection.partId&&(selection.objectCount??1)===1;",
  "const single=!!selection.partId&&(selection.objectCount??1)<=1;")
 html=once(html,
  "const s=state(),single=!!s?.selection?.partId&&(s.selection.objectCount??1)===1;",
  "const s=state(),single=!!s?.selection?.partId&&(s.selection.objectCount??1)<=1;")

 # The existing inspector CTA was disabled because there was not yet a
 # selectable face. That's an impossible prerequisite on plain primitives.
 html=once(html,
  "cta.disabled=!s.selection?.ids?.some(Number.isInteger);",
  "cta.disabled=!s.selection?.partId;")
 html=once(html,
  "cta.textContent=baking?'Bake edits & preview rim':'Make editable & preview rim';",
  "cta.textContent=baking?'Bake edits & make editable':s.selection?.ids?.some(Number.isInteger)?'Make editable & preview rim':'Make mesh editable';")

 # Keep the existing v453 preparation action and vertex bake confirmation.
 # Without a preselected face it converts only, then asks the user to tap
 # the desired square region. No fake preview, no extra history checkpoint.
 html=once(html,
  "if(!id||seed===undefined){se430BeginnerWrite(tooltip,'Tap a square face first.');return;}",
  "if(!id){se430BeginnerWrite(tooltip,'Select one cube first.');return;}")
 html=once(html,
  "if(!converted?.ok){se430BeginnerResult(converted);return;}\n  const region=api().selectRegion(seed,id);",
  "if(!converted?.ok){se430BeginnerResult(converted);return;}\n"
  "  if(seed===undefined){\n"
  "   se430BeginnerResult(converted);\n"
  "   se430BeginnerWrite(tooltip,'Editable cube ready. Tap a square face to preview the rim.');\n"
  "   currentState=state();refresh();return;\n"
  "  }\n"
  "  const region=api().selectRegion(seed,id);")

 # Preserve the controls' original IDs, callbacks and parent docking layout.
 for old,new in [
  ("ENGINE · MAKER v11.456","ENGINE · MAKER v11.457"),
  ("v11.456 · guided cube conversion before Inset","v11.457 · reliable editable cube conversion"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.456'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.457'"),
  ("<title>§wyrl§ Engine · Maker v11.456</title>",
   "<title>§wyrl§ Engine · Maker v11.457</title>")
 ]:html=once(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.456';source.version=11.456;"
 assert html.count(prior)==5,("v11.457 provenance",html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.457';source.version=11.457;")

 key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[e for e in notes.get("history",[]) if e.get("version")!="v11.456"]
 notes["history"].insert(0,{"version":"v11.456","changes":notes.get("changes",[])})
 notes.update(version="v11.457",date="2026-11-14",
  title="Inset conversion: no face-selection prerequisite",
  changes=[
   "The viewport Make Editable & Continue button now works when Face mode retains the selected cube but reports zero object-level selections. More than one selected mesh remains blocked by native bridge guards.",
   "The older Face modifier conversion button is no longer disabled until a face is selected, eliminating the circular dependency shown on mobile.",
   "Converting from the legacy button without a face now performs only the native safeguarded conversion, then prompts for a square face; it never fabricates an Inset preview.",
   "When an existing valid face seed exists, the earlier convert-and-preview behavior remains. Vertex edit baking still requires confirmation; blocked authored/rigged meshes are not converted.",
   "All changes reuse the original native se430 topology, Apply/Cancel, Undo and component selection. No new rendering loop, camera reset, independent geometry pipeline or UI panel is added."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace("</",r"<\/")+html[at+width:]
