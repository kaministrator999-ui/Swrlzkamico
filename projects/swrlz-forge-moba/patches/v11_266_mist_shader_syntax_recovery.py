"""§E v11.266 — restore editor boot by correcting malformed mist shader arrays.

In v11.264 a replacement added 'varying float vMistAngle;' to *both*
JavaScript shader source arrays but omitted the JS array-element separator.
The resulting adjacent string literals cause SyntaxError: Unexpected string
at JavaScript parse time, before any per-emitter guard or initialization.
Fix both arrays without modifying shaders, UI, Sheep Tag or release history.
"""
import json

def once(source, before, after, label):
    n=source.count(before)
    if n!=1: raise AssertionError(("v11.266",label,n,before[:130]))
    return source.replace(before,after,1)

def apply(html):
    malformed="'varying float vMistAngle;'\n 'varying vec3 vMistTint;',"
    repaired="'varying float vMistAngle;',\n 'varying vec3 vMistTint;',"
    assert html.count(malformed)==2,("v11.266 expected vertex+fragment syntax errors",html.count(malformed))
    html=html.replace(malformed,repaired)
    assert html.count(repaired)==2
    for marker in (
        "function se264Profile(cfg,arm){",
        "function makeInnerTendrils(cfg){",
        "function makeCoreHalo(){",
        "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
        "const se263AtlasTexture=new THREE.TextureLoader().load(",
        "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
        "window.SWYRL_ENGINE_QUEST_PERFORMANCE_210",
        "renderer.setAnimationLoop(tick);"
    ):
        assert marker in html,("v11.266 preservation",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.265';source.version=11.265;"
    assert html.count(old)==2,("v11.266 metadata",html.count(old))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.266';source.version=11.266;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_265_SHEEP_RENDER_NERD_STATS",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_266_SHADER_ARRAY_BOOT_FIX"),
        ("ENGINE · MAKER v11.265","ENGINE · MAKER v11.266"),
        ("v11.265 · Sheep Tag runtime batching and nerd stats",
         "v11.266 · galaxy mist JS syntax and editor boot fix"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.265'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.266'"),
        ("<title>§wyrl§ Engine · Maker v11.265</title>",
         "<title>§wyrl§ Engine · Maker v11.266</title>")
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Galaxy mist startup syntax recovery",
       date="2026-11-04",changes=[
         "Repair two missing JavaScript commas introduced with v11.264's smoke tangent varyings. Without them, the compiled engine inline script fails to parse and the editor can remain stuck initializing.",
         "Add a release-time JavaScript syntax check of the actual assembled editor script, not just source-string or SHA presence assertions; block publication on parse errors.",
         "Preserve v11.264 purple-origin filaments/core halo/short roots, v11.263 smoke atlas, v11.265 Sheep Tag house optimization/Nerd Stats, and v11.257/v11.258 particle crash recovery.",
         "No new particle features, renderer, or input changes in this emergency initialization fix. Real-device load and scene acceptance remains required."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
       separators=(",",":")).replace("</","<\\/")+html[at+width:]
