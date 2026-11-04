"""§E v11.269 — match the owner's luminous, densely wound galaxy reference.

On the Moto screenshot the six half-S wisps remain a loose scatter of neon
patches, not the reference's coherent spiral. Change the shared arm trajectory,
the native flowing particles, and existing smoke batches together. No extra
renderer, frame loop, native emitter, or texture; preserve error isolation,
editor gestures, LAN multiplayer and Sheep Tag diagnostics.
"""
import json

def once(source, old, new, label):
    count=source.count(old)
    if count != 1:
        raise AssertionError(("v11.269",label,count,old[:150]))
    return source.replace(old,new,1)

def apply(html):
    # Existing ribbon, mist, stars, and violet roots all call location().
    # The larger turn makes a connected whorl rather than three loose S's.
    html=once(html,
        "const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u);",
        "const a=phase+spin+arm*TAU/3+u*4.85+.18*Math.sin(TAU*u);",
        "tighter curved spiral trajectory")
    # Older native star particles use the same conceptual trajectory.
    html=once(html,
        "const t=angle+u*3.0+.38*Math.sin(TAU*u);",
        "const t=angle+u*4.85+.18*Math.sin(TAU*u);",
        "native points track rendered spiral rather than stray tangents")
    # Fade the light streams away gradually instead of a blunt outer stop.
    html=once(html,
        "' float tip=smoothstep(.005,.07,x)*(1.0-smoothstep(.79,1.0,x));',",
        "' float tip=smoothstep(.008,.07,x)*(1.0-smoothstep(.68,1.0,x));',",
        "long tapered outer light tails")
    # Keep the two smoke batches (one for each colored native emitter) but
    # overlap slightly more feathered puffs along the same spiral.
    html=once(html,"const MIST_N=60;","const MIST_N=72;",
              "24 contiguous textured puffs per branch")
    html=once(html,
        "const u=.045+.92*(ordinal+.34+Math.random()*.29)/(MIST_N/3);",
        "const u=.018+.96*(ordinal+.31+Math.random()*.24)/(MIST_N/3);",
        "smoke traces from violet core to outer rim")
    html=once(html,
        "const variation=.87+Math.random()*.26;",
        "const variation=.92+Math.random()*.17;",
        "small instead of abrupt smoke size variations")
    html=once(html,
        "const size=(.59+1.36*u)*variation;",
        "const size=(.76+1.42*u)*variation;",
        "slightly overlapping clouds without a larger sprite cap")
    html=once(html,
        "lateral:side*(.014+.083*u),height:(Math.random()-.5)*(.025+.105*u),",
        "lateral:side*(.014+.072*u),height:(Math.random()-.5)*(.018+.085*u),",
        "keep clouds hugging filament paths")
    html=once(html,
        "' float alpha=clamp((haze*.72+wisp*.55)*edge*uMistDensity*shimmer,0.0,.29);',",
        "' float alpha=clamp((haze*.90+wisp*.54)*edge*uMistDensity*shimmer,0.0,.30);',",
        "continuous low-opacity smoky body under brush wisps")
    # The core is a luminous hotspot inside purple halo, not a giant white orb.
    html=once(html,
        "rec.material.size=cfg.preset==='vortexCore'?Math.min(.20,cfg.size):",
        "rec.material.size=cfg.preset==='vortexCore'?Math.min(.14,cfg.size):",
        "smaller sharp white core with preserved violet glow")
    # Brighter but narrower star flares; all existing point buffers reused.
    html=once(html,
        "' float halo=.24*(1.0-smoothstep(.02,.48,r));',",
        "' float halo=.17*(1.0-smoothstep(.02,.47,r));',",
        "replace round stars with fine sparkling points")
    html=once(html,
        "' float ray=.32*exp(-abs(p.x)*32.0)*(1.0-smoothstep(.05,.48,abs(p.y)));',",
        "' float ray=.46*exp(-abs(p.x)*45.0)*(1.0-smoothstep(.05,.48,abs(p.y)));',",
        "fine vertical star flares")
    html=once(html,
        "' ray+=.32*exp(-abs(p.y)*32.0)*(1.0-smoothstep(.05,.48,abs(p.x)));',",
        "' ray+=.46*exp(-abs(p.y)*45.0)*(1.0-smoothstep(.05,.48,abs(p.x)));',",
        "fine horizontal star flares")
    for marker in (
        "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_SHEEP_VR_LAN_268",
        "function se264Profile(cfg,arm){",
        "function makeInnerTendrils(cfg){",
        "function makeCoreHalo(){",
        "const se263AtlasTexture=new THREE.TextureLoader().load(",
        "renderer.setAnimationLoop(tick);",
        "['nebulaDensity','Smoke density',.1,2,.05,1]",
    ):
        assert marker in html,("v11.269 preservation",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.268';source.version=11.268;"
    assert html.count(old)==2,("v11.269 version metadata",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.269';source.version=11.269;")
    for a,b in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_268_QUEST_LAN_MAIN_MENU",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_269_REFERENCE_SPIRAL_WISPS"),
        ("ENGINE · MAKER v11.268","ENGINE · MAKER v11.269"),
        ("v11.268 · Quest Sheep Tag multiplayer LAN menu",
         "v11.269 · cohesive spiral galaxy wisps"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.268'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.269'"),
        ("<title>§wyrl§ Engine · Maker v11.268</title>",
         "<title>§wyrl§ Engine · Maker v11.269</title>"),
    ):
        html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Tighter purple/cyan vortex with continuous tapered energy and smoke",
        date="2026-11-04",changes=[
            "Reshape all six half-S wisps into denser, continuous spiral arms using the same shared trajectory for bright ribbons, short violet roots, stars, smoke, and native particles.",
            "Extend the nebula's existing two batched smoke buffers from 60 to 72 overlapping reference-textured puffs each; preserve opacity, gradients, artist mask, and user smoke controls.",
            "Strengthen low-opacity connecting haze, taper the filament trails, sharpen stellar flares, and reduce oversized white core while retaining the magenta halo.",
            "Preserve Particle Studio pan/orbit/zoom/timeline, v11.258 emitter fault boundary, v11.265 Nerd Stats, v11.268 Quest LAN, single WebGL renderer and animation loop.",
            "Owner Moto and Quest appearance/performance acceptance remains outstanding."
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
