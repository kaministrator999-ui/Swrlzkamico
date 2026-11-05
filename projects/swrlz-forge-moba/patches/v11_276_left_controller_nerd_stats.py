"""§E v11.276: keep Quest Nerd Stats facing user and following the left controller.

Only active in immersive WebXR Sheep Tag; do not attempt to use non-XR
Quest browser window HTML as a tracked 3D object.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(s,old,new,label):
    n=s.count(old)
    if n!=1: raise AssertionError(("v11.276",label,n,old[:100]))
    return s.replace(old,new,1)
def apply(html):
    source=(ROOT/"runtime/sheep_left_controller_nerd_stats_v11_276.js").read_text("utf8")
    for key in (
      "window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze",
      "function se210PanelFrame(){",
      "function se210PanelCreate(kind){",
      "function se210PanelClose(kind){",
      "function se191XRHeadPose(){",
      "function se192InputRecord(side){",
      "function se193XRFrame(){",
      "function se193XRCleanup(){",
      "window.SWYRL_ENGINE_VIEWPORT_NERD_STATS_274=Object.freeze",
      "function makeContinuousSwirl(cfg){",
    ):
        assert key in html,("v11.276 predecessor required",key)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        source+"\nwindow.SWRLZ_FORGE_BUILD=","add left-hand WebXR metrics follow")
    prev=" source.engine='§wyrl§ Engine · Maker v11.275';source.version=11.275;"
    assert html.count(prev)==2,("v11.276 metadata",html.count(prev))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.276';source.version=11.276;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_275_CONTINUOUS_SWIRL_FLOW",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_276_LEFT_CONTROLLER_NERD_STATS"),
      ("ENGINE · MAKER v11.275","ENGINE · MAKER v11.276"),
      ("v11.275 · continuous independent swirl particles",
       "v11.276 · left-controller VR Nerd Stats"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.275'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.276'"),
      ("<title>§wyrl§ Engine · Maker v11.275</title>",
       "<title>§wyrl§ Engine · Maker v11.276</title>"),
    ): html=once(html,a,b,"runtime identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Quest VR Nerd Stats follows left controller with readable front face",
      date="2026-11-04",changes=[
        "In immersive WebXR Sheep Tag, the existing three-page Nerd Stats panel now tracks the left controller every native XR frame instead of remaining pinned at a world-space location.",
        "Orient its Three.js text front (+Z) toward the tracked headset; fix the reversed/back-facing appearance without disabling depth-safe panel rendering.",
        "Keep left-thumbstick-click L3 show/hide, right-hand menu ray hit detection, page changes, and existing rendering/diagnostic metrics.",
        "If the left controller disconnects temporarily, the same panel moves to a safe headset-relative fallback, never the wrong controller.",
        "Normal floating Quest browser 2D windows cannot offer controller pose to webpage HTML; only immersive WebXR mode can attach native panels.",
        "Do not create another VR render loop, scene, canvas texture, input action or saved layout, and do not touch Sheep Tag AI, LAN, particle studio, galaxy or 2D HUD.",
        "Owner to test wrist position, text orientation, L3 toggle and tracking on Quest 2 in genuine immersive WebXR."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
