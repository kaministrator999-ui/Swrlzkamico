"""§E v11.245: actual header-only Particle Studio inspector collapse.

Append-only visual/control change. Retains v11.243 Compact/Expand mode,
v11.240 preview renderer, saved VFX definitions and all game and VR paths.
"""
from pathlib import Path
import json


def once(source, before, after, label):
    count=source.count(before)
    if count!=1:
        raise AssertionError(("v11.245 source anchor",label,count,before[:120]))
    return source.replace(before,after,1)


def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/"runtime/particle_inspector_collapse_v11_245.js").read_text(encoding="utf8")
    css=(root/"runtime/particle_inspector_collapse_v11_245.css").read_text(encoding="utf8")
    for expected in (
      "function se225Hide(clearRoute=false)",
      "delete document.body.dataset.se243InspectorOpen;",
      "window.SWYRL_ENGINE_PARTICLE_STAGE_240",
      "id=\"se243ParticleLayout\"",
      "function se223Install()",
      "function se223UIRefresh()",
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_244_SHEEP_MENU_GRASS_REMOVAL",
      "window.SWRLZ_FORGE_BUILD=",
    ):
        if expected not in html:
            raise AssertionError(("v11.245 missing prerequisite",expected))
    # Assembled source includes a second inert documentation head; inject only first.
    html=html.replace("</head>",
        '<style id="se245ParticleCollapseStyle">\n'+css+'\n</style>\n</head>',
        1)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        js+"\nwindow.SWRLZ_FORGE_BUILD=",
        "single owner of collapsed inspector behavior")
    html=once(html,
        "function se225Hide(clearRoute=false){\n delete document.body.dataset.se243InspectorOpen;",
        "function se225Hide(clearRoute=false){\n"
        " window.SWYRL_ENGINE_PARTICLE_COLLAPSE_245?.reset?.();\n"
        " delete document.body.dataset.se243InspectorOpen;",
        "reset collapse and touch focus on studio exit")

    old=" source.engine='§wyrl§ Engine · Maker v11.244';source.version=11.244;"
    if html.count(old)!=2:
        raise AssertionError(("v11.245 native project provenance",html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.245';source.version=11.245;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_244_SHEEP_MENU_GRASS_REMOVAL",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_245_PARTICLE_INSPECTOR_COLLAPSE"),
      ("ENGINE · MAKER v11.244","ENGINE · MAKER v11.245"),
      ("v11.244 · Sheep Tag menu, grass and destruction performance",
       "v11.245 · Particle Studio true inspector collapse"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.244'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.245'"),
      ("<title>§wyrl§ Engine · Maker v11.244</title>",
       "<title>§wyrl§ Engine · Maker v11.245</title>"),
    ):
        html=once(html,before,after,"release identity")
    marker="const SE_RELEASE_NOTES="
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(
      title="Particle Studio inspector now collapses to a small bottom bar",
      date="2026-11-03",
      changes=[
        "Add an explicit Collapse / Show controls button to the native Particle Studio inspector header, separate from the existing Compact/Expand control.",
        "Collapsed state hides editor settings and reduces the bottom inspector to a 59px header bar, giving the 3D effects chamber its full mobile height.",
        "Restoring reuses the same live emitter controls and preserves each section, values and prior Compact/Expand mode without rebuilding the particle editor.",
        "Reset collapsed accessibility and size state when leaving Particle Studio. Preserve the close button, Chat overlay, material/model/game tabs and all project and Quest behavior.",
        "Owner Moto G Power and Quest Browser manual tests still required."
      ]
    )
    return html[:at]+json.dumps(notes,ensure_ascii=False,
                               separators=(",",":")).replace("</","<\\/")+html[at+width:]
