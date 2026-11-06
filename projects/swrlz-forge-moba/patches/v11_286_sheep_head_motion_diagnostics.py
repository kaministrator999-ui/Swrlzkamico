"""§E v11.286: append observational head-motion vs stationary Sheep Tag VR metrics.
Only adds counters and Nerd Stats pages; XR tracking, game and assets unchanged.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(("v11.286",label,count,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/"runtime/sheep_xr_head_motion_diagnostics_v11_286.js").read_text("utf8")
    for term in (
        "window.SWYRL_ENGINE_QUEST_MENU_CADENCE_278=Object.freeze",
        "window.SWYRL_ENGINE_QUEST_HEADTURN_239=Object.freeze",
        "window.SWYRL_ENGINE_QUEST_LEFT_WRIST_STATS_276=Object.freeze",
        "function se265Lines(s,page){",
        "function se191XRHeadPose(){",
        "function se210Place(panel,pose){",
        "function se195MoveRig(",
        "renderer.setAnimationLoop(tick);",
    ):
        assert term in html,("v11.286 missing prerequisite",term)
    html=once(html,
        "se265Perf.metricPage=(se265Perf.metricPage+1)%4;",
        "se265Perf.metricPage=(se265Perf.metricPage+1)%6;",
        "enable 6-page VR metrics cycle")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        js+"\nwindow.SWRLZ_FORGE_BUILD=",
        "append Sheep Tag head-movement runtime diagnostics")
    old_version=" source.engine='§wyrl§ Engine · Maker v11.285';source.version=11.285;"
    assert html.count(old_version)==3,("v11.286 provenance count",html.count(old_version))
    html=html.replace(old_version,
        " source.engine='§wyrl§ Engine · Maker v11.286';source.version=11.286;")
    for old,new in [
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_285_COMPACT_PROJECT_CATEGORIES",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_286_SHEEP_HEAD_MOTION_DIAGNOSTICS"),
      ("ENGINE · MAKER v11.285","ENGINE · MAKER v11.286"),
      ("v11.285 · compact mobile project library and native starter tabs",
       "v11.286 · Sheep Tag Quest head-motion Nerd Stats"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.285'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.286'"),
      ("<title>§wyrl§ Engine · Maker v11.285</title>",
       "<title>§wyrl§ Engine · Maker v11.286</title>"),
    ]:
        html=once(html,old,new,"runtime identity")
    token="const SE_RELEASE_NOTES="
    at=html.index(token)+len(token)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Quest Sheep Tag head movement performance diagnostics",
      date="2026-11-05",changes=[
       "Add Sheep Tag VR Nerd Stats pages 5/6 and 6/6, with head movement versus stationary frames and callback gap counts.",
       "Compare existing game pose reads, camera-rig reference-space writes, gameplay rays, panel placement and HUD redraw work by headset motion category.",
       "Measure head-direction and headset-position differences using existing WebXR pose reads without creating a new tracking loop.",
       "Report callback gaps and prior-frame draw-call averages as observational diagnostics, not GPU timing or proof of a causal bottleneck.",
       "Preserve existing pages 1–4, left thumbstick toggle and center-page cycling, physics, multiplayer and native HMD tracking.",
       "Quest 2 gameplay acceptance pending: hold head still, turn head with no controller input, then repeat with builds and menus."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
