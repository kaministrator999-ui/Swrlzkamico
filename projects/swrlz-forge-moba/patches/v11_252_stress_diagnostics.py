"""§E v11.252 — user-controlled model and particle stress diagnostics.
Test geometry is temporary and separate from authored projects and play state.
"""
from pathlib import Path
import json

def once(source,old,new,why):
    n=source.count(old)
    if n!=1:raise AssertionError(("v11.252",why,n,old[:130]))
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    model=(root/"runtime/model_stress_core_v11_252.js").read_text("utf8")
    ui=(root/"runtime/editor_stress_controls_v11_252.js").read_text("utf8")
    css=(root/"runtime/editor_stress_controls_v11_252.css").read_text("utf8")
    # Directly inside the native ModelAtelier closure: use its existing
    # world and renderer rather than spawning a separate WebGL context.
    html=once(html,
        "  function geometry(part){",
        model+"\n  function geometry(part){",
        "insert disposable geometry specimen in native Model Atelier")
    html=once(html,
        "  function close(){\n    if(!panel||panel.hidden)return;",
        "  function close(){\n    se252ModelStop();\n    if(!panel||panel.hidden)return;",
        "release temporary model buffers on native close")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
        ui+"\nwindow.SWRLZ_FORGE_BUILD=",
        "mount independent stress sliders in existing editor docks")
    html=once(html,"</head>",
        '<style id="se252StressDiagnosticsStyle">\n'+css+'\n</style>\n</head>',
        "add scoped stress diagnostic dock styling")
    old=" source.engine='§wyrl§ Engine · Maker v11.251';source.version=11.251;"
    if html.count(old)!=2:raise AssertionError(("v11.252 provenance",html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.252';source.version=11.252;")
    for before,after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_251_UNIFIED_GALAXY_CURVES",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_252_STRESS_DIAGNOSTICS"),
        ("ENGINE · MAKER v11.251","ENGINE · MAKER v11.252"),
        ("v11.251 · Galaxy Nebula, editable curves and unified studio docks",
         "v11.252 · model and particle stress diagnostics"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.251'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.252'"),
        ("<title>§wyrl§ Engine · Maker v11.251</title>",
         "<title>§wyrl§ Engine · Maker v11.252</title>")
    ):html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Native model and particle stress-test sliders",
        date="2026-11-04",changes=[
          "Model Atelier inspector: opt-in slider and exact numeric field from 100 to 1,000,000 requested triangles; Apply generates a real temporary high-subdivision indexed sphere in its own existing WebGL scene. The panel reports the exact generated triangle count and render calls.",
          "Particle Studio inspector: opt-in slider and numeric input from 100 to 1,000,000 animated point particles; the isolated 3D test chamber renders a disposable buffer geometry using its existing renderer and layer.",
          "Stress tests require an explicit Apply action rather than rebuilding while sliding; Stop removes and disposes GPU resources. Leaving the editor or switching project also cleans up temporary load.",
          "Running counts, approximate animation-frame FPS/frame time, and particle buffer update counts are visible in each editor. FPS is a requestAnimationFrame estimate, not a GPU query.",
          "Test specimens never write to saved model parts, emitters, history, project JSON, gameplay collisions, or gameplay performance budget. Native particle emitter limits are unchanged.",
          "All other editor workstations and the Sheep Tag in-game radial menu remain untouched; device-side acceptance is pending."
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
