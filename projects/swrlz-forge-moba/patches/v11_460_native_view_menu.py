"""§E v11.460: repair the visibly inert Display/Camera View panel.

The v11.459 boot fix stopped referencing private atelierViewGlobal from an
outer script, but accidentally replaced working view commands with a lookup
for a DOM selector that is not the authority. Expose small native-scoped
commands through ModelAtelier while preserving the safe boot separation.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_460_NATIVE_VIEW_MENU"

def one(s,a,b):
    n=s.count(a)
    if n!=1:raise AssertionError(("v11.460 source anchor drift",a[:150],n))
    return s.replace(a,b,1)

def apply(html):
    script=(ROOT/"runtime/model_native_view_commands_v11_460.js").read_text("utf8")
    assert script.startswith("/* SE460_NATIVE_VIEW_COMMANDS_START */")
    assert script.rstrip().endswith("/* SE460_NATIVE_VIEW_COMMANDS_END */")
    # These declarations are in the ORIGINAL ModelAtelier closure, not the
    # separate quick-menu script, and are passed out only after init returns.
    html=one(html,"/* ATELIER_BRIDGE_END */",script+"\n/* ATELIER_BRIDGE_END */")
    # Menu remains outside the closure. Never reach into private renderer
    # variables or guess at hidden #ViewportMode selectors.
    a=html.index("/* SE455_VIEW_READABILITY_START */")
    b=html.index("/* SE455_VIEW_READABILITY_END */",a)
    display=html[a:b]
    display=one(display,
        " const mode=()=>panel?.querySelector('#ViewportMode')?.value||'solid';",
        " const mode=()=>window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.mode||'solid';")
    sc=display.index(" function choose(next){")
    ec=display.index(" function selectCamera(view){",sc)
    choose=""" function choose(next){
  if(!valid(next))return false;
  const bridge=window.SWYRL_ENGINE_MODEL_VIEW;
  if(!bridge?.setMode){
   if(typeof status==='function')status('View controls are not initialized yet.',true);
   return false;
  }
  const ok=bridge.setMode(next)===true;
  if(ok)update();
  return ok;
 }
 """
    display=display[:sc]+choose+display[ec:]
    sc=display.index(" function selectCamera(view){")
    ec=display.index(" function addOptions(){",sc)
    camera=""" function selectCamera(view){
  if(!['front','right','top','three'].includes(view))return false;
  const ok=window.SWYRL_ENGINE_MODEL_VIEW?.setCamera?.(view)===true;
  if(ok){menu.hidden=true;update();}
  return ok;
 }
 """
    display=display[:sc]+camera+display[ec:]
    display=one(display,
        "    previewActive:active(),camera:se430ModelCamera.inspect()?.view||'orbit'})",
        "    previewActive:active(),camera:window.SWYRL_ENGINE_MODEL_VIEW?.inspect?.()?.camera||'orbit'})")
    html=html[:a]+display+html[b:]

    html=one(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_459_VIEWPORT_BOOT_GUARD",MARKER)
    html=one(html,"/* SE460_NATIVE_VIEW_COMMANDS_END */",
       "/* SE460_NATIVE_VIEW_COMMANDS_END */\n"
       "/* Historical v11.459 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_459_VIEWPORT_BOOT_GUARD */")
    for a,b in [
        ("ENGINE · MAKER v11.459","ENGINE · MAKER v11.460"),
        ("v11.459 · safe viewport initialization","v11.460 · working Display and Camera views"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.459'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.460'"),
        ("<title>§wyrl§ Engine · Maker v11.459</title>",
         "<title>§wyrl§ Engine · Maker v11.460</title>")
    ]:html=one(html,a,b)
    prior=" source.engine='§wyrl§ Engine · Maker v11.459';source.version=11.459;"
    assert html.count(prior)==5,("v11.460 provenance",html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.460';source.version=11.460;")
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[x for x in notes.get("history",[]) if x.get("version")!="v11.459"]
    notes["history"].insert(0,{"version":"v11.459","changes":notes.get("changes",[])})
    notes.update(version="v11.460",date="2026-11-15",
       title="Restore functional viewport display and camera controls",
       changes=[
         "The visible View panel now sends every Solid, Material, Shaded Wire, Wireframe, X-Ray, Flat, and Clay action into the original Model Atelier renderer through a native-scoped public bridge instead of a missing DOM selector.",
         "Front, Right, Top and 3/4 camera buttons call the same native camera API used by existing orientation controls, preserving frame/orbit state and avoiding unbound private identifiers.",
         "The bridge is defined inside the existing ModelAtelier closure, exported only once the modeler is ready, and never assumes private renderer variables are accessible from outer UI scripts.",
         "During active Inset/Extrude previews, presentation changes update live materials without rebuilding geometry or discarding the preview; camera preset changes remain blocked until the preview is committed or canceled.",
         "Preserves v11.459 startup fix, v11.458 dock sizing, native cube conversion, Undo, VR input and existing material/source ownership."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
