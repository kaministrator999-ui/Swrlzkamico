"""§E v11.487 — export active model and selected My Projects card by their real names."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_487_CORRECT_MODEL_PROJECT_EXPORT"

def once(text,old,new,tag):
 n=text.count(old)
 if n!=1:raise AssertionError(("v11.487 anchor",tag,n,old[:120]))
 return text.replace(old,new,1)

def apply(html):
 assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS" in html
 model=(ROOT/"runtime/model_export_identity_v11_487.js").read_text("utf8")
 projects=(ROOT/"runtime/my_projects_export_v11_487.js").read_text("utf8")
 for token in ("se487ExportDisplayName","se487ExportStem","se487ExportOBJName"):
  assert token in model,token
 for token in ("async function exportNative(","async function exportUpdate(","selectedDocument(record,source)"):
  assert token in projects,token

 # Keep the historic export format; replace only the three Prism-Jester
 # filename/object-name literals. Model Atelier's model() already selects the
 # current project's model, or the isolated standalone scratch document.
 html=once(html,"  function exportJSON(){if(!model())return;",
  model+"\n  function exportJSON(){if(!model())return;","model export identity helper")
 html=once(html,
  "'prism-jester.model.json'",
  "se487ExportStem()+'.model.json'",
  "native model JSON filename")
 html=once(html,
  "'o Prism_Jester'",
  "'o '+se487ExportOBJName()",
  "OBJ object label")
 html=once(html,
  "'prism-jester.mesh.obj'",
  "se487ExportStem()+'.mesh.obj'",
  "OBJ download filename")

 # Wrap the existing My Projects cards *after* v11.471 deletion wrapper,
 # preserving Open/Preview/Delete behavior and any selection/default controls.
 # Exporting a card reads that record directly from IndexedDB or the existing
 # authenticated cloud RPC; it never switches the editor to that project.
 html=once(html,"function se184SyncDefaultBoxes(){",
  projects+"\nfunction se184SyncDefaultBoxes(){",
  "selected My Projects export actions")

 for old,new,tag in (
  ("SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS",MARKER,"release marker"),
  ("ENGINE · MAKER v11.486","ENGINE · MAKER v11.487","engine header"),
  ("v11.486 · rolling project revisions and in-place model updates",
   "v11.487 · named exports for active models and saved projects","release headline"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.486'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.487'","build metadata"),
  ("<title>§wyrl§ Engine · Maker v11.486</title>",
   "<title>§wyrl§ Engine · Maker v11.487</title>","browser title")
 ):html=once(html,old,new,tag)
 prior=" source.engine='§wyrl§ Engine · Maker v11.486';source.version=11.486;"
 assert html.count(prior)==5,("provenance count",html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.487';source.version=11.487;")
 key="const SE_RELEASE_NOTES="
 at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[h for h in notes.get("history",[]) if h.get("version")!="v11.486"]
 notes["history"].insert(0,{"version":"v11.486","changes":notes.get("changes",[])})
 notes.update(version="v11.487",date="2026-11-17",
  title="Correct active-model and My Projects export identity",
  changes=[
   "Model Atelier's native JSON and OBJ exports use the active project or standalone model name instead of the hardcoded original Prism Jester starter filename; OBJ object labels match the selected model.",
   "My Projects now exports the selected card's actual saved native project, whether on-device or in the account, instead of the currently open scene; account exports preserve the exact stored bytes and revision archive.",
   "My Projects also offers a model-only update package bound to the chosen project's stable ID and its account revision, compatible with the existing in-place update workflow.",
   "All exports preserve existing model source IDs, mesh data, UV textures, materials, rigs and animation. Only exported filenames and the new card actions change.",
   "Starter protection, native save/clone, rolling eight-slot revisions and VR controls remain unchanged."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
