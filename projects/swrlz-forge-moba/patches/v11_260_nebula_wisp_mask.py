"""§E v11.260 — undo broad solid translucent galaxy fans.

Append-only fix grounded in Moto screenshot: v11.259's two normal-blended
smoke bands per arm expanded into flat colored fan/pinwheel panels.
Use bounded ribbon width and wispy alpha with noise-carved holes instead
of a uniformly filled translucent sheet. Preserve slow six-arm motion,
existing materials, stars and v11.258 particle-error boundaries.
"""
import json

def once(source, old, new, reason):
    count=source.count(old)
    if count!=1:
        raise AssertionError(("v11.260",reason,count,old[:150]))
    return source.replace(old,new,1)

def apply(html):
    # Most of each smoke triangle must be clear; a solid alpha floor across
    # a meter-wide ribbon reads as a translucent paddle instead of smoke.
    html=once(html,
      """'  float turbulence=.64*n+.36*n2;',
'  float ragged=edge+(n-.5)*.42+(n2-.5)*.22;',
'  float body=1.0-smoothstep(.48,1.04,ragged);',
'  float current=.12*sin(x*28.+y*8.-uTime*.12);',
'  float billows=smoothstep(.19,.73,turbulence+current);',
'  float vein=(edge-.28-.22*n)*5.5;',
'  float wisp=exp(-vein*vein)*.2*n2;',
'  float opacity=tip*uOpacity*(body*(.29+.71*billows)+wisp);',
'  gl_FragColor=vec4(uColor*(.70+.85*turbulence),clamp(opacity,0.,.96));',""",
      """'  float n3=noise2(drift*4.6+vec2(8.4,3.7));',
'  float cloud=.50*n+.33*n2+.17*n3;',
'  float ragged=edge+(n-.5)*.38+(n2-.5)*.24;',
'  float feather=1.0-smoothstep(.24,.85,ragged);',
'  float holes=smoothstep(.39,.72,cloud);',
'  float detail=smoothstep(.28,.66,n3);',
'  float driftLine=edge-(.16+.17*sin(x*21.+n2*3.+uTime*.07));',
'  float wisp=exp(-driftLine*driftLine*18.)*(.24+.76*n2);',
'  float plume=feather*holes*(.35+.65*detail);',
'  float opacity=tip*uOpacity*(.85*plume+.31*wisp);',
'  gl_FragColor=vec4(uColor*(.70+.80*cloud),clamp(opacity,0.,.58));',""",
      "remove uniform smoke fill, add noise-cut gaps and feathery streaks")
    # More subtle soft motion, no extra texture fetch / render pass.
    html=once(html,
      "'  vec2 drift=vec2(x*17.+uTime*.038,y*4.2-uTime*.021);',",
      "'  vec2 drift=vec2(x*18.+uTime*.033,y*5.1-uTime*.019);',",
      "wispy noise aspect scale with slow drift")
    # Avoid the huge overlapping fans from v11.259. Width still grows with
    # arm length but is ~40-55% smaller at the very outer end.
    html=once(html,
      """   (.05+Math.pow(u,.72)*(.88+b.index*.37))*widthFactor;""",
      """   (.035+Math.pow(u,.83)*(.39+b.index*.15))*widthFactor;""",
      "bound smoke-ribbon width; retain outer widening")
    html=once(html,
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.78:.53)*""",
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.66:.43)*""",
      "reduce accumulated alpha from two crossing smoke layers")
    # Keep the UI's user-selected v11.259 smoke density; no schema change.
    assert "['nebulaDensity','Smoke density',.1,2,.05,1]" in html
    assert "window.SWYRL_ENGINE_PARTICLE_ERRORS_258" in html
    assert "const nextPoint=location(Math.min(1,u+.001)" in html
    assert "b.se259UVReady" in html

    old=" source.engine='§wyrl§ Engine · Maker v11.259';source.version=11.259;"
    assert html.count(old)==2,("v11.260 provenance",html.count(old))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.260';source.version=11.260;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_259_SMOKY_GALAXY_ARMS",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_260_NEBULA_WISP_ALPHA_MASK"),
      ("ENGINE · MAKER v11.259","ENGINE · MAKER v11.260"),
      ("v11.259 · layered nebula smoke and density control",
       "v11.260 · wispy galaxy smoke alpha-mask correction"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.259'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.260'"),
      ("<title>§wyrl§ Engine · Maker v11.259</title>",
       "<title>§wyrl§ Engine · Maker v11.260</title>")
    ):
        html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Galaxy smoke correction — feathered wisps, no flat colored fans",
      date="2026-11-04",changes=[
       "Correct wide translucent colored pinwheel/fan panels reported in the latest Moto Particle Studio screenshot.",
       "Narrow smoke ribbons without losing outward growth and replace filled-in opacity with irregular turbulent gaps and narrow feathered wisps.",
       "Keep luminous thin cyan/violet half-S strands, bright core, star particles and slow swirl unchanged; no new render pass or additional emitter.",
       "Keep Smoke density control saved/undoable and all particle-error containment and editor camera/timeline protections intact.",
       "Owner mobile screenshot and performance comparison required for visual acceptance."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
