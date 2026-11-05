"""§E v11.278: give controller-mounted metrics breathing room, reduce HUD repaints,
and expose approximate callback cadence by open-menu state without changing gameplay.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,a,b,reason):
    count=html.count(a)
    if count!=1:
        raise AssertionError(("v11.278",reason,count,a[:130]))
    return html.replace(a,b,1)
def apply(html):
    source=(ROOT/"runtime/sheep_quest_menu_cadence_v11_278.js").read_text("utf8")
    for symbol in (
        "window.SWYRL_ENGINE_QUEST_LEFT_WRIST_STATS_276=Object.freeze",
        "window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze",
        "function se265Lines(s,page){",
        "function se210CanvasRender(panel){",
        "function se210PanelPress(hit){",
        "function se193XRFrame(){",
        "function se193XRCleanup(){",
        "window.SWYRL_ENGINE_CURVE_LIVE_277=api;",
        "renderer.setAnimationLoop(tick);"
    ):
        assert symbol in html,("v11.278 missing prerequisite",symbol)
    html=once(html,
       "hand.localToWorld(se276StatsWrist.offset.clone())",
       "hand.localToWorld(se278StatsScratch.copy(se276StatsWrist.offset))",
       "reuse controller-space HUD vector on each XR callback")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        source+"\nwindow.SWRLZ_FORGE_BUILD=","append tracked menu cadence and wrist spacing")
    assert html.count("renderer.setAnimationLoop(tick);")==1
    prev=" source.engine='§wyrl§ Engine · Maker v11.277';source.version=11.277;"
    assert html.count(prev)==2,("v11.278 source version anchor",html.count(prev))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.278';source.version=11.278;")
    for old,new in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_277_LIVE_PRECISION_CURVES",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_278_QUEST_MENU_CADENCE"),
        ("ENGINE · MAKER v11.277","ENGINE · MAKER v11.278"),
        ("v11.277 · precision curve live preview",
         "v11.278 · Quest metrics wrist clearance and menu cadence"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.277'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.278'"),
        ("<title>§wyrl§ Engine · Maker v11.277</title>",
         "<title>§wyrl§ Engine · Maker v11.278</title>"),
    ):html=once(html,old,new,"runtime identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Quest Nerd Stats wrist clearance and menu cadence comparison",
       date="2026-11-04",changes=[
        "Move the existing left-controller mounted native VR metrics panel 12 cm farther forward and 6 cm higher for a more comfortable reading distance; preserve the existing full-size, readable text and L3 toggle.",
        "Reuse a single scratch Vector3 for controller-local position transformation instead of allocating one each XR frame; no new tracking or rendering loop.",
        "Reduce ordinary metrics CanvasTexture refresh frequency to about every two seconds under immersive VR load; ensure center-click page changes and first draws still update immediately.",
        "Add optional VR Nerd Stats page 4/4, showing approximate measured XR callback frame time when both panels are closed, stats only, radial menu only, or both visible, with sample counts. These observational measurements are NOT GPU timing or controlled benchmarks.",
        "Leave existing menu ray casting, game AI, LAN authority, camera input and all 3 original diagnostics pages untouched. Particle Studio precision curves, nebula and other editors remain unchanged.",
        "On-Quest verification: compare FPS and page 4 samples while opening/closing stats and build menus at the same house count. Any underlying GPU/rendering bottleneck remains an independent issue."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
