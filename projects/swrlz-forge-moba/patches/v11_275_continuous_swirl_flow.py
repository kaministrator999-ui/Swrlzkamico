"""§E v11.275: independently circulating motes, with no rewind on timeline loop.

Append new shader-batched particles to each of the two existing galaxy arm
records. All older native particles, stars, colored smoke, and ribbons remain.
Ownership/disposal stays in the v11.251 nebula closure. No independent RAF.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(src,old,new,why):
    n=src.count(old)
    if n!=1:raise AssertionError(("v11.275",why,n,old[:170]))
    return src.replace(old,new,1)

def apply(html):
    source=(ROOT/"runtime/astral_continuous_swirl_v11_275.js").read_text("utf8")
    for term in (
      "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
      "window.SWYRL_ENGINE_VIEWPORT_NERD_STATS_274=Object.freeze",
      "window.SWYRL_ENGINE_SHEEP_NERD_L3_272=Object.freeze",
      "window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271=Object.freeze",
      "function makeInnerTendrils(cfg){",
      "function updateInnerTendrils(t,cfg,rec,origin){",
      "function se264Profile(cfg,arm){",
      "function makeNebulaMist(cfg){",
      "function updateNebulaMist(m,cfg,rec,origin){",
      "renderer.setAnimationLoop(tick);",
    ):
        assert term in html,("v11.275 predecessor guard",term)
    # This is within the existing galaxy closure, so private renderer/THREE,
    # clamp, and scene helpers remain accessible without creating an extra
    # engine owner or global tick.
    html=once(html,"function makeStars(cfg){",
       source+"\nfunction makeStars(cfg){",
       "insert GPU swirl inside established galaxy runtime")

    html=once(html,
      """ const mist=makeNebulaMist(cfg);
 const inner=makeInnerTendrils(cfg);
 r.cloud.add(mist.points);
 r.cloud.add(inner.mesh);
 r.cloud.add(stars.mesh);
 return {bands,stars,mist,inner};""",
      """ const mist=makeNebulaMist(cfg);
 const inner=makeInnerTendrils(cfg);
 const flow=makeContinuousSwirl(cfg);
 r.cloud.add(mist.points);
 r.cloud.add(inner.mesh);
 r.cloud.add(flow.mesh);
 r.cloud.add(stars.mesh);
 return {bands,stars,mist,inner,flow};""",
      "append rather than replace existing effects")
    html=once(html,
      """  r.se251Nebula.inner.mesh.layers.mask=mask;
  r.se251Nebula.stars.mesh.layers.mask=mask;""",
      """  r.se251Nebula.inner.mesh.layers.mask=mask;
  r.se251Nebula.flow.mesh.layers.mask=mask;
  r.se251Nebula.stars.mesh.layers.mask=mask;""",
      "use author's isolated Particle Studio/VR render layer")
    html=once(html,
      """  updateInnerTendrils(rec.se251Nebula.inner,cfg,rec,origin);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
      """  updateInnerTendrils(rec.se251Nebula.inner,cfg,rec,origin);
  updateContinuousSwirl(rec.se251Nebula.flow,cfg,rec,origin,dt);
  updateStars(rec.se251Nebula.stars,cfg,rec,origin);""",
      "advance new monotonic lifetime clock with existing particle step")
    html=once(html,
      """  const inner=r.se251Nebula.inner;
  inner.mesh.removeFromParent();inner.g.dispose();inner.mat.dispose();""",
      """  const inner=r.se251Nebula.inner;
  inner.mesh.removeFromParent();inner.g.dispose();inner.mat.dispose();
  const flow=r.se251Nebula.flow;
  flow.mesh.removeFromParent();flow.geom.dispose();flow.material.dispose();""",
      "dispose supplementary GPU buffer and material with original emitter")

    html=once(html,
      "innerPurpleRootsPerEmitter:ROOT_INNER,slimWispsPerEmitter:ROOT_N-ROOT_INNER,",
      "innerPurpleRootsPerEmitter:ROOT_INNER,slimWispsPerEmitter:ROOT_N-ROOT_INNER,continuousFlowMotesPerEmitter:SE275_N,flowClockIndependent:true,",
      "inspector exposes particle count and continuous clock rationale")
    assert html.count("renderer.setAnimationLoop(tick);")==1
    assert html.count("function makeContinuousSwirl(cfg){")==1
    assert html.count("function updateContinuousSwirl(flow,cfg,rec,origin,dt){")==1
    prev=" source.engine='§wyrl§ Engine · Maker v11.274';source.version=11.274;"
    assert html.count(prev)==2,("v11.275 metadata",html.count(prev))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.275';source.version=11.275;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_274_VIEWPORT_NERD_STATS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_275_CONTINUOUS_SWIRL_FLOW"),
      ("ENGINE · MAKER v11.274","ENGINE · MAKER v11.275"),
      ("v11.274 · toggleable editor viewport Nerd Stats",
       "v11.275 · continuous independent swirl particles"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.274'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.275'"),
      ("<title>§wyrl§ Engine · Maker v11.274</title>",
       "<title>§wyrl§ Engine · Maker v11.275</title>"),
    ):html=once(html,old,new,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Additional continuous vortex flow motes without reversing",
      date="2026-11-04",changes=[
        "Keep the existing purple/cyan spiral arms, galaxy particle motes, stars, nebula clouds, core and slim filaments unchanged. Add 84 independent moving swirl motes per violet/cyan arm emitter.",
        "New particles follow an organic, slowly spinning outward path with independently distributed lifetimes, staggered births and ease-in/ease-out opacity; wrap is fully invisible before each mote respawns.",
        "Use a monotonic per-emitter local clock, not Particle Studio's repeating timeline or older resetting vortex phase. Never visibly jump a mote from the tip backward to the core.",
        "Animate point positions and colors on GPU in two existing emitter-owned batches, with one additional draw call per colored emitter and no new native emitters, animation loops, or WebGL renderers.",
        "Preserve the v11.274 editor Nerd Stats HUD, v11.272 Quest left-stick Nerd Stats, v11.271 multiplayer LAN auto-discovery, modeler, saved project format and viewport controls. Device appearance and FPS remain for owner acceptance."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
