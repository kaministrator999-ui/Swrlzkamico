"""§E v11.191 — Quest 2 immersive black-view recovery.

Use project-owned Arrival Court XR reference-space translation, an unlit
head-visible diagnostic HUD, reliable exit recovery and bounded ray tests.
No scene JSON mutation, parallel WebGL renderer, or automatic browser suite.
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.191 anchor',old[:175],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_black_screen_recovery_v11_191.js').read_text(encoding='utf8')

    # Insert before native animation loop, alongside other native XR handlers.
    html=once(html,
        'let se181MainLoopBooted=false;\nfunction tick(){',
        js+'\nlet se181MainLoopBooted=false;\nfunction tick(){')

    # Keep XR request directly in a user gesture. Framebuffer selection must
    # be configured before activating the XR session, never during headset play.
    html=once(html,
        """  renderer.xr.enabled=true;
  renderer.xr.setReferenceSpaceType('local-floor');
  requested=await navigator.xr.requestSession('immersive-vr',{requiredFeatures:['local-floor']});""",
        """  renderer.xr.enabled=true;
  renderer.xr.setReferenceSpaceType('local-floor');
  se191XRPrepareFramebuffer();
  requested=await navigator.xr.requestSession('immersive-vr',{requiredFeatures:['local-floor']});""")

    html=once(html,
        """  await renderer.xr.setSession(requested);
  se181XR.session=requested;
  se181XR.controllers=[se181XRMakeController(0),se181XRMakeController(1)];
  se181XRMakeExitPanel();""",
        """  await renderer.xr.setSession(requested);
  se181XR.session=requested;
  // XR reference-space offset is separate from the 2D orbit/edit camera.
  se191XRInstallLanding();
  se181XR.controllers=[se181XRMakeController(0),se181XRMakeController(1)];
  se181XRMakeExitPanel();
  se191XRMakeBeacon();
  se191XRStartWatchdog(requested);""")

    # A screen-space diagnostic must appear before any CPU-heavy ray selection.
    html=once(html,
        """  if(renderer.xr.isPresenting){
    se181XRRender();renderer.render(scene,camera);se189Rendered=true;
  }else if(shouldRenderFrame(frameNow)){""",
        """  if(renderer.xr.isPresenting){
    se191XRRenderFrame();
    se181XRRender();renderer.render(scene,camera);se189Rendered=true;
  }else if(shouldRenderFrame(frameNow)){""")

    # This is the expensive per-frame hover path ONLY. Selectstart still uses
    # a fresh native ray hit (so controller precision and authoritative edits
    # remain unchanged).
    html=once(html,
        """ for(const record of se181XR.controllers){
  const hit=se181XRRaycast(record);
  record.ray.scale.z=Math.max(.15,Math.min(hit?.distance||10,24));""",
        """ for(const record of se181XR.controllers){
  const hit=se191XRRayHit(record);
  record.ray.scale.z=Math.max(.15,Math.min(hit?.distance||10,24));""")

    html=once(html,
        """function se181XRRelease(){
 for(const record of se181XR.controllers){""",
        """function se181XRRelease(){
 se191XRCleanup();
 for(const record of se181XR.controllers){""")

    # Provide on-headset first-frame status separately from failure recovery.
    html=once(html,
        """  se181XRNote('Immersive §E active · trigger selects actors · aim at EXIT VR or use Quest menu.');""",
        """  se181XRNote('Immersive §E active · '+se191XR.reason+' · use the illuminated EXIT VR sign or Quest menu to leave.');""")

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_190_RENDER_FPS_VAULT_BATCHING',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_191_XR_BLACK_VIEW_RECOVERY'),
      ('ENGINE · MAKER v11.190','ENGINE · MAKER v11.191'),
      ('v11.190 · render FPS and safe vault batching','v11.191 · Quest VR arrival and black-view diagnostics'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.190'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.191'"),
      ('<title>§wyrl§ Engine · Maker v11.190</title>',
       '<title>§wyrl§ Engine · Maker v11.191</title>')
    ]:html=once(html,old,new)

    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Quest 2 VR entry: arrive inside Dragon Den with an unlit recovery overlay',
      date='2026-10-31',changes=[
        'Place the immersive Quest headset at the project-owned Arrival Court teleport zone through an XRReferenceSpace offset; use the Dragon Den fallback only when an authored zone is unavailable, and leave unrelated games at their own origin.',
        'Show a head-visible, unlit introductory VR diagnostic panel and an EXIT VR sign, even if dark geometry surrounds the headset. The introductory panel disappears after nine seconds.',
        'Return to the normal editor automatically only if absolutely no headset render frames arrive during the first nine seconds; never overwrite a project or discard its editor camera.',
        'Reduce per-frame controller-ray scene traversal to at most once per 95ms per hand; controller selectstart still uses a fresh hit test. One native XR render loop is retained.',
        'Prefer 80% native XR framebuffer scale when the WebXR renderer supports it, configured before opening the session. Ordinary mobile graphics and editor settings remain unchanged.',
        'Keep an inspectable diagnostic API for frame arrival, selected spawn, reference offset, and exit visibility. Physical Quest 2 validation is required to distinguish black compositor frames from a misplaced camera.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
