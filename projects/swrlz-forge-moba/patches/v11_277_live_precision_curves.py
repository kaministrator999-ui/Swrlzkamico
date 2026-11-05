"""§E v11.277: precision curve handles with live renderer sampling and one undo.

Replace the old five-point graph entirely because it destroyed captured
pointer targets on every move. Leave native emitter validation, saved schema,
renderer, timeline and undo transaction API in charge.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def once(source, old, new, label):
    n=source.count(old)
    if n!=1:raise AssertionError(("v11.277",label,n,old[:150]))
    return source.replace(old,new,1)

def apply(html):
    editor=(ROOT/"runtime/particle_curve_editor_live_v11_277.js").read_text("utf8")
    css=(ROOT/"runtime/particle_curve_editor_live_v11_277.css").read_text("utf8")
    for symbol in (
      "window.SWYRL_ENGINE_VIEWPORT_NERD_STATS_274=Object.freeze",
      "window.SWYRL_ENGINE_SHEEP_LEFT_NERD_276",
      "window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271",
      "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
      "function se251CurveValue(cfg,key,t){",
      "function se251CurveValidate(value){",
      "function se223Update(id,changes){",
      "renderer.setAnimationLoop(tick);",
      "window.SWYRL_ENGINE_PARAMETER_TIMELINE_251=Object.freeze",
    ):
      assert symbol in html,("prerequisite",symbol)
    html=once(html,
       " const v=cfg?.curves?.[key]||SE251_CURVE_DEFAULTS[key];",
       " const v=window.SWYRL_ENGINE_CURVE_LIVE_277?.value?.(cfg,key)||cfg?.curves?.[key]||SE251_CURVE_DEFAULTS[key];",
       "renderer reads transient drag values without mutating saved model")
    # The bundled v11.251 editor is a self-contained IIFE directly before
    # the five-lane timeline IIFE. Preserve the latter exactly.
    start="// §E v11.251 — native five-point editable particle curves. No fake keyframe state."
    end="// §E v11.251: real 5-channel timeline, linked to editable saved Curves."
    assert html.count(start)==1 and html.count(end)==1
    a=html.index(start)
    b=html.index(end,a)
    old=html[a:b]
    for symbol in (
      "graph.replaceChildren();",
      "function updateDraft(index,v){",
      "function saveDraft(){",
      "window.SWYRL_ENGINE_PARTICLE_CURVES_251=Object.freeze",
    ): assert symbol in old,("legacy curve contract drift",symbol)
    html=html[:a]+editor+"\n"+html[b:]
    html=once(html,"</head>",
       "<style id=\"se277PrecisionCurveStyle\">\n"+css+"\n</style>\n</head>",
       "install scoped precision curve CSS")
    for marker in (
      "window.SWYRL_ENGINE_CURVE_LIVE_277=api;",
      "window.SWYRL_ENGINE_PARTICLE_CURVES_251=api;",
      "function move(e){",
      "function stage(i,value){",
      "function commit(){",
      "updateLane(arr);",
      "window.SWYRL_ENGINE_PARAMETER_TIMELINE_251=Object.freeze",
      "window.SWYRL_ENGINE_SHEEP_LEFT_NERD_276",
    ):assert marker in html,("v11.277 preservation",marker)
    assert html.count("renderer.setAnimationLoop(tick);")==1
    prev=" source.engine='§wyrl§ Engine · Maker v11.276';source.version=11.276;"
    assert html.count(prev)==2,("v11.277 engine metadata",html.count(prev))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.277';source.version=11.277;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_276_LEFT_CONTROLLER_NERD_STATS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_277_LIVE_PRECISION_CURVES"),
      ("ENGINE · MAKER v11.276","ENGINE · MAKER v11.277"),
      ("v11.276 · left-controller VR Nerd Stats",
       "v11.277 · precision curve live preview"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.276'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.277'"),
      ("<title>§wyrl§ Engine · Maker v11.276</title>",
       "<title>§wyrl§ Engine · Maker v11.277</title>"),
    ):html=once(html,before,after,"release identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Precision particle curve graph with live GPU/particle preview",
      date="2026-11-04",changes=[
        "Keep stable five-point SVG hit targets and pointer capture throughout touch, pen and mouse drags; do not replace graph nodes mid-gesture. Tap graph near a point, or drag a handle without snapping values on pointer-down.",
        "Add Fine ×10 drag sensitivity, Shift/Alt fine movement, 0.1-percent numeric fields and accessible arrow-key control with optional 0.1-percent nudging.",
        "Stage only a temporary curve overlay while dragging. Native se251CurveValue samples it every regular particle frame, updating size, emission, opacity, color and rotational envelopes live with no saved-model mutation.",
        "Update the graph value readout and selected animation lane immediately during a gesture; commit once on release through native se223Update for a single undo step, or rollback on cancellation.",
        "Retain existing five-point curve schema, editor docks, galaxy, continuous flow, all VR features including left-controller Nerd Stats, Sheep Tag LAN, single renderer and original animation loop.",
        "Mobile Moto touch feel, GPU appearance and Quest acceptance remain for owner to test."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
