"""§E v11.267 — make the nebula flow as continuous long arms, not stamped leaves.

Owner Moto screenshot: purple/cyan coloration now works, but atlas-derived
smoke stamps are too distinct, too widely scattered, and visually obscure the
primary flowing filament paths. Constrain smoke to tangent-aligned strand
chains, blend soft body haze with detailed brush texture IN THE SAME existing
shader, and strengthen continuous paths. Keep six purple-rooted branches,
short inner tendrils, core halo, undoable smoke controls and engine safety.
No extra scene, WebGL renderer, draw-call batch or frame loop.
"""
import json

def once(s,a,b,label):
    n=s.count(a)
    if n!=1:
        raise AssertionError(("v11.267",label,n,a[:180]))
    return s.replace(a,b,1)

def apply(html):
    # 20 staggered plumes per main strand rather than 24 disjoint leaf stamps;
    # points remain a single GPU buffer and draw call for each arm emitter.
    html=once(html,"const MIST_N=72;","const MIST_N=60;",
              "reduce redundant smoke overdraw without deleting live strands")
    html=once(html,
      "const u=.08+.88*(ordinal+.32+Math.random()*.55)/(MIST_N/3);",
      "const u=.045+.92*(ordinal+.34+Math.random()*.29)/(MIST_N/3);",
      "space plumes evenly along long arms with small path jitter")
    html=once(html,
      "const variation=.82+Math.random()*.54;",
      "const variation=.87+Math.random()*.26;",
      "reduce per-stamp size contrast")
    html=once(html,
      "const size=(.52+1.28*u)*variation;",
      "const size=(.59+1.36*u)*variation;",
      "stretch regular arm segments while allowing broader soft outer trails")
    html=once(html,
      """specs.push({u,branch,phase:(Math.random()-.5)*.15,
    lateral:side*(.035+.28*u),height:(Math.random()-.5)*(.08+.30*u),
    depth:(Math.random()-.5)*(.07+.13*u),size});""",
      """specs.push({u,branch,phase:(Math.random()-.5)*.035,
    lateral:side*(.014+.083*u),height:(Math.random()-.5)*(.025+.105*u),
    depth:(Math.random()-.5)*(.03+.08*u),size});""",
      "keep cloud trails on the curving strand rather than scattered around it")

    # Textures are only the fine brush detail; an independent low-contrast
    # elliptical haze connects puffs at every zoom level. Two layers in
    # existing fragment shader, NOT extra objects or render passes.
    html=once(html,
      "' float angle=1.5707963-vMistAngle+(vMistSeed-.5)*.46;',",
      "' float angle=1.5707963-vMistAngle+(vMistSeed-.5)*.24;',",
      "reduce arbitrary rotation away from screen-projected filament tangent")
    html=once(html,
      "' vec2 p=vec2(cos(angle)*q.x-sin(angle)*q.y,sin(angle)*q.x+cos(angle)*q.y);',",
      """' vec2 rotated=vec2(cos(angle)*q.x-sin(angle)*q.y,sin(angle)*q.x+cos(angle)*q.y);',
 ' vec2 p=rotated*vec2(1.10,.67);',""",
      "elongate each plume along its parent's curved energy line")
    html=once(html,
      "' float radius=length(p*vec2(.89,1.1));',",
      "' float radius=length(p*vec2(.86,1.04));',",
      "shape the softer oblong smoke envelope")
    html=once(html,
      "' float edge=1.0-smoothstep(.58,1.06,radius);',",
      "' float edge=1.0-smoothstep(.38,1.05,radius);',",
      "feather edges more gradually to erase individual stamp outlines")
    html=once(html,
      "' float fallback=(1.0-smoothstep(.15,.86,radius))*.23;',",
      """' float fallback=(1.0-smoothstep(.12,.94,radius))*.19;',
 ' float haze=(1.0-smoothstep(.17,1.04,radius))*.24;',""",
      "provide low-contrast connective nebula beneath brush detail")
    html=once(html,
      "' float wisp=mix(fallback,painted*2.2,uMistAtlasReady);',",
      """' float brush=mix(fallback,painted,uMistAtlasReady);',
 ' float wisp=mix(haze*.70,brush,.46);',""",
      "reduce hard reference-atlas stamp contrast")
    html=once(html,
      "' float shimmer=.88+.12*sin(uMistTime*.11+vMistSeed*13.0);',",
      "' float shimmer=.92+.08*sin(uMistTime*.10+vMistSeed*13.0);',",
      "keep slow living mist without visible pulsing")
    html=once(html,
      "' float alpha=clamp(wisp*edge*uMistDensity*shimmer*.78,0.0,.38);',",
      "' float alpha=clamp((haze*.72+wisp*.55)*edge*uMistDensity*shimmer,0.0,.29);',",
      "connect thin smoke plumes without opaque flat fans")
    html=once(html,
      "' gl_FragColor=vec4(vMistTint*vec3(1.60,1.44,1.73),alpha);',",
      "' gl_FragColor=vec4(vMistTint*vec3(1.40,1.26,1.50),alpha);',",
      "reduce neon leaf contrast and preserve purple-to-cyan strand color")

    # Existing primary filament ribbons now lead visually, tapering
    # toward the ends; no change to half-S paths or slow spin.
    html=once(html,
      """  const grow=u=>b.kind==='filament'?
   .024+u*.010:""",
      """  const grow=u=>b.kind==='filament'?
   .031+u*.014:""",
      "give continuous flowing filaments more readable body at mobile zoom")
    html=once(html,
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.76:.52)*""",
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?1.08:b.index===0?.76:.52)*""",
      "foreground fine energy strands over diffuse smoke")
    html=once(html,
      "'  gl_FragColor=vec4(stream*(1.08+.075*sin(x*64.-uTime*.11)),opacity);',",
      "'  gl_FragColor=vec4(stream*(1.20+.075*sin(x*64.-uTime*.11)),opacity);',",
      "emphasize the purple-rooted long-arm visual hierarchy")

    # Preserve important unrelated changes, especially the exact v11.266
    # JavaScript syntax repair and v11.265 Sheep Tag profiling.
    for marker in (
       "'varying float vMistAngle;',\n 'varying vec3 vMistTint;',",
       "window.SWYRL_ENGINE_SHEEP_NERD_STATS_265",
       "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
       "function makeInnerTendrils(cfg){",
       "function makeCoreHalo(){",
       "function se264Profile(cfg,arm){",
       "const se263AtlasTexture=new THREE.TextureLoader().load(",
       "['nebulaDensity','Smoke density',.1,2,.05,1]",
       "renderer.setAnimationLoop(tick);"
    ):
       assert marker in html, ("v11.267 preserve",marker)

    old=" source.engine='§wyrl§ Engine · Maker v11.266';source.version=11.266;"
    assert html.count(old)==2,("v11.267 metadata",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.267';source.version=11.267;")
    for a,b in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_266_SHADER_ARRAY_BOOT_FIX",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_267_CONTINUOUS_GALAXY_WISPS"),
      ("ENGINE · MAKER v11.266","ENGINE · MAKER v11.267"),
      ("v11.266 · galaxy mist JS syntax and editor boot fix",
       "v11.267 · continuous flowing nebula wisps"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.266'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.267'"),
      ("<title>§wyrl§ Engine · Maker v11.266</title>",
       "<title>§wyrl§ Engine · Maker v11.267</title>")
    ):
       html=once(html,a,b,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Continuous flowing galaxy filaments and blended nebula smoke",
       date="2026-11-04",changes=[
        "Tighten 60 feathered atlas-smoke plumes per vortex color around their six short half-S paths; reduce random radial, vertical and angular scattering for distinct long wisps rather than leaf-like sprite stamps.",
        "Align stretched smoke textures more faithfully with each arm's projected tangent, with less random rotation. Blend a soft connecting haze and artist-derived brush details inside the existing fragment shader—no new render pass.",
        "Raise primary strand visibility slightly while maintaining thin tips and the purple origin/cyan transitions, mixed purple outer splotches and short central violet tendrils.",
        "Retain the purple center halo, live smoke density/arm spread controls, v11.266 parsed boot fix, v11.265 Sheep Tag Nerd Stats/batching, saved projects and emitter error isolation.",
        "Maintain one engine render loop and the same number of native emitters/draw-call batches. Check assembled JavaScript syntax and exact source receipt before deployment; owner mobile visual/performance acceptance remains required."
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
       separators=(",",":")).replace("</","<\\/")+html[at+width:]
