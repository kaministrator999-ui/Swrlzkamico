"""§E v11.254: Particle Studio panel/preview/camera hotfix.

Source-traced:
- The Materials shell's v11.251 resize grips leaked into Particle Studio.
- v11.250 dock init ran once on DOMContentLoaded; the v11.249 particle root
  can be lazily created afterwards, leaving its real grips/buttons absent.
- A v11.247 Game Editor preview cleanup could cancel Particle Studio preview.
- Global game pause should not disable the isolated edit-mode particle chamber.
- Camera adjustments should apply immediately, with inspectable distance.
"""
import json

def once(text, before, after, reason):
    n=text.count(before)
    if n!=1:raise AssertionError(("v11.254",reason,n,before[:160]))
    return text.replace(before,after,1)

def apply(html):
    # Once the workstation has mounted its DOM, install real v11.250 dock
    # controls. The v11.250 module has already exported its init method.
    html=once(html,
        " state.installed=true;document.body.dataset.se249Mobile='timeline';",
        " state.installed=true;document.body.dataset.se249Mobile='timeline';\n"
        " window.SWYRL_ENGINE_PARTICLE_DOCKS_250?.init?.();",
        "install real particle grips for late-mounted workspace")

    # v11.251 Materials controls are in the shared se225Shell. They must only
    # be hit-testable/visible while Materials is the active workspace.
    css="""
body[data-se225-workspace=particles] #se225Shell #se251-split-materials-left,
body[data-se225-workspace=particles] #se225Shell #se251-split-materials-right{
 display:none!important;visibility:hidden!important;pointer-events:none!important
}
"""
    html=html.replace("</head>",
        '<style id="se254ParticleDockHotfix">'+css+'</style>\n</head>',1)

    # Edit-mode game previews and particle authoring have separate ownership.
    # The Game Preview teardown should not stop an already active test chamber.
    html=once(html,
        """function stopParticles(){
  if(!state.particles)return;
  state.particles=false;se223State.preview=false;se223State.playingLast=false;""",
        """function stopParticles(){
  if(!state.particles)return;
  state.particles=false;
  if(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())return;
  se223State.preview=false;se223State.playingLast=false;""",
        "do not cancel Particle Studio preview on Game Editor exit")

    # While running the dedicated particle chamber, game mode pause must not
    # prevent native emitter processing; Stop Preview remains authoritative.
    html=once(html,
        " const stageActive=window.SWYRL_ENGINE_PARTICLE_STAGE_240?.frame?.()===true;\n const active=!paused&&(!!playing||!!simulating||se223State.preview);",
        " const stageActive=window.SWYRL_ENGINE_PARTICLE_STAGE_240?.frame?.()===true;\n"
        " const active=stageActive?!!se223State.preview:!paused&&(!!playing||!!simulating||se223State.preview);",
        "isolate edit-mode particle preview from game pause")

    # Stage adjust already changes distance, but make it immediately move the
    # actual native camera when Zoom +/- is clicked rather than waiting for tick.
    html=once(html,
        "if(kind==='zoom'){state.distance=Math.max(3.2,Math.min(23,state.distance+Number(value||0)));return true;}",
        "if(kind==='zoom'){state.distance=Math.max(3.2,Math.min(23,state.distance+Number(value||0)));"
        "if(state.active)frame();return true;}",
        "apply camera zoom immediately")
    html=once(html,
        "      rendererCount:1,layer:LAYER,project:state.project?.name||null,",
        "      rendererCount:1,layer:LAYER,zoomDistance:state.distance,\n"
        "      project:state.project?.name||null,",
        "expose actual chamber zoom distance for targeted diagnosis")

    # Avoid stale visible buttons if the stage is previewing but the previous
    # game preview changed their labels. Refresh the selected emitter UI after
    # the standalone chamber begins.
    html=once(html,
        "      se223State.preview=true;\n      se223Reset();\n      status('Isolated 3D test chamber",
        "      se223State.preview=true;\n      se223Reset();\n"
        "      if(typeof se223UIRefresh==='function')se223UIRefresh();\n"
        "      status('Isolated 3D test chamber",
        "refresh preview button after chamber startup")

    old=" source.engine='§wyrl§ Engine · Maker v11.253';source.version=11.253;"
    assert html.count(old)==2,("v11.254 provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.254';source.version=11.254;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_253_STARTUP_UNFREEZE",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_254_PARTICLE_DOCK_PREVIEW_CAMERA"),
        ("ENGINE · MAKER v11.253","ENGINE · MAKER v11.254"),
        ("v11.253 · release dialog and editor boot freeze hotfix",
         "v11.254 · particle editor dock, preview and zoom repairs"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.253'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.254'"),
        ("<title>§wyrl§ Engine · Maker v11.253</title>",
         "<title>§wyrl§ Engine · Maker v11.254</title>")
    ):html=once(html,before,after,"release identity")

    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Particle editor: correctly docked grips, live preview and camera zoom",
      date="2026-11-04",changes=[
        "Materials editor resize handles no longer appear in the Particle Studio viewport. Each editor now shows and controls only its own dock grips.",
        "Initialize Particle Studio's real draggable splitters and collapse buttons after its root mounts, including when opening the studio after initial page load.",
        "Leaving Game Editor particle preview no longer turns off an active Particle Studio chamber preview, and global game pause no longer blocks isolated VFX edit-mode playback.",
        "Camera Zoom +/− changes the actual authoring camera immediately; camera distance is now exposed for focused diagnostics.",
        "Keep the single WebGL renderer, native emitter schema, 12-emitter library, new stress sliders, saved projects, Sheep Tag gameplay and Quest controls unchanged."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
