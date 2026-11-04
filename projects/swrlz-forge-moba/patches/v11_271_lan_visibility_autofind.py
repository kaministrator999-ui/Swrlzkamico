"""§E v11.271 — show LAN in Sheep Tag's browser preview and Quest VR main menu,
with automatic live-room discovery on opening multiplayer. Preserve the existing
WebRTC, LAN Bridge, simulation and v11.270 galaxy render pipeline.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new):
    found=html.count(old)
    if found!=1:raise AssertionError(("v11.271 missing anchor",old[:100],found))
    return html.replace(old,new,1)

def apply(html):
    script=(ROOT/"runtime/sheep_lan_visibility_autofind_v11_271.js").read_text("utf8")
    for marker in (
      "window.SWYRL_ENGINE_SHEEP_VR_LAN_268",
      "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
      "function se195RadialHit(", "function se195HandleAction(",
      "function se146Install(", "function se146Open(",
      "function se159Start(", "function se159Probe(",
      "function seLevelsPlayMenu(", "function seLevelsEnsureUI(",
      "function makeNebulaMist(", "renderer.setAnimationLoop(tick);"
    ):
      assert marker in html,("v11.271 required predecessor",marker)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      script+"\nwindow.SWRLZ_FORGE_BUILD=")
    old=" source.engine='§wyrl§ Engine · Maker v11.270';source.version=11.270;"
    assert html.count(old)==2,("v11.271 metadata",html.count(old))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.271';source.version=11.271;")
    for a,b in (
       ("SWYRL_ENGINE_DEPLOY_MARKER: V11_270_HAIRLINE_GALAXY_WISPS",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_271_LAN_VISIBILITY_AUTOFIND"),
       ("ENGINE · MAKER v11.270","ENGINE · MAKER v11.271"),
       ("v11.270 · fine secondary galaxy wisps",
        "v11.271 · discoverable LAN multiplayer menu"),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.270'",
        "window.SWRLZ_FORGE_BUILD={version:'v11.271'"),
       ("<title>§wyrl§ Engine · Maker v11.270</title>",
        "<title>§wyrl§ Engine · Maker v11.271</title>"),
    ):html=once(html,a,b)
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Find Sheep Tag LAN multiplayer from browser and Quest VR menus",
      date="2026-11-04",changes=[
        "Add a visible LOCAL LAN · FIND GAMES button directly to the Sheep Tag editable browser menu preview. Clicking it launches the actual runtime multiplayer browser without changing the authored level or editor save state.",
        "Always expose a high-contrast Local LAN button alongside Play in the full browser main menu, preserving the original network and close/back actions.",
        "Automatically probe the existing public HTTPS room directory when multiplayer opens; show available verified rooms and live status. On the local HTTP LAN Bridge, refresh the real local directory. Public HTTPS grouping is by shared network exit and cannot scan private Wi-Fi addresses.",
        "Add a distinct world-pinned controller-selectable LOCAL LAN tile alongside the existing main VR radial so it is obvious and accessible without searching through editor tools. Intercepts real controller ray hits and prevents selecting scenery behind it.",
        "Preserve v11.270 galaxy thin wisps, v11.269 spiral arms, v11.268 multiplayer code, v11.265 Nerd Stats and house batching, single renderer, WebXR input controls and match simulation. Physical Quest and two-device live discovery remain to be tested."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
