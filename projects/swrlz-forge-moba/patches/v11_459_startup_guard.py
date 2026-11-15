"""§E v11.459 — startup safety correction for optional v11.458 viewport helper.

No model, topology, camera, or layout changes. A missing/out-of-scope internal
rendering function must NEVER throw before the editor initializer runs.
Retain v11.458 CSS, dock-size fix, safe event-based contour refresh and camera
correction whenever their native dependencies are available.
"""
import json

MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_459_VIEWPORT_BOOT_GUARD"

def once(s,a,b):
    n=s.count(a)
    if n!=1:raise AssertionError(("v11.459 source drift",a[:120],n))
    return s.replace(a,b,1)

def apply(html):
    # Limit the surgery to the optional v11.458 module, not the native
    # rendering and modeling code that happens to use the same identifiers.
    start=html.index("/* SE458_MODEL_VIEWPORT_STABILITY_START */")
    stop=html.index("/* SE458_MODEL_VIEWPORT_STABILITY_END */",start)
    seg=html[start:stop]
    # Eager capture accessed atelierViewModeApply before the initializer
    # necessarily exposes it. A ReferenceError can stop the editor boot.
    seg=once(seg,
        """ const beforeViewApply=atelierViewModeApply;
 atelierViewModeApply=function(mesh,part){
  const result=beforeViewApply.apply(this,arguments);
  update(mesh,part);
  return result;
 };""",
        """ // Optional extension: render initialization must never depend on this.
 // Even typeof on a lexical binding in its temporal dead zone can throw.
 try {
  const se459NativeViewApply=typeof atelierViewModeApply==='function'
    ?atelierViewModeApply:null;
  if(se459NativeViewApply){
   atelierViewModeApply=function(mesh,part){
    const result=se459NativeViewApply.apply(this,arguments);
    update(mesh,part);
    return result;
   };
  }
 }catch(_){
  // A private/uninitialized renderer cannot prevent scene boot.
 }""")
    seg=once(seg,
        " function selected(part){return part?.id===selection;}",
        " function selected(part){return part?.id===(typeof selection==='undefined'?null:selection);}")
    seg=once(seg,
        "  const mode=atelierViewModeFor(part);",
        "  const mode=typeof atelierViewModeFor==='function'?atelierViewModeFor(part):null;")
    seg=once(seg,
        "   const part=partById(mesh.userData.atelierId);\n   update(mesh,part);",
        "   const part=typeof partById==='function'?partById(mesh.userData.atelierId):null;\n   update(mesh,part);")
    seg=once(seg,
        "  if(!state?.selection?.partId||state?.preview?.active||atelierCameraInterior)return;",
        "  if(!state?.selection?.partId||state?.preview?.active||\n   typeof atelierCameraInterior==='undefined'||atelierCameraInterior||\n   typeof se430ModelCamera==='undefined'||typeof atelierCameraPan==='undefined'||\n   typeof cameraUpdate!=='function')return;")
    html=html[:start]+seg+html[stop:]
    html=once(html,
        "/* SE458_MODEL_VIEWPORT_STABILITY_END */",
        "/* SE458_MODEL_VIEWPORT_STABILITY_END */\n"
        "/* SE459_STARTUP_SAFETY_COMPLETE */")

    html=once(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_458_DOCK_ORBIT_CONTRAST",MARKER)
    html=once(html,"/* SE459_STARTUP_SAFETY_COMPLETE */",
        "/* SE459_STARTUP_SAFETY_COMPLETE */\n"
        "/* Historical v11.458 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_458_DOCK_ORBIT_CONTRAST */")
    for a,b in [
        ("ENGINE · MAKER v11.458","ENGINE · MAKER v11.459"),
        ("v11.458 · stable model orbit and dock resizing","v11.459 · safe viewport initialization"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.458'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.459'"),
        ("<title>§wyrl§ Engine · Maker v11.458</title>",
         "<title>§wyrl§ Engine · Maker v11.459</title>")
    ]:html=once(html,a,b)
    old=" source.engine='§wyrl§ Engine · Maker v11.458';source.version=11.458;"
    assert html.count(old)==5,("v11.459 provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.459';source.version=11.459;")
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes["history"]=[e for e in notes.get("history",[]) if e.get("version")!="v11.458"]
    notes["history"].insert(0,{"version":"v11.458","changes":notes.get("changes",[])})
    notes.update(version="v11.459",date="2026-11-15",
        title="Prevent optional viewport helper from blocking editor startup",
        changes=[
            "The v11.458 selected-outline helper no longer references an internal renderer before the Model Studio initialization has exposed it. An unavailable optional renderer simply disables that hook instead of throwing on startup.",
            "Optional model selection, view shading and camera references are checked before use. Scene creation, project restoration, modeling controls, model conversion and Inset are independent of these visual additions.",
            "v11.458 dock sizing, edge rendering when supported, post-commit camera focus, native Undo, VR/desktop editor architecture and existing sculpt workflow remain preserved. No new graphics pipeline or loop is introduced."
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
