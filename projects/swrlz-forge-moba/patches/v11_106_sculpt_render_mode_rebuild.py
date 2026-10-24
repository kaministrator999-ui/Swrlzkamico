"""Keep viewport material and redraw state stable after native sculpt geometry edits."""
import hashlib
import json

def once(s,a,b):
    count=s.count(a)
    assert count==1,(a[:120],count)
    return s.replace(a,b,1)

REPAIR = """
// §E v11.106: render mode is editor display state, not part of sculpt history.
// Final material check runs *after* the mesh has been regenerated from saved
// geometry. Nothing here mutates source vertex data, part properties or Undo.
function atelierViewEnsureAfterGeometryEdit(){
 if(!modelRoot||!model())return;
 for(const part of model().parts){
  const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===part.id);
  if(!mesh||!mesh.material)continue;
  const mode=atelierViewModeFor(part);
  const mat=mesh.material;
  const hasOverlay=mesh.children.some(o=>o.name==='Viewport wireframe overlay');
  const mismatch=(mode==='wireframe'&&!mat.wireframe)||
    (mode==='xray'&&(!mat.transparent||mat.opacity>.31||mat.depthWrite))||
    (mode==='overlay'&&!hasOverlay)||
    (mode==='shaded'&&(mat.wireframe||hasOverlay||
      (mat.userData?.atelierViewportClone&&mat.transparent&&mat.opacity<.5)));
  if(mismatch){
   if(mode==='shaded'){
    // A geometry rebuild ought to have supplied the native material already.
    // Do not overlay a mode-specific clone or reconstruct a source mesh here.
    const native=material(part);
    if(mesh.material!==native&&!mesh.material.userData?.atelierHDMaterial)mesh.material.dispose?.();
    mesh.material=native;
    for(const child of [...mesh.children]){
     if(child.name==='Viewport wireframe overlay'){
      mesh.remove(child);
      child.material?.dispose?.();
     }
    }
   }else{
    atelierViewModeApply(mesh,part);
   }
  }
 }
 // HD animation loops only draw dirty frames. A geometry edit changes the
 // scene without moving the camera; explicitly request a new visible frame.
 atelierHDDirty=true;
 atelierViewportControlsRefresh();
}
"""

def apply(html):
    html=once(html,
      "  function signalEdited(){",
      REPAIR+"\n  function signalEdited(){")
    html=once(html,
      "  function signalEdited(){",
      "  function signalEdited(){\n    queueMicrotask(atelierViewEnsureAfterGeometryEdit);")
    html=once(html,
      "function atelierViewRebuild(){if(modelRoot)renderParts();}",
      "function atelierViewRebuild(){if(modelRoot){renderParts();atelierHDDirty=true;}}")
    html=once(html,
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_105_SCULPT_UNDO_VIEW_MENU",
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_106_SCULPT_RENDER_MODE_REBUILD")
    for a,b in [
      ("ENGINE · MAKER v11.105","ENGINE · MAKER v11.106"),
      ("v11.105 · undo view preservation and spaced menus",
       "v11.106 · stable viewport mode after sculpt"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.105'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.106'"),
      ("<title>§wyrl§ Engine · Maker v11.105</title>",
       "<title>§wyrl§ Engine · Maker v11.106</title>"),
    ]:html=once(html,a,b)
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Stable render modes when sculpt geometry rebuilds",
     date="2026-10-24",changes=[
      "Preserve the chosen Shaded, X-Ray, Wireframe or Overlay materials across Apply brush and Remove last stroke.",
      "Check that rebuilt mesh materials actually match display mode and reapply display shading only when mismatched.",
      "Mark the HD viewport dirty on geometry edits and display changes so a static camera still redraws.",
      "Keep approved v11.105 menu spacing, panel drag/height, pick marker, touch inputs and all saved meshes intact."
     ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
    raw=html.encode("utf-8")
    print("SWRLZ_V11106_BUILD_MEASURE",len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
