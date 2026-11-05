"""§E v11.274 · toggleable, lightweight viewport Nerd Stats in browser studios.
Retain original Quest VR L3 diagnostics and Sheep Tag's existing browser HUD.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(src, old, new, note):
    count=src.count(old)
    if count!=1:
        raise AssertionError(("v11.274", note, count, old[:100]))
    return src.replace(old, new, 1)

def apply(html):
    hud=(ROOT/"runtime/editor_viewport_nerd_stats_v11_274.js").read_text("utf8")
    for symbol in (
        "window.SWYRL_ENGINE_STRESS_TEST_252=Object.freeze",
        "window.SWYRL_ENGINE_MODEL_STRESS_252=Object.freeze",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265=Object.freeze",
        "window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze",
        "window.SWYRL_ENGINE_PARTICLE_UI_249",
        "window.SWYRL_ENGINE_STUDIOS=Object.freeze"
    ):
        assert symbol in html, ("v11.274 missing prereq",symbol)
    html=once(html, "window.SWRLZ_FORGE_BUILD=",
        hud+"\nwindow.SWRLZ_FORGE_BUILD=", "append native HUD")
    prev=" source.engine='§wyrl§ Engine · Maker v11.273';source.version=11.273;"
    assert html.count(prev)==2, ("v11.274 metadata",html.count(prev))
    html=html.replace(prev,
        " source.engine='§wyrl§ Engine · Maker v11.274';source.version=11.274;")
    for old,new in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_273_ORGANIC_GALAXY_FILAMENTS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_274_VIEWPORT_NERD_STATS"),
        ("ENGINE · MAKER v11.273","ENGINE · MAKER v11.274"),
        ("v11.273 · organic broken galaxy filaments",
         "v11.274 · toggleable editor viewport Nerd Stats"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.273'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.274'"),
        ("<title>§wyrl§ Engine · Maker v11.273</title>",
         "<title>§wyrl§ Engine · Maker v11.274</title>"),
    ):
        html=once(html,old,new,"release identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Optional Nerd Stats HUD in every browser editor viewport",
        date="2026-11-04", changes=[
          "Toggle Nerd Stats in the active Game, Modeling, Particle or Material Studio browser viewport with its small ▥ Nerd Stats button or F3.",
          "Display approximate RAF FPS/frame time, renderer draw calls/triangles, available GPU texture/geometry object counts, viewport size and supported JS heap estimates.",
          "Reuse existing model/particle stress test measurements for actual temporary triangle or particle-buffer counts, without generating new test loads.",
          "Sample only every 800 ms with no new WebGL context, render loop, or gameplay AI scheduling changes.",
          "Hide this browser-only HUD in immersive VR (Quest left-joystick L3 retains existing three-page metrics); Sheep Tag live browser play retains its existing in-game Nerd Stats toggle.",
          "Browser/Quest real-device acceptance remains with the owner."
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
