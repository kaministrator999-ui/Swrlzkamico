"""§E v11.273 — replace decorative neon rings with organic, broken spectral wisps.

Owner 5:51 Moto screenshot: coherent spiral restored but secondary filaments
are over-bright smooth circular arcs and mist looks like disjoint stamps.
Keep the established vortex and batch count; reshape its existing filaments,
short wisps and smoke. Preserve v11.271 LAN and v11.272 Quest L3 metrics.
"""
import json

def once(source,old,new,label):
    count=source.count(old)
    if count!=1:raise AssertionError(("v11.273",label,count,old[:160]))
    return source.replace(old,new,1)

def apply(html):
    # The shared spiral carries native particles, stars, smoke, and primary
    # strands. Small deterministic turbulence makes all of them flow together.
    html=once(html,
      "const a=phase+spin+arm*TAU/3+u*4.85+.18*Math.sin(TAU*u);",
      "const a=phase+spin+arm*TAU/3+u*4.85+.18*Math.sin(TAU*u)\n  +u*(.072*Math.sin(u*8.7+arm*2.3)+.025*Math.sin(u*23.+arm*4.1));",
      "subtle nonlinear ripple without breaking shared trajectory")
    # Main ribbons should resemble luminous fibers, not six perfect
    # equally bright illuminated roads.
    html=once(html,
      "'  float opacity=tip*(.73*core+.21*halo)*pulse*uOpacity;',",
      """'  float rough=noise2(vec2(x*21.+uBranch*2.4,uTime*.015));',
'  float gaps=smoothstep(.14,.66,rough);',
'  float sparkle=.86+.14*sin(x*47.+uBranch*1.8-uTime*.09);',
'  float opacity=tip*(.66*core+.18*halo)*pulse*uOpacity*(.36+.64*gaps)*sparkle;',""",
      "modulate neon ribbon alpha with soft glints and irregular dark passages")
    html=once(html,
      "'  gl_FragColor=vec4(stream*(1.20+.075*sin(x*64.-uTime*.11)),opacity);',",
      "'  gl_FragColor=vec4(stream*(1.08+.13*sin(x*64.-uTime*.11)),opacity);',",
      "less uniformly hot neon filament")
    html=once(html,
      "   .034+u*.015:",
      "   (.009+.024*Math.pow(Math.sin(Math.PI*u),.72))*(.91+.09*Math.sin(u*29.+b.arm*3.));",
      "narrow primary energy lines with gradual tapered edges")
    # Keep same smoke billboard count and derived atlas, but remove sharp
    # rectangular individual sprite impressions.
    html=once(html,
      "' float edge=1.0-smoothstep(.38,1.05,radius);',",
      "' float edge=1.0-smoothstep(.21,.91,radius);',",
      "soft feathered smoke edges")
    html=once(html,
      "' float alpha=clamp((haze*.82+wisp*.50)*edge*uMistDensity*shimmer,0.0,.265);',",
      "' float alpha=clamp((haze*.87+wisp*.44)*edge*uMistDensity*shimmer,0.0,.245);',",
      "low-contrast haze no blocky stamped smoke")
    # Existing one draw-call secondary root mesh per native colored emitter.
    # Do not increase point, material, native emitter or GPU batch count.
    a=html.index("const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;")
    b=html.index("// Purple light bloom around the EXISTING white/hot core emitter.",a)
    assert html.count("const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;")==1
    assert "function se270WispSpec(k,cfg){" in html[a:b]
    assert "function updateInnerTendrils(t,cfg,rec,origin){" in html[a:b]
    roots=r"""
const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;
// Natural strand distribution: 3 central violet shoots, 4 short/mid daughter
// wisps and 2 longer escaping energy tails in each native color emitter.
function se270WispSpec(k,cfg){
 const inner=k<ROOT_INNER, n=k-ROOT_INNER;
 const lengths=[.35,.53,.29,.68,.43,.76];
 const starts=[.080,.110,.052,.175,.140,.195];
 return {
  inner,
  start:inner?.012+k*.012:starts[n],
  length:inner?.16+k*.085:lengths[n],
  arm:inner?k+.38:(n%3)+(n<3?.075:-.095),
  offset:inner?0:(n%2?-.034:.042),
  bend:inner?.018:(.065+.022*(n%3))*(n%2?1:-1),
  depth:inner?0:(n%3-1)*.033,
  phase:n*1.73+k*.37,
  blue:!inner&&(cfg.preset==='vortexCyan'||n===1||n===3||n===5),
 };
}
function makeInnerTendrils(cfg){
 const g=new THREE.BufferGeometry(),
       positions=new Float32Array(ROOT_N*ROOT_SEG*18),
       colors=new Float32Array(ROOT_N*ROOT_SEG*18);
 const ink=new THREE.Color(),specs=[];
 for(let k=0;k<ROOT_N;k++){
  const spec=se270WispSpec(k,cfg);specs.push(spec);
  for(let i=0;i<ROOT_SEG;i++){
   const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
   for(let j=0;j<6;j++){
    const t=(j===2||j===4||j===5)?u1:u0;
    const root=se264Smooth((t-.12)/.61);
    const blue=spec.blue?root*(k%3===0?.94:.73):0;
    const patch=spec.blue?(.83+.17*Math.sin(t*21.+spec.phase)):1;
    const contour=Math.pow(Math.max(0,Math.sin(Math.PI*t)),.68);
    const grain=.55+.45*Math.sin(t*29.+spec.phase)*Math.sin(t*13.+spec.phase*2.1);
    const flicker=.4+.6*se264Smooth((grain-.19)/.74);
    const power=(spec.inner?.63:.67)*contour*flicker;
    ink.copy(se264Purple).lerp(se264Blue,blue*patch).multiplyScalar(power);
    ink.toArray(colors,((k*ROOT_SEG+i)*6+j)*3);
   }
  }
 }
 g.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
 g.setAttribute('color',new THREE.BufferAttribute(colors,3));
 g.setDrawRange(0,ROOT_N*ROOT_SEG*6);
 const mat=new THREE.MeshBasicMaterial({color:0xffffff,vertexColors:true,
  transparent:true,depthWrite:false,depthTest:true,side:THREE.DoubleSide,
  blending:THREE.AdditiveBlending,opacity:.71});
 const mesh=new THREE.Mesh(g,mat);
 mesh.frustumCulled=false;mesh.renderOrder=9;
 mesh.name='Astral Vortex · irregular tapered spectral threads';
 return {g,mat,mesh,specs};
}
function updateInnerTendrils(t,cfg,rec,origin){
 const attr=t.g.getAttribute('position');
 const phase=rec.se249Time*(cfg.vortexSpin??1)*.22;
 for(let k=0;k<ROOT_N;k++){
  const spec=t.specs[k];
  const arm=spec.arm+(cfg.preset==='vortexCyan'?.5:0);
  const at=v=>{
   const t=clamp(v,0,1);
   // The strand peels gently away from its parent's curved arm, never
   // outlines an additional perfect circular orbit.
   const displacement=spec.offset*t+spec.bend*
      Math.sin(t*5.5+spec.phase)*t*(1.-.32*t);
   return location(Math.min(1.04,spec.start+spec.length*t),phase,cfg,
      origin,displacement,0,arm);
  };
  for(let i=0;i<ROOT_SEG;i++){
   const u0=i/ROOT_SEG,u1=(i+1)/ROOT_SEG;
   const p0=at(u0),p1=at(u1);
   const before=at(Math.max(0,u0-.008)),after=at(Math.min(1,u1+.008));
   const dx=after[0]-before[0],dy=after[1]-before[1];
   const inv=1/Math.max(.0001,Math.hypot(dx,dy));
   const nx=-dy*inv,ny=dx*inv;
   const w=u=>(spec.inner?.0015:.0022)+
     (spec.inner?.006:.0055)*Math.pow(Math.max(0,Math.sin(Math.PI*u)),.8)*
       (.82+.18*Math.sin(u*27.+spec.phase));
   const w0=w(u0),w1=w(u1);
   const a0=[p0[0]+nx*w0,p0[1]+ny*w0,p0[2]+spec.depth*u0];
   const b0=[p0[0]-nx*w0,p0[1]-ny*w0,p0[2]+spec.depth*u0];
   const a1=[p1[0]+nx*w1,p1[1]+ny*w1,p1[2]+spec.depth*u1];
   const b1=[p1[0]-nx*w1,p1[1]-ny*w1,p1[2]+spec.depth*u1];
   const vertices=[a0,b0,a1,b0,b1,a1];
   for(let j=0;j<6;j++){
    const p=vertices[j];
    attr.setXYZ((k*ROOT_SEG+i)*6+j,p[0],p[1],p[2]);
   }
  }
 }
 attr.needsUpdate=true;
 t.mat.opacity=clamp(.71*(cfg.vortexGlow??1),.15,.92);
}
"""
    html=html[:a]+roots+html[b:]
    for marker in (
       "const ROOT_N=9,ROOT_SEG=28,ROOT_INNER=3;",
       "function se270WispSpec(k,cfg){",
       "g.setAttribute('color',new THREE.BufferAttribute(colors,3));",
       "slimWispsPerEmitter:ROOT_N-ROOT_INNER",
       "window.SWYRL_ENGINE_SHEEP_NERD_L3_272",
       "window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271",
       "window.SWYRL_ENGINE_PARTICLE_ERRORS_258",
       "renderer.setAnimationLoop(tick);"
    ):assert marker in html,("v11.273 preserve",marker)
    old=" source.engine='§wyrl§ Engine · Maker v11.272';source.version=11.272;"
    assert html.count(old)==2,("v11.273 identity",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.273';source.version=11.273;")
    for x,y in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_272_SHEEP_NERD_L3_TOGGLE",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_273_ORGANIC_GALAXY_FILAMENTS"),
        ("ENGINE · MAKER v11.272","ENGINE · MAKER v11.273"),
        ("v11.272 · left-stick click Nerd Stats toggle",
         "v11.273 · organic broken galaxy filaments"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.272'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.273'"),
        ("<title>§wyrl§ Engine · Maker v11.272</title>",
         "<title>§wyrl§ Engine · Maker v11.273</title>"),
    ):html=once(html,x,y,"release identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Organic, tapered galaxy energy instead of neon spiral arcs",
      date="2026-11-04",changes=[
       "Replace decorative even-width neon arcs with varied-length, narrow, locally branching spectral threads that fade and break into soft glints.",
       "Introduce shared subtle turbulent spiral path undulations and textured brightness along existing major filaments without separating the smoke, stars and particles.",
       "Feather atlas-smoke billboards to remove hard square patches while keeping violet/cyan mixed nebula body.",
       "Retain the 6 main arms, 9 existing fine/inner ribbons per emitter, smoke buffer budget, editor/orbit/timeline, VR L3 diagnostics and Sheep Tag LAN.",
       "No new native emitter, render pass, particle renderer, material per frame or animation loop. Owner Moto/Quest visual acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
