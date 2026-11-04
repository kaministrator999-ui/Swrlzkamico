"""§E v11.272 — toggle existing VR Nerd Stats using left joystick press (L3).

The WebXR input edge uses standard Gamepad button 3, not analog axes.
The existing world-space metrics panel owns open/close, persisted layout,
texture and stats rendering. No new input loop, render pass or player orders.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(src,before,after):
    assert src.count(before)==1,("v11.272 source anchor",before[:110],src.count(before))
    return src.replace(before,after,1)

def apply(html):
    source=(ROOT/"runtime/sheep_nerd_stats_l3_toggle_v11_272.js").read_text("utf8")
    for symbol in (
        "function se210PanelCreate(", "function se210PanelClose(",
        "function se210Active(", "function se192InputRecord(",
        "function se193XRFrame(", "function se193XRCleanup(",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271",
        "renderer.setAnimationLoop(tick);",
    ):
        assert symbol in html,("v11.272 prerequisite",symbol)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",source+"\nwindow.SWRLZ_FORGE_BUILD=")
    old=" source.engine='§wyrl§ Engine · Maker v11.271';source.version=11.271;"
    assert html.count(old)==2,("v11.272 version metadata",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.272';source.version=11.272;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_271_LAN_VISIBILITY_AUTOFIND",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_272_SHEEP_NERD_L3_TOGGLE"),
        ("ENGINE · MAKER v11.271","ENGINE · MAKER v11.272"),
        ("v11.271 · discoverable LAN multiplayer menu",
         "v11.272 · left-stick click Nerd Stats toggle"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.271'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.272'"),
        ("<title>§wyrl§ Engine · Maker v11.271</title>",
         "<title>§wyrl§ Engine · Maker v11.272</title>"),
    ):
        html=once(html,before,after)
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Sheep Tag VR Nerd Stats toggle on left joystick click (L3)",
      date="2026-11-04",changes=[
        "Click the left Quest controller's thumbstick (WebXR button 3) during immersive Sheep Tag gameplay to show the existing Nerd Stats metrics panel. Release and click L3 again to hide it.",
        "Edge-trigger the physical click only once per press; directional left-stick movement remains unchanged and the button works while the sheep is moving.",
        "Re-use the existing pinned/grabbable three-page stats panel; preserve other workspace panels and saved metric panel layout, without extra canvas or render loop.",
        "Do not open stats in the editor/main menu or from a button held across game/OS overlay transitions. Re-arm cleanly on XR cleanup.",
        "Preserve prior §E v11.271 LAN auto-find and Quest VR menu, v11.270 galaxy wisps, v11.265 rendering optimization, multiplayer authority, and headset controls. Owner physical Quest L3 verification remains required."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
