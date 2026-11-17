"""§E v11.490: native cloth pose playback repair and project-specific workspace resume.
Appends code inside Model Atelier; geometry and texture assets remain untouched.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_490_MODEL_RIG_WORKSPACE"

def once(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(("v11.490 anchor",old[:100],n))
 return s.replace(old,new,1)

def apply(html):
 assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_489_CLOTH_RIG_PROJECT_UPDATE" in html
 src=(ROOT/"runtime/model_atelier_rig_workspace_v11_490.js").read_text("utf8")
 assert "window.SWYRL_ENGINE_MODEL_WORKSPACE_490=se490Workspace" in src
 # v11.489's cloth rig code is already inside the original ModelAtelier
 # closure; retain the same lexical scope for its rig/render/camera hooks.
 html=once(html,"  function refreshList(){",src+"\n  function refreshList(){")
 # Add a narrow, validated project-specific layout adapter to the v11.251
 # dock controller; the original model, materials and resize handlers remain.
 html=once(html,
  "window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251=Object.freeze({\n mode,setMode:mode,",
  """window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251=Object.freeze({
 modelDock:()=>({mode:state.mode,...state.model}),
 setModelDock:next=>{
  if(!next||typeof next!=='object')return false;
  for(const side of ['left','right'])
   if(Number.isFinite(next[side])&&next[side]>=140&&next[side]<=480)
    state.model[side]=next[side];
  for(const field of ['collapsed','rightCollapsed'])
   if(typeof next[field]==='boolean')state.model[field]=next[field];
  if(['auto','desktop','compact'].includes(next.mode))state.mode=next.mode;
  sync();save();window.dispatchEvent(new Event('resize'));
  return true;
 },
 mode,setMode:mode,""")

 for old,new in (
  ("SWYRL_ENGINE_DEPLOY_MARKER: V11_489_CLOTH_RIG_PROJECT_UPDATE",MARKER),
  ("ENGINE · MAKER v11.489","ENGINE · MAKER v11.490"),
  ("v11.489 · cloth rig animation and in-place account model updates",
   "v11.490 · cloth rig playback and project workspace restoration"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.489'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.490'"),
  ("<title>§wyrl§ Engine · Maker v11.489</title>",
   "<title>§wyrl§ Engine · Maker v11.490</title>")
 ):html=once(html,old,new)
 prev=" source.engine='§wyrl§ Engine · Maker v11.489';source.version=11.489;"
 if html.count(prev)!=5:raise AssertionError(("v11.490 provenance",html.count(prev)))
 html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.490';source.version=11.490;")
 tag="const SE_RELEASE_NOTES=";at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[x for x in notes.get("history",[]) if x.get("version")!="v11.489"]
 notes["history"].insert(0,{"version":"v11.489","changes":notes.get("changes",[])})
 notes.update(version="v11.490",date="2026-11-17",
  title="Rigged cloth animation playback and model workspace resume",
  changes=[
   "Model Studio checks that an imported weighted cloth rig is attached to an actual GPU SkinnedMesh, recovering from a plain Mesh topology-render path without rewriting the authored surface.",
   "Timeline selection, scrub position and working clip are preserved with the model's last open workspace; the animation panel no longer appears to control an unbound mesh in the fallback path.",
   "Per-project workspace includes exact camera position/target, projection and view, primary mesh selection, tool mode, inspector scroll, rig panel state, clip/playhead and folding rail state.",
   "Workspace state uses a lightweight per-project on-device record and is embedded in explicit project/model saves for portability. It does not save full project bytes or credentials to localStorage.",
   "Existing native cloud compare-and-swap, revision history, project naming and protected user geometry/UVs are not modified."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+n:]
