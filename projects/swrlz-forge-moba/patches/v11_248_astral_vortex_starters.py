"""§E v11.248 · Astral Vortex native starter, starter particle tab and violet editor chrome.
Additive release; the single existing WebGL scene, XR input and saved game levels remain authoritative.
"""
from pathlib import Path
import json


def once(src, old, new, description):
    count = src.count(old)
    if count != 1:
        raise AssertionError(("v11.248", description, count, old[:110]))
    return src.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    js = (root / "runtime/astral_vortex_starter_v11_248.js").read_text("utf8")
    css = (root / "runtime/astral_vortex_starter_v11_248.css").read_text("utf8")
    # Feed the original validated emitter schema with four normal presets;
    # no custom project format, second renderer, or hidden actor geometry.
    presets = """const SE223_PRESETS=Object.freeze({
 vortex:{label:'Astral Vortex · violet arm',mode:'continuous',shape:'circle',rate:42,life:3.4,speed:1.7,spread:.3,gravity:0,drag:.1,size:.24,radius:2.15,direction:[0,0,0],startColor:'#ec63ff',endColor:'#812fff',blend:'additive'},
 vortexCyan:{label:'Astral Vortex · cyan arm',mode:'continuous',shape:'circle',rate:40,life:3.4,speed:1.8,spread:.3,gravity:0,drag:.1,size:.23,radius:2.02,direction:[0,0,0],startColor:'#53e4ff',endColor:'#4165ff',blend:'additive'},
 vortexCore:{label:'Astral Vortex · radiant core',mode:'continuous',shape:'sphere',rate:36,life:2.2,speed:.15,spread:.2,gravity:0,drag:.3,size:.33,radius:.16,direction:[0,0,0],startColor:'#ffffff',endColor:'#e876ff',blend:'additive'},
 vortexSpark:{label:'Astral Vortex · flying sparks',mode:'continuous',shape:'sphere',rate:24,life:2.9,speed:.6,spread:1,gravity:0,drag:.2,size:.095,radius:2.4,direction:[0,0,0],startColor:'#eabaff',endColor:'#65d9ff',blend:'additive'},
"""
    html = once(html, "const SE223_PRESETS=Object.freeze({",
                presets, "validated vortex presets")
    # The native stage normally shows only the selected emitter. A selected
    # Vortex component renders its four emitter layers together as ONE starter.
    old = (" const editEmitters=stageActive?data.emitters.filter(e=>"
           "e.id===(se223State.selected||data.emitters[0]?.id)):data.emitters;")
    new = """ const se248Selected=se223State.selected||data.emitters[0]?.id;
 const se248Group=stageActive&&data.emitters.some(e=>e.id===se248Selected&&/^vortex(?:Cyan|Core|Spark)?$/.test(e.preset));
 const editEmitters=stageActive?data.emitters.filter(e=>se248Group?/^vortex(?:Cyan|Core|Spark)?$/.test(e.preset):e.id===se248Selected):data.emitters;"""
    html = once(html, old, new, "preview multi-emitter starter in the one stage")
    html = once(html, "window.SWRLZ_FORGE_BUILD=",
                js + "\nwindow.SWRLZ_FORGE_BUILD=",
                "load native vortex motion and real library UI")
    html = html.replace("</head>",
                        '<style id="se248AstralVortexTheme">\n' + css + '\n</style>\n</head>', 1)
    old_provenance = " source.engine='§wyrl§ Engine · Maker v11.247';source.version=11.247;"
    if html.count(old_provenance) != 2:
        raise AssertionError(("v11.248 source provenance", html.count(old_provenance)))
    html = html.replace(old_provenance,
                        " source.engine='§wyrl§ Engine · Maker v11.248';source.version=11.248;")
    for before, after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_247_EDITOR_PREVIEW_TOGGLES",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_248_ASTRAL_VORTEX_STARTERS"),
        ("ENGINE · MAKER v11.247", "ENGINE · MAKER v11.248"),
        ("v11.247 · Edit-mode particles and cinematic toggles",
         "v11.248 · Astral Vortex and Starter Particles"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.247'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.248'"),
        ("<title>§wyrl§ Engine · Maker v11.247</title>",
         "<title>§wyrl§ Engine · Maker v11.248</title>"),
    ):
        html = once(html, before, after, "release identity")
    key = "const SE_RELEASE_NOTES="
    at = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(
        title="Astral Vortex particle starter and violet/cyan studio chrome",
        date="2026-11-04",
        changes=[
            "Projects → Starter Projects includes a native Starter Particles tab with a working Astral Vortex card.",
            "The starter creates four validated project-native emitters (violet arm, cyan arm, radiant core and sparks) in one undoable transaction, not a decorative screenshot.",
            "Native Particle Studio previews all four vortex layers together in its existing isolated test chamber and original renderer.",
            "Vortex animation uses lightweight 96-point-per-emitter motion, radial glow texture, spiral arms and color interpolation within the existing total particle budget.",
            "Particle Studio has violet/cyan chrome, desktop starter library and project-emitter tree, toolbar actions connected to original create/preview/export controls, and a touch-friendly mobile starter drawer.",
            "Existing saved emitters, user-defined particle data, games, modeling, materials, animations and VR input remain unchanged; physical Moto and Quest acceptance is owner-operated."
        ]
    )
    return html[:at] + json.dumps(
        notes, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + html[at+width:]
