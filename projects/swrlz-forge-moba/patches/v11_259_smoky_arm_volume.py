"""§E v11.259 — reference-facing smoke volume for six slow half-S galaxy arms.

Append-only correction to v11.258: broaden and strengthen layered wisps,
preserve visible bright core filaments, and expose an undoable smoke density
control. No new emitter, renderer, timeline, or frame callback.
"""
import json

def once(source,old,new,label):
    count=source.count(old)
    if count!=1:raise AssertionError(("v11.259",label,count,old[:130]))
    return source.replace(old,new,1)

def apply(html):
    # Smoke must be spatial volume, not translucent edges around a neon wire.
    # The two smoke layers are already generated per half-S arm; reuse those.
    html=once(html,
       """'  float jag=.47+.39*n+.16*n2;',
'  float fray=1.0-smoothstep(jag-.28,jag+.23,edge);',
'  float cloud=smoothstep(.24,.73,.55*n+.45*n2);',
'  float smoky=(.31+.69*cloud)*fray;',
'  float glow=(1.0-smoothstep(.0,1.0,edge))*.14;',
'  float opacity=(smoky+glow)*tip*uOpacity;',
'  gl_FragColor=vec4(uColor*(.66+.68*n),opacity);',""",
       """'  float turbulence=.64*n+.36*n2;',
'  float ragged=edge+(n-.5)*.42+(n2-.5)*.22;',
'  float body=1.0-smoothstep(.48,1.04,ragged);',
'  float current=.12*sin(x*28.+y*8.-uTime*.12);',
'  float billows=smoothstep(.19,.73,turbulence+current);',
'  float wisp=exp(-pow((edge-.28-.22*n)*5.5,2.0))*.2*n2;',
'  float opacity=tip*uOpacity*(body*(.29+.71*billows)+wisp);',
'  gl_FragColor=vec4(uColor*(.70+.85*turbulence),clamp(opacity,0.,.96));',""",
       "billowing irregular smoke with soft negative space")
    html=once(html,
      "' vec2 drift=vec2(x*23.+uTime*.045,y*5.7-uTime*.026);',",
      "'  vec2 drift=vec2(x*17.+uTime*.038,y*4.2-uTime*.021);',",
      "coarser smoke mass, slow texture crawl")
    # No extra GPU draw calls: two smoke ribbons already exist for each arm.
    html=once(html,
      "transparent:true,depthWrite:false,side:THREE.DoubleSide,blending:THREE.AdditiveBlending,",
      """transparent:true,depthWrite:false,side:THREE.DoubleSide,
  blending:kind==='filament'?THREE.AdditiveBlending:THREE.NormalBlending,""",
      "smoke needs actual translucent pigment, filament remains emissive")
    html=once(html,
      "mesh.frustumCulled=false;\n return {mesh,geom,mat,kind,index,arm};",
      """mesh.frustumCulled=false;
 // Draw translucent smoke first and the thin additive strand over it.
 mesh.renderOrder=kind==='filament'?8:5+index;
 return {mesh,geom,mat,kind,index,arm};""",
      "layering puts sharp energy strands above diffuse smoke")
    html=once(html,
      """   (.035+Math.pow(u,.86)*(.57+b.index*.22))*widthFactor;""",
      """   (.05+Math.pow(u,.72)*(.88+b.index*.37))*widthFactor;""",
      "widen smoky layers with radial distance from the core")
    html=once(html,
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.95:b.index===0?.46:.30)*
  clamp(cfg.vortexGlow??1,.15,2);""",
      """b.mat.uniforms.uOpacity.value=(b.kind==='filament'?.92:b.index===0?.78:.53)*
  clamp(cfg.vortexGlow??1,.15,2)*
  (b.kind==='filament'?1:clamp(cfg.nebulaDensity??1,.1,2));""",
      "controllable visible smoke, independent of filament brightness")
    # Update immutable UV topology once rather than re-uploading it each frame.
    html=once(html,
      "   uv.setXY(ix,(j===2||j===4||j===5)?u1:u0,(j===1||j===3||j===4)?1:0);",
      """   if(!b.se259UVReady)uv.setXY(ix,
    (j===2||j===4||j===5)?u1:u0,(j===1||j===3||j===4)?1:0);""",
      "avoid redundant per-frame UV writes")
    html=once(html,
      " attr.needsUpdate=true;uv.needsUpdate=true;",
      """ attr.needsUpdate=true;
 if(!b.se259UVReady){uv.needsUpdate=true;b.se259UVReady=true;}""",
      "upload static UV buffer once per ribbon")
    # Native schema-validated control; persists via original project serializer,
    # with native se223Update undo/redo and old-project defaults.
    html=once(html,
      """const specs=[['nebulaSpread','Smoke arm spread',.25,2.5,.05,1],
 ['starDensity','Starfield density',0,1,.05,.75]];""",
      """const specs=[['nebulaSpread','Smoke arm spread',.25,2.5,.05,1],
 ['nebulaDensity','Smoke density',.1,2,.05,1],
 ['starDensity','Starfield density',0,1,.05,.75]];""",
      "expose editable and saved smoke density")
    # Release lineage / identity
    old=" source.engine='§wyrl§ Engine · Maker v11.258';source.version=11.258;"
    assert html.count(old)==2,("v11.259 provenance",html.count(old))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.259';source.version=11.259;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_258_SLOW_NEBULA_FAULT_GUARD",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_259_SMOKY_GALAXY_ARMS"),
      ("ENGINE · MAKER v11.258","ENGINE · MAKER v11.259"),
      ("v11.258 · slow half-S nebula and isolated particle errors",
       "v11.259 · layered nebula smoke and density control"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.258'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.259'"),
      ("<title>§wyrl§ Engine · Maker v11.258</title>",
       "<title>§wyrl§ Engine · Maker v11.259</title>")
    ):html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Galaxy nebula smoke volume and editable density",
      date="2026-11-04",changes=[
       "Retain six slow half-S arms from v11.258, but expand their two existing smoke bands into visible outward-widening irregular violet and cyan clouds.",
       "Introduce slower turbulence and translucent pigment blending so the effect reads as feathery nebula clouds around the bright additive filament, not neon wire outlines.",
       "Expose saved, undoable Smoke density (0.1–2.0) alongside Smoke arm spread and Starfield density; older projects default safely without changing imported emitters.",
       "Avoid redundant UV geometry updates each animation frame and reuse the same ribbons, emitter count, GPU renderer and editor camera.",
       "Keep the v11.257 TDZ repair and v11.258 per-emitter fault isolation and editor error toasts. On-device phone/Quest visual and performance acceptance remains pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,
        separators=(",",":")).replace("</","<\\/")+html[at+width:]
