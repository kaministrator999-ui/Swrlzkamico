"""§E v11.251 — reference-facing Galaxy Nebula, native editable curves,
five-lane timeline, and shared Model/Materials/Game workstation vocabulary.

Additive to v11.250. Native emitter schema remains backward compatible and
single scene/render loop/Quest controllers remain authoritative.
"""
from pathlib import Path
import json

def once(source,old,new,why):
    n=source.count(old)
    if n!=1:raise AssertionError(("v11.251",why,n,old[:150]))
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    scripts=[
      "particle_curve_runtime_v11_251.js",
      "astral_nebula_settings_v11_251.js",
      "astral_nebula_filaments_v11_251.js",
      "particle_curve_editor_v11_251.js",
      "particle_parameter_timeline_v11_251.js",
      "shared_editor_workstations_v11_251.js",
    ]
    styles=[
      "particle_curve_editor_v11_251.css",
      "particle_parameter_timeline_v11_251.css",
      "shared_editor_workstations_v11_251.css",
    ]
    js="\n".join((root/"runtime"/p).read_text("utf8") for p in scripts)
    css="\n".join((root/"runtime"/p).read_text("utf8") for p in styles)
    # v11.249 wrote emitter rows every 70ms, undoing v11.250's curve-track
    # redraw. The live native timeline remains authoritative until 251 is ready.
    html=once(html,
      " const legend=vq('#se249LayerRows');if(legend){",
      " const legend=vq('#se249LayerRows');if(legend&&!window.SWYRL_ENGINE_PARAMETER_TIMELINE_251){",
      "prevent native frame updates overwriting editable timeline lanes")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
       js+"\nwindow.SWRLZ_FORGE_BUILD=",
       "load native curve runtime, galaxy and shared workstation")
    html=html.replace("</head>",
      '<style id="se251UnifiedStudiosStyle">\n'+css+'\n</style>\n</head>',1)
    # Compatible source provenance and identity. Keep the single renderer and
    # exactly the same project JSON import/export entrypoints.
    prev=" source.engine='§wyrl§ Engine · Maker v11.250';source.version=11.250;"
    if html.count(prev)!=2:
       raise AssertionError(("v11.251 provenance",html.count(prev)))
    html=html.replace(prev,
       " source.engine='§wyrl§ Engine · Maker v11.251';source.version=11.251;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_250_DESKTOP_DOCKS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_251_UNIFIED_GALAXY_CURVES"),
      ("ENGINE · MAKER v11.250","ENGINE · MAKER v11.251"),
      ("v11.250 · resizable desktop/VR Particle Studio and soft vortex",
       "v11.251 · Galaxy Nebula, editable curves and unified studio docks"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.250'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.251'"),
      ("<title>§wyrl§ Engine · Maker v11.250</title>",
       "<title>§wyrl§ Engine · Maker v11.251</title>")
    ):html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Galaxy Nebula and true editable curves across unified editor workstations",
      date="2026-11-04",changes=[
        "Astral Vortex has an upright camera-facing galaxy shape, thin bright spiral filaments fading outward, two outward-widening jagged noise-based smoke layers per arm and multi-size stars in both purple and cyan.",
        "Native validated Smoke arm spread and Starfield density modifiers alter the real effect, with single-renderer budget and cached records; original Sheep Tag and Quest Play are untouched.",
        "The Curves dock is now editable: select Emission/Size/Opacity/Color/Rotation and drag or numerically edit five control points. Changes save through existing native se223Update Undo/Redo and validated project JSON.",
        "The lower Timeline has five corresponding clickable colored parameter tracks, rather than four emitter rows that previously overwrote the intended curves.",
        "Game Engine, Model Atelier, Material & Texture Studio and Particle Studio share dark-violet design tokens and workstation control hierarchy, with native editable Model and Material project explorers, right-side inspectors and resize handles.",
        "Desktop/VR vs Compact remains user-selectable. Models, rigs, materials, game levels, saved positions, physics, networking and Quest controls remain managed by existing native systems.",
        "Owner on-device screenshot comparison and input validation are still required; source build/syntax checks cannot establish pixel-match with a concept rendering."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
      separators=(",",":")).replace("</","<\\/")+html[at+width:]
