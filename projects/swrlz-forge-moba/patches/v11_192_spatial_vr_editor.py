"""§E v11.192: first live spatial Quest Game Editor, native actions and stable labels.

One Three renderer and XR animation loop. Reuse native editor selection,
history, actors, prefab creation. Keep modeler and saved projects independent.
"""
from pathlib import Path
import json

def once(s,old,new):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.192 anchor',old[:180],n))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_spatial_editor_v11_192.js').read_text(encoding='utf8')
    html=once(html,
      'let se181MainLoopBooted=false;\nfunction tick(){',
      js+'\nlet se181MainLoopBooted=false;\nfunction tick(){')

    # Genuine XR trigger button. All native UI and scene hit tests now use
    # the exact same calibrated target ray as the visible beam and reticle.
    html=once(html,
      """const onSelect=()=>{if(se181XR.session&&renderer.xr.isPresenting)se181XRSelect(record);};""",
      """const onSelect=()=>{if(se181XR.session&&renderer.xr.isPresenting)se192Select(record);};""")

    html=once(html,
      """ try{hit=se181XRRaycast(record);}catch(e){se191XR.lastError='XR ray: '+String(e?.message||e).slice(0,120);}""",
      """ try{hit=se192Raycast(record);}catch(e){se191XR.lastError='XR ray: '+String(e?.message||e).slice(0,120);}""")

    # Stop rendering the disconnected, thin old line. A 3D tapered ray and
    # a surface cursor now share the same calibrated WebXR targetRaySpace.
    html=once(html,
      """ for(const record of se181XR.controllers){
  const hit=se191XRRayHit(record);
  record.ray.scale.z=Math.max(.15,Math.min(hit?.distance||10,24));
  record.ray.material.color.setHex(hit?0xa4ffa1:(record.index===0?0x65f8fc:0xffd77b));
 }""",
      """ // v11.192: real Quest rays are rendered by the spatial editor adapter.
 // Do not render or raycast the displaced legacy debug lines.
 """)

    # Poll actual Quest gamepad inputs in the single XR frame; don't route
    # raw button events through the 2D simulation-only VR Controller Studio.
    html=once(html,
      """    se191XRRenderFrame();
    se181XRRender();renderer.render(scene,camera);se189Rendered=true;""",
      """    se191XRRenderFrame();
    se181XRRender();se192VRFrame();renderer.render(scene,camera);se189Rendered=true;""")

    html=once(html,
      """  se191XRMakeBeacon();
  se191XRStartWatchdog(requested);""",
      """  se191XRMakeBeacon();
  se191XRStartWatchdog(requested);
  se192VRStart();""")
    html=once(html,
      """function se181XRRelease(){
 se191XRCleanup();""",
      """function se181XRRelease(){
 se192VRCleanup();
 se191XRCleanup();""")

    # For users in immersive editor, expose actual interaction state while
    # still clearly disclosing that full model sculpt is not enabled.
    html=once(html,
      """  nativeSelectionCount:se181XR.selectedCount,
  modelAtelierXR:false,sculptXR:false,locomotionXR:false,""",
      """  nativeSelectionCount:se181XR.selectedCount,
  modelAtelierXR:false,sculptXR:false,locomotionXR:!!se181XR.session,
  spatialEditorXR:!!se181XR.session,""")

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_191_XR_BLACK_VIEW_RECOVERY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_192_XR_SPATIAL_EDITOR'),
      ('ENGINE · MAKER v11.191','ENGINE · MAKER v11.192'),
      ('v11.191 · Quest VR arrival and black-view diagnostics',
       'v11.192 · spatial VR map editor'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.191'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.192'"),
      ('<title>§wyrl§ Engine · Maker v11.191</title>',
       '<title>§wyrl§ Engine · Maker v11.192</title>')
    ]:html=once(html,old,new)

    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Spatial Quest editor: controller-linked tapered beams, locomotion and native scene editing',
      date='2026-10-31',changes=[
       'Render Quest beams directly from calibrated WebXR targetRaySpace for each controller, tapering both ends and showing a surface hit reticle; use the exact same computed ray for trigger selection, palette actions and 3D placement.',
       'Provide an in-world, world-anchored editor palette (select, move, wall, rock, undo, aim trim and exit) that interacts with the existing native editor instead of a disconnected second engine.',
       'Use left stick for free 3D glide, left grip plus stick for vertical flight and right stick for snap-turn. Maintain arrival tracking, scene continuity and native Quest head tracking.',
       'Right grip moves a selected native object by preserving its grab offset; one native transaction is committed per grab for existing undo history. Trigger still selects editor actors; X toggles the tool palette; A switches editor interaction modes.',
       'Convert native WorkspaceStationLabel camera-facing sprites into fixed world-oriented mesh labels only during XR, restoring original sprites and shared textures on exit.',
       'Allow headset-side ray yaw trim with in-world AIM buttons; store only per-device calibration. Model Atelier VR sculpting, two-hand rig transforms, full prefab UI and play-session authority are not claimed.',
       'The normal browser editor, saved scenes and projects, Google login, 2D modeling workspace, VR session and Quest menu exit remain unchanged. Physical Quest controller acceptance pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
