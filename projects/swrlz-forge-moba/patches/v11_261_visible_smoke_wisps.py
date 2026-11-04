"""§E v11.261 — restore visible luminous smoke, retain broken-up wispy silhouette.

Moto screenshot of v11.260: six half-S trails and stars visible, clouds near
invisible. Previous v11.259 made opaque translucent sheets; v11.260 over-masked
and left faint alpha-blended pigment on a black viewport. Restore controlled
additive luminance in the SAME existing two ribbon layers, soften the noise
threshold and keep a strict per-fragment alpha cap. No new draw calls.
"""
import json

def once(source, old, new, label):
    count=source.count(old)
    if count!=1:
        raise AssertionError(("v11.261", label, count, old[:150]))
    return source.replace(old,new,1)

def apply(html):
    # Sparse but *visible* clouds. A moderate noise threshold leaves dark
    # pockets, while rounded feather edges prevent fan-like silhouettes.
    html=once(html,
      "'  float holes=smoothstep(.39,.72,cloud);',",
      "'  float holes=smoothstep(.33,.61,cloud);',",
      "keep cloudy areas visible while retaining irregular gaps")
    html=once(html,
      "'  float detail=smoothstep(.28,.66,n3);',",
      "'  float detail=smoothstep(.25,.64,n3);',",
      "restore smoke texture at typical mobile pixel density")
    html=once(html,
      "'  float plume=feather*holes*(.35+.65*detail);',",
      "'  float plume=feather*holes*(.48+.52*detail);',",
      "feathered body with textured variations, not a filled sheet")
    html=once(html,
      "'  float opacity=tip*uOpacity*(.85*plume+.31*wisp);',",
      "'  float opacity=tip*uOpacity*(1.13*plume+.43*wisp);',",
      "bring back discernible nebula and wispy streaks")
    html=once(html,
      "'  gl_FragColor=vec4(uColor*(.70+.80*cloud),clamp(opacity,0.,.58));',",
      "'  gl_FragColor=vec4(uColor*(.95+1.05*cloud),clamp(opacity,0.,.52));',",
      "bright nebula RGB with bounded fragment alpha")
    # Additive smoke is essential to make low alpha read as emission on the
    # black space background. The noise-cut alpha mask prevents v11.259 fans.
    html=once(html,
      "blending:kind==='filament'?THREE.AdditiveBlending:THREE.NormalBlending,",
      "blending:THREE.AdditiveBlending,",
      "restore self-luminous gas rather than black-matted translucent pigment")
    html=once(html,
      "   (.035+Math.pow(u,.83)*(.39+b.index*.15))*widthFactor;",
      "   (.035+Math.pow(u,.83)*(.47+b.index*.18))*widthFactor;",
      "mild outer plume widening, still far narrower than solid v11.259 panels")
    html=once(html,
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.66:.43)*""",
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.76:.52)*""",
      "moderate ribbon smoke intensity without changing filament brightness")
    # Preserve previous fixes as explicit source guards.
    for marker in (
      "['nebulaDensity','Smoke density',.1,2,.05,1]",
      "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
      "const nextPoint=location(Math.min(1,u+.001)",
      "b.se259UVReady",
      "const a=phase+spin+arm*TAU/3+u*3.0+.38*Math.sin(TAU*u)"
    ):
        assert marker in html, ("v11.261 legacy preservation",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.260';source.version=11.260;"
    assert html.count(old)==2,("v11.261 provenance",html.count(old))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.261';source.version=11.261;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_260_NEBULA_WISP_ALPHA_MASK",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_261_LUMINOUS_NEBULA_WISPS"),
      ("ENGINE · MAKER v11.260","ENGINE · MAKER v11.261"),
      ("v11.260 · wispy galaxy smoke alpha-mask correction",
       "v11.261 · visible luminous smoke wisps"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.260'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.261'"),
      ("<title>§wyrl§ Engine · Maker v11.260</title>",
       "<title>§wyrl§ Engine · Maker v11.261</title>")
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Visible nebula wisps, without translucent fan panels",
      date="2026-11-04",changes=[
       "Fix smoke becoming nearly invisible after v11.260 noise masking, as reported in Moto Particle Studio screenshot.",
       "Keep shorter galaxy arms and slowly swirling motion; restore luminous violet/cyan wisps using more readable layered noise and controlled additive smoke blending.",
       "Retain feathered edges, noise-carved gaps and a hard alpha ceiling so the former flat colored fan panels do not return.",
       "Preserve the editor-safe particle error toast, sealed prior fixes, saved Smoke density control, the same smoke ribbons, native emitter budget, and renderer.",
       "Owner Moto/Quest visual and performance verification is still required."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
