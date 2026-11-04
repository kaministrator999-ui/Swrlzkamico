"""§E v11.247 — independent edit-only particle and cinematic preview toggles.
Append-only; native frame loop, renderer, saved projects and VR Play unchanged.
"""
from pathlib import Path
import json

def once(source,before,after,why):
    count=source.count(before)
    if count!=1:
        raise AssertionError(("v11.247 anchor",why,count,before[:130]))
    return source.replace(before,after,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/"runtime/editor_live_preview_v11_247.js").read_text("utf8")
    css=(root/"runtime/editor_live_preview_v11_247.css").read_text("utf8")
    for required in (
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_246_PARTICLE_BOTTOM_TOGGLE",
      "function se223Frame(dt,t){",
      "animeUpdateCinematic=function(dt){",
      "window.SWYRL_ENGINE_GUI_STUDIO=Object.freeze",
      "window.SWYRL_ENGINE_PARTICLE_STAGE_240",
      "window.SWRLZ_FORGE_BUILD=",
      "const SE_RELEASE_NOTES=",
    ):
        if required not in html:
            raise AssertionError(("v11.247 prerequisite",required))
    html=html.replace("</head>",
       '<style id="se247LivePreviewStyle">\n'+css+'\n</style>\n</head>',1)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
       js+"\nwindow.SWRLZ_FORGE_BUILD=","one UI controller, no new RAF")
    html=once(html,"function se223Frame(dt,t){\n",
       "function se223Frame(dt,t){\n window.SWYRL_ENGINE_EDITOR_PREVIEW_247?.sync?.();\n",
       "reuse existing native particle frame to sync editor state")
    old=" source.engine='§wyrl§ Engine · Maker v11.246';source.version=11.246;"
    if html.count(old)!=2:
        raise AssertionError(("v11.247 saved project provenance",html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.247';source.version=11.247;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_246_PARTICLE_BOTTOM_TOGGLE",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_247_EDITOR_PREVIEW_TOGGLES"),
      ("ENGINE · MAKER v11.246","ENGINE · MAKER v11.247"),
      ("v11.246 · Reliable mobile Particle Studio collapse",
       "v11.247 · Edit-mode particles and cinematic toggles"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.246'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.247'"),
      ("<title>§wyrl§ Engine · Maker v11.246</title>",
       "<title>§wyrl§ Engine · Maker v11.247</title>"),
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Scene editor opt-in live previews",
      date="2026-11-03",changes=[
        "Add a compact Preview button beside Game Engine Scene and GUI/Menus; open the editor-only inspector on demand without crowding the top toolbar.",
        "Independently turn native scene particle emitters on or off while editing; unchecking clears existing particle draws and resets preview state without changing saved VFX.",
        "In the authored cinematic episode, optionally loop its existing timeline in Edit mode with the original storyboard renderer. Stop restores the editor camera.",
        "Unsupported projects display cinematic preview disabled, rather than pretending arbitrary game animations have an authored timeline.",
        "No extra renderers, requestAnimationFrame loops, Play-mode modifications, or new gameplay work. Preview defaults off and resets on project/studio changes.",
        "Moto G Power and Meta Quest 2 real-device acceptance remains owner-operated."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
